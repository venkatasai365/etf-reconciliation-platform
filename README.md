# ETF Data Reconciliation & Reporting Platform

A production-grade Python application for ETF operations reconciliation, settlement validation, and daily reporting.

## Overview

This platform automates the critical front-office operations workflow for ETF administration:

- **PCF Reconciliation**: Matches internal Portfolio Composition Files with external DTCC/custodian settlement records
- **Settlement Validation**: Tracks ETF Create/Redeem transactions and validates settlement amounts
- **Options Greeks Analysis**: Reconciles portfolio options exposures (Delta, Gamma, Theta, Vega, Rho)
- **Daily Reporting**: Generates basket composition, settlement status, and exception reports for stakeholders

## Project Structure

```
ETF_Reconciliation_Platform/
├── data/                              # Sample datasets
│   ├── internal_pcf_20260324.csv              # Internal portfolio composition
│   ├── external_dtcc_settlement_20260324.csv  # DTCC settlement records
│   ├── etf_options_greeks_20260324.csv        # Options Greeks data
│   └── create_redeem_transactions_20260324.csv # CR transactions
├── reports/                           # Generated daily reports
├── logs/                              # Application logs
├── etf_reconciliation_engine.py       # Core reconciliation logic
├── etf_reporting_system.py            # Report generation
├── main.py                            # Application entry point
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

## Key Features

### 1. ETF Basket Reconciliation
- Matches internal PCF against external DTCC settlement data
- Configurable tolerance levels for quantity and valuation discrepancies
- Identifies and flags reconciliation breaks for manual review
- Generates detailed variance analysis (quantity %, valuation %)

### 2. Settlement Processing
- Tracks Create and Redeem transactions
- Validates cash settlement amounts per basket unit
- Monitors settlement schedules (T-Date, T+0, T+1, T+2)
- Identifies suspicious or exceptional transactions

### 3. Options Greeks Management
- Aggregates portfolio-level Greeks exposures
- Validates individual option Greeks (Delta, Gamma, Theta, Vega, Rho)
- Calculates cumulative portfolio sensitivity to price, volatility, time
- Supports options on leveraged ETFs (LETFs)

### 4. Daily Reporting
- **Basket Composition Report**: Securities holdings and cash for Portfolio Managers
- **Settlement Status Report**: Create/Redeem activity and settlement tracking for Operations
- **Greeks Analysis Report**: Portfolio option exposures for Risk Management
- **Exception Report**: Reconciliation breaks and discrepancies requiring investigation

## Installation & Usage

### Prerequisites
- Python 3.8+
- pandas, numpy

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run daily reconciliation
python main.py --date 2026-03-24 --etf SPY

# Or with default parameters
python main.py
```

### Sample Output

```
Starting ETF Reconciliation Platform for SPY on 2026-03-24

[STEP 1/4] Reconciling ETF Baskets...
✓ Loaded internal data: 8 records
✓ Loaded external data: 8 records
✓ Reconciliation complete: 7 MATCHES, 1 BREAK

[STEP 2/4] Reconciling Options Greeks...
✓ Portfolio Greeks calculated
✓ Greeks Validation: All valid

[STEP 3/4] Validating Create/Redeem Transactions...
✓ Processed 5 CR transactions
✓ All settlement amounts within expected range

[STEP 4/4] Generating Reports...
✓ Reports generated in: reports/
```

## Data Format

### Internal PCF (Portfolio Composition File)
```csv
Trade_Date,ETF_Ticker,Basket_ID,Security_ID,Quantity,Price,Valuation,Source
2026-03-24,SPY,1,AAPL,150,185.75,27862.50,Internal
```

### External DTCC Settlement
```csv
Trade_Date,ETF_Ticker,Basket_ID,Security_ID,Quantity,Price,Valuation,Source
2026-03-24,SPY,1,AAPL,150,185.75,27862.50,External_DTCC
```

