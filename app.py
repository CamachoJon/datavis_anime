import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load the data into a pandas dataframe
df = pd.read_csv('anime_revenue.csv')

# Define the app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("Anime Dataset"),
    html.Div([
        html.Div([
            html.Label("Feature to Plot"),
            dcc.Dropdown(
                id="feature-to-plot",
                options=[{"label": col, "value": col} for col in df.columns],
                value="Revenue (Millions)"
            )
        ], className="six columns"),
        html.Div([
            html.Label("Feature to Split"),
            dcc.Dropdown(
                id="feature-to-split",
                options=[{"label": col, "value": col} for col in df.columns],
                value="source"
            )
        ], className="six columns"),
    ], className="row"),
    html.Div([
        dcc.Graph(id="histogram"),
    ], className="six columns"),
    html.Div([
        dcc.Graph(id="top-10-barplot"),
    ], className="six columns"),
])

# Define the callbacks
@app.callback(
    [Output("histogram", "figure"), Output("top-10-barplot", "figure")],
    [Input("feature-to-plot", "value"), Input("feature-to-split", "value")]
)
def update_plots(feature_to_plot, feature_to_split):
    # Create the histogram plot
    histogram = px.histogram(
        df,
        x=feature_to_plot,
        color=feature_to_split,
        nbins=50,
        histnorm='probability density',
        color_discrete_sequence=px.colors.sequential.Agsunset
    )
    histogram.update_layout(
        title=f'Histogram of {feature_to_plot} splitting by {feature_to_split}',
        xaxis_title=feature_to_plot,
        yaxis_title=feature_to_split
    )

    # Create the top 10 barplot
    top10_df = df.sort_values(feature_to_plot, ascending=False).head(10)
    top10_barplot = px.bar(
        top10_df,
        x='title',
        y=feature_to_plot,
        text=feature_to_plot,
        hover_data=[feature_to_plot],
        color_continuous_scale=px.colors.sequential.Agsunset
    )
    top10_barplot.update_layout(
        title=f'Top 10 Animes by {feature_to_plot}',
        xaxis_title='Anime Title',
        yaxis_title=feature_to_plot,
        yaxis_tickformat='$,.2f'
    )

    return histogram, top10_barplot

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
