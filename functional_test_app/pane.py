import os, sys
import json
import time
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback, no_update
from dash.dependencies import MATCH

import plotly.graph_objs as go
import plotly.express.colors as px_colors
from plotly.validators.scatter.marker import SymbolValidator
# sys.path.insert(0,"/")
DASH_APPS_DIR = os.getenv('DASHBOARD_APPS_DIR')
DASH_APPS_CONTAINED_DIR = f'{DASH_APPS_DIR}/..'
print(DASH_APPS_CONTAINED_DIR)
from dashboard_apps.functional_test_app.dataframe import FunctionalTestDataFrame
from dashboard_apps.database.mongodb_dashboard import Collection

def get_symbols_list():
    symbols = []
    for i in range(0,len(SymbolValidator().values),12):
        symbols.append(SymbolValidator().values[i])
    return symbols

VERSION = 'v1.3.3'
SYMBOLS = get_symbols_list()
COLORS = px_colors.qualitative.Dark24 + px_colors.qualitative.Prism
INFO_COLLECTION_FILE = os.path.join(DASH_APPS_CONTAINED_DIR,"dashboard_apps/functional_test_app/info_collections.json")
RESTYLEDATA_VALUES = 0
RESTYLEDATA_INDEXES = 1

# Dynamic components ids (names)
DYNAMIC_DOWNLOAD = 'dynamic_download'
DYNAMIC_EXPORT_BUTTON = 'dynamic_export_button'
DYNAMIC_SERIAL_DROPDOWN = 'serial_dropdown'
DYNAMIC_PRODUCT_DROPDOWN = 'product_dropdown'
DYNAMIC_TEST_PASS_CHECKBOX = 'pass_checkbox'
DYNAMIC_MAIN_PLOT = 'main_plot'
DYNAMIC_STORE_VISIBLE_STEPS = 'store_visible_steps'

