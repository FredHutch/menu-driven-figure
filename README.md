# Menu Driven Figure
Render a figure based on user inputs from a configurable set of menus

## Background

Researchers often organize visual displays of information into units
of 'figures', each of which conveys a discrete unit of information.
While there are many tools available for generating figures, many of
the approaches which provide the greatest degree of flexibility also
require knowledge of programming languages like R or Python. While
these languages are extremely useful and worthwhile for all researchers,
we felt that there was a need for the ability to generate complex
figures that could be customized to some degree by an end-user.

In the menu-driven-figure approach, figures are rendered using the
interactive visualization framework provided by Plotly/Dash. The
user is presented with a set of menus or selection elements, and the
figure is rendered interactively based on the selections made in those
menus.

To make use of the `menu-driven-figure` project, a researcher with
experience in making figures with
[Python/Plotly](https://plotly.com/python/) will design a figure
which is rendered from `data` (read from a set of input files) and
`menus` (which are defined in the syntax of this project). The resulting
figure will be rendered as a web application which can then be viewed
by users who do not need to have any prior training in writing code.
Those users may then modify the selections of the menu and view the
modified figure which is presented as a result.

## Implementation

The `menu-driven-figure` codebase is a Python library which defines
the `MenuDrivenFigure` class. A `MenuDrivenFigure` is instantiated
using (1) a function for reading in `data` which will be used to render
a figure, (2) a definition of the set of `menus` which will be presented
to the user, and (3) a function which returns a figure based on the
contents of the `data` and `menus` data objects.

Additional functionality includes:
- Interpolation of values from `data` for menu options
- Conditional display of menus
- Customization with [bootstrap themes](https://www.bootstrapcdn.com/bootswatch/)
- Exporting vector-quality PDFs
- Save or load menu configurations to local files

## Usage

A minimal example of `MenuDrivenFigure` includes:
- 

```python

# Import the menu-driven-figure library
from menu_driven_figure import MenuDrivenFigure

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

# Instantiate the MenuDrivenFigure object
mdf = MenuDrivenFigure(
    data=data,
    menus=menus,
)

# Define the function used to render the plot, driven
# by the data and menu selections
@mdf.attach_plot()
def plot_iris_data(data, menus):

    # Subset the plotting data based on the dropdown menu
    plot_df = data.query(
        f"species == '{menus['display-species']}'"
    )

    # Make a figure using Plotly
    fig = px.scatter(
        # Plot the subset data
        plot_df,
        # Specify data for X and Y
        x="sepal_width",
        y="sepal_length",
        # Add a title based on the user input
        title=menus['plot-title']
    )

    # Return the figure
    return fig

# Launch the Dash/Flask app
app.run_server(
    host='0.0.0.0',
    port=8080,
    debug=True,
)
```
