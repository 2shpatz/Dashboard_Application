from multiprocessing.connection import _ConnectionBase
import os, sys
import json
import time
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback, no_update
from dash.dependencies import MATCH
DASH_APPS_DIR = os.getenv('DASHBOARD_APPS_DIR')
DASH_APPS_CONTAINED_DIR = f'../{DASH_APPS_DIR}'
sys.path.insert(0,DASH_APPS_CONTAINED_DIR)
from dashboard_apps.functional_test_app.pane import AppInstanceManager as ChildAppInstanceManager # for different application replace this import with the wanted application path
from dashboard_apps.database.mongodb_dashboard import Collection


VERSION = 'v4.3.4'

# Card select global variables, TBD: move to user configuration file 
APP_TITLE = "Functional Tests History"
FIELD_TO_CARD = 'test_name'
DATABASE_VS_COLLECTION_FILE = os.path.join(DASH_APPS_DIR, "card_select/databases_collections.json")

SESSION_TIMEDOUT_STRING = 'Session finished! Please refresh the page.'
NUM_OF_HOURS_TO_TIMEOUT = 6 # number of unused hours before session timeout
INSTANCE_SESSION_TIMEOUT = NUM_OF_HOURS_TO_TIMEOUT * 3600 # in sec, if an instance won't be used for longer then this time it will be deleted


DATABASE_POS = 0
COLLECTION_POS = 1
VALUE_POS = 2

# URL sectors:
# URL_SITE_ADDRESS = 'http://seil-embp01/dashboard-night-build'
URL_SITE_NUM_OF_FIELDS = 3
URL_DB_COL_FIELD_INDEX = 0
URL_CONFIG_START = 1

# Dynamic components ids (names)
DYNAMIC_CARDS_BODY = 'dynamic_card_body'
DYNAMIC_CARDS_FOOTER = 'dynamic_card_footer'
DYNAMIC_MAIN_TITLE = 'dynamic_main_title'
DYNAMIC_MAIN_DROPDOWN = 'dynamic_main_dropdown'
DYNAMIC_APPLY_PB = 'dynamic_apply_PB'
DYNAMIC_GENERATE_URL_PB = 'dynamic_generate_url_PB'
DYNAMIC_LOCATION = 'dynamic_location'
DYNAMIC_URL_POPOVER = 'dynamic_popover'
DYNAMIC_URL_POPOVER_BODY = 'dynamic_popover_body'


