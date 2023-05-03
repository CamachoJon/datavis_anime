# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import requests
import pandas as pd
from bs4 import BeautifulSoup
import statsmodels.api as sm
import plotly.graph_objs as go

app = Dash(__name__)

SOURCES = ['4-koma manga', 'Book', 'Card game', 'Digital manga', 'Game',
           'Light novel', 'Manga', 'Music', 'Novel', 'Original', 'Other',
           'Picture book', 'Radio', 'Unknown', 'Visual novel', 'Web manga']


def scraper_modifier(anime_df, scraped_df):

    anime_df["Revenue (Millions)"] = 0.0
    anime_df["Sales per volume"] = 0.0
    anime_df['title_lower'] = anime_df['title'].str.lower()

    scraped_df['title_lower'] = scraped_df['Manga series'].str.lower()

    final_anime = anime_df.merge(scraped_df, on='title_lower', how='inner')

    final_anime['Sales (Million)'] = final_anime['Approximate sales'].str.extract(
        r'^([\d\.]+)', expand=False)

    final_anime['Average Sales Per Volume (Million)'] = final_anime['Average sales per volume'].str.extract(
        r'^([\d\.]+)', expand=False)

    final_anime['Sales (Million)'] = final_anime['Sales (Million)'].astype(
        'float')
    final_anime['Average Sales Per Volume (Million)'] = final_anime['Average Sales Per Volume (Million)'].astype(
        'float') * 100

    return final_anime


def web_scraper(anime_df):

    url = 'https://en.wikipedia.org/wiki/List_of_best-selling_manga'
    response = requests.get(url)
    html = response.content

    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table', {'class': 'wikitable'})

    dfs = []
    for table in tables:
        df = pd.read_html(str(table))[0]
        df.columns.values[7] = 'Average sales per volume'
        dfs.append(df)

    final_scrap = pd.concat(dfs)
    scraped_df = scraper_modifier(anime_df, final_scrap)

    return scraped_df


