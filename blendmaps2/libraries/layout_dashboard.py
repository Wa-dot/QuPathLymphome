from dash import Dash, html, dcc, callback, Output, Input,dash_table, callback_context
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import pandas
from PIL import Image
import cv2
import numpy as np
import os

import plotly.graph_objects as go
import plotly.express as px

# Info displayed on the dashboard
DASHBOARD = "Dashboard"
DASHBOARD_TITLE = "Clinics analysis"
DASHBOARD_QUIT = "You have left the application..."
DASHBOARD_UNAVAILABLE = "Website is unavailable."
DASHBOARD_CHOOSE_IMAGE = "Choose an image"
DASHBOARD_CHOOSE_ANNOTATION = "Choose an annotation"
DASHBOARD_ANNOTATION_HEATMAP = "Annotation and Heatmap"
DASHBOARD_OPAQUE = "Set opacity"
DASHBOARD_HTM_2 = "Heatmap"
DASHBOARD_BOXPLOT = "Boxplot of lymphoma probabilities"
DASHBOARD_FILTER = "Filter lymphoma probability by tile"
DASHBOARD_EXIT_BUTTON = "Exit"
DASHBOARD_EXIT_CONFIRM_TEXT = "Are you sure you want to exit?"
DASHBOARD_EXIT_CONFIRM = "Confirm"
DASHBOARD_EXIT_CONFIRMATION = "Confirmation"
DASHBOARD_EXIT_CANCEL = "Cancel"


