from dash import Dash, html, dcc, callback, Output, Input,dash_table
import os, glob
import numpy as np
import pandas
import plotly.express as px
import webbrowser
from PIL import Image
import json
from dash.exceptions import PreventUpdate
from generateDatas import create_proba_json

external_stylesheets = ['assets/style.css']
df = []
web_open = False

path_name_image = "C:/Users/Computer/Desktop/Projet/QuPathLymphome/blendmaps2/data/**/*.png"
# path_name_annotation = "C:/Users/tom62/Desktop/QuPathLymphome/blendmaps2/data/**/*.json"
# path_name_wsifolders = "C:/Users/tom62/Desktop/QuPathLymphome/blendmaps2/"
# create_proba_json(path_name_wsifolders,path_name_annotation)
path_name_data = "C:/Users/Computer/Desktop/Projet/QuPathLymphome/blendmaps2/data/**/*result.json"


for file_ in glob.glob(path_name_image, recursive = True):
    base, image_name = os.path.split(file_)
    base, annotation = os.path.split(base)
    base, wsi = os.path.split(base)
    df.append({'annotation': annotation, 'wsi': wsi, 'image': image_name, 'path': file_})

data = []    
for file_ in glob.glob(path_name_data, recursive=True):
    try:
        with open(file_, "r") as json_file:
            json_data = json_file.read()
            # print("JSON data read:", json_data)  # Add this line to inspect the data
            data.append(json.loads(json_data))
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)


df = pandas.DataFrame(df)
#ajout de la colonne data
df['data'] =  data
print(df)
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Analyse cliniques"
app.layout = html.Div(
    id="app-container",
    children=[
    html.Div([
       html.Button('Exit', id='exit-button'),
       html.H1('Dashboard')
    ]),
    html.Div(id="selection-part",children=[
        html.Div([
           html.H4('Choisissez une image'),
           dcc.Dropdown(df['wsi'].unique(), df['wsi'].unique()[0],       id='dropdown-wsi')
        ]),
        html.Div([
           html.H4('Choisissez une annotation'),
           dcc.Dropdown(df['annotation'].unique(),df['annotation'].unique()[0] , id='dropdown-annotation')
        ])
    ]),
    html.Div(
    id="main-container",
    children=[
       dcc.Graph(id='images'),
       html.Div([
          html.H4('Table des résultats'),
          html.Div([
              html.H4('Filtrer les lymphomes'),
              dcc.Checklist(
                id='lymphoma-filter',
                options=[
                   {'label': 'Lymphomes > 0.5', 'value': 'lymphoma_above_0.5'}
                ],
                value=[]
              )
            ]),    
          html.Div(id='table-container'),
       ]),
       dcc.Location(id='url', refresh=False)
    ])
])
    
#Dropdown annotaion part
@callback(
    Output("dropdown-annotation", "options"),
    Input('dropdown-wsi', 'value')
)
def update_dropdown(input_value):
    df_wsi = df[df['wsi'] == input_value]
    df_annotation=df_wsi["annotation"].unique()
    return df_annotation

#Dropdown Image part
@callback(
    Output('images', 'figure'),
    [Input('dropdown-wsi', 'value'), Input('dropdown-annotation', 'value')]
)
def update_image(wsi, annotation):
    dff = df[df['wsi'] == wsi]
    dff = dff[dff['annotation'] == annotation]
    print(dff)
    img_sequence = []
    names = []
    for i, row in dff.iterrows():
        img = np.array(Image.open(row['path']).reduce(4))
        img_sequence.append(img)
        names.append(row['image'])
    # print(dff['data'][0]['tiles']['tile_id'=="tile_0_0"])
    img_sequence = np.stack(img_sequence, axis=0)
    #PROBLEME IL NOUS FAUT LES DIMENSIONS DE LA VRAIE IMAGE POUR FAIRE LE RAPPORT AVEC LA PNG AFIN DE SAVOIR OU POSITIONNER QUELLE TILE SUR LA PNG CAR LES ECHELLE NES SONT PAS LES MEMES
    h_png, w_png = img_sequence.shape[1:3]
    
    fig = px.imshow(img_sequence, facet_col=0, binary_string=True)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    # Set facet titles
    for i, name in enumerate(names):
        fig.layout.annotations[i]['text'] = name

    return fig

#Table part
@callback(
    Output('table-container', 'children'),
    [Input('dropdown-wsi', 'value'), Input('dropdown-annotation', 'value'), Input('lymphoma-filter', 'value')]
)
def update_table(wsi, annotation,filter_value):
    dff = df[df['wsi'] == wsi]
    dff = dff[dff['annotation'] == annotation]
    
    table_data = []
    #RESOLUTION de la table juste ici
    dff.reset_index(drop=True, inplace=True)
   
    table_data = dff['data'][0]['tiles']
    # Création du DataFrame pour afficher les données dans le tableau
    df_table = pandas.DataFrame(table_data)
    
    if 'lymphoma_above_0.5' in filter_value:
        df_table = df_table.query('lymphoma_probability > 0.9')
    # Création du composant DataTable
    table = dash_table.DataTable(
        id='table',
        columns=[{'name': col, 'id': col} for col in df_table.columns[1:]],
        data=df_table.to_dict('records'),
        style_table={'overflowX': 'auto'},  # Permet de faire défiler horizontalement si le tableau est trop large
        style_cell={
            'textAlign': 'left',
            'minWidth': '50px', 'width': '100px', 'maxWidth': '200px',
            'whiteSpace': 'normal'
        },
        page_size=10,
            # Nombre d'éléments par page
    )

    return table

# Callback pour gérer le clic sur le bouton Exit
@app.callback(
    Output('url', 'pathname'),
    [Input('exit-button', 'n_clicks')]
)
def exit_button_click(n_clicks):
    if n_clicks:
        os._exit(0)  # Ferme l'application
        return None

if __name__ == '__main__':
    web_open : webbrowser.open_new('http://127.0.0.1:8888/')
    app.run(debug=True, port=8888, use_reloader=False)
