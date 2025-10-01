from classes._md_convert import MarkdownConverter
from utils.utils import tokenizer
from dotenv import load_dotenv
import requests
import time
import json
import os

load_dotenv()


#############################################


def get_cik(company_identifier):
    """util to extract SEC CIK from ticker/exact co. name"""

    headers = {
        "User-Agent": f"{os.getenv("USER_NAME_FOR_SEC")} {os.getenv("EMAIL_FOR_SEC")}",
        "Accept": "application/json",
    }

    tickers_url = "https://www.sec.gov/files/company_tickers.json"
    tickers_response = requests.get(tickers_url, headers=headers, timeout=30)
    tickers_response.raise_for_status()
    tickers_data = tickers_response.json()

    time.sleep(0.2)

    ### find company CIK
    cik = None
    identifier_lower = company_identifier.lower()
    for key, company_info in tickers_data.items():
        if (
            identifier_lower in company_info["title"].lower()
            or identifier_lower == company_info["ticker"].lower()
        ):
            cik = str(company_info["cik_str"]).zfill(10)
            break

    if not cik:
        return None

    return cik


########################################################################


def extract_metric_from_xbrl(
    facts_data, metric_name, target_year=None, target_form=None
):
    """Extract specific metric from SEC XBRL facts data with precise filtering

    Args:
        facts_data: Raw SEC XBRL facts JSON data
        metric_name: Exact XBRL concept name (e.g., "Revenues", "NetIncomeLoss")
        target_year: Specific fiscal year to filter (e.g., 2023)
        target_form: Specific form type to filter (e.g., "10-K", "10-Q")

    Returns:
        Dictionary with metric data or None if not found
    """

    ### Search in US-GAAP taxonomy first
    us_gaap_data = facts_data.get("facts", {}).get("us-gaap", {}).get(metric_name, {})

    if us_gaap_data:
        units_data = us_gaap_data.get("units", {})

        ### Try different unit types in order of preference
        for unit_type in ["USD", "shares", "USD/shares", "pure"]:
            if unit_type in units_data:
                values = units_data[unit_type]

                filtered_values = values

                if target_year is not None:
                    target_year_int = (
                        int(target_year)
                        if isinstance(target_year, str)
                        else target_year
                    )
                    filtered_values = [
                        v for v in filtered_values if v.get("fy") == target_year_int
                    ]

                if target_form is not None:
                    filtered_values = [
                        v for v in filtered_values if v.get("form") == target_form
                    ]

                if filtered_values:
                    latest_value = max(filtered_values, key=lambda x: x.get("end", ""))

                    return {
                        "concept": metric_name,
                        "label": us_gaap_data.get("label", metric_name),
                        "description": us_gaap_data.get("description", ""),
                        "value": latest_value.get("val"),
                        "unit": unit_type,
                        "start_date": latest_value.get("start"),
                        "end_date": latest_value.get("end"),
                        "fiscal_year": latest_value.get("fy"),
                        "fiscal_period": latest_value.get("fp"),
                        "form": latest_value.get("form"),
                        "accession": latest_value.get("accn"),
                        "taxonomy": "us-gaap",
                    }

    ### Search in DEI taxonomy if not found in US-GAAP
    dei_data = facts_data.get("facts", {}).get("dei", {}).get(metric_name, {})

    if dei_data:
        units_data = dei_data.get("units", {})

        for unit_type in units_data:
            values = units_data[unit_type]

            filtered_values = values

            if target_year is not None:
                target_year_int = (
                    int(target_year) if isinstance(target_year, str) else target_year
                )
                filtered_values = [
                    v for v in filtered_values if v.get("fy") == target_year_int
                ]

            if target_form is not None:
                filtered_values = [
                    v for v in filtered_values if v.get("form") == target_form
                ]

            if filtered_values:
                latest_value = max(filtered_values, key=lambda x: x.get("end", ""))

                return {
                    "concept": metric_name,
                    "label": dei_data.get("label", metric_name),
                    "description": dei_data.get("description", ""),
                    "value": latest_value.get("val"),
                    "unit": unit_type,
                    "start_date": latest_value.get("start"),
                    "end_date": latest_value.get("end"),
                    "fiscal_year": latest_value.get("fy"),
                    "fiscal_period": latest_value.get("fp"),
                    "form": latest_value.get("form"),
                    "accession": latest_value.get("accn"),
                    "taxonomy": "dei",
                }

    return None