def dashboard_layout(df, dirName):
    # external_stylesheets = [dbc.themes.BOOTSTRAP]
    external_stylesheets = ['/assets/style.css']
    # Dash app init
    app = Dash(__name__, external_stylesheets=external_stylesheets)
    app.title = DASHBOARD_TITLE
    
    exit_layout = html.Div(
        className="exit-page",
        children=[
            html.H1(DASHBOARD_QUIT),
            html.P(DASHBOARD_UNAVAILABLE),
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
                dbc.Button(DASHBOARD_EXIT_BUTTON, id='exit-button'),
                html.H2(DASHBOARD, className= "title")
            ]),
            html.Div(id="selection-part", children=[
                html.Div([
                    html.H4(DASHBOARD_CHOOSE_IMAGE),
                    dcc.Dropdown(df['wsi'].unique(), df['wsi'].unique()[0], id='dropdown-wsi')
                ]),
                html.Div([
                    html.H4(DASHBOARD_CHOOSE_ANNOTATION),
                    dcc.Dropdown(df['annotation'].unique(), df['annotation'].unique()[0], id='dropdown-annotation')
                ])
            ]),
            html.Div(
                id="main-container",
                children=[
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4(DASHBOARD_ANNOTATION_HEATMAP, className="card-title"),
                                    dcc.Graph(id='images'),
                                    html.Div([
                                        html.H6(DASHBOARD_OPAQUE),
                                        dcc.Slider(id='opacity-slider',
                                            min=0,
                                            max=1,
                                            step=0.01,
                                            marks={i/5: str(i/5) for i in range(11)},
                                            value=0.5)
                                        ])
                                    ])
                            ],className="rounded-3")
                        ], width= 12)
                    ],className="rounded-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4(DASHBOARD_HTM_2, className="card-title"),
                                    html.Div([
                                    dcc.Graph(id='heatmap')
                                    ],style={'display':'flex','align-items': 'center', 'justify-content': 'center','height':'100%'})
                                ]),
                            ], className="h-100"),
                        ], width='50%'),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4(DASHBOARD_BOXPLOT, className="card-title"),
                                    dcc.Graph(id="boxplot")
                                ]),
                            ], className="h-100"),
                        ], width='50%')
                    ], className="align-items-stretch"),
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.H4(DASHBOARD_FILTER),
                                    dcc.Slider(id='lymphome-slider',
                                        min=0,
                                        max=1,
                                        step=0.01,
                                        marks={i/5: str(i/5) for i in range(11)},
                                        value=0.5),
                                        html.Div(id='slider-value-output'),
                                            html.Div(id='table-container'),
                                            ],
                                            className="row"
                                            ),
                                            dcc.Location(id='url', refresh=False),
                                        ],className= "rounded-3"),
                        ])
                    ]),
    
    
            dbc.Modal(
                [
                    dbc.ModalHeader(DASHBOARD_EXIT_CONFIRMATION),
                    dbc.ModalBody(DASHBOARD_EXIT_CONFIRM_TEXT),
                    dbc.ModalFooter(
                        [
                            dbc.Button(DASHBOARD_EXIT_CANCEL, id="close", className="ml-auto"),
                            dbc.Button(DASHBOARD_EXIT_CONFIRM, id="confirm", className="mr-auto"),
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
    # callback : reaction to an input in the dashboard
    # Activate exit page
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

    # Activate exit popup
    @app.callback(
        [Output("modal", "is_open"), Output('url', 'pathname')],
        [Input("exit-button", "n_clicks"), Input("confirm", "n_clicks"), Input("close", "n_clicks")],
        [State("modal", "is_open")],
    )
    def exit_butt(but1,but2, but3, is_open):
        changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        if 'exit-button' in changed_id:
            return not is_open, None
        elif 'confirm' in changed_id:
            return True, None, os._exit(0)
        else:
            return False, None
        


    # Dropdown annotation
    @app.callback(
        Output("dropdown-annotation", "options"),
        Input('dropdown-wsi', 'value')
    )
    def update_dropdown(input_value):
        df_wsi = df[df['wsi'] == input_value]
        df_annotation = df_wsi["annotation"].unique().tolist()
        return [{'label': i, 'value': i} for i in df_annotation]

    #Dropdown Image
    @app.callback(
        Output('images', 'figure'),
        [Input('dropdown-wsi', 'value'), Input('dropdown-annotation', 'value'),Input('opacity-slider','value')]
    )
    def update_image(wsi, annotation,alpha):
        dff = df[df['wsi'] == wsi]
        dff = dff[dff['annotation'] == annotation]
        img_sequence = []
        names = []
        img = np.array(Image.open(dff['path'].iloc[0]).reduce(4))
        img_sequence.append(img)
        names.append(dff['image'].iloc[0])
        
        
        heatmap_path = f'{dirName}/data/{wsi}/{annotation}/{annotation}_heatmap.png'
        heatmap = np.array(Image.open(heatmap_path).reduce(4))
        heatmap_without_alpha = heatmap[:, :, :3]
        
        # Opacity
        alpha = alpha  
        output = cv2.addWeighted(heatmap_without_alpha, alpha, img, 1-alpha, 0)
        img_sequence.append(output)
    
        names.append("Heatmap")
        img_sequence = np.stack(img_sequence, axis=0)
        
        fig = px.imshow(img_sequence, facet_col=0, binary_string=True)
        fig.update_layout(showlegend=False)
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        #set  facet titles
        for i, name in enumerate(names):
            fig.layout.annotations[i]['text'] = name
        return fig


    # Update heatmap
    @app.callback(
        Output('heatmap', 'figure'),
        [Input('dropdown-wsi', 'value'), 
        Input('dropdown-annotation', 'value'),
        ]
    )
    def update_heatmap(wsi, annotation):
        dff = df[df['wsi'] == wsi]
        dff = dff[dff['annotation'] == annotation]
    

        if not dff.empty:
            annotations = dff['data'].iloc[0]['tiles']
            probability_dict = {}

            for annotation in annotations:
                tile_id = annotation['tile_id']
                probability = annotation['lymphome_probability']
                probability_dict[tile_id] = probability
            #Get coordonate x, y and the probability for each tiles
            x_values = []
            y_values = []
            probabilities = []
            for annotation in annotations:
                tile_id = annotation['tile_id']
                x, y = map(int, tile_id.split('_')[1:])
                x_values.append(x)
                y_values.append(y)
                probabilities.append(probability_dict.get(tile_id, 0))  

            heatmap_data = [{
                'z': probabilities,
                'y': y_values,
                'x': x_values,
                'type': 'heatmap',
                'colorscale': 'rdbu',
                'colorbar': {'title': 'Probability'},
            }]

            fig = go.Figure(data=heatmap_data[0])
            fig.update_layout(
                autosize=False,
                width=400,
                height=230,
                margin=dict(l=0, r=0, b=0, t=0),  
                xaxis=dict(side='top'),
                showlegend=False
            )
            return fig
        else:
            return {'data': [], 'layout': {}}
      
    # Update boxplot  
    @app.callback(
        Output('boxplot', 'figure'),
        [Input('dropdown-wsi', 'value'), 
        Input('dropdown-annotation', 'value')]
    )
    def update_boxplot(wsi, annotation):
        dff = df[df['wsi'] == wsi]
        dff = dff[dff['annotation'] == annotation]

        if not dff.empty:
            annotations = dff['data'].iloc[0]['tiles']
            
            # Get lymphomas probabilities
            lymphome_probabilities = [annotation['lymphome_probability'] for annotation in annotations]

            # Create plotbox
            fig = go.Figure(go.Box(y=lymphome_probabilities, name='Probabilité de lymphome'))
            fig.update_layout(title='Boxplot des probabilités de lymphomes')
            return fig
        else:
            return {'data': [], 'layout': {}}


    # Update tab
    @app.callback(
        Output('table-container', 'children'),
        [Input('dropdown-wsi', 'value'), Input('dropdown-annotation', 'value'), Input('lymphome-slider', 'value')]
    )
    def update_table(wsi, annotation, slider_value):
        dff = df[df['wsi'] == wsi]
        dff = dff[dff['annotation'] == annotation]
        
        table_data = []
        dff.reset_index(drop=True, inplace=True)
        table_data = dff['data'][0]['tiles']
        
        df_table = pandas.DataFrame(table_data)
        
        df_table = df_table.query(f'lymphome_probability > {slider_value}')
        
        table = dash_table.DataTable(
            id='table',
            columns=[{'name': col, 'id': col} for col in df_table.columns[1:]],
            data=df_table.to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'minWidth': '50px', 'width': '100px', 'maxWidth': '200px',
                'whiteSpace': 'normal'
            },
            page_size=10,
        )

        return table

    @app.callback(
        Output('slider-value-output', 'children'),
        [Input('lymphome-slider', 'value')]
    )
    def update_slider_value_output(slider_value):
        return f'Valeur actuelle : {slider_value}'
    @app.callback(
        Output('dropdown-annotation', 'value'),
        [Input('dropdown-wsi', 'value')]
    )
    def update_default_annotation(wsi):
        # Obtenez la première annotation disponible pour l'image sélectionnée
        default_annotation = df[df['wsi'] == wsi]['annotation'].unique()[0]
        return default_annotation
    return app
