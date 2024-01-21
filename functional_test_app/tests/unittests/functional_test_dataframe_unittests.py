import os
import sys
import pandas as pd
import unittest
LAB_DIR = os.getenv("LAB_DIR")
DASHBOARD_DIR = os.path.join(LAB_DIR, "applications/dashboard")
sys.path.insert(0, str(os.environ.get('TOOLS_DIR')))
sys.path.insert(0, str(os.environ.get('LAB_DIR')))


from applications.dashboard.dashboard_apps.functional_test_app.dataframe import FunctionalTestDataFrame

TEST_DF_JSON_PATH = os.path.join(DASHBOARD_DIR, "unittests/dataframe.json")

def create_df():
    return pd.DataFrame([
            {"_id": {"Index": {"serial_number": ["7C00324F"], "ciBuild": [130434]}, "data": {"Product Type": "VENUS_LITE", "avg_check_upgrade": 454.1107714176178, "avg_reboot": 454.1107714176178, "avg_dead_time": 73.319806}}},
            {"_id": {"Index": {"serial_number": ["7C00324F"], "ciBuild": [157668]}, "data": {"Product Type": "VENUS_LITE", "avg_check_upgrade": 465.25683641433716, "avg_reboot": 465.25683641433716, "avg_dead_time": 74.539094}}},
            {"_id": {"Index": {"serial_number": ["7C00324F"], "ciBuild": [247015]}, "data": {"Product Type": "JUMBO_JUPITER", "avg_check_upgrade": 393.1274130344391, "avg_reboot": 393.1274130344391, "avg_dead_time": 158.564535}}},
            {"_id": {"Index": {"serial_number": ["7C00324F"], "ciBuild": [123492]}, "data": {"Product Type": "VENUS_LITE", "avg_check_upgrade": 443.84056663513184, "avg_reboot": 443.84056663513184, "avg_dead_time": 68.56154}}},
            {"_id": {"Index": {"serial_number": ["7C003304"], "ciBuild": [128305]}, "data": {"Product Type": "VENUS3", "avg_check_upgrade": 391.4494173526764, "avg_reboot": 391.4494173526764, "avg_dead_time": 47.349489}}},
            {"_id": {"Index": {"serial_number": ["7C003304"], "ciBuild": [277374]}, "data": {"Product Type": "JUMBO_JUPITER", "avg_check_upgrade": 392.126416683197, "avg_reboot": 392.126416683197, "avg_dead_time": 49.336127}}},
            {"_id": {"Index": {"serial_number": ["7C003304"], "ciBuild": [127704]}, "data": {"Product Type": "VENUS_LITE", "avg_check_upgrade": 417.39873456954956, "avg_reboot": 417.39873456954956, "avg_dead_time": 55.975061}}},
            {"_id": {"Index": {"serial_number": ["7C003304"], "ciBuild": [197071]}, "data": {"Product Type": "JUMBO_JUPITER", "avg_check_upgrade": 486.87, "avg_reboot": 486.87, "avg_dead_time": 78.973785}}},
            {"_id": {"Index": {"serial_number": ["7C003304"], "ciBuild": [267935]}, "data": {"Product Type": "VENUS3", "avg_check_upgrade": 394.20925641059875, "avg_reboot": 394.20925641059875, "avg_dead_time": 50.13212}}},
            {"_id": {"Index": {"serial_number": ["7C003304"], "ciBuild": [269609]}, "data": {"Product Type": "JUPITER", "avg_check_upgrade": 393.6700096130371, "avg_reboot": 393.6700096130371, "avg_dead_time": 49.141308}}},
            {"_id": {"Index": {"serial_number": ["7C003304"], "ciBuild": [97097]}, "data": {"Product Type": "VENUS_LITE", "avg_check_upgrade": 390.9276430606842, "avg_reboot": 390.9276430606842, "avg_dead_time": 50.19704}}},
            {"_id": {"Index": {"serial_number": ["7C003304"], "ciBuild": [188954]}, "data": {"Product Type": "VENUS_LITE", "avg_check_upgrade": 481.55, "avg_reboot": 481.55, "avg_dead_time": 74.11741}}},
            {"_id": {"Index": {"serial_number": ["7C111111"], "ciBuild": [130434]}, "data": {"Product Type": "VENUS3", "avg_check_upgrade": 454.1107714176178, "avg_reboot": 454.1107714176178, "avg_dead_time": 73.319806}}},
            {"_id": {"Index": {"serial_number": ["7C111111"], "ciBuild": [157668]}, "data": {"Product Type": "VENUS_LITE", "avg_check_upgrade": 465.25683641433716, "avg_reboot": 465.25683641433716, "avg_dead_time": 74.539094}}},
            {"_id": {"Index": {"serial_number": ["7C111111"], "ciBuild": [247015]}, "data": {"Product Type": "VENUS_LITE", "avg_check_upgrade": 393.1274130344391, "avg_reboot": 393.1274130344391, "avg_dead_time": 158.564535}}},
            {"_id": {"Index": {"serial_number": ["7C111111"], "ciBuild": [123492]}, "data": {"Product Type": "JUPITER", "avg_check_upgrade": 443.84056663513184, "avg_reboot": 443.84056663513184, "avg_dead_time": 68.56154}}},
            {"_id": {"Index": {"serial_number": ["7C111111"], "ciBuild": [128305]}, "data": {"Product Type": "JUMBO_JUPITER", "avg_check_upgrade": 391.4494173526764, "avg_reboot": 391.4494173526764, "avg_dead_time": 47.349489}}},
            {"_id": {"Index": {"serial_number": ["7C111111"], "ciBuild": [277374]}, "data": {"Product Type": "VENUS_LITE", "avg_check_upgrade": 392.126416683197, "avg_reboot": 392.126416683197, "avg_dead_time": 49.336127}}},
            {"_id": {"Index": {"serial_number": ["7C111111"], "ciBuild": [127704]}, "data": {"Product Type": "VENUS_LITE", "avg_check_upgrade": 417.39873456954956, "avg_reboot": 417.39873456954956, "avg_dead_time": 55.975061}}},
            {"_id": {"Index": {"serial_number": ["7C111111"], "ciBuild": [197071]}, "data": {"Product Type": "JUPITER", "avg_check_upgrade": 486.87, "avg_reboot": 486.87, "avg_dead_time": 78.973785}}},
            {"_id": {"Index": {"serial_number": ["6B222222"], "ciBuild": [267935]}, "data": {"Product Type": "JUMBO_JUPITER", "avg_check_upgrade": 394.20925641059875, "avg_reboot": 394.20925641059875, "avg_dead_time": 50.13212}}},
            {"_id": {"Index": {"serial_number": ["6B222222"], "ciBuild": [269609]}, "data": {"Product Type": "VENUS_LITE", "avg_check_upgrade": 393.6700096130371, "avg_reboot": 393.6700096130371, "avg_dead_time": 49.141308}}},
            {"_id": {"Index": {"serial_number": ["6B222222"], "ciBuild": [97097]}, "data": {"Product Type": "VENUS3", "avg_check_upgrade": 390.9276430606842, "avg_reboot": 390.9276430606842, "avg_dead_time": 50.19704}}},
            {"_id": {"Index": {"serial_number": ["6B222222"], "ciBuild": [188954]}, "data": {"Product Type": "VENUS_LITE", "avg_check_upgrade": 481.55, "avg_reboot": 481.55, "avg_dead_time": 74.11741}}}
        ])
    

