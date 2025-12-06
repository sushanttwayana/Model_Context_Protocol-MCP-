# ## conversion of main.py to a fastapi server
# from fastapi import FastAPI
# from main import mcp  # Import your FastMCP instance from the script where it's defined

# # Create a FastAPI app
# app = FastAPI(lifespan=mcp.http_app().lifespan)  # Use the MCP's lifespan for proper startup/shutdown

# # Mount the MCP's HTTP app as the root or under a path
# app.mount("/", mcp.http_app())  # Mount at root to serve MCP directly via FastAPI

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


# -------------------------------------------------------------------------------------------------


# ## CONVERSION OF FASTAPI TO MCP SERVER

# from fastmcp import FastMCP
# from with_fastapi import app ## import your FastAPU app

# # convert fastapi app to mcp server
# mcp = FastMCP.from_fastapi(app=app, name="Expense Tracker MCP Server")

# if __name__ == "__main__":
#     mcp.run()


#------------------------------------------------------------------

#### PROXY SERVER ADDED FOR CONNECTORS 


from fastmcp import FastMCP

## Create a proxy to you remote FastMCP Cloud Server
## FastMCP CLoud uses Streamable HTTP(Defaut), so just use the /mcp URL

mcp = FastMCP.as_proxy(
    "https://expense-tracker-mcp-proj.fastmcp.app/mcp", ## standard FastMCP Cloud URL
    name = "FastMCP Expense Tracker Proxy "
)


if __name__ == "__main__":
    mcp.run()