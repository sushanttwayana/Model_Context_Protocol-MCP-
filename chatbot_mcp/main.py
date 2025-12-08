import asyncio
import os, json
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain_core.messages import ToolMessage, HumanMessage, AIMessage
from contextlib import asynccontextmanager

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# MCP Client initialization (startup event)
SERVERS = {
    "math_server": {
        "command": "C:/Users/Vanilla/anaconda3/Scripts/uv.exe",
        "args": [
            "run",
            "--directory",
            "G:/sushant/Model_Context_Protocol/chatbot_mcp",
            "fastmcp",
            "run",
            "math_server.py"
        ],
        "transport": "stdio"
    },
    "expense": {
        "transport": "streamable_http",
        "url": "https://expense-tracker-mcp-proj.fastmcp.app/mcp"
    },
}

async def init_mcp_client():
    """Initialize MCP client and tools once"""
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()
    named_tools = {tool.name: tool for tool in tools}
    return tools, named_tools

tools_cache = None
named_tools_cache = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - runs once when server starts
    global tools_cache, named_tools_cache
    tools_cache, named_tools_cache = await init_mcp_client()
    print(f"✅ Loaded {len(named_tools_cache)} MCP tools: {list(named_tools_cache.keys())}")
    
    yield  # App is running here
    
    # Shutdown - runs when server stops
    print("🔄 MCP Expense Analyzer shutting down...")


app = FastAPI(title="🧮 MCP Expense Analyzer (NPR)", description="FastAPI version of Streamlit MCP chat", lifespan=lifespan)

# CORS for frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (in production, use Redis)
clients: Dict[str, tuple[WebSocket, List[Dict[str, Any]]]] = {}
model_name = "openai/gpt-oss-20b"
currency_context = True

class ChatRequest(BaseModel):
    message: str
    use_npr: bool = True

def get_currency_context():
    if currency_context:
        return """
Respond ONLY in English. Use Nepali Rupees (NPR/रु) for all monetary amounts.
Current exchange: 1 USD ≈ 143 NPR. Convert dollars to NPR automatically.
Keep explanations in English, only currency symbols/names in NPR format
        """
    return ""

@app.get("/")
async def get_ui():
    """Serve simple HTML chat UI"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MCP Expense Analyzer (NPR)</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f8fafc; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #1e293b; font-size: 2.5em; }
            .chat-container { background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); height: 70vh; overflow-y: auto; padding: 20px; margin-bottom: 20px; }
            .message { margin-bottom: 15px; padding: 12px 16px; border-radius: 12px; max-width: 80%; word-wrap: break-word; }
            .user { background: #3b82f6; color: white; margin-left: auto; text-align: right; }
            .assistant { background: #f1f5f9; color: #1e293b; }
            .input-container { display: flex; gap: 10px; }
            input { flex: 1; padding: 15px; border: 2px solid #e2e8f0; border-radius: 12px; font-size: 16px; }
            button { padding: 15px 25px; background: #10b981; color: white; border: none; border-radius: 12px; font-weight: 600; cursor: pointer; }
            button:hover { background: #059669; }
            .quick-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 20px; }
            .quick-btn { padding: 10px 20px; background: #f59e0b; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; }
            .quick-btn:hover { background: #d97706; }
            .status { background: #ecfdf5; padding: 10px; border-radius: 8px; margin: 10px 0; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🧮 MCP Math + 💰 Expense Tracker</h1>
            <div class="status">✅ Connected | Model: "openai/gpt-oss-20b" | NPR Currency: ON</div>
        </div>
        
        <div id="chat-container" class="chat-container"></div>
        
        <div class="input-container">
            <input type="text" id="message-input" placeholder="Ask about expenses, math, or summaries (e.g., 'Weekly NPR expenses summary')">
            <button onclick="sendMessage()">Send</button>
        </div>
        
        <div class="quick-actions">
            <button class="quick-btn" onclick="quickAction('Summarize my expenses from last week to today in NPR')">📊 Weekly Summary</button>
            <button class="quick-btn" onclick="quickAction('What is my total expenses this month in NPR?')">💰 Monthly Total</button>
            <button class="quick-btn" onclick="quickAction('Show my top 3 expense categories by amount in NPR')">📈 Top Categories</button>
            <button class="quick-btn" onclick="quickAction('Calculate 10% of my total expenses in NPR')">🧮 10% of Total</button>
        </div>

        <script>
            const ws = new WebSocket(`ws://localhost:8000/ws`);
            const chatContainer = document.getElementById('chat-container');
            const messageInput = document.getElementById('message-input');
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                addMessage(data.role, data.content);
                if (data.role === 'assistant') scrollToBottom();
            };
            
            function addMessage(role, content) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${role}`;
                messageDiv.innerHTML = content;
                chatContainer.appendChild(messageDiv);
            }
            
            function scrollToBottom() {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            
            async function sendMessage() {  // ✅ Make async
                const message = messageInput.value.trim();
                if (!message) return;
                
                // ✅ Display user message IMMEDIATELY (local)
                addMessage('user', message);
                scrollToBottom();
                
                // ✅ Send to server
                ws.send(JSON.stringify({message: message}));
                messageInput.value = '';
            }
            
            function quickAction(message) {
                messageInput.value = message;
                sendMessage();
            }
            
            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
        </script>

    </body>
    </html>
    """
    return HTMLResponse(html)