def discrete_intervals(anime_df):
    anime_df['score_bin'] = pd.cut(anime_df['score'], bins=[
                                   0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    rating_grading_df = anime_df.pivot_table(
        index='rating', columns='score_bin', values='title', aggfunc='count').reset_index()
    rating_grading_df.columns = [
        'rating', '0-1', '1-2', '2-3', '3-4', '4-5', '5-6', '6-7', '7-8', '8-9', '9-10']

    return rating_grading_df


# creation of dataframes
anime_df = pd.read_csv('anime_filtered.csv', sep=',')
scrapped_df = web_scraper(anime_df)

# Graph #1
df_counts = pd.pivot_table(
    anime_df, index='type', columns='source', aggfunc='size', fill_value=0).reset_index()
graph_1 = px.bar(df_counts, x='type', y=SOURCES, title='Count of sources by type of show',
                 color_discrete_sequence=px.colors.sequential.Agsunset)

# Graph #2
graph_2 = px.strip(anime_df, x='score', y='rating', color='airing', custom_data=[
                   'title'], hover_data={'title': True}, color_discrete_sequence=px.colors.sequential.Agsunset)

# Graph #3
graph_3 = px.violin(anime_df, y="score", x="airing", color="status", box=True,
                    points="all", hover_data=anime_df.columns, color_discrete_sequence=px.colors.sequential.Agsunset)

# Graph #4
graph_4 = px.scatter(scrapped_df, x="score", y="scored_by", size="Sales (Million)", color="episodes",
                     hover_name="title", log_x=True, size_max=40)

# Graph #5

rating_grading_df = discrete_intervals(anime_df)
graph_5 = px.bar(rating_grading_df, x='rating', y='5-6')

# Graph 8
feature = 'Sales (Million)'
top10_df = scrapped_df.sort_values(feature, ascending=False).head(10)

graph_8 = px.bar(
    top10_df, x='title', y=feature,
    text=feature,
    custom_data=[feature, 'Author(s)', 'genre'],
    hover_data=[feature, 'Author(s)', 'genre'],
    color_continuous_scale=px.colors.sequential.Agsunset)

# Graph 9
graph_9 = px.scatter(
    anime_df,
    x='members',
    y='score',
    color='type',
    hover_data=['title'],
    opacity=0.7,
    color_discrete_sequence=px.colors.sequential.Agsunset
)

# Graph 10
anime_df['Year'] = anime_df['premiered'].str.extract('(\d{4})')
anime_df['Season'] = anime_df['premiered'].str.extract(
    '(Winter|Spring|Summer|Fall)')
seasons = ['Winter', 'Spring', 'Summer', 'Fall']

premieres = anime_df.groupby(
    ['Year', 'Season']).size().reset_index(name='Count')

graph_10 = go.Figure()

for season in seasons:
    season_data = premieres[premieres['Season'] == season]
    graph_10.add_trace(go.Scatter(
        x=season_data['Year'],
        y=season_data['Count'],
        mode='lines+markers',
        name=season,
        line=dict(
            color=px.colors.sequential.Agsunset[seasons.index(season)],
            width=3
        )
    ))

app.layout = html.Div(
    className='main-div',
    children=[
        html.H1(children='Charts about different Animes and Mangas'),

        dcc.Graph(
            className='margin-class',
            id='graph-1',
            figure=graph_1
        ),

        html.Div(
            className='margin-class',
            children=[dcc.Dropdown(
                id='dropdown-ratings',
                options=[
                    {'label': 'Score', 'value': 'score'},
                    {'label': 'Scored By', 'value': 'scored_by'},
                    {'label': 'Rank', 'value': 'rank'},
                    {'label': 'Popularity', 'value': 'popularity'},
                    {'label': 'Members', 'value': 'members'},
                    {'label': 'Favorites', 'value': 'favorites'}],
                value='score'),

                dcc.Graph(
                className='chart',
                id='graph-2',
                figure=graph_2
            )

            ]),

        dcc.Graph(
            className='margin-class',
            id='graph-3',
            figure=graph_3
        ),

        html.Div(
            className='margin-class',
            children=[dcc.Dropdown(id='dropdown-sales',
                                   options=[{'label': 'Sales', 'value': 'sales'},
                                            {'label': 'Sales per Volume', 'value': 'sales_volume'}],
                                   value='sales'),

                      dcc.Graph(
                id='graph-4',
                figure=graph_4
            )
            ]),

        html.Div(
            className='margin-class',
            children=[dcc.Dropdown(id='dropdown-count-scores',
                                   options=[
                                       {'label': '0-1', 'value': '0-1'},
                                       {'label': '1-2', 'value': '1-2'},
                                       {'label': '2-3', 'value': '2-3'},
                                       {'label': '3-4', 'value': '3-4'},
                                       {'label': '4-5', 'value': '4-5'},
                                       {'label': '5-6', 'value': '5-6'},
                                       {'label': '6-7', 'value': '6-7'},
                                       {'label': '7-8', 'value': '7-8'},
                                       {'label': '8-9', 'value': '8-9'},
                                       {'label': '9-10', 'value': '9-10'}],
                                   value='5-6'),

                      dcc.Graph(
                id='graph-5',
                figure=graph_5
            )
            ]),

        html.Div(
            className='margin-class',
            children=[
                html.H2('Treemap'),
                html.Label('X variable'),
                dcc.Dropdown(
                    id='x-var',
                    options=[{'label': col, 'value': col}
                             for col in anime_df.select_dtypes('object').columns],
                    value='status'
                ),
                html.Label('Y variable'),
                dcc.Dropdown(
                    id='y-var',
                    options=[{'label': col, 'value': col}
                             for col in anime_df.select_dtypes('object').columns],
                    value='source'
                ),
                dcc.Graph(id='treemap')
            ]),

        html.Div(
            className='margin-class',
            children=[
                html.H2('Histogram'),
                html.Label('Feature to plot'),
                dcc.Dropdown(
                    id='feature-to-plot',
                    options=[{'label': col, 'value': col}
                             for col in scrapped_df.columns],
                    value='Revenue (Millions)'
                ),
                html.Label('Feature to split'),
                dcc.Dropdown(
                    id='feature-to-split',
                    options=[{'label': col, 'value': col}
                             for col in scrapped_df.columns],
                    value='source'
                ),
                dcc.Graph(id='histogram')
            ]),

        dcc.Graph(
            className='margin-class',
            id='graph-8',
            figure=graph_8
        ),

        dcc.Graph(
            className='margin-class',
            id='graph-9',
            figure=graph_9
        ),

        dcc.Graph(
            className='margin-class',
            id='graph-10',
            figure=graph_10
        )

    ])


@app.callback(
    Output('graph-2', 'figure'),
    Input('dropdown-ratings', 'value'))
def update_graph(value):
    graph_2.update_traces(x=anime_df[value])
    graph_2.update_layout(xaxis={'title': f'{value}'})
    return graph_2


@app.callback(
    Output('graph-4', 'figure'),
    Input('dropdown-sales', 'value')
)
def update_graph_sales(value):
    if value == 'sales':
        graph_4.update_traces(marker=dict(size=scrapped_df['Sales (Million)']))
    elif value == 'sales_volume':
        graph_4.update_traces(marker=dict(
            size=scrapped_df['Average Sales Per Volume (Million)']))

    graph_4.update_layout(xaxis={'title': f'{value}'})
    return graph_4


@app.callback(
    Output('graph-5', 'figure'),
    Input('dropdown-count-scores', 'value')
)
def update_bar_graph(value):
    graph_5.update_yaxes(title_text=value)
    graph_5.update_traces(y=rating_grading_df[value])
    return graph_5


@app.callback(
    Output('treemap', 'figure'),
    Input('x-var', 'value'),
    Input('y-var', 'value')
)
def update_treemap(x_var, y_var):
    grouped_df = anime_df.groupby(
        [y_var, x_var]).size().reset_index(name='Count')
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
    graph_7 = px.histogram(scrapped_df, x=feature_to_plot, color=feature_to_split, nbins=50, histnorm='probability density',
                           color_discrete_sequence=px.colors.sequential.Agsunset)
    graph_7.update_layout(
        title=f'Histogram of {feature_to_plot} splitting by {feature_to_split}',
        xaxis_title=feature_to_plot,
        yaxis_title=feature_to_split,
    )
    return graph_7


if __name__ == '__main__':
    app.run_server(debug=True)
