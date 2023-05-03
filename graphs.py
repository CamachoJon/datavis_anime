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
scrapped_df['Average Sales Per Volume (Million)'] = scrapped_df['Average Sales Per Volume (Million)'].astype('float') * 100

graph_4 = px.scatter(scrapped_df, x = "score", y = "scored_by", size = "Sales (Million)", color = "source",
           hover_name = "title", log_x = True, size_max = 40)

# fifth Graph
# bin the score column into discrete intervals
anime_df['score_bin'] = pd.cut(anime_df['score'], bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# create a pivot table to count the number of shows by rating and score interval
rating_grading_df = anime_df.pivot_table(index='rating', columns='score_bin', values='title', aggfunc='count').reset_index()
rating_grading_df.columns = ['rating', '0-1', '1-2', '2-3', '3-4', '4-5', '5-6', '6-7', '7-8', '8-9', '9-10']

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
