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


## CONVERSION OF FASTAPI TO MCP SERVER

# from fastmcp import FastMCP
# from with_fastapi import app ## import your FastAPU app

# # convert fastapi app to mcp server
# mcp = FastMCP.from_fastapi(app=app, name="Expense Tracker MCP Server")

# if __name__ == "__main__":
#     mcp.run()

#------------------------------------------------------------------


#### PROXY SERVER ADDED FOR CONNECTORS 

from fastmcp import FastMCP
import asyncio

# create a proxy to your remote FastMCP Cloud Server
# FastMCP Cloud uses Streamable HTTP (default), so just use the /mcp url


# This proxy forwards all requests to your deployed FastMCP Cloud server
# Make sure your main.py is deployed and running on FastMCP Cloud first!

# from fastmcp import FastMCP
# import asyncio

# # create a proxy to your remote FastMCP Cloud Server
# # FastMCP Cloud uses Streamable HTTP (default), so just use the /mcp url

# mcp = FastMCP.as_proxy(
#     "https://expense-tracker-mcp-proj.fastmcp.app/mcp",  ## Standard FastMCP Cloud URL
#     name="Expense Tracker Proxy"
# )

# # async def main():
# #     """Run the proxy server asynchronously."""
# #     await mcp.run_async()

# # if __name__ == "__main__":
# #     asyncio.run(main())

# if __name__ == "__main__":
#     # Run the proxy server
#     # This just forwards requests - no database initialization needed
#     mcp.run()


# --------------------------------------------------------------------------------------


#### PROXY SERVER FOR FASTMCP CLOUD DEPLOYMENT

from fastmcp import FastMCP
import sys
import asyncio

# Your FastMCP Cloud URL
CLOUD_URL = "https://expense-tracker-mcp-proj.fastmcp.app/mcp"

print(f"🔗 Connecting proxy to: {CLOUD_URL}", file=sys.stderr)

try:
    # Create proxy to FastMCP Cloud server
    mcp = FastMCP.as_proxy(
        CLOUD_URL,
        name="FastMCP Expense Tracker Proxy"
    )
    print("✅ Proxy created successfully", file=sys.stderr)
except Exception as e:
    print(f"❌ Failed to create proxy: {e}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    try:
        print("🚀 Starting proxy server...", file=sys.stderr)
        mcp.run()
    except KeyboardInterrupt:
        print("\n⏹️  Proxy server stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error running proxy: {e}", file=sys.stderr)
        sys.exit(1)