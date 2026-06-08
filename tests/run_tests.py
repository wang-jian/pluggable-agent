from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_agent_loop import (  # noqa: E402
    test_agent_loop_calls_memory_lifecycle_for_final_answer,
    test_agent_loop_calls_memory_lifecycle_for_max_turns,
    test_agent_loop_calls_memory_lifecycle_for_tool_error,
    test_final_answer_returns_immediately,
    test_max_turns,
    test_runtime_can_be_built_from_pluggable_providers,
    test_runtime_tools_can_come_from_tool_provider,
    test_tool_result_is_fed_back_to_model,
    test_unknown_tool_can_stop_on_error,
)
from test_openviking_memory import (  # noqa: E402
    test_openviking_context_for_uses_search_with_session,
    test_openviking_finish_turn_writes_assistant_message,
    test_openviking_import_error_is_clear,
    test_openviking_remember_commits_by_default,
)
from test_script_tools import (  # noqa: E402
    test_http_script_tool_posts_json_and_reads_response,
    test_local_script_tool_reports_errors,
    test_local_script_tool_uses_json_stdin_stdout,
    test_script_tool_provider_loads_manifest_specs,
    test_script_tools_provider_can_be_registered,
)
from test_web_tools import (  # noqa: E402
    test_web_fetch_tool_calls_client,
    test_web_search_tool_calls_client_and_formats_results,
    test_web_tool_provider_returns_search_and_fetch,
    test_web_tools_report_network_errors,
)


def main() -> None:
    tests = [
        test_final_answer_returns_immediately,
        test_tool_result_is_fed_back_to_model,
        test_unknown_tool_can_stop_on_error,
        test_max_turns,
        test_runtime_can_be_built_from_pluggable_providers,
        test_runtime_tools_can_come_from_tool_provider,
        test_agent_loop_calls_memory_lifecycle_for_final_answer,
        test_agent_loop_calls_memory_lifecycle_for_tool_error,
        test_agent_loop_calls_memory_lifecycle_for_max_turns,
        test_openviking_context_for_uses_search_with_session,
        test_openviking_finish_turn_writes_assistant_message,
        test_openviking_remember_commits_by_default,
        test_openviking_import_error_is_clear,
        test_script_tool_provider_loads_manifest_specs,
        test_local_script_tool_uses_json_stdin_stdout,
        test_http_script_tool_posts_json_and_reads_response,
        test_local_script_tool_reports_errors,
        test_script_tools_provider_can_be_registered,
        test_web_search_tool_calls_client_and_formats_results,
        test_web_fetch_tool_calls_client,
        test_web_tools_report_network_errors,
        test_web_tool_provider_returns_search_and_fetch,
    ]
    for test in tests:
        test()
        print(f"ok - {test.__name__}")


if __name__ == "__main__":
    main()
