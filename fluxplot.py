import plotly.plotly as py
from plotly.graph_objs import *
import numpy as np
import pandas as pd
import sys
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import math


def FluxPloter(filename, path='data/flux/', pathexport='graphs/flux/'):

    df = pd.read_csv(path+filename, header=None, delim_whitespace=1)

    """
    df[0] means date
    df[1] means time
    df[2] means flux
    df[3] means error
    """

    upper_bound = Scatter(
        name='Upper Bound',
        x=df[0]+' '+df[1],
        y=df[2]+df[3],
        mode='lines',
        marker=dict(color="444"),
        line=dict(width=0),
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty')

    trace = Scatter(
        name='Measurement',
        x=df[0]+' '+df[1],
        y=df[2],
        mode='lines',
        line=dict(color='rgb(31, 119, 180)'),
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty')

    lower_bound = Scatter(
        name='Lower Bound',
        x=df[0]+' '+df[1],
        y=df[2]-df[3],
        marker=dict(color="444"),
        line=dict(width=0),
        mode='lines')

    # Trace order can be important
    # with continuous error bars
    data = [lower_bound, trace, upper_bound]

    layout = dict(
        height=800,
        width=1500,
        title='Plot for '+filename,
        xaxis=dict(range=[0, 10]))
    fig = dict(data=data, layout=layout)
    plot(fig, filename=pathexport+filename+'_plot.html')
