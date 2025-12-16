# Figma MCP Server

This is a Model Context Protocol (MCP) server that provides tools to interact with the Figma API.

## Features

- **get_file_nodes**: Retrieve specific nodes from a Figma file.
- **post_comment**: Post comments to a Figma file, optionally attached to a specific node.

## Setup

1. **Install Dependencies**:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2. **Configure Environment**:
    - Copy `.env.example` to `.env`.
    - Add your Figma Personal Access Token to `FIGMA_API_KEY`.

3. **Run the Server**:

    ```bash
    python src/server.py
    ```

## Usage with Claude Desktop / MCP Client

Add the following to your MCP client configuration:

```json
{
  "mcpServers": {
    "figma": {
      "command": "/path/to/servers/figma-mcp/.venv/bin/python",
      "args": ["/path/to/servers/figma-mcp/src/server.py"]
    }
  }
}
```
