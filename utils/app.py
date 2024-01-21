from flask import Flask
import dash
import dash_bootstrap_components as dbc

def start_app(app_title='Dash'):
    server = Flask(__name__)
    app = dash.Dash(__name__,server=server,title=app_title, external_stylesheets=[dbc.themes.PULSE], suppress_callback_exceptions=True)
    # server = app.server
    return app
