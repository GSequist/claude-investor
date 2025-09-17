from models_anthropic_ import model_call
from utils.utils import extract_json_
from typing import List, Dict
import json


async def graph_charter(query, financial_context, extracted_json_data):
    formatted_structured_data = json.dumps(extracted_json_data, indent=2)
    graph_request = f"""
    Your task is to review the financial analysis below.
    Propose a chart that would further aid the analysis.
    You will be given to financial ratios and analysis performed by your team.

    <client_request>
    {query}
    </client_request>

    <financial_calculations>
    {financial_context}
    </financial_calculations>

    <structured_analysis>
    {formatted_structured_data}
    </structured_analysis>

    Return JSON which will be rendered as a chart in this exact structure:

    {{
    "graph": {{
        "type": "line|bar|scatter|multi_line|grouped_bar",
        "title": "Chart Title",
        "x_label": "X-axis label",
        "y_label": "Y-axis label",
        "data": {{
            "x": ["Category1", "Category2", "Category3"],
            "y": [100, 120, 115],
            "series": [
                {{
                    "name": "Series 1",
                    "values": [100, 120, 115],
                    "color": "green|red|blue|yellow"
                }}
            ],
            "annotations": [
                {{
                    "x": "Category2",
                    "y": 120,
                    "text": "Peak value"
                }}
            ]
        }},
        "insights": "Key insights about what this chart reveals about the investment opportunity"
        }}
    }} 

        """
    msgs: List[Dict[str, str]] = [
        {"role": "system", "content": graph_request},
        {
            "role": "user",
            "content": f"Please start.",
        },
    ]

    try:
        response = await model_call(
            input=msgs,
            model="claude-4",
            thinking=True,
            stream=False,
        )

        graph_json_data = {}

        thinking_block = next(
            (block for block in response.content if block.type == "thinking"),
            None,
        )
        text_block = next(
            (block for block in response.content if block.type == "text"), None
        )

        if text_block:
            graph_json = extract_json_(text_block.text)
            for json_obj in graph_json:
                if isinstance(json_obj, dict):
                    graph_json_data.update(json_obj)

        return graph_json_data
    except Exception as e:
        print(f"Error generating chart: {str(e)}")
        return {}
