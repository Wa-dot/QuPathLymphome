from dash import Dash, html, dcc, callback, Output, Input,dash_table
import os, glob
import numpy as np
import pandas
import plotly.express as px
import webbrowser
from PIL import Image
import json
from dash.exceptions import PreventUpdate
from generateDatas import create_proba
import plotly.graph_objects as go

import dash
from dash.dependencies import Input, Output, State
import pandas as pd
import dash_bootstrap_components as dbc

external_stylesheets = [dbc.themes.BOOTSTRAP]

#external_stylesheets = ['assets/style.css']
df = []
web_open = False
dirName = os.path.dirname(__file__)
#récupérer les chemins 

create_proba(dirName)


path_name_image = dirName+"/data/**/*.png"
path_name_data = dirName+"/data/**/*result.json"
print(path_name_data)

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
            data.append(json.loads(json_data))
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)


df = pandas.DataFrame(df)
#ajout de la colonne data
df['data'] =  data
print(df)

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Analyse cliniques"

exit_layout = html.Div(
    className="exit-page",
    children=[
        html.H1("Vous avez quitté l'application..."),
        html.P("Ce site est inaccessible."),
    ]
)

exit_state = False

# Détermination du layout initial en fonction de exit_state
if exit_state:
    initial_layout = exit_layout
else:
    
    initial_layout = html.Div(
    id="app-container",
    children=[
        html.Div([
            html.Button('Exit', id='exit-button'),
            html.H1('Dashboard')
        ]),
        html.Div(id="selection-part", children=[
            html.Div([
                html.H4('Choisissez une image'),
                dcc.Dropdown(df['wsi'].unique(), df['wsi'].unique()[0], id='dropdown-wsi')
            ]),
            html.Div([
                html.H4('Choisissez une annotation'),
                dcc.Dropdown(df['annotation'].unique(), df['annotation'].unique()[0], id='dropdown-annotation')
            ])
        ]),
        html.Div(
            id="main-container",
            children=[
                dcc.Graph(id='images'),
                dcc.Graph(id='heatmap'),
                html.Div([
                    html.H4('Table des résultats'),
                    html.Div([
                        html.H4('Filtrer les lymphomes'),
                        dcc.Checklist(
                            id='lymphome-filter',
                            options=[
                                {'label': 'Lymphomes > 0.5', 'value': 'lymphome_above_0.5'}
                            ],
                            value=[]
                        )
                    ]),
                    html.Div(id='table-container'),
                ]),
            ],
            className="row"
        ),
        dcc.Location(id='url', refresh=False),

        # Ajoutez la boîte de dialogue modale pour la confirmation de fermeture
        dbc.Modal(
            [
                dbc.ModalHeader("Confirmation"),
                dbc.ModalBody("Êtes-vous sûr de vouloir quitter ?"),
                dbc.ModalFooter(
                    [
                        dbc.Button("Annuler", id="close", className="ml-auto"),
                        dbc.Button("Confirmer", id="confirm", className="mr-auto"),
                    ]
                ),
            ],
            id="modal",
            centered=True,
            backdrop="static",
        ),
    ]
)

app.layout = initial_layout 


@app.callback(
    Output("app-container", "children"),
    [Input("confirm", "n_clicks")]
)
def display_exit_page(n_clicks):
    global exit_state
    if n_clicks:
        exit_state = True
        return exit_layout
    else: return app.layout

