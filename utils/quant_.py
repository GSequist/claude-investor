import json
from textwrap import indent

from tools.sec_tools_ import sec_fetch_metrics_structured

##TODO complete the calcs be more comprehensive
##TODO y-o-y q-o-q comparison

# SEC XBRL Concept Fallback Hierarchies
# Companies use different concept names for same economic metrics
CONCEPT_HIERARCHIES = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
        "SalesRevenueGoodsNet",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "NetSales",
        "TotalRevenues",
    ],
    "gross_profit": ["GrossProfit", "GrossProfitLoss"],
    "operating_income": [
        "OperatingIncomeLoss",
        "IncomeLossFromOperations",
        "OperatingIncome",
    ],
    "net_income": [
        "NetIncomeLoss",
        "NetIncomeLossAttributableToParent",
        "ProfitLoss",
        "NetIncomeLossAvailableToCommonStockholdersBasic",
    ],
    "total_assets": ["Assets", "TotalAssets"],
    "shareholders_equity": [
        "StockholdersEquity",
        "StockholdersEquityAttributableToParent",
        "ShareholdersEquityAttributableToParent",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
    "current_assets": ["AssetsCurrent", "CurrentAssets"],
    "current_liabilities": ["LiabilitiesCurrent", "CurrentLiabilities"],
    "inventory": ["InventoryNet", "Inventory"],
    "long_term_debt": [
        "LongTermDebt",
        "LongTermDebtNoncurrent",
        "LongTermDebtAndCapitalLeaseObligations",
    ],
    "current_debt": [
        "LongTermDebtCurrent",
        "LongTermDebtCurrentMaturities",
        "ShortTermBorrowings",
    ],
    "cash": ["CashAndCashEquivalentsAtCarryingValue", "CashAndCashEquivalents", "Cash"],
    "cost_of_goods_sold": [
        "CostOfGoodsAndServicesSold",
        "CostOfRevenue",
        "CostOfSales",
    ],
    "accounts_receivable": [
        "AccountsReceivableNetCurrent",
        "AccountsReceivableNet",
        "AccountsReceivable",
    ],
    "accounts_payable": ["AccountsPayableCurrent", "AccountsPayable"],
    "operating_cash_flow": [
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashFromOperatingActivities",
    ],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "CapitalExpenditures"],
    "shares_outstanding": [
        "EntityCommonStockSharesOutstanding",
        "CommonStockSharesOutstanding",
        "WeightedAverageNumberOfSharesOutstandingBasic",
    ],
    "eps_basic": ["EarningsPerShareBasic", "BasicEarningsPerShare"],
    "eps_diluted": ["EarningsPerShareDiluted", "DilutedEarningsPerShare"],
    "depreciation": [
        "DepreciationDepletionAndAmortization",
        "Depreciation",
        "DepreciationAndAmortization",
    ],
    "rd_expense": ["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenses"],
    "sga_expense": [
        "SellingGeneralAndAdministrativeExpense",
        "SellingGeneralAndAdministrativeExpenses",
    ],
    "interest_expense": ["InterestExpense", "InterestExpenseDebt"],
    "long_term_debt_noncurrent": [
        "LongTermDebtNoncurrent",
        "LongTermDebt",
        "LongTermDebtAndCapitalLeaseObligations",
    ],
    "working_capital_turnover_revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
        "NetSales",
    ],
}


def get_metric_value(metrics, concept_group):
    """Get first available metric from concept hierarchy"""
    concepts = CONCEPT_HIERARCHIES.get(concept_group, [concept_group])

    for concept in concepts:
        if concept in metrics:
            return metrics[concept]["value"], concept

    return None, None


# Core Valuation Ratios

# - P/E Ratio (Price/EPS) - need current stock price
# - P/B Ratio (Price/Book Value per Share)
# - P/S Ratio (Price/Sales per Share)
# - EV/EBITDA (Enterprise Value/EBITDA)
# - EV/Sales
# - PEG Ratio (P/E / Earnings Growth Rate)

