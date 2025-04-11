import pandas as pd
import yfinance as yf
import requests
import fredapi
import datetime
import plotly.graph_objects as go
from datetime import date, timedelta

# You'll need to sign up for these API keys
FRED_API_KEY = '29b5bb86f4e744bdeced6768b31d5cda'
ALPHA_VANTAGE_API_KEY = 'FO3DP9DZ3WIU2AOS'

class LiquidityTracker:
    def __init__(self):
        self.fred = fredapi.Fred(api_key=FRED_API_KEY)
        
    def get_fed_funds_rate(self):
        """Get Federal Funds Rate from FRED"""
        try:
            return self.fred.get_series('DFF')
        except Exception as e:
            print(f"Error fetching Fed Funds Rate: {e}")
            return None

    def get_treasury_yields(self):
        """Get Treasury Yield Curve data"""
        try:
            maturities = ['DGS1MO', 'DGS3MO', 'DGS6MO', 'DGS1', 'DGS2', 'DGS5', 'DGS10', 'DGS30']
            data = pd.DataFrame()
            
            for maturity in maturities:
                series = self.fred.get_series(maturity)
                data[maturity] = series
                
            return data
        except Exception as e:
            print(f"Error fetching Treasury Yields: {e}")
            return None

    def get_ted_spread(self):
        """Calculate TED Spread (LIBOR - T-Bill rate)"""
        try:
            ted = self.fred.get_series('TEDRATE')
            return ted
        except Exception as e:
            print(f"Error fetching TED Spread: {e}")
            return None

    def get_excess_reserves(self):
        """Get Excess Reserves of Depository Institutions"""
        try:
            reserves = self.fred.get_series('EXCSRESNS')
            return reserves
        except Exception as e:
            print(f"Error fetching Excess Reserves: {e}")
            return None

    def get_market_depth(self, symbol='SPY'):
        """Get market depth using yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            return ticker.info
        except Exception as e:
            print(f"Error fetching Market Depth: {e}")
            return None

    def plot_yield_curve(self, yields_data):
        """Plot the yield curve"""
        if yields_data is not None and not yields_data.empty:
            latest_date = yields_data.index[-1]
            latest_yields = yields_data.iloc[-1]
            
            maturities = [0.083, 0.25, 0.5, 1, 2, 5, 10, 30]  # in years
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=maturities, y=latest_yields,
                                   mode='lines+markers',
                                   name='Yield Curve'))
            
            fig.update_layout(title=f'Treasury Yield Curve ({latest_date.date()})',
                            xaxis_title='Maturity (years)',
                            yaxis_title='Yield (%)')
            fig.show()

def main():
    tracker = LiquidityTracker()
    
    # Get data
    fed_funds = tracker.get_fed_funds_rate()
    treasury_yields = tracker.get_treasury_yields()
    ted_spread = tracker.get_ted_spread()
    excess_reserves = tracker.get_excess_reserves()
    
    # Create daily report
    print("=== Daily Liquidity Report ===")
    print(f"Date: {date.today()}\n")
    
    if fed_funds is not None:
        print(f"Federal Funds Rate: {fed_funds.iloc[-1]:.2f}%")
    
    if ted_spread is not None:
        print(f"TED Spread: {ted_spread.iloc[-1]:.2f} basis points")
    
    if excess_reserves is not None:
        print(f"Excess Reserves: ${excess_reserves.iloc[-1]/1000:.2f} billion")
    
    # Plot yield curve
    tracker.plot_yield_curve(treasury_yields)
    
    # Save data to CSV
    if all(v is not None for v in [fed_funds, treasury_yields, ted_spread, excess_reserves]):
        daily_data = pd.DataFrame({
            'Fed_Funds_Rate': fed_funds.iloc[-1],
            'TED_Spread': ted_spread.iloc[-1],
            'Excess_Reserves': excess_reserves.iloc[-1]
        }, index=[date.today()])
        
        daily_data.to_csv(f'liquidity_data_{date.today()}.csv')

if __name__ == "__main__":
    main()