class CardSelect():
    def __init__(self, component_index:int, children_application_manager:object, database_vs_collection_file_path:str, field_to_cards_name:str, page_title:str, create_callbakes:True) -> None:
        self.children_application_manager = children_application_manager # the application that will be start when a card is selected (for example FunctionalTestPane)
        self.database_vs_collection_file_path = database_vs_collection_file_path # contains json dict with databases collections and test names
        self.field_to_cards_name = field_to_cards_name
        self.page_title = page_title
        self.collections_dictionary = self.create_dict_from_collection_file()
        self.body_content = []
        self.version = VERSION
        self.last_used = time.time()
        ############## Component IDs ##############
        self.card_body_id = {'type': DYNAMIC_CARDS_BODY, 'index': component_index, 'id':id(self)}
        self.card_footer_id = {'type': DYNAMIC_CARDS_FOOTER, 'index': component_index, 'id':id(self)}
        self.main_title = {'type': DYNAMIC_MAIN_TITLE, 'index': component_index, 'id':id(self)}
        self.dropdown_id = {'type': DYNAMIC_MAIN_DROPDOWN, 'index': component_index, 'id':id(self)}
        self.apply_cards_PB_id = {'type': DYNAMIC_APPLY_PB, 'index': component_index, 'id':id(self)}
        self.generate_url_id = {'type': DYNAMIC_GENERATE_URL_PB, 'index': component_index, 'id':id(self)}
        self.location_id = {'type': DYNAMIC_LOCATION, 'index': component_index, 'id':id(self)}
        self.popover_id = {'type': DYNAMIC_URL_POPOVER, 'index': component_index, 'id':id(self)}
        self.popover_body_id = {'type': DYNAMIC_URL_POPOVER_BODY, 'index': component_index, 'id':id(self)}
        ###########################################
        self.card = self.create_main_page()
        if create_callbakes:
            self.create_callbacks()

    def get_last_used_time(self):
        return self.last_used

    def update_last_used_time(self):
        self.last_used = time.time()

    def create_callbacks(self):

        @callback(
            Output(self.apply_cards_PB_id, 'disabled'),
            Input(self.dropdown_id, 'value')
            )
        def set_button_enabled_state(dropdown_value):
            button_disabled = dropdown_value is None
            return button_disabled

        @callback(
            [Output(self.card_footer_id, "children"),
            Output(self.dropdown_id, 'value')],
            Input(self.apply_cards_PB_id, 'n_clicks'),
            [State(self.location_id, 'search'),
            State(self.dropdown_id, 'value'),
            State(self.card_footer_id, "children")]
        )
        def action_create_cards(n_clicks, pathname, dropdown_items, card_children):
            # actions to performe when the apply_cards_PB is pressed
            # add or remove cards and update the cards_id list
            if n_clicks>0:
                print("apply pressed")
                if dropdown_items is not None:
                    for item in dropdown_items:
                        card = self.create_application_card(field_path=item)
                        card_children.insert(0, card)
                dropdown_value = None

                return card_children, dropdown_value
            if pathname:
                url_strings = pathname.strip('?').split('&')
                for string in url_strings:
                    card = self.create_application_card(field_path=string.split(';')[URL_DB_COL_FIELD_INDEX], initial_configure=string.split(';')[URL_CONFIG_START:])
                    card_children.insert(0, card)
                
                return card_children, no_update
            return no_update, no_update

        @callback(
            Output(self.popover_body_id, 'massage'),
            Input(self.generate_url_id, 'n_clicks'),
            State(self.location_id, 'href'),
            prevent_initial_call=True
        )
        def generate_url(_, real_url):
            print('copy url pressed')
            url_site = '/'.join(real_url.split('/')[:URL_SITE_NUM_OF_FIELDS])
            state_search = self.generate_state_search_url()
            full_url = os.path.join(url_site, state_search)
            return full_url
            
    @staticmethod
    def _read_json_file(file_path):
        # reads json setting file
        with open(file_path) as json_file:
            return json.load(json_file)
        
    def get_card(self):
        return self.card

    def generate_state_search_url(self):
        
        instances_urls = []
        app_instances = self.children_application_manager.get_parent_filtered_dict(parent_id=id(self))
        if app_instances is not None:
            for instance_data in app_instances.values():
                app_instance = instance_data.get('app_instance')
                instance_collection = instance_data.get('collection')
                field_name = instance_data.get('field_name')
                database = instance_collection.get_database_name()
                collection = instance_collection.get_collection_name()
                state = app_instance.get_card_state()
                systems = ''
                if state.get('systems'):
                    systems_values = str(state.get('systems')).translate({ord(i):None for i in "' "})
                    systems = f';systems{systems_values}'
                steps = ''
                if state.get('steps'):
                    steps_values = str(state.get('steps')).translate({ord(i):None for i in "' "})
                    steps = f';steps{steps_values}'
                formated_url = f'{database}:{collection}:{field_name}{systems}{steps}'
                instances_urls.append(formated_url)
        search = ''
        if instances_urls:
            search = f'?{"&".join(instances_urls)}'
        return search

    def read_collections_file(self):
        # reads the database vs collection file
        collection_dict = self._read_json_file(self.database_vs_collection_file_path)
        return collection_dict

    def create_dict_from_collection_file(self) -> dict:
        '''
            Creates a dictionary of databases vs collections vs <requested_field> from predefine collection file
            for example, if the requested field is "tests_list" and the collection file is databases_collections.json.example, the dictionary will be:
            dictionary = {'databases': [
                name: <database1> : {collections : [{name : <collection1_name>, tests_list : [test1, test2, ...], collection_instance : object}, {name : <collection2_name>, tests_list:[...], collection_instance: object}, ...]},
                name: <database2> : {collections : [{name : <collection1_name>, tests_list : [test1, test2, ...], collection_instance : object}, {name : <collection2_name>, tests_list:[...], collection_instance: object}, ...]},
                ...
                ]}
            uses get_collection_test_names() and create_collection_object()
        '''
        collections_dictionary = self.read_collections_file()
        for database in collections_dictionary.get("databases"):
            for collection in database.get("collections"):
                collection_obj = self.create_collection_object(database.get("name"), collection.get("name"))
                collection[self.field_to_cards_name] = self.get_collection_field_values(collection=collection_obj, field=self.field_to_cards_name)

        return collections_dictionary

    def create_collection_object(self, database_name, collection_name):
		# creates database Collection object for a given collection_name
        # the collections are used to connect with the database
        return Collection(database_name=database_name, collection_name=collection_name)


    def get_collection_field_values(self, collection:object, field) -> list:
        # retrieves list of the collection field values
        field_values_list = collection.distinct(field_name=field)
        return field_values_list

    def create_main_page(self):
        self.body_content.append(self.create_location())
        self.body_content.append(self.create_upper_section())
        self.body_content.append(self.create_select_dropdown())
        self.body_content.append(self.create_PB(children="Apply", id=self.apply_cards_PB_id, n_clicks=0, color="primary", disabled=True))
        self.body_content.append(self.create_PB(children=[html.Img(src=r'/assets/update_url.png',
                                                                    style={'height':'46px', 'width':'46px', 'margin-left': '-11px', 'margin-top':'-5px'})],
                                                id=self.generate_url_id, n_clicks=0,
                                                color="secondary", title='Generate State URL',
                                                style={'width':'50px', 'height':'50px', 'float': 'right', 'display': 'inline-block'}))
        self.body_content.append(self.create_Popover(id=self.popover_id, body_id=self.popover_body_id, header='Copy and share', massage='Generating URL...', target=self.generate_url_id, trigger="legacy", placement='left'))
        

        card_content = [
                dbc.CardBody(id=self.card_body_id, children=self.body_content, style={"outline": "solid purple", "border": "none",
                            'background-image': 'url("/assets/black-white.png")',
                            'background-position': 'top right'}),
                dbc.CardFooter(html.Div(id=self.card_footer_id, children=[]))
            ]
        card = dbc.Card(children=[html.Div(children=card_content)], style={"width": "auto"})
        return card

    def create_upper_section(self):
        # creates the main card upper section
        section_content = []
        section_content.append(html.Div([self.create_header(id=self.main_title, text=self.page_title, size=1, color='purple')], style={'display': 'inline-block'}))
        section_content.append(html.Div([self.create_text(children=self.version, style={'text-align': 'right'})], style={'float': 'right', 'display': 'inline-block'}))
        return html.Div(section_content)

    def create_text(self, **kwargs):
        return html.Plaintext(**kwargs)

    def create_header(self, text:str, size:int=3, color:str=None, align:str=None, **kwargs):
        
        style={'color':color, 'text-align':align}

        return {
            1: html.H1(children=text, className=text, style=style, **kwargs),
            2: html.H2(children=text, className=text, style=style, **kwargs),
            3: html.H3(children=text, className=text, style=style, **kwargs),
            4: html.H4(children=text, className=text, style=style, **kwargs),
            5: html.H5(children=text, className=text, style=style, **kwargs),
            6: html.H6(children=text, className=text, style=style, **kwargs)
        }[size]

    def create_Popover(self, body_id, header, massage, **kwargs):
        
        return dbc.Popover(
        children=[
            dbc.PopoverHeader(header),
            dbc.PopoverBody(id=body_id, children=massage)],
        **kwargs
        )

    def create_location(self):
        return dcc.Location(id=self.location_id, refresh=False)

    def create_store(self, store_id):
        return dcc.Store(store_id)

    def list_database_vs_collection_vs_field(self):
        collection_vs_field = []
        for database in self.collections_dictionary.get("databases"):
            database_name = database.get("name")
            for collection in database.get("collections"):
                collection_name = collection.get("name")
                for field in collection.get(self.field_to_cards_name):
                    collection_vs_field.append([database_name, collection_name, field])
        return collection_vs_field

	####### select card functions #######
    def create_select_dropdown(self):
		# creates dropdown from the self.collections_name_dict
        dropdown_options = [{'label': f"{item[COLLECTION_POS]} > {item[VALUE_POS]}", 'value': ":".join(item)} for item in self.list_database_vs_collection_vs_field()]
        return html.Div([
            dcc.Dropdown(id=self.dropdown_id, multi=True, options=dropdown_options, placeholder=f"Select {self.field_to_cards_name}")], style={"width": "50%"}
        )

    def create_PB(self, **kwargs) -> dbc.Button:
        return dbc.Button(**kwargs)

    def create_image(self, **kwargs):
        return html.Img(**kwargs)

    def create_clipboard(self, **kwargs):
        return dcc.Clipboard(**kwargs)

    def remove_card(self, card_id:str):
        # removes a card from the main card (from the card's body_content)
        ...

    #####################################

    def create_application_card(self, field_path, initial_configure=None) -> dbc.Card:
        # trigger a creation of application card (create_application_card) and adds it to the main card (to the card's body_content)
        # creates an instance of the received application (self.children_application_manager) and returns its card
        database_name, collection_name, field_value = field_path.split(':')
        collection = self.create_collection_object(database_name, collection_name)
        app_instance = self.children_application_manager.create_instance(id(self), collection, field_value, initial_configure)
        new_card = app_instance.get_card()
        return new_card

