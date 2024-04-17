import random
import json
import os
import numpy as np
from PIL import Image
import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go
def generate_tile_probabilities(annotation, tile_size,num_tiles_width,num_tiles_height,wsi_folder):
    tile_probabilities = []
    annotation_id = annotation["id"]
    geometry = annotation["geometry"]
    xmin, ymin = geometry["coordinates"][0][0]  # Coin supérieur gauche de l'annotation
    xmax, ymax = geometry["coordinates"][0][2]  # Coin inférieur droit de l'annotation
    width = xmax - xmin
    height = ymax - ymin
    tile_width = tile_size
    tile_height = tile_size
    
    for i in range(num_tiles_width):
        for j in range(num_tiles_height):
            tile_xmin = xmin + i * tile_width
            tile_ymin = ymin + j * tile_height
            tile_xmax = xmin + (i + 1) * tile_width
            tile_ymax = ymin + (j + 1) * tile_height
            # Calculer la probabilité de présence de lymphome pour chaque tuile
            probability = random.uniform(0, 1)
            tile_probabilities.append({
                "annotation_id": annotation_id,
                "tile_id": f"tile_{i}_{j}",
                "x":i,
                "y":j,
                "xmin": tile_xmin,
                "xmax": tile_xmax,
                "ymin": tile_ymin,
                "ymax": tile_ymax,
                "lymphome_probability": probability
            })
    
    json_file = {
        "wsi_id":wsi_folder,
        "tiles":tile_probabilities
    }
    return json_file

