"""
Author: Thomas Hein, Nathan Knauf, & Luis
"""
import plotly.plotly as py
from plotly.graph_objs import *
import numpy as np
import pandas as pd
import sys
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import math
import functions as f


def FluxPlotter(filename, path='data/flux/', pathexport='graphs/flux/', plotTitle='$$$$$'):
    if plotTitle == '$$$$$':
        if filename[:4].isdigit() and filename[4] == '.':
            plotTitle = 'Flux Plot for detector '+str(filename[:4])
            if filename[15] != "0":
                plotTitle += " channel "+filename[15]
        else:
            plotTitle = 'Flux Plot for '+filename

    skiprows = f.linesToSkip(path+filename)

    df = pd.read_csv(path+filename, skiprows=skiprows, header=None, delim_whitespace=1)

    """
    df[0] means date
    df[1] means time
    df[2] means flux
    df[3] means error
    """

    upper_bound = Scatter(
        name='Upper Error Bound',
        x=df[0]+' '+df[1],
        y=df[2]+df[3],
        mode='lines',
        marker=dict(color="444"),
        line=dict(width=0),
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty')

    trace = Scatter(
        name='Flux',
        x=df[0]+' '+df[1],
        y=df[2],
        mode='lines',
        line=dict(color='rgb(31, 119, 180)'),
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty')

    lower_bound = Scatter(
        name='Lower Error Bound',
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
        title=plotTitle,
        xaxis=dict(
            range=[0, 10],
            title='Date Time (UTC)',
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        ),
        yaxis=dict(
            title='Flux (events/60s*m^2)',
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )))
    fig = dict(data=data, layout=layout)
    plot(fig, filename=pathexport+filename+'_plot.html')
    return pathexport+filename+'_plot.html'
