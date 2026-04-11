import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

st.set_page_config(page_title="PortfolioPulse - AI Portfolio Dashboard", layout="wide")
st.title("🚀 PortfolioPulse")
st.markdown("**AI-Powered Stock & Crypto Portfolio Tracker** | Built as a live demo by Karthikeyan")

# Sidebar
st.sidebar.header("Your Portfolio")

tickers_input = st.sidebar.text_input(
    "Enter tickers (comma separated)", 
    "RELIANCE.NS, TCS.NS, AAPL, BTC-USD"
)
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

weights_input = st.sidebar.text_input(
    "Weights % (comma separated, must sum to 100)", 
    "40,30,20,10"
)
try:
    weights = [float(w.strip()) / 100 for w in weights_input.split(",")]
except ValueError:
    st.sidebar.error("Invalid weights. Please enter numbers only.")
    weights = []

start_date = st.sidebar.date_input("Start Date", datetime(2024, 1, 1))
amount = st.sidebar.number_input("Initial Investment (₹ / $)", value=100000.0, min_value=1000.0)

if st.sidebar.button("Build Portfolio"):
    if len(tickers) == 0:
        st.error("Please enter at least one ticker.")
        st.stop()
    if len(weights) != len(tickers):
        st.error(f"Number of weights ({len(weights)}) must match number of tickers ({len(tickers)}).")
        st.stop()
    if abs(sum(weights) - 1.0) > 0.01:
        st.warning("Weights do not sum to 100%. They will be normalized.")

    with st.spinner("Fetching live market data from Yahoo Finance..."):
        # Download all at once (more efficient and better alignment)
        try:
            data = yf.download(tickers, start=start_date, progress=False, auto_adjust=True)
        except Exception as e:
            st.error(f"Failed to download data: {e}")
            st.stop()

        if data.empty:
            st.error("No data returned. Check tickers or date range.")
            st.stop()

        # Extract Close prices - handle both single and multi-ticker cases
        if len(tickers) == 1:
            prices = pd.DataFrame(data['Close']).rename(columns={'Close': tickers[0]})
        else:
            prices = data['Close'] if 'Close' in data.columns.levels[0] else data

        # Drop any rows where ALL prices are NaN
        prices = prices.dropna(how='all')

        if prices.empty:
            st.error("No valid price data found for the selected period.")
            st.stop()

        # Forward-fill missing prices (common for different trading days, e.g., stocks vs crypto)
        prices = prices.ffill().dropna()

        # Calculate daily returns
        returns = prices.pct_change().dropna()

        # Normalize weights in case they don't sum exactly to 1
        weights = np.array(weights[:len(prices.columns)])
        weights = weights / weights.sum()

        # Portfolio returns
        portfolio_returns = returns.dot(weights)

        # Cumulative portfolio value
        cumulative = (1 + portfolio_returns).cumprod() * amount

        st.subheader("📊 Portfolio Performance")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Value", f"₹{cumulative.iloc[-1]:,.0f}")
        col2.metric("Total Return", f"{((cumulative.iloc[-1] / amount) - 1) * 100:.2f}%")
        col3.metric("Volatility (Ann.)", f"{portfolio_returns.std() * np.sqrt(252) * 100:.2f}%")
        col4.metric("Sharpe Ratio (approx)", 
                    f"{(portfolio_returns.mean() / portfolio_returns.std()) * np.sqrt(252):.2f}" 
                    if portfolio_returns.std() != 0 else "N/A")

        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Portfolio Value", "Individual Stocks", "EDA & Correlation", "AI Insights"])

        with tab1:
            fig = px.line(cumulative, title="Portfolio Value Over Time", labels={'value': 'Portfolio Value'})
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig2 = px.line(prices, title="Individual Asset Prices")
            st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            st.write("**Correlation Heatmap**")
            corr = returns.corr()
            fig3 = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu', aspect='auto')
            st.plotly_chart(fig3, use_container_width=True)

            st.write("**Portfolio Daily Returns Distribution**")
            fig4 = px.histogram(portfolio_returns, nbins=50, title="Daily Returns Distribution")
            st.plotly_chart(fig4, use_container_width=True)

        with tab4:
            st.subheader("🤖 AI Insights")
            latest_return = portfolio_returns.iloc[-1] * 100
            if latest_return > 1.5:
                st.success(f"Strong positive momentum today (+{latest_return:.2f}%). Consider holding or adding.")
            elif latest_return < -1.5:
                st.warning(f"Pullback today ({latest_return:.2f}%). Review allocation.")
            else:
                st.info("Market is relatively stable today.")

            st.write("**What-if Analysis**")
            new_weight = st.slider("Increase equity weight by (%)", 0, 30, 10)
            st.info(f"Shifting +{new_weight}% to equities could boost expected annual return by ~{new_weight * 0.8:.1f}% "
                    f"(rough estimate based on historical data).")

            st.caption("💡 Pro tip: Real LLM integration (Groq / Gemini / Grok) can be added in the full custom version.")

        # Download button
        csv = prices.to_csv().encode('utf-8')
        st.download_button(
            label="📥 Download Full Price Data (CSV)",
            data=csv,
            file_name="portfolio_data.csv",
            mime="text/csv"
        )

        st.success("✅ Portfolio built successfully!")

else:
    st.info("👈 Enter your tickers, weights, and click **Build Portfolio** to analyze.")