# Profitability Analysis

# - Gross Margin (Gross Profit / Revenue)
# - Operating Margin (Operating Income / Revenue)
# - Net Margin (Net Income / Revenue)
# - ROE (Net Income / Shareholders Equity)
# - ROA (Net Income / Total Assets)
# - ROIC (NOPAT / Invested Capital)

# Financial Health

# - Current Ratio (Current Assets / Current Liabilities)
# - Quick Ratio ((Current Assets - Inventory) / Current Liabilities)
# - Debt-to-Equity (Total Debt / Shareholders Equity)
# - Interest Coverage (EBIT / Interest Expense)
# - Cash Ratio (Cash / Current Liabilities)

# Growth Metrics

# - Revenue Growth (YoY, QoQ)
# - EPS Growth (YoY, QoQ)
# - Free Cash Flow Growth
# - Book Value Growth

# Efficiency Ratios

# - Asset Turnover (Revenue / Average Total Assets)
# - Working Capital Turnover (Revenue / Working Capital)
# - Cash Conversion Cycle

# Advanced Analysis

# - Free Cash Flow (Operating CF - CapEx)
# - DCF Valuation (NPV of projected FCF)
# - Altman Z-Score (bankruptcy risk)
# - Economic Value Added (EVA)

# 1. 10-K vs 10-Q Data Strategy

# Recommendation: Use most recent data (10-Q) for calculations

# Why:
# - Timeliness: 10-Q gives you current quarter performance (Q3 2025 vs annual 2024)
# - Market relevance: Stock prices reflect most recent data, not year-old 10-K
# - Trend analysis: QoQ growth rates are more actionable than YoY from stale data

# Best Practice:
# - Use latest 10-Q for current metrics
# - Use previous 4 quarters for TTM (Trailing Twelve Months) calculations
# - Use 10-K for annual comparisons when needed


##TODO finish the predetermined calcs


### PROFITABILITY ANALYSIS
def gross_margin(data):
    metrics = data["metrics"]
    revenue, _ = get_metric_value(metrics, "revenue")
    gross_profit, _ = get_metric_value(metrics, "gross_profit")

    if revenue and gross_profit:
        return (gross_profit / revenue) * 100
    return None


def prev_gross_margin(data, user_id):
    """Gross margin same period prior year"""
    metrics = data["metrics"]

    # Current period - use fallback system
    curr_revenue, rev_concept = get_metric_value(metrics, "revenue")
    curr_gross_profit, gp_concept = get_metric_value(metrics, "gross_profit")

    if not curr_revenue or not curr_gross_profit:
        return {"current": None, "prior_year": None, "change": None}

    curr_margin = (curr_gross_profit / curr_revenue) * 100

    # Get period info - check both metrics match
    rev_form = metrics[rev_concept]["form"]
    rev_year = metrics[rev_concept]["fiscal_year"]
    gross_profit_form = metrics[gp_concept]["form"]
    gross_profit_year = metrics[gp_concept]["fiscal_year"]

    # Only calculate if forms and years match
    if rev_form == gross_profit_form and rev_year == gross_profit_year:
        try:
            prev_data_response = sec_fetch_metrics_structured(
                data["company"],
                "all",
                target_year=rev_year - 1,
                target_form=rev_form,
                user_id=user_id,
            )
            prev_data = (
                prev_data_response[0]
                if isinstance(prev_data_response, tuple)
                else prev_data_response
            )

            # Use same fallback system for previous data
            prev_gross_profit, _ = get_metric_value(
                prev_data["metrics"], "gross_profit"
            )
            prev_rev, _ = get_metric_value(prev_data["metrics"], "revenue")
            prev_margin = (prev_gross_profit / prev_rev) * 100

            return {
                "current": curr_margin,
                "prior_year": prev_margin,
                "change": curr_margin - prev_margin,
            }
        except:
            return {"current": curr_margin, "prior_year": None, "change": None}

    return {"current": curr_margin, "prior_year": None, "change": None}


