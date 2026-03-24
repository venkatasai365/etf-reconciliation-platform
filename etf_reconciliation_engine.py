"""
ETF Data Reconciliation & Reporting Platform
=============================================
Production-grade reconciliation system for ETF operations.
Handles PCF matching, settlement validation, and Greeks reconciliation.

Author: [Your Name]
Version: 1.0.0
Date: March 24, 2026
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Tuple, Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/reconciliation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ETFReconciliationEngine:
    """
    Main reconciliation engine for ETF operations.
    Matches internal PCF records with external DTCC/custodian data.
    """

    def __init__(self, tolerance_pct: float = 0.01, tolerance_qty: float = 0.5):
        """
        Initialize reconciliation engine.

        Args:
            tolerance_pct: Percentage tolerance for valuation differences (0.01 = 1%)
            tolerance_qty: Absolute tolerance for quantity differences (units)
        """
        self.tolerance_pct = tolerance_pct
        self.tolerance_qty = tolerance_qty
        self.matches = []
        self.breaks = []
        self.reconciliation_report = None
        logger.info(f"ETF Reconciliation Engine initialized with tolerances: {tolerance_pct*100}% price, {tolerance_qty} qty")

    def load_data(self, internal_path: str, external_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load internal and external data files."""
        df_internal = pd.read_csv(internal_path)
        df_external = pd.read_csv(external_path)
        logger.info(f"Loaded internal data: {len(df_internal)} records")
        logger.info(f"Loaded external data: {len(df_external)} records")
        return df_internal, df_external

    def reconcile_baskets(self, df_internal: pd.DataFrame, df_external: pd.DataFrame) -> pd.DataFrame:
        """
        Reconcile internal PCF with external DTCC settlement records.

        Key matching fields:
        - ETF_Ticker + Security_ID + Trade_Date (mandatory)
        - Tolerance applied to Quantity and Valuation
        """
        logger.info("=== Starting Basket Reconciliation ===")

        # Merge on key fields
        merge_cols = ['Trade_Date', 'ETF_Ticker', 'Security_ID']
        df_merged = df_internal.merge(
            df_external,
            on=merge_cols,
            suffixes=('_INT', '_EXT'),
            how='outer',
            indicator=True
        )

        # Identify unmatched records
        unmatched = df_merged[df_merged['_merge'] != 'both'].copy()
        if len(unmatched) > 0:
            logger.warning(f"Unmatched records found: {len(unmatched)}")
            self.breaks.append(unmatched)

        # For matched records, calculate variances
        matched = df_merged[df_merged['_merge'] == 'both'].copy()

        # Calculate quantity variance
        matched['Qty_Variance'] = matched['Quantity_EXT'] - matched['Quantity_INT']
        matched['Qty_Var_Pct'] = (matched['Qty_Variance'] / matched['Quantity_INT'].replace(0, 1)) * 100

        # Calculate valuation variance
        matched['Val_Variance'] = matched['Valuation_EXT'] - matched['Valuation_INT']
        matched['Val_Var_Pct'] = (matched['Val_Variance'] / matched['Valuation_INT'].replace(0, 1)) * 100

        # Determine match status based on tolerances
        matched['Match_Status'] = matched.apply(
            lambda row: 'MATCH' if (
                abs(row['Qty_Var_Pct']) <= self.tolerance_pct * 100 and
                abs(row['Val_Var_Pct']) <= self.tolerance_pct * 100
            ) else 'BREAK',
            axis=1
        )

        # Separate matches and breaks
        self.matches = matched[matched['Match_Status'] == 'MATCH'].copy()
        self.breaks.extend(matched[matched['Match_Status'] == 'BREAK'].values.tolist())

        logger.info(f"Reconciliation complete: {len(self.matches)} MATCHES, {len(self.breaks)} BREAKS")

        return matched

    def reconcile_options_greeks(self, df_options: pd.DataFrame) -> Dict:
        """
        Validate ETF options Greeks consistency and portfolio impact.
        """
        logger.info("=== Starting Options Greeks Reconciliation ===")

        # Calculate portfolio-level Greeks
        portfolio_greeks = {
            'Total_Delta': (df_options['Delta'] * df_options['Portfolio_Quantity']).sum(),
            'Total_Gamma': (df_options['Gamma'] * df_options['Portfolio_Quantity']).sum(),
            'Total_Theta': (df_options['Theta'] * df_options['Portfolio_Quantity']).sum(),
            'Total_Vega': (df_options['Vega'] * df_options['Portfolio_Quantity']).sum(),
            'Total_Rho': (df_options['Rho'] * df_options['Portfolio_Quantity']).sum(),
        }

        # Validate Greeks ranges (realistic bounds)
        options_validation = {
            'Delta_Valid': all(df_options['Delta'].between(-1, 1)),
            'Gamma_Valid': all(df_options['Gamma'] >= 0),
            'Theta_Valid': True,  # Theta can be any value
            'Vega_Valid': all(df_options['Vega'] >= 0),
            'Rho_Valid': True,  # Rho can be any value
        }

        logger.info(f"Portfolio Greeks: {portfolio_greeks}")
        logger.info(f"Greeks Validation: {options_validation}")

        return {
            'portfolio_greeks': portfolio_greeks,
            'validation': options_validation,
            'greeks_data': df_options
        }

    def reconcile_cr_transactions(self, df_transactions: pd.DataFrame) -> Dict:
        """
        Validate Create/Redeem transaction settlement amounts.
        """
        logger.info("=== Starting Create/Redeem Transaction Validation ===")

        # Summary by transaction type
        cr_summary = df_transactions.groupby('Transaction_Type').agg({
            'Basket_Units': 'sum',
            'Cash_Component': 'sum',
            'Transaction_ID': 'count'
        }).rename(columns={'Transaction_ID': 'Count'})

        # Validate settlement amounts (basic checks)
        df_transactions['Cash_Per_Unit'] = df_transactions['Cash_Component'] / df_transactions['Basket_Units']

        # Expected cash per unit range (validation threshold)
        expected_range = (0.02, 0.03)  # Realistic range for SPY
        df_transactions['Settlement_Valid'] = df_transactions['Cash_Per_Unit'].between(expected_range[0], expected_range[1])

        invalid_transactions = df_transactions[~df_transactions['Settlement_Valid']]

        logger.info(f"Transaction validation: {len(df_transactions) - len(invalid_transactions)} valid, {len(invalid_transactions)} suspicious")

        return {
            'summary': cr_summary,
            'transactions': df_transactions,
            'invalid_count': len(invalid_transactions)
        }

    def generate_reconciliation_report(self) -> pd.DataFrame:
        """Generate comprehensive reconciliation report."""

        report_data = {
            'Metric': [
                'Total Internal Records',
                'Total External Records',
                'Reconciled Matches',
                'Unmatched Records',
                'Break Exceptions',
                'Match Rate (%)',
            ],
            'Value': [
                100,  # Placeholder - will be replaced by actual data
                100,
                len(self.matches),
                0,
                len(self.breaks),
                f"{(len(self.matches) / (len(self.matches) + len(self.breaks)) * 100) if (len(self.matches) + len(self.breaks)) > 0 else 0:.2f}",
            ]
        }

        self.reconciliation_report = pd.DataFrame(report_data)
        logger.info("Reconciliation report generated")

        return self.reconciliation_report


def main():
    """Main execution function."""
    logger.info("Starting ETF Reconciliation Process")

    engine = ETFReconciliationEngine(tolerance_pct=0.01, tolerance_qty=0.5)

    # Load data
    df_internal, df_external = engine.load_data(
        'data/internal_pcf_20260324.csv',
        'data/external_dtcc_settlement_20260324.csv'
    )

    # Run reconciliations
    basket_recon = engine.reconcile_baskets(df_internal, df_external)

    # Load options and transactions
    df_options = pd.read_csv('data/etf_options_greeks_20260324.csv')
    df_transactions = pd.read_csv('data/create_redeem_transactions_20260324.csv')

    options_recon = engine.reconcile_options_greeks(df_options)
    cr_recon = engine.reconcile_cr_transactions(df_transactions)

    # Generate report
    report = engine.generate_reconciliation_report()

    logger.info("ETF Reconciliation Process Complete")

    return engine, basket_recon, options_recon, cr_recon, report


if __name__ == "__main__":
    main()
