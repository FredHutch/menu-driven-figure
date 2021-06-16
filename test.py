#!/usr/bin/env python3

# Import the menu-driven-figure library
from menu_driven_figure.app import MenuDrivenFigure

# Import Plotly Express for plotting
import plotly.express as px

# Import seaborn in order to use its example data
import seaborn as sns

# Read in a set of data to be displayed
data = sns.load_dataset('iris')

# Define the menu items to be presented to the user
# The `menus` object is a list, which organizes the menus into tabs
menus = [
    # Second level is a dict, which defines the content of each menu tab
    # This example only has a single tab, but each additional dict
    # will add another tab to the menu display
    dict(
        # Label to be displayed at the top of the tab
        label="Customize Display",
        params=[
            dict(
                # ID used to access the value of this menu item
                elem_id="display-species",
                # Define the type of menu item
                type="dropdown",
                # Label displayed along this menu item
                label="Display Species",
                # Options to display in the dropdown menu
                options=[
                    # Each item in the list has a label and value
                    dict(
                        label='setosa',
                        value='setosa'
                    ),
                    dict(
                        label='versicolor',
                        value='versicolor'
                    ),
                    dict(
                        label='virginica',
                        value='virginica'
                    )
                ],
                # Default value
                value="virginica",
            ),
            # Allow the user to set a title to the plot
            dict(
                # ID used to access the value of this menu item
                elem_id="plot-title",
                # Label displayed along this menu item
                label="Plot Title",
                # Free-form input box
                type="input",
                # Input must be a string
                input_type="string",
                # Default value
                value="Iris Dataset",
            )
        ]
    )
]

# Define the function used to render the plot, driven
# by the data and menu selections
def plot_iris_data(data, selections):

    # Subset the plotting data based on the dropdown menu
    plot_df = data.query(
        f"species == '{selections['display-species']}'"
    )

    # Make a figure using Plotly
    fig = px.scatter(
        # Plot the subset data
        plot_df,
        # Specify data for X and Y
        x="sepal_width",
        y="sepal_length",
        # Add a title based on the user input
        title=selections['plot-title']
    )

    # Return the figure
    return fig

# Instantiate the MenuDrivenFigure object
mdf = MenuDrivenFigure(
    data=data,
    menus=menus,
    function=plot_iris_data,
)

# Launch the Dash/Flask app
mdf.run_server(
    host='0.0.0.0',
    port=8080,
    debug=True,
)