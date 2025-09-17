from utils.visualize_result_ import visualize_result
from utils.visualize_graph_ import visualize_graph
from utils.token_counter_ import calculate_costs
from utils.utils import keyboard_listener
from colorama import Fore, Style, init
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)
from pocket_gekko import gekko_looper_
from rich.panel import Panel
from rich.live import Live
import questionary
import argparse
import threading
from dotenv import load_dotenv, set_key
import asyncio
import os


load_dotenv()


def check_and_setup_env():
    """Check for required environment variables and prompt for missing ones"""
    required_vars = {
        "ANTHROPIC_API_KEY": "Anthropic API Key (from console.anthropic.com)",
        "SERPAPI_KEY": "SerpAPI Key (from serpapi.com for web search)",
        "USER_NAME_FOR_SEC": "Application name for SEC API (e.g., 'MyCompany email@company.com')",
        "EMAIL_FOR_SEC": "Email address for SEC API requests",
    }

    missing_vars = []
    env_file_path = ".env"

    # Check which variables are missing or empty
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if not value or value.strip() == "":
            missing_vars.append((var_name, description))

    if missing_vars:
        console.print(
            Panel.fit(
                "[bold red]⚠️  Missing Required Environment Variables[/bold red]\n"
                "[yellow]The following environment variables need to be set:[/yellow]",
                border_style="red",
            )
        )

        # Prompt for each missing variable
        for var_name, description in missing_vars:
            console.print(f"\n[cyan]Setting up {var_name}:[/cyan]")
            console.print(f"[dim]{description}[/dim]")

            if var_name.endswith("_KEY"):
                # Hide API keys while typing
                value = questionary.password(f"Enter {var_name}:").ask()
            else:
                value = questionary.text(f"Enter {var_name}:").ask()

            if value and value.strip():
                try:
                    # Write to .env file
                    set_key(env_file_path, var_name, value.strip())
                    console.print(f"[green]✅ {var_name} saved to .env[/green]")
                    # Update current environment
                    os.environ[var_name] = value.strip()
                except Exception as e:
                    console.print(f"[red]❌ Error saving {var_name}: {str(e)}[/red]")
                    console.print(
                        f"[yellow]Please manually add to .env file: {var_name}={value.strip()}[/yellow]"
                    )
            else:
                console.print(f"[red]❌ {var_name} cannot be empty[/red]")
                return False

        console.print(
            Panel.fit(
                "[bold green]✅ Environment setup complete![/bold green]\n"
                "[dim]Variables saved to .env file[/dim]",
                border_style="green",
            )
        )

    return True


async def main(query, no_turns, thinking, graph, style):
    user_id = "local_user"
    stream_id = "stream"

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        refresh_per_second=4,
    )

    header = Panel.fit(
        f"[bold green]Pocket Gekko Analyst[/bold green]\n"
        f"[white]Query:[/white] {query}\n"
        f"[white]Style:[/white] {', '.join(s.replace('_', ' ').title() for s in style)}",
        border_style="green",
    )

    console.print(header)

    with progress:
        task_id = progress.add_task("Initializing Gordon Gekko...", total=100)

        async for update in gekko_looper_(
            query=query,
            style=style,
            no_turns=no_turns or 30,
            thinking=thinking,
            graph=graph,
            user_id=user_id,
            stream_id=stream_id,
        ):
            if update.get("type") == "tool_progress":
                progress_text = update.get("progress", "Processing...")
                percentage = update.get("percentage", 0)
                progress.update(
                    task_id, description=progress_text, completed=percentage
                )

            elif update.get("type") == "tool_result":
                progress.update(
                    task_id, completed=100, description="Analysis Complete!"
                )
                console.print("\n[green]Analysis complete![/green]")
                result_content = update.get("content", {})
                if (
                    isinstance(result_content, dict)
                    and "structured_data" in result_content
                ):
                    console.print("\n[yellow]Displaying analysis results...[/yellow]\n")
                    visualize_result(result_content["structured_data"])
                    visualize_graph(result_content["graph"])

                    sources_panel = Panel.fit(
                        f"[italic white]Sources Used[/italic white]\n"
                        f"[italic white]{result_content.get('sources', 'No sources available')}[/italic white]",
                        border_style="blue",
                    )
                    console.print(f"\n{sources_panel}")
                tokens = calculate_costs()
                console.print(tokens)
                break


