
import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
from EJ_indicator import read_dims, calc_EJ_index, DIMS
import io
import numpy as np
import json
import plotly.graph_objects as go
import math




DESCRIPTIONS = {
    "Red List Index": """
    The ** Red List Index ** measures trends in species' extinction risk on a scale from 0 to 1, where 1 means no species are at risk, and 0 means all species are extinct. It includes mammals, birds, cycads, amphibians, and corals, with regional and national indices weighted by species' distribution. Linked to SDG Goal 15, specifically Target 15.5, it tracks progress in halting biodiversity loss, reducing habitat degradation, and preventing species extinction, aligning with efforts to protect and restore ecosystems.
""",
    "Air Pollution Mortality": """
SDG Indicator 3.9.1 measures the age-standardized **mortality** rate (per 100,000 population) caused by household and **ambient air pollution**. It highlights the health impact of air quality, tracking deaths linked to exposure to harmful pollutants. This indicator supports SDG Goal 3 by monitoring progress in reducing preventable deaths from environmental health risks, emphasizing the need for clean air initiatives to improve public health. 

*Note: Due to data limitations, values for 2007 are approximated using 2010 data, and values for 2022 are approximated using 2019 data*.
""",
    "Education Index": """
The **education component of the Human Development Index (HDI)** measures the average and expected years of schooling to assess both current achievements and future potential in education. Average years of schooling reflect the education level of adults aged 25 and older, while expected years of schooling estimate the total education a child entering school is likely to receive based on current enrollment rates. This indicator provides a comprehensive view of educational attainment and its contribution to human development.
""",
    "Citizen Carbon Footprint": """
The **per capita consumption-based CO₂ emissions** measures the CO₂ emissions tied to the goods and services consumed by the average person in a country, rather than where those goods are produced. It adjusts production-based emissions by subtracting emissions from exports and adding those from imports, providing a clear picture of a citizen's carbon impact. This excludes emissions from land use, deforestation, and international aviation or shipping, focusing on consumption-related emissions.
""",
    "Waste Management": """
**Waste Management** measures a country's commitment to sustainable waste practices by combining three components: compliance with two international conventions under SDG 12 (the Basel Convention on hazardous waste and the Stockholm Convention on persistent organic pollutants), each contributing 25% to the score, and the percentage of municipal waste recycled, accounting for 50%. Ratification of each convention gives a country 100 points, while non-ratification scores 0. Recycling reflects the share of household and business waste collected and recycled by local authorities. 

*Note: For the two conventions, 2015 data was used for 2017, and 2022 data was used for 2020.*
""",
    "EJ Events": """
**Cumulative unresolved Environmental Justice events** measures the share of unresolved environmental justice events by country, based on cumulative data filtered to exclude stopped projects and events with known end dates. It highlights the distribution of verified environmental justice conflicts from historical records up to 2022, ranking countries by their share of the total unresolved cases. This indicator sheds light on the ten most affected countries, emphasizing persistent socio-environmental injustices globally.


*DISCLAIMER: Please consider that the indicator has been produced using original data from the Environmental Justice Atlas (see publication at https://doi.org/10.2458/v22i1.21108). The original data set cannot be considered globally representative or its coverage complete. The EJAtlas data are a crowd-sourced convenience sample of environmental conflicts globally that updates and expands continuously. The absence of cases in the EJAtlas does not necessarily indicate an absence of environmental conflicts, but also areas for which the EJAtlas team has limited access to data; finally, EJAtlas data can be out of date, and at all effects consider the Data Set as an archive of cases describing environmental conflict until their specific day of publication or updating.*
""",
    "Climate Disaster": """
**Climate disaster damages** measures the economic impact of climate-related disasters, including climatological, hydrological, and meteorological events. It aggregates the total damages in % of country GDP, focusing on events since 2000. The indicator also tracks trends using a 5-year moving average, offering insights into the financial burden of these disasters over time at both country and regional levels.
""",
    "Protected Forests": """
**Forest coverage and management sustainability index** measures the combined progress in forest area preservation and sustainable forest management practices, providing a holistic view of forest health. It averages the proportion of land covered by forests and a composite measure of sustainable management practices. 

*Note: Data for 2007 and 2012 were interpolated using values from 2005 and 2010, and 2010 and 2015, respectively, while 2022 values rely on data from 2020 due to limited availability.*
""",
    "Energy Perspective": """
The Index of **Energy Perspective**  assesses a country's commitment to sustainable energy by analyzing the contribution to investment in renewable technologies and fossil fuel subsidies, relative to gross domestic product (GDP). 

This indicator is calculated by aggregating and normalizing investment in renewable technologies (using IRENA data) against GDP. Similarly, Fossil Fuel Subsidies (taken from IMF), which include both direct financial support and implicit subsidies such as underestimation of environmental externalities, are calculated and normalized. The Index of Energy Perspective is obtained by subtracting normalized fossil fuel subsidies from normalized renewable investments, providing a net value that reflects the nation's actual financial orientation toward sustainable energy.

*Note: Due to data limitations in Fossil Fuels Subsidies, values for 2007 and 2012 were assumed to be the same as 2015 in the absence of older data.*
""",
"EJ Index": """
** Environmental Justice Index** is a synthetic index aims at measuring the relative enviromental justice across the world. The indicator is calcuated as a weighted average of indicators for three dimensions:

- **Human Rights**:  measured as an average of *"Air Pollution Moratlity","Education Index", and "Protected Forests"*
- **Common Goods**:  measured as an average of *"Red List Index","EJ Events", and "Climate Disaster"*
- **Sustainability**: measured as an average of *"Citizen Carbon Footprint","Waste Management", and "Energy Perspective"*
"""
}

