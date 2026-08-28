"""Legal Validator MCP Server module."""

import json
import sys
from core.validator import validate_party_requisites, validate_inn, validate_bik, validate_bank_account


def main():
    """Simple JSON-RPC / CLI interface for MCP tool invocation."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print(json.dumps({"status": "ready", "module": "mcp-server-legal-validator"}))
        return

    # Process stdin
    try:
        input_data = sys.stdin.read().strip()
        if input_data:
            req = json.loads(input_data)
            res = validate_party_requisites(req)
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"status": "ready"}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))


if __name__ == "__main__":
    main()
