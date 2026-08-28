"""Windows Packager MCP Server module."""

import json
import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print(json.dumps({"status": "ready", "module": "mcp-server-windows-packager"}))
        return

    print(json.dumps({"status": "ready"}))


if __name__ == "__main__":
    main()
