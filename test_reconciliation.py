"""
Unit tests for ETF Reconciliation Platform
"""

import unittest
import pandas as pd
from datetime import datetime
from etf_reconciliation_engine import ETFReconciliationEngine


class TestETFReconciliation(unittest.TestCase):
    """Test cases for reconciliation engine."""

    def setUp(self):
        """Initialize test fixtures."""
        self.engine = ETFReconciliationEngine(tolerance_pct=0.01, tolerance_qty=0.5)

    def test_engine_initialization(self):
        """Test engine initializes with correct tolerances."""
        self.assertEqual(self.engine.tolerance_pct, 0.01)
        self.assertEqual(self.engine.tolerance_qty, 0.5)

    def test_data_loading(self):
        """Test data loading functionality."""
        df_internal, df_external = self.engine.load_data(
            'data/internal_pcf_20260324.csv',
            'data/external_dtcc_settlement_20260324.csv'
        )
        self.assertIsInstance(df_internal, pd.DataFrame)
        self.assertIsInstance(df_external, pd.DataFrame)
        self.assertGreater(len(df_internal), 0)
        self.assertGreater(len(df_external), 0)

    def test_basket_reconciliation(self):
        """Test basket reconciliation logic."""
        df_internal, df_external = self.engine.load_data(
            'data/internal_pcf_20260324.csv',
            'data/external_dtcc_settlement_20260324.csv'
        )
        basket_recon = self.engine.reconcile_baskets(df_internal, df_external)

        # Check reconciliation produces expected columns
        self.assertIn('Qty_Variance', basket_recon.columns)
        self.assertIn('Val_Variance', basket_recon.columns)
        self.assertIn('Match_Status', basket_recon.columns)

    def test_greeks_validation(self):
        """Test options Greeks validation."""
        df_options = pd.read_csv('data/etf_options_greeks_20260324.csv')
        greeks_result = self.engine.reconcile_options_greeks(df_options)

        # Check all Greeks calculated
        self.assertIn('Total_Delta', greeks_result['portfolio_greeks'])
        self.assertIn('Total_Gamma', greeks_result['portfolio_greeks'])
        self.assertIn('Total_Theta', greeks_result['portfolio_greeks'])

    def test_cr_transaction_validation(self):
        """Test Create/Redeem transaction validation."""
        df_transactions = pd.read_csv('data/create_redeem_transactions_20260324.csv')
        cr_result = self.engine.reconcile_cr_transactions(df_transactions)

        # Check transactions processed
        self.assertGreater(len(cr_result['transactions']), 0)
        self.assertIn('Settlement_Valid', cr_result['transactions'].columns)


if __name__ == '__main__':
    unittest.main()
