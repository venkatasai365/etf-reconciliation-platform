# ETF Reconciliation Platform - Usage Guide

## Quick Start

### 1. Installation
```bash
# Clone repository
git clone [your-repo-url]
cd ETF_Reconciliation_Platform

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Daily Reconciliation
```bash
# With default parameters (today's date, SPY)
python main.py

# With specific date and ETF
python main.py --date 2026-03-24 --etf SPY

# View help
python main.py --help
```

### 3. Check Reports
```bash
# All reports generated in reports/ directory
ls reports/

# View specific report
cat reports/basket_composition_report_20260324.txt
cat reports/settlement_status_report_20260324.txt
cat reports/greeks_analysis_report_20260324.txt
cat reports/exception_report_20260324.txt
```

### 4. Check Logs
```bash
# Application logs
tail -f logs/reconciliation.log
```

---

## Detailed Workflow

### Input Data Preparation

Before running reconciliation, ensure input files exist:

1. **Internal PCF File**: `data/internal_pcf_YYYYMMDD.csv`
   ```csv
   Trade_Date,ETF_Ticker,Basket_ID,Security_ID,Quantity,Price,Valuation,Source
   ```

2. **External Settlement File**: `data/external_dtcc_settlement_YYYYMMDD.csv`
   ```csv
   Trade_Date,ETF_Ticker,Basket_ID,Security_ID,Quantity,Price,Valuation,Source
   ```

3. **Options Greeks File** (optional): `data/etf_options_greeks_YYYYMMDD.csv`
   ```csv
   Option_ID,ETF_Underlying,Expiration,Strike,Option_Type,Spot_Price,Last_Price,Delta,Gamma,Theta,Vega,Rho,Portfolio_Quantity
   ```

4. **Transactions File** (optional): `data/create_redeem_transactions_YYYYMMDD.csv`
   ```csv
   Transaction_Date,Transaction_ID,Transaction_Type,ETF_Ticker,Basket_Units,AP_Name,Cash_Component,Settlement_Date
   ```

### Execution Steps

1. **Load Data**: Platform reads CSV files from `data/` directory
2. **Reconcile Baskets**: Matches internal vs external records
   - Merges on: Trade_Date, ETF_Ticker, Security_ID
   - Calculates variances: Quantity, Valuation
   - Applies tolerance checks (default: 1%)
3. **Reconcile Options**: Validates Greeks and aggregates portfolio exposure
4. **Validate Transactions**: Checks Create/Redeem settlement amounts
5. **Generate Reports**: Creates stakeholder-facing documentation

### Output Reports

#### Basket Composition Report
**Purpose**: Portfolio Managers need to know daily holdings  
**Format**: Markdown-style text report  
**Contents**:
- List of all securities in ETF basket
- Quantities and valuations
- Top 5 holdings by weight
- Cash component

**Use Case**: 
- Verify intraday portfolio for trading decisions
- Confirm index rebalancing
- Monitor exposure concentrations

#### Settlement Status Report
**Purpose**: Operations team tracks Create/Redeem activity  
**Format**: Text report with transaction table  
**Contents**:
- Summary of CREATE and REDEEM transactions
- Basket units and cash amounts
- Detailed transaction listing
- Settlement calendar (T-Date through T+2)

**Use Case**:
- Monitor settlement progress
- Track cash flows
- Verify delivery schedules

#### Greeks Analysis Report
**Purpose**: Risk Management tracks options exposures  
**Format**: Text report with sensitivity analysis  
**Contents**:
- Portfolio-level Delta, Gamma, Theta, Vega, Rho
- Interpretation of each Greek
- Validation status of Greeks
- Risk sensitivity interpretations

**Use Case**:
- Monitor portfolio Greeks before market open
- Track Greeks changes EOD
- Hedge or rebalance portfolio

#### Exception Report
**Purpose**: Operational risk - flags discrepancies  
**Format**: Text report with break details  
**Contents**:
- Reconciliation summary (matches vs breaks)
- Match rate percentage
- List of exception records
- Priority for investigation

**Use Case**:
- Identify reconciliation failures
- Escalate breaks to management
- Support audit trail

---

## Configuration & Tuning

### Adjust Tolerance Levels

Edit `main.py`:

```python
# Current tolerances
engine = ETFReconciliationEngine(
    tolerance_pct=0.01,    # 1% for valuations
    tolerance_qty=0.5      # 0.5 units for quantities
)

