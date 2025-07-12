import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import json
import time
from typing import Dict, List, Optional
import uuid
import warnings
warnings.filterwarnings('ignore')

# Configure Streamlit page
st.set_page_config(
    page_title="Stock Trading Simulator - Debugged",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for gaming aesthetics
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem 0;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .portfolio-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 25px rgba(255,107,107,0.3);
        border: 2px solid rgba(255,255,255,0.2);
    }
    
    .profit-card {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 25px rgba(40,167,69,0.3);
    }
    
    .loss-card {
        background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 25px rgba(220,53,69,0.3);
    }
    
    .trade-success {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .trade-error {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    
    .positive { color: #28a745; font-weight: bold; }
    .negative { color: #dc3545; font-weight: bold; }
    .neutral { color: #6c757d; }
    
    .achievement-badge {
        background: #17a2b8;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.8em;
        margin: 2px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

class TradingSimulator:
    def __init__(self):
        self.initialize_session_state()
        self.available_stocks = self.get_available_stocks()
        
    def initialize_session_state(self):
        """Initialize session state for the trading game"""
        if 'players' not in st.session_state:
            st.session_state.players = {}
        
        if 'current_player' not in st.session_state:
            st.session_state.current_player = None
            
        if 'game_settings' not in st.session_state:
            st.session_state.game_settings = {
                'starting_cash': 100000,
                'commission': 9.99,
                'game_duration_days': 30,
                'created_date': datetime.now()
            }
            
        if 'market_data_cache' not in st.session_state:
            st.session_state.market_data_cache = {}
            
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
    
    def get_available_stocks(self) -> List[str]:
        """Get list of available stocks for trading"""
        return [
            # Large Cap Tech
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META', 'NFLX', 'ADBE',
            'CRM', 'ORCL', 'IBM', 'INTC', 'AMD', 'QCOM', 'AVGO', 'TXN', 'AMAT', 'LRCX',
            'NOW', 'INTU', 'PANW', 'CRWD', 'ZS', 'SNOW', 'PLTR', 'DDOG', 'OKTA', 'ZM',
            
            # Finance
            'BRK-B', 'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC', 'TFC',
            'COF', 'AXP', 'BLK', 'SCHW', 'SPGI', 'ICE', 'CME', 'CB', 'AIG', 'PGR',
            'V', 'MA', 'PYPL', 'SQ', 'FIS', 'FISV', 'COIN',
            
            # Healthcare & Biotech
            'UNH', 'JNJ', 'PFE', 'ABBV', 'TMO', 'ABT', 'DHR', 'BMY', 'AMGN', 'GILD',
            'BIIB', 'REGN', 'VRTX', 'ILMN', 'ISRG', 'DXCM', 'ZTS', 'MRNA', 'BNTX', 'CVS',
            
            # Consumer & Retail
            'HD', 'WMT', 'PG', 'KO', 'PEP', 'COST', 'NKE', 'SBUX', 'MCD', 'DIS',
            'LOW', 'TJX', 'TGT', 'LULU', 'CMG', 'YUM', 'ULTA', 'ROST', 'BBY',
            
            # Energy
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'MPC', 'VLO', 'PSX', 'OXY', 'KMI',
            
            # Industrial
            'BA', 'HON', 'UPS', 'RTX', 'CAT', 'DE', 'MMM', 'LMT', 'GD', 'NOC',
            'FDX', 'CSX', 'NSC', 'UNP', 'ITW', 'EMR', 'ETN', 'PH', 'CMI',
            
            # Utilities & REITs
            'NEE', 'SO', 'DUK', 'AEP', 'SRE', 'D', 'EXC', 'XEL', 'PEG',
            'AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'WELL', 'DLR', 'SPG', 'O',
            
            # Communication Services
            'VZ', 'T', 'TMUS', 'CHTR', 'CMCSA', 'TWTR', 'SNAP', 'PINS', 'ROKU',
            
            # ETFs
            'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'VEA', 'VWO', 'BND', 'AGG',
            'XLE', 'XLF', 'XLK', 'XLV', 'XLI', 'XLU', 'XLP', 'XLY', 'XLB',
        ]
    
    @st.cache_data(ttl=300)
    def get_stock_price(_self, symbol: str) -> Dict:
        """Get current stock price and info with error handling"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="5d")
            
            if hist.empty:
                return None
                
            info = stock.info
            
            current_price = hist['Close'].iloc[-1]
            prev_close = info.get('previousClose', current_price)
            if prev_close == 0:
                prev_close = current_price
                
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close > 0 else 0
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol)[:50],  # Limit name length
                'price': float(current_price),
                'change': float(change),
                'change_percent': float(change_percent),
                'volume': int(hist['Volume'].iloc[-1]) if len(hist) > 0 and not pd.isna(hist['Volume'].iloc[-1]) else 0,
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'day_high': float(hist['High'].iloc[-1]) if len(hist) > 0 else current_price,
                'day_low': float(hist['Low'].iloc[-1]) if len(hist) > 0 else current_price,
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'last_updated': datetime.now()
            }
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    @st.cache_data(ttl=600)
    def get_comprehensive_stock_data(_self, symbols: List[str]) -> pd.DataFrame:
        """Get comprehensive stock data for research with error handling"""
        data = []
        progress_bar = st.progress(0)
        
        for i, symbol in enumerate(symbols):
            try:
                stock_data = _self.get_stock_price(symbol)
                if stock_data:
                    data.append({
                        'Ticker': symbol,
                        'Name': stock_data['name'],
                        'Sector': stock_data['sector'],
                        'Industry': stock_data['industry'],
                        'Price': stock_data['price'],
                        'Change': stock_data['change'],
                        'Change%': stock_data['change_percent'],
                        'Volume': stock_data['volume'],
                        'Market Cap': stock_data['market_cap'],
                        'P/E Ratio': stock_data['pe_ratio'],
                        'Day High': stock_data['day_high'],
                        'Day Low': stock_data['day_low'],
                    })
                progress_bar.progress((i + 1) / len(symbols))
            except Exception as e:
                continue
        
        progress_bar.empty()
        return pd.DataFrame(data)
    
    def create_player(self, name: str, email: str = "") -> str:
        """Create a new player"""
        player_id = str(uuid.uuid4())[:8]
        
        st.session_state.players[player_id] = {
            'name': name,
            'email': email,
            'cash': st.session_state.game_settings['starting_cash'],
            'portfolio': {},
            'trade_history': [],
            'created_date': datetime.now(),
            'total_trades': 0,
            'total_profit_loss': 0,
            'best_trade': 0,
            'worst_trade': 0,
            'achievements': [],
            'portfolio_value_history': []
        }
        
        return player_id
    
    def buy_stock(self, player_id: str, symbol: str, shares: int) -> Dict:
        """Execute a buy order with proper error handling"""
        try:
            if player_id not in st.session_state.players:
                return {'success': False, 'message': 'Player not found'}
            
            if shares <= 0:
                return {'success': False, 'message': 'Invalid number of shares'}
            
            stock_data = self.get_stock_price(symbol)
            if not stock_data:
                return {'success': False, 'message': 'Unable to get stock price'}
            
            player = st.session_state.players[player_id]
            total_cost = (stock_data['price'] * shares) + st.session_state.game_settings['commission']
            
            if player['cash'] < total_cost:
                return {'success': False, 'message': f'Insufficient funds. Need ${total_cost:.2f}, have ${player["cash"]:.2f}'}
            
            # Execute trade
            player['cash'] -= total_cost
            
            if symbol in player['portfolio']:
                # Update existing position
                existing_shares = player['portfolio'][symbol]['shares']
                existing_avg_price = player['portfolio'][symbol]['avg_price']
                new_avg_price = ((existing_shares * existing_avg_price) + (shares * stock_data['price'])) / (existing_shares + shares)
                
                player['portfolio'][symbol]['shares'] += shares
                player['portfolio'][symbol]['avg_price'] = new_avg_price
            else:
                # New position
                player['portfolio'][symbol] = {
                    'shares': shares,
                    'avg_price': stock_data['price'],
                    'name': stock_data['name']
                }
            
            # Record trade
            trade = {
                'id': str(uuid.uuid4())[:8],
                'type': 'BUY',
                'symbol': symbol,
                'shares': shares,
                'price': stock_data['price'],
                'commission': st.session_state.game_settings['commission'],
                'total_cost': total_cost,
                'timestamp': datetime.now(),
                'name': stock_data['name']
            }
            
            player['trade_history'].append(trade)
            player['total_trades'] += 1
            
            # Update session state
            st.session_state.players[player_id] = player
            
            return {
                'success': True, 
                'message': f'Successfully bought {shares} shares of {symbol} at ${stock_data["price"]:.2f}',
                'trade': trade
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error executing buy order: {str(e)}'}
    
    def sell_stock(self, player_id: str, symbol: str, shares: int) -> Dict:
        """Execute a sell order with proper error handling"""
        try:
            if player_id not in st.session_state.players:
                return {'success': False, 'message': 'Player not found'}
            
            if shares <= 0:
                return {'success': False, 'message': 'Invalid number of shares'}
            
            player = st.session_state.players[player_id]
            
            if symbol not in player['portfolio']:
                return {'success': False, 'message': 'You do not own this stock'}
            
            if player['portfolio'][symbol]['shares'] < shares:
                return {'success': False, 'message': f'Insufficient shares. You own {player["portfolio"][symbol]["shares"]}, trying to sell {shares}'}
            
            stock_data = self.get_stock_price(symbol)
            if not stock_data:
                return {'success': False, 'message': 'Unable to get stock price'}
            
            # Execute trade
            total_proceeds = (stock_data['price'] * shares) - st.session_state.game_settings['commission']
            player['cash'] += total_proceeds
            
            # Calculate profit/loss
            avg_price = player['portfolio'][symbol]['avg_price']
            profit_loss = (stock_data['price'] - avg_price) * shares - st.session_state.game_settings['commission']
            
            # Update portfolio
            player['portfolio'][symbol]['shares'] -= shares
            if player['portfolio'][symbol]['shares'] == 0:
                del player['portfolio'][symbol]
            
            # Record trade
            trade = {
                'id': str(uuid.uuid4())[:8],
                'type': 'SELL',
                'symbol': symbol,
                'shares': shares,
                'price': stock_data['price'],
                'commission': st.session_state.game_settings['commission'],
                'total_proceeds': total_proceeds,
                'profit_loss': profit_loss,
                'timestamp': datetime.now(),
                'name': stock_data['name']
            }
            
            player['trade_history'].append(trade)
            player['total_trades'] += 1
            player['total_profit_loss'] += profit_loss
            
            # Update best/worst trades
            if profit_loss > player['best_trade']:
                player['best_trade'] = profit_loss
            if profit_loss < player['worst_trade']:
                player['worst_trade'] = profit_loss
            
            # Update session state
            st.session_state.players[player_id] = player
            
            return {
                'success': True, 
                'message': f'Successfully sold {shares} shares of {symbol} at ${stock_data["price"]:.2f}',
                'trade': trade,
                'profit_loss': profit_loss
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error executing sell order: {str(e)}'}
    
    def get_portfolio_value(self, player_id: str) -> float:
        """Calculate total portfolio value with error handling"""
        try:
            if player_id not in st.session_state.players:
                return 0
            
            player = st.session_state.players[player_id]
            total_value = player['cash']
            
            for symbol, position in player['portfolio'].items():
                stock_data = self.get_stock_price(symbol)
                if stock_data:
                    total_value += stock_data['price'] * position['shares']
            
            return total_value
        except Exception as e:
            st.error(f"Error calculating portfolio value: {str(e)}")
            return 0
    
    def get_leaderboard(self) -> pd.DataFrame:
        """Get leaderboard of all players"""
        try:
            leaderboard_data = []
            
            for player_id, player in st.session_state.players.items():
                portfolio_value = self.get_portfolio_value(player_id)
                total_return = portfolio_value - st.session_state.game_settings['starting_cash']
                return_percentage = (total_return / st.session_state.game_settings['starting_cash']) * 100
                
                leaderboard_data.append({
                    'Rank': 0,
                    'Player': player['name'],
                    'Portfolio Value': portfolio_value,
                    'Total Return': total_return,
                    'Return %': return_percentage,
                    'Total Trades': player['total_trades'],
                    'Player ID': player_id
                })
            
            df = pd.DataFrame(leaderboard_data)
            if not df.empty:
                df = df.sort_values('Portfolio Value', ascending=False).reset_index(drop=True)
                df['Rank'] = range(1, len(df) + 1)
            
            return df
        except Exception as e:
            st.error(f"Error creating leaderboard: {str(e)}")
            return pd.DataFrame()
    
    def format_large_number(self, value):
        """Format large numbers for display"""
        try:
            if pd.isna(value) or value == 0:
                return 'N/A'
            
            if abs(value) >= 1e12:
                return f"${value/1e12:.2f}T"
            elif abs(value) >= 1e9:
                return f"${value/1e9:.2f}B"
            elif abs(value) >= 1e6:
                return f"${value/1e6:.2f}M"
            elif abs(value) >= 1e3:
                return f"${value/1e3:.2f}K"
            else:
                return f"${value:.2f}"
        except:
            return 'N/A'
    
    def create_portfolio_chart(self, player_id: str):
        """Create portfolio allocation pie chart with error handling"""
        try:
            if player_id not in st.session_state.players:
                return None
            
            player = st.session_state.players[player_id]
            
            if not player['portfolio']:
                return None
            
            portfolio_data = []
            for symbol, position in player['portfolio'].items():
                stock_data = self.get_stock_price(symbol)
                if stock_data:
                    value = stock_data['price'] * position['shares']
                    portfolio_data.append({
                        'Symbol': symbol,
                        'Value': value,
                        'Shares': position['shares']
                    })
            
            if not portfolio_data:
                return None
            
            df = pd.DataFrame(portfolio_data)
            
            fig = px.pie(
                df, 
                values='Value', 
                names='Symbol',
                title='Portfolio Allocation'
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            return fig
            
        except Exception as e:
            st.error(f"Error creating portfolio chart: {str(e)}")
            return None
    
    def create_performance_chart(self, player_id: str):
        """Create portfolio performance chart with error handling"""
        try:
            if player_id not in st.session_state.players:
                return None
            
            player = st.session_state.players[player_id]
            
            if not player['trade_history']:
                return None
            
            # Calculate portfolio value over time
            dates = []
            portfolio_values = []
            
            running_cash = st.session_state.game_settings['starting_cash']
            holdings = {}
            
            for trade in player['trade_history']:
                dates.append(trade['timestamp'])
                
                if trade['type'] == 'BUY':
                    running_cash -= trade['total_cost']
                    if trade['symbol'] in holdings:
                        holdings[trade['symbol']]['shares'] += trade['shares']
                    else:
                        holdings[trade['symbol']] = {'shares': trade['shares']}
                else:  # SELL
                    running_cash += trade['total_proceeds']
                    if trade['symbol'] in holdings:
                        holdings[trade['symbol']]['shares'] -= trade['shares']
                        if holdings[trade['symbol']]['shares'] <= 0:
                            del holdings[trade['symbol']]
                
                # Calculate current portfolio value
                portfolio_value = running_cash
                for symbol, position in holdings.items():
                    stock_data = self.get_stock_price(symbol)
                    if stock_data:
                        portfolio_value += stock_data['price'] * position['shares']
                
                portfolio_values.append(portfolio_value)
            
            if len(dates) < 1:
                return None
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=portfolio_values,
                mode='lines+markers',
                name='Portfolio Value',
                line=dict(color='#28a745', width=3)
            ))
            
            # Starting value line
            fig.add_hline(
                y=st.session_state.game_settings['starting_cash'],
                line_dash="dash",
                line_color="gray",
                annotation_text="Starting Value"
            )
            
            fig.update_layout(
                title='Portfolio Performance Over Time',
                xaxis_title='Date',
                yaxis_title='Value ($)',
                template='plotly_white',
                height=400
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating performance chart: {str(e)}")
            return None
    
    def create_stock_price_chart(self, symbol: str, period: str = "3mo"):
        """Create stock price chart with error handling"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            
            if hist.empty:
                return None
            
            fig = go.Figure()
            
            # Candlestick chart
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name='Price'
            ))
            
            # Moving averages
            if len(hist) >= 20:
                hist['MA20'] = hist['Close'].rolling(window=20).mean()
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=hist['MA20'],
                    mode='lines',
                    name='MA20',
                    line=dict(color='orange', width=2)
                ))
            
            if len(hist) >= 50:
                hist['MA50'] = hist['Close'].rolling(window=50).mean()
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=hist['MA50'],
                    mode='lines',
                    name='MA50',
                    line=dict(color='blue', width=2)
                ))
            
            fig.update_layout(
                title=f"{symbol} - Stock Analysis",
                yaxis_title="Price ($)",
                xaxis_title="Date",
                template="plotly_white",
                height=500
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating stock chart for {symbol}: {str(e)}")
            return None

def main():
    simulator = TradingSimulator()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>💰 Stock Trading Simulator - Debugged</h1>
        <p>🎮 Learn trading with virtual money • 📈 Build your portfolio • 🏆 Compete with friends</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Error handling wrapper
    try:
        # Sidebar - Player Management
        with st.sidebar:
            st.header("🎮 Player Management")
            
            # Create or select player
            if not st.session_state.players:
                st.write("**Create your first player to start trading!**")
                with st.form("create_player"):
                    player_name = st.text_input("Player Name", placeholder="Enter your name")
                    player_email = st.text_input("Email (optional)", placeholder="your@email.com")
                    
                    if st.form_submit_button("🚀 Start Trading!"):
                        if player_name:
                            player_id = simulator.create_player(player_name, player_email)
                            st.session_state.current_player = player_id
                            st.success(f"Welcome {player_name}!")
                            st.rerun()
                        else:
                            st.error("Please enter a player name")
            
            else:
                # Player selection
                player_options = {pid: player['name'] for pid, player in st.session_state.players.items()}
                
                if st.session_state.current_player not in player_options:
                    st.session_state.current_player = list(player_options.keys())[0]
                
                selected_player = st.selectbox(
                    "Select Player",
                    options=list(player_options.keys()),
                    format_func=lambda x: player_options[x],
                    index=list(player_options.keys()).index(st.session_state.current_player) if st.session_state.current_player in player_options else 0
                )
                
                st.session_state.current_player = selected_player
                
                # Add new player option
                with st.expander("➕ Add New Player"):
                    with st.form("add_player"):
                        new_player_name = st.text_input("New Player Name")
                        new_player_email = st.text_input("Email (optional)")
                        
                        if st.form_submit_button("Add Player"):
                            if new_player_name:
                                new_player_id = simulator.create_player(new_player_name, new_player_email)
                                st.session_state.current_player = new_player_id
                                st.success(f"Added {new_player_name}!")
                                st.rerun()
            
            # Game settings
            with st.expander("⚙️ Game Settings"):
                st.write(f"**Starting Cash:** ${st.session_state.game_settings['starting_cash']:,.2f}")
                st.write(f"**Commission:** ${st.session_state.game_settings['commission']:.2f}")
                
                if st.button("Reset All Data"):
                    st.session_state.players = {}
                    st.session_state.current_player = None
                    st.success("All data reset!")
                    st.rerun()
        
        # Main content
        if st.session_state.current_player and st.session_state.current_player in st.session_state.players:
            current_player = st.session_state.players[st.session_state.current_player]
            
            # Player dashboard
            st.subheader(f"👨‍💼 {current_player['name']}'s Dashboard")
            
            # Portfolio overview
            portfolio_value = simulator.get_portfolio_value(st.session_state.current_player)
            total_return = portfolio_value - st.session_state.game_settings['starting_cash']
            return_percentage = (total_return / st.session_state.game_settings['starting_cash']) * 100
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                card_class = "profit-card" if total_return >= 0 else "loss-card"
                st.markdown(f"""
                <div class="{card_class}">
                    <h3>💰 Portfolio Value</h3>
                    <h2>${portfolio_value:,.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="portfolio-card">
                    <h3>💵 Cash Available</h3>
                    <h2>${current_player['cash']:,.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                card_class = "profit-card" if total_return >= 0 else "loss-card"
                st.markdown(f"""
                <div class="{card_class}">
                    <h3>📈 Total Return</h3>
                    <h2>${total_return:,.2f}</h2>
                    <p>({return_percentage:+.2f}%)</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="portfolio-card">
                    <h3>🔄 Total Trades</h3>
                    <h2>{current_player['total_trades']}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Main tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Research", "💰 Trade", "📈 Portfolio", "📋 History", "🏆 Leaderboard"])
            
            with tab1:
                st.subheader("📊 Stock Research & Analysis")
                
                # Load comprehensive data
                if st.button("🔄 Load Research Data") or 'research_data' not in st.session_state:
                    with st.spinner("Loading stock data..."):
                        research_stocks = simulator.available_stocks[:30]  # Limit for performance
                        st.session_state.research_data = simulator.get_comprehensive_stock_data(research_stocks)
                
                if 'research_data' in st.session_state and not st.session_state.research_data.empty:
                    df = st.session_state.research_data.copy()
                    
                    # Filters
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        search_term = st.text_input("🔍 Search Stocks", placeholder="Enter symbol or name")
                    
                    with col2:
                        sectors = ['All'] + sorted(df['Sector'].unique().tolist())
                        selected_sector = st.selectbox("📈 Filter by Sector", sectors)
                    
                    with col3:
                        sort_options = ['Change%', 'Market Cap', 'Price', 'Volume']
                        sort_by = st.selectbox("📊 Sort by", sort_options)
                    
                    # Apply filters
                    if search_term:
                        df = df[
                            df['Ticker'].str.contains(search_term.upper(), na=False) |
                            df['Name'].str.contains(search_term, case=False, na=False)
                        ]
                    
                    if selected_sector != 'All':
                        df = df[df['Sector'] == selected_sector]
                    
                    # Sort data
                    if sort_by == 'Change%':
                        df = df.sort_values('Change%', ascending=False)
                    elif sort_by == 'Market Cap':
                        df = df.sort_values('Market Cap', ascending=False)
                    elif sort_by == 'Price':
                        df = df.sort_values('Price', ascending=False)
                    elif sort_by == 'Volume':
                        df = df.sort_values('Volume', ascending=False)
                    
                    # Display results
                    st.write(f"**Found {len(df)} stocks**")
                    
                    if len(df) > 0:
                        # Format display
                        display_df = df.copy()
                        display_df['Price'] = display_df['Price'].apply(lambda x: f"${x:.2f}")
                        display_df['Change%'] = display_df['Change%'].apply(lambda x: f"{x:+.2f}%")
                        display_df['Volume'] = display_df['Volume'].apply(lambda x: f"{x/1e6:.1f}M" if x > 0 else 'N/A')
                        display_df['Market Cap'] = display_df['Market Cap'].apply(simulator.format_large_number)
                        
                        display_columns = ['Ticker', 'Name', 'Sector', 'Price', 'Change%', 'Volume', 'Market Cap']
                        st.dataframe(display_df[display_columns], use_container_width=True, height=400)
            
            with tab2:
                st.subheader("🛒 Buy & Sell Stocks")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("### 📈 Buy Stocks")
                    
                    selected_stock = st.selectbox(
                        "Select Stock",
                        [''] + simulator.available_stocks[:20],  # Limit for performance
                        key="buy_stock"
                    )
                    
                    if selected_stock:
                        stock_data = simulator.get_stock_price(selected_stock)
                        if stock_data:
                            st.write(f"**{stock_data['name']}**")
                            st.write(f"**Current Price:** ${stock_data['price']:.2f}")
                            
                            change_class = "positive" if stock_data['change'] >= 0 else "negative"
                            st.markdown(f"**Change:** <span class='{change_class}'>${stock_data['change']:+.2f} ({stock_data['change_percent']:+.2f}%)</span>", unsafe_allow_html=True)
                            
                            buy_shares = st.number_input("Number of Shares", min_value=1, value=1, key="buy_shares")
                            total_cost = (stock_data['price'] * buy_shares) + st.session_state.game_settings['commission']
                            
                            st.write(f"**Total Cost:** ${total_cost:.2f}")
                            
                            if st.button("🛒 Buy Stock", key="buy_button"):
                                result = simulator.buy_stock(st.session_state.current_player, selected_stock, buy_shares)
                                if result['success']:
                                    st.success(result['message'])
                                    st.rerun()
                                else:
                                    st.error(result['message'])
                
                with col2:
                    st.write("### 📉 Sell Stocks")
                    
                    if current_player['portfolio']:
                        owned_stocks = list(current_player['portfolio'].keys())
                        selected_sell_stock = st.selectbox(
                            "Select Stock to Sell",
                            [''] + owned_stocks,
                            key="sell_stock"
                        )
                        
                        if selected_sell_stock:
                            position = current_player['portfolio'][selected_sell_stock]
                            stock_data = simulator.get_stock_price(selected_sell_stock)
                            
                            if stock_data:
                                st.write(f"**{stock_data['name']}**")
                                st.write(f"**Shares Owned:** {position['shares']}")
                                st.write(f"**Average Price:** ${position['avg_price']:.2f}")
                                st.write(f"**Current Price:** ${stock_data['price']:.2f}")
                                
                                sell_shares = st.number_input(
                                    "Shares to Sell", 
                                    min_value=1, 
                                    max_value=position['shares'], 
                                    value=1,
                                    key="sell_shares"
                                )
                                
                                total_proceeds = (stock_data['price'] * sell_shares) - st.session_state.game_settings['commission']
                                st.write(f"**Total Proceeds:** ${total_proceeds:.2f}")
                                
                                if st.button("💰 Sell Stock", key="sell_button"):
                                    result = simulator.sell_stock(st.session_state.current_player, selected_sell_stock, sell_shares)
                                    if result['success']:
                                        st.success(result['message'])
                                        st.rerun()
                                    else:
                                        st.error(result['message'])
                    else:
                        st.info("You don't own any stocks yet!")
            
            with tab3:
                st.subheader("📊 Your Portfolio")
                
                if current_player['portfolio']:
                    # Portfolio charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        portfolio_chart = simulator.create_portfolio_chart(st.session_state.current_player)
                        if portfolio_chart:
                            st.plotly_chart(portfolio_chart, use_container_width=True)
                    
                    with col2:
                        performance_chart = simulator.create_performance_chart(st.session_state.current_player)
                        if performance_chart:
                            st.plotly_chart(performance_chart, use_container_width=True)
                    
                    # Portfolio table
                    portfolio_data = []
                    
                    for symbol, position in current_player['portfolio'].items():
                        stock_data = simulator.get_stock_price(symbol)
                        if stock_data:
                            current_value = stock_data['price'] * position['shares']
                            cost_basis = position['avg_price'] * position['shares']
                            unrealized_pl = current_value - cost_basis
                            
                            portfolio_data.append({
                                'Symbol': symbol,
                                'Name': stock_data['name'][:30],
                                'Shares': position['shares'],
                                'Avg Price': f"${position['avg_price']:.2f}",
                                'Current Price': f"${stock_data['price']:.2f}",
                                'Current Value': f"${current_value:.2f}",
                                'Unrealized P&L': f"${unrealized_pl:+.2f}"
                            })
                    
                    if portfolio_data:
                        df = pd.DataFrame(portfolio_data)
                        st.dataframe(df, use_container_width=True)
                else:
                    st.info("Your portfolio is empty. Start trading!")
            
            with tab4:
                st.subheader("📋 Trade History")
                
                if current_player['trade_history']:
                    trade_data = []
                    
                    for trade in reversed(current_player['trade_history']):
                        trade_data.append({
                            'Date': trade['timestamp'].strftime('%Y-%m-%d %H:%M'),
                            'Type': trade['type'],
                            'Symbol': trade['symbol'],
                            'Shares': trade['shares'],
                            'Price': f"${trade['price']:.2f}",
                            'Total': f"${trade.get('total_cost', trade.get('total_proceeds', 0)):.2f}",
                            'P&L': f"${trade.get('profit_loss', 0):+.2f}" if 'profit_loss' in trade else 'N/A'
                        })
                    
                    df = pd.DataFrame(trade_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Trades", current_player['total_trades'])
                    with col2:
                        st.metric("Best Trade", f"${current_player['best_trade']:+.2f}")
                    with col3:
                        st.metric("Worst Trade", f"${current_player['worst_trade']:+.2f}")
                else:
                    st.info("No trades yet!")
            
            with tab5:
                st.subheader("🏆 Leaderboard")
                
                leaderboard_df = simulator.get_leaderboard()
                
                if not leaderboard_df.empty:
                    display_df = leaderboard_df.drop(['Player ID'], axis=1).copy()
                    display_df['Portfolio Value'] = display_df['Portfolio Value'].apply(lambda x: f"${x:,.2f}")
                    display_df['Total Return'] = display_df['Total Return'].apply(lambda x: f"${x:+,.2f}")
                    display_df['Return %'] = display_df['Return %'].apply(lambda x: f"{x:+.2f}%")
                    
                    st.dataframe(display_df, use_container_width=True)
                else:
                    st.info("No players yet!")
        
        else:
            # Welcome screen
            st.markdown("""
            ## 🎮 Welcome to the Stock Trading Simulator!
            
            **Learn to trade stocks with virtual money:**
            
            ### 🌟 Features:
            - 💰 Start with $100,000 virtual cash
            - 📈 Trade real stocks with live prices
            - 🏆 Compete with friends on the leaderboard
            - 📊 Advanced charts and analysis
            - 📋 Track your portfolio performance
            
            ### 🚀 How to Start:
            1. Create a player account in the sidebar
            2. Research stocks in the Research tab
            3. Buy stocks you're interested in
            4. Watch your portfolio grow (or shrink!)
            5. Compete with friends on the leaderboard
            
            **Ready to start? Create a player in the sidebar!**
            """)
    
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.write("Please refresh the page and try again.")
        
        # Debug information
        with st.expander("Debug Information"):
            st.write("**Error Details:**")
            st.code(str(e))
            st.write("**Session State:**")
            st.json(dict(st.session_state))
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🎮 Stock Trading Simulator - Debugged Version | 📈 Educational Tool | ⚠️ Virtual Money Only</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()