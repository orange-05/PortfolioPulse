# 📈 PortfolioPulse — AI-Powered Portfolio Dashboard

> A **Streamlit dashboard** for tracking stocks and crypto in real time. Build a weighted portfolio, see live performance, correlation, and get rule-based AI insights — all in your browser, powered by **Yahoo Finance**.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=for-the-badge&logo=plotly)
![yfinance](https://img.shields.io/badge/Data-Yahoo%20Finance-7B1FA2?style=for-the-badge)
![Pandas](https://img.shields.io/badge/Pandas-Data-150458?style=for-the-badge&logo=pandas)

---

## ✨ Features

- 🎯 **Custom weighted portfolios** — mix stocks and crypto (e.g. `RELIANCE.NS, TCS.NS, AAPL, BTC-USD`)
- 📅 **Date range picker** — backtest from any start date
- 💰 **Initial investment input** — see your portfolio grow (or shrink) from any base amount
- 📊 **4 key metrics** — current value, total return, annualized volatility, Sharpe ratio
- 📈 **Portfolio value chart** — cumulative returns plotted with Plotly
- 🔍 **Individual asset prices** — see what each holding did
- 🌡️ **Correlation heatmap** — how your assets move together
- 🤖 **AI insights tab** — rule-based commentary on the latest daily move + a what-if slider
- 📥 **CSV download** — pull the full price history for offline analysis
- 🇮🇳 **Indian market support** — NSE tickers (`.NS`) work out of the box alongside US tickers

---

## 🏗️ Architecture

```
PortfolioPulse/
├── app.py                       # the entire dashboard (single-file Streamlit app)
├── requirements.txt
├── .devcontainer/               # reproducible dev container
└── README.md
```

### Data flow

```
Sidebar inputs (tickers, weights, start date, amount)
   │
   ▼
yf.download(tickers, start=start, auto_adjust=True)
   │
   ▼
prices.pct_change()  ──►  returns
   │
   ▼
returns.dot(weights)  ──►  portfolio_returns
   │
   ▼
cumulative = (1 + portfolio_returns).cumprod() * amount
   │
   ▼
4 KPI cards + 4 tabs (Value / Stocks / EDA / AI Insights)
```

---

## 🚀 Quick Start

### 1. Install

```bash
git clone https://github.com/orange-05/PortfolioPulse.git
cd PortfolioPulse
pip install -r requirements.txt
```

### 2. Run

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

### 3. Build a portfolio

1. In the sidebar, type tickers (comma-separated), e.g.

   ```
   RELIANCE.NS, TCS.NS, AAPL, BTC-USD
   ```

2. Type matching weights (must sum to 100), e.g.

   ```
   40, 30, 20, 10
   ```

3. Pick a start date and an initial investment amount
4. Click **Build Portfolio**

---

## 📊 What you'll see

| Tab | Contents |
|---|---|
| **Portfolio Value** | Single line chart of your portfolio's cumulative value over time |
| **Individual Stocks** | Each asset's price plotted separately |
| **EDA & Correlation** | Correlation heatmap + histogram of daily returns |
| **AI Insights** | Latest-day commentary (strong gain / pullback / stable) + a "shift to equities" what-if slider |

The four KPI cards at the top show:

- 💵 **Current Value**
- 📈 **Total Return** (%)
- 📉 **Volatility (annualized)**
- ⚖️ **Sharpe Ratio** (approx, rf=0)

---

## 🧰 Tech Stack

- **[Streamlit](https://streamlit.io/)** — UI
- **[yfinance](https://pypi.org/project/yfinance/)** — market data from Yahoo Finance
- **[pandas](https://pandas.pydata.org/)** + **[NumPy](https://numpy.org/)** — returns, weights, Sharpe
- **[Plotly Express](https://plotly.com/python/plotly-express/)** — interactive charts

---

## ⚠️ Caveats

- **Yahoo Finance is unofficial** — `yfinance` can break if Yahoo changes its endpoint. If downloads fail, try a wider date range or fewer tickers.
- **Sharpe ratio** uses `rf = 0` (no risk-free rate). The slider in the AI tab is a *rough* estimate, not a portfolio optimizer.
- **Live data** — the dashboard fetches data on demand; there's no background scheduler. Refresh the page to pull new prices.

---

## 🗺️ Roadmap

- [ ] Caching of price downloads to speed up repeat visits
- [ ] Monte Carlo simulation tab
- [ ] Efficient-frontier visualization
- [ ] Persist portfolios in `st.session_state` / a tiny SQLite store
- [ ] Real broker integrations (Zerodha Kite, Alpaca)

---

## 📄 License

MIT — see `LICENSE` for details.