# Conservative (stricter)
engine = ETFReconciliationEngine(
    tolerance_pct=0.005,   # 0.5% tolerance
    tolerance_qty=0.1      # 0.1 unit tolerance
)

# Permissive (looser)
engine = ETFReconciliationEngine(
    tolerance_pct=0.02,    # 2% tolerance
    tolerance_qty=1.0      # 1 unit tolerance
)
```

### Add New Reconciliation Rules

In `etf_reconciliation_engine.py`:

```python
def reconcile_baskets(self, df_internal, df_external):
    # After existing matching logic:

    # Custom rule: Flag if quantity > 500 units
    matched['Large_Qty'] = matched['Quantity_INT'] > 500

    # Custom rule: Flag if valuation variance > $10,000
    matched['Large_Val_Break'] = abs(matched['Val_Variance']) > 10000
```

### Monitor Specific ETFs

In `main.py`:

```python
# Add ETF-specific thresholds
ETF_CONFIG = {
    'SPY': {'tolerance_pct': 0.01, 'alert_if_breaks': 5},
    'QQQ': {'tolerance_pct': 0.015, 'alert_if_breaks': 3},
    'IWM': {'tolerance_pct': 0.02, 'alert_if_breaks': 7},
}
```

---

## Troubleshooting

### No input files found
```
FileNotFoundError: data/internal_pcf_20260324.csv
```
**Solution**: 
- Check data files exist in `data/` directory
- Use correct date format (YYYYMMDD)
- Verify file naming convention

### Reconciliation takes too long
- Split large files (>100K records) into multiple runs
- Increase tolerance_pct to reduce break handling
- Use filtering: reconcile only specific securities

### Greeks validation fails
- Check all Greeks values are numeric (not text)
- Verify Delta is between -1 and 1
- Verify Gamma, Vega >= 0
- Check Theta and Rho for NaN values

### Reports not generated
- Verify `reports/` directory exists
- Check write permissions
- Review logs for error messages

---

## Running Tests

```bash
# Run all tests
python -m unittest test_reconciliation

# Run specific test
python -m unittest test_reconciliation.TestETFReconciliation.test_basket_reconciliation

# Verbose output
python -m unittest test_reconciliation -v
```

---

## Integration with Excel/BI Tools

Export reconciliation summary to Excel:

```python
# In main.py, after reconciliation
summary = engine.generate_reconciliation_report()
summary.to_excel('reports/summary.xlsx', index=False)
```

Create Power BI or Tableau visualization:
```bash
# Point visualization tool to:
reports/reconciliation_summary_20260324.csv
```

---

## API Usage (Advanced)

```python
from etf_reconciliation_engine import ETFReconciliationEngine
from etf_reporting_system import ETFReportingSystem

# Custom workflow
engine = ETFReconciliationEngine(tolerance_pct=0.01)
df_internal, df_external = engine.load_data('internal.csv', 'external.csv')
basket_recon = engine.reconcile_baskets(df_internal, df_external)

# Custom reporting
reporter = ETFReportingSystem('SPY', '2026-03-24')
report = reporter.generate_basket_composition_report(basket_recon)
print(report)
```

---

## Support & Contact

For issues or questions:
1. Check logs: `logs/reconciliation.log`
2. Review documentation: `README.md`
3. Run tests: `python -m unittest test_reconciliation`
4. Contact: [your-email@company.com]

---

**Last Updated**: March 24, 2026  
**Version**: 1.0.0
