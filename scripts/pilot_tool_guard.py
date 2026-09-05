"""Future worker hook: reject notebook output reads before they reach MCP."""
import json
import sys


def guard(event):
    name=event.get('tool_name','');args=event.get('tool_input',{})
    if name.endswith('__get_cells') and args.get('includeOutputs') is not False:
        return {'hookSpecificOutput':{'hookEventName':'PreToolUse','permissionDecision':'deny',
            'permissionDecisionReason':'PILOT_OUTPUT_READ_BLOCKED: set includeOutputs=false; raw notebook outputs are private.'}}
    return {}


if __name__=='__main__':
    try:result=guard(json.load(sys.stdin))
    except Exception:
        print('Malformed pilot tool-guard input',file=sys.stderr);raise SystemExit(2)
    print(json.dumps(result))
