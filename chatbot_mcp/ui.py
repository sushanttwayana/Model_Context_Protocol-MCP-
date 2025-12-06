import asyncio
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain_core.messages import ToolMessage, HumanMessage

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Streamlit UI
st.set_page_config(page_title="MCP Expense Analyzer (NPR)", layout="wide")
st.title("🧮 MCP Math + 💰 Expense Tracker")

# Sidebar for settings
st.sidebar.header("⚙️ Settings")
model_name = st.sidebar.selectbox("Groq Model", ["openai/gpt-oss-20b", "llama-3.3-70b-versatile"])
currency_context = st.sidebar.checkbox("Use NPR Currency Context", value=True)

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize MCP client (once)
@st.cache_resource
async def init_mcp_client():
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
    
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()
    named_tools = {tool.name: tool for tool in tools}
    
    st.sidebar.success(f"✅ Loaded {len(named_tools)} tools")
    st.sidebar.info(f"Tools: {list(named_tools.keys())}")
    
    return tools, named_tools

# Currency context injection
def get_currency_context():
    if currency_context:
        return """
All expenses and calculations should be in Nepali Rupees (NPR/रु). 
Use NPR symbol ₹ or रु for currency. Current exchange: 1 USD ≈ 134 NPR.
Convert all dollar amounts to NPR automatically.
        """
    return ""

# Chat processing
async def process_chat(prompt):
    tools, named_tools = await init_mcp_client()
    
    # Add NPR context to prompt
    full_prompt = f"{get_currency_context()}\n\nUser: {prompt}"
    
    llm = ChatGroq(model=model_name, groq_api_key=groq_api_key)
    llm_with_tools = llm.bind_tools(tools)
    
    with st.spinner("🤖 Thinking..."):
        # Step 1: Initial LLM call
        response = await llm_with_tools.ainvoke([HumanMessage(content=full_prompt)])
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            # Execute tool calls
            tool_results = []
            for tool_call in response.tool_calls:
                selected_tool = named_tools[tool_call['name']]
                tool_args = tool_call['args']
                tool_id = tool_call['id']
                
                st.info(f"🔧 Calling: `{tool_call['name']}`({tool_args})")
                
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

# Main chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about expenses, math, or summaries (e.g., 'Weekly NPR expenses summary')"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.status("Processing...", expanded=True):
            result = asyncio.run(process_chat(prompt))
            st.markdown(result)
    
    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": result})

# Quick action buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📊 Weekly NPR Summary"):
        st.session_state.messages.append({"role": "user", "content": "Summarize my expenses from last week to today in NPR"})
with col2:
    if st.button("💰 Monthly Total"):
        st.session_state.messages.append({"role": "user", "content": "What is my total expenses this month in NPR?"})
with col3:
    if st.button("📈 Top Categories"):
        st.session_state.messages.append({"role": "user", "content": "Show my top 3 expense categories by amount in NPR"})
with col4:
    if st.button("🧮 10% of Total"):
        st.session_state.messages.append({"role": "user", "content": "Calculate 10% of my total expenses in NPR"})
