#Run this ability check from functional_test_pane_index.py
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback

from dash.dependencies import Input, Output


class FunctionalTestPane():
    def __init__(self, functional_test_data_frame_instance:object, test_name:str) -> None:
        self.test_name = test_name
        self.df_object = functional_test_data_frame_instance
        self.body_content = []
        self.card = self.create_pane()

    def create_header(self, text):
        return html.H3(text, className=text)
    
    def create_pane(self):
        # create the pane with all of the needed components and creates the pane layout
        self.body_content.append(self.create_header(self.test_name))
        self.body_content.append(self.create_plot())
        self.body_content.append(self.create_export_PB())
        self.body_content.append(self.create_download_for_export_PB())

        card_content = [
                dbc.CardHeader(),
                #dbc.CardImg(src="/static/images/placeholder286x180.png", top=True),
                dbc.CardBody(self.body_content, style={"outline": "solid purple", "border": "none"}),
                
            ]
        card = dbc.Card(card_content,
            style={"width": "75rem"},
        )
        return card
    
    def create_export_PB(self, location=None) -> id:
        button_id = f'{id(self)}_export_PB'
        @callback(
            Output(f'{id(self)}_download_csv', "data"),
            Input(button_id, "n_clicks"),
            prevent_initial_call=True,
        )
        def action_export_PB(n_clicks):
            # trigger export and download dataframe as a CSV file
            return dcc.send_data_frame(self.df_object.test_df.to_csv, "mydf.csv")

        return dbc.Button("Download CSV", id=button_id)

    def create_download_for_export_PB(self):

        return dcc.Download(id=f'{id(self)}_download_csv')

    def create_plot(self) -> dcc.Graph:
        fig = go.Figure(data=[
                                
                                go.Scatter(x=self.df_object.test_df['a'], y=self.df_object.test_df['b']),
                                go.Scatter(x=self.df_object.test_df['a'], y=self.df_object.test_df['c'])
                                ])
        return dcc.Graph(figure=fig)

    

if __name__ == "__main__":
    pass