def prev_revenue_growth(data, user_id):
    """Revenue growth vs same period prior year"""
    metrics = data["metrics"]

    # Current period - use fallback system
    curr_revenue, rev_concept = get_metric_value(metrics, "revenue")

    if not curr_revenue:
        return {"current": None, "prior_year": None, "growth_pct": None}

    rev_form = metrics[rev_concept]["form"]
    rev_year = metrics[rev_concept]["fiscal_year"]

    try:
        prev_data_response = sec_fetch_metrics_structured(
            data["company"],
            [rev_concept],
            target_year=rev_year - 1,
            target_form=rev_form,
            user_id=user_id,
        )
        prev_data = (
            prev_data_response[0]
            if isinstance(prev_data_response, tuple)
            else prev_data_response
        )
        # Use fallback system for previous data
        prev_revenue, _ = get_metric_value(prev_data["metrics"], "revenue")
        growth_pct = ((curr_revenue - prev_revenue) / prev_revenue) * 100

        return {
            "current": curr_revenue,
            "prior_year": prev_revenue,
            "growth_pct": growth_pct,
        }
    except:
        return {"current": curr_revenue, "prior_year": None, "growth_pct": None}


def prev_operating_margin(data, user_id):
    """Operating margin vs same period prior year"""
    metrics = data["metrics"]

    # Current period - use fallback system
    curr_revenue, rev_concept = get_metric_value(metrics, "revenue")
    curr_operating_income, op_concept = get_metric_value(metrics, "operating_income")

    if not curr_revenue or not curr_operating_income:
        return {"current": None, "prior_year": None, "change": None}

    curr_margin = (curr_operating_income / curr_revenue) * 100

    # Check forms/years match
    rev_form = metrics[rev_concept]["form"]
    rev_year = metrics[rev_concept]["fiscal_year"]
    op_form = metrics[op_concept]["form"]
    op_year = metrics[op_concept]["fiscal_year"]

    if rev_form == op_form and rev_year == op_year:
        try:
            prev_data_response = sec_fetch_metrics_structured(
                data["company"],
                [rev_concept, op_concept],
                target_year=rev_year - 1,
                target_form=rev_form,
                user_id=user_id,
            )
            prev_data = (
                prev_data_response[0]
                if isinstance(prev_data_response, tuple)
                else prev_data_response
            )
            # Use same fallback system for previous data
            prev_operating_income, _ = get_metric_value(
                prev_data["metrics"], "operating_income"
            )
            prev_revenue, _ = get_metric_value(prev_data["metrics"], "revenue")
            prev_margin = (prev_operating_income / prev_revenue) * 100

            return {
                "current": curr_margin,
                "prior_year": prev_margin,
                "change": curr_margin - prev_margin,
            }
        except:
            return {"current": curr_margin, "prior_year": None, "change": None}

    return {"current": curr_margin, "prior_year": None, "change": None}


def operating_margin(data):
    metrics = data["metrics"]
    revenue, _ = get_metric_value(metrics, "revenue")
    operating_income, _ = get_metric_value(metrics, "operating_income")

    if revenue and operating_income:
        return (operating_income / revenue) * 100
    return None


def net_margin(data):
    metrics = data["metrics"]
    revenue, _ = get_metric_value(metrics, "revenue")
    net_income, _ = get_metric_value(metrics, "net_income")

    if revenue and net_income:
        return (net_income / revenue) * 100
    return None


def roe(data):
    """Return on Equity"""
    metrics = data["metrics"]
    net_income, _ = get_metric_value(metrics, "net_income")
    equity, _ = get_metric_value(metrics, "shareholders_equity")

    if net_income and equity:
        return (net_income / equity) * 100
    return None


def roa(data):
    """Return on Assets"""
    metrics = data["metrics"]
    net_income, _ = get_metric_value(metrics, "net_income")
    assets, _ = get_metric_value(metrics, "total_assets")

    if net_income and assets:
        return (net_income / assets) * 100
    return None


