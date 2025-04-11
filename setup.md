This script:
* Fetches Federal Funds Rate
* Gets Treasury Yield Curve data
* Calculates TED Spread
* Tracks Excess Reserves
* Creates basic market depth information
* Generates a daily report
* Plots the yield curve
* Saves data to CSV

```
pip install pandas yfinance fredapi requests plotly
```
or
```
conda install pandas
conda install yfinance -y
conda install conda-forge::yfinance -y
conda install conda-forge::fredapi -y
conda install anaconda::requests -y
conda install conda-forge::plotly -y
```

Sign up for API keys:
FRED API: https://fred.stlouisfed.org/docs/api/api_key.html
Alpha Vantage (optional): https://www.alphavantage.co/
Replace the API keys in the script with your own.

FRED
Your registered API key is: 29b5bb86f4e744bdeced6768b31d5cda Documentation is available on the St. Louis Fed web services website.

Alpha Vantage
Here is your API key: FO3DP9DZ3WIU2AOS. Please record this API key at a safe place for future data access.

## liquidity_dashboard
pip install streamlit pandas mplfinance plotly
```
conda install conda-forge::streamlit -y
conda install conda-forge::mplfinance -y
```

streamlit run liquidity_dashboard.py

origin git@github.com:skrinak/LiquidityLens.git