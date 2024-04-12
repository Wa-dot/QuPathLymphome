import random
import json
import os

def generate_tile_probabilities(annotation, num_tiles_per_annotation,wsi_folder):
    tile_probabilities = []
    annotation_id = annotation["id"]
    geometry = annotation["geometry"]
    xmin, ymin = geometry["coordinates"][0][0]  # Coin supérieur gauche de l'annotation
    xmax, ymax = geometry["coordinates"][0][2]  # Coin inférieur droit de l'annotation
    width = xmax - xmin
    height = ymax - ymin
    tile_width = width / num_tiles_per_annotation
    tile_height = height / num_tiles_per_annotation
    
    for i in range(num_tiles_per_annotation):
        for j in range(num_tiles_per_annotation):
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
                "ymin": tile_ymin,
                "xmax": tile_xmax,
                "ymax": tile_ymax,
                "lymphome_probability": probability
            })
    
    json_file = {
        "wsi_id":wsi_folder,
        "tiles":tile_probabilities
    }
    return json_file
 

def create_proba(dirName):
    num_tiles_per_annotation =20
    wsi_folders_name = os.listdir(dirName+"/data")

    for wsi_folder in wsi_folders_name:
        annotation_folders_name = os.listdir(f'{dirName}/data/{wsi_folder}')
        for annotation_folder in annotation_folders_name:
            existing_annotation_files = [
            filename for filename in os.listdir(f'{dirName}/data/{wsi_folder}/{annotation_folder}') if filename.endswith('result.json')
            ]
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
                        lymphome_probabilities = generate_tile_probabilities(annotation, num_tiles_per_annotation,
                                                                                 wsi_folder)

                        # Enregistrer les probabilités de lymphomes dans un fichier JSON
                        with open(output_file, 'w') as f:
                            json.dump(lymphome_probabilities, f)

                        print(f'Probabilités aléatoires de présence de lymphomes pour {filename} (annotation) générées et enregistrées dans:', output_file)
            else:
                print(f"Des fichiers d'annotation existent déjà dans le dossier {annotation_folder}. Aucune nouvelle génération de fichiers n'est nécessaire.")
                        