class CreateAppDynamicCallbacks():
    '''This Class creates Dynamic Callbacks for the Dash elements.
    Dynamic Callbacks are mandatory for controling elements that are currently not exist and will be created in the future.'''
    def __init__(self, instances_dict) -> None:
        self.instances_dict = instances_dict

        self.create_dynamic_callback()


    def create_dynamic_callback(self):

        @callback(
            Output({'type': DYNAMIC_APPLY_PB, 'id':MATCH, 'index': MATCH}, 'disabled'),
            Input({'type': DYNAMIC_MAIN_DROPDOWN, 'id':MATCH, 'index': MATCH}, 'value')
        )
        def select_from_dropdown_actions(dropdown_value):
            button_disabled = dropdown_value is None
            return button_disabled

        @callback(
            [Output({'type': DYNAMIC_CARDS_FOOTER, 'id':MATCH, 'index': MATCH}, 'children'),
            Output({'type': DYNAMIC_MAIN_DROPDOWN, 'id':MATCH, 'index': MATCH}, 'value'),
            Output({'type': DYNAMIC_MAIN_TITLE, 'id':MATCH, 'index': MATCH}, 'children')],
            Input({'type': DYNAMIC_APPLY_PB, 'id':MATCH, 'index': MATCH}, 'n_clicks'),
            [State({'type': DYNAMIC_APPLY_PB, 'id':MATCH, 'index': MATCH}, 'id'),
            State({'type': DYNAMIC_LOCATION, 'id':MATCH, 'index': MATCH}, 'search'),
            State({'type': DYNAMIC_MAIN_DROPDOWN, 'id':MATCH, 'index': MATCH}, 'value'),
            State({'type': DYNAMIC_CARDS_FOOTER, 'id':MATCH, 'index': MATCH}, 'children')],
        )
        def action_create_cards(n_clicks, comp_id, pathname, dropdown_items, card_children):
            # actions to performe when the apply_cards_PB is pressed
            # add or remove cards and update the cards_id list
            id_of_the_pressed_button_card = comp_id.get('id')
            pressed_card_dict = self.instances_dict.get(id_of_the_pressed_button_card)
            if pressed_card_dict is None:
                return no_update, no_update, SESSION_TIMEDOUT_STRING
            pressed_card_instance = pressed_card_dict.get('app_instance')
            pressed_card_instance.update_last_used_time()
            if n_clicks>0:
                print('manual action_create_cards')
                if dropdown_items is not None:
                    for item in dropdown_items:
                        card = pressed_card_instance.create_application_card(field_path=item)
                        card_children.insert(0, card)
                dropdown_value = None

                return card_children, dropdown_value, no_update
            if pathname:
                print('startup action_create_cards')
                url_strings = pathname.strip('?').split('&')
                for string in url_strings:
                    card = pressed_card_instance.create_application_card(field_path=string.split(';')[URL_DB_COL_FIELD_INDEX], initial_configure=string.split(';')[URL_CONFIG_START:])
                    card_children.insert(0, card)
                return card_children, no_update, no_update
            return no_update, no_update, no_update

        @callback(
            Output({'type': DYNAMIC_URL_POPOVER_BODY, 'id':MATCH, 'index': MATCH}, 'children'),
            Input({'type': DYNAMIC_URL_POPOVER, 'id':MATCH, 'index': MATCH}, 'is_open'),
            [State({'type': DYNAMIC_URL_POPOVER, 'id':MATCH, 'index': MATCH}, 'id'),
            State({'type': DYNAMIC_LOCATION, 'id':MATCH, 'index': MATCH}, 'href')],
            prevent_initial_call=True
        )
        def generate_url(is_open, comp_id, real_url):
            print('copy url pressed')
            if not is_open:
                return 'Generating URL...'
            id_of_the_pressed_button_card = comp_id.get('id')
            pressed_card_dict = self.instances_dict.get(id_of_the_pressed_button_card)
            if pressed_card_dict is None:
                return SESSION_TIMEDOUT_STRING

            pressed_card_instance = pressed_card_dict.get('app_instance')
            pressed_card_instance.update_last_used_time()
            url_site = '/'.join(real_url.split('/')[:URL_SITE_NUM_OF_FIELDS])
            state_search = pressed_card_instance.generate_state_search_url()
            full_url = os.path.join(url_site, state_search)
            return full_url

