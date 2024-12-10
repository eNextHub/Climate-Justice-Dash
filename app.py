# %%

LOREM_IPSUM = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla bibendum, ligula quis efficitur tincidunt, nisl urna fermentum felis, quis maximus urna lorem quis augue. Curabitur ultrices viverra metus, a facilisis nulla tempor ac. Curabitur metus mi, eleifend ut volutpat vel, iaculis vitae nibh. Nullam convallis vulputate eleifend. Suspendisse congue purus a eleifend hendrerit. Vestibulum congue, purus vel mollis ornare, 
"""

# %%
import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
from EJ_indicator import read_dims, calc_EJ_index, DIMS
import io


import numpy as np

MARKS = np.arange(0, 1.1, 0.1).tolist()

HOVER_COLS = ["name_official", "Year", "Value"]


def load_all_data():
    indicators = []
    for k, v in DIMS.items():
        indicators.extend(v)

    return pd.concat([pd.read_csv(f"data/{i}.csv") for i in indicators])


dims = read_dims()
EJ = calc_EJ_index(
    dims,
)

# Load the dataset
try:
    df = load_all_data()  # Replace 'data.csv' with your file path
except Exception as e:
    print(f"Error loading CSV: {e}")
    df = pd.DataFrame(
        columns=[
            "Region",
            "Year",
            "Indicator",
            "Value",
            "continent",
            "UNregion",
            "name_official",
            "Normalized",
        ]
    )

REGIONS = [{"label": "World", "value": "World"}]
for val in df.continent.unique():
    REGIONS.append({"label": val, "value": val})
# %%
# Customize hover text
# df["Country"] = df.apply(
#     lambda row: f"Country: {row['name_official']}<br>Value: {row['Value']:.3f}", axis=1
# )

df["Country"] = df.apply(lambda row: f" {row['name_official']}", axis=1)


# %%
# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"],
    suppress_callback_exceptions=True,
)


# Extract unique indicators and years for dropdown
indicators = df["Indicator"].unique().tolist() if not df.empty else []
indicators.insert(0, "EJ Index")

EXPLANATIONS = {k: LOREM_IPSUM for k in indicators}

# App layout
app.layout = html.Div(
    [
        # Top Banner
        html.Div(
            className="study-browser-banner",
            children=[
                html.H2(className="h2-title", children="Environmental Justice Index"),
            ],
        ),
        html.Div(
            id="error-popup",
            children="Error: The sum of X and Y values cannot exceed 1.",
            style={
                "display": "none",  # Initially hidden
                "position": "fixed",
                "top": "20px",
                "right": "20px",
                "background-color": "red",
                "color": "white",
                "padding": "10px",
                "border-radius": "5px",
                "z-index": 1050,
                "box-shadow": "0 4px 8px rgba(0,0,0,0.2)",
            },
        ),
        # Dropdown for selecting the indicator
        html.Div(
            className="indicator-browser user-box box-shadow",
            children=[
                html.Div(
                    className="inline-elemnts",
                    children=[
                        html.Label("Select Indicator:", style={"font-weight": "bold"}),
                        dcc.Dropdown(
                            id="indicator-dropdown",
                            options=[
                                {"label": ind, "value": ind} for ind in indicators
                            ],
                            value=(
                                indicators[0] if len(indicators) > 0 else None
                            ),  # Default value
                            clearable=False,
                            className="dropdown",
                        ),
                        # Download button
                        html.Div(
                            [
                                html.Button(
                                    "Download Data",
                                    id="download-button",
                                    n_clicks=0,
                                    className="minimal-button",
                                ),
                                dcc.Download(id="download-data"),
                            ],
                        ),
                    ],
                ),
                html.Div(id="indicator-explanation", className="indicator-explanation"),
            ],
            style={"width": "50%", "margin": "auto"},
        ),
        html.Br(),
        # Store initial values for sliders
        dcc.Store(id="x-value-store", data=0.33),  # Default value for x-slider
        dcc.Store(id="y-value-store", data=0.33),  # Default value for y-slider
        dcc.Store(id="z-value-store", data=0.34),  # Default value for z-slider
        html.Div(
            className="map-holder",
            children=[
                html.Div(
                    children=[
                        dcc.Dropdown(
                            id="drop_continent",
                            clearable=False,
                            searchable=False,
                            options=REGIONS,
                            value="World",
                        ),
                        html.Div(
                            dcc.Graph(id="choropleth-map"),
                            className="map-container",  # Use CSS for styling
                            style={
                                "width": "100%",
                                "height": "100%",
                                "margin-top": "20px",
                            },  # Dynamic size
                        ),
                    ],
                ),
                # Sliders in a styled container
                html.Div(
                    id="sliders-container",
                    className="sliders-container",
                    children=[
                        html.Div(id="x-slider-container", className="slider-container"),
                        html.Div(id="y-slider-container", className="slider-container"),
                        html.Div(id="z-slider-container", className="slider-container"),
                    ],
                    style={"display": "none"},
                ),  # Initially hidden
            ],
        ),
    ]
)


# Callback to update choropleth map
@app.callback(
    Output("choropleth-map", "figure"),
    [
        Input("indicator-dropdown", "value"),
        Input("x-value-store", "data"),
        Input("y-value-store", "data"),
        Input("z-value-store", "data"),
        Input("drop_continent", "value"),
    ],
)
def update_choropleth(selected_indicator, x_value, y_value, z_value, continent):
    if not selected_indicator:
        return px.choropleth()  # Return an empty figure if no indicator is selected

    # Filter data based on the selected indicator

    if selected_indicator == "EJ Index":
        filtered_df = calc_EJ_index(
            dims,
            {
                "Common goods": x_value,
                "Human rights": y_value,
                "Sustainability": z_value,
            },
        )

        filtered_df["Country"] = filtered_df.apply(
            lambda row: f"{row['name_official']}", axis=1
        )
        HOVER_COLS = []

    else:
        filtered_df = df[df["Indicator"] == selected_indicator]
        HOVER_COLS = ["Value"]

    if filtered_df.empty:
        return px.choropleth()  # Return an empty figure if no data matches

    hover_data = {}
    for col in filtered_df.columns:
        if col in HOVER_COLS:
            hover_data[col] = True
        else:
            hover_data[col] = False
    # Generate choropleth map

    if continent != "World":
        filtered_df = filtered_df.loc[filtered_df.continent == continent]
    fig = px.choropleth(
        filtered_df,
        locations="Region",  # ISO3 country code column
        color="Normalized",  # Data to color map by
        animation_frame="Year",  # Animation by year
        projection="natural earth",
        hover_data=hover_data,
        hover_name="name_official",
        color_continuous_scale=[
            (0.0, "red"),  # Red at 0
            (0.5, "yellow"),  # Yellow at 0.5
            (1.0, "green"),  # Green at 1
        ],
    )
    # Lock color bar range from 0 to 1 (fixed color scale)
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Normalized Value",  # Title for the color bar
            tickvals=[0, 0.25, 0.5, 0.75, 1],  # Intervals for ticks
            ticktext=["0", "0.25", "0.5", "0.75", "1"],  # Corresponding labels
            tickmode="array",  # Use `tickvals` and `ticktext` for ticks
            lenmode="pixels",  # Set the color bar length in pixels
            len=300,  # Length of the color bar
        ),
        coloraxis=dict(
            cmin=0,  # Set fixed minimum value for color scale
            cmax=1,  # Set fixed maximum value for color scale
        ),
        hovermode="x unified",
    )

    fig.update_layout(
        autosize=True,
        margin=dict(l=1, r=1, b=1, t=1, pad=4, autoexpand=True),
        width=1300,
        height=800,
    )

    return fig


# Callback to handle data download
@app.callback(
    Output("download-data", "data"),
    Input("download-button", "n_clicks"),
    State("indicator-dropdown", "value"),
    State("x-value-store", "data"),
    State("y-value-store", "data"),
    State("z-value-store", "data"),
    prevent_initial_call=True,
)
def download_data(n_clicks, selected_indicator, x_value, y_value, z_value):
    """Prepare and return the data for download."""
    # Check the selected indicator and prepare data
    if selected_indicator == "EJ Index":
        filtered_df = calc_EJ_index(
            dims,
            {
                "Common goods": x_value,
                "Human rights": y_value,
                "Sustainability": z_value,
            },
        )
    else:
        filtered_df = df[df["Indicator"] == selected_indicator]

    # Use dcc.send_data_frame directly with the DataFrame
    return dcc.send_data_frame(
        filtered_df.to_csv,  # Function to convert DataFrame to CSV
        filename=f"{selected_indicator}_data.csv",  # File name
        index=False,  # Don't include index in the CSV
    )


@app.callback(
    [
        Output("x-slider-container", "children"),
        Output("y-slider-container", "children"),
        Output("z-slider-container", "children"),
    ],
    [
        Input("indicator-dropdown", "value"),
        Input("x-value-store", "data"),
        Input("y-value-store", "data"),
    ],
)
def render_sliders(selected_indicator, x_value, y_value):
    if selected_indicator == "EJ Index":

        if (x_value + y_value) >= 1:
            if x_value >= y_value:
                y_value = 1 - x_value
            else:
                x_value = 1 - y_value

        # Calculate z-slider value dynamically
        z_value = 1 - x_value - y_value

        marks = {k: f"{round(k,1)}" for k in MARKS}

        # Return slider components with updated values
        return (
            html.Div(
                [
                    html.Label(
                        f"Common goods: {x_value:.2f}", style={"font-weight": "bold"}
                    ),
                    dcc.Slider(
                        id="x-slider",
                        min=0,
                        max=1,
                        step=0.01,
                        value=x_value,
                        marks=marks,
                    ),
                ]
            ),
            html.Div(
                [
                    html.Label(
                        f"Human rights: {y_value:.2f}", style={"font-weight": "bold"}
                    ),
                    dcc.Slider(
                        id="y-slider",
                        min=0,
                        max=1,
                        step=0.01,
                        value=y_value,
                        marks=marks,
                    ),
                ]
            ),
            html.Div(
                [
                    html.Label(
                        f"Sustainability: {z_value:.2f}", style={"font-weight": "bold"}
                    ),
                    dcc.Slider(
                        id="z-slider",
                        min=0,
                        max=1,
                        step=0.01,
                        value=z_value,
                        marks=marks,
                        disabled=True,
                    ),
                ]
            ),
        )
    return None, None, None  # If not 'EJ Index', return None for sliders


@app.callback(
    [
        Output("x-value-store", "data"),
        Output("y-value-store", "data"),
        Output("z-value-store", "data"),
    ],
    [Input("x-slider", "value"), Input("y-slider", "value")],
)
def update_slider_values(x_value, y_value):
    # Calculate z-value dynamically based on x and y
    z_value = 1 - x_value - y_value

    # Return updated values to the store
    return x_value, y_value, z_value


@app.callback(
    Output("sliders-container", "style"), Input("indicator-dropdown", "value")
)
def toggle_sliders(selected_indicator):
    """Show sliders only if 'EJ Index' is selected."""
    if selected_indicator == "EJ Index":
        return {"display": "block", "width": "70%", "margin": "auto"}
    return {"display": "none"}


@app.callback(
    Output("indicator-explanation", "children"), Input("indicator-dropdown", "value")
)
def update_explanation(selected_indicator):
    if not selected_indicator:
        return "Please select an indicator to view its explanation."
    return EXPLANATIONS.get(
        selected_indicator, "Explanation not available for the selected indicator."
    )


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
