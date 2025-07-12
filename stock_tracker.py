import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import time
from typing import Dict, List, Optional

# Configure Streamlit page
st.set_page_config(
    page_title="Fortune 500 Stock Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        padding: 1rem 0;
        border-bottom: 2px solid #e6f3ff;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .stock-card {
        border: 1px solid #e6f3ff;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .positive { color: #28a745; }
    .negative { color: #dc3545; }
    .neutral { color: #6c757d; }
</style>
""", unsafe_allow_html=True)

class StockTracker:
    def __init__(self):
        self.fortune_500_tickers = self.get_fortune_500_tickers()
        self.cache_duration = 300  # 5 minutes
        
    def get_fortune_500_tickers(self) -> Dict[str, Dict]:
        """Returns a dictionary of Fortune 500 companies with their details"""
        return {
            # Technology
            "AAPL": {"name": "Apple Inc.", "sector": "Technology"},
            "MSFT": {"name": "Microsoft Corporation", "sector": "Technology"},
            "GOOGL": {"name": "Alphabet Inc.", "sector": "Technology"},
            "AMZN": {"name": "Amazon.com Inc.", "sector": "Technology"},
            "NVDA": {"name": "NVIDIA Corporation", "sector": "Technology"},
            "TSLA": {"name": "Tesla Inc.", "sector": "Technology"},
            "META": {"name": "Meta Platforms Inc.", "sector": "Technology"},
            "NFLX": {"name": "Netflix Inc.", "sector": "Technology"},
            "ADBE": {"name": "Adobe Inc.", "sector": "Technology"},
            "CRM": {"name": "Salesforce Inc.", "sector": "Technology"},
            
            # Finance
            "BRK-B": {"name": "Berkshire Hathaway", "sector": "Finance"},
            "JPM": {"name": "JPMorgan Chase", "sector": "Finance"},
            "BAC": {"name": "Bank of America", "sector": "Finance"},
            "WFC": {"name": "Wells Fargo", "sector": "Finance"},
            "GS": {"name": "Goldman Sachs", "sector": "Finance"},
            "MS": {"name": "Morgan Stanley", "sector": "Finance"},
            "C": {"name": "Citigroup", "sector": "Finance"},
            "AXP": {"name": "American Express", "sector": "Finance"},
            
            # Healthcare
            "JNJ": {"name": "Johnson & Johnson", "sector": "Healthcare"},
            "UNH": {"name": "UnitedHealth Group", "sector": "Healthcare"},
            "PFE": {"name": "Pfizer Inc.", "sector": "Healthcare"},
            "ABBV": {"name": "AbbVie Inc.", "sector": "Healthcare"},
            "TMO": {"name": "Thermo Fisher Scientific", "sector": "Healthcare"},
            "ABT": {"name": "Abbott Laboratories", "sector": "Healthcare"},
            "MRK": {"name": "Merck & Co.", "sector": "Healthcare"},
            "CVS": {"name": "CVS Health", "sector": "Healthcare"},
            
            # Energy
            "XOM": {"name": "Exxon Mobil", "sector": "Energy"},
            "CVX": {"name": "Chevron Corporation", "sector": "Energy"},
            "COP": {"name": "ConocoPhillips", "sector": "Energy"},
            "SLB": {"name": "Schlumberger", "sector": "Energy"},
            
            # Consumer Goods
            "PG": {"name": "Procter & Gamble", "sector": "Consumer Goods"},
            "KO": {"name": "Coca-Cola", "sector": "Consumer Goods"},
            "PEP": {"name": "PepsiCo", "sector": "Consumer Goods"},
            "WMT": {"name": "Walmart", "sector": "Consumer Goods"},
            "HD": {"name": "Home Depot", "sector": "Consumer Goods"},
            "MCD": {"name": "McDonald's", "sector": "Consumer Goods"},
            
            # Industrial
            "BA": {"name": "Boeing", "sector": "Industrial"},
            "CAT": {"name": "Caterpillar", "sector": "Industrial"},
            "GE": {"name": "General Electric", "sector": "Industrial"},
            "MMM": {"name": "3M Company", "sector": "Industrial"},
        }
    
    @st.cache_data(ttl=300)
    def fetch_stock_data(_self, tickers: List[str]) -> pd.DataFrame:
        """Fetch real-time stock data for given tickers"""
        try:
            data = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, ticker in enumerate(tickers):
                try:
                    status_text.text(f'Fetching data for {ticker}...')
                    
                    # Get stock data
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period="2d")
                    info = stock.info
                    
                    if len(hist) >= 1:
                        current_price = hist['Close'].iloc[-1]
                        prev_close = info.get('previousClose', current_price)
                        change = current_price - prev_close
                        change_percent = (change / prev_close) * 100
                        
                        # Get additional metrics
                        market_cap = info.get('marketCap', 0)
                        pe_ratio = info.get('trailingPE', 0)
                        dividend_yield = info.get('dividendYield', 0)
                        volume = hist['Volume'].iloc[-1] if len(hist) > 0 else 0
                        
                        data.append({
                            'Ticker': ticker,
                            'Name': _self.fortune_500_tickers[ticker]['name'],
                            'Sector': _self.fortune_500_tickers[ticker]['sector'],
                            'Price': current_price,
                            'Change': change,
                            'Change%': change_percent,
                            'Market Cap': market_cap,
                            'P/E Ratio': pe_ratio,
                            'Dividend Yield': dividend_yield * 100 if dividend_yield else 0,
                            'Volume': volume
                        })
                    
                    progress_bar.progress((i + 1) / len(tickers))
                    
                except Exception as e:
                    st.warning(f"Error fetching data for {ticker}: {str(e)}")
                    continue
            
            progress_bar.empty()
            status_text.empty()
            return pd.DataFrame(data)
            
        except Exception as e:
            st.error(f"Error fetching stock data: {str(e)}")
            return pd.DataFrame()
    
    def format_market_cap(self, market_cap):
        """Format market cap for display"""
        if market_cap == 0:
            return 'N/A'
        
        if market_cap >= 1e12:
            return f"${market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            return f"${market_cap/1e9:.2f}B"
        elif market_cap >= 1e6:
            return f"${market_cap/1e6:.2f}M"
        else:
            return f"${market_cap:,.0f}"
    
    def create_price_chart(self, ticker: str, period: str = "1mo") -> go.Figure:
        """Create a price chart for a specific ticker"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            fig = go.Figure()
            
            # Add candlestick chart
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name=ticker
            ))
            
            fig.update_layout(
                title=f"{ticker} - {self.fortune_500_tickers[ticker]['name']}",
                yaxis_title="Price ($)",
                xaxis_title="Date",
                template="plotly_white",
                height=400
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating chart for {ticker}: {str(e)}")
            return None
    
    def create_sector_performance_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create a sector performance chart"""
        try:
            sector_performance = df.groupby('Sector')['Change%'].mean().sort_values(ascending=False)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=sector_performance.index,
                    y=sector_performance.values,
                    marker_color=['green' if x > 0 else 'red' for x in sector_performance.values]
                )
            ])
            
            fig.update_layout(
                title="Average Sector Performance Today",
                xaxis_title="Sector",
                yaxis_title="Average Change (%)",
                template="plotly_white",
                height=400
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating sector chart: {str(e)}")
            return None

def main():
    # Initialize tracker
    tracker = StockTracker()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📈 Fortune 500 Stock Tracker</h1>
        <p>Real-time monitoring of America's largest companies</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar controls
    st.sidebar.header("🔧 Controls")
    
    # Sector filter
    sectors = ['All'] + list(set([info['sector'] for info in tracker.fortune_500_tickers.values()]))
    selected_sector = st.sidebar.selectbox("Filter by Sector", sectors)
    
    # Number of companies to display
    num_companies = st.sidebar.slider("Number of Companies", 10, 50, 20)
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.experimental_rerun()
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=False)
    
    # Filter tickers based on sector
    if selected_sector == 'All':
        filtered_tickers = list(tracker.fortune_500_tickers.keys())[:num_companies]
    else:
        filtered_tickers = [
            ticker for ticker, info in tracker.fortune_500_tickers.items()
            if info['sector'] == selected_sector
        ][:num_companies]
    
    # Fetch data
    with st.spinner("Fetching real-time stock data..."):
        df = tracker.fetch_stock_data(filtered_tickers)
    
    if df.empty:
        st.error("No data available. Please check your internet connection and try again.")
        return
    
    # Market Overview
    st.subheader("📊 Market Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_change = df['Change%'].mean()
        st.metric(
            "Average Change",
            f"{avg_change:.2f}%",
            delta=f"{avg_change:.2f}%"
        )
    
    with col2:
        gainers = len(df[df['Change%'] > 0])
        st.metric("Gainers", gainers)
    
    with col3:
        losers = len(df[df['Change%'] < 0])
        st.metric("Losers", losers)
    
    with col4:
        total_volume = df['Volume'].sum()
        st.metric("Total Volume", f"{total_volume/1e6:.1f}M")
    
    # Sector Performance Chart
    st.subheader("📈 Sector Performance")
    sector_chart = tracker.create_sector_performance_chart(df)
    if sector_chart:
        st.plotly_chart(sector_chart, use_container_width=True)
    
    # Stock Table
    st.subheader("📋 Stock Data")
    
    # Format the dataframe for display
    display_df = df.copy()
    display_df['Price'] = display_df['Price'].apply(lambda x: f"${x:.2f}")
    display_df['Change'] = display_df['Change'].apply(lambda x: f"${x:.2f}")
    display_df['Change%'] = display_df['Change%'].apply(lambda x: f"{x:.2f}%")
    display_df['Market Cap'] = display_df['Market Cap'].apply(tracker.format_market_cap)
    display_df['P/E Ratio'] = display_df['P/E Ratio'].apply(lambda x: f"{x:.2f}" if x > 0 else 'N/A')
    display_df['Dividend Yield'] = display_df['Dividend Yield'].apply(lambda x: f"{x:.2f}%" if x > 0 else 'N/A')
    display_df['Volume'] = display_df['Volume'].apply(lambda x: f"{x/1e6:.1f}M" if x > 0 else 'N/A')
    
    st.dataframe(display_df, use_container_width=True)
    
    # Individual Stock Charts
    st.subheader("📊 Individual Stock Charts")
    
    # Stock selection for detailed view
    selected_stock = st.selectbox(
        "Select a stock for detailed chart",
        options=df['Ticker'].tolist(),
        format_func=lambda x: f"{x} - {tracker.fortune_500_tickers[x]['name']}"
    )
    
    if selected_stock:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Time period selection
            period = st.selectbox("Time Period", ['1d', '5d', '1mo', '3mo', '6mo', '1y'])
            
            # Create and display chart
            chart = tracker.create_price_chart(selected_stock, period)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
        
        with col2:
            # Stock details
            stock_data = df[df['Ticker'] == selected_stock].iloc[0]
            
            st.markdown("**Company Details**")
            st.write(f"**Name:** {stock_data['Name']}")
            st.write(f"**Sector:** {stock_data['Sector']}")
            st.write(f"**Price:** ${stock_data['Price']:.2f}")
            st.write(f"**Change:** ${stock_data['Change']:.2f} ({stock_data['Change%']:.2f}%)")
            st.write(f"**Market Cap:** {tracker.format_market_cap(stock_data['Market Cap'])}")
            st.write(f"**P/E Ratio:** {stock_data['P/E Ratio']}")
            st.write(f"**Volume:** {stock_data['Volume']/1e6:.1f}M")
    
    # Top Performers
    st.subheader("🏆 Top Performers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Top Gainers**")
        top_gainers = df.nlargest(5, 'Change%')[['Ticker', 'Name', 'Change%']]
        for _, row in top_gainers.iterrows():
            st.write(f"• {row['Ticker']}: +{row['Change%']:.2f}%")
    
    with col2:
        st.write("**Top Losers**")
        top_losers = df.nsmallest(5, 'Change%')[['Ticker', 'Name', 'Change%']]
        for _, row in top_losers.iterrows():
            st.write(f"• {row['Ticker']}: {row['Change%']:.2f}%")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(30)
        st.experimental_rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Data provided by Yahoo Finance | Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

if __name__ == "__main__":
    main()