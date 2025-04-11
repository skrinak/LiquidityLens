import streamlit as st
import pandas as pd
import mplfinance as mpf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path

class LiquidityDashboard:
    def __init__(self):
        self.data = None
        self.yield_curve_data = None
        
    def load_data(self):
        """Load the most recent CSV file from the directory"""
        try:
            # Get the most recent CSV file
            files = list(Path('.').glob('liquidity_data_*.csv'))
            latest_file = max(files, key=lambda x: x.stat().st_mtime)
            self.data = pd.read_csv(latest_file, index_col=0, parse_dates=True)
            return True
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return False

    def plot_fed_funds_rate(self):
        """Plot Federal Funds Rate"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=self.data['Fed_Funds_Rate'],
            mode='lines',
            name='Fed Funds Rate'
        ))
        fig.update_layout(
            title='Federal Funds Rate',
            xaxis_title='Date',
            yaxis_title='Rate (%)'
        )
        return fig

    def plot_ted_spread(self):
        """Plot TED Spread"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=self.data['TED_Spread'],
            mode='lines',
            name='TED Spread'
        ))
        fig.update_layout(
            title='TED Spread',
            xaxis_title='Date',
            yaxis_title='Basis Points'
        )
        return fig

    def plot_excess_reserves(self):
        """Plot Excess Reserves"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=self.data['Excess_Reserves'] / 1e9,  # Convert to billions
            mode='lines',
            name='Excess Reserves'
        ))
        fig.update_layout(
            title='Excess Reserves',
            xaxis_title='Date',
            yaxis_title='Billions USD'
        )
        return fig

def main():
    st.set_page_config(
        page_title="Liquidity Dashboard",
        page_icon="📊",
        layout="wide"
    )

    st.title("Market Liquidity Dashboard")
    st.markdown("---")

    dashboard = LiquidityDashboard()

    if dashboard.load_data():
        # Create three columns for the metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Current Fed Funds Rate",
                f"{dashboard.data['Fed_Funds_Rate'].iloc[-1]:.2f}%",
                f"{dashboard.data['Fed_Funds_Rate'].iloc[-1] - dashboard.data['Fed_Funds_Rate'].iloc[-2]:.2f}%"
            )

        with col2:
            st.metric(
                "TED Spread",
                f"{dashboard.data['TED_Spread'].iloc[-1]:.2f} bps",
                f"{dashboard.data['TED_Spread'].iloc[-1] - dashboard.data['TED_Spread'].iloc[-2]:.2f}"
            )

        with col3:
            excess_reserves_b = dashboard.data['Excess_Reserves'].iloc[-1] / 1e9
            excess_reserves_change = (dashboard.data['Excess_Reserves'].iloc[-1] - 
                                    dashboard.data['Excess_Reserves'].iloc[-2]) / 1e9
            st.metric(
                "Excess Reserves (Billions)",
                f"${excess_reserves_b:.2f}B",
                f"${excess_reserves_change:.2f}B"
            )

        # Create tabs for different charts
        tab1, tab2, tab3 = st.tabs(["Fed Funds Rate", "TED Spread", "Excess Reserves"])

        with tab1:
            st.plotly_chart(dashboard.plot_fed_funds_rate(), use_container_width=True)

        with tab2:
            st.plotly_chart(dashboard.plot_ted_spread(), use_container_width=True)

        with tab3:
            st.plotly_chart(dashboard.plot_excess_reserves(), use_container_width=True)

        # Add a data table with recent values
        st.markdown("### Recent Data")
        st.dataframe(dashboard.data.tail(10))

        # Add download button for the data
        st.download_button(
            label="Download Data as CSV",
            data=dashboard.data.to_csv(),
            file_name="liquidity_data.csv",
            mime="text/csv"
        )

    else:
        st.error("Unable to load data. Please ensure the data file exists.")

    # Add footer
    st.markdown("---")
    st.markdown("Data updated daily | Source: Federal Reserve Economic Data (FRED)")

if __name__ == "__main__":
    main()
