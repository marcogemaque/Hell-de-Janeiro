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
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import statsmodels.api as sm

#Create the dataframe
df = pd.read_csv("./static/output.csv")
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
with open('./static/location.json', encoding='utf-8') as json_file:
    locations = json.load(json_file)

#Create a copy so we don't change the original file
df_final = df_out.copy()

#Build the latitude and longitude columns from the json dictionary
df_final['lat'] = df_final['content'].apply(lambda x: locations[x][0])
df_final['lon'] = df_final['content'].apply(lambda x: locations[x][1])
counts = df_final['content'].value_counts()
df_final['size'] = df_final['content'].apply(lambda x: counts[x])

#external stylesheet for dash
external_style = ['./static/stylesheet.css']

#Create the Dash app
app = dash.Dash(__name__, external_stylesheets=external_style)
server = app.server

#Figures created for the dashboard
fig1 = go.Figure(data=go.Scattergeo(
                lon=df_final['lon'],
                lat=df_final['lat'],
                mode='markers',
                text=df_final['content'],
                marker_color=df_final['size'],
                ))
fig1.update_layout(title="Shootings Reported per Location",
                    geo_scope='south america',
                    height=800)

fig2 = px.bar(counts[:10], x=counts[:10].index, y=counts[:10],
        labels={'x':'Neighborhoods','y':"Shooting's count"},
        color=counts[:10].index)
fig2.update_layout(title="Shootings reported by neighborhoods in RJ")

#Prepare the data for the 3rd figure
def prepare_df(df_x, name_nb='Belford Roxo'):
    #Function created to return a dataframe ready for plotting.
    #2 entry variables: original dataframe and neighborhood to filter by
    df_fig = df_x.copy()
    df_fig = df_fig.loc[df_fig['content'] == name_nb]
    df_fig['date'] = df_fig['date'].str[:11]
    df_fig = df_fig.sort_values(by=['date'])
    list_vals = [x for x in range(df_fig.shape[0])] #Create a list with the number of 
    df_fig['counts'] = list_vals
    i = 1 #counter for the loop so we can refer to the previous iteration
    list_dates = [0]
    for x in range(1,df_fig['date'].shape[0]):
        if df_fig['date'].values[i] == df_fig['date'].values[i-1]:
            list_dates.append(list_dates[-1])
            i+=1
        else:
            list_dates.append(x)
            i+=1
    df_fig['date_num'] = list_dates
    return df_fig

df_fig3 = prepare_df(df_final)
fig3 = px.scatter(
    df_fig3, x='date_num',y='counts',
    opacity=0.65,
    trendline='ols',
    trendline_color_override='darkblue'
)

app.layout = html.Div(children=[
    html.H1(children='Hell de Janeiro'),
    html.P("In a world of universal deceipt, telling the truth is a revolutionary act."),
    dcc.Link('Check out the Github', href="https://github.com/marcogemaque", target="_blank"),
    html.Div(
        className="row",
        style={'width':500,'margin':20,'display':'flex'},
    children=[
        html.Div([
            html.H3('Tweets Read'),
            html.P(df_final.shape[0]),
        ], className='six columns',
        style={'margin':20}),
        html.Div([
            html.H3('Last Date Collected'),
            html.P(df_final['date'][0][:4]+"/"+df_final['date'][0][5:7]+'/'+df_final['date'][0][8:10]),
        ], className='six columns',
        style={'margin':20}),
        html.Div([
            html.H3('Oldest Date Collected'),
            html.P(df_final['date'][df_final.shape[0]][:4]+"/"+df_final['date'][df_final.shape[0]][5:7]+'/'+df_final['date'][df_final.shape[0]][8:10]),
        ], className="six columns",
        style={'margin':20}),
    ]),
    dcc.Graph(
        id='main-chart',
        figure=fig1
    ),
    dcc.Graph(
        id='secondary',
        figure=fig2
    ),
    html.H3("Select a neighborhood to visualize the shooting prediction"),
    html.Div([
        "Input: ",
        dcc.Dropdown(id="dropdown",
        options=[
            {'label':i, 'value':i} for i in df_final['content'].unique()
        ]),
    ]),
    dcc.Graph(
        id='third',
        figure=fig3
    ),
])

@app.callback(
    Output('third', 'figure'),
    Input('dropdown','value'))
def update_figure(value):
    df_update = prepare_df(df_final,value)
    fig3 = px.scatter(
        df_update, x='date_num',y='counts',
        opacity=0.65,
        trendline='ols',
        trendline_color_override='darkblue'
    )
    return fig3

if __name__ == '__main__':
    app.run_server(debug=True)