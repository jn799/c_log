# Phase 2: parse ~/.claude/projects/<encoded>/<uuid>.jsonl
# Each line is a JSON event: user message, assistant message, tool call, tool result, thinking block.
# Assistant messages carry usage.input_tokens / usage.output_tokens and model fields.

def parse_session(path: str) -> dict:
    raise NotImplementedError("Phase 2")