### FINANCIAL HEALTH
def current_ratio(data):
    metrics = data["metrics"]
    current_assets, _ = get_metric_value(metrics, "current_assets")
    current_liabilities, _ = get_metric_value(metrics, "current_liabilities")

    if current_assets and current_liabilities:
        return current_assets / current_liabilities
    return None


def quick_ratio(data):
    metrics = data["metrics"]
    current_assets, _ = get_metric_value(metrics, "current_assets")
    inventory, _ = get_metric_value(metrics, "inventory")
    current_liabilities, _ = get_metric_value(metrics, "current_liabilities")

    if current_assets and current_liabilities:
        inventory = inventory or 0  # Some companies don't have inventory
        return (current_assets - inventory) / current_liabilities
    return None


def debt_to_equity(data):
    metrics = data["metrics"]
    long_term_debt, _ = get_metric_value(metrics, "long_term_debt")
    equity, _ = get_metric_value(metrics, "shareholders_equity")

    if long_term_debt and equity:
        return long_term_debt / equity
    return None


def cash_ratio(data):
    metrics = data["metrics"]
    cash, _ = get_metric_value(metrics, "cash")
    current_liabilities, _ = get_metric_value(metrics, "current_liabilities")

    if cash and current_liabilities:
        return cash / current_liabilities
    return None


### EFFICIENCY RATIOS
def asset_turnover(data):
    metrics = data["metrics"]
    revenue, _ = get_metric_value(metrics, "revenue")
    assets, _ = get_metric_value(metrics, "total_assets")

    if revenue and assets:
        return revenue / assets
    return None


def working_capital(data):
    metrics = data["metrics"]
    current_assets, _ = get_metric_value(metrics, "current_assets")
    current_liabilities, _ = get_metric_value(metrics, "current_liabilities")

    if current_assets and current_liabilities:
        return current_assets - current_liabilities
    return None


### CASH FLOW ANALYSIS
def free_cash_flow(data):
    metrics = data["metrics"]
    operating_cf, _ = get_metric_value(metrics, "operating_cash_flow")
    capex, _ = get_metric_value(metrics, "capex")

    if operating_cf and capex:
        return operating_cf - capex
    return None


### PER SHARE METRICS
def book_value_per_share(data):
    metrics = data["metrics"]
    equity, _ = get_metric_value(metrics, "shareholders_equity")
    shares, _ = get_metric_value(metrics, "shares_outstanding")

    if equity and shares:
        return equity / shares
    return None


def eps_basic(data):
    metrics = data["metrics"]
    eps, _ = get_metric_value(metrics, "eps_basic")
    return eps


def eps_diluted(data):
    metrics = data["metrics"]
    eps, _ = get_metric_value(metrics, "eps_diluted")
    return eps


### ADVANCED FINANCIAL HEALTH
def interest_coverage(data):
    """EBIT / Interest Expense (if available)"""
    metrics = data["metrics"]

    operating_income, _ = get_metric_value(metrics, "operating_income")
    interest_expense, _ = get_metric_value(metrics, "interest_expense")

    if operating_income and interest_expense:
        return operating_income / interest_expense
    return None


def debt_service_coverage(data):
    """Operating CF / Interest Expense (cash-based coverage)"""
    metrics = data["metrics"]

    operating_cf, _ = get_metric_value(metrics, "operating_cash_flow")
    interest_expense, _ = get_metric_value(metrics, "interest_expense")

    if operating_cf and interest_expense:
        return operating_cf / interest_expense
    return None


def inventory_turnover(data):
    """Cost of Goods Sold / Inventory"""
    metrics = data["metrics"]
    cogs, _ = get_metric_value(metrics, "cost_of_goods_sold")
    inventory, _ = get_metric_value(metrics, "inventory")

    if cogs and inventory:
        return cogs / inventory
    return None


