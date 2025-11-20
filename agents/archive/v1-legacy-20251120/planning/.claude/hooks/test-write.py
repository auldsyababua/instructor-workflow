#!/usr/bin/env python3
import json, sys
data = json.load(sys.stdin)
tool_name = data.get('tool_name', '')
print(f"[HOOK] Testing: {tool_name}", file=sys.stderr)
if tool_name in ['Write', 'Edit']:
    print("[HOOK] BLOCKED", file=sys.stderr)
    sys.exit(2)  # Block
sys.exit(0)  # Allow
