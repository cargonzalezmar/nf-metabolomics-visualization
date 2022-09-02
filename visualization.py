#!/usr/bin/env python

# Libraries

# datta processing
import pandas as pd
import numpy as np

# visualizations
import plotly.graph_objects as go
import plotly.express as px

import re

import os
from glob import glob


from load_data.load_data import LoadData
from graphs.visualizations import *

from dash import Dash, dcc, html, Input, Output
import dash_bio as dashbio

# separador = os.path.sep
# dir_actual = os.path.dirname(os.path.abspath(__file__))
# results_path = separador.join(dir_actual.split(separador)[:-1])

results_path = "./subbset_results"
data = LoadData(results_path)
data.loadConsensus(), data.loadFeatMapsData(), data.loadMSDF()


var_x = "RT"
var_y = "mz"
samples_cols = data.intensity_cons_cols
sample_name = [dict(label=x, value=x) for x in samples_cols]
template = "simple_white"
columns = list(data.intensity_df.columns)
rows = list(data.intensity_df.index)


### Initialize graphs
init_cons_fig = init_consensus_graph()

# df = data.consensus_df

app = Dash(__name__)

app.layout = html.Div(children=[
                html.Div([
                    dcc.Dropdown(
                        id="samples_dropdown",
                        options=sample_name
                    )
                ]),

                html.Div([
                    html.H1(children='Consensus'),
                    dcc.Graph(
                        id="consensus_graph",
                        figure = init_cons_fig
                    )
                ]),

                html.Div([
                    html.H2(children='MS1'),
                    dcc.Graph(
                        id="ms1_graph",
                    )
                ]),

                html.Div([
                    html.H2(children='MS2'),
                    dcc.Graph(
                        id="ms2_graph2",
                    )

                ]),
                html.Div([
                    html.H2(children='MS2'),
                    dcc.Graph(
                        id="ms2_graph",
                    )
                ]),

                html.Div([
                    html.H2(children='Cluster-Heatmap'),
                    dcc.Graph(figure=dashbio.Clustergram(
                            data=data.intensity_df.loc[rows].values,
                            column_labels=columns,
                            row_labels=rows,
                            color_threshold={
                            'row': 250,
                            'col': 700
                            },
                            hidden_labels='row',
                            height=800,
                            width=700
                    ))
                ])
            ])


@app.callback(
    Output("consensus_graph", "figure"), 
    [Input("samples_dropdown", "value")])
def update_consensus_graph(sample_name): 
    df1 = data.consensus_df[data.consensus_df[sample_name]>0]
    df2 = data.consensus_df[data.consensus_df[sample_name]==0]
    fig = create_consensus_graph(df1, df2, sample_name)
    return fig

@app.callback(
    Output("ms1_graph", "figure"), 
    [Input("samples_dropdown", "value")])
def update_ms1_graph(sample_name): 
    feat_maps_df = data.dct_feat_maps_df[sample_name]
    fig = create_ms1_graph(feat_maps_df)
    return fig


@app.callback(
    Output("ms2_graph", "figure"),
    Input("ms1_graph", "hoverData"),
    Input("samples_dropdown", "value"))
def update_ms2_graph(hoverData, sample_name):
    feature_id = hoverData['points'][0]['customdata']
    index_list = data.dct_feat_maps_df[sample_name].loc[feature_id]["MS2_spectra_array"]
    fig = create_ms2_graph(index_list, sample_name)
    return fig

@app.callback(
    Output("ms2_graph2", "figure"),
    Input("ms1_graph", "hoverData"),
    Input("samples_dropdown", "value"))
def update_ms2_graph2(hoverData, sample_name):
    feature_id = hoverData['points'][0]['customdata']
    index_list = data.dct_feat_maps_df[sample_name].loc[feature_id]["MS2_spectra_array"]
    fig = create_ms2_graph2(index_list, sample_name)
    return fig

if __name__=='__main__':
    app.run_server(debug=True)
