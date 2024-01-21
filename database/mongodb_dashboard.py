
import os
import sys
from pymongo import MongoClient,DESCENDING
from pymongo import errors as mongo_error
import pandas as pd

MONGOBD_SEDG_SERVER = "emb-jenk-slv01"
MONGOBD_SEDG_PORT = 27017

class MongoDB_Dash(MongoClient):
    def __init__(self, host=MONGOBD_SEDG_SERVER, port=MONGOBD_SEDG_PORT):
        try:
            super().__init__(host, port)
        except [mongo_error.ConnectionFailure, mongo_error.ConfigurationError] as err:
            exc_type, _, exc_tb = sys.exc_info()
            error = f"[{os.path.basename(__file__)}]Exception: {err} {exc_type} Error line: {exc_tb.tb_lineno}"
            raise

    def get_collection(self, database_name, collection_name):
        # Retrieves mongodb collection from database by name
        database = self.get_database(database_name)
        return database[collection_name]


class Collection():
    # This class accessing the mongodb collection functions to the dashboard apps
    def __init__(self, database_name, collection_name):
        self.database_name = database_name
        self.collection_name = collection_name
        self.collection = MongoDB_Dash().get_collection(database_name, collection_name)

    def get_database_name(self):
        return self.database_name

    def get_collection_name(self):
        return self.collection_name

    def get_aggregated_dataframe(self, pipeline:list) -> pd.DataFrame:
        return pd.DataFrame(list(self.collection.aggregate(pipeline)))

    def distinct(self, field_name:str) -> list:
        # Retrieves list of all the values of a given field name
        return self.collection.distinct(field_name)

    def get_all_documents_cursor(self):
        return self.collection.find({})

    def find_one(self, field, value):
        # retrieves the last document that found in the collection
        return self.collection.find_one({field : value})
    
    def find_last(self, field, value):
        # retrieves the first document that found in the collection
        return self.collection.find_one({field : value}, sort=[('_id', DESCENDING)])

if __name__ == '__main__':

    function_tests_collection = Collection("pipeline_regression", "01_function_tests")
