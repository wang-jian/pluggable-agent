from __future__ import annotations

import json
import sys


def main() -> None:
    payload = json.loads(sys.stdin.read())
    text = payload["arguments"]["text"]
    print(json.dumps({"content": f"echo: {text}", "ok": True, "data": {"text": text}}))


if __name__ == "__main__":
    main()
