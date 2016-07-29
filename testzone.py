from __future__ import division
import pandas as pd
import numpy as np
import scipy.interpolate as inter
import scipy.stats as stat
import functions as f
import jdcal
from pandas.tseries.offsets import Hour, Minute, Second


def create_flux_ts(thresh_file, bin_width, area):
    # start by loading threshold data

    bins = str(int(bin_width/60))+'T'

    names = ['id', 'jul', 'RE', 'FE', 'timeOverThresh']
    skiprows = f.linesToSkip('data/thresh/'+thresh_file+'.thresh')
    df = pd.read_csv('data/thresh/'+thresh_file+'.thresh', skiprows=skiprows, names=names, delim_whitespace=True)

    df['date/times'] = df['jul'] + df['RE']
    start = df['RE'][0] - 0.5
    df['date/times'] = pd.to_datetime(map(f.get_date_time, df['date/times']))
    df.index = df['date/times']

    flux_ts = pd.Series(data=df['timeOverThresh'], index=df.index)

    flux_ts = flux_ts.resample(bins).count() * (1/((bin_width/60)*area))

    offset_hours = (int(bin_width/2) + int(start*86400)) // 3600
    offset_minutes = (int(bin_width/2) + int(start*86400) - offset_hours * 3600) // 60
    offset_seconds = int(bin_width/2) + int(start*86400) - offset_hours * 3600 - offset_minutes * 60
    offset = offset_hours*Hour() + offset_minutes*Minute() + offset_seconds*Second()

    flux_ts.index += offset