def calculate_num_tiles(image_path, tile_size):
    with Image.open(image_path) as img:
        width, height = img.size
        print("width :"+str(width) +"\n height: "+str(height))
        num_tiles_width = (width//4)//tile_size
        num_tiles_height = (height//4)//tile_size
    return num_tiles_width , num_tiles_height



def create_proba(dirName, tile_size):
    wsi_folders_name = os.listdir(dirName+"/data")

    for wsi_folder in wsi_folders_name:
        annotation_folders_name = os.listdir(f'{dirName}/data/{wsi_folder}')
        for annotation_folder in annotation_folders_name:
            existing_annotation_files = [
            filename for filename in os.listdir(f'{dirName}/data/{wsi_folder}/{annotation_folder}') if filename.endswith('result.json')
            ]
            existing_heatmap_files = [
            filename for filename in os.listdir(f'{dirName}/data/{wsi_folder}/{annotation_folder}') if filename.endswith('heatmap.png')
            ]
            if not existing_heatmap_files:
                for filename in os.listdir(dirName+"/data/"+wsi_folder+"/"+annotation_folder):
                    if filename.endswith('.png'):
                        print("filename: "+filename)
                        num_tiles_width,num_tiles_height = calculate_num_tiles(f'{dirName}/data/{wsi_folder}/{annotation_folder}/{filename}', tile_size)
                        

            if not existing_annotation_files:  # Si aucun fichier d'annotation n'existe
                for filename in os.listdir(dirName+"/data/"+wsi_folder+"/"+annotation_folder):
                    if filename.endswith('.json'):
                        # Lire les annotations à partir du fichier JSON
                        with open(f'{dirName}/data/{wsi_folder}/{annotation_folder}/{filename}', 'r') as f:
                            annotation = json.load(f)
                        # print("annotation: "+annotation)
                        filename = filename.split('.')[0]
                        
                        output_file = f'{dirName}/data/{wsi_folder}/{annotation_folder}/{filename}_result.json'

                        # Générer les probabilités de lymphomes pour cette annotation
                        lymphome_probabilities = generate_tile_probabilities(annotation,tile_size, num_tiles_width, num_tiles_height,wsi_folder)

                        # Enregistrer les probabilités de lymphomes dans un fichier JSON
                        with open(output_file, 'w') as f:
                            json.dump(lymphome_probabilities, f)

                        print(f'Probabilités aléatoires de présence de lymphomes pour {filename} (annotation) générées et enregistrées dans:', output_file)
            else:
                print(f"Des fichiers d'annotation existent déjà dans le dossier {annotation_folder}. Aucune nouvelle génération de fichiers n'est nécessaire.")



def create_heatmap_png(dirName, tile_size):
    wsi_folders_name = os.listdir(dirName + "/data")

    for wsi_folder in wsi_folders_name:
        annotation_folders_name = os.listdir(f'{dirName}/data/{wsi_folder}')
        for annotation_folder in annotation_folders_name:
            existing_heatmap_files_result = [
                filename for filename in os.listdir(f'{dirName}/data/{wsi_folder}/{annotation_folder}') if filename.endswith('result.json')
            ]
            existing_heatmap_files_heatmap = [
                filename for filename in os.listdir(f'{dirName}/data/{wsi_folder}/{annotation_folder}') if filename.endswith('heatmap.png')
            ]
            
            if not existing_heatmap_files_heatmap:
                df = None  # Initialisation de df à l'extérieur des conditions
                for filename in os.listdir(dirName+"/data/"+wsi_folder+"/"+annotation_folder):
                    if filename.endswith('.png'):
                        annotation_image_path = f'{dirName}/data/{wsi_folder}/{annotation_folder}/{filename}'
                        with Image.open(annotation_image_path) as img:
                            annotation_width, annotation_height = img.size
            if not existing_heatmap_files_heatmap:
                for filename in os.listdir(dirName+"/data/"+wsi_folder+"/"+annotation_folder):
                    if filename.endswith('result.json'):
                        # Lire les annotations à partir du fichier JSON
                        with open(f'{dirName}/data/{wsi_folder}/{annotation_folder}/{filename}', 'r') as f:
                            annotation_result = json.load(f)
                        # Convertir le JSON en DataFrame
                        df = pd.json_normalize(annotation_result['tiles'])
                        print(df)
                        
                        if df is not None and not df.empty:  # Vérification supplémentaire de df
                            # Créer un dictionnaire pour stocker les probabilités pour chaque tile_id
                            probability_dict = {}
                            x_values = []
                            y_values = []
                            probabilities = []

                            for index, row in df.iterrows():
                                tile_id = row['tile_id']
                                probability = row['lymphome_probability']
                                probability_dict[tile_id] = probability
                                tile_id = row['tile_id']
                                x, y = map(int, tile_id.split('_')[1:])  # Obtenir les coordonnées x et y du tile_id
                                x_values.append(x)
                                y_values.append(y)
                                probabilities.append(probability_dict.get(tile_id, 0))  # Récupérer la probabilité

                            heatmap_data = [{
                                'z': probabilities,
                                'y': y_values,
                                'x': x_values,
                                'type': 'heatmap',
                                'colorscale': 'rdbu',
                            }]

                            # Créer la figure
                            fig = go.Figure(data=heatmap_data)

                            # Mise en page de la figure
                            fig.update_layout(
                                autosize=False,
                                width=annotation_width,
                                height=annotation_height,
                                margin=dict(l=0, r=0, b=0, t=0),  # Ajuster les marges pour enlever les bords blancs
                                xaxis=dict(visible=False),  # Cacher l'axe x
                                yaxis=dict(visible=False),  # Cacher l'axe y
                                showlegend=False, # Cacher la légende
                                margin_autoexpand=False
                            )

                            print(f'{dirName}/data/{wsi_folder}/{annotation_folder}/{annotation_folder}_heatmap.png')
                            # Enregistrer l'image au format PNG
                            
                            try:
                                pio.write_image(fig, f'{dirName}/data/{wsi_folder}/{annotation_folder}/{annotation_folder}_heatmap.png')
                                print("Image créée avec succès")
                            except Exception as e:
                                print(f"Une erreur s'est produite lors de la création de l'image : {str(e)}")
                        

    
    