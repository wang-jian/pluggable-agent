# TODO

## Add MemoryPolicy / MemoryFilter

Goal: prevent raw conversation content from being blindly written into memory providers such as OpenViking.

Planned behavior:

- Add a `MemoryPolicy` or `MemoryFilter` layer before `MemoryStore.start_turn()`, `finish_turn()`, and `remember()`.
- Filter or redact secrets such as API keys, tokens, passwords, credentials, and private keys.
- Avoid storing system prompts, tool internals, large tool outputs, and irrelevant code blobs.
- Respect explicit user intent such as "do not remember this".
- Support provider-specific behavior, for example allowing OpenViking automatic session history while restricting commits.

Likely implementation points:

- `agent_framework/memory/base.py`
- `agent_framework/runtime/runtime.py`
- `agent_framework/core/loop.py`
- `agent_framework/memory/openviking.py`

Testing notes:

- Add fake memory tests for redaction before `start_turn()` and `finish_turn()`.
- Add tests that secrets are not passed into `remember()`.
- Keep `LocalMemoryStore` behavior backward-compatible unless a policy is configured.