class FunctionalTestPane():
    def __init__(self, main_dataframe:pd.DataFrame, test_name:str, info_collections_dict:dict=None, component_index=-1, initial_configure=None, create_callbacks=True) -> None:
        self.test_name = test_name
        self.df_object = FunctionalTestDataFrame(main_dataframe)

        if info_collections_dict is not None:
            self.info_collections_dict = info_collections_dict
            self.systems_collection = self.get_system_collection()
        self.initial_configure = initial_configure
        self.test_steps = self.df_object.get_test_step_fields()
        self.version = VERSION
        self.last_used = time.time()
        #################### component IDs #######################
        self.download_id = {'type': DYNAMIC_DOWNLOAD, 'index': component_index, 'id':id(self)}
        self.button_id = {'type': DYNAMIC_EXPORT_BUTTON, 'index': component_index, 'id':id(self)}
        self.serial_dropdown_id = {'type': DYNAMIC_SERIAL_DROPDOWN, 'index': component_index, 'id':id(self)}
        self.type_dropdown_id = {'type': DYNAMIC_PRODUCT_DROPDOWN, 'index': component_index, 'id':id(self)}
        self.test_pass_id = {'type': DYNAMIC_TEST_PASS_CHECKBOX, 'index': component_index, 'id':id(self)}
        self.plot_id = {'type': DYNAMIC_MAIN_PLOT, 'index': component_index, 'id':id(self)}
        self.store_visible_steps_id = {'type': DYNAMIC_STORE_VISIBLE_STEPS, 'index': component_index, 'id':id(self)}
        ##########################################################
        self.card_state = {} # contains current card selections
        self.body_content = []
        self.fields_to_set = [] # fields to set with initial configs
        self.set_initial_values()
        if create_callbacks:
            self.create_callbacks()
        self.card = self.create_pane()

    def get_last_used_time(self):
        return self.last_used

    def update_last_used_time(self):
        self.last_used = time.time()

    def set_initial_values(self):
        #parse the initial configurations and set the fields_to_set

        if self.initial_configure is not None:
            for values in self.initial_configure:
                if values != '[]':
                    field = values.split('[')[0]
                    self.fields_to_set.append(field)
                    self.card_state[field] = values.split(field)[-1]
                

    def get_card_state(self):
        return self.card_state

    def get_df_object(self):
        return self.df_object

    def get_system_collection(self):
        # retrieves the system information collection from the info_collections_dict
        system_collection = self.info_collections_dict.get("systems_info")
        return system_collection

    def get_system_accessories(self, serial):
        # retrieves system accessories by serial number
        system_document = self.systems_collection.find_one(field='_id', value=serial)
        if system_document is not None:
            return system_document.get('acrs')
        return ['N/A']


    def create_callbacks(self):

        @callback(
            Output(self.download_id, "data"),
            Input(self.button_id, "n_clicks"),
            prevent_initial_call=True
        )
        def export_PB_callback(n_clicks):
            return dcc.send_data_frame(self.df_object.get_dataframe().to_csv, f"{self.test_name}_data.csv")
        
        
        @callback(
            Output(self.plot_id, "figure"),
            Input(self.serial_dropdown_id, "value"),
            prevent_initial_call=True
        )
        def update_plot_callback(serial_number):

            print('serial selected')
            filtered_df = self.df_object.filter_by_field_n_value(field='serial_number', value=serial_number)
            portia_versions = self.df_object.get_portia_versions(filtered_df)
            plot_data = [go.Scatter(x=portia_versions, y=filtered_df[step].to_list()) for step in self.test_steps]
            plot = go.Figure(data=plot_data, layout=go.Layout(height=700))

            return plot


    def get_dataframe(self):
        return self.df_object.get_dataframe()

    def get_name(self):
        return self.test_name

    def get_card(self):
        return self.card

    def create_pane(self) -> dbc.Card:
        # create the pane with all of the needed components and creates the pane layout
        self.body_content.append(self.create_store_visible_steps())
        self.body_content.append(self.create_download())
        self.body_content.append(self.create_header(self.test_name, 3))
        self.body_content.append(self.create_graph_section())
        self.body_content.append(self.create_export_PB())

        self.card_content = [
                dbc.CardBody(self.body_content, id=f'{id(self)}_card_body', style={"outline": "solid purple", "border": "none","margin-bottom": "15px"}),
            ]
        card = dbc.Card(self.card_content, style={"width": "auto"})
        return card

    def create_store_visible_steps(self):
        visible_steps = ''
        if 'steps' in self.fields_to_set:
            print('set initial steps')
            card_state = self.get_card_state()
            visible_steps = str(card_state.get('steps')).strip('[]').translate({ord("'"): None}).replace(',',';')
            self.fields_to_set.remove('steps')
            
        return dcc.Store(self.store_visible_steps_id, data=visible_steps)

    def create_download(self):
        # creates download element, this element needs to be created only once and then many components can use it
        return dcc.Download(id=self.download_id)

    def create_text(self, text:str, size:int=100, color:str=None, align:str=None):
        # add plain text
        style={'font-size':f'{size}%', 'color':color, 'text-align':align}
        return html.Plaintext(children=text, style=style)

    def create_header(self, text:str, size:int=3, color:str=None, align:str=None):
        # add header
        style={'color':color, 'text-align':align}
        return {
            1: html.H1(children=text, className=text, style=style),
            2: html.H2(children=text, className=text, style=style),
            3: html.H3(children=text, className=text, style=style),
            4: html.H4(children=text, className=text, style=style),
            5: html.H5(children=text, className=text, style=style),
            6: html.H6(children=text, className=text, style=style)
        }[size]

    def create_graph_section(self):
        # the graph section is the body area in the card, all the components that are in the same possition level as the graph
        graph_section_content = []
        graph_section_content.append(html.Div([self.create_graph()], style={'width': '84%', 'display': 'inline-block'}))
        graph_section_content.append(html.Div([
                                                self.create_line_breaks(5),
                                                self.create_header('Systems', 5, 'blue'),
                                                self.create_text(text='* Hover with the cursor for\n  additional system information', size=90),
                                                self.create_sn_dropdown(),
                                                self.create_line_breaks(2),
                                                html.Div([self.create_header('Filter Systems by:', 5, 'blue'),
                                                self.create_header('Product Type', 6, 'blue'),
                                                self.create_pt_dropdown()], style={"border":"1px black solid", 'padding': '6px 6px 6px 8px'}),
                                                self.create_line_breaks(1),
                                                self.create_header('Filter results', 5, 'blue'),
                                                self.create_results_filter_checkbox()
                                                ],
                                                style={'width': '16%', 'float': 'right', 'display': 'inline-block', 'font-size':'80%'}))
                                                

                                                

        return html.Div(graph_section_content)

    def create_line_breaks(self, quantity=1):
        # adds line break
        return html.Div([html.Br()]*quantity)

    def create_graph(self):
        # create the main card graph
        layout = go.Layout(
            height=700,
            xaxis=dict(
                title="Version",
                linecolor="#BCCCDC",  # Sets color of X-axis line
                showgrid=False  # Removes X-axis grid lines
            ),
            yaxis=dict(
                title="Time [sec]",  
                linecolor="#BCCCDC",  # Sets color of Y-axis line
                showgrid=False,  # Removes Y-axis grid lines
            ),
            legend=dict(
                uirevision=True
            )
        )

        config = {'displaylogo': False, 'modeBarButtonsToRemove': ['zoomIn2d', 'zoomOut2d', 'resetScale2d'] }

        plot = go.Figure(data=[], layout=layout)
        return dcc.Graph(id=self.plot_id, figure=plot, config=config)

    def create_sn_dropdown(self):
        # creates serial number dropdown
        values = None
        if 'systems' in self.fields_to_set:
            systems = self.card_state.get('systems')
            if systems != '[]':
                values = systems.strip('[]').split(',')
        new_line = '\n  '
        options = [{'label': f'{serial} - {product}', 'value': serial, 'title': f'Accessories:{new_line}{new_line.join(self.get_system_accessories(serial))}'}
        for serial, product in self.df_object.get_sn_pt_list()]
        element = dcc.Dropdown(
            id=self.serial_dropdown_id,
            options=options,
            value=values,
            multi=True,
            placeholder="Select System"
        )
        return element

    def create_pt_dropdown(self):
        # creates product type dropdown
        element = dcc.Dropdown(
            id=self.type_dropdown_id,
            options=[{'label': product, 'value': product} for product in self.df_object.get_pt_list()],
            clearable=True,
            multi=True,
            placeholder="Select Product"
        )
        return element

    def create_export_PB(self):
        return dbc.Button("Download CSV", id=self.button_id, n_clicks=0, style={'float': 'left'})

    def create_results_filter_checkbox(self):
        element = dcc.Checklist(
            id=self.test_pass_id,
            options=[
                {'label': 'Passed tests', 'value': 'test_pass'}],
            value=['test_pass']
        )
        return element

