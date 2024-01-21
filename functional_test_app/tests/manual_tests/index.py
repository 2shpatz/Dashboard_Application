
from dash import html
import pandas as pd
from applications.dashboard.dashboard_apps.functional_test_app.pane import FunctionalTestPane

from applications.dashboard.dashboard_apps.utils.app import app


cards = []

df1 = pd.DataFrame({"a": [1, 2, 3, 4], "b": [2, 1, 5, 6], "c": [6, 0, 8, 4]}) #for test
df2 = pd.DataFrame({"a": [1, 2, 3, 4], "b": [5, 9, 3, 7], "c": [2, 2, 1, 5]}) #for test
df3 = pd.DataFrame({"a": [1, 2, 3, 4], "b": [7, 7, 1, 2], "c": [8, 3, 1, 0]}) #for test

tests_list = [(df1, "test_no1"), (df2, "test_no2"), (df3, "test_no3")]

for test_df, test_name in tests_list:
    instance = FunctionalTestPane(dataframe=test_df, test_name=test_name)
    cards.append(instance.get_card())
app.layout = html.Div(cards)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