# HTTP Chat Endpoint (for API clients)
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    result = await process_chat(request.message)
    return {"response": result}

async def process_chat(prompt: str):
    """Core chat processing logic (same as Streamlit)"""
    global tools_cache, named_tools_cache
    
    full_prompt = f"{get_currency_context()}\n\nUser: {prompt}"
    
    llm = ChatGroq(model=model_name, groq_api_key=groq_api_key)
    llm_with_tools = llm.bind_tools(tools_cache)
    
    # Step 1: Initial LLM call
    response = await llm_with_tools.ainvoke([HumanMessage(content=full_prompt)])
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        # Execute tool calls
        tool_results = []
        for tool_call in response.tool_calls:
            selected_tool = named_tools_cache[tool_call['name']]
            tool_args = tool_call['args']
            tool_id = tool_call['id']
            
            tool_result = await selected_tool.ainvoke(tool_args)
            tool_results.append(ToolMessage(
                content=str(tool_result), 
                tool_call_id=tool_id
            ))
        
        # Step 2: Final response with all tool results
        messages = [HumanMessage(content=full_prompt), response] + tool_results
        final_response = await llm_with_tools.ainvoke(messages)
        return final_response.content
    else:
        return response.content

# WebSocket Chat (replaces Streamlit chat)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(id(websocket))
    clients[client_id] = (websocket, [])
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Send user message back immediately
            # await websocket.send_text(json.dumps({
            #     "role": "user", 
            #     "content": message["message"]
            # }))
            
            # Process chat (same logic as Streamlit)
            result = await process_chat(message["message"])
            
            # Send assistant response
            await websocket.send_text(json.dumps({
                "role": "assistant", 
                "content": result
            }))
            
            # Update history
            clients[client_id][1].append({"role": "user", "content": message["message"]})
            clients[client_id][1].append({"role": "assistant", "content": result})
                
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
        if client_id in clients:
            del clients[client_id]

    except json.JSONDecodeError:
        await websocket.send_text(json.dumps({
            "role": "error", 
            "content": "Invalid JSON message"
        }))
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({
            "role": "error", 
            "content": f"Server error: {str(e)}"
        }))

# Quick action endpoints
@app.get("/quick/{action}")
async def quick_action(action: str):
    prompts = {
        "weekly": "Summarize my expenses from last week to today in NPR",
        "monthly": "What is my total expenses this month in NPR?",
        "categories": "Show my top 3 expense categories by amount in NPR",
        "ten_percent": "Calculate 10% of my total expenses in NPR"
    }
    result = await process_chat(prompts.get(action, prompts["weekly"]))
    return {"response": result}

# Health check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "tools": len(named_tools_cache),
        "model": model_name,
        "npr_context": currency_context
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
