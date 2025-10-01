from execute_tool_ import _get_tool_schemas, _execute_tool_call
from utils.ratios_precalc_ import precalculate_ratios
from utils.graph_charting_ import graph_charter
from utils.token_cutter_ import token_cutter
from models.investors_ import GORDOK_GEKKO
from models_anthropic_ import model_call
from utils.utils import extract_json_
from tools.planning_ import (
    _get_plan,
    get_contextual_plan_reminder,
    show_full_plan,
    get_post_tool_plan_reminder,
)
from utils.printer_ import printer
from typing import Dict, List
from dotenv import load_dotenv
import datetime
import asyncio


load_dotenv()


async def gekko_looper_(
    query,
    no_turns: int = 30,
    thinking: bool = False,
    graph: bool = False,
    *,
    user_id: str,
    stream_id: str,
):
    """
    looping gekko
    """

    max_tokens = 30000

    yield {
        "type": "tool_progress",
        "toolName": "gekko_looper_",
        "progress": f"Beginning analysis, performing financial calculations..",
        "percentage": 1,
        "stream_id": stream_id,
    }

    ###quant block
    financial_context = await precalculate_ratios(query, user_id)

    ###deep research block
    system_msg = f"""
Your task is to perform deep investment analysis for client.
Use your deep knowledge of investment banking and think systematically.

Current datetime: {datetime.datetime.now().strftime("%B %d, %Y")}

In order to succeed, you will follow these phases:

<planning_phase>
- Use <make_plan> to create detailed research plan with steps:
- Make sure the steps are granular to guide you through your work
- Make sure the plan outlines which tools to use for which step
</planning_phase>

<web_research_phase>
- Succint highly focused research on 
- company news, 
- industry/sector news/trends/dynamics, 
- competitor news
- analyst opinions
- document your findings after each tool run with <update_step>
</web_research_phase>

<sec_phase>
- Use sec_fetch:
- choose keywords based on what interests you after your initial research, e.g. R&D, director compensation, etc.
- make sure to define keywords in the context of your findings in web phase
- document your findings after each tool run with <update_step>
</sec_phase>

<quant_phase>
- You are given some already precalculated financial ratios:
{financial_context}
- Use sec_fetch_metrics to get more data 
-> fetch with metrics filter set to None at first to get initial full data 
-> then you can rerun with metrics filter that interest you with filter for year or form for more granular data
- Think what other calculations would make sense in the context of your findings
</quant_phase>

⚠️ CRITICAL INSTRUCTION:
- After each tool, note down your findings using <update_step>
- Use <show_full_plan> to track progress through each phase
- If your research leads to new findings that require more work that initially planned use <add_step> to add more steps to the plan

Before you finish make sure to use <show_full_plan> to review if you satisfied all steps
When you are done finish with <RESEARCH_COMPLETE>
    """

    msgs: List[Dict[str, str]] = [
        {"role": "system", "content": system_msg},
        {
            "role": "user",
            "content": f"[⌘ORIGINAL_QUERY]: {query}",
        },
    ]
    tool_schemas = _get_tool_schemas()

    steps = 0
    stop_flag = False
    all_sources = []

    while steps <= no_turns and stop_flag == False:

        # Calculate progress: steps 0-no_turns map to 5-60%
        progress_percentage = min(5 + int((steps / no_turns) * 55), 60)

        yield {
            "type": "tool_progress",
            "toolName": "gekko_looper_",
            "progress": f"Research phase {steps}/{no_turns}...",
            "percentage": progress_percentage,
            "stream_id": stream_id,
        }

        plan = _get_plan(user_id)
        if plan:
            plan_reminder = get_contextual_plan_reminder(plan)
            if plan_reminder.strip():
                msgs.append(
                    {
                        "role": "system",
                        "content": f"[⌘PLAN]: {plan_reminder}",
                    }
                )

        web_research_limit = int(no_turns * 0.50)
        sec_research_limit = int(no_turns * 0.80)

        if steps > sec_research_limit:
            msgs.append(
                {
                    "role": "user",
                    "content": f"""
⚠️ CRITICAL: Claude you've used too much time on <sec_phase>, move on to quant phase before wrapping up!
                """,
                }
            )
        elif steps > web_research_limit:
            msgs.append(
                {
                    "role": "user",
                    "content": f"""
⚠️ CRITICAL: Claude you've used too much time on <web_research_phase>, consider moving to SEC/quant phases now!
                """,
                }
            )

        msgs = token_cutter(msgs, max_tokens)

        ## reminder for the final run
        if steps == no_turns:
            yield {
                "type": "tool_progress",
                "toolName": "gekko_looper_",
                "progress": f"Finishing research..",
                "percentage": 60,
                "stream_id": stream_id,
            }

            full_plan, *_ = show_full_plan(user_id=user_id)
            if full_plan.strip():
                msgs.append(
                    {
                        "role": "user",
                        "content": f"[⌘PLAN]: Here is the full plan notes up to now\n{full_plan}",
                    }
                )
            msgs.append(
                {
                    "role": "user",
                    "content": """You have made too many tool calls, this is your final run. 
⚠️ CRITICAL INSTRUCTION: Do not call any more tools, otherwise all the information collected will be lost.
⚠️ CRITICAL INSTRUCTION: Summarize all your findings up to now.
Finish with <RESEARCH_COMPLETE>         
                """,
                }
            )

        ##add step
        steps += 1

        # printer(msgs, max_tokens) ### for testing

        try:
            response = await model_call(
                input=msgs,
                model="claude-4.5",
                tools=tool_schemas,
                thinking=True,
                stream=False,
            )

            thinking_block = next(
                (block for block in response.content if block.type == "thinking"), None
            )
            text_block = next(
                (block for block in response.content if block.type == "text"), None
            )
            tool_use_block = next(
                (block for block in response.content if block.type == "tool_use"), None
            )

            if thinking_block:
                yield {
                    "type": "tool_progress",
                    "toolName": "gekko_looper_",
                    "progress": f"Thinking...",
                    "percentage": progress_percentage,
                    "stream_id": stream_id,
                }

            if text_block:
                yield {
                    "type": "tool_progress",
                    "toolName": "gekko_looper_",
                    "progress": f"Writing notes...",
                    "percentage": progress_percentage,
                    "stream_id": stream_id,
                }

                if not thinking_block:
                    msgs.append({"role": "assistant", "content": text_block.text})

                if "<RESEARCH_COMPLETE>" in text_block.text:
                    msgs.append({"role": "assistant", "content": text_block.text})
                    stop_flag = True
                    break

            if tool_use_block:
                yield {
                    "type": "tool_progress",
                    "toolName": "gekko_looper_",
                    "progress": f"Using tool {tool_use_block.name}...",
                    "percentage": progress_percentage,
                    "stream_id": stream_id,
                }

                tool_output = None
                async for update in _execute_tool_call(
                    tool_use_block, user_id=user_id, stream_id=stream_id
                ):
                    if update["type"] == "tool_progress":
                        yield update
                    else:
                        tool_output = update["content"]
                        sources = update.get("sources", "")
                        max_tokens = update.get("max_tokens", 10000)
                        if sources:
                            all_sources.append(sources)

                msgs.append(
                    {"role": "assistant", "content": [thinking_block, tool_use_block]}
                )
                msgs.append(
                    {
                        "type": "function_call_output",
                        "call_id": tool_use_block.id,
                        "output": tool_output,
                    }
                )
                plan = _get_plan(user_id)
                if plan:
                    post_tool_reminder = get_post_tool_plan_reminder(
                        plan, tool_use_block.name
                    )
                    if post_tool_reminder:
                        msgs.append(
                            {
                                "role": "user",
                                "content": f"[⌘PLAN]: {post_tool_reminder}",
                            }
                        )

        except:
            yield {
                "type": "tool_progress",
                "toolName": "gekko_looper_",
                "progress": f"Failed...continuing next run..",
                "percentage": 10,
                "stream_id": stream_id,
            }

    complete_notes = []

    for m in msgs:
        if isinstance(m, dict) and m.get("role") == "assistant":
            content = m.get("content", "")
            if isinstance(content, str):
                complete_notes.append(content)
            # elif isinstance(content, list): ### intermediate thinking not useful
            #     for block in content:
            #         if hasattr(block, "thinking"):
            #             complete_notes.append(block.thinking)

    flatten_notes = "\n".join(complete_notes)

    yield {
        "type": "tool_progress",
        "toolName": "gekko_looper_",
        "progress": f"Starting final analysis..",
        "percentage": 75,
        "stream_id": stream_id,
    }

    analysis_request = f"""
{GORDOK_GEKKO}

Your analysts have performed deep analysis based on your client request:

Current datetime: {datetime.datetime.now().strftime("%B %d, %Y")}

<client_request>
{query}
</client_request>

<structure_analysis_result>
{flatten_notes}
</structure_analysis_result>

<financial_calculations>
{financial_context}
</financial_calculations>

<full_analysis_notes>
{full_plan}
</full_analysis_notes>

Your task is to review and provide final recommendation and identify hidden opportunities:

Think your analysis through. Take the time. Write succintly but cover everything.

For each stock, write your:

action = buy|sell|hold|short,
reasoning: explain your reasoning comprehensively,
numbers - back up and explain your reasoning with deep analysis of financial ratios,
conviction_level - high|medium|low,
price_target - $150.00,
key_catalysts - Q1 earnings, product launch,
primary_risks - regulatory, competition,
sector_outlook - what do you think of the sector,
valuation_assessment - undervalued|fairly_valued|overvalued,
momentum_indicators - positive|neutral|negative,
institutional_sentiment - bullish|neutral|bearish

Return your final analysis as JSON with this structure:

{{
"ticker": {{
        "action": "...",
        "reasoning": "...",
        "numbers": "...",
        "conviction_level": "...",
        "price_target": "...",
        "key_catalysts": "...",
        "primary_risks": "...",
        "sector_outlook": "...",
        "valuation_assessment": "...",
        "momentum_indicators": "...",
        "institutional_sentiment": "..."
    }}
...for each stock analyzed.
}} 

    """
    msgs: List[Dict[str, str]] = [
        {"role": "system", "content": analysis_request},
        {
            "role": "user",
            "content": f"Please start.",
        },
    ]

    try:
        response = await model_call(
            input=msgs,
            model="claude-4.5",
            thinking=True,
            stream=False,
        )
        reasoning = []
        extracted_json_data = {}

        thinking_block = next(
            (block for block in response.content if block.type == "thinking"),
            None,
        )
        text_block = next(
            (block for block in response.content if block.type == "text"), None
        )
        if thinking_block:
            yield {
                "type": "tool_progress",
                "toolName": "gekko_looper_",
                "progress": f"Thinking... {thinking_block.thinking[:50]}...",
                "percentage": 90,
                "stream_id": stream_id,
            }
            reasoning.append(thinking_block.thinking)

        if text_block:
            yield {
                "type": "tool_progress",
                "toolName": "gekko_looper_",
                "progress": f"Writing analysis...",
                "percentage": 90,
                "stream_id": stream_id,
            }

            extracted_deep_reasoning_json = extract_json_(text_block.text)
            for json_obj in extracted_deep_reasoning_json:
                if isinstance(json_obj, dict):
                    extracted_json_data.update(json_obj)
        if thinking:
            extracted_json_data["thinking_notes"] = "\n".join(reasoning)

    except:
        yield {
            "type": "tool_progress",
            "toolName": "gekko_looper_",
            "progress": f"Failed...continuing processing..",
            "percentage": 99,
            "stream_id": stream_id,
        }

    graph_json_data = {}
    if graph:
        graph_json_data = await graph_charter(
            query, financial_context, extracted_json_data
        )
        if not graph_json_data:
            graph_json_data = {}

    final_return = {
        "structured_data": (
            extracted_json_data if extracted_json_data else flatten_notes
        ),
        "graph": graph_json_data if graph else {},
        "sources": all_sources,
    }

    yield {
        "type": "tool_progress",
        "toolName": "gekko_looper_",
        "progress": f"Research complete.",
        "percentage": 90,
        "stream_id": stream_id,
    }

    yield {
        "type": "tool_result",
        "toolName": "gekko_looper_",
        "result": "Completed research...",
        "content": final_return,
        "sources": "",
        "tokens": 0,
        "stream_id": stream_id,
    }