class AppDynamicCallbacks():
    '''This Class creates Dynamic Callbacks for the Dash elements.
    Dynamic Callbacks are mandatory for controling elements that are currently not exist and will be created in the future.'''
    def __init__(self, instances_dict) -> None:
        self.instances_dict = instances_dict

        self.create_dynamic_callback()


    def create_dynamic_callback(self):
        print('create pane dynamic callback')
        @callback(
            Output({'type': DYNAMIC_DOWNLOAD, 'id':MATCH, 'index': MATCH}, 'data'),
            Input({'type': DYNAMIC_EXPORT_BUTTON, 'id':MATCH, 'index': MATCH}, 'n_clicks'),
            State({'type': DYNAMIC_EXPORT_BUTTON, 'id':MATCH, 'index': MATCH}, 'id'),
            prevent_initial_call=True
        )
        def export_csv(_, comp_id):
            print("export_csv pressed")

            id_of_the_pressed_button_card = comp_id.get('id')
            pressed_card_instance = self.instances_dict.get(id_of_the_pressed_button_card).get('app_instance')
            pressed_card_instance.update_last_used_time()
            card_title = pressed_card_instance.get_name()
            dataframe = pressed_card_instance.get_dataframe()
            return dcc.send_data_frame(dataframe.to_csv, f"{card_title}_data.csv")

        @callback(
            Output({'type': DYNAMIC_STORE_VISIBLE_STEPS, 'id':MATCH, 'index': MATCH}, 'data'),
            Input({'type': DYNAMIC_MAIN_PLOT, 'id':MATCH, 'index': MATCH}, 'restyleData'),
            State({'type': DYNAMIC_STORE_VISIBLE_STEPS, 'id':MATCH, 'index': MATCH}, 'id'),
            State({'type': DYNAMIC_STORE_VISIBLE_STEPS, 'id':MATCH, 'index': MATCH}, 'data'),
            
            prevent_initial_call=True
        )
        def save_legend_state(legend_last_change, comp_id, visible_steps):
                        
            id_of_the_pressed_button_card = comp_id.get('id')
            pressed_card_instance = self.instances_dict.get(id_of_the_pressed_button_card).get('app_instance')
            pressed_card_instance.update_last_used_time()

            if visible_steps is None:
                visible_steps = ''

            if legend_last_change is not None:
                all_test_steps = pressed_card_instance.test_steps
                step_visibility_values = legend_last_change[RESTYLEDATA_VALUES].get('visible')
                step_index_list = legend_last_change[RESTYLEDATA_INDEXES]
                for index, step_index in enumerate(step_index_list):
                    if step_index >= len(all_test_steps):
                        break
                    if step_visibility_values[index] is True and all_test_steps[step_index] not in visible_steps:
                        visible_steps+=f';{all_test_steps[step_index]}'
                    elif step_visibility_values[index] == 'legendonly' and all_test_steps[step_index] in visible_steps:
                        visible_steps = visible_steps.replace(all_test_steps[step_index],'')

                visible_steps = visible_steps.replace(';;', ';').strip(';')
                pressed_card_instance.card_state['steps'] = visible_steps.split(';')
                return visible_steps
            return no_update

        @callback(
            
            Output({'type': DYNAMIC_MAIN_PLOT, 'id':MATCH, 'index': MATCH}, 'figure'),
            Input({'type': DYNAMIC_SERIAL_DROPDOWN, 'id':MATCH, 'index': MATCH}, 'value'),
            Input({'type': DYNAMIC_TEST_PASS_CHECKBOX, 'id':MATCH, 'index': MATCH}, 'value'),
            State({'type': DYNAMIC_STORE_VISIBLE_STEPS, 'id':MATCH, 'index': MATCH}, 'data'),
            State({'type': DYNAMIC_SERIAL_DROPDOWN, 'id':MATCH, 'index': MATCH}, 'id'),
            # prevent_initial_call=True
        )
        def update_plot(serial_number, pass_filter, visible_steps, comp_id):
            print('serial selected')
            id_of_the_pressed_button_card = comp_id.get('id')
            pressed_card_instance = self.instances_dict.get(id_of_the_pressed_button_card).get('app_instance')
            pressed_card_instance.update_last_used_time()

            if not serial_number:
                pressed_card_instance.card_state['systems'] = []
                plot = go.Figure(layout=go.Layout(height=700))
                return plot
            
            if visible_steps is not None:
                visible_steps_list = visible_steps.split(';')
            else:
                visible_steps_list = []
            
            instance_dataframe_obj = pressed_card_instance.get_df_object()
            test_steps = pressed_card_instance.test_steps
            
            filtered_df = instance_dataframe_obj.filter_by_field_n_value(field='serial_number', value=serial_number)
            
            if pass_filter:
                filtered_df = instance_dataframe_obj.filter_by_field_n_value(field="test_pass", value=True, alternative_dataframe=filtered_df)
            x_axis_data = instance_dataframe_obj.get_portia_versions(alternative_dataframe=filtered_df)
            plot = go.Figure(layout=go.Layout(height=700))
            plot_mode = 'lines+markers'
            total_step_count = 0
            
            for index, serial in enumerate(serial_number):
                one_serial_df = instance_dataframe_obj.init_steps_values_by_serial_numbers(serial_number=serial, fields_to_update=test_steps, alternative_dataframe=filtered_df)
                
                for step in test_steps:
                    step_visibility = 'legendonly'
                    if step in visible_steps_list:
                        step_visibility = True
                    total_step_count+=1
                    if total_step_count < len(COLORS):
                        line_color = COLORS[total_step_count]
                    else:
                        line_color = None
                    y_axis_data = one_serial_df[step].to_list()
                    plot.add_trace(go.Scatter(x=x_axis_data, y=y_axis_data, mode=plot_mode, line = dict(color=line_color), marker_symbol=SYMBOLS[index], marker_size=8, marker_line_width=1,
                        name=serial,
                        legendgroup=f"{step}_group", legendgrouptitle_text=step,
                        visible=step_visibility,
                        text=[step]*len(x_axis_data),
                        hovertemplate='%{text}<br>Version: %{x}<br>Time: %{y} [sec]'))

            plot.update_yaxes(
                title_text = "Time [sec]",
                title_standoff = 25
                )
            pressed_card_instance.card_state['systems'] = serial_number
            return plot

        @callback(
            Output({'type': DYNAMIC_SERIAL_DROPDOWN, 'id':MATCH, 'index': MATCH}, 'options'),
            Input({'type': DYNAMIC_PRODUCT_DROPDOWN, 'id':MATCH, 'index': MATCH}, 'value'),
            State({'type': DYNAMIC_PRODUCT_DROPDOWN, 'id':MATCH, 'index': MATCH}, 'id'),
            prevent_initial_call=True
        )
        def filter_sn_by_product_type(product_type, comp_id):
            print('product selected')
            
            id_of_the_pressed_button_card = comp_id.get('id')
            pressed_card_instance = self.instances_dict.get(id_of_the_pressed_button_card).get('app_instance')
            pressed_card_instance.update_last_used_time()
            instance_df_object = pressed_card_instance.get_df_object()

            if not product_type:
                updated_sn_list = instance_df_object.get_sn_pt_list()
            else:
                filtered_by_pt_df = instance_df_object.filter_by_field_n_value(field='Product Type', value=product_type)
                updated_sn_list = instance_df_object.get_sn_pt_list(alternative_dataframe=filtered_by_pt_df)
            new_line = '\n  '
            filtered_options = [{'label': f'{serial} - {product}', 'value': serial, 'title': f'Accessories:{new_line}{new_line.join(pressed_card_instance.get_system_accessories(serial))}'} for serial, product in updated_sn_list]

            return filtered_options


