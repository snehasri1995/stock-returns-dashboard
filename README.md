# Stock Returns Dashboard

An interactive financial analytics dashboard tracking 3 years of daily price data across 10 tickers — equities, fixed income, and commodities.

**Live UI built with Streamlit + Plotly. Static analysis in Jupyter.**

---

## Dashboard Preview

| Section | Description |
|---|---|
| Correlation Heatmap | Pairwise Pearson correlation of daily returns |
| Annualized Returns | Which stocks performed best over 2022–2024 |
| Annualized Volatility | Which stocks carried the most risk |
| Cumulative Returns | Growth of $1 invested from Jan 2022 |
| Summary Statistics | Returns, volatility, Sharpe ratio, and max drawdown per ticker |

---

## Universe

| Ticker | Asset |
|---|---|
| AAPL, AMZN, MSFT | US Large-Cap Tech |
| JPM, BLK | US Financials |
| XOM | US Energy |
| QQQ, SPY | Broad Market ETFs |
| GLD | Gold (commodity hedge) |
| BND | US Aggregate Bond ETF |

**Period:** January 2022 – December 2024  
**Data source:** Yahoo Finance via `yfinance`

---

## Project Structure

```
stock-returns-dashboard/
├── app.py                 # Streamlit interactive dashboard
├── data.py                # Data download & metric computation
├── visualization.ipynb    # Jupyter notebook with static charts
├── visualize.py           # Standalone correlation heatmap
├── prices.csv             # Adjusted closing prices
├── returns.csv            # Daily percentage returns
└── requirements.txt       # Python dependencies
```

---

## Quickstart

**1. Clone the repo**
```bash
git clone https://github.com/snehasri1995/stock-returns-dashboard.git
cd stock-returns-dashboard
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. (Optional) Refresh data**
```bash
python data.py
```

**4. Launch the dashboard**
```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Key Metrics

All metrics computed from daily returns:

- **Annualized Return** = mean daily return × 252
- **Annualized Volatility** = std dev of daily returns × √252
- **Sharpe Ratio** = Ann. Return / Ann. Volatility *(risk-free rate = 0)*
- **Max Drawdown** = largest peak-to-trough decline over the period

---

## Tech Stack

- **Python 3** — pandas, numpy
- **Streamlit** — interactive web UI
- **Plotly** — interactive charts
- **Matplotlib / Seaborn** — static charts (Jupyter)
- **yfinance** — market data

---

*Built as part of a quantitative finance portfolio project.*
