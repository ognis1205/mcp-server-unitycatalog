# mcp-server-unitycatalog: An Unity Catalog MCP server

<p align="center" float="left">
  <img width="512" src="https://raw.githubusercontent.com/ognis1205/mcp-server-unitycatalog/main/docs/screen.gif">
</p>

## TODO

 - Implement support for create_python_function.
 - Implement catalog explorer tools.
 - Make the codebase more concise and versatile.
 - Add Docker image.
 - Consider implementing minimal data clean room support.

## Overview

A Model Context Protocol server for Unity Catalog Functions. This server provides Unity Catalog Functions as MCP tools.

Please note that mcp-server-unitycatalog is currently in early development. The functionality and available tools are subject to change and expansion as we continue to develop and improve the server.

### Tools

You can use all Unity Catalog Functions registered in Unity Catalog.

## Configuration

These values can be set via CLI options or environment variables. Required arguments are the Unity Catalog server, catalog, and schema, while the access token and verbosity level are optional.

| Argument               | Environment Variable | Description                                                                             | Required/Optional |
|------------------------|----------------------|-----------------------------------------------------------------------------------------|-------------------|
| `-u`, `--uc_server`    | `UC_SERVER`          | The base URL of the Unity Catalog server.                                               | Required          |
| `-c`, `--uc_catalog`   | `UC_CATALOG`         | The name of the Unity Catalog catalog.                                                  | Required          |
| `-s`, `--uc_schema`    | `UC_SCHEMA`          | The name of the schema within a Unity Catalog catalog.                                  | Required          |
| `-t`, `--uc_token`     | `UC_TOKEN`           | The access token used to authorize API requests to the Unity Catalog server.            | Optional          |
| `-v`, `--uc_verbosity` | `UC_VERBOSITY`       | The verbosity level for logging or debugging Unity Catalog operations. Default: `warn`. | Optional          |

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
        "--uc_server",
        "<your unity catalog url>",
        "--uc_catalog",
        "<your catalog name>",
        "--uc_schema",
        "<your schema name>"
      ]
    }
  }
}
```

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
