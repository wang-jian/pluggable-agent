from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_agent_loop import (  # noqa: E402
    test_final_answer_returns_immediately,
    test_max_turns,
    test_runtime_can_be_built_from_pluggable_providers,
    test_runtime_tools_can_come_from_tool_provider,
    test_tool_result_is_fed_back_to_model,
    test_unknown_tool_can_stop_on_error,
)


def main() -> None:
    tests = [
        test_final_answer_returns_immediately,
        test_tool_result_is_fed_back_to_model,
        test_unknown_tool_can_stop_on_error,
        test_max_turns,
        test_runtime_can_be_built_from_pluggable_providers,
        test_runtime_tools_can_come_from_tool_provider,
    ]
    for test in tests:
        test()
        print(f"ok - {test.__name__}")


if __name__ == "__main__":
    main()
