from models_anthropic_ import model_call
from tools.kernel_tool_ import kernel
from tools.planning_ import make_plan, show_full_plan
from typing import Any, Dict
import asyncio
import inspect
import json


def function_to_schema(func: callable) -> Dict[str, Any]:
    func_name = func.__name__
    doc = inspect.getdoc(func) or ""
    doc_parts = doc.split("#parameters:")
    main_description = doc_parts[0].strip()
    sig = inspect.signature(func)
    sig_params = list(sig.parameters.keys())
    INTERNAL_PARAMS = ["user_id", "stream_id", "conversation_id"]
    param_descriptions = {}
    param_schemas = {}

    if len(doc_parts) > 1:
        param_section = doc_parts[1].strip()
        param_lines = param_section.split("\n")
        current_param = None
        current_content = []
        for line in param_lines:
            line = line.strip()
            if not line:
                continue
            if ":" in line and not line.startswith(" "):
                if current_param and current_content:
                    param_content = " ".join(current_content).strip()
                    try:
                        if param_content.startswith("{") and param_content.endswith(
                            "}"
                        ):
                            try:
                                param_schemas[current_param] = json.loads(param_content)
                                if "description" in param_schemas[current_param]:
                                    param_descriptions[current_param] = param_schemas[
                                        current_param
                                    ]["description"]
                            except json.JSONDecodeError as e:
                                print(f"JSON error for {current_param}: {e}")
                                print(f"Content: {param_content}")
                                param_descriptions[current_param] = param_content
                        else:
                            param_descriptions[current_param] = param_content
                    except Exception as e:
                        print(f"General error: {e}")
                        param_descriptions[current_param] = param_content
                current_param = line.split(":", 1)[0].strip()
                current_content = [line.split(":", 1)[1].strip()]
            else:
                if current_param:
                    current_content.append(line)
        if current_param and current_content:
            param_content = " ".join(current_content).strip()
            try:
                if param_content.startswith("{") and param_content.endswith("}"):
                    param_schemas[current_param] = json.loads(param_content)
                    if "description" in param_schemas[current_param]:
                        param_descriptions[current_param] = param_schemas[
                            current_param
                        ]["description"]
                else:
                    param_descriptions[current_param] = param_content
            except json.JSONDecodeError as e:
                print(f"General error: {e}")
                param_descriptions[current_param] = param_content
    properties = {}
    required_params = []

    for param_name in param_descriptions:
        if param_name in param_schemas:
            properties[param_name] = param_schemas[param_name]
        else:
            properties[param_name] = {
                "type": "string",
                "description": param_descriptions[param_name],
            }

        if param_name in sig_params and param_name not in INTERNAL_PARAMS:
            param = sig.parameters[param_name]
            if param.default == inspect.Parameter.empty:
                required_params.append(param_name)

    for param_name in sig_params:
        if param_name not in properties and param_name not in INTERNAL_PARAMS:
            properties[param_name] = {"type": "string", "description": ""}
            if sig.parameters[param_name].default == inspect.Parameter.empty:
                required_params.append(param_name)

    return {
        "name": func_name,
        "description": main_description,
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required_params,
        },
    }


async def main():

    functions = [
        # kernel,
        make_plan
    ]

    for func in functions:
        schema = function_to_schema(func)
        print(f"\nSchema for {func.__name__}:")
        print(json.dumps(schema, indent=2))

        try:
            response = await model_call(
                input=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {
                        "role": "user",
                        "content": "use the tool write a cussing plan to do web research on stocks",
                    },
                ],
                tools=[schema],
                model="claude-3.5",
            )
            print("\nAPI Response:")
            print(json.dumps(response.model_dump(), indent=2))
            print("\nSchema validation successful!")

            # Extract tool use block and test make_plan
            tool_use_block = next(
                (block for block in response.content if block.type == "tool_use"), None
            )
            if tool_use_block:
                try:
                    make_plan(**tool_use_block.input, user_id="test_user")
                except Exception as e:
                    print(f"\nMake plan error: {e}")
                full_plan = show_full_plan(user_id="test_user")
                print(full_plan)
        except Exception as e:
            print(f"\nSchema validation error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
