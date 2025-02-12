# mcp-server-unitycatalog: An Unity Catalog MCP server

<p align="center" float="left">
  <img width="512" src="https://raw.githubusercontent.com/ognis1205/mcp-server-unitycatalog/main/docs/screen.gif">
</p>

## TODO

- [ ] Implement support for `create_python_function`.
- [ ] Implement catalog explorer tools.
- [ ] Make the codebase more concise and versatile.
- [ ] Add Docker image.
- [ ] Consider implementing minimal data clean room support.
- [ ] Implement `use_xxx` methods. In the current implementation, `catalog` and `schema` need to be defined when starting the server. However, they will be implemented as `use_catalog` and `use_schema` functions, dynamically updating the list of available functions when the `use_xxx` is executed.
- [ ] Consider unified tool returned type interface.

## Overview

A Model Context Protocol server for Unity Catalog Functions. This server provides Unity Catalog Functions as MCP tools.

Please note that mcp-server-unitycatalog is currently in early development. The functionality and available tools are subject to change and expansion as we continue to develop and improve the server.

### Tools

You can use **all Unity Catalog Functions registered in Unity Catalog** alongside the following predefined Unity Catalog AI tools:

1. `uc_list_functions`
   - Lists functions within the specified parent catalog and schema
   - Returns: A list of functions retrieved from Unity Catalog

2. `uc_get_function`
   - Gets a function from within a parent catalog and schema
   - Input:
     - `name` (string): The name of the function (not fully-qualified)
   - Returns: A function details retrieved from Unity Catalog

## Configuration

These values can be set via CLI options or `.env` environment variables. Required arguments are the Unity Catalog server, catalog, and schema, while the access token and verbosity level are optional. Run `uv run mcp-server-unitycatalog --help` for more detailed configuration options.

| Argument                   | Environment Variable | Description                                                                        | Required/Optional |
|----------------------------|----------------------|------------------------------------------------------------------------------------|-------------------|
| `-u`, `--uc_server`        | `UC_SERVER`          | The base URL of the Unity Catalog server.                                          | Required          |
| `-c`, `--uc_catalog`       | `UC_CATALOG`         | The name of the Unity Catalog catalog.                                             | Required          |
| `-s`, `--uc_schema`        | `UC_SCHEMA`          | The name of the schema within a Unity Catalog catalog.                             | Required          |
| `-t`, `--uc_token`         | `UC_TOKEN`           | The access token used to authorize API requests to the Unity Catalog server.       | Optional          |
| `-v`, `--uc_verbosity`     | `UC_VERBOSITY`       | The verbosity level for logging. Default: `warn`.                                  | Optional          |
| `-l`, `--uc_log_directory` | `UC_LOG_DIRECTORY`   | The directory where log files will be stored. Default: `.mcp_server_unitycatalog`. | Optional          |

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

If you are using a runtime version manager, such as `asdf`, the configuration file may look like this:

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
      ],
      "env": {
        "PATH": "/<path to your asdf installation>/.asdf/shims:/usr/bin:/bin",
        "ASDF_DIR": "/<path to your asdf installation>/.asdf",
        "ASDF_DATA_DIR": "/<path to your asdf installation>/.asdf",
        "ASDF_UV_VERSION": "<your uv version>"
      }
    }
  }
}
```

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
