from mcp.server.fastmcp import FastMCP

from .figma_tools import get_file_nodes, get_file_structure, post_comment

# Initialize FastMCP server
mcp = FastMCP("figma-mcp")

# Register tools
mcp.tool()(get_file_nodes)
mcp.tool()(get_file_structure)
mcp.tool()(post_comment)

if __name__ == "__main__":
    mcp.run()
