
import os
import webbrowser
from libraries.get_datas import get_data_from_json
from libraries.layout_dashboard import dashboard_layout
from libraries.models.generateDatas import create_proba, create_heatmap_png

# set path of the project
dirName = os.path.dirname(__file__)

TILE_SIZE = 50

create_proba(dirName, TILE_SIZE)
create_heatmap_png(dirName)

df = get_data_from_json(dirName)
if __name__ == '__main__':
    webbrowser.open_new('http://127.0.0.1:8888/')
    app = dashboard_layout(df, dirName)
    app.run_server(debug=False, port=8888, use_reloader=False)