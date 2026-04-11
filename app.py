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
    st.sidebar.error("Invalid weights. Please use numbers only.")
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

    with st.spinner("Fetching live market data from Yahoo Finance..."):
        try:
            # Download data - more robust for cloud
            data = yf.download(tickers, start=start_date, progress=False, auto_adjust=True, threads=False)
            
            if isinstance(data.columns, pd.MultiIndex):
                prices = data['Close']
            else:
                # Single ticker case
                prices = pd.DataFrame(data['Close'], columns=tickers)
                
            # Clean data
            prices = prices.dropna(how='all').ffill().dropna()
            
            if prices.empty or len(prices) < 2:
                st.error("❌ Not enough price data returned. Try these fixes:")
                st.error("• Change Start Date to an older date (e.g., 2023-01-01)")
                st.error("• Remove or check tickers (some may be delisted or have issues)")
                st.error("• Try fewer tickers first")
                st.stop()
                
        except Exception as e:
            st.error(f"Failed to fetch data: {str(e)}")
            st.stop()

        # Calculate returns
        returns = prices.pct_change().dropna()
        
        if returns.empty:
            st.error("No valid daily returns could be calculated.")
            st.stop()

        # Normalize weights
        weights = np.array(weights[:len(prices.columns)])
        weights = weights / weights.sum()

        # Portfolio returns & cumulative value
        portfolio_returns = returns.dot(weights)
        cumulative = (1 + portfolio_returns).cumprod() * amount

        # === SAFETY CHECK BEFORE METRICS ===
        if len(cumulative) == 0:
            st.error("Portfolio calculation returned no data. Please try a different date range or tickers.")
            st.stop()

        st.subheader("📊 Portfolio Performance")
        col1, col2, col3, col4 = st.columns(4)
        
        current_value = cumulative.iloc[-1]
        total_return = ((current_value / amount) - 1) * 100
        volatility = portfolio_returns.std() * np.sqrt(252) * 100
        sharpe = (portfolio_returns.mean() / portfolio_returns.std()) * np.sqrt(252) if portfolio_returns.std() != 0 else 0

        col1.metric("Current Value", f"₹{current_value:,.0f}")
        col2.metric("Total Return", f"{total_return:.2f}%")
        col3.metric("Volatility (Ann.)", f"{volatility:.2f}%")
        col4.metric("Sharpe Ratio (approx)", f"{sharpe:.2f}")

        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Portfolio Value", "Individual Stocks", "EDA & Correlation", "AI Insights"])

        with tab1:
            fig = px.line(cumulative, title="Portfolio Value Over Time", labels={'value': 'Portfolio Value (₹)'})
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
            fig4 = px.histogram(portfolio_returns, nbins=50)
            st.plotly_chart(fig4, use_container_width=True)

        with tab4:
            st.subheader("🤖 AI Insights")
            latest_ret = portfolio_returns.iloc[-1] * 100
            if latest_ret > 1.5:
                st.success(f"Strong positive momentum today (+{latest_ret:.2f}%).")
            elif latest_ret < -1.5:
                st.warning(f"Pullback today ({latest_ret:.2f}%). Consider reviewing.")
            else:
                st.info("Market is stable today.")

            st.write("**What-if Analysis**")
            new_weight = st.slider("Increase equity weight by (%)", 0, 30, 10)
            st.info(f"Shifting +{new_weight}% to equities could increase expected annual return by ~{new_weight * 0.8:.1f}% (estimate).")

        # Download
        csv = prices.to_csv().encode('utf-8')
        st.download_button("📥 Download Full Price Data (CSV)", csv, "portfolio_data.csv", "text/csv")

        st.success("✅ Portfolio built successfully!")

else:
    st.info("👈 Fill the sidebar and click **Build Portfolio** to see your portfolio analysis.")