class AppInstanceCreator():
    '''this class is a "man in the middle" between the instance manager and the application'''
    def __init__(self) -> None:
        self.info_collections_file_path = INFO_COLLECTION_FILE
        self.info_collections_dict = self.create_info_collections_dict()

    def _read_collections_file(self):
        # reads json collection file
        with open(self.info_collections_file_path) as json_file:
            return json.load(json_file)

    def create_info_collections_dict(self):
        # reads the database vs collection file and retrieves info collection dictionary
        # this dictionary contains collections with additional information
        collection_file_dict = self._read_collections_file()
        info_collections_dict = {}
        for database in collection_file_dict.get("databases"):
            for collection in database.get("collections"):
                collection_type=collection.get("type")
                info_collections_dict[collection_type] = Collection(database_name=database.get("name"), collection_name=collection.get("name"))
        return info_collections_dict


    def create_instance(self, main_collection:Collection, test_name:str, component_index:int, initial_configure:list):
        test_document = self.get_test_document(main_collection, test_name)
        test_dataframe = self.create_test_dataframe(main_collection, test_name, test_document)
        app_instance = FunctionalTestPane(main_dataframe=test_dataframe, test_name=test_name, info_collections_dict=self.info_collections_dict, component_index=component_index, initial_configure=initial_configure, create_callbacks=False)
        return app_instance

    def get_all_test_fields(self, test_document):
        return test_document.keys()

    def get_test_document(self, main_collection, test_name) -> dict:
        # retrieves the test document from the database
        test_document = main_collection.find_last('test_name', test_name)
        return test_document

    def find_timing_fields(self, test_document) -> list:
        # retrieves all fields in the test that contains the word 'timing'
        # ****takes some time to run****
        all_test_fields = self.get_all_test_fields(test_document)
        timing_objects = [field for field in all_test_fields if 'timing' in field]
        return timing_objects

    def get_time_steps(self, test_document, timing_fields:list) -> dict:
        # get list of timing fields and retrieves a dictionary of all the step fields they contains {key=timing_field, value=[<list_of_steps>]}
        time_steps = {}
        for field in timing_fields:
            if field is not None:
                steps_list = test_document.get(field)
                if steps_list is not None:
                    time_steps[field] = list(test_document.get(field).keys())
        return time_steps

    def create_test_dataframe(self, main_collection, test_name, test_document):
        # creates the test main dataframe
        timing_fields = ['steps_timing', 'upgrade_timing'] # used to save time for generic timing fields use self.find_timing_fields()
        time_steps_dict = self.get_time_steps(test_document, timing_fields)

        groupby_dict = { "_id": {
                "serial_number" : "$controllers.PORTIA.serial_number",
                "portia_version": "$controllers.PORTIA.version",
                "ciBuild": "$controllers.PORTIA.version.ciBuild",
                },

                "portia_version" : {"$first" : "$controllers.PORTIA.version"},
                "serial_number" : {"$first" : "$controllers.PORTIA.serial_number"},
                "Product Type" : {"$first" : "$Product Type"},
                "test_pass" : {"$first" : "$test_pass"}
                }
        for field, value in time_steps_dict.items():
            for step in value:
                groupby_dict[f'avg_{step}'] = {"$avg" : f"${field}.{step}"}

        pipeline = [{"$match" : {"test_name" : test_name}},
                    {"$group": groupby_dict},
                    {"$sort": {"_id.portia_version" : 1}}
                    
        ]
        agg = main_collection.get_aggregated_dataframe(pipeline)
        
        dataframe = pd.DataFrame(agg)
        ######## Dataframe handling #########
        dataframe = dataframe.drop('_id', 1)
        dataframe["portia_version"] = dataframe["portia_version"].apply(lambda x: x[0])
        dataframe["serial_number"] = dataframe["serial_number"].apply(lambda x: x[0])
        #####################################
        return dataframe

