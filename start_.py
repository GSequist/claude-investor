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


async def main(query, no_turns, thinking, graph):
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
        f"[white]Analysis Depth:[/white] {no_turns} turns",
        border_style="green",
    )

    console.print(header)

    with progress:
        task_id = progress.add_task("Initializing Gordon Gekko...", total=100)

        async for update in gekko_looper_(
            query=query,
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
                    console.print("\n")
                    console.print(sources_panel)

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

    try:
        # Get query if not provided via args
        if not query:
            query = questionary.text(
                "What do you want me to research?",
                validate=lambda x: len(x.strip()) > 0 or "Query cannot be empty",
            ).ask()

        # Get number of turns if not provided via args
        if not no_turns:
            no_turns = questionary.select(
                "How deep should the analysis be?",
                instruction="\n[Space] to select • [Enter] to confirm",
                choices=[
                    questionary.Choice("Quick Analysis (20 turns)", value=20),
                    questionary.Choice("Standard Analysis (30 turns)", value=30),
                    questionary.Choice("Deep Analysis (50 turns)", value=50),
                    questionary.Choice("Custom", value="custom"),
                ],
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

            if no_turns == "custom":
                custom_turns = questionary.text(
                    "Enter number of analysis turns (20-100):",
                    validate=lambda x: x.isdigit()
                    and 20 <= int(x) <= 100
                    or "Please enter a number between 20 and 100",
                ).ask()
                no_turns = int(custom_turns)

        console.print(f"\n[green]Selected:[/green] {no_turns} analysis turns\n")

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

    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled by user. Exiting...[/yellow]")
        exit(0)

    keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
    keyboard_thread.start()
    try:
        asyncio.run(main(query, no_turns, thinking, graph))
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
