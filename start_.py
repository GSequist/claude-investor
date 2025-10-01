from utils.visualize_result_ import visualize_result
from utils.visualize_graph_ import visualize_graph
from utils.token_counter_ import calculate_costs
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
from dotenv import load_dotenv, set_key
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
import questionary
import os
import sys
import termios
import tty
import select
import threading
import asyncio
import time
import os


load_dotenv()

###########################################################################


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


###########################################################################


def display_header(settings):
    """Display rich formatted header and settings"""
    console = Console()
    width = console.width

    console.print()  ##gap

    combined_text = Text()
    combined_text.append("◉ Pocket Gekko Analyst", style="bold white")
    combined_text.append("\n")
    combined_text.append("\n")
    combined_text.append(
        f"Settings: turns={settings['no_turns']}, thinking={'on' if settings['thinking'] else 'off'}, graph={'on' if settings['graph'] else 'off'}",
        style="dim",
    )

    # Put in single panel that fits content
    combined_panel = Panel.fit(combined_text, border_style="white")
    console.print(combined_panel)

    console.print()  ##gap

    console.print(
        "[dim]Type your query and press Enter | ESC to quit | / for commands[/dim]"
    )

    console.print("─" * width, style="dim")


###########################################################################


def keyboard_listener(settings, input_buffer, input_ready):
    """Enhanced keyboard listener that handles all input and commands"""
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setraw(sys.stdin.fileno())

    try:
        while True:
            # Check if we should stop the listener
            if settings.get("_stop_listener", False):
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                return  # Exit keyboard listener cleanly

            if select.select([sys.stdin], [], [], 0.1)[0]:
                char = sys.stdin.read(1)

                # ESC key - immediate exit
                if char == "\x1b":
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    print("\nESC pressed - exiting")
                    os._exit(0)

                # Enter key - submit input
                elif char == "\r" or char == "\n":
                    if input_buffer["text"].strip():
                        input_ready["ready"] = True
                        print()  # New line after input

                # Backspace
                elif char == "\x7f":
                    if input_buffer["text"]:
                        input_buffer["text"] = input_buffer["text"][:-1]
                        print(
                            "\r" + " " * 80 + "\r> " + input_buffer["text"],
                            end="",
                            flush=True,
                        )

                # Forward slash for commands
                elif char == "/":
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

                    # Clear screen to remove questionnaire clutter
                    os.system("clear" if os.name == "posix" else "cls")

                    # Redisplay current status with Rich formatting
                    display_header(settings)
                    print("\n📋 Choose an option:")
                    choice = questionary.select(
                        "What would you like to do?",
                        choices=[
                            "Change number of turns",
                            "Toggle thinking mode",
                            "Toggle graph mode",
                            "Show current settings",
                            "Back to input",
                        ],
                    ).ask()

                    if choice == "Change number of turns":
                        new_turns = no_turns_questionnaire()
                        settings["no_turns"] = new_turns
                        print(f"✅ Turns updated to: {new_turns}")
                    elif choice == "Toggle thinking mode":
                        new_thinking = thinking_questionnaire()
                        settings["thinking"] = new_thinking
                        print(f"✅ Thinking mode: {'on' if new_thinking else 'off'}")
                    elif choice == "Toggle graph mode":
                        new_graph = graph_questionnaire()
                        settings["graph"] = new_graph
                        print(f"✅ Graph mode: {'on' if new_graph else 'off'}")
                    elif choice == "Show current settings":
                        print(
                            f"Current settings: turns={settings['no_turns']}, thinking={settings['thinking']}, graph={settings['graph']}"
                        )
                    elif choice == "Back to input":
                        pass  # Just continue to return to input

                    # Clear screen again for clean return to input
                    os.system("clear" if os.name == "posix" else "cls")

                    # Redisplay current status with updated settings using Rich
                    display_header(settings)

                    # Return to input mode cleanly
                    if input_buffer["text"]:
                        print(f"> {input_buffer['text']}", end="", flush=True)
                    else:
                        print("> ", end="", flush=True)

                    tty.setraw(sys.stdin.fileno())

                # Regular characters
                elif ord(char) >= 32 and ord(char) < 127:
                    input_buffer["text"] += char
                    print(char, end="", flush=True)

    except Exception as e:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        print(f"\n⚠️ Keyboard error: {e}")
        os._exit(0)


###########################################################################


def no_turns_questionnaire():
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
    return no_turns


def thinking_questionnaire():
    thinking = questionary.confirm(
        "Do you want to see Gordon Gekko's detailed thinking process?",
        default=False,
    ).ask()
    return thinking


def graph_questionnaire():
    graph = questionary.confirm(
        "Do you want also a chart?",
        default=False,
    ).ask()
    return graph


###########################################################################


async def main(query, no_turns, thinking, graph, user_id, stream_id):

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        refresh_per_second=4,
    )

    settings = {"no_turns": no_turns, "thinking": thinking, "graph": graph}
    display_header(settings)
    input_buffer = {"text": ""}
    input_ready = {"ready": False}

    # Start keyboard listener immediately - it handles all input
    keyboard_thread = threading.Thread(
        target=keyboard_listener,
        args=(settings, input_buffer, input_ready),
        daemon=True,
    )
    keyboard_thread.start()

    # Show prompt and wait for input through keyboard listener
    print("> ", end="", flush=True)

    # Wait for user to press Enter
    while not input_ready["ready"]:
        time.sleep(0.1)

    user_query = input_buffer["text"]
    if not user_query.strip():
        console.print("[yellow]No query entered. Exiting...[/yellow]")
        return

    with progress:
        task_id = progress.add_task("Initializing Gordon Gekko...", total=100)

        async for update in gekko_looper_(
            query=user_query,  # Use actual user query
            no_turns=settings["no_turns"],
            # no_turns=10,
            thinking=settings["thinking"],
            graph=settings["graph"],
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

                # STOP keyboard listener and exit raw mode BEFORE visualization
                settings["_stop_listener"] = True
                time.sleep(0.5)  # Give keyboard thread time to exit raw mode

                # Ensure terminal is in normal mode for visualizations
                old_settings = termios.tcgetattr(sys.stdin)
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

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


###########################################################################

if __name__ == "__main__":

    console = Console()

    if not check_and_setup_env():
        console.print("[red]❌ Environment setup failed. Exiting...[/red]")
        exit(1)

    ### def placeholders
    user_id = "local_user"
    stream_id = "stream"
    query = ""
    no_turns = 30
    thinking = False
    graph = False

    try:
        asyncio.run(main(query, no_turns, thinking, graph, user_id, stream_id))
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