def receivables_turnover(data):
    """Revenue / Accounts Receivable"""
    metrics = data["metrics"]
    revenue, _ = get_metric_value(metrics, "revenue")
    receivables, _ = get_metric_value(metrics, "accounts_receivable")

    if revenue and receivables:
        return revenue / receivables
    return None


def payables_turnover(data):
    """COGS / Accounts Payable"""
    metrics = data["metrics"]
    cogs, _ = get_metric_value(metrics, "cost_of_goods_sold")
    payables, _ = get_metric_value(metrics, "accounts_payable")

    if cogs and payables:
        return cogs / payables
    return None


### CASH CONVERSION CYCLE COMPONENTS
def days_sales_outstanding(data):
    """Days to collect receivables"""
    metrics = data["metrics"]
    revenue, _ = get_metric_value(metrics, "revenue")
    receivables, _ = get_metric_value(metrics, "accounts_receivable")

    if revenue and receivables:
        return (receivables / revenue) * 365
    return None


def days_inventory_outstanding(data):
    """Days inventory held"""
    metrics = data["metrics"]
    cogs, _ = get_metric_value(metrics, "cost_of_goods_sold")
    inventory, _ = get_metric_value(metrics, "inventory")

    if cogs and inventory:
        return (inventory / cogs) * 365
    return None


def days_payable_outstanding(data):
    """Days to pay suppliers"""
    metrics = data["metrics"]
    cogs, _ = get_metric_value(metrics, "cost_of_goods_sold")
    payables, _ = get_metric_value(metrics, "accounts_payable")

    if cogs and payables:
        return (payables / cogs) * 365
    return None


def cash_conversion_cycle(data):
    """DIO + DSO - DPO"""
    dio = days_inventory_outstanding(data)
    dso = days_sales_outstanding(data)
    dpo = days_payable_outstanding(data)
    return dio + dso - dpo


### OPERATIONAL EFFICIENCY
def rd_intensity(data):
    """R&D Expense / Revenue"""
    metrics = data["metrics"]
    rd_expense, _ = get_metric_value(metrics, "rd_expense")
    revenue, _ = get_metric_value(metrics, "revenue")

    if rd_expense and revenue:
        return (rd_expense / revenue) * 100
    return None


def sga_ratio(data):
    """SG&A Expense / Revenue"""
    metrics = data["metrics"]
    sga, _ = get_metric_value(metrics, "sga_expense")
    revenue, _ = get_metric_value(metrics, "revenue")

    if sga and revenue:
        return (sga / revenue) * 100
    return None


### LEVERAGE RATIOS
def debt_to_assets(data):
    """Total Debt / Total Assets"""
    metrics = data["metrics"]
    long_term_debt, _ = get_metric_value(metrics, "long_term_debt")
    current_debt, _ = get_metric_value(metrics, "current_debt")
    assets, _ = get_metric_value(metrics, "total_assets")

    if long_term_debt and current_debt and assets:
        total_debt = long_term_debt + current_debt
        return (total_debt / assets) * 100
    return None


def equity_multiplier(data):
    """Total Assets / Shareholders Equity"""
    metrics = data["metrics"]
    assets, _ = get_metric_value(metrics, "total_assets")
    equity, _ = get_metric_value(metrics, "shareholders_equity")

    if assets and equity:
        return assets / equity
    return None


### CASH FLOW RATIOS
def operating_cash_flow_ratio(data):
    """Operating CF / Current Liabilities"""
    metrics = data["metrics"]
    operating_cf, _ = get_metric_value(metrics, "operating_cash_flow")
    current_liabilities, _ = get_metric_value(metrics, "current_liabilities")

    if operating_cf and current_liabilities:
        return operating_cf / current_liabilities
    return None


def cash_flow_to_debt(data):
    """Operating CF / Total Debt"""
    metrics = data["metrics"]
    operating_cf, _ = get_metric_value(metrics, "operating_cash_flow")
    long_term_debt, _ = get_metric_value(metrics, "long_term_debt")
    current_debt, _ = get_metric_value(metrics, "current_debt")

    if operating_cf and long_term_debt and current_debt:
        total_debt = long_term_debt + current_debt
        return operating_cf / total_debt
    return None


