from colorama import Fore, Style
from tabulate import tabulate
import plotext as plt
import textwrap


def visualize_result(data: dict):
    """
    terminal visualization of the investment analysis
    """

    if not data or not isinstance(data, dict):
        print(f"{Fore.RED}No analysis data received{Style.RESET_ALL}")
        return

    # Extract thinking notes if present
    thinking_notes = data.get("thinking_notes", "")

    # Filter out non-ticker keys
    ticker_data = {
        k: v
        for k, v in data.items()
        if k not in ["thinking_notes"] and isinstance(v, dict)
    }

    if not ticker_data:
        print(f"{Fore.RED}No ticker analysis found{Style.RESET_ALL}")
        return

    # TABLE 1: Executive Summary - All tickers overview
    _render_summary_table(ticker_data)

    print(f"\n{Fore.GREEN}{'-' * 80}{Style.RESET_ALL}\n")

    # TABLE 2: Detailed Analysis - Individual ticker deep dives
    _render_detailed_analysis(ticker_data)

    # TABLE 3: Thinking Notes (if present)
    if thinking_notes and thinking_notes.strip():
        _render_thinking_notes(thinking_notes)


def _render_summary_table(ticker_data: dict):
    """Render executive summary table with all tickers"""

    print(f"{Fore.GREEN}{Style.BRIGHT}EXECUTIVE SUMMARY{Style.RESET_ALL}\n")

    summary_data = []
    for ticker, analysis in ticker_data.items():
        action = analysis.get("action", "UNKNOWN").upper()
        price_target = analysis.get("price_target", "N/A")
        conviction = analysis.get("conviction_level", "N/A").upper()

        # Extract key catalyst (first 40 chars)
        catalysts = analysis.get("key_catalysts", "No catalysts")
        key_catalyst = textwrap.shorten(catalysts, width=40, placeholder="...")

        # Get valuation assessment
        valuation = analysis.get("valuation_assessment", "N/A").upper()

        # Color the action
        action_colored = _color_action(action)

        summary_data.append(
            [
                f"{Fore.CYAN}{ticker}{Style.RESET_ALL}",
                action_colored,
                price_target,
                _color_sentiment(conviction),
                key_catalyst,
                _color_sentiment(valuation),
            ]
        )

    print(
        tabulate(
            summary_data,
            headers=[
                f"{Fore.GREEN}TICKER{Style.RESET_ALL}",
                f"{Fore.GREEN}ACTION{Style.RESET_ALL}",
                f"{Fore.GREEN}PRICE TARGET{Style.RESET_ALL}",
                f"{Fore.GREEN}CONVICTION{Style.RESET_ALL}",
                f"{Fore.GREEN}KEY CATALYST{Style.RESET_ALL}",
                f"{Fore.GREEN}VALUATION{Style.RESET_ALL}",
            ],
            tablefmt="grid",
            colalign=("center", "center", "center", "center", "left", "center"),
        )
    )


