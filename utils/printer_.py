from termcolor import colored


def printer(msgs, max_tokens):
    print("\n--------------------------------------------------------------new loop")
    print(f"\nmax tokens limit set: {max_tokens}")
    for msg in msgs:
        role = msg.get("role", "")
        type = msg.get("type", "")
        content = msg.get("content") or msg.get("output", "")

        # Handle list content for assistant messages
        if isinstance(content, list):
            preview_parts = []
            for block in content:
                if hasattr(block, "type"):
                    if block.type == "thinking":
                        thinking_preview = (
                            block.thinking[:150] + "..."
                            if len(block.thinking) > 150
                            else block.thinking
                        )
                        preview_parts.append(f"[thinking: {thinking_preview}]")
                    elif block.type == "tool_use":
                        preview_parts.append(f"[tool_use: {block.name}]")
                    elif block.type == "text":
                        text_preview = (
                            block.text[:100] + "..."
                            if len(block.text) > 100
                            else block.text
                        )
                        preview_parts.append(f"[text: {text_preview}]")
                    else:
                        preview_parts.append(f"[{block.type}]")
            preview = " + ".join(preview_parts)
        else:
            preview = (
                str(content)[:200] + "..." if len(str(content)) > 200 else str(content)
            )

        if role == "user":
            print(colored(f"\nuser: {preview}", "cyan"))
        elif role == "assistant":
            print(colored(f"\nassistant: {preview}", "white"))
        elif type == "function_call_output":
            print(colored(f"\nfunction_call_output: {preview}", "green"))
        elif type == "system":
            print(colored(f"\nsystem: {preview}", "blue"))
        else:
            print(f"\n{role}: {preview}")