WELCOME = """

Created by **Mani Tese** in partnership with the **University of Milan**, **Politecnico di Milano**, and **eNextGen**, and funded by **Fondazione Cariplo**, the **EJI** weaves together **twelve open-source indicators** – spanning *Human Rights*, *Common Goods*, and *Sustainability* – to reveal which countries contribute most to environmental and social degradation and which suffer its greatest impacts.

Each indicator is normalized to a **0–1 scale**, and the three dimensions are **equally weighted by default** (⅓ each, but fully adjustable) to deliver a single, transparent score for every country across four benchmark years: **2007, 2012, 2017, and 2022**.


** Environmental Justice Index Report**

The full scientific method, data sources, and policy implications are detailed in the **Environmental Justice Index Report** (click here for more info: [Environmental Justice Index - Mani Tese](https://www.manitese.it/iniziative/environmental-justice-index/)).

- [Download PDF – Italian](https://www.manitese.it/wp-content/uploads/2025/04/Environmental_Justice_Index_bassa.pdf)  
- [Download PDF – English](#)


** How to Use the Platform in Three Quick Steps**

1.**Explore the map**  
   Select a year in the top-right menu, then hover or tap on any country to view its overall score and the breakdown by dimension.

2.**Dive into specific indicators**  
   Use the drop-down list to visualize a single metric – such as per-capita carbon footprint, mortality from air pollution, or unresolved environmental-justice conflicts.

3.**Adjust the perspective**  
   Move the sliders below the map to change the weights of the three dimensions and watch colors and rankings update instantly. When you’re ready for deeper analysis, click **Download data** to obtain the raw and normalized datasets.


** Questions? **

Consult the **Methodology** section or write to [lenhard@manitese.it](mailto:lenhard@manitese.it).  

**Enjoy exploring – and thank you for advancing environmental justice!**

"""

COPYRIGHT = """
© 2025 [Environmental Justice Index](https://ejindex.manitese.it/). All rights reserved ([Mani Tese](https://www.manitese.it)).
"""

dcc.Store(id="window-size", data={"width": 800, "height": 600}),
dcc.Interval(id="resize-interval", interval=500, n_intervals=0),  # Checks window size


# Load JSON file into a dictionary
with open('metadata.json', 'r') as json_file:
    metadata = json.load(json_file)


def calc_slider_vals(x_value,y_value,z_value):
    if (x_value + y_value) >= 1:
        if x_value >= y_value:
            y_value = 1 - x_value
        else:
            x_value = 1 - y_value

    # Calculate z-slider value dynamically
    z_value = 1 - x_value - y_value

    return x_value,y_value,z_value


def build_hover(df,metadata):

    hover_text = []

    for row,vals in df.iterrows():
        indicator = vals.Indicator
        country = vals.Official_Name
        region = vals.UN_Region
        macro_category = metadata[indicator]["dimension"]
        normalized_value = round(vals.Normalized,3)
        unit = metadata[indicator]["unit"]
        absolute_value = round(vals.Value,3)

        if unit == "":
            text = f"""
        {macro_category} <br>
        {country} ({region}) <br>
        - Normalized value: {normalized_value} <br>
        - Absolute value: {absolute_value}
        """
        else:
            text = f"""
        {macro_category} <br>
        {country} ({region}) <br>
        - Normalized value: {normalized_value} <br>
        - Absolute value: {absolute_value} [{unit}]
        """

        hover_text.append(text)

    return hover_text