########################################################################


def sec_fetch_metrics_structured(
    company_name: str,
    metrics: list = "all",
    target_year: int = None,
    target_form: str = None,
    *,
    user_id: str,
) -> str:
    """Fetch financial metrics from SEC XBRL data - fetches all available metrics by default and returns as structure dictionary - method used for predetermined calcs
    #parameters:
    company_name: exact company name as it appears in SEC filings or ticker symbol or a ticker, example: Apple Inc. or AAPL
    metrics: list of exact XBRL concept names or "all" to fetch all available metrics (default: "all")
    target_year: specific fiscal year to filter (e.g., 2023), if None gets most recent
    target_form: specific form type to filter (e.g., "10-K", "10-Q"), if None gets any form
    """
    max_tokens = 30000

    cik = get_cik(company_name)

    if not cik:
        return (
            f"Company '{company_name}' not found in SEC database.",
            "",
            "",
            max_tokens,
        )

    headers = {
        "User-Agent": f"{os.getenv("USER_NAME_FOR_SEC")} {os.getenv("EMAIL_FOR_SEC")}",
        "Accept": "application/json",
    }

    try:
        # Get XBRL facts data
        facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        facts_response = requests.get(facts_url, headers=headers, timeout=30)
        facts_response.raise_for_status()
        facts_data = facts_response.json()

        ### full print
        # with open("sec_raw_data.json", "w") as f:
        #     json.dump(facts_data, f, indent=2)
        # print(f"Raw SEC data saved to sec_raw_data.json for analysis")

        us_gaap_concepts = list(facts_data.get("facts", {}).get("us-gaap", {}).keys())
        dei_concepts = list(facts_data.get("facts", {}).get("dei", {}).keys())

        ### if "all" or none get all
        if isinstance(metrics, str) and metrics.lower() == "all":
            metrics = us_gaap_concepts + dei_concepts
        elif isinstance(metrics, str):
            metrics = [m.strip() for m in metrics.split(",") if m.strip()]

        ### extract
        results = {}
        for metric in metrics:
            metric_data = extract_metric_from_xbrl(
                facts_data, metric, target_year, target_form
            )
            if metric_data:
                results[metric] = metric_data
            ### Skip concepts that don't have data for the specified filters

        structured_results = {
            "company": company_name,
            "target_year": target_year,
            "target_form": target_form,
            "metrics": {},
        }

        for metric, data in results.items():
            value = data.get("value")
            unit = data.get("unit", "")
            label = data.get("label", metric)
            # print(f"\n{label}")
            end_date = data.get("end_date")
            fiscal_year = data.get("fiscal_year")
            fiscal_period = data.get("fiscal_period")
            form = data.get("form")
            taxonomy = data.get("taxonomy", "unknown")

            clean_value = value if isinstance(value, (int, float)) else None

            structured_results["metrics"][metric] = {
                "label": label,
                "value": clean_value,
                "unit": unit,
                "end_date": end_date,
                "fiscal_year": fiscal_year,
                "fiscal_period": fiscal_period,
                "form": form,
                "taxonomy": taxonomy,
            }

        # print(json.dumps(structured_results, indent=2))
        # with open("sec_raw_data.json", "w") as f:
        #     json.dump(structured_results, f, indent=2)
        # print(f"Raw SEC data saved to sec_raw_data.json for analysis")
        return structured_results, structured_results, facts_url, max_tokens

    except Exception as e:
        return f"Error fetching SEC metrics: {str(e)}", "", "", max_tokens


########################################################################


