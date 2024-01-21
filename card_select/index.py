import os,sys
from dash import html, Input, Output, callback

# sys.path.insert(0,"/")
DASH_APPS_DIR = os.getenv('DASHBOARD_APPS_DIR')
DASH_APPS_CONTAINED_DIR = f'{DASH_APPS_DIR}/..'
sys.path.insert(0,DASH_APPS_CONTAINED_DIR)
from dashboard_apps.card_select.card_select import AppInstanceManager, APP_TITLE

from dashboard_apps.utils.app import start_app

if __name__ == '__main__':
    app = start_app(APP_TITLE)
    instance_manager = AppInstanceManager()
    
    @callback(
        Output('container', 'children'),
        Input('container', 'children'),
        )
    def create_card_select_instance(_):
        card_select_instance = instance_manager.create_instance()
        card_select = card_select_instance.get_card()
        instance_manager.print_count_of_active_instances()
        return card_select

    app.layout = html.Div(id='container', children=[])
    app.run_server(debug=False, host='0.0.0.0')
