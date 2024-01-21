from calendar import c
from numpy import NaN
import pandas as pd

class FunctionalTestDataFrame():
    # this class gets panda dataframe and manages it according to the program needs
    def __init__(self, test_df:pd.DataFrame):
        self.test_df = test_df
        self.add_formated_version_field()

    
    def get_dataframe(self):
        return self.test_df
        
    def insert_column(self, column_name, values=None, location=None):
        # insert a column to the dataframe with the requested values
        if values is None:
            values = ['NaN']*len(self.test_df.index)
        if location is None:
            location = len(self.test_df.columns)
        self.test_df.insert(loc=location, column=column_name, value=values)

    def filter_by_field_n_value(self, field, value, alternative_dataframe:pd.DataFrame=None) -> pd.DataFrame:
        # filter chosen results from the main data frame
        # for example field = "serial_number" , value = "7C111111" or value = ["7C111111", "7C222222", ...]
        dataframe = self.test_df
        if alternative_dataframe is not None:
            dataframe = alternative_dataframe

        if isinstance(value, (bool, str)):
            filtered_df = dataframe.loc[dataframe[field] == value]
        elif isinstance(value, list):
            filtered_df = dataframe.loc[dataframe[field].isin(value)]
        else:
            raise TypeError(f'The given value type: {type(value)} is invalid')
        return filtered_df

    def init_steps_values_by_serial_numbers(self, serial_number, fields_to_update, alternative_dataframe:pd.DataFrame=None) -> pd.DataFrame:
        # updates value of fields according to another field condition
        # for example, update all steps of rows with: filter_field = "serial_number" , filter_field_value = "7C111111" to new_value

        dataframe = self.test_df.copy()
        if alternative_dataframe is not None:
            dataframe = alternative_dataframe.copy()

        dataframe.loc[dataframe.serial_number != serial_number, fields_to_update] = None
        dataframe = dataframe.sort_values(["formated_version", fields_to_update[0]]).drop_duplicates("formated_version", keep='first')

        return dataframe


    def get_sn_list(self, alternative_dataframe:pd.DataFrame=None) -> list:
        # collects all serial numbers from the data frame
        dataframe = self.test_df
        if alternative_dataframe is not None:
            dataframe = alternative_dataframe
        serial_numbers_df =  dataframe["serial_number"]
        serial_numbers_list = serial_numbers_df.drop_duplicates().values.tolist()
        return serial_numbers_list

    def get_sn_pt_list(self, alternative_dataframe:pd.DataFrame=None) -> list:
        # collects all serial numbers and product type from the data frame and returns them as list of lists
        dataframe = self.test_df
        if alternative_dataframe is not None:
            dataframe = alternative_dataframe
        serial_vs_product_df = dataframe[["serial_number", "Product Type"]]
        serial_vs_product_list = serial_vs_product_df.drop_duplicates().values.tolist()
        
        return serial_vs_product_list

    def get_pt_list(self) -> list:
        # collects all product types from the data frame
        return list(set(self.test_df["Product Type"]))

    def get_test_step_fields(self):
        # collects all test steps from the data frame
        df_columns_list = list(self.test_df.columns)
        columns_to_remove = ['portia_version', 'serial_number', 'Product Type', 'formated_version', 'test_pass']
        step_fields = [field for field in df_columns_list if field not in columns_to_remove]
        return step_fields

    def get_portia_versions(self, alternative_dataframe=None):
        # collect portia versions and return it with the format: <major>.<minor>.<build>.<ciBuild> (exp: 4.20.7.46247)
        dataframe = self.test_df
        if alternative_dataframe is not None:
            dataframe = alternative_dataframe
        portia_versions_list = dataframe["formated_version"].tolist()

        formatted_list = list(dict.fromkeys(portia_versions_list)) # remove duplicates and keep order
        return formatted_list

    def add_formated_version_field(self):
        self.test_df['formated_version'] = self.test_df["portia_version"].apply(lambda item: f"{item.get('major')}.{item.get('minor')}.{item.get('build')}.{item.get('ciBuild')}")

if __name__ == "__main__":
    data = pd.DataFrame({'serial_number' : ['1', '2'], 
                        'Product Type' : ['X', 'Y'],
                        'C' : [2, 3]})
    ft_dataframe = FunctionalTestDataFrame(data)
    print (ft_dataframe.get_sn_list())