if __name__ == "__main__":

    console = Console()

    console.print(
        Panel.fit(
            "[bold green]Pocket Gekko Analyst[/bold green]\n"
            "[italic]Greed is good. Choose your style.[/italic]\n"
            "[bold red]Press q + Enter at any time to exit[/bold red]",
            border_style="green",
        )
    )

    # Check and setup environment variables
    if not check_and_setup_env():
        console.print("[red]❌ Environment setup failed. Exiting...[/red]")
        exit(1)

    parser = argparse.ArgumentParser(
        description="--init Gordon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--query",
        type=str,
        help="Investment analysis query (company names, sectors, themes, other like your investment situation)",
    )
    parser.add_argument("--no_turns", type=int, help="How many turns")
    parser.add_argument(
        "--thinking", action="store_true", help="Show Gekko's thinking process"
    )
    parser.add_argument(
        "--graph", action="store_true", help="Should Gekko create a chart?"
    )
    args = parser.parse_args()

    query = args.query
    no_turns = args.no_turns
    thinking = args.thinking
    graph = args.graph

    # Get query if not provided via args
    if not query:
        query = questionary.text(
            "What investment opportunity shall we hunt?",
            validate=lambda x: len(x.strip()) > 0 or "Query cannot be empty",
        ).ask()

    # Get number of turns if not provided via args
    if not no_turns:
        no_turns = questionary.select(
            "How deep should the analysis be?",
            choices=[
                questionary.Choice("Quick Analysis (5 turns)", value=5),
                questionary.Choice("Standard Analysis (15 turns)", value=15),
                questionary.Choice("Deep Analysis (30 turns)", value=30),
                questionary.Choice("Custom", value="custom"),
            ],
            default="📊 Standard Analysis (15 turns)",
        ).ask()

        if no_turns == "custom":
            no_turns = questionary.int(
                "Enter number of analysis turns (30-100):",
                validate=lambda x: 30 <= x <= 100 or "Minimum recommended 30",
            ).ask()

    # Get thinking preference if not provided via args
    if not thinking:  # This handles both None and False from store_true
        thinking = questionary.confirm(
            "Do you want to see Gordon Gekko's detailed thinking process?",
            default=False,
        ).ask()

    if not graph:  # This handles both None and False from store_true
        graph = questionary.confirm(
            "Do you want also a chart?",
            default=False,
        ).ask()

    STYLES = {
        "deep_analysis": {
            "logic": "Perform deep analysis starting with broader news affecting industry/sector then company news and finally deep down on SEC reports and financial news and indicators."
        },
        "medium_analysis": {
            "logic": "You have limited time, so focus on company/industry news and proceed with getting data from SEC and performing calculations."
        },
        "light_analysis": {
            "logic": "You have very short time. The client wants an answer in an hour. Just pull the company metrics and basic data from SEC reports and perform calculations."
        },
    }

    choices = questionary.checkbox(
        "Choose the analysis style.",
        choices=[
            questionary.Choice(f"🎯 {key.replace('_', ' ').title()}", value=key)
            for key in STYLES
        ],
        instruction="\n[Space] to select • [a] to select all • [Enter] to confirm",
        validate=lambda x: len(x) > 0 or "You must select at least one style.",
        style=questionary.Style(
            [
                ("checkbox-selected", "fg:green bold"),
                ("selected", "fg:green"),
                ("highlighted", "fg:yellow bold"),
                ("pointer", "fg:green bold"),
                ("instruction", "fg:cyan"),
            ]
        ),
    ).ask()

    selected_style = choices
    console.print(
        f"\n[green]Selected:[/green] {', '.join(choice.replace('_', ' ').title() for choice in choices)}\n"
    )

    keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
    keyboard_thread.start()
    try:
        style_logic = [STYLES[style]["logic"] for style in selected_style]
        asyncio.run(main(query, no_turns, thinking, graph, style_logic))
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
