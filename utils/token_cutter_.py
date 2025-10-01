from utils.utils import tokenizer
import json


def token_cutter(messages, max_tokens=30000):
    """Keep only the last N messages to manage token limits"""
    """
    token cutter.
    """

    ## MUST KEEP PRESERVATION BLOCK ##
    must_keep = {
        "user": None,
        "assistant": None,
        "function_call_output": None,
    }
    full_messages = messages.copy()
    for msg in reversed(full_messages):
        r = msg.get("role")
        if msg.get("type") == "function_call":
            continue  # Skip tool calls for now, handle separately
        if msg.get("type") == "function_call_output":
            r = "function_call_output"
        if r in must_keep and must_keep[r] is None:
            must_keep[r] = msg
            if all(must_keep.values()):
                break  # Found all required message types
    must_keep_ids = {id(m) for m in must_keep.values() if m}

    ### [PLAN] & [ORIGINAL_QUERY]: PRESERVATION
    plan_critical_messages = []
    original_query_msg = None

    for msg in full_messages:
        content = msg.get("content", "")
        if "[⌘PLAN]:" in content:
            plan_critical_messages.append(msg)
        if "[⌘ORIGINAL_QUERY]:" in content:
            original_query_msg = msg

    # Always preserve the original query
    if original_query_msg:
        must_keep_ids.add(id(original_query_msg))

    # Preserve most recent plan message
    if plan_critical_messages:
        most_recent_plan_msg = plan_critical_messages[-1]
        must_keep_ids.add(id(most_recent_plan_msg))

    ### preserve 2nd tool output
    tool_call_outputs = [
        m
        for m in full_messages
        if m.get("type") == "function_call_output" and id(m) not in must_keep_ids
    ]
    tool_calls = [m for m in full_messages if m.get("type") == "function_call"]

    if tool_call_outputs:
        second_most_recent_output = (
            tool_call_outputs[-1] if len(tool_call_outputs) >= 1 else None
        )
        if second_most_recent_output:
            output_call_id = second_most_recent_output.get("call_id")
            matching_call = next(
                (call for call in tool_calls if call.get("call_id") == output_call_id),
                None,
            )
            if matching_call:
                must_keep_ids.add(id(second_most_recent_output))
                must_keep_ids.add(id(matching_call))
    must_keep_list = [m for m in full_messages if id(m) in must_keep_ids]

    ## NON-ESSENTIAL MESSAGE SELECTION BLOCK ##
    non_essential = [m for m in full_messages if id(m) not in must_keep_ids]
    non_essential.reverse()
    used_tokens = 0
    for m in must_keep_list:
        if "content" in m:
            content = m.get("content", "")
            if isinstance(content, list):
                for block in content:
                    if hasattr(block, "thinking"):
                        used_tokens += len(tokenizer.encode(block.thinking))
            else:
                used_tokens += len(tokenizer.encode(m.get("content", "")))
        elif m.get("type") == "function_call_output" and "output" in m:
            output = m.get("output", "")
            if isinstance(output, (dict, list)):
                output = json.dumps(output)
            used_tokens += len(tokenizer.encode(output))
    available = max_tokens - used_tokens
    ## TOKEN CUTTING BLOCK ##
    preserved = []
    seen_content = set()
    for msg in non_essential:
        content = ""
        if "content" in msg:
            raw_content = msg.get("content", "")
            if isinstance(raw_content, list):
                thinking_parts = []
                for block in raw_content:
                    if hasattr(block, "thinking"):
                        thinking_parts.append(block.thinking)
                content = "\n".join(thinking_parts)
            else:
                content = raw_content
        elif msg.get("type") == "function_call_output" and "output" in msg:
            content = msg.get("output", "")
        if not content:
            continue
        if msg.get("type") == "function_call_output":
            msg_key = ("function_call_output", content)
        else:
            msg_key = (msg.get("role", ""), content)
        if msg_key in seen_content:
            continue
        tokens = tokenizer.encode(content)
        length = len(tokens)
        if available <= 0:
            continue
        if length <= available:
            preserved.insert(0, msg)
            seen_content.add(msg_key)
            used_tokens += length
            available -= length
        elif available >= 1000:
            trimmed = msg
            if "[⌘PLAN]:" in content:
                plan_marker_pos = content.find("[⌘PLAN]:")
                plan_content = content[:plan_marker_pos]
                plan_message = content[plan_marker_pos:]

                plan_content_tokens = tokenizer.encode(plan_content)
                trimmed_plan_content = tokenizer.decode(
                    plan_content_tokens[:available]
                ).rstrip()
                final_content = (
                    trimmed_plan_content
                    + "\n\n... (trimmed for token limit)"
                    + plan_message
                ).rstrip()
            else:
                final_content = (
                    tokenizer.decode(tokens[:1000]).rstrip()
                    + "\n\n... (trimmed for token limit)"
                ).rstrip()

            if "content" in trimmed:
                trimmed["content"] = final_content
            elif trimmed.get("type") == "function_call_output" and "output" in trimmed:
                trimmed["output"] = final_content

            preserved.insert(0, trimmed)

            if "content" in trimmed:
                seen_content.add((msg.get("role", ""), trimmed["content"]))
            elif trimmed.get("type") == "function_call_output":
                seen_content.add(("function_call_output", trimmed["output"]))

            used_tokens += 1000
            available -= 1000

    ## FINAL REORDERING BLOCK ##
    final_order = []
    seen_ids = set()
    # Iterate through original message list most recent first we keepo must keeps and the selected from token cutter
    for m in reversed(full_messages):
        if id(m) in must_keep_ids or any(id(x) == id(m) for x in preserved):
            if id(m) not in seen_ids:
                final_order.append(m)
                seen_ids.add(id(m))

    final_order.reverse()

    ## TOOL CALL PAIRING BLOCK ##
    calls_lookup = {}
    for m in full_messages:
        if m.get("role") == "assistant":
            content = m.get("content", "")
            if isinstance(content, list):
                for block in content:
                    if hasattr(block, "type") and block.type == "tool_use":
                        call_id = block.id
                        calls_lookup[call_id] = m
    # Insert function_calls before their outputs
    output = []
    for m in final_order:
        if m.get("type") == "function_call_output" and m.get("call_id"):
            call_id = m.get("call_id")
            func_call = calls_lookup.get(call_id)
            if func_call and func_call not in output:
                output.append(func_call)
        output.append(m)

    ## ORPHANED CALLS/OUTPUTs CLEANUP ##
    function_call_ids = set()
    for m in output:
        if m.get("role") == "assistant" and isinstance(m.get("content"), list):
            for block in m.get("content", []):
                if hasattr(block, "type") and block.type == "tool_use":
                    function_call_ids.add(block.id)
    function_output_ids = {
        m.get("call_id") for m in output if m.get("type") == "function_call_output"
    }

    validated_output = []
    for m in output:
        if m.get("role") == "assistant" and isinstance(m.get("content"), list):
            has_valid_tool_use = False
            for block in m.get("content", []):
                if hasattr(block, "type") and block.type == "tool_use":
                    if block.id in function_output_ids:
                        has_valid_tool_use = True
                        break
            if has_valid_tool_use or not any(
                hasattr(block, "type") and block.type == "tool_use"
                for block in m.get("content", [])
            ):
                validated_output.append(m)
            else:
                pass
                # print(f"Removing assistant message with orphaned tool_use blocks")
        elif m.get("type") == "function_call_output" and m.get("call_id"):
            if m.get("call_id") in function_call_ids:
                validated_output.append(m)
            else:
                pass
                # print(
                #     f"Removing orphaned function_call_output with call_id: {m.get('call_id')}"
                # )
        else:
            validated_output.append(m)

    ### RM ANY TRAILING WHITESPACE
    for msg in validated_output:
        if "content" in msg and isinstance(msg["content"], str):
            msg["content"] = msg["content"].rstrip()
        elif (
            msg.get("type") == "function_call_output"
            and "output" in msg
            and isinstance(msg["output"], str)
        ):
            msg["output"] = msg["output"].rstrip()

    return validated_output
