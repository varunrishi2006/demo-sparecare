import dash
import json
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
from pandas.api.types import CategoricalDtype
import dash_bootstrap_components as dbc
import datetime
from datetime import datetime as dt, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pathlib
# import dash_auth
from plotly.subplots import make_subplots

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1, maximum-scale=1.2, minimum-scale=0.5,"}],
)
server = app.server

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../src/datasets").resolve()

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../src/datasets").resolve()

# auth = dash_auth.BasicAuth(
#     app,
#     {'Sparecare': 'Sparecare@2023'}
# )
app.title = "SpareCare Dealer Dashboard"

df_dealer_perf = pd.read_excel(DATA_PATH.joinpath("Sample_Data.xlsx"))
dealer_codes = df_dealer_perf['Dealer'].unique().tolist()

month_order = CategoricalDtype([
    "Jan'23",
    "Feb'23",
    "Mar'23",
    "Apr'23",
    "May'23",
    "Jun'23",
], ordered=True)

disc_order = CategoricalDtype([
    "0-5",
    "6-10",
    "11-20",
    "21-50",
    "51-75",
    "76-100",
], ordered=True)

df_dealer_perf['Month'] = df_dealer_perf['Month'].astype(month_order)


def description_card():
    """
    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5("Location Performance Analysis ",
                    style={"font-weight": "bold"}),
            html.H3("Welcome to the Location Performance Analysis Dashboard"),
            html.P(
                "Explore the revenue performance of your locations.\n"
                "Analyse the overall revneue and discount trend by month, location, revenue lines etc.",
                style={'fontSize': 14}),
            html.P()
        ],
    )


def generate_control_card():
    """
    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.P(),
            html.B("Dealer Code"),
            html.Br(),
            dcc.Dropdown(
                id="dealer-code",
                options=[{"label": i, "value": i} for i in dealer_codes],
                value=101,
                multi=False,
                className="dcc_control",
            ),
            html.Br(),
            html.P(),
            html.B("Locations"),
            html.Br(),
            dcc.Dropdown(
                id="locations",
                multi=False,
                className="dcc_control",
            ),
            html.Br(),
            html.P(),
            html.Span(children=[
                html.I(
                    "Note: The dashboard has been constructed to analyse the peformance of each dealer location-wise."),
                # html.I("as the operating Carrier and other carriers as potential competitors in the route."),
                html.I(
                    "Filters in this section will work as a global filter and will impact all the views of the dashboard.")],
                style={'color': 'brown', 'fontSize': 14})
            # html.B("Top N Locations by Revenue"),
            # html.P(),
            # html.Div(
            #     dcc.RangeSlider(
            #         id="location-count",
            #         min=1,
            #         max=10,
            #         step=1,
            #         value=[1, 5],
            #         allowCross=False,
            #         marks={i: f"{i}" for i in range(1, 11, 1)},
            #         className="dcc_control"
            #     ),
            #     style={'color': 'black'}
            # ),
        ],
    )