def build_ej_hover(df,dims):

    
    hover_text = []
    for row,vals in df.iterrows():
        country = vals.Official_Name
        region = vals.UN_Region
        normalized_value = round(vals.Normalized,3)
        common_goods = dims["Common goods"].loc[row,"Normalized"]
        human_right = dims["Human rights"].loc[row,"Normalized"]
        sustainability = dims["Sustainability"].loc[row,"Normalized"]
        # x = round(x*normalized_value,3)
        # y = round(y*normalized_value,3)
        # z = round(z*normalized_value,3)
        text = f"""
    {country} ({region}) <br>
    Normalized value: {normalized_value} <br><br>
    <b>Dimensions</b><br>
    - Common goods ({round(common_goods,3)}) <br>
    - Human rights ({round(human_right,3)}) <br>
    - Sustainability ({round(sustainability,3)}) <br>
    """
        
        hover_text.append(text)
    
    return hover_text

MARKS = np.arange(0, 1.1, 0.1).tolist()

HOVER_COLS = ["Official_Name", "Year", "Value"]


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
    df = load_all_data()

except Exception as e:
    print(f"Error loading CSV: {e}")
    df = pd.DataFrame(
        columns=[
            "Region",
            "Year",
            "Indicator",
            "Value",
            "Continent",
            "UN_Region",
            "Official_Name",
            "Normalized",
        ]
    )

df["hover_text"] = build_hover(df,metadata)

REGIONS = [{"label": "World", "value": "World"}]
for val in df.Continent.unique():
    REGIONS.append({"label": val, "value": val})

# %%
# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"],
    suppress_callback_exceptions=True,
    show_undo_redo=False,

)


app.clientside_callback(
    """
    function(n) {
        return {'width': window.innerWidth, 'height': window.innerHeight};
    }
    """,
    Output("window-size", "data"),
    Input("resize-interval", "n_intervals"),
)

# Extract unique indicators and years for dropdown
indicators = df["Indicator"].unique().tolist() if not df.empty else []
indicators.insert(0, "EJ Index")



