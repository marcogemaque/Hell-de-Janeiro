#import packages
import pandas as pd
import numpy as np
import re
import json

#import dash
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

#Create the dataframe
df = pd.read_csv('output.csv')
df = df.drop(['Unnamed: 0'], axis=1) #Drop the first column containing unnamed axis

#Regex the hell outta the dataframe
"""
So this is how things are going to be.
1) Create regex expression to filter dataframe
2) Get indexes of filtered entries by regex
3) On to the next regex expression, remove the indexes from the previous created regex
"""

#Standard Local: xxx, Rio de Janeiro or Local: xxx
df_out = df.copy()
df_out['content'] = df['content'].str.split(r"\s*Local:", expand=True)[1]
df_out['content'] = df_out['content'].str.split(r"\s*Rio de Janeiro|\n", expand=True)[0]
df_out['content'] = df_out['content'].str.replace(r"^\s", "")
df_out = df_out.dropna()

#Regex to prepare our data
df_out['content'] = df_out['content'].str.replace(r"^\s", "") #replaces blank space ahead
df_out['content'] = df_out['content'].str.replace(r"\s$", "") #replaces blank space at the end or dot
df_out['content'] = df_out['content'].apply(lambda x: x.split("(")[0] if "(" in x else x) #removes everything after "("
df_out['content'] = df_out['content'].apply(lambda x: x.split("-")[0] if "-" in x else x) #removes everything after "-"
df_out['content'] = df_out['content'].apply(lambda x: x.split("/")[0] if "/" in x else x) #removes everything after "/"
df_out['content'] = df_out['content'].apply(lambda x: x.split(".")[0] if "." in x else x) #removes everything after "."
df_out['content'] = df_out['content'].apply(lambda x: x.split(",")[0] if "," in x else x) #removes everything after ","
df_out['content'] = df_out['content'].apply(lambda x: x.split(r" Rio de J")[0] if " Rio de J" in x else x) #removes everything after " Rio de Jan"
df_out['content'] = df_out['content'].apply(lambda x: x.split(r" e ")[0] if " e " in x else x) #removes everything after " e "
df_out['content'] = df_out['content'].apply(lambda x: x.rstrip()) #removes whitespace at the end of the string

#Drop values which are equivalent to ''
empties = df_out.loc[df_out['content'] == '']
empties = empties.index.tolist()
df_out = df_out.drop(empties)

#Import dictionary with geolocations
with open('location.json', encoding='utf-8') as json_file:
    locations = json.load(json_file)

#Create a copy so we don't change the original file
df_final = df_out.copy()

#Build the latitude and longitude columns from the json dictionary
df_final['lat'] = df_final['content'].apply(lambda x: locations[x][0])
df_final['lon'] = df_final['content'].apply(lambda x: locations[x][1])
counts = df_final['content'].value_counts()
df_final['size'] = df_final['content'].apply(lambda x: counts[x])

#Create the Dash app
app = dash.Dash(__name__)

fig = px.scatter(df_final, x="lat", y="lon", size='size')

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Hell de Janeiro: Unaccustomed to reality.
    '''),

    dcc.Graph(
        id='main-chart',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)