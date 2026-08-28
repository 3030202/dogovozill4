"""Typst Compiler MCP Server module."""

import json
import sys
import shutil
import subprocess
from core.rendering.typst_engine import TypstEngine


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        has_typst = shutil.which("typst") is not None
        print(json.dumps({"status": "ready", "module": "mcp-server-typst-compiler", "has_typst_cli": has_typst}))
        return

    print(json.dumps({"status": "ready", "has_typst": shutil.which("typst") is not None}))


if __name__ == "__main__":
    main()
