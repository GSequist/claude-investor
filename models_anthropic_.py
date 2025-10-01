from typing import List, Dict, Any, Optional, Union
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import json

load_dotenv()

################################################


def log_tokens(input_tokens: int, output_tokens: int, model: str):
    """utility function to log token usage"""
    log = {
        "timestamp": datetime.now().isoformat(),
        "input": input_tokens,
        "output": output_tokens,
        "model": model,
    }
    with open("utils/token_usage.json", "a") as f:
        f.write(json.dumps(log) + "\n")


####################################################


async def model_call(
    input: Union[List[Dict[str, Any]], str],
    model="claude-4",
    encoded_image: Optional[Union[str, List[str]]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: Optional[Dict[str, Any]] = None,
    stream: bool = False,
    thinking=False,
    max_tokens: int = 8000,
    client_timeout: int = 240,
):
    client = AsyncAnthropic(timeout=client_timeout)
    retries = 3
    sleep_time = 2
    if model == "opus-4.1":
        model = "claude-opus-4-1-20250805"
    elif model == "claude-3.7":
        model = "claude-3-7-sonnet-20250219"
    elif model == "claude-4":
        model = "claude-sonnet-4-20250514"
    elif model == "claude-3.5":
        model = "claude-3-5-haiku-20241022"

    system_prompts = []
    messages = []

    if encoded_image:
        if not isinstance(input, str):
            raise ValueError("Image input requires string query")

        content = []
        if isinstance(encoded_image, str):
            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": encoded_image,
                    },
                }
            )
        else:
            for img in encoded_image:
                content.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": img,
                        },
                    }
                )

        content.append({"type": "text", "text": input})
        messages = [{"role": "user", "content": content}]
    elif isinstance(input, str):
        messages = [{"role": "user", "content": input}]
    else:
        for msg in input:
            if msg.get("type") == "function_call":
                tool_use = {
                    "type": "tool_use",
                    "id": msg.get("call_id", msg.get("id", "")),
                    "name": msg.get("name", ""),
                    "input": json.loads(
                        msg.get("arguments", "{}") if msg.get("arguments") else "{}"
                    ),
                }
                messages.append({"role": "assistant", "content": [tool_use]})
                continue
            elif msg.get("type") == "function_call_output":
                tool_result = {
                    "type": "tool_result",
                    "tool_use_id": msg.get("call_id", ""),
                    "content": msg.get("output", ""),
                }
                messages.append({"role": "user", "content": [tool_result]})
                continue

            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("developer", "system"):
                if isinstance(content, str):
                    system_prompts.append(content)
                continue

            messages.append({"role": role, "content": content})

    api_parameters = {"model": model}

    if system_prompts:
        api_parameters["system"] = "\n".join(system_prompts)

    if tools:
        api_parameters["tools"] = tools

    if tool_choice:
        api_parameters["tool_choice"] = tool_choice

    if thinking:
        api_parameters["thinking"] = {"type": "enabled", "budget_tokens": 16000}
        api_parameters["max_tokens"] = 60000
        api_parameters["extra_headers"] = {
            "anthropic-beta": "interleaved-thinking-2025-05-14"
        }
    else:
        api_parameters["max_tokens"] = max_tokens

    api_parameters["messages"] = messages

    api_parameters["stream"] = stream

    for attempt in range(retries):
        try:
            response = await client.messages.create(**api_parameters)
            if hasattr(response, "usage"):
                log_tokens(
                    response.usage.input_tokens,
                    response.usage.output_tokens,
                    api_parameters["model"],
                )
            return response

        except Exception as e:
            print(f"\n[model_call]: {e}")
            if attempt < retries - 1:
                sleep_time = sleep_time * (2**attempt)
                print(f"\n[model_call]: Retrying in {sleep_time} seconds...")
                await asyncio.sleep(sleep_time)
            else:
                print(f"\n[model_call]: Failed after {retries} attempts")
                break

    return None


#########################################