def _render_detailed_analysis(ticker_data: dict):
    """Render detailed analysis for each ticker"""

    print(f"{Fore.GREEN}{Style.BRIGHT}DETAILED ANALYSIS BY TICKER{Style.RESET_ALL}\n")

    for i, (ticker, analysis) in enumerate(ticker_data.items()):
        print(f"{Fore.CYAN}{Style.BRIGHT}{ticker} - DEEP DIVE{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'-' * 50}{Style.RESET_ALL}")

        # Recommendation summary
        action = analysis.get("action", "UNKNOWN").upper()
        price_target = analysis.get("price_target", "N/A")
        conviction = analysis.get("conviction_level", "N/A").upper()

        summary_data = [
            [_color_action(action), price_target, _color_sentiment(conviction)]
        ]

        print(
            tabulate(
                summary_data,
                headers=[
                    f"{Fore.GREEN}RECOMMENDATION{Style.RESET_ALL}",
                    f"{Fore.GREEN}PRICE TARGET{Style.RESET_ALL}",
                    f"{Fore.GREEN}CONVICTION{Style.RESET_ALL}",
                ],
                tablefmt="grid",
            )
        )

        # Detailed analysis
        details_data = [
            [
                "INVESTMENT THESIS",
                _wrap_text(analysis.get("reasoning", "No reasoning provided")),
            ],
            [
                "NUMBERS",
                _wrap_text(analysis.get("numbers", "No numbers provided")),
            ],
            [
                "KEY CATALYSTS",
                _wrap_text(analysis.get("key_catalysts", "No catalysts identified")),
            ],
            [
                "PRIMARY RISKS",
                _wrap_text(analysis.get("primary_risks", "No risks identified")),
            ],
            [
                "SECTOR OUTLOOK",
                _wrap_text(analysis.get("sector_outlook", "No sector analysis")),
            ],
            [
                "VALUATION ASSESSMENT",
                _wrap_text(
                    analysis.get("valuation_assessment", "No valuation analysis")
                ),
            ],
            [
                "MOMENTUM INDICATORS",
                _wrap_text(analysis.get("momentum_indicators", "No momentum analysis")),
            ],
            [
                "INSTITUTIONAL SENTIMENT",
                _wrap_text(
                    analysis.get("institutional_sentiment", "No sentiment analysis")
                ),
            ],
        ]

        print(f"\n{tabulate(details_data, tablefmt='grid', colalign=('left', 'left'))}")

        # Separator between tickers
        if i < len(ticker_data) - 1:
            print(f"\n{Fore.GREEN}{'-' * 80}{Style.RESET_ALL}\n")


def _color_action(action: str) -> str:
    """Color the action appropriately"""
    colors = {
        "BUY": Fore.GREEN,
        "SELL": Fore.RED,
        "HOLD": Fore.YELLOW,
        "SHORT": Fore.RED,
        "TRIM": Fore.RED,
    }
    color = colors.get(action, Fore.WHITE)
    return f"{color}{action}{Style.RESET_ALL}"


def _color_sentiment(sentiment: str) -> str:
    """Color the sentiment/conviction/valuation"""
    sentiment_upper = sentiment.upper()
    colors = {
        "HIGH": Fore.GREEN,
        "MEDIUM": Fore.YELLOW,
        "LOW": Fore.RED,
        "POSITIVE": Fore.GREEN,
        "NEUTRAL": Fore.YELLOW,
        "NEGATIVE": Fore.RED,
        "UNDERVALUED": Fore.GREEN,
        "FAIRLY_VALUED": Fore.YELLOW,
        "OVERVALUED": Fore.RED,
        "BULLISH": Fore.GREEN,
        "BEARISH": Fore.RED,
    }
    color = colors.get(sentiment_upper, Fore.WHITE)
    return f"{color}{sentiment_upper}{Style.RESET_ALL}"


def _render_thinking_notes(thinking_notes: str):
    """Render the thinking notes section beautifully"""

    print(f"\n{Fore.GREEN}{'-' * 80}{Style.RESET_ALL}\n")
    print(f"{Fore.GREEN}{Style.DIM}Pocket Gekko's thinking:{Style.RESET_ALL}\n")

    # Split into paragraphs and format nicely
    paragraphs = thinking_notes.split("\n\n")

    for i, paragraph in enumerate(paragraphs):
        if paragraph.strip():
            # Clean up the paragraph
            clean_paragraph = paragraph.strip().replace("\n", " ")
            # Wrap to readable width
            wrapped = textwrap.fill(
                clean_paragraph, width=90, initial_indent="  ", subsequent_indent="  "
            )
            print(f"{Fore.CYAN}{Style.DIM}{wrapped}{Style.RESET_ALL}")

            # Add spacing between paragraphs (but not after the last one)
            if i < len(paragraphs) - 1:
                print()

    print(f"\n{Fore.GREEN}{'-' * 80}{Style.RESET_ALL}")


def _wrap_text(text: str, width: int = 70) -> str:
    """Wrap text to specified width"""
    if not text or text.strip() == "":
        return "No information available"

    return textwrap.fill(text, width=width, subsequent_indent="  ")
