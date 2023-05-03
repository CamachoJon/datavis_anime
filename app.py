import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load the data
df = pd.read_csv('anime_filtered.csv')
df_revenue = pd.read_csv('anime_revenue.csv')

# Create the app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1('Anime Data Dashboard'),
    html.Div([
        html.H2('Treemap'),
        dcc.Graph(id='treemap'),
        html.Label('X variable'),
        dcc.Dropdown(
            id='x-var',
            options=[{'label': col, 'value': col} for col in df.select_dtypes('object').columns],
            value='status'
        ),
        html.Label('Y variable'),
        dcc.Dropdown(
            id='y-var',
            options=[{'label': col, 'value': col} for col in df.select_dtypes('object').columns],
            value='source'
        )
    ]),
    html.Div([
        html.H2('Histogram'),
        dcc.Graph(id='histogram'),
        html.Label('Feature to plot'),
        dcc.Dropdown(
            id='feature-to-plot',
            options=[{'label': col, 'value': col} for col in df_revenue.columns],
            value='Revenue (Millions)'
        ),
        html.Label('Feature to split'),
        dcc.Dropdown(
            id='feature-to-split',
            options=[{'label': col, 'value': col} for col in df_revenue.columns],
            value='source'
        )
    ])
])

# Define the callbacks
@app.callback(
    Output('treemap', 'figure'),
    Input('x-var', 'value'),
    Input('y-var', 'value')
)
def update_treemap(x_var, y_var):
    grouped_df = df.groupby([y_var, x_var]).size().reset_index(name='Count')
    graph_6 = px.treemap(
        grouped_df,
        path=[y_var, x_var],
        values='Count',
        color='Count',
        color_continuous_scale=px.colors.sequential.Agsunset)
    graph_6.update_layout(
        title=f'Treemap of {x_var} and {y_var}',
    )
    return graph_6

@app.callback(
    Output('histogram', 'figure'),
    Input('feature-to-plot', 'value'),
    Input('feature-to-split', 'value')
)
def update_histogram(feature_to_plot, feature_to_split):
    graph_7 = px.histogram(df_revenue, x=feature_to_plot, color=feature_to_split, nbins=50, histnorm='probability density', 
                       color_discrete_sequence=px.colors.sequential.Agsunset)
    graph_7.update_layout(
        title=f'Histogram of {feature_to_plot} splitting by {feature_to_split}',
        xaxis_title=feature_to_plot,
        yaxis_title=feature_to_split,
    )
    return graph_7

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
