# mcp-server-unitycatalog: An Unity Catalog MCP server

<p align="center" float="left">
  <img width="256" src="https://raw.githubusercontent.com/ognis1205/mcp-server-unitycatalog/main/docs/screen.gif">
</p>

## Overview

A Model Context Protocol server for Unity Catalog Functions. This server provides Unity Catalog Functions as MCP tools.

Please note that mcp-server-unitycatalog is currently in early development. The functionality and available tools are subject to change and expansion as we continue to develop and improve the server.

### Tools

You can use all Unity Catalog Functions registered in Unity Catalog.

## Development

If you are doing local development, test your changes as follows:

1. Test using the Claude desktop app (or VSCode Cline). Add the following to your `claude_desktop_config.json` (or `cline_mcp_settings.json`):

### UVX
```json
{
  "mcpServers": {
    "unitycatalog": {
      "command": "uv",
      "args": [
        "--directory",
        "/<path to your local git repository>/mcp-server-unitycatalog",
        "run",
        "mcp-server-unitycatalog",
        "--url",
        "<your unity catalog url>",
        "--catalog",
        "<your catalog name>",
        "--schema",
        "<your schema name>"
      ]
    }
  }
}
```

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
