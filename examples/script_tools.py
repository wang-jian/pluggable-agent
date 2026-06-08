from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_framework.runtime import CapabilityConfig, ProviderRegistry, RuntimeConfig
from agent_framework.tools import register_script_tools_provider


def main() -> None:
    registry = ProviderRegistry()
    register_script_tools_provider(registry)

    config = RuntimeConfig(
        model=CapabilityConfig("your-model-provider"),
        tools=CapabilityConfig(
            "script",
            {"manifest_path": "examples/script_tools/tools.json"},
        ),
    )
    print(config)


if __name__ == "__main__":
    main()
