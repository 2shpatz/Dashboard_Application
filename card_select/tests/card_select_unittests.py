import os
import sys
import pandas as pd

import unittest
from unittest import mock
import dash_bootstrap_components as dbc


LAB_DIR = os.getenv("LAB_DIR")
DASHBOARD_DIR = os.path.join(LAB_DIR, "applications/dashboard")
CARD_SELECT_DIR = os.path.join(DASHBOARD_DIR, "dashboard_apps/card_select")
COLLECTION_DICT = {'databases': [{'database_name': 'tests', 'collections': [{'name': 'functional_tests', 'test_names': []}, {'name': 'operation_tests', 'test_names': []}, {'name': 'general_tests', 'test_names': []}]}, {'database_name': 'statistics', 'collections': [{'name': 'portia_statistics', 'test_names': []}, {'name': 'general_statistics', 'test_names': []}]}]}


sys.path.insert(0, str(os.environ.get('TOOLS_DIR')))
sys.path.insert(0, str(os.environ.get('LAB_DIR')))
sys.path.insert(0, str(os.environ.get('CARD_SELECT_DIR')))

from dashboard_apps.functional_test_app.pane import FunctionalTestPane
from dashboard_apps.database.mongodb_dashboard import MongoDB_SE, Collection
from dashboard_apps.card_select.card_select import CardSelect
import dashboard_apps.card_select.card_select as card_select_module
FunctionalTestPane = mock.Mock()
Collection.distinct = mock.Mock()
MongoDB_SE.get_collection = mock.Mock()
card_select_module.read_json_file = mock.Mock()
# Collection = mock.Mock()
TEST_APPLICATION = FunctionalTestPane()
MOCKED_INSTANCE = Collection("test", "test")

class TestCardSelect(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        super(TestCardSelect, self)
        self.application_for_testing = TEST_APPLICATION
        ################ mocking ####################
        card_select_module.read_json_file.return_value = COLLECTION_DICT
        Collection.distinct.return_value = ["test1", "test2", "test3"]
        #############################################
    @mock.patch.object(MongoDB_SE, "get_collection", return_value="test")
    @mock.patch.object(CardSelect, "read_collections_file", return_value=COLLECTION_DICT)
    def setUp(self, read_collections_file_mocked, get_collection_mocked):
        print("setUp")
        
        self.card_select_instance = CardSelect(self.application_for_testing, "", "", "test_names", "test_title")
        
    def tearDown(self):
        del self.card_select_instance
        print("tearDown")

    @unittest.skip
    def test_read_collection_file(self):
        expected = {'databases': [{'database_name': 'tests', 'collections': [{'name': 'functional_tests', 'test_names': []}, {'name': 'operation_tests', 'test_names': []}, {'name': 'general_tests', 'test_names': []}]}, {'database_name': 'statistics', 'collections': [{'name': 'portia_statistics', 'test_names': []}, {'name': 'general_statistics', 'test_names': []}]}]}
        received = self.card_select_instance.read_collections_file()
        self.assertEqual(expected, received)
    
    @unittest.skip
    @mock.patch.object(Collection, "distinct", return_value=["test1", "test2", "test3"])
    def test_get_collection_field_values(self, distinct_mocked):
        expected = ["test1", "test2", "test3"]
        received = self.card_select_instance.get_collection_field_values(MOCKED_INSTANCE, field="test")
        self.assertEqual(expected, received)
    
    @unittest.skip
    def test_create_collection_object(self):
        expected = MOCKED_INSTANCE
        received = self.card_select_instance.create_collection_object(database_name="test", collection_name="test")
        self.assertEqual(type(expected), type(received))

    @unittest.skip
    @mock.patch.object(CardSelect, "create_collection_object", return_value=MOCKED_INSTANCE)
    @mock.patch.object(CardSelect, "get_collection_field_values", return_value=["test1", "test2", "test3"])
    def test_create_dict_from_collection_file(self, get_collection_test_names_mocked, create_collection_object_mocked):
        expected = {'databases': [
            {'database_name': 'tests', 'collections': [
                {'name': 'functional_tests', 'test_names': ["test1", "test2", "test3"], "collection_instance": MOCKED_INSTANCE},
                {'name': 'operation_tests', 'test_names': ["test1", "test2", "test3"], "collection_instance": MOCKED_INSTANCE},
                {'name': 'general_tests', 'test_names': ["test1", "test2", "test3"]}], "collection_instance": MOCKED_INSTANCE},
            {'database_name': 'statistics', 'collections': [
                {'name': 'portia_statistics', 'test_names': ["test1", "test2", "test3"], "collection_instance": MOCKED_INSTANCE},
                {'name': 'general_statistics', 'test_names': ["test1", "test2", "test3"], "collection_instance": MOCKED_INSTANCE}]}]}

        received = self.card_select_instance.create_dict_from_collection_file(field="test_names")
        self.assertEqual(expected, received)

    @unittest.skip("TBD")
    @mock.patch.object(FunctionalTestPane, "get_card", return_value=dbc.Card)
    def test_create_application_card(self, get_card_mocked):
        expected = dbc.Card()
        received = self.card_select_instance.create_application_card()
        self.assertEqual(expected, received)

    @unittest.skip
    @mock.patch.object(CardSelect, "create_application_card", return_value=dbc.Card)
    def test_add_card(self, create_application_card_mocked):
        
        expected_body_content = [dbc.Card]
        self.card_select_instance.add_card()
        received_body_content = self.card_select_instance.body_content
        self.assertListEqual(expected_body_content, received_body_content)

    @unittest.skip
    def test_remove_card(self):
        card_to_be_removed = dbc.Card()
        card_to_be_removed_id = id(card_to_be_removed)

        card1 = dbc.Card()
        card1_id = id(card1)
        card2 = dbc.Card()
        card2_id = id(card2)
        card3 = dbc.Card()
        card3_id = id(card3)

        self.card_select_instance.body_content = [card1, card_to_be_removed, card2, card3]

        expected_body_content = [card1, card2, card3]
        self.card_select_instance.remove_card(card_to_be_removed_id)
        self.assertListEqual(expected_body_content, self.card_select_instance.body_content)

if __name__ == "__main__":
    unittest.main()
    