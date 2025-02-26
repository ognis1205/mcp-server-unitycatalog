# mcp-server-unitycatalog: An Unity Catalog MCP server

<p align="center" float="left">
  <img width="256" src="https://raw.githubusercontent.com/ognis1205/mcp-server-unitycatalog/main/docs/vscode1.webp" />
  <img width="256" src="https://raw.githubusercontent.com/ognis1205/mcp-server-unitycatalog/main/docs/vscode2.webp" />
  <img width="256" src="https://raw.githubusercontent.com/ognis1205/mcp-server-unitycatalog/main/docs/vscode3.webp" />
</p>

## Overview

A Model Context Protocol server for [Unity Catalog](https://www.unitycatalog.io/). This server provides [Unity Catalog Functions](https://docs.unitycatalog.io/usage/functions/) as MCP tools.

### Tools

You can use **all Unity Catalog Functions registered in Unity Catalog** alongside the following predefined Unity Catalog AI tools:

1. `uc_list_functions`
   - Lists functions within the specified parent catalog and schema.
   - Returns: A list of functions retrieved from Unity Catalog.

2. `uc_get_function`
   - Gets a function within a parent catalog and schema.
   - Input:
     - `name` (string): The name of the function (not fully-qualified).
   - Returns: A function details retrieved from Unity Catalog.

3. `uc_create_function`
   - Creates a function within a parent catalog and schema. **WARNING: This API is experimental and will change in future versions**.
   - Input:
     - `name` (string): The name of the function (not fully-qualified).
     - `script` (string): The Python script including the function to be registered.
   - Returns: A function details created within Unity Catalog.

4. `uc_delete_function`
   - Deletes a function within a parent catalog and schema.
   - Input:
     - `name` (string): The name of the function (not fully-qualified).
   - Returns: None.

## Installation

### Using uv

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will use
[`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *mcp-server-git*.

## Configuration

These values can also be set via CLI options or `.env` environment variables. Required arguments are the Unity Catalog server, catalog, and schema, while the access token and verbosity level are optional. Run `uv run mcp-server-unitycatalog --help` for more detailed configuration options.

| Argument                   | Environment Variable | Description                                                                        | Required/Optional |
|----------------------------|----------------------|------------------------------------------------------------------------------------|-------------------|
| `-u`, `--uc_server`        | `UC_SERVER`          | The base URL of the Unity Catalog server.                                          | Required          |
| `-c`, `--uc_catalog`       | `UC_CATALOG`         | The name of the Unity Catalog catalog.                                             | Required          |
| `-s`, `--uc_schema`        | `UC_SCHEMA`          | The name of the schema within a Unity Catalog catalog.                             | Required          |
| `-t`, `--uc_token`         | `UC_TOKEN`           | The access token used to authorize API requests to the Unity Catalog server.       | Optional          |
| `-v`, `--uc_verbosity`     | `UC_VERBOSITY`       | The verbosity level for logging. Default: `warn`.                                  | Optional          |
| `-l`, `--uc_log_directory` | `UC_LOG_DIRECTORY`   | The directory where log files will be stored. Default: `.mcp_server_unitycatalog`. | Optional          |

### Usage with Claude Desktop or VSCode Cline

Add this to your `claude_desktop_config.json` (or `cline_mcp_settings.json`):

<details>
<summary>Using uv</summary>

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
</details>

<details>
<summary>Using docker</summary>

* Note: replace '/Users/username' with the a path that you want to be accessible by this tool

```json
{
  "mcpServers": {
    "unitycatalog": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "mcp/unitycatalog",
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
</details>

## Building

Docker:

```bash
docker build -t mcp/unitycatalog .   
```

## Future Plans

- [x] Implement support for `list_functions`.
- [x] Implement support for `get_function`.
- [x] Implement support for `create_python_function`.
- [x] Implement support for `execute_function`.
- [x] Implement support for `delete_function`.
- [ ] Implement semantic catalog explorer tools.
- [x] Add Docker image.
- [ ] Implement `use_xxx` methods. In the current implementation, `catalog` and `schema` need to be defined when starting the server. However, they will be implemented as `use_catalog` and `use_schema` functions, dynamically updating the list of available functions when the `use_xxx` is executed.

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
