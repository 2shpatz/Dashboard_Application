import dash
import random
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State


class CardTest():
    def __init__(self):
        self.my_id = id(self)

    def create_div(self):
        return html.Div(
                [
                    f"Title: my card test",
                    html.Div(id="card_test_space", children=[
                        html.Button(f'my_card_test{self.my_id}', id=f'card_test{self.my_id}', n_clicks=0),
                        html.Div(id=f'my_output{self.my_id}')
                        ])
                    ]
                )

    def create_callback(self):
        print(f"hello{self.my_id}")
        @dash.callback(
            Output(component_id=f'my_output{self.my_id}', component_property='children'),
            Input(component_id=f'my_card_test{self.my_id}', component_property='n_clicks'),
        )
        def update_div(n_clicks):
            return str(n_clicks)

class CardSelect():
    def __init__(self):
        pass

    def create_div(self):
        return html.Div(
                [
                    f"Title: App_title",
                    html.Button('Submit', id=f'add_card_test', n_clicks=0),
                    html.Div(id="card_test_space", children=[])
                    ]
                )
    def create_callback(self):
        @dash.callback(
            Output(component_id=f'card_test_space', component_property='children'),
            Input(component_id=f'add_card_test', component_property='n_clicks'),
            State('card_test_space',  component_property='children')
        )
        def update_div(n_clicks, children):
            new_card = CardTest()
            children.append(new_card.create_div())
            new_card.create_callback()
            return children

def main():
    app = dash.Dash(__name__)
    card_select = CardSelect()
    app.layout = html.Div(
            [
                html.H6("Change the value in the text box to see callbacks in action!"),
                card_select.create_div(),
                html.Br(),
                ]
            )

    card_select.create_callback()
    app.run_server(debug=True)

if __name__ == '__main__':
    main()
