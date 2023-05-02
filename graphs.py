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

def webscrapping(anime_df):

    # Send an HTTP request to the web page and get the HTML content
    url = 'https://en.wikipedia.org/wiki/List_of_best-selling_manga'
    response = requests.get(url)
    html = response.content

    # Parse the HTML using Beautiful Soup and find all the tables with a given class
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table', {'class': 'wikitable'})

    # Convert each HTML table into a pandas DataFrame and store them in a list
    dfs = []
    for table in tables:
        df = pd.read_html(str(table))[0]
        df.columns.values[7] = 'Average sales per volume'
        dfs.append(df)

    anime_df["Revenue (Millions)"] = 0.0
    anime_df["Sales per volume"] = 0.0

    final_scrapp = pd.concat(dfs)

    anime_df['title_lower'] = anime_df['title'].str.lower()
    final_scrapp['title_lower'] = final_scrapp['Manga series'].str.lower()

    final_anime = anime_df.merge(final_scrapp, on='title_lower', how='inner')

    final_anime['Sales (Million)'] = final_anime['Approximate sales'].str.extract(
        r'^([\d\.]+)', expand=False)
    final_anime['Average Sales Per Volume (Million)'] = final_anime['Average sales per volume'].str.extract(
        r'^([\d\.]+)', expand=False)

    return final_anime

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
anime_df = pd.read_csv('anime_filtered.csv', sep=',')
scrapped_df = webscrapping(anime_df)

# use pivot_table method to create new dataframe with counts
df_counts = pd.pivot_table(anime_df, index='type', columns='source', aggfunc='size', fill_value=0).reset_index()

graph_1 = px.bar(df_counts, x='type', y=['4-koma manga', 'Book', 'Card game', 'Digital manga', 'Game',
       'Light novel', 'Manga', 'Music', 'Novel', 'Original', 'Other',
       'Picture book', 'Radio', 'Unknown', 'Visual novel', 'Web manga'], title='Count of sources by type of show')

# graph 2
graph_2 = px.strip(anime_df, x='score', y='rating', color='airing', custom_data=['title'], hover_data={'title': True})

# Third graph
graph_3 = px.violin(anime_df, y="score", x="airing", color="status", box=True,
                    points="all", hover_data=anime_df.columns)


# Fourth graph
# TODO add changes to visualize different 
scrapped_df['Sales (Million)'] = scrapped_df['Sales (Million)'].astype('float')
scrapped_df['Average Sales Per Volume (Million)'] = scrapped_df['Average Sales Per Volume (Million)'].astype('float')

graph_4 = px.scatter(scrapped_df, x = "score", y = "scored_by", size = "Sales (Million)", color = "source",
           hover_name = "title", log_x = True, size_max = 60)

app.layout = html.Div(children=[
    html.H1(children='Charts about different Animes and Mangas'),

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
        id='graph-1',
        figure=graph_1
    ),

    dcc.Graph(
        id='graph-3',
        figure=graph_3
    ),

    dcc.Graph(
        id='graph-4',
        figure=graph_4
    )

])

@app.callback(
    Output('graph-2', 'figure'),
    Input('dropdown-ratings', 'value'))

def update_graph(value):

    if value == 'score':
        graph_2.update_traces(x=anime_df['score'])
    elif value == 'scored_by':
        graph_2.update_traces(x=anime_df['scored_by'])
    elif value == 'rank':
        graph_2.update_traces(x=anime_df['rank'])
    elif value == 'popularity':
        graph_2.update_traces(x=anime_df['popularity'])
    elif value == 'members':
        graph_2.update_traces(x=anime_df['members'])
    elif value == 'favorites':
        graph_2.update_traces(x=anime_df['favorites'])

    graph_2.update_layout(xaxis={'title': f'{value}'})
    return graph_2


if __name__ == '__main__':
    app.run_server(debug=True)
