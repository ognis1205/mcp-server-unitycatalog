"""Unity Catalog Model Context Protocol Server Entry Point.

This module serves as the entry point for the Model Context Protocol (MCP) server, enabling AI agents
to execute Unity Catalog Functions on behalf of user agents.

License:
MIT License (c) 2025 Shingo OKAWA
"""

import sys
from traceback import format_exc
from mcp_server_unitycatalog import main


if __name__ == "__main__":
    try:
        main()
    except Exception as _:
        print(format_exc(), file=sys.stderr)