def sec_fetch_metrics(
    company_name: str,
    metrics: str = "all",
    target_year: int = None,
    target_form: str = None,
    *,
    user_id: str,
) -> str:
    """Fetch financial metrics from SEC XBRL data - fetches all available metrics by default
    #parameters:
    company_name: exact company name as it appears in SEC filings or ticker symbol or a ticker, example: Apple Inc. or AAPL
    metrics: comma-separated string of exact XBRL concept names (e.g., "Revenues,Assets,Liabilities") or "all" to fetch all available metrics (default: "all")
    target_year: specific fiscal year to filter (e.g., 2023), if None gets most recent
    target_form: specific form type to filter (e.g., "10-K", "10-Q"), if None gets any form
    """
    max_tokens = 30000

    cik = get_cik(company_name)

    if not cik:
        return (
            f"Company '{company_name}' not found in SEC database.",
            "",
            "",
            max_tokens,
        )

    headers = {
        "User-Agent": f"{os.getenv("USER_NAME_FOR_SEC")} {os.getenv("EMAIL_FOR_SEC")}",
        "Accept": "application/json",
    }

    try:
        facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        facts_response = requests.get(facts_url, headers=headers, timeout=30)
        facts_response.raise_for_status()
        facts_data = facts_response.json()

        ### full print if review needed
        # with open("sec_raw_data.json", "w") as f:
        #     json.dump(facts_data, f, indent=2)
        # print(f"Raw SEC data saved to sec_raw_data.json for analysis")

        us_gaap_concepts = list(facts_data.get("facts", {}).get("us-gaap", {}).keys())
        dei_concepts = list(facts_data.get("facts", {}).get("dei", {}).keys())

        ### if "all" or None get all
        if isinstance(metrics, str) and metrics.lower() == "all":
            metrics = us_gaap_concepts + dei_concepts
        elif isinstance(metrics, str):
            metrics = [m.strip() for m in metrics.split(",") if m.strip()]

        ### extract
        results = {}
        for metric in metrics:
            metric_data = extract_metric_from_xbrl(
                facts_data, metric, target_year, target_form
            )
            if metric_data:
                results[metric] = metric_data
            ### Skip concepts that don't have data for the specified filters

        ### formatter
        formatted_results = []
        formatted_results.append(f"Financial Metrics for {company_name} (CIK: {cik})")
        if target_year:
            formatted_results.append(f"Filtered by Year: {target_year}")
        if target_form:
            formatted_results.append(f"Filtered by Form: {target_form}")
        formatted_results.append("=" * 60)

        for metric, data in results.items():
            value = data.get("value", "N/A")
            unit = data.get("unit", "")
            label = data.get("label", metric)
            end_date = data.get("end_date", "N/A")
            fiscal_year = data.get("fiscal_year", "N/A")
            fiscal_period = data.get("fiscal_period", "N/A")
            form = data.get("form", "N/A")
            taxonomy = data.get("taxonomy", "unknown")

            if isinstance(value, (int, float)) and unit == "USD":
                if value >= 1_000_000_000:
                    formatted_value = f"${value/1_000_000_000:.2f}B"
                elif value >= 1_000_000:
                    formatted_value = f"${value/1_000_000:.2f}M"
                else:
                    formatted_value = f"${value:,.2f}"
            elif isinstance(value, (int, float)) and unit == "shares":
                formatted_value = f"{value:,} shares"
            elif isinstance(value, (int, float)):
                formatted_value = f"{value:,}"
            else:
                formatted_value = str(value)

            formatted_results.append(
                f"{label} ({metric}):"
            )  ### including full metric name like OCI, Debt Securities, Available-for-Sale, Unrealized Holding Gain (Loss), before Adjustment, after Tax (OtherComprehensiveIncomeUnrealizedHoldingGainLossOnSecuritiesArisingDuringPeriodNetOfTax)
            # formatted_results.append(f"{label}:") ### abbreviated cleaner return

            formatted_results.append(f"  Value: {formatted_value}")
            formatted_results.append(
                f"  Period: {end_date} | FY: {fiscal_year} | FP: {fiscal_period} | Form: {form}"
            )
            formatted_results.append(f"  Taxonomy: {taxonomy}")
            formatted_results.append("")

        result_text = "\n".join(formatted_results)
        return result_text, "", facts_url, max_tokens

    except Exception as e:
        return f"Error fetching SEC metrics: {str(e)}", "", "", max_tokens


########################################################################


