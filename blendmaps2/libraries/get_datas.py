
import glob, json, os
import pandas
from libraries.models.generateDatas import create_proba,create_heatmap_png

PATH_IMAGE = "/data/**/*.png"
PATH_JSON_RESULT = "/data/**/*result.json"
HEATMAP = "heatmap.png"

def get_data_from_json(dirName):
    df = []
    web_open = False
    tile_size = 50

    path_name_image = dirName + PATH_IMAGE
    path_name_data = dirName + PATH_JSON_RESULT

    data = []    

    for file_ in glob.glob(path_name_image, recursive = True):
        if not file_.endswith(HEATMAP):
            base, image_name = os.path.split(file_)
            base, annotation = os.path.split(base)
            base, wsi = os.path.split(base)
            if not image_name: image_name = None
            if not annotation: annotation = None
            if not wsi: wsi = None
            df.append({'annotation': annotation, 'wsi': wsi, 'image': image_name, 'path': file_})
        

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
    return df