### Options Greeks
```csv
Option_ID,ETF_Underlying,Expiration,Strike,Option_Type,Spot_Price,Last_Price,Delta,Gamma,Theta,Vega,Rho,Portfolio_Quantity
SPY_CALL_385,SPY,2026-04-17,385,CALL,384.50,8.75,0.68,0.012,-0.025,0.35,0.15,500
```

## Configuration

Tolerance levels can be adjusted in `ETFReconciliationEngine`:

```python
engine = ETFReconciliationEngine(
    tolerance_pct=0.01,    # 1% tolerance for valuation differences
    tolerance_qty=0.5      # 0.5 unit tolerance for quantity differences
)
```

## Real-World Workflow Integration

### Morning Workflow (T-Day)
1. ETF Agent sends PCF files at ~7:00 AM
2. Platform loads PCF and DTCC settlement data
3. Reconciliation runs automatically
4. Exception reports flagged to Operations for investigation
5. Basket Composition Report sent to Portfolio Managers by 8:30 AM

### Daily Operations
- Monitor Create/Redeem transactions throughout the day
- Validate settlement amounts and identify unusual patterns
- Track portfolio Greeks for risk management

### End-of-Day
- Final reconciliation for settlement day
- Generate comprehensive daily reports
- Archive logs and reports for compliance

## Business Impact

- **Automation**: Replaces manual reconciliation (2-3 hours → 5 minutes)
- **Accuracy**: Catches discrepancies before settlement
- **Auditability**: Full logging and report trail
- **Scalability**: Handles multiple ETFs simultaneously
- **Risk Management**: Portfolio-level Greeks analysis for position monitoring

## Technical Architecture

### Reconciliation Engine (etf_reconciliation_engine.py)
- `ETFReconciliationEngine`: Main orchestrator
  - `load_data()`: CSV loading and validation
  - `reconcile_baskets()`: Core PCF matching logic
  - `reconcile_options_greeks()`: Options Greeks aggregation
  - `reconcile_cr_transactions()`: Settlement validation
  - `generate_reconciliation_report()`: Summary report generation

### Reporting System (etf_reporting_system.py)
- `ETFReportingSystem`: Report generation engine
  - `generate_basket_composition_report()`: Holdings summary
  - `generate_settlement_status_report()`: CR transactions tracking
  - `generate_greeks_analysis_report()`: Risk exposure analysis
  - `generate_exception_report()`: Break items and discrepancies
  - `export_report_to_file()`: File export functionality

### Main Application (main.py)
- Command-line interface with argument parsing
- Orchestrates full reconciliation workflow
- Error handling and logging

## For Job Applications

This project demonstrates:
1. **Front-Office Operations Knowledge**: PCF, DTCC, settlement processes
2. **Python Programming**: OOP, pandas, logging, error handling
3. **Data Reconciliation**: Matching algorithms, tolerance handling, exception reporting
4. **Report Generation**: Stakeholder-facing documentation
5. **System Design**: Modular architecture, configuration management
6. **Production Quality**: Logging, error handling, documentation

### Portfolio Impact
- Shows ability to design automated solutions for manual processes
- Demonstrates understanding of ETF lifecycle (creation, redemption, settlement)
- Exhibits data manipulation and analytics skills
- Aligns with FOO Analyst job requirements

## Future Enhancements

- [ ] Database integration (PostgreSQL for historical tracking)
- [ ] Real-time alert system for breaks
- [ ] Web dashboard for report visualization
- [ ] Multi-currency support
- [ ] Options pricing models (Black-Scholes validation)
- [ ] API integration with DTCC systems
- [ ] Email notification system

## Author
[Your Name]  
Quantitative Analyst / ETF Operations Specialist  
LinkedIn: [Your Profile]  
GitHub: [Your Repository]

## License
Proprietary - For demonstration purposes

---

**Last Updated**: March 24, 2026  
**Version**: 1.0.0
