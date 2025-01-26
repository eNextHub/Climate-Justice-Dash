#%%
import pandas as pd
import plotly.express as px

DIMS = {
    "Common goods": ["Red List Index","EJ Events","Climate Disaster"],
    "Human rights": ["Air Pollution Mortality","Education Index","Protected Forests"],
    "Sustainability": ["Citizen Carbon Footprint","Waste Management","Fossil Fuel Subsidies"],
}
dfs = {}

def read_dims():
    for dim,indicators in DIMS.items():
        dfs[dim] = []
        for indicator in indicators:
            dfs[dim].append(pd.read_csv(f"data/{indicator}.csv"))
           
        dim_value = dfs[dim][0]
        dim_value["Normalized"] = sum([df["Normalized"] for df in dfs[dim]])/len(dfs[dim])
        dim_value["Indicator"] = dim

        dfs[dim] = dim_value.drop("Value",axis=1)

    return dfs

DEFAULT_WEIGHTS = {
    "Common goods": 1/3,
    "Human rights": 1/3,
    "Sustainability": 1/3,
}
def calc_EJ_index(dfs,weights = DEFAULT_WEIGHTS):

    df = dfs["Common goods"].copy()

    df["Normalized"] = sum(indicator["Normalized"]*weights[dim] for dim,indicator in dfs.items())
    df["Indicator"] = "EJ Index"
    df["Source"] = "Calcualted"

    # df.to_csv("data/EJ index.csv")
    return df

def plot(data):
    fig = px.choropleth(
        data,
        locations="Region",          # ISO3 country codes
        color="Normalized",               # Data column for color scale
        hover_name="Official",         # Hover information
        animation_frame="Year",      # Column used for animation (dropdown-like behavior)
        color_continuous_scale="BrBG",
        projection="natural earth"
    )
    vmin = data["Normalized"].min()
    vmax = data["Normalized"].max()
    # Update the color axis to fix the color scale range
    fig.update_layout(
        coloraxis_colorbar=dict(title="Value"),
        coloraxis=dict(cmin=vmin, cmax=vmax)  # Set the fixed min and max range
    )

    # Update layout for better appearance
    fig.update_layout(
        title=data.Indicator.iloc[0],
        geo=dict(showframe=False, showcoastlines=True)
    )

    indicator = data.Indicator.iloc[0]
    fig.write_html(f"plots/{indicator}.html")



if __name__ == "__main__":
    dfs = read_dims()
    # data = calc_EJ_index(dfs)
    # plot(data)

# %%