app.layout = html.Div(
    id="app-container",
    children=[
        # html.Div(
        dbc.Row(
            [
                # html.Div(
                dbc.Col(
                    id="left-column",
                    className="pretty_container four columns",
                    children=[description_card(), generate_control_card()],
                    xs=12, sm=12, md=6, lg=4, xl=4,
                    style={'border': '1px solid black'}
                ),
                # Right column
                # html.Div(
                dbc.Col(
                    [
                        html.B("Top N Locations by Revenue"),
                        html.P(),
                        html.Div(
                            dcc.RangeSlider(
                                id="location-count",
                                min=1,
                                max=10,
                                step=1,
                                value=[1, 5],
                                allowCross=False,
                                # marks={i: f"{i}" for i in range(1, 11, 1)},
                                marks={i: {'label': str(i), 'style': {'color': 'black'}} for i in range(1, 11, 1)},
                                className="dcc_control",
                            ),
                        ),
                        html.Div(
                            [
                                dcc.Graph(id='loc_details')
                            ],
                            # className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    xs=12, sm=12, md=6, lg=8, xl=8,
                    className="pretty_container eight columns",
                ),
            ],
            className="row flex-display",
        ),
        # html.Div(
        dbc.Row(
            [
                # html.Div(
                dbc.Col(
                    [
                        dcc.Graph(id="trend-performance")
                    ],
                    xs=12, sm=12, md=5, lg=5, xl=5,
                    className="pretty_container six columns"
                ),
                # html.Div(
                dbc.Col(
                    [
                        dcc.Graph(id="revenue_contr_source")
                    ],
                    xs=12, sm=12, md=5, lg=5, xl=5,
                    className="pretty_container six columns"
                ),
            ],
            className="row flex-display",
        ),
    ]
)


@app.callback(
    Output("locations", "options"),
    Output("locations", "value"),
    Input("dealer-code", "value")
)
def update_locations(dealer_code):
    options = []
    default_value = None
    locations = df_dealer_perf[df_dealer_perf['Dealer'] == dealer_code]['Location'].unique().tolist()
    options = [
        {'label': 'All', 'value': 'all'},
        *[
            {'label': i, 'value': i} for i in locations
        ]
    ]
    default_value = 'all'
    print(f'Lets check the value of options {options}')
    return options, default_value


@app.callback(
    Output('loc_details', 'figure'),
    Input('dealer-code', 'value'),
    Input('locations', 'value'),
    Input('location-count', 'value')
)
def loc_analysis(dealer_code, location, loc_count):
    print(f'Lets check the value of dealer code {dealer_code}')
    print(f'Lets check the value of location {location}')
    print(f'Lets check the value of loc count {loc_count}')
    if location == 'all':
        df_dealer_1 = df_dealer_perf[df_dealer_perf['Dealer'] == dealer_code]
    else:
        df_dealer_1 = df_dealer_perf[
            (df_dealer_perf['Dealer'] == dealer_code) & (df_dealer_perf['Location'] == location)]

    df_1 = df_dealer_1.groupby('Location', as_index=False).agg({'Revenue': 'sum', 'Discount': 'sum'}).sort_values(
        by='Revenue', ascending=False)[loc_count[0] - 1:loc_count[1]]
    df_1['Discount %'] = round(df_1['Discount'] / df_1['Revenue'] * 100, 2)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            name="Overall Discount % by Location",
            x=df_1['Location'],
            y=df_1['Discount %'],
            marker=dict(color="crimson"),
            hovertemplate='Location: %{x} <br> Discount(%): %{y}',
            hoverinfo='text',
        ),
        secondary_y=True
    )

    # Add Bar traces for Data 1 (Revenue) and Data 2 (Discount) - Stacked
    fig.add_trace(
        go.Bar(
            name='Total Revenue by Location',
            x=df_1['Location'],
            y=df_1['Revenue'],
            hovertemplate='Location: %{x}<br>Revenue: %{y}',
            hoverinfo='text'
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Bar(
            name='Total Discount by Location',
            x=df_1['Location'],
            y=df_1['Discount'],
            hovertemplate='Location: %{x}<br>Discount: %{y}',
            base=df_1['Revenue'],  # Set the base parameter to stack the bars
        ),
        secondary_y=False,
    )

    fig.update_layout(barmode='stack')

    # Update the layout and show the figure
    fig.update_layout(title="Revenue/Discount Analysis by Location",
                      title_x=0.5,
                      xaxis_title="Locations",
                      # height=550,
                      yaxis_title="Total Revenue & Discounts by each Location",
                      yaxis2_title="Discount as perc of Total Revenue",
                      showlegend=False,
                      font=dict(family="Arial", size=12, color="black"),
                      plot_bgcolor='rgba(0,0,0,0)',
                      template='ggplot2',
                      yaxis2=dict(
                          type='linear',
                          range=[1, 10],
                          ticksuffix='%'))

    return fig


@app.callback(
    Output('trend-performance', 'figure'),
    Input('dealer-code', 'value'),
    Input('locations', 'value'),
    Input('location-count', 'value'),
    Input('loc_details', 'clickData')
)
def loc_analysis(dealer_code, location, loc_count, clickData):
    print(f'Lets check the value of dealer code {dealer_code}')
    print(f'Lets check the value of location {location}')
    print(f'Lets check the value of clickData {clickData}')
    loc = ""
    if clickData is not None:
        loc = clickData['points'][0]['x']
        print(f'Lets check the value of loc {loc}')

    if clickData is not None:
        df_dealer_1 = df_dealer_perf[
            (df_dealer_perf['Dealer'] == dealer_code) & (df_dealer_perf['Location'] == loc)]
    else:
        if location == 'all':
            df_dealer_1 = df_dealer_perf[df_dealer_perf['Dealer'] == dealer_code]
        else:
            df_dealer_1 = df_dealer_perf[
                (df_dealer_perf['Dealer'] == dealer_code) & (df_dealer_perf['Location'] == location)]

    df_1 = df_dealer_1.groupby('Month', as_index=False).agg({'Revenue': 'sum', 'Discount': 'sum'})
    df_1['Discount %'] = round(df_1['Discount'] / df_1['Revenue'] * 100, 2)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            name="Overall Discount % by Location",
            x=df_1['Month'],
            y=df_1['Discount %'],
            marker=dict(color="crimson"),
            hovertemplate='Location: %{x} <br> Discount(%): %{y}',
            hoverinfo='text',
        ),
        secondary_y=True
    )

    # Add Bar traces for Data 1 (Revenue) and Data 2 (Discount) - Stacked
    fig.add_trace(
        go.Bar(
            name='Total Revenue by Location',
            x=df_1['Month'],
            y=df_1['Revenue'],
            hovertemplate='Location: %{x}<br>Revenue: %{y}',
            hoverinfo='text'
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Bar(
            name='Total Discount by Location',
            x=df_1['Month'],
            y=df_1['Discount'],
            hovertemplate='Location: %{x}<br>Discount: %{y}',
            base=df_1['Revenue'],  # Set the base parameter to stack the bars
        ),
        secondary_y=False,
    )

    fig.update_layout(barmode='stack')

    # Update the layout and show the figure
    if loc == "":
        fig.update_layout(title="Revenue/Discount Analysis by Month across Locations")
    else:
        fig.update_layout(title="Revenue/Discount Analysis by Month for Location " + loc)

    fig.update_layout(title_x=0.5,
                      xaxis_title="Locations",
                      # height=550,
                      yaxis_title="Total Revenue & Discounts by each Location",
                      yaxis2_title="Discount as perc of Total Revenue",
                      showlegend=False,
                      font=dict(family="Arial", size=12, color="black"),
                      plot_bgcolor='rgba(0,0,0,0)',
                      template='ggplot2',
                      yaxis2=dict(
                          type='linear',
                          range=[1, 10],
                          ticksuffix='%'))

    return fig


@app.callback(
    Output('revenue_contr_source', 'figure'),
    Input('dealer-code', 'value'),
    Input('locations', 'value'),
    Input('loc_details', 'clickData'),
    Input('trend-performance', 'clickData')
    # Input('location-count', 'value')
)
def update_rev_sources(dealer_code, location, clickData, clickData1):
    print(f'Lets check the value of clickdata1 {clickData1}')
    loc = ""
    selected_month = ""
    if clickData is not None:
        loc = clickData['points'][0]['x']
        print(f'Lets check the value of loc {loc}')

    if clickData is not None:
        df_dealer_1 = df_dealer_perf[
            (df_dealer_perf['Dealer'] == dealer_code) & (df_dealer_perf['Location'] == loc)]
    else:
        if location == 'all':
            df_dealer_1 = df_dealer_perf[df_dealer_perf['Dealer'] == dealer_code]
        else:
            df_dealer_1 = df_dealer_perf[
                (df_dealer_perf['Dealer'] == dealer_code) & (df_dealer_perf['Location'] == location)]

    if clickData1 is not None:
        selected_month = clickData1['points'][0]['x']
        print(f'Check the value of selected month {selected_month}')
        df_dealer_1 = df_dealer_1[df_dealer_1['Month'] == selected_month]

    df_init = pd.melt(df_dealer_1,
                      id_vars=['Dealer', 'Location', 'Month', 'Revenue Line', 'Revenue', 'Discount %', 'Discount'],
                      var_name='Discount Range(%)',
                      value_name='Quantity')

    df_init['Discount Range(%)'] = df_init['Discount Range(%)'].astype(disc_order)
    df_pivot = pd.pivot_table(df_init, values="Quantity", index='Revenue Line', columns='Discount Range(%)')

    df_pivot.columns.name = None
    df_pivot.index.name = None
    cols = df_pivot.columns.tolist()
    rows = df_pivot.index.tolist()
    df_pivot['Cum Qty'] = df_pivot.sum(axis=1)
    df_pivot.loc['Total'] = df_pivot.sum(axis=0)
    df_pivot = round(df_pivot)

    fig = px.imshow(
        df_pivot.iloc[:-1, :-1].values,
        labels=dict(x="Revenue Line", y="Discount Category(%)", color="Quantity"),
        x=cols,
        y=rows,
        color_continuous_scale="viridis",
        aspect="auto",
        text_auto='auto'
    )

    if loc == "" and selected_month == "":
        fig.update_layout(title="Discount Breakup by Revenue Line")
    elif loc != "" and selected_month != "":
        fig.update_layout(title="Discount Breakup for Location " + loc + " and Month " + selected_month)
    elif loc != "" and selected_month == "":
        fig.update_layout(title="Discount Breakup for Location " + loc)
    else:
        fig.update_layout(title="Discount Breakup for Month " + selected_month)

    fig.update_layout(title_x=0.5,
                      xaxis_title="Discount Category",
                      xaxis=dict(ticksuffix='%'),
                      # height=550,
                      yaxis_title="Revenue Line",
                      showlegend=False,
                      font=dict(family="Arial", size=12, color="black"),
                      plot_bgcolor='rgba(0,0,0,0)',
                      template='ggplot2',
                      yaxis=dict(title='y-axis', visible=False, showticklabels=False),
                      # yaxis2=dict(title='y-axis', visible=False, showticklabels=False),
                      )

    return fig


# Run the server
if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
