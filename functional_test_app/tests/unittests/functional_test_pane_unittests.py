import os
import sys
import pandas as pd

import unittest
from unittest.mock import Mock
LAB_DIR = os.getenv("LAB_DIR")

sys.path.insert(0, str(os.environ.get('TOOLS_DIR')))
sys.path.insert(0, str(os.environ.get('LAB_DIR')))


from applications.dashboard.dashboard_apps.functional_test_app.pane import FunctionalTestPane
from applications.dashboard.dashboard_apps.functional_test_app.dataframe import FunctionalTestDataFrame
class TestFunctionalTestPane(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        super()
        self.test_df = pd.DataFrame({"a": [5, 4, 3, 1], "b": [2, 1, 5, 6], "c": ["x", "x", "y", "y"]}) #for test
        self.dataframe_instance = FunctionalTestDataFrame(self.test_df)
        self.functional_test_pane = FunctionalTestPane(test_name="test", functional_test_data_frame_instance=self.dataframe_instance)

    def setUp(self):
        print("setUp")

    def tearDown(self):
        print("tearDown")


    # def test_export_PB(self):
    #     #This test checks the export_PB, loads the csv file that the export_PB creating and 
    
if __name__ == "__main__":
    unittest.main()
    