import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Load the data into a pandas dataframe
df = pd.read_csv('anime_filtered.csv')

# Define the app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1('Anime Dashboard'),
    dcc.Tabs([
        dcc.Tab(label='Treemap', children=[
            html.Div([
                html.H2('Treemap of Anime Status and Source'),
                html.Div([
                    html.P('Select x variable:'),
                    dcc.Dropdown(
                        id='treemap-x-var',
                        options=df.columns,
                        value='status'
                    ),
                    html.P('Select y variable:'),
                    dcc.Dropdown(
                        id='treemap-y-var',
                        options=df.columns,
                        value='type'
                    ),
                ]),
                dcc.Graph(id='treemap')
            ])
        ]),
        dcc.Tab(label='Scatter Plot', children=[
            html.Div([
                html.H2('Scatter Plot of Anime Scores and Members'),
                html.Div([
                    html.P('Select x variable:'),
                    dcc.Dropdown(
                        id='scatter-x-var',
                        options=df.columns,
                        value='members'
                    ),
                    html.P('Select y variable:'),
                    dcc.Dropdown(
                        id='scatter-y-var',
                        options=df.columns,
                        value='score'
                    ),
                    html.P('Select color variable:'),
                    dcc.Dropdown(
                        id='scatter-color-var',
                        options=df.columns,
                        value='type',
                        multi=False
                    ),
                ]),
                dcc.Graph(id='scatter')
            ])
        ]),
        dcc.Tab(label='Timeline', children=[
            html.Div([
                html.H2('Number of Animes Premiered by Season'),
                dcc.Graph(id='timeline')
            ])
        ]),
    ])
])

# Define the treemap callback
@app.callback(
    Output('treemap', 'figure'),
    Input('treemap-x-var', 'value'),
    Input('treemap-y-var', 'value')
)
def update_treemap(x_var, y_var):
    grouped_df = df.groupby([y_var, x_var]).size().reset_index(name='Count')
    fig = px.treemap(
        grouped_df,
        path=[y_var, x_var],
        values='Count',
        color='Count',
        color_continuous_scale=px.colors.sequential.Agsunset)
    fig.update_layout(
        title=f'Treemap of {x_var} and {y_var}',
    )
    return fig

@app.callback(
    Output('scatter-color-var', 'options'),
    Input('scatter-x-var', 'value'),
    Input('scatter-y-var', 'value')
)
def update_scatter_color_options(x_var, y_var):
    options = [{'label': col, 'value': col} for col in df.columns if col not in [x_var, y_var]]
    return options


@app.callback(
    Output('scatter-plot', 'figure'),
    Input('scatter-x-var', 'value'),
    Input('scatter-y-var', 'value'),
    Input('scatter-color-var', 'value')
)
def update_scatter(x_var, y_var, color_var):
    # DOESNT SHOW CHART
    fig = px.scatter(
        df,
        x=x_var,
        y=y_var,
        color=color_var,
        hover_data=['title'],
        opacity=0.7,
        color_continuous_scale=px.colors.sequential.Agsunset
    )

    fig.update_layout(
        title=f'Scatter of {y_var} and {x_var}',
        xaxis_title=x_var,
        yaxis_title=y_var,
    )

    return fig


def timeline():
    # DOESNT WORK
    df['Year'] = df['premiered'].str.extract('(\d{4})')
    df['Season'] = df['premiered'].str.extract('(Winter|Spring|Summer|Fall)')

    premieres = df.groupby(['Year', 'Season']).size().reset_index(name='Count')

    fig = go.Figure()
    seasons = ['Winter', 'Spring', 'Summer', 'Fall']
    for season in seasons:
        season_data = premieres[premieres['Season'] == season]
        fig.add_trace(go.Scatter(
            x=season_data['Year'],
            y=season_data['Count'],
            mode='lines+markers',
            name=season,
            line=dict(
                color=px.colors.sequential.Agsunset[seasons.index(season)],
                width=3
            )
        ))

    fig.update_layout(
        title='Number of Animes Premiered by Season',
        xaxis_title='Year',
        yaxis_title='Number of Animes',
        yaxis_tickformat=',d'
    )

    return fig


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)