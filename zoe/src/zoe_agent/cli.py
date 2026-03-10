"""Zoe-Agent CLI — `zoe run 'task'`"""

import json, sys
from .core import Zoe, ZoeState
from pathlib import Path


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print("""zoe — Minimalist AI Agent

Usage:
  zoe run   "task"     Execute a task
  zoe status           Show checkpoint state
  zoe resume           Resume from last checkpoint
  zoe version          Show version

Env:
  ZOE_API_KEY      LLM API key (required)
  ZOE_BASE_URL     API endpoint
  ZOE_MODEL        Model name
""")
        return

    cmd = sys.argv[1]

    if cmd == "version":
        from . import __version__
        print(f"zoe-agent {__version__}")

    elif cmd == "status":
        state = ZoeState.load(Path("/tmp/zoe-default/state.json"))
        print(json.dumps(state.__dict__, indent=2, ensure_ascii=False))

    elif cmd == "run":
        if len(sys.argv) < 3:
            print("Usage: zoe run 'your task'", file=sys.stderr)
            sys.exit(1)
        task = " ".join(sys.argv[2:])
        agent = Zoe(name="default", verbose=True)
        result = agent.run(task)
        print(result)

    elif cmd == "resume":
        state = ZoeState.load(Path("/tmp/zoe-default/state.json"))
        if state.phase in ("idle", "done"):
            print("Nothing to resume.")
        else:
            agent = Zoe(name="default", verbose=True)
            agent.state = state
            result = agent.run(state.task)
            print(result)

    else:
        print(f"Unknown: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
