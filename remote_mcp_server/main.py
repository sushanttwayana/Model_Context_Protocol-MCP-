from fastmcp import FastMCP
import random 
import json

## Create a FastMCP server isnstance
mcp = FastMCP("Simple Calculator Server")

## Tool add two numbers
@mcp.tool
def add(a: float, b:float) -> float:

    """
    ADD two numbers together 

    Args: 
        a: first number
        b: second number

    Returns:
        The sum of a and b
    """
    return a + b

#TOOL TO GENERATE A random NUMBER 
@mcp.tool
def random_number(min_val: int =1, max_val: int=100) -> int:
    """
    GENERATE a random number within the sepecified range

    Args:
        - min_val: Minimum value (default:1)
        - max_val: Maximum value (default:100)

    Returns:
        A random integer between min_val and max_val
    """ 

    return random.randint(min_val, max_val)


# Resource: Server Information
@mcp.resource("http://localhost:8000/info/server")
def server_info() -> str:
    """Get information about this server."""
    info = {
        "name": "Simple Calculator Server",
        "version": "1.0.0",
        "description": "A basic MCP server with math tools.",
        "tools": ["add", "random_number"],
        "author": "Your Name"
    }
    return json.dumps(info, indent=2)

# Start the server
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