class AppInstanceCreator():
    '''this class is a "man in the middle" between the instance manager and the application'''

    def __init__(self) -> None:
        self.database_vs_collection_file_path = DATABASE_VS_COLLECTION_FILE
        self.field_to_cards_name = FIELD_TO_CARD
        self.page_title = APP_TITLE

    def create_instance(self, **kwargs):
        
        app_instance = CardSelect(database_vs_collection_file_path=self.database_vs_collection_file_path, field_to_cards_name=self.field_to_cards_name, page_title=self.page_title, create_callbakes=False, **kwargs)
        return app_instance

class AppInstanceManager():
    '''this class manages all of the Card_Select instances'''
    def __init__(self) -> None:
        self.next_component_index = 1
        self.dict_of_instances_dicts = {}
        self.dynamic_callbacks = CreateAppDynamicCallbacks(instances_dict=self.dict_of_instances_dicts)
        self.instance_creator = AppInstanceCreator()
        self.child_instance_manager = self.create_child_instance_manager()

    def remove_parent_instance_children(self, parent_id):
        self.child_instance_manager.delete_instances_by_parent_id(parent_id)

    def get_instance_dict(self):
        return self.dict_of_instances_dicts

    def get_children_instances_dicts(self, parent_id):
        # retrieves the instances dictionary for the given parent id
        return self.child_instance_manager.get_parent_filtered_dict(parent_id)

    def print_count_of_active_instances(self):
        print(f'Current number of active instances: {len(self.dict_of_instances_dicts)}')

    def delete_timedout_instances(self):
        list_of_instances_to_delete = []

        # for each parent ID if all of its children instances have timedout request an instance deletation by parent ID from the child_instance_manager
        for instance_id, instance in self.dict_of_instances_dicts.items():
            instance_unused_time = time.time() - instance.get('app_instance').last_used
            children_instances_dicts = self.get_children_instances_dicts(parent_id=instance_id)
            if children_instances_dicts is not None:
                for child_instance_id, _ in children_instances_dicts.items():
                    child_instance_last_use = self.child_instance_manager.get_instance_last_use(child_instance_id)
                    child_instance_unused_time = time.time() - child_instance_last_use
                    print(child_instance_unused_time)
                    if child_instance_unused_time < INSTANCE_SESSION_TIMEOUT:
                        break
                else:
                    print(instance_unused_time)
                    if instance_unused_time >= INSTANCE_SESSION_TIMEOUT:
                        print(f'Instance {instance_id} timedout, deleting')
                        self.child_instance_manager.delete_instances_by_parent_id(instance_id)
                        list_of_instances_to_delete.append(instance_id)
            else:
                if instance_unused_time >= INSTANCE_SESSION_TIMEOUT:
                    print(f'Instance {instance_id} timedout, deleting')
                    list_of_instances_to_delete.append(instance_id)
        # after deleting the children instances, delete also the parent instance
        for instance_id in list_of_instances_to_delete:
            instance_to_delete_dict = self.dict_of_instances_dicts.pop(instance_id, None)
            if instance_to_delete_dict is not None:
                instance_to_delete = instance_to_delete_dict.get('app_instance')
                del instance_to_delete
        

    def create_child_instance_manager(self):
        # crates instance manager for the child application that imported at the start of this code
        instance_manager = ChildAppInstanceManager()
        return instance_manager

    def create_instance(self):
        # request an app instance creation from the App Creator and delete timedout instances
        self.delete_timedout_instances()
        app_instance = self.instance_creator.create_instance(children_application_manager=self.child_instance_manager, component_index=self.next_component_index)
        self.next_component_index += 1
        self.dict_of_instances_dicts[id(app_instance)] = {'app_instance':app_instance}
        return app_instance

if __name__ == '__main__':
    pass