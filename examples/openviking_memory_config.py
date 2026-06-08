from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_framework.memory import register_openviking_memory_provider
from agent_framework.runtime import CapabilityConfig, ProviderRegistry, RuntimeConfig


def main() -> None:
    registry = ProviderRegistry()
    register_openviking_memory_provider(registry)

    config = RuntimeConfig(
        model=CapabilityConfig("your-model-provider"),
        memory=CapabilityConfig(
            "openviking",
            options={
                "path": "./openviking-data",
                "session_id": "optional-existing-session-id",
                "target_uri": "",
                "limit": 5,
                "score_threshold": None,
                "initialize": True,
                "auto_commit_on_remember": True,
            },
        ),
    )
    print(config)


if __name__ == "__main__":
    main()
