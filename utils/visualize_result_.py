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


def test():
    data = {
        "AAPL": {
            "action": "buy",
            "reasoning": "Strong fundamentals with iPhone 16 cycle driving revenue growth. Trading at discount to historical P/E multiple with robust services growth.",
            "conviction_level": "high",
            "price_target": "$230.00",
            "key_catalysts": "iPhone 16 launch, AI integration, services revenue expansion",
            "primary_risks": "China trade tensions, regulatory pressure on App Store",
            "sector_outlook": "Technology sector showing resilience despite macro headwinds",
            "valuation_assessment": "undervalued",
            "momentum_indicators": "positive",
            "institutional_sentiment": "bullish",
        },
        "TSLA": {
            "action": "sell",
            "reasoning": "Overvalued at current levels with slowing EV growth and increasing competition from traditional automakers",
            "conviction_level": "medium",
            "price_target": "$180.00",
            "key_catalysts": "Cybertruck production ramp, FSD progress",
            "primary_risks": "High valuation, competition, regulatory scrutiny",
            "sector_outlook": "EV market experiencing growth slowdown and margin compression",
            "valuation_assessment": "overvalued",
            "momentum_indicators": "negative",
            "institutional_sentiment": "bearish",
        },
        "thinking_notes": """Looking at both Apple and Tesla, I need to consider the broader market dynamics and valuation frameworks that drive my investment thesis.

For Apple, the key insight is that despite trading at what appears to be a premium valuation, the company's moat in the premium consumer electronics space remains unassailable. The services revenue growth trajectory - now representing over 20% of total revenue - provides predictable recurring income that traditional hardware-focused valuations miss.

The iPhone replacement cycle dynamics are fascinating. While unit growth has plateaued in mature markets, the average selling price continues to climb due to AI integration and premium features. This mirrors the luxury goods playbook - fewer units at higher margins.

Tesla presents a completely different investment case. The company benefited enormously from first-mover advantage in premium EVs, but that advantage is rapidly eroding. Traditional automakers have caught up on build quality while Chinese manufacturers are competing aggressively on price.

Most concerning for Tesla is the valuation disconnect. The stock still trades on growth multiples despite decelerating fundamentals. Musk's diversification into AI and robotics, while potentially valuable long-term, doesn't justify current automotive valuations when core auto margins are compressing.""",
    }
    visualize_result(data)


if __name__ == "__main__":
    test()
