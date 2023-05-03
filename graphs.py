# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import requests
import pandas as pd
from bs4 import BeautifulSoup
import statsmodels.api as sm

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
    
    final_anime['Sales (Million)'] = final_anime['Sales (Million)'].astype('float')
    final_anime['Average Sales Per Volume (Million)'] = final_anime['Average Sales Per Volume (Million)'].astype('float') * 100
    
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
    anime_df['score_bin'] = pd.cut(anime_df['score'], bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    rating_grading_df = anime_df.pivot_table(index='rating', columns='score_bin', values='title', aggfunc='count').reset_index()
    rating_grading_df.columns = ['rating', '0-1', '1-2', '2-3', '3-4', '4-5', '5-6', '6-7', '7-8', '8-9', '9-10']

    return rating_grading_df

# creation of dataframes
anime_df = pd.read_csv('anime_filtered.csv', sep=',')
scrapped_df = web_scraper(anime_df)

# Graph #1
df_counts = pd.pivot_table(anime_df, index='type', columns='source', aggfunc='size', fill_value=0).reset_index()
graph_1 = px.bar(df_counts, x='type', y=SOURCES, title='Count of sources by type of show')

# Graph #2
graph_2 = px.strip(anime_df, x='score', y='rating', color='airing', custom_data=['title'], hover_data={'title': True})

# Graph #3
graph_3 = px.violin(anime_df, y="score", x="airing", color="status", box=True,
                    points="all", hover_data=anime_df.columns)

# Graph #4
graph_4 = px.scatter(scrapped_df, x = "score", y = "scored_by", size = "Sales (Million)", color = "source",
           hover_name = "title", log_x = True, size_max = 40)

# Graph #5
rating_grading_df = discrete_intervals(anime_df)
graph_5 = px.bar(rating_grading_df, x='rating', y='5-6')

app.layout = html.Div(children=[
    html.H1(children='Charts about different Animes and Mangas'),

    dcc.Graph(
        id='graph-1',
        figure=graph_1
    ),

    html.Div([

        dcc.Dropdown(
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
        id='graph-2',
        figure=graph_2
    )

    ]),

    dcc.Graph(
        id='graph-3',
        figure=graph_3
    ),

    html.Div([
        dcc.Dropdown(id='dropdown-sales',
                    options=[{'label': 'Sales', 'value': 'sales'},
                             {'label': 'Sales per Volume', 'value': 'sales_volume'}],
                             value='sales'),

        dcc.Graph(
            id='graph-4',
            figure=graph_4
        )
    ]),

    html.Div([

        dcc.Dropdown(id='dropdown-count-scores',
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
    ])

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
        graph_4.update_traces(marker=dict(size=scrapped_df['Average Sales Per Volume (Million)']))

    graph_4.update_layout(xaxis={'title': f'{value}'})
    return graph_4

@app.callback(
    Output('graph-5', 'figure'),
    Input('dropdown-count-scores', 'value')
)

def update_bar_graph(value):
    graph_5.update_traces(y=rating_grading_df[value])
    return graph_5

if __name__ == '__main__':
    app.run_server(debug=True)