class AppInstanceManager():
    '''this class manages all of the FunctionalTestPane instances'''
    def __init__(self) -> None:
        self.dict_of_instances_dicts = {}
        self.dynamic_callbacks = AppDynamicCallbacks(instances_dict=self.dict_of_instances_dicts)
        self.instance_creator = AppInstanceCreator()

    def delete_instance(self, instance_dict):
        # deletes an instance for a given instance dictionary 
        try:
            instance = instance_dict.get('app_instance')
            collection_object = instance_dict.get('collection')
            del instance
            del collection_object
        except AttributeError:
            print("Can't delete instance, not exists")

    def delete_instances_by_parent_id(self, parent_id):
        # retrieves the parent instance dictionary (children instances that belong to the specific instance) and deletes them all
        instances_to_delete = []
        parent_filtered_dict = self.get_parent_filtered_dict(parent_id)
        for instance_id, instance_dict in parent_filtered_dict.items():
            instances_to_delete.append(instance_id)

        for instance_id in instances_to_delete:
            parent_filtered_dict.pop(instance_id, None)
            self.delete_instance(instance_dict)

    def get_instance_dict(self):
        return self.dict_of_instances_dicts

    def get_parent_filtered_dict(self, parent_id):
        # returns a filtered dict_of_instances_dicts by parent_id, this we can manage all instances that was created by a specific parent instance
        instances_sub_dicts = self.dict_of_instances_dicts.items()
        filtered_dictionary = {key: value for key, value in instances_sub_dicts if value['parent_id'] == parent_id}
        if filtered_dictionary == {}:
            return None
        return filtered_dictionary

    def get_instance_last_use(self, instance_id):
        instance = self.dict_of_instances_dicts.get(instance_id).get('app_instance')
        instance_last_used = instance.get_last_used_time()
        return instance_last_used

    def create_instance(self, parent_id:id, main_collection:Collection, test_name:str, initial_configure:list):
        component_index = len(self.dict_of_instances_dicts)+1
        app_instance = self.instance_creator.create_instance(main_collection=main_collection, test_name=test_name, component_index=component_index, initial_configure=initial_configure)
        self.dict_of_instances_dicts[id(app_instance)] = {'parent_id':parent_id, 'app_instance':app_instance, 'collection':main_collection, 'field_name':test_name}
        return app_instance

if __name__ == "__main__":
    instance = AppInstanceCreator()
    test_name = "SeBus"
    function_tests_collection = Collection("pipeline_regression", "01_function_tests")
    test_document = instance.get_test_document(function_tests_collection, test_name)
    test_dataframe = instance.create_test_dataframe(function_tests_collection, test_name, test_document)

    print(test_dataframe)