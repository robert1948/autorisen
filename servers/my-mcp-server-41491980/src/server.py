from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-mcp-server-41491980")

@mcp.tool()
def hello_world() -> str:
    """A simple hello world tool."""
    return "Hello from my-mcp-server-41491980!"

if __name__ == "__main__":
    mcp.run()