# App layout
app.layout = html.Div(
    [

# dcc.Store(id="window-size", data={"width": 800, "height": 600}),

# Top Banner
html.Div(
    className="study-browser-banner",
    children=[
        html.Div(
            className="banner-content",
            children=[
                # Logo on the left
                html.A(
                    href="https://www.manitese.it/",
                    children=html.Img(
                        src="https://manitese.it/wp-content/themes/manitese/assets/images/manitese.svg",
                        className="banner-logo",
                    ),
                ),

                # Title (Centered)
                html.H2(
                    "Environmental Justice Index",
                    className="banner-title",
                ),

                # Empty div for spacing (balances layout)
                html.Div(className="banner-space"),
            ],
        ),
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
        html.Div(
            [html.H1("Welcome to the Environmental Justice Index (EJI) Dashboard",style={'textAlign': 'center','fontSize': '24px' }),
            dcc.Markdown(WELCOME,style={"text-align": "justify"}),],
            className="user-box box-shadow indicator-explanation indicator-browser",
            style={"width": "70%", "margin": "auto","margin-bottom":"20px"},
            ),
      html.Div(
    className="indicator-browser user-box box-shadow",
    children=[
        html.Div(
            className="inline-elements",
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
                            className="button button-sm",
                        ),
                        dcc.Download(id="download-data"),
                    ],
                    className="download-button-container",  # Added a wrapper class here
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

        html.Div([
            dcc.Dropdown(
            id="drop_continent",
            className="continent-filter",
            clearable=False,
            searchable=False,
            options=REGIONS,
            value="World",
        ),

    html.Div(
    dcc.Graph(
        id="choropleth-map",
        config={"responsive": True},  # Important for responsiveness
        style={"width": "10%", "height": "10%","margin-top":"20px"}  # Allow full use of container
    ),
    className="map-container",

),
        html.Div(id="soure-box", className="indicator-explanation"),
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
        html.Div(dcc.Markdown(COPYRIGHT),className="indicator-explanation"),
        ],className="result-container",
        ),
         # Add the resize interval to update the window size
    # dcc.Interval(id="resize-interval", interval=500, n_intervals=0),
    ]
)


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
def update_choropleth(selected_indicator, x_value, y_value, z_value, continent,):
    if not selected_indicator:
        return px.choropleth()  # Return an empty figure if no indicator is selected

    x_value, y_value, z_value = calc_slider_vals(x_value, y_value, z_value)

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
        filtered_df["hover_text"] = build_ej_hover(filtered_df, dims)
        HOVER_COLS = []
    else:
        filtered_df = df[df["Indicator"] == selected_indicator]
        HOVER_COLS = []

    if filtered_df.empty:
        return px.choropleth()  # Return an empty figure if no data matches

    hover_data = {col: col in HOVER_COLS for col in filtered_df.columns}

    if continent != "World":
        filtered_df = filtered_df.loc[filtered_df.Continent == continent]

    fig = px.choropleth(
        filtered_df,
        locations="Region",
        color="Normalized",
        animation_frame="Year",
        projection="natural earth",
        hover_data=hover_data,
        hover_name="hover_text",
        color_continuous_scale=[
            (0.0, "#B02A2A"),
            (0.5, "#C2D201"),
            (1.0, "#22835A"),
        ],
    )

     # Predefined centers and zoom levels for each continent
    continent_zoom = {
        "Africa": {"center": {"lat": 1.0, "lon": 20.0}, "zoom": 1.5},
        "Asia": {"center": {"lat": 34.0, "lon": 100.0}, "zoom": 1.5},
        "Europe": {"center": {"lat": 50.0, "lon": 10.0}, "zoom": 1.5},
        "America": {"center": {"lat": 37.0, "lon": -90.0}, "zoom": 1.0},  # Adjusted zoom level to 2.5
        "Oceania": {"center": {"lat": -25.0, "lon": 140.0}, "zoom": 1.5},
        "World": {"center": {"lat": 0.0, "lon": 0.0}, "zoom": 1}  # World view as default
    }


    # Set the center and zoom based on the continent
    if continent in continent_zoom:
        center = continent_zoom[continent]["center"]
        zoom = continent_zoom[continent]["zoom"]
    else:
        center = continent_zoom["World"]["center"]
        zoom = continent_zoom["World"]["zoom"]

    # Check if the relayoutData has the keys we're interested in for zoom


    fig.update_layout(
        autosize=True,
        # width=map_width,
        # height=map_height,
        coloraxis=dict(cmin=0, cmax=1),
        hovermode="x unified",
        geo=dict(
            projection_type="natural earth",  # Set projection to "natural earth"
            center=center,  # Set center to the continent's center
            projection_scale=zoom,  # Set zoom level
        ),
    )



    # For larger screens (desktop, etc.)
    fig.update_layout(
        coloraxis_colorbar=dict(
        title="Normalized",  # Title for the color bar
        tickvals=[0, 0.25, 0.5, 0.75, 1],  # Intervals for ticks
        ticktext=["0", "0.25", "0.5", "0.75", "1"],  # Corresponding labels
        tickmode="array",  # Use `tickvals` and `ticktext` for ticks
        lenmode="fraction",  # Set the color bar length in pixels,
        thicknessmode = "fraction",
        len=0.5,  # Size of the color bar
        thickness = 0.05
        ),
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
        filtered_df = df[df["Indicator"] == selected_indicator].drop("hover_text",errors="ignore",axis=1)

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

        x_value, y_value, z_value = calc_slider_vals(x_value, y_value,0)

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
    explanation = DESCRIPTIONS.get(
        selected_indicator, "Explanation not available for the selected indicator."
    )

    return dcc.Markdown(explanation, className="bold-text")

@app.callback(
    Output("soure-box","children"),Input("indicator-dropdown", "value")
)
def update_source_links(selected_indicator):

    if selected_indicator == "EJ Index":
        return None

    source = metadata[selected_indicator]["source"]
    link = metadata[selected_indicator]["link"]
    filtered_df = df[df["Indicator"] == selected_indicator]
    estimated_data = filtered_df[filtered_df["Source"]=="Estimated"]
    
    share_of_estimation = len(estimated_data)/len(filtered_df)*100

    if isinstance(source, str):
        text = f"""
Source: [{source}]({link})
"""
    else:
        text = "Source:\n"
        for s, l in zip(source, link):
            text += f"- [{s}]({l})\n"




#     text = f"""
# Source: *{source}*

# Link: *{link}*

# """
    if share_of_estimation != 0:
        text += f"""
Note: {math.ceil(share_of_estimation)}% of data is estimated
"""

    return dcc.Markdown(
        text,
    )


# Run the app
if __name__ == "__main__":
    app.run_server(debug=False)
