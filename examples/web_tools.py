from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_framework.runtime import CapabilityConfig, ProviderRegistry, RuntimeConfig
from agent_framework.tools.web import WebToolProvider


def main() -> None:
    registry = ProviderRegistry()
    registry.register("tools", "web", lambda options: WebToolProvider())

    config = RuntimeConfig(
        model=CapabilityConfig("your-model-provider"),
        tools=CapabilityConfig("web"),
    )
    print(config)


if __name__ == "__main__":
    main()
