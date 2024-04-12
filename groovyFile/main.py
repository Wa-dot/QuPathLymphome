import os
import json
import random
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from glob import glob
import webbrowser
# Fonction pour générer les probabilités aléatoires de présence de lymphomes pour chaque tuile
def generate_tile_probabilities(num_tiles):
    tile_probabilities = []
    for _ in range(num_tiles):
        # Générer une probabilité aléatoire de présence de lymphome pour chaque tuile
        probability = random.uniform(0, 1)
        tile_probabilities.append({
            "tile_id": generate_unique_tile_id(),
            "lymphoma probability": probability
        })
    return tile_probabilities
# Fonction pour générer un identifiant unique pour chaque tuile
# Counter for generating unique tile IDs
tile_id_counter = 0
def generate_unique_tile_id():
    global tile_id_counter
    tile_id_counter += 1
    return str('tile' + str(tile_id_counter))
# Fonction pour générer les probabilités aléatoires de présence de lymphomes pour chaque annotation
def generate_lymphoma_probabilities(annotation, num_probabilities, num_tiles_per_annotation):
    lymphoma_probabilities = []
    for _ in range(num_probabilities):
        annotation_probabilities = {
            "annotation_id": annotation["id"],  # Ajouter l'identifiant de l'annotation
            "tiles": generate_tile_probabilities(num_tiles_per_annotation)  # Générer les probabilités de lymphomes pour chaque tuile
        }
        lymphoma_probabilities.append(annotation_probabilities)
    return lymphoma_probabilities
# Fonction pour enregistrer les probabilités des lymphomes dans un fichier JSON
def save_lymphoma_probabilities(lymphoma_probabilities, output_file):
    with open(output_file, 'w') as f:
        json.dump(lymphoma_probabilities, f)
def main():
    # Chemin du répertoire contenant les fichiers d'annotations
    annotations_directory = 'C:/Users/Computer/Desktop/Projet/QuPathLymphome/blendmaps2/data'
    # Chemin du répertoire de sortie pour les fichiers de probabilités de lymphomes
    output_directory = 'C:/Users/Computer/Desktop/Projet/QuPathLymphome/blendmaps2/data'
    # Nombre de probabilités à générer pour chaque annotation
    num_probabilities = 1
    num_tiles_per_annotation = 10
    # Parcourir tous les fichiers JSON dans le répertoire des annotations
    for filename in os.listdir(annotations_directory):
        if filename.endswith('.json'):
            annotation_file = os.path.join(annotations_directory, filename)
            # Lire les annotations à partir du fichier JSON
            with open(annotation_file, 'r') as f:
                annotations = json.load(f)
            # Parcourir chaque annotation dans la liste
            for idx, annotation in enumerate(annotations):
                output_file = os.path.join(output_directory, f'{os.path.splitext(filename)[0]}_{idx}_lymphoma_probabilities.json')
                # Générer les probabilités de lymphomes pour cette annotation
                lymphoma_probabilities = generate_lymphoma_probabilities(annotation, num_probabilities,num_tiles_per_annotation)
                # Enregistrer les probabilités de lymphomes dans un fichier JSON
                save_lymphoma_probabilities(lymphoma_probabilities, output_file)
                print(f'Probabilités aléatoires de présence de lymphomes pour {filename} (annotation {idx}) générées et enregistrées dans:', output_file)
    # Charger les fichiers JSON de probabilités de lymphomes
    json_files = glob(os.path.join(output_directory, '*.json'))
    # Concaténer les données de tous les fichiers JSON
    all_data = []
    for file in json_files:
        with open(file, 'r') as f:
            data = json.load(f)
            all_data.extend(data)
    # Convertir les données en DataFrame pandas
    df = pd.DataFrame(all_data)
    # Initialiser l'application Dash
    app = dash.Dash(__name__)
    # Layout du tableau de bord
    app.layout = html.Div([
        dcc.Dropdown(
            id='annotation-dropdown',
            options=[{'label': f'Annotation {idx}', 'value': idx} for idx in df.index if isinstance(df.loc[idx, 'annotation_id'], str)],
            value=df.index[0]  # Valeur par défaut
        ),
        dcc.Graph(id='lymphoma-probabilities-graph'),
        html.Button('Exit', id='exit-button')  # Bouton pour quitter
    ])
    # Callback pour mettre à jour le graphique en fonction de la sélection de l'annotation
    @app.callback(
        Output('lymphoma-probabilities-graph', 'figure'),
        [Input('annotation-dropdown', 'value')]
    )
    def update_graph(selected_annotation_idx):
        selected_annotation_id = df.loc[selected_annotation_idx, 'annotation_id']
        selected_tiles = df.loc[selected_annotation_idx, 'tiles']
        # Si les tuiles ne sont pas vides, on les utilise pour le graphique
        if isinstance(selected_tiles, list):
            tiles_df = pd.DataFrame(selected_tiles)
            # Créer un graphique
            fig = px.line(tiles_df, x='tile_id', y='lymphoma_probability',
                          title=f'Probabilités de lymphomes pour l\'annotation {selected_annotation_idx}',
                          labels={'tile_id': 'Tuile', 'lymphoma_probability': 'Probabilité de lymphome'},
                          markers=True,  # Afficher des points
                          line_shape='linear')  # Utiliser des lignes droites entre les points
        else:
            # Si aucune tuile n'est présente, on crée un graphique vide
            fig = px.scatter(title=f'Aucune tuile disponible pour l\'annotation {selected_annotation_id}')
        return fig
    # Callback pour gérer le clic sur le bouton Exit
    @app.callback(
        Output('exit-button', 'n_clicks'),
        [Input('exit-button', 'n_clicks')]
    )
    def exit_button_click(n_clicks):
        if n_clicks:
            os._exit(0)  # Ferme l'application
        return None  # Réinitialise le nombre de clics à None après la sortie

   # Fonction pour ouvrir automatiquement la fenêtre du navigateur
    def open_browser():
        webbrowser.open_new('http://127.0.0.1:8050/')
    # Lancer l'application sur un serveur local
    if __name__ == '__main__':
        open_browser()
        app.run_server(debug=True)
if __name__ == '__main__':
    main()