def sec_fetch(
    company_name: str,
    keywords: list,
    filing_type: str = "10-K",
    *,
    user_id: str,
) -> str:
    """Fetch SEC filing by company name and convert to markdown -> the tool will return relevant snippets of the SEC report where your keywords are located
    #parameters:
    company_name: exact company name as it appears in SEC filings or ticker symbol or a ticker, example: Apple Inc. or AAPL
    keywords: keywords to search for in the report - either a python list of the keywords or a string split by ","
    filing_type: type of SEC filing to search for, defaults to "10-K" (annual report). Other options: "10-Q" (quarterly), "8-K" (current report)
    """
    max_tokens = 30000
    converter = MarkdownConverter()

    if keywords == None:
        return (
            f"You must provide keywords to search for in the filing, either py list or string separated by commas",
            "",
            "",
            max_tokens,
        )
    keywords = (
        keywords
        if isinstance(keywords, list)
        else [k.strip() for k in str(keywords).split(",") if k.strip()]
    )

    try:
        cik = get_cik(company_name)

        if not cik:
            return (
                f"Company '{company_name}' not found in SEC database. Try using the exact company name as it appears in SEC filings.",
                "",
                "",
                max_tokens,
            )

        headers = {
            "User-Agent": f"{os.getenv("USER_NAME_FOR_SEC")} {os.getenv("EMAIL_FOR_SEC")}",
            "Accept": "application/json",
        }

        ### Step 2: Get recent filings for this CIK
        submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        submissions_response = requests.get(
            submissions_url, headers=headers, timeout=30
        )
        submissions_response.raise_for_status()
        submissions_data = submissions_response.json()

        ### SEC rate limit: wait
        time.sleep(0.2)

        ### Find most recent filing of requested type
        recent_filings = submissions_data.get("filings", {}).get("recent", {})
        forms = recent_filings.get("form", [])
        accession_numbers = recent_filings.get("accessionNumber", [])
        filing_dates = recent_filings.get("filingDate", [])
        primary_documents = recent_filings.get("primaryDocument", [])

        target_filing = None
        for i, form in enumerate(forms):
            if form == filing_type:
                target_filing = {
                    "accession_number": accession_numbers[i],
                    "accession_number_no_dash": accession_numbers[i].replace("-", ""),
                    "filing_date": filing_dates[i],
                    "primary_document": (
                        primary_documents[i]
                        if i < len(primary_documents)
                        else f"{accession_numbers[i]}.htm"
                    ),
                }
                break

        if not target_filing:
            return (
                f"No {filing_type} filing found for {company_name}",
                "",
                "",
                max_tokens,
            )

        ### Step 3: Construct the SEC filing URL using the primary document name
        filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{target_filing['accession_number_no_dash']}/{target_filing['primary_document']}"

        ### Step 4: Fetch the actual filing
        filing_headers = {
            "User-Agent": f"{os.getenv("USER_NAME_FOR_SEC")} {os.getenv("EMAIL_FOR_SEC")}",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

        response = requests.get(filing_url, headers=filing_headers, timeout=30)
        response.raise_for_status()

        result = converter.convert(response)

        md_result = result.text_content.strip()

        snippets = []
        for k in keywords:
            start_idx = 0
            matches_found = 0
            while True:
                idx = md_result.lower().find(k.lower(), start_idx)
                if idx == -1 or matches_found >= 3:
                    break

                start = max(0, idx - 2500)  ###arnd 500 tokens
                end = min(len(md_result), idx + len(k) + 2500)  ### arnd 500 tokens
                snippet = md_result[start:end].strip()
                snippets.append(f"Keyword '{k}' at position {idx}: ...{snippet}...")

                start_idx = idx + 1
                matches_found += 1

        flatten_snippets = "\n".join(snippets)

        snippet_tokens = tokenizer.encode(flatten_snippets)
        token_count = len(snippet_tokens)
        if token_count > 20000:
            trimmed_tokens = snippet_tokens[:20000]
            trimmed_snippets = tokenizer.decode(trimmed_tokens)
            trimmed_snippets += f"\n\n[TRUNCATED - Original: {token_count} tokens, showing first 30,000 +  tokens]"
        else:
            trimmed_snippets = flatten_snippets

        return trimmed_snippets, trimmed_snippets, filing_url, max_tokens

    except Exception as e:
        return f"Error fetching SEC filing: {str(e)}", "", "", max_tokens


########################################################################
