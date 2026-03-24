"""
ETF Daily Reporting System
==========================
Generates daily reports for Portfolio Managers, Analysts, and Operations teams.
Includes basket composition, settlement status, Greeks analysis, and exception reports.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from io import StringIO
import logging

logger = logging.getLogger(__name__)


class ETFReportingSystem:
    """Generate and format daily reports for stakeholders."""

    def __init__(self, etf_ticker: str, trade_date: str):
        self.etf_ticker = etf_ticker
        self.trade_date = trade_date
        self.reports = {}

    def generate_basket_composition_report(self, df_basket: pd.DataFrame) -> str:
        """
        Generate basket composition report for Portfolio Managers.
        Shows daily securities and cash composition.
        """
        report = f"""
╔════════════════════════════════════════════════════════════════════╗
║         DAILY BASKET COMPOSITION REPORT                            ║
║         ETF: {self.etf_ticker}                                              ║
║         Date: {self.trade_date}                                    ║
╚════════════════════════════════════════════════════════════════════╝

BASKET CONSTITUENTS
───────────────────────────────────────────────────────────────────
{df_basket.to_string(index=False)}

BASKET SUMMARY
───────────────────────────────────────────────────────────────────
Total Securities:        {len(df_basket) - 1}
Total Valuation:         ${df_basket['Valuation'].sum():,.2f}
Cash Component:          ${df_basket[df_basket['Security_ID'] == 'CASH']['Valuation'].values[0]:,.2f}
Securities Valuation:    ${df_basket[df_basket['Security_ID'] != 'CASH']['Valuation'].sum():,.2f}

LARGEST HOLDINGS
───────────────────────────────────────────────────────────────────
"""

        top_5 = df_basket[df_basket['Security_ID'] != 'CASH'].nlargest(5, 'Valuation')
        for idx, row in top_5.iterrows():
            pct = (row['Valuation'] / df_basket['Valuation'].sum()) * 100
            report += f"{row['Security_ID']:8} | ${row['Valuation']:>12,.2f} | {pct:>6.2f}%\n"

        return report

    def generate_settlement_status_report(self, df_transactions: pd.DataFrame) -> str:
        """
        Generate settlement status report for Operations team.
        Shows Create/Redeem activity and settlement tracking.
        """
        report = f"""
╔════════════════════════════════════════════════════════════════════╗
║         SETTLEMENT STATUS REPORT                                    ║
║         ETF: {self.etf_ticker}                                              ║
║         Trade Date: {self.trade_date}                              ║
╚════════════════════════════════════════════════════════════════════╝

CREATE/REDEEM ACTIVITY SUMMARY
───────────────────────────────────────────────────────────────────
Transaction Type    | Count  | Basket Units  | Cash Component
"""

        summary = df_transactions.groupby('Transaction_Type').agg({
            'Transaction_ID': 'count',
            'Basket_Units': 'sum',
            'Cash_Component': 'sum'
        })

        for txn_type, row in summary.iterrows():
            report += f"{txn_type:20} | {int(row['Transaction_ID']):5} | {int(row['Basket_Units']):>12} | ${row['Cash_Component']:>12,.2f}\n"

        report += f"""
DETAILED TRANSACTIONS
───────────────────────────────────────────────────────────────────
{df_transactions.to_string(index=False)}

SETTLEMENT SCHEDULE
───────────────────────────────────────────────────────────────────
T-Date (Trade Date):     {self.trade_date}
T+0 (Today):             N/A - Awaiting execution
T+1 (Settlement):        Next business day
T+2 (Final Settlement):  T+1 + 1 business day
"""

        return report

    def generate_greeks_analysis_report(self, greeks_dict: Dict) -> str:
        """
        Generate Greeks analysis report for risk management.
        Portfolio-level Greeks sensitivity analysis.
        """
        portfolio_greeks = greeks_dict['portfolio_greeks']

        report = f"""
╔════════════════════════════════════════════════════════════════════╗
║         OPTIONS GREEKS ANALYSIS REPORT                             ║
║         ETF: {self.etf_ticker}                                              ║
║         Analysis Date: {self.trade_date}                            ║
╚════════════════════════════════════════════════════════════════════╝

PORTFOLIO GREEK EXPOSURES (Aggregate)
───────────────────────────────────────────────────────────────────

Delta (Δ)    Price Sensitivity
  Value:     {portfolio_greeks['Total_Delta']:>10,.2f}
  Meaning:   For every $1 move in {self.etf_ticker}, portfolio changes by ${portfolio_greeks['Total_Delta']:,.2f}

Gamma (Γ)    Delta Acceleration
  Value:     {portfolio_greeks['Total_Gamma']:>10,.6f}
  Meaning:   Delta will increase by {portfolio_greeks['Total_Gamma']:.6f} per $1 move

Theta (Θ)    Time Decay
  Value:     ${portfolio_greeks['Total_Theta']:>9,.2f}
  Meaning:   Portfolio loses ${abs(portfolio_greeks['Total_Theta']):.2f} per day to time decay

Vega (ν)     Volatility Sensitivity
  Value:     {portfolio_greeks['Total_Vega']:>10,.2f}
  Meaning:   For 1% vol increase, portfolio gains ${portfolio_greeks['Total_Vega']:,.2f}

Rho (ρ)      Interest Rate Sensitivity
  Value:     ${portfolio_greeks['Total_Rho']:>9,.2f}
  Meaning:   For 1% rate increase, portfolio changes by ${portfolio_greeks['Total_Rho']:,.2f}

GREEK VALIDATION RESULTS
───────────────────────────────────────────────────────────────────
"""

        validation = greeks_dict['validation']
        for greek, valid in validation.items():
            status = "✓ VALID" if valid else "✗ INVALID"
            report += f"{greek:20} : {status}\n"

        return report

    def generate_exception_report(self, breaks_data: List, matched_count: int) -> str:
        """
        Generate exception/break report for reconciliation discrepancies.
        """
        report = f"""
╔════════════════════════════════════════════════════════════════════╗
║         RECONCILIATION EXCEPTION REPORT                            ║
║         ETF: {self.etf_ticker}                                              ║
║         Date: {self.trade_date}                                    ║
╚════════════════════════════════════════════════════════════════════╝

RECONCILIATION SUMMARY
───────────────────────────────────────────────────────────────────
Records Matched:        {matched_count}
Exceptions/Breaks:      {len(breaks_data)}
Match Rate:             {(matched_count / (matched_count + len(breaks_data)) * 100) if (matched_count + len(breaks_data)) > 0 else 0:.2f}%

EXCEPTION DETAILS
───────────────────────────────────────────────────────────────────
"""

        if len(breaks_data) > 0:
            report += "Exceptions requiring investigation:\n"
            for i, break_record in enumerate(breaks_data[:5], 1):  # Show top 5
                report += f"  {i}. Break detected - Review and reconcile manually\n"
        else:
            report += "✓ No exceptions - All records reconciled successfully\n"

        return report

    def export_report_to_file(self, report_name: str, report_content: str, output_dir: str = 'reports'):
        """Export report to text file."""
        filename = f"{output_dir}/{report_name}_{self.trade_date}.txt"
        with open(filename, 'w') as f:
            f.write(report_content)
        logger.info(f"Report exported: {filename}")
        return filename


# Type hint for Dict
from typing import Dict, List

