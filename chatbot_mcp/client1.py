import asyncio
import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain_core.messages import ToolMessage, HumanMessage, AIMessage

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

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
        "transport": "streamable_http",  # if this fails, try "sse"
        "url": "https://expense-tracker-mcp-proj.fastmcp.app/mcp"
    },
}

async def main():
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()
    
    named_tools = {tool.name: tool for tool in tools}
    print(f"Loaded {len(named_tools)}")
    print(f"Available Tools:", named_tools.keys())
    
    llm = ChatGroq(model="openai/gpt-oss-20b", groq_api_key=groq_api_key)
    llm_with_tools = llm.bind_tools(tools)

    # Step 1: Initial LLM call
    # prompt = "What is the product of 12 and 10 using tools available?"
    # prompt = "What is the captial of Nepal"
    prompt = "could you summarize my expeneses from last one week to today in proper format"
    response = await llm_with_tools.ainvoke([HumanMessage(content=prompt)])
    
    # Step 2: Check if tool calls exist and execute
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_call = response.tool_calls[0] 
        selected_tool = named_tools[tool_call['name']]
        tool_args = tool_call['args']
        tool_id = tool_call['id']
        
        print(f"Calling tool: {tool_call['name']} with args: {tool_args}")
        
        # Step 3: Execute tool
        tool_result = await selected_tool.ainvoke(tool_args)
        print(f"Tool result: {tool_result}")
        
        # Step 4: Create ToolMessage and send back to LLM
        tool_message = ToolMessage(
            content=str(tool_result), 
            tool_call_id=tool_id
        )
        
        # Step 5: Final response with tool result
        final_response = await llm_with_tools.ainvoke([
            HumanMessage(content=prompt),
            response,
            tool_message
        ])
        
        print("Final Answer:", final_response.content)
    else:
        print("No tool calls made. Direct response:", response.content)

if __name__ == "__main__":
    asyncio.run(main())
