import json
from datetime import datetime
from collections import defaultdict

# Constants for pricing per million tokens
PRICING = {
    "claude-sonnet-4-20250514": {
        "input": 3.0,  # $3 per 1M input tokens
        "output": 15.0,  # $15 per 1M output tokens
    },
    "claude-3-5-haiku-20241022": {
        "input": 0.25,  # $0.25 per 1M input tokens
        "output": 1.25,  # $1.25 per 1M output tokens
    },
    "claude-3-7-sonnet-20250219": {
        "input": 3.0,  # $3 per 1M input tokens (assuming same as claude-4)
        "output": 15.0,  # $15 per 1M output tokens
    },
}


def calculate_costs(file_path="utils/token_usage.json"):
    """Calculate costs by model, handling mixed model usage correctly"""
    model_stats = defaultdict(lambda: {"input": 0, "output": 0, "calls": 0})

    try:
        with open(file_path, "r") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    model = data["model"]
                    model_stats[model]["input"] += data["input"]
                    model_stats[model]["output"] += data["output"]
                    model_stats[model]["calls"] += 1
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print(f"Token usage file {file_path} not found")
        return

    if not model_stats:
        print("No token usage data found")
        return

    print(f"\n=== Token Usage Summary ===")

    total_cost = 0
    total_input = 0
    total_output = 0
    total_calls = 0

    for model, stats in model_stats.items():
        if model not in PRICING:
            print(f"Warning: Unknown model '{model}' - skipping cost calculation")
            continue

        input_cost = (stats["input"] / 1_000_000) * PRICING[model]["input"]
        output_cost = (stats["output"] / 1_000_000) * PRICING[model]["output"]
        model_cost = input_cost + output_cost

        print(f"\n--- {model} ---")
        print(f"API Calls: {stats['calls']:,}")
        print(f"Input Tokens: {stats['input']:,}")
        print(f"Output Tokens: {stats['output']:,}")
        print(f"Input Cost: ${input_cost:.4f}")
        print(f"Output Cost: ${output_cost:.4f}")
        print(f"Model Total: ${model_cost:.4f}")

        total_cost += model_cost
        total_input += stats["input"]
        total_output += stats["output"]
        total_calls += stats["calls"]

    print(f"\n=== Overall Summary ===")
    print(f"Total API Calls: {total_calls:,}")
    print(f"Total Input Tokens: {total_input:,}")
    print(f"Total Output Tokens: {total_output:,}")
    print(f"Total Cost: ${total_cost:.4f}")


if __name__ == "__main__":
    calculate_costs()