def capex_intensity(data):
    """CapEx / Revenue"""
    metrics = data["metrics"]
    capex, _ = get_metric_value(metrics, "capex")
    revenue, _ = get_metric_value(metrics, "revenue")

    if capex and revenue:
        return (capex / revenue) * 100
    return None


### MARKET EFFICIENCY (need stock price for these)
def price_to_book(stock_price, data):
    """Stock Price / Book Value per Share"""
    bvps = book_value_per_share(data)
    return stock_price / bvps


def price_to_sales_per_share(stock_price, data):
    """Stock Price / Sales per Share"""
    metrics = data["metrics"]
    revenue, _ = get_metric_value(metrics, "revenue")
    shares, _ = get_metric_value(metrics, "shares_outstanding")

    if revenue and shares:
        sales_per_share = revenue / shares
        return stock_price / sales_per_share
    return None


def price_to_earnings(stock_price, data):
    """Stock Price / EPS"""
    eps = eps_diluted(data)
    return stock_price / eps


### EV
def calculate_ebitda(data):
    """EBITDA = Operating Income + Depreciation & Amortization"""
    metrics = data["metrics"]
    operating_income, _ = get_metric_value(metrics, "operating_income")
    depreciation, _ = get_metric_value(metrics, "depreciation")

    if operating_income and depreciation:
        return operating_income + depreciation
    return None


def calculate_enterprise_value(market_cap, data):
    """EV = Market Cap + Total Debt - Cash"""
    metrics = data["metrics"]

    # Total Debt - use noncurrent specific fallback for EV calc
    long_term_debt, _ = get_metric_value(metrics, "long_term_debt_noncurrent")
    current_debt, _ = get_metric_value(metrics, "current_debt")
    cash, _ = get_metric_value(metrics, "cash")

    if market_cap and long_term_debt and current_debt and cash:
        total_debt = long_term_debt + current_debt
        enterprise_value = market_cap + total_debt - cash
        return enterprise_value
    return None


def ev_ebitda_multiple(market_cap, data):
    """EV/EBITDA Multiple"""
    ev = calculate_enterprise_value(market_cap, data)
    ebitda = calculate_ebitda(data)
    return ev / ebitda


def implied_equity_value_from_ev_ebitda(data, peer_ev_ebitda_median):
    """Calculate implied equity value using peer median EV/EBITDA"""
    metrics = data["metrics"]

    ebitda = calculate_ebitda(data)
    long_term_debt, _ = get_metric_value(metrics, "long_term_debt_noncurrent")
    current_debt, _ = get_metric_value(metrics, "current_debt")
    cash, _ = get_metric_value(metrics, "cash")

    if ebitda and long_term_debt and current_debt and cash:
        implied_ev = ebitda * peer_ev_ebitda_median
        total_debt = long_term_debt + current_debt
        implied_equity_value = implied_ev - total_debt + cash

        return {
            "implied_ev": implied_ev,
            "implied_equity_value": implied_equity_value,
            "ebitda": ebitda,
            "peer_multiple": peer_ev_ebitda_median,
        }
    return None


