# Work Log

## 2026-06-08

### Repository Setup

- Initialized the local git repository.
- Connected the repository to `git@github.com:wang-jian/pluggable-agent.git`.
- Configured local git author as `wang-jian <190133829@qq.com>`.
- Merged the remote initial commit and preserved the remote `LICENSE`.

### Agent Framework

- Added the initial learning-oriented agent framework.
- Implemented `Agent`, `AgentLoop`, `ModelAdapter`, runtime events, messages, tool calls, and tool results.
- Added pluggable runtime assembly with `RuntimeConfig`, `CapabilityConfig`, `ProviderRegistry`, and `RuntimeBuilder`.
- Added capability interfaces for memory, RAG, MCP, skills, and tools.
- Added minimal examples and no-dependency tests.

Commit:

```text
5fa1553 Implement pluggable agent runtime framework
```

### OpenViking Memory

- Added `OpenVikingMemoryStore` as a pluggable memory provider.
- Added memory lifecycle hooks: `start_turn()` and `finish_turn()`.
- Integrated memory session lifecycle into `AgentLoop`.
- Used OpenViking session-aware `search()` for memory context retrieval.
- Added `remember()` support with session commit.
- Added fake-client tests and an OpenViking config example.
- Added `todo.md` for future `MemoryPolicy` / `MemoryFilter`.

Commit:

```text
d3da942 Add OpenViking memory provider
```

### Web Tools

- Added `WebSearchTool` and `WebFetchTool`.
- Added `WebToolProvider` to expose both web tools through the runtime.
- Implemented default web client with Python standard library.
- Added fake-client tests and a runtime config example.

Commit:

```text
1754f90 Add web search and fetch tools
```

### Custom Script Tools

- Added `ScriptTool` and `ScriptToolProvider`.
- Added support for local tools using JSON stdin/stdout.
- Added support for URL tools as HTTP POST endpoints.
- Added `register_script_tools_provider(registry)`.
- Added example `tools.json` and local `echo_tool.py`.
- Added `agent_framework/tools/readme.md` describing tool features and how to add custom tools.
- Added unit tests for manifest loading, local scripts, HTTP endpoints, and error handling.

Commit:

```text
dca1785 Add custom script tool provider
```

## Current Status

- Local `main` is synced with `origin/main`.
- Latest commit:

```text
dca1785 Add custom script tool provider
```

- Verification commands used:

```text
python3 tests/run_tests.py
python3 examples/script_tools.py
python3 -m compileall agent_framework examples tests
```

## Next Work

- Add `MemoryPolicy` / `MemoryFilter` before memory writes.
- Add sandbox and permission policy for risky tools.
- Add real model providers such as OpenAI-compatible, AWS Bedrock, and Volcano Ark.
- Add MCP stdio / HTTP integration.
- Improve script tool security with allowlists, working directory constraints, and secret redaction.