class TestFunctionalTestPane(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        super()
        self.df = create_df
        self.test_steps_names = ["avg_check_upgrade", "avg_reboot", "avg_dead_time"]
        self.func_test_df_instance = FunctionalTestDataFrame(self.df)
        
    def setUp(self):
        print("setUp")

    def tearDown(self):
        print("tearDown")

    def test_get_sn_list(self):
        expected_list = ["7C00324F", "7C003304", "7C111111", "6B222222"]
        result_list = self.func_test_df_instance.get_sn_list()
        self.assertEqual(set(result_list), set(expected_list))

    def test_collect_test_fields(self):
        expected_list = self.test_steps_names
        result_list = self.func_test_df_instance.collect_test_step_fields()
        self.assertEqual(set(result_list), set(expected_list))

    def test_filter_by_field_n_value_using_serial_number(self):
        requested_sn = "6B222222"
        expected_list = [{"_id": {"Index": {"serial_number": [requested_sn], "ciBuild": [267935]}, "data": {"Product Type": "VENUS_LITE", "avg_check_upgrade": 394.20925641059875, "avg_reboot": 394.20925641059875, "avg_dead_time": 50.13212}}},
            {"_id": {"Index": {"serial_number": [requested_sn], "ciBuild": [269609]}, "data": {"Product Type": "VENUS_LITE", "avg_check_upgrade": 393.6700096130371, "avg_reboot": 393.6700096130371, "avg_dead_time": 49.141308}}},
            {"_id": {"Index": {"serial_number": [requested_sn], "ciBuild": [97097]}, "data": {"Product Type": "VENUS_LITE", "avg_check_upgrade": 390.9276430606842, "avg_reboot": 390.9276430606842, "avg_dead_time": 50.19704}}},
            {"_id": {"Index": {"serial_number": [requested_sn], "ciBuild": [188954]}, "data": {"Product Type": "VENUS_LITE", "avg_check_upgrade": 481.55, "avg_reboot": 481.55, "avg_dead_time": 74.11741}}}
        ]
        result_list = self.func_test_df_instance.filter_by_field_n_value(field="serial_number", value="6B222222")
        self.assertEqual(set(result_list), set(expected_list))

    def test_filter_by_field_n_value_using_product_type(self):
        requested_product_type = "JUMBO_JUPITER"
        expected_list = [{"_id": {"Index": {"serial_number": ["7C00324F"], "ciBuild": [247015]}, "data": {"Product Type": requested_product_type, "avg_check_upgrade": 393.1274130344391, "avg_reboot": 393.1274130344391, "avg_dead_time": 158.564535}}},
            {"_id": {"Index": {"serial_number": ["7C003304"], "ciBuild": [277374]}, "data": {"Product Type": requested_product_type, "avg_check_upgrade": 392.126416683197, "avg_reboot": 392.126416683197, "avg_dead_time": 49.336127}}},
            {"_id": {"Index": {"serial_number": ["7C003304"], "ciBuild": [197071]}, "data": {"Product Type": requested_product_type, "avg_check_upgrade": 486.87, "avg_reboot": 486.87, "avg_dead_time": 78.973785}}},
            {"_id": {"Index": {"serial_number": ["7C111111"], "ciBuild": [128305]}, "data": {"Product Type": requested_product_type, "avg_check_upgrade": 391.4494173526764, "avg_reboot": 391.4494173526764, "avg_dead_time": 47.349489}}},
            {"_id": {"Index": {"serial_number": ["6B222222"], "ciBuild": [267935]}, "data": {"Product Type": "JUMBO_JUPITER", "avg_check_upgrade": 394.20925641059875, "avg_reboot": 394.20925641059875, "avg_dead_time": 50.13212}}}
        ]
        result_list = self.func_test_df_instance.filter_by_field_n_value(field="Product Type", value="JUMBO_JUPITER")
        self.assertEqual(set(result_list), set(expected_list))

        
if __name__ == "__main__":
    unittest.main()
    