from models_anthropic_ import model_call
from utils.utils import extract_json_
from tools.sec_tools_ import sec_fetch_metrics_structured
from utils.quant_ import calculate_all_ratios, calculate_peer_benchmarks
from utils.stock_price_ import get_price
import asyncio


async def precalculate_ratios(query, user_id):
    financial_context = ""
    try:
        response = await model_call(
            input=f"""
Review this user request and extract any company tickers or exact company name as they appear in SEC filings. 
Define peer ticker up to 3 peers.
Return this exact JSON:

{{
    company_name: {{
        ticker: ticker you found
        peer_one: peer ticker
        peer_two: peer ticker (OPTIONAL) 
        peer_three: peer ticker (OPTIONAL) 
    }}
    company_name: {{
        ticker: ticker you found
        peer_one: peer ticker
        peer_two: peer ticker (OPTIONAL) 
        peer_three: peer ticker (OPTIONAL) 
    }}
    ...and so on for each company
}}

If there are none respond with simple "NONE".

The user request:
{query}
            """,
            model="claude-3.5",
            stream=False,
        )
        raw_resp = response.content[0].text

        if "NONE" not in raw_resp:
            json_resp = extract_json_(raw_resp)
            all_analyses = []

            if json_resp:
                companies_data = json_resp[0] if json_resp else {}
                for company_name, item in companies_data.items():
                    try:
                        # Get primary company data
                        ticker_current_data, *_ = sec_fetch_metrics_structured(
                            company_name=item["ticker"], user_id=user_id
                        )
                        ticker_calcs = calculate_all_ratios(
                            ticker_current_data, user_id=user_id
                        )
                        ticker_price = get_price(item["ticker"])

                        await asyncio.sleep(1)  ### SEC

                        ### Get peer data with null checks
                        peer_calcs = []
                        peer_tickers = []

                        # Peer one (required)
                        if "peer_one" in item and item["peer_one"]:
                            peer_one_data, *_ = sec_fetch_metrics_structured(
                                company_name=item["peer_one"], user_id=user_id
                            )
                            peer_one_calcs = calculate_all_ratios(
                                peer_one_data, stock_price=ticker_price, user_id=user_id
                            )
                            peer_calcs.append(peer_one_calcs)
                            peer_tickers.append(item["peer_one"])

                        await asyncio.sleep(1)  ### SEC

                        # Peer two (optional)
                        if "peer_two" in item and item["peer_two"]:
                            peer_two_data, *_ = sec_fetch_metrics_structured(
                                company_name=item["peer_two"], user_id=user_id
                            )
                            peer_two_calcs = calculate_all_ratios(
                                peer_two_data, user_id=user_id
                            )
                            peer_calcs.append(peer_two_calcs)
                            peer_tickers.append(item["peer_two"])

                        await asyncio.sleep(1)  ### SEC

                        # Peer three (optional)
                        if "peer_three" in item and item["peer_three"]:
                            peer_three_data, *_ = sec_fetch_metrics_structured(
                                company_name=item["peer_three"], user_id=user_id
                            )
                            peer_three_calcs = calculate_all_ratios(
                                peer_three_data, user_id=user_id
                            )
                            peer_calcs.append(peer_three_calcs)
                            peer_tickers.append(item["peer_three"])

                        peer_benchmarks = calculate_peer_benchmarks(
                            ticker_calcs, peer_calcs
                        )

                        # Format analysis text with ALL calculations
                        analysis_text = (
                            f"\n=== FINANCIAL ANALYSIS: {item['ticker']} ===\n"
                        )

                        # Show ALL calculated ratios first
                        analysis_text += "\n--- ALL CALCULATED RATIOS ---\n"
                        if ticker_calcs.get("ratios"):
                            for ratio, value in ticker_calcs["ratios"].items():
                                if isinstance(value, float):
                                    analysis_text += f"- {ratio}: {value:.2f}\n"
                                else:
                                    analysis_text += f"- {ratio}: {value}\n"

                        # Then show peer comparison for key ratios
                        key_ratios = [
                            "roe",
                            "roa",
                            "current_ratio",
                            "debt_to_equity",
                            "operating_margin",
                            "net_margin",
                            "free_cash_flow",
                            "asset_turnover",
                        ]
                        analysis_text += f"\n--- PEER COMPARISON (vs {len(peer_tickers)} peers) ---\n"

                        for ratio in key_ratios:
                            if ratio in peer_benchmarks.get("peer_analysis", {}):
                                bench_data = peer_benchmarks["peer_analysis"][ratio]
                                analysis_text += (
                                    f"- {ratio}: {bench_data['company_value']:.2f} "
                                )
                                analysis_text += (
                                    f"(peer median: {bench_data['peer_median']:.2f}, "
                                )
                                analysis_text += (
                                    f"rank: {bench_data['percentile_rank']:.0f}%, "
                                )
                                analysis_text += (
                                    f"{bench_data['performance_vs_peers']})\n"
                                )
                            elif ratio in ticker_calcs.get("ratios", {}):
                                value = ticker_calcs["ratios"][ratio]
                                if isinstance(value, float):
                                    analysis_text += (
                                        f"- {ratio}: {value:.2f} (no peer data)\n"
                                    )

                        # Show peer raw data
                        analysis_text += f"\n--- PEER RAW DATA ---\n"
                        for i, (peer_calc, peer_ticker) in enumerate(
                            zip(peer_calcs, peer_tickers)
                        ):
                            analysis_text += f"\n{peer_ticker} Key Ratios:\n"
                            if peer_calc.get("ratios"):
                                for ratio in key_ratios:
                                    if ratio in peer_calc["ratios"]:
                                        value = peer_calc["ratios"][ratio]
                                        if isinstance(value, float):
                                            analysis_text += (
                                                f"  - {ratio}: {value:.2f}\n"
                                            )

                        all_analyses.append(analysis_text)

                    except Exception as e:
                        all_analyses.append(
                            f"\n=== ERROR ANALYZING {item.get('ticker', 'UNKNOWN')}: {str(e)} ===\n"
                        )

            financial_context = "\n".join(all_analyses)

    except Exception as e:
        print(f"Error calculating {e}")
        financial_context = ""

    return financial_context