def calculate_peer_benchmarks(company_ratios, peer_ratios_list):
    """Calculate where company stands vs peers for each metric"""

    benchmarks = {
        "company": company_ratios.get("company"),
        "peer_analysis": {},
        "relative_performance": {},
    }

    if not company_ratios.get("ratios") or not peer_ratios_list:
        return benchmarks

    # For each ratio, calculate peer statistics
    for ratio_name, company_value in company_ratios["ratios"].items():
        if not isinstance(company_value, (int, float)):
            continue

        # Collect peer values for this ratio
        peer_values = []
        for peer_data in peer_ratios_list:
            if peer_data.get("ratios", {}).get(ratio_name) is not None:
                peer_val = peer_data["ratios"][ratio_name]
                if isinstance(peer_val, (int, float)):
                    peer_values.append(peer_val)

        if len(peer_values) >= 1:  # Need at least 1 peer for comparison
            peer_values.sort()

            # Calculate peer statistics
            peer_median = peer_values[len(peer_values) // 2] if peer_values else 0
            peer_min = min(peer_values)
            peer_max = max(peer_values)
            peer_avg = sum(peer_values) / len(peer_values)

            # Calculate company's percentile rank
            better_than = sum(1 for v in peer_values if company_value > v)
            percentile_rank = (better_than / len(peer_values)) * 100

            # Determine performance category
            if percentile_rank >= 75:
                performance = "OUTPERFORM"
            elif percentile_rank >= 50:
                performance = "ABOVE_MEDIAN"
            elif percentile_rank >= 25:
                performance = "BELOW_MEDIAN"
            else:
                performance = "UNDERPERFORM"

            benchmarks["peer_analysis"][ratio_name] = {
                "company_value": company_value,
                "peer_median": peer_median,
                "peer_average": peer_avg,
                "peer_min": peer_min,
                "peer_max": peer_max,
                "percentile_rank": percentile_rank,
                "performance_vs_peers": performance,
                "peer_count": len(peer_values),
            }

    return benchmarks


## TODO finish the earnings quality
# def earnings_quality_score(current_data, prior_data):
#     """Composite score predicting earnings surprise direction"""

#     # 1. Cash conversion deterioration
#     current_ocf_ni = current_data["operating_cf"] / current_data["net_income"]
#     prior_ocf_ni = prior_data["operating_cf"] / prior_data["net_income"]

#     # 2. Working capital acceleration
#     current_wc_days = current_data["cash_conversion_cycle"]
#     prior_wc_days = prior_data["cash_conversion_cycle"]

#     # 3. Investment intensity decline
#     current_capex_depr = current_data["capex"] / current_data["depreciation"]
#     prior_capex_depr = prior_data["capex"] / prior_data["depreciation"]

#     return "composite_score_placeholder"  # Higher = more likely to surprise positively


##############################################################


def calculate_all_ratios(data, stock_price=None, peer_multiples=None, *, user_id):
    """Calculate all available ratios, skip if metrics missing"""

    results = {
        "company": data.get("company"),
        "year": data.get("target_year"),
        "ratios": {},
        "missing_metrics": [],
    }

    ### STEP 1: Calculate market cap FIRST (if stock price provided)
    if stock_price:
        try:
            shares, _ = get_metric_value(data["metrics"], "shares_outstanding")
            results["ratios"]["market_cap"] = stock_price * shares
        except:
            results["missing_metrics"].append("market_cap: missing shares outstanding")

    ### STEP 2: Basic ratio functions
    # w/o userid
    basic_ratio_functions = [
        ("gross_margin", gross_margin),
        ("operating_margin", operating_margin),
        ("net_margin", net_margin),
        ("roe", roe),
        ("roa", roa),
        # Liquidity
        ("current_ratio", current_ratio),
        ("quick_ratio", quick_ratio),
        ("cash_ratio", cash_ratio),
        # Leverage
        ("debt_to_equity", debt_to_equity),
        ("debt_to_assets", debt_to_assets),
        ("equity_multiplier", equity_multiplier),
        # Efficiency
        ("asset_turnover", asset_turnover),
        ("inventory_turnover", inventory_turnover),
        ("receivables_turnover", receivables_turnover),
        ("payables_turnover", payables_turnover),
        # Cash Flow
        ("free_cash_flow", free_cash_flow),
        ("operating_cash_flow_ratio", operating_cash_flow_ratio),
        ("cash_flow_to_debt", cash_flow_to_debt),
        # Per Share
        ("book_value_per_share", book_value_per_share),
        ("eps_basic", eps_basic),
        ("eps_diluted", eps_diluted),
        # Cash Conversion
        ("days_sales_outstanding", days_sales_outstanding),
        ("days_inventory_outstanding", days_inventory_outstanding),
        ("days_payable_outstanding", days_payable_outstanding),
        ("cash_conversion_cycle", cash_conversion_cycle),
        # Advanced
        ("interest_coverage", interest_coverage),
        ("debt_service_coverage", debt_service_coverage),
        ("rd_intensity", rd_intensity),
        ("sales_gen_admin_exp_rev_ratio", sga_ratio),
        ("capex_intensity", capex_intensity),
        ("working_capital", working_capital),
        # Standalone calculations
        ("ebitda", calculate_ebitda),
    ]

    ##  need user id
    trend_ratio_functions = [
        ("prev_gross_margin", prev_gross_margin),
        ("prev_revenue_growth", prev_revenue_growth),
        ("prev_operating_margin", prev_operating_margin),
    ]

    ### Calculate basic ratios (no user_id needed)
    for ratio_name, ratio_func in basic_ratio_functions:
        try:
            value = ratio_func(data)
            if value is not None:
                results["ratios"][ratio_name] = value
        except KeyError as e:
            results["missing_metrics"].append(f"{ratio_name}: missing {str(e)}")
        except (ZeroDivisionError, TypeError):
            results["missing_metrics"].append(f"{ratio_name}: calculation error")

    ## Calculate trend ratios (need user_id)
    for ratio_name, ratio_func in trend_ratio_functions:
        try:
            value = ratio_func(data, user_id)
            if value is not None:
                results["ratios"][ratio_name] = value
        except KeyError as e:
            results["missing_metrics"].append(f"{ratio_name}: missing {str(e)}")
        except (ZeroDivisionError, TypeError, Exception):
            results["missing_metrics"].append(f"{ratio_name}: calculation error")

    ### STEP 3: Market-dependent ratios (require stock_price)
    if stock_price and "market_cap" in results["ratios"]:
        try:
            results["ratios"]["price_to_book"] = price_to_book(stock_price, data)
        except:
            results["missing_metrics"].append("price_to_book: calculation error")

        try:
            results["ratios"]["price_to_earnings"] = price_to_earnings(
                stock_price, data
            )
        except:
            results["missing_metrics"].append("price_to_earnings: calculation error")

        try:
            results["ratios"]["price_to_sales_per_share"] = price_to_sales_per_share(
                stock_price, data
            )
        except:
            results["missing_metrics"].append(
                "price_to_sales_per_share: calculation error"
            )

    ### STEP 4: EV calculations (require market_cap)
    if "market_cap" in results["ratios"]:
        try:
            results["ratios"]["enterprise_value"] = calculate_enterprise_value(
                results["ratios"]["market_cap"], data
            )
        except:
            results["missing_metrics"].append(
                "enterprise_value: missing debt/cash data"
            )

        if "enterprise_value" in results["ratios"] and "ebitda" in results["ratios"]:
            try:
                results["ratios"]["ev_ebitda"] = (
                    results["ratios"]["enterprise_value"] / results["ratios"]["ebitda"]
                )
            except:
                results["missing_metrics"].append("ev_ebitda: calculation error")

            try:
                results["ratios"]["ev_to_sales"] = (
                    results["ratios"]["enterprise_value"]
                    / data["metrics"][
                        "RevenueFromContractWithCustomerExcludingAssessedTax"
                    ]["value"]
                )
            except:
                results["missing_metrics"].append("ev_to_sales: calc error")

    ### STEP 5: Peer multiple analysis (if provided)
    if peer_multiples and "ev_ebitda_median" in peer_multiples:
        try:
            implied_val = implied_equity_value_from_ev_ebitda(
                data, peer_multiples["ev_ebitda_median"]
            )
            results["ratios"]["implied_equity_value"] = implied_val[
                "implied_equity_value"
            ]
            results["ratios"]["implied_ev"] = implied_val["implied_ev"]
        except:
            results["missing_metrics"].append("implied_valuation: calculation error")

    return results
