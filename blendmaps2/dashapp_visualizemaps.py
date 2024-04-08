from dash import Dash, html, dcc, callback, Output, Input
import os, glob
import numpy as np
import pandas
import plotly.express as px
from PIL import Image

df = []
path_name_image = "./**/*.png"
path_name_data = "./**/*.json"
for file_ in glob.glob(path_name_image, recursive = True):
    base, image_name = os.path.split(file_)
    base, annotation = os.path.split(base)
    base, wsi = os.path.split(base)
    df.append({'annotation': annotation, 'wsi': wsi, 'image': image_name, 'path': file_})
    
for file_ in glob.glob(path_name_data, recursive = True):
    base, data = os.path.split(base)
    df.append({'data': data})
    
df = pandas.DataFrame(df)

app = Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(df['wsi'].unique(), df['wsi'].unique()[0], id='dropdown-wsi'),
    dcc.Dropdown(df['annotation'].unique(), id='dropdown-annotation'),
    dcc.Graph(id='images')])

@callback(
    Output("dropdown-annotation", "options"),
    Input('dropdown-wsi', 'value')
)
def update_dropdown(input_value):
    df_wsi = df[df['wsi'] == input_value]
    df_annotation=df_wsi["annotation"].unique()
    return df_annotation


@callback(
    Output('images', 'figure'),
    Input('dropdown-annotation', 'value')
)
def update(wsi, annotation):
    print(df["data"])
    dff = df[df['wsi'] == wsi]
    dff = dff[dff['annotation'] == annotation]

    img_sequence = []
    names = []
    for i, row in dff.iterrows():
        img = np.array(Image.open(row['path']).reduce(4))
        img_sequence.append(img)
        names.append(row['image'])
    img_sequence = np.stack(img_sequence, axis=0)
    
    h, w = img_sequence.shape[1:3]
    fig = px.imshow(img_sequence, facet_col=0, binary_string=True)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    # Set facet titles
    for i, name in enumerate(names):
        fig.layout.annotations[i]['text'] = name

    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8888)