# Modifiez le callback pour afficher la boîte de dialogue modale
@app.callback(
    [Output("modal", "is_open"), Output('url', 'pathname')],
    [Input("exit-button", "n_clicks"), Input("confirm", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def exit_butt(but1,but2, but3, is_open):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'exit-button' in changed_id:
        return not is_open, None
    elif 'confirm' in changed_id:
        return True, None, os._exit(0)
    else:
        return False, None
    


# Dropdown annotaion part
@app.callback(
    Output("dropdown-annotation", "options"),
    Input('dropdown-wsi', 'value')
)
def update_dropdown(input_value):
    df_wsi = df[df['wsi'] == input_value]
    df_annotation = df_wsi["annotation"].unique().tolist()
    return [{'label': i, 'value': i} for i in df_annotation]

#Dropdown Image part
@app.callback(
    Output('images', 'figure'),
    [Input('dropdown-wsi', 'value'), Input('dropdown-annotation', 'value')]
)
def update_image(wsi, annotation):
    dff = df[df['wsi'] == wsi]
    dff = dff[dff['annotation'] == annotation]
    img_sequence = []
    names = []
    img = np.array(Image.open(dff['path'].iloc[0]).reduce(4))
    img_sequence.append(img)
    names.append(dff['image'].iloc[0])
    img_bis = np.array(Image.open(dff['path'].iloc[0]).reduce(4))
    img_sequence.append(img_bis)
    names.append(dff['image'].iloc[0]+' bis')
    img_sequence = np.stack(img_sequence, axis=0)
        #PROBLEME IL NOUS FAUT LES DIMENSIONS DE LA VRAIE IMAGE POUR FAIRE LE RAPPORT AVEC LA PNG AFIN DE SAVOIR OU POSITIONNER QUELLE TILE SUR LA PNG CAR LES ECHELLE NES SONT PAS LES MEMES
    h_png, w_png = img_sequence.shape[1:3]
    fig = px.imshow(img_sequence, facet_col=0, binary_string=True)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    #set  facet titles
    for i, name in enumerate(names):
        fig.layout.annotations[i]['text'] = name
    return fig



@app.callback(
    Output('heatmap', 'figure'),
    [Input('dropdown-wsi', 'value'), 
     Input('dropdown-annotation', 'value')]
)
def update_heatmap(wsi, annotation):
    dff = df[df['wsi'] == wsi]
    dff = dff[dff['annotation'] == annotation]

    # # Imprimez le DataFrame filtré juste avant d'accéder aux données de la heatmap
    # print("DataFrame filtré (dff) avant de créer la heatmap:")
    # print(dff)

    if not dff.empty:
        annotations = dff['data'].iloc[0]['tiles']

        # Créer un dictionnaire pour stocker les probabilités pour chaque tile_id
        probability_dict = {}

        for annotation in annotations:
            tile_id = annotation['tile_id']
            probability = annotation['lymphome_probability']
            probability_dict[tile_id] = probability

        # Récupérer les coordonnées x, y et les probabilités pour chaque tuile
        x_values = []
        y_values = []
        probabilities = []
        for annotation in annotations:
            tile_id = annotation['tile_id']
            x, y = map(int, tile_id.split('_')[1:])  # Obtenir les coordonnées x et y du tile_id
            x_values.append(x)
            y_values.append(y)
            probabilities.append(probability_dict.get(tile_id, 0))  # Récupérer la probabilité ou 0 si non trouvée
            #print(probabilities)

        heatmap_data = [{
            'z': probabilities,
            'y': y_values,
            'x': x_values,
            'type': 'heatmap',
            'colorscale': 'bluered',
            'colorbar': {'title': 'Probability'},
        }]

        # Déterminer la taille de la heatmap en fonction du nombre de tuiles
        max_x = max(x_values) + 1
        max_y = max(y_values) + 1
        heatmap_width = max_x * 20 # Largeur de chaque tuile supposée être de 50 pixels
        heatmap_height = max_y * 20  # Hauteur de chaque tuile supposée être de 50 pixels

        fig = go.Figure(data=heatmap_data[0])
        fig.update_layout(
            width=heatmap_width,
            height=heatmap_height,
            xaxis=dict(side='top')
        )
        return fig
    else:
        return {'data': [], 'layout': {}}
    

@app.callback(
    Output('table-container', 'children'),
    [Input('dropdown-wsi', 'value'), Input('dropdown-annotation', 'value'), Input('lymphome-filter', 'value')]
)
def update_table(wsi, annotation, filter_value):
    dff = df[df['wsi'] == wsi]
    dff = dff[dff['annotation'] == annotation]
    
    table_data = []
    #RESOLUTION de la table juste ici
    dff.reset_index(drop=True, inplace=True)
    table_data = dff['data'][0]['tiles']
    
    # Création du DataFrame pour afficher les données dans le tableau
    df_table = pandas.DataFrame(table_data)
    
    if 'lymphome_above_0.5' in filter_value:
        df_table = df_table.query('lymphome_probability > 0.9')
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


@app.callback(
    Output('dropdown-annotation', 'value'),
    [Input('dropdown-wsi', 'value')]
)
def update_default_annotation(wsi):
    # Obtenez la première annotation disponible pour l'image sélectionnée
    default_annotation = df[df['wsi'] == wsi]['annotation'].unique()[0]
    return default_annotation

if __name__ == '__main__':
    webbrowser.open_new('http://127.0.0.1:8888/')
    app.run_server(debug=True, port=8888, use_reloader=False)
