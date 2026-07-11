##### Python script

import pandas as pd
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import IsolationForest

# Page set up
st.set_page_config(
    page_title='Project 3', 
    page_icon='📊', 
    layout='wide'
)

# Descrição do projeto # Project description 
st.header('Project 3')
st.markdown('**Outlier detection in an assets percentage returns using Isolation Forest.**')

 # Function to calculate returns and detect outliers
def detect_outliers(data, contamination):
    # Calculates daily returns
    data['returns'] = data['Close'].pct_change()

    # Adjust data for outlier detection, removing NaNs
    returns = data['returns'].dropna().values.reshape(-1, 1)

    # Applies Isolation Forest
    model = IsolationForest(contamination=contamination, random_state=1)
    outliers = model.fit_predict(returns)
    data['outlier'] = pd.Series([1] + list(outliers), index=data.index)

    return data

# Side Bar Settings
st.sidebar.header('Options Menu')

# Tickers Selection
selected_stock = st.sidebar.text_input('Enter the stock ticker', value='PETR4.SA').upper()

# Selection of start and end dates
start_date = st.sidebar.date_input('Initial date', value=pd.to_datetime('today') - pd.DateOffset(days=100))
end_date = st.sidebar.date_input('Final date', value=pd.to_datetime('today'))

# Slider to adjust the contamination parameter
contamination = st.sidebar.slider(
    'Detection sensitivity',
    min_value=0.01,
    max_value=0.5,
    value=0.1, 
    step=0.01
)

# Downloads data for the selected stock.
data = yf.Ticker(selected_stock).history(start=start_date, end=end_date)

if not data.empty:
    #  Detects the outliers
    data = detect_outliers(data, contamination)

    #  Creates the subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Returns', 'Closing price'),
        vertical_spacing=0.2  # Espaçamento entre os subgráficos
    )

    # Returns chart
    fig.add_trace(go.Scatter(
        x=data.index, 
        y=data['returns'], 
        mode='lines', 
        name='returns',
        line=dict(color='orange', width=2)
    ), row=1, col=1)

    # Highlights the outliers in the returns chart.
    outliers_returns = data[data['outlier'] == -1]
    fig.add_trace(go.Scatter(
        x=outliers_returns.index, 
        y=outliers_returns['returns'], 
        mode='markers', 
        name='Outliers', 
        marker=dict(color='red', size=10, symbol='x')
    ), row=1, col=1)

    # Closing price chart
    fig.add_trace(go.Scatter(
        x=data.index, 
        y=data['Close'], 
        mode='lines', 
        name='Closing price',
        line=dict(color='darkblue', width=2)
    ), row=2, col=1)

    # Highlights outliers on the price chart.
    outliers_price = data[data['outlier'] == -1]
    fig.add_trace(go.Scatter(
        x=outliers_price.index, 
        y=outliers_price['Close'], 
        mode='markers', 
        name='Outliers', 
        marker=dict(color='red', size=10, symbol='x')
    ), row=2, col=1)

    # Setup the layout chart
    fig.update_layout(
        height=700,
        xaxis_title='Date',
        hovermode='x unified', # Unifies the x-axis tooltip for both charts.
        legend=dict(
            orientation='h',  
            yanchor='bottom',
            y=1.05,
            xanchor='center',
            x=0.5
        ),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    # Aligns the y-axes of the returns subplot
    fig.update_yaxes(title_text='Returns', row=1, col=1)

    # Enables x-axis linking.
    fig.update_xaxes(matches='x')

    # Show the chart
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error(f'No data was found for the asset {selected_stock}.')

st.sidebar.markdown('''
    <p style="margin-top: 30px; text-align: center">
        Project 3 for the financial market in Python.<br>
    </p>
''', unsafe_allow_html=True)
