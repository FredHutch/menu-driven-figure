#!/usr/bin/env python3

from copy import copy
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, ALL
from functools import lru_cache
import json
import plotly.graph_objects as go
from scipy import stats
from scipy import cluster


######################
# MENU DRIVEN FIGURE #
######################
class MenuDrivenFigure:
    """Object used to format a flask app rendering a figure based on inputs from the user."""

    def __init__(
        self,
        menus=None,
        data=None,
        function=None,
        param_menu_ncols=2,    # Number of columns in each parameter menu
        theme="LUMEN",
        title="Interactive Figure",
    ):

        # Save the configuration of the menu
        self.menus = menus

        # Save the provided data
        self.data = data

        # Save the plotting function
        self.plotting_function = function

        # Save the preferences for the display
        self.param_menu_ncols = param_menu_ncols
        self.theme = theme
        self.title = title

    def render_figure(self, selected_params):
        """Function to run the plotting function provided by the user."""

        return self.plotting_function(
            self.data,
            selected_params
        )

    def layout(self):
        """Define the layout of the app."""

        return html.Div(
            children=[

                # Save the current configuration
                self.hidden_div("current-settings"),

                # Save the configuration history
                self.hidden_div("past-settings"),
                self.hidden_div("future-settings"),

                # Toast used for notifications
                self.notification_toast(),

                # Navbar
                self.navbar(),

                # Parameter menu items
                self.parameter_menus(),

                # Plot area for the heatmap
                self.figure_display(),

            ]
        )

    def hidden_div(self, elem_id, children=None):
        # Return a hidden div
        return html.Div(
            children=children,
            id=elem_id,
            style=dict(display='none')
        )

    def notification_toast(self):
        # Set up a toast to use for notifications
        return dbc.Toast(
            header="Notification",
            id="notification-toast",
            dismissable=True,
            is_open=False,
            style=dict(
                position="fixed",
                top=100,
                right=10,
                width=350,
                zIndex=10,
            )
        )

    def navbar(self):

        return dbc.NavbarSimple(
            children=[
                dbc.Button(
                    param_menu["label"],
                    id=dict(
                        menu=f"menu-{menu_ix}",
                        elem="open-button"
                    ),
                    outline=True,
                    style=dict(
                        margin="5px"
                    )
                )
                for menu_ix, param_menu in enumerate(self.menus)
            ],
            brand="Annotated Heatmap",
            color="primary",
            dark=True,
        )

    def parameter_menus(self):

        return html.Div([
            # Make a collapse for each menu to drive show/hide
            dbc.Collapse(
                dbc.Card(
                    [dbc.Row(
                        [
                            dbc.Col(
                                [
                                    # Render each parameter element
                                    self.render_param_elem(param_item)
                                    for param_item in param_menu_column
                                    if param_item.get("show", True)
                                    # Also add a footer with "Close"
                                ]
                            )
                            for param_menu_column in self.split_param_columns(
                                param_menu["params"],
                                self.param_menu_ncols
                            )
                        ]
                    )] + self.param_menu_footer(
                        f"menu-{menu_ix}",
                    ),
                    body=True
                ),
                # Set the ID of the collapse based on the menu
                id=dict(
                    menu=f"menu-{menu_ix}",
                    elem="collapse"
                )
            )
            for menu_ix, param_menu in enumerate(self.menus)
        ])

    def split_param_columns(self, param_menu_list, ncols):

        # If there are no items in the list
        if len(param_menu_list) == 0:

            # Return an empty list
            return []

        # If there is only one item in the list
        elif len(param_menu_list) == 1:

            # Just return the list as a sublist
            return [param_menu_list]

        # If we are only supposed to return a single column
        elif ncols == 1:

            # Return a single column
            return [param_menu_list]

        # Otherwise
        else:

            # Split off the first 1/ncols of the list
            # Make sure to keep menu items together as needed

            # Find the first item of the next list
            next_list_ix = None
            for split_ix, i in enumerate(param_menu_list):

                # Skip the first item
                if split_ix == 0:
                    continue

                # If this item should be kept with the previous
                elif i.get("keep_with_previous", False):

                    # Then don't split the list here
                    continue

                # If the index position is 1/ncol of the total
                elif float(split_ix) >= len(param_menu_list) / float(ncols):

                    # Mark the position
                    next_list_ix = split_ix

                    # and stop here
                    break

        # If we found a place to make the split
        if next_list_ix is not None:

            # Return the list, added to the recursive join
            return [
                param_menu_list[:next_list_ix]
            ] + self.split_param_columns(
                param_menu_list[next_list_ix:],
                int(ncols - 1)
            )
        
        # Otherwise
        else:

            # Just return the whole list
            return [param_menu_list]

    def render_param_elem(self, param_item):
        """Render the selector element for a single parameter."""

        # Style applied to each element
        elem_style = dict(
            marginBottom="5px"
        )

        # ID to use for the input element
        elem_id = dict(input_elem=param_item["elem_id"])

        # Get the default value
        default_value = self.data.get(    # Check if the user provided --params
            "params", {}
        ).get(
            param_item["elem_id"],        # Check if this element has a value
            param_item.get("value", [])   # If not, check for a default config
        )                                 # Falling back to an empty list

        # First set up the element which will be used for selection by the user

        # Dropdown element
        if param_item["type"] == "dropdown":
            elem = dcc.Dropdown(
                options=[
                    dict(
                        label=i['label'],
                        value=i['value'],
                    )
                    for i in param_item["options"]
                    if i.get('show', True)
                ],
                value=default_value,
                style=elem_style,
                id=elem_id,
            )

        # Checkbox
        elif param_item["type"] == "checkbox":
            elem = dcc.Checklist(
                options=[
                    dict(
                        label="",
                        value="CHECKED"
                    )
                ],
                value=default_value,
                style=elem_style,
                id=elem_id,
            )

        # Selector
        elif param_item["type"] == "selector":

            elem = dcc.Dropdown(
                options=[
                    dict(
                        label=item_str,
                        value=item_str
                    )
                    for item_str in param_item["options"]
                ],
                value=default_value,
                multi=True,
                style=elem_style,
                id=elem_id,
            )

        # If the element is a slider
        elif param_item["type"] == "slider":

            min_val = param_item["min_val"]
            max_val = param_item["max_val"]

            # Mark the middle value
            mid_val = min_val + ((max_val - min_val) / 2.)

            elem = dcc.Slider(
                min=min_val,
                max=max_val,
                value=param_item["value"],
                marks={x: f"{x}{param_item.get('suffix', '')}" for x in [
                    int(min_val) if min_val == int(min_val) else min_val,
                    int(mid_val) if mid_val == int(mid_val) else mid_val,
                    int(max_val) if max_val == int(max_val) else max_val
                ]},
                step=param_item["step"],
                id=elem_id,
            )

        # If the element is an 'input'
        elif param_item["type"] == "input":

            elem = dbc.Input(
                id=elem_id,
                type=param_item["input_type"],
                value=param_item.get("value")
            )

        # We need to add support for this parameter type
        else:
            assert False, f"parameter type not recognized: {param_item['type']}"

        # Wrap the element up in a Collapse
        return dbc.Collapse(
            dbc.Form(
                dbc.FormGroup(
                    [
                        dbc.Label(
                            param_item["label"],
                            style=dict(
                                marginRight="5px",
                                marginLeft="15px" if param_item["type"] == "checkbox" else "0px"
                            )
                        ),
                        elem
                    ],
                    row=param_item["type"] == "checkbox"
                )
            ),
            id=f"{param_item['elem_id']}-collapse",
            is_open=True
        )

    def param_menu_footer(self, menu_id):
        """Specify the footer to place at the bottom of each param menu."""

        return [
            dbc.Button(
                "Hide Menu",
                id=dict(
                    menu=menu_id,
                    elem="close-button"
                )
            )
        ]

    def figure_display(self):
        """Return the element used to render the display."""
        return dbc.Card(
            dbc.Row(
                dbc.Col(
                    dbc.Spinner(
                        dcc.Graph(
                            id="rendered-figure"
                        )
                    ),
                    width=12
                )
            ),
            body=True
        )

    def decorate_callbacks(self, app):
        """Define the interactivity of the app."""

        # Show / Hide the parameter menus
        @app.callback(
            Output({"menu": ALL, "elem": "collapse"}, "is_open"),
            [
                Input({"menu": ALL, "elem": "open-button"}, "n_clicks"),
                Input({"menu": ALL, "elem": "close-button"}, "n_clicks"),
            ]
        )
        def open_close_parameter_menus(open_clicks, close_clicks):

            # Get the context which triggered the callback
            ctx = dash.callback_context

            # Get the element which triggered the callback
            trigger = ctx.triggered[0]['prop_id']

            # If there was no trigger
            if trigger == ".":

                # Close all menus
                open_menu = None

            else:
                # Get the ID of the button which was clicked
                trigger_id = json.loads(
                    trigger.rsplit(".", 1)[0]
                )

                # If the open button was clicked
                if trigger_id["elem"] == "open-button":

                    # Open the selected menu
                    open_menu = trigger_id["menu"]

                # Otherwise
                else:
                    # Close all menus
                    open_menu = None

            # Open the selected menu
            return [
                output_elem["id"]["menu"] == open_menu
                for output_elem in ctx.outputs_list
            ]

        # Changes to the parameters will change the URL
        @app.callback(
            Output("current-settings", "children"),
            [
                Input({"input_elem": ALL}, "value")
            ]
        )
        def update_url(input_elements):

            # Get the context which triggered the callback
            ctx = dash.callback_context

            # Make sure that each element has the required keys
            for elem in ctx.inputs_list[0]:
                for k in ['value', 'id']:
                    msg = f"Element missing key {k}: {json.dumps(elem)}"
                    assert k in elem, msg

            # Get the values which were selected by the user
            selected_params = {
                elem["id"]["input_elem"]: elem["value"]
                for elem in ctx.inputs_list[0]
            }

            # Format the values as key1=value1;key2=value2;
            return json.dumps(selected_params)

        # Render the figure based on changes to the URL
        @app.callback(
            [
                Output("rendered-figure", "figure"),
                Output("notification-toast", "is_open"),
                Output("notification-toast", "children"),
            ],
            [
                Input("current-settings", "children")
            ]
        )
        def figure_callback(selected_params):

            # Parse the parameters from the serialized JSON
            selected_params = self.parse_params(selected_params)

            # Try to render the figure
            try:

                # Generate a figure object
                fig = self.render_figure(selected_params)

                # If everything went well, just show the figure
                return fig, False, None

            # If there was an error
            except Exception as e:

                # Format a message to display
                msg = f"Unable to render -- {e}"

                # Show an empty figure, and open the notification
                return self.empty_plot(), True, msg

        # Apply the `show_if` directive to each menu item

        # Iterate over each parameter menu
        for param_menu in self.menus:

            # Iterate over each item in the list
            for param_item in param_menu["params"]:

                # If this item should not be shown
                if param_item.get("show", True) is False:

                    # Skip it
                    continue

                # If there is a "show_if" field
                if isinstance(param_item.get("show_if"), dict):

                    # There cannot also be a "hide_if" field
                    msg = "Cannot combine show_if and hide_if"
                    assert param_item.get("hide_if") is None, msg

                    # Get the target element
                    target_elem = param_item.get("show_if").get("target")
                    assert target_elem is not None

                    # Get the target value
                    target_value = param_item.get("show_if").get("value")
                    assert target_value is not None

                    # Set up the callback
                    self.add_show_if_callback(
                        app,
                        copy(param_item['elem_id']),
                        copy(target_elem),
                        copy(target_value)
                    )

                # If there is a "show_if" field
                elif isinstance(param_item.get("hide_if"), dict):

                    # Get the target element
                    target_elem = param_item.get("hide_if").get("target")
                    assert target_elem is not None

                    # Get the target value
                    target_value = param_item.get("hide_if").get("value")
                    assert target_value is not None

                    # Set up the callback
                    self.add_hide_if_callback(
                        app,
                        copy(param_item['elem_id']),
                        copy(target_elem),
                        copy(target_value)
                    )

    def add_show_if_callback(
        self,
        app,
        elem_id,
        target_elem,
        target_value
    ):

        @app.callback(
            Output(f"{elem_id}-collapse", "is_open"),
            [
                Input({"input_elem": target_elem}, "value")
            ]
        )
        def callback_show_param_if(obs_value):

            return obs_value in target_value

    def add_hide_if_callback(
        self,
        app,
        elem_id,
        target_elem,
        target_value
    ):

        @app.callback(
            Output(f"{elem_id}-collapse", "is_open"),
            [
                Input({"input_elem": target_elem}, "value")
            ]
        )
        def callback_hide_param_if(obs_value):

            return obs_value not in target_value


    @lru_cache(maxsize=128)
    def parse_params(self, selected_params):
        """Parse the JSON string."""

        return json.loads(selected_params)

    @lru_cache(maxsize=1)
    def empty_plot(self):
        return go.Figure(
            layout=dict(
                xaxis=dict(
                    visible=False
                ),
                yaxis=dict(
                    visible=False
                ),
                plot_bgcolor="rgba(0, 0, 0, 0)",
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
        )

    def run_server(
        self,
        debug=False,
        port=8050,
        host='0.0.0.0',
    ):
        """Launch a flask server rendering the supplied plot driven by menu selections."""

        # Assert that a plotting function has been attached
        msg = "Use attach_plot() to specify the plotting function"
        assert self.plotting_function is not None, msg


        ##################
        # SET UP THE APP #
        ##################

        # Dash app
        app = dash.Dash(
            __name__,
            external_stylesheets=[
                # Set the bootstrap theme
                dbc.themes.__dict__[self.theme]
            ],
        )

        app.title = self.title


        #####################
        # SET UP APP LAYOUT #
        #####################

        # Set up the layout of the app
        app.layout = self.layout


        ####################
        # SET UP CALLBACKS #
        ####################

        # Decorate the callback functions with @app.callback as appropriate
        self.decorate_callbacks(app)


        ##############
        # SET UP APP #
        ##############

        # Used for gunicorn execution
        server = app.server

        # Run the app
        app.run_server(
            host=host,
            port=port,
            debug=debug,
        )

