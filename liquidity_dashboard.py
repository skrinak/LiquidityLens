import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import numpy as np
from typing import List, Optional

class LiquidityDashboard:
    def __init__(self):
        self.data = None
        self.ma_windows = [5, 10, 20, 50]  # Default MA periods
        
    def load_data(self):
        """Load the most recent CSV file from the directory"""
        try:
            # Get the most recent CSV file
            files = list(Path('.').glob('liquidity_data_*.csv'))
            if not files:
                st.error("No data files found")
                return False
                
            latest_file = max(files, key=lambda x: x.stat().st_mtime)
            self.data = pd.read_csv(latest_file, index_col=0, parse_dates=True)
            
            # Convert Excess_Reserves to numeric, removing any commas
            self.data['Excess_Reserves'] = pd.to_numeric(self.data['Excess_Reserves'].astype(str).str.replace(',', ''), errors='coerce')
            
            # Verify we have data
            if self.data.empty:
                st.error("Data file is empty")
                return False
                
            # Debug information
            st.sidebar.write("Data Types:", self.data.dtypes)
            st.sidebar.write("Excess Reserves Range:", 
                           f"Min: {self.data['Excess_Reserves'].min():,.2f}",
                           f"Max: {self.data['Excess_Reserves'].max():,.2f}")
                
            return True
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return False

    def calculate_metric_change(self, column):
        """Safely calculate change in metric"""
        if len(self.data[column]) < 2:
            return 0.0
        return float(self.data[column].iloc[-1]) - float(self.data[column].iloc[-2])

    def calculate_moving_averages(self, column: str, windows: Optional[List[int]] = None) -> pd.DataFrame:
        """Calculate moving averages for a specific column"""
        if windows is None:
            windows = self.ma_windows
            
        if self.data is None or self.data.empty:
            return pd.DataFrame()
            
        ma_data = pd.DataFrame(index=self.data.index)
        
        if column == 'Excess_Reserves_Billions':
            ma_data[column] = self.data['Excess_Reserves'] / 1e9
        else:
            ma_data[column] = self.data[column]
        
        for window in windows:
            ma_data[f'MA_{window}'] = ma_data[column].rolling(window=window).mean()
            
        return ma_data

    def plot_with_moving_averages(self, column: str, title: str, y_label: str, 
                                windows: Optional[List[int]] = None) -> go.Figure:
        """Create a plot with moving averages"""
        if self.data is None or self.data.empty:
            return None
            
        ma_data = self.calculate_moving_averages(column, windows)
        
        fig = go.Figure()
        
        # Plot main data
        fig.add_trace(go.Scatter(
            x=ma_data.index,
            y=ma_data[column],
            mode='lines',
            name=column,
            line=dict(color='blue')
        ))
        
        # Plot moving averages
        colors = ['red', 'green', 'orange', 'purple', 'brown']
        for i, window in enumerate(self.ma_windows):
            if f'MA_{window}' in ma_data.columns:
                fig.add_trace(go.Scatter(
                    x=ma_data.index,
                    y=ma_data[f'MA_{window}'],
                    mode='lines',
                    name=f'{window}-day MA',
                    line=dict(color=colors[i % len(colors)])
                ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title=y_label,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        return fig

    def plot_fed_funds_rate(self):
        """Plot Federal Funds Rate with moving averages"""
        return self.plot_with_moving_averages(
            'Fed_Funds_Rate',
            'Federal Funds Rate with Moving Averages',
            'Rate (%)'
        )

    def plot_ted_spread(self):
        """Plot TED Spread with moving averages"""
        return self.plot_with_moving_averages(
            'TED_Spread',
            'TED Spread with Moving Averages',
            'Basis Points'
        )

    def plot_excess_reserves(self):
        """Plot Excess Reserves with moving averages"""
        return self.plot_with_moving_averages(
            'Excess_Reserves_Billions',
            'Excess Reserves with Moving Averages',
            'Billions USD'
        )

    def add_ma_analysis(self) -> str:
        """Perform moving average analysis and return insights"""
        if self.data is None or self.data.empty:
            return "No data available for analysis"
            
        analysis_text = []
        
        # Analyze Fed Funds Rate and TED Spread
        for column in ['Fed_Funds_Rate', 'TED_Spread']:
            ma_data = self.calculate_moving_averages(column)
            current_value = ma_data[column].iloc[-1]
            
            ma_analysis = []
            for window in self.ma_windows:
                ma_value = ma_data[f'MA_{window}'].iloc[-1]
                if not np.isnan(ma_value):
                    if current_value > ma_value:
                        ma_analysis.append(f"above {window}-day MA")
                    else:
                        ma_analysis.append(f"below {window}-day MA")
            
            if ma_analysis:
                analysis_text.append(f"{column} is {', '.join(ma_analysis)}")
        
        # Analyze Excess Reserves separately
        ma_data = self.calculate_moving_averages('Excess_Reserves_Billions')
        current_value = ma_data['Excess_Reserves_Billions'].iloc[-1]
        
        ma_analysis = []
        for window in self.ma_windows:
            ma_value = ma_data[f'MA_{window}'].iloc[-1]
            if not np.isnan(ma_value):
                if current_value > ma_value:
                    ma_analysis.append(f"above {window}-day MA")
                else:
                    ma_analysis.append(f"below {window}-day MA")
        
        if ma_analysis:
            analysis_text.append(f"Excess Reserves is {', '.join(ma_analysis)}")
        
        return "\n".join(analysis_text)

def main():
    st.set_page_config(
        page_title="LiquidityLens",
        page_icon="📊",
        layout="wide"
    )

    st.title("LiquidityLens Dashboard")
    st.markdown("---")

    dashboard = LiquidityDashboard()

    # Add MA period selector to sidebar
    st.sidebar.header("Settings")
    selected_ma_periods = st.sidebar.multiselect(
        "Select Moving Average Periods",
        options=[5, 10, 20, 50, 100, 200],
        default=[5, 20, 50]
    )
    
    if selected_ma_periods:
        dashboard.ma_windows = selected_ma_periods

    if dashboard.load_data():
        # Create three columns for the metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            current_ffr = dashboard.data['Fed_Funds_Rate'].iloc[-1] if not dashboard.data.empty else 0
            ffr_change = dashboard.calculate_metric_change('Fed_Funds_Rate')
            st.metric(
                "Current Fed Funds Rate",
                f"{current_ffr:.2f}%",
                f"{ffr_change:.2f}%"
            )

        with col2:
            current_ted = dashboard.data['TED_Spread'].iloc[-1] if not dashboard.data.empty else 0
            ted_change = dashboard.calculate_metric_change('TED_Spread')
            st.metric(
                "TED Spread",
                f"{current_ted:.2f} bps",
                f"{ted_change:.2f}"
            )

        with col3:
            current_reserves = float(dashboard.data['Excess_Reserves'].iloc[-1]) / 1e9
            reserves_change = dashboard.calculate_metric_change('Excess_Reserves') / 1e9
            st.metric(
                "Excess Reserves (Billions)",
                f"${current_reserves:.2f}B",
                f"${reserves_change:.2f}B"
            )

        # Add MA analysis
        st.markdown("### Moving Average Analysis")
        st.markdown(dashboard.add_ma_analysis())

        # Create tabs for different charts
        tab1, tab2, tab3 = st.tabs(["Fed Funds Rate", "TED Spread", "Excess Reserves"])

        with tab1:
            fig = dashboard.plot_fed_funds_rate()
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig = dashboard.plot_ted_spread()
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        with tab3:
            fig = dashboard.plot_excess_reserves()
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        # Add technical analysis section
        st.markdown("### Technical Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Moving Average Crossovers")
            for column in ['Fed_Funds_Rate', 'TED_Spread', 'Excess_Reserves_Billions']:
                if column == 'Excess_Reserves_Billions':
                    ma_data = dashboard.calculate_moving_averages(column)
                else:
                    ma_data = dashboard.calculate_moving_averages(column)
                
                if len(ma_data) >= max(dashboard.ma_windows):
                    st.markdown(f"**{column}**")
                    for i in range(len(dashboard.ma_windows)-1):
                        for j in range(i+1, len(dashboard.ma_windows)):
                            ma1 = dashboard.ma_windows[i]
                            ma2 = dashboard.ma_windows[j]
                            if f'MA_{ma1}' in ma_data.columns and f'MA_{ma2}' in ma_data.columns:
                                if ma_data[f'MA_{ma1}'].iloc[-1] > ma_data[f'MA_{ma2}'].iloc[-1]:
                                    st.write(f"MA{ma1} is above MA{ma2}")
                                else:
                                    st.write(f"MA{ma1} is below MA{ma2}")

        # Add a data table with recent values
        if len(dashboard.data) >= 10:
            st.markdown("### Recent Data")
            st.dataframe(dashboard.data.tail(10))
        else:
            st.markdown("### Recent Data")
            st.dataframe(dashboard.data)

        # Add download button for the data
        st.download_button(
            label="Download Data as CSV",
            data=dashboard.data.to_csv(),
            file_name="liquidity_data.csv",
            mime="text/csv"
        )

    # Add footer
    st.markdown("---")
    st.markdown("Data updated daily | Source: Federal Reserve Economic Data (FRED)")

if __name__ == "__main__":
    main()