from tools.planning_ import (
    make_plan,
    update_step,
    add_step,
    advance_to_step,
    format_structured_plan,
    get_contextual_plan_reminder,
    show_full_plan,
    get_post_tool_plan_reminder,
    check_plan_completion,
)
from utils.schema_ import function_to_schema
from tools.sec_tools_ import sec_fetch, sec_fetch_metrics
from tools.web_tools_ import (
    web_search,
    visit_url,
    find_on_page,
    find_next,
    page_down,
    page_up,
)
from typing import Dict, List
from typing import Any
import json


def _get_tool_schemas() -> List[Dict[str, Any]]:
    """tools to schema"""
    return [
        function_to_schema(web_search),
        function_to_schema(visit_url),
        function_to_schema(find_on_page),
        function_to_schema(find_next),
        function_to_schema(page_down),
        function_to_schema(page_up),
        function_to_schema(make_plan),
        function_to_schema(update_step),
        function_to_schema(advance_to_step),
        function_to_schema(add_step),
        function_to_schema(show_full_plan),
        function_to_schema(sec_fetch),
        function_to_schema(sec_fetch_metrics),
    ]


async def _execute_tool_call(
    tool_call: Dict[str, Any], *, user_id: str, stream_id: str
):
    """
    Runs the requested tool and yields progress updates and final results.
    Handles both sync and async tools properly.
    """

    name = tool_call.name
    raw_args = tool_call.input

    if isinstance(raw_args, dict):
        args = raw_args
    else:
        try:
            args: Dict[str, Any] = json.loads(raw_args)
        except Exception as e:
            print(f"error args load {e}")
            args = {}

    try:
        if name == "web_search":
            text, _, sources, max_tokens = web_search(**args, user_id=user_id)
            yield {
                "type": "tool_result",
                "content": text,
                "sources": sources,
                "max_tokens": max_tokens,
            }
        elif name == "visit_url":
            text, _, sources, max_tokens = visit_url(**args, user_id=user_id)
            yield {
                "type": "tool_result",
                "content": text,
                "sources": sources,
                "max_tokens": max_tokens,
            }
        elif name == "find_on_page":
            text, _, sources, max_tokens = find_on_page(**args, user_id=user_id)
            yield {
                "type": "tool_result",
                "content": text,
                "sources": sources,
                "max_tokens": max_tokens,
            }
        elif name == "find_next":
            text, _, sources, max_tokens = find_next(**args, user_id=user_id)
            yield {
                "type": "tool_result",
                "content": text,
                "sources": sources,
                "max_tokens": max_tokens,
            }
        elif name == "page_down":
            text, _, sources, max_tokens = page_down(**args, user_id=user_id)
            yield {
                "type": "tool_result",
                "content": text,
                "sources": sources,
                "max_tokens": max_tokens,
            }
        elif name == "page_up":
            text, _, sources, max_tokens = page_up(**args, user_id=user_id)
            yield {
                "type": "tool_result",
                "content": text,
                "sources": sources,
                "max_tokens": max_tokens,
            }
        elif name == "sec_fetch":
            text, _, sources, max_tokens = sec_fetch(**args, user_id=user_id)
            yield {
                "type": "tool_result",
                "content": text,
                "sources": sources,
                "max_tokens": max_tokens,
            }
        elif name == "sec_fetch_metrics":
            text, _, sources, max_tokens = sec_fetch_metrics(**args, user_id=user_id)
            yield {
                "type": "tool_result",
                "content": text,
                "sources": sources,
                "max_tokens": max_tokens,
            }
        elif name == "make_plan":
            text, _, sources, max_tokens = make_plan(**args, user_id=user_id)
            yield {
                "type": "tool_result",
                "content": text,
                "sources": sources,
                "max_tokens": max_tokens,
            }
        elif name == "update_step":
            text, _, sources, max_tokens = update_step(**args, user_id=user_id)
            yield {
                "type": "tool_result",
                "content": text,
                "sources": sources,
                "max_tokens": max_tokens,
            }
        elif name == "add_step":
            text, _, sources, max_tokens = add_step(**args, user_id=user_id)
            yield {
                "type": "tool_result",
                "content": text,
                "sources": sources,
                "max_tokens": max_tokens,
            }
        elif name == "advance_to_step":
            text, _, sources, max_tokens = advance_to_step(**args, user_id=user_id)
            yield {
                "type": "tool_result",
                "content": text,
                "sources": sources,
                "max_tokens": max_tokens,
            }
        elif name == "show_full_plan":
            text, _, sources, max_tokens = show_full_plan(**args, user_id=user_id)
            yield {
                "type": "tool_result",
                "content": text,
                "sources": sources,
                "max_tokens": max_tokens,
            }
        else:
            yield {
                "type": "tool_result",
                "content": f"Unknown tool {name}",
                "sources": "",
                "max_tokens": "",
            }
    except Exception as e:
        print(f"Error executing {name}: {e}")
        yield {"type": "tool_result", "content": f"Error executing {name}: {e}"}
