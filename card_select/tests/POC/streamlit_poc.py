import streamlit as st
import pandas as pd

class CardTest():
    def __init__(self, testname):
        self.testname = testname
        self.my_id = id(self)

    def create_component(self):
        df1 = pd.DataFrame({"a": [1, 2, 3, 4], "b": [2, 1, 5, 6], "c": [6, 0, 8, 4]}) #for test
        st.title(f'{id(self)}_{self.testname}')
        st.download_button(label="export_csv", data=df1.to_csv(), file_name="my.csv", key=f'{id(self)}_download')


class CardSelect():
    def __init__(self):
        self.create_component()
        

    def create_component(self):
        st.title("card_select")
        st.button(label="apply", on_click=self.apply_action)

    def apply_action(self):
        new_app = CardTest("test")
        new_app.create_component()
        new_app1 = CardTest("test")
        new_app1.create_component()


def main():
    card_select = CardSelect()

if __name__ == '__main__':
    main()