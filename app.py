from texts import TEXTS
from pathlib import Path
from utils.handlers import CandleHandler
import dxfeed as dx
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Dash imports
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output


# DxFeed init
date_time = datetime.now() - relativedelta(days=3)
endpoint = dx.Endpoint('demo.dxfeed.com:7300')

candle_subscription = endpoint.create_subscription('Candle', date_time=date_time)
candle_handler = CandleHandler(40)
candle_subscription.set_event_handler(candle_handler).add_symbols(['AAPL&Q{=5m}', 'IBM&Q{=5m}'])

# Dash app
app = dash.Dash(__name__, title='DxFeed Candle Charting')
app.layout = html.Div([
    html.Link(rel='stylesheet', href='/assets/stylesheet.css'),
    html.Img(src='assets/dxfeed_logo.png', id='logo'),
    dcc.Markdown(TEXTS.get('header'), dangerously_allow_html=True),
    html.Div([
        dcc.Interval(
                id='interval-component',
                interval=5*60*1000,  # in milliseconds
                n_intervals=0
        ),
        dcc.Graph(id='candle-graph'),
        dcc.RadioItems(
            id='candle-stocks',
            options=[
                {'label': 'AAPL', 'value': 'AAPL'},
                {'label': 'IBM', 'value': 'IBM'},
            ],
            value='AAPL'
        )
    ])
])


@app.callback(Output('candle-graph', 'figure'),
              [Input('interval-component', 'n_intervals'),
               Input('candle-stocks', 'value')])
def update_candle_graph(n, stocks):
    plots = list()  # List with data to display
    if 'AAPL' in stocks:
        plots.append(go.Candlestick(x=candle_handler.aapl_data['Time'].safe_get(),
                                    open=candle_handler.aapl_data['Open'].safe_get(),
                                    high=candle_handler.aapl_data['High'].safe_get(),
                                    low=candle_handler.aapl_data['Low'].safe_get(),
                                    close=candle_handler.aapl_data['Close'].safe_get(),
                                    name='AAPL'))
    if 'IBM' in stocks:
        plots.append(go.Candlestick(x=candle_handler.ibm_data['Time'].safe_get(),
                                    open=candle_handler.ibm_data['Open'].safe_get(),
                                    high=candle_handler.ibm_data['High'].safe_get(),
                                    low=candle_handler.ibm_data['Low'].safe_get(),
                                    close=candle_handler.ibm_data['Close'].safe_get(),
                                    name='IBM'))

    return dict(data=plots, layout=go.Layout(title='AAPL/IBM candles',
                                             showlegend=False,
                                             uirevision=True,
                                             font=dict(family="Open Sans, serif", size=18,)
                                             ))


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_silence_routes_logging=True)
