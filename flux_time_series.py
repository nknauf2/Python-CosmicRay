from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import functions as f
import pandas as pd
import scipy.fftpack as fft
from jdcal import gcal2jd
from pandas.tseries.offsets import Hour, Minute, Second
from scipy.stats import binned_statistic

def create_flux_ts(thresh_file, bin_width, area):
    # creates a time series of flux data
    # returns time series object of flux
    # bin_width is time bin size in seconds, area is area of detector in square meters

    # read in data from threshold file
    names = ['id', 'jul', 'RE', 'FE', 'FLUX']
    skiprows = f.linesToSkip('data/thresh/' + thresh_file + '.thresh')
    df = pd.read_csv('data/thresh/' + thresh_file + '.thresh', skiprows=skiprows, names=names, delim_whitespace=True)

    # sort by date/times instead of julian days
    df['date/times'] = df['jul'] + df['RE']
    df['date/times'] = pd.to_datetime(map(f.get_date_time, df['date/times']))
    df.index = df['date/times']

    # create time series, sample according to bin_width
    # calculate bins in pandas notation
    bins = str(int(bin_width / 60)) + 'T'
    flux_ts = pd.Series(data=df['FLUX'], index=df.index)
    flux_ts = flux_ts.resample(bins).count() * (1 / ((bin_width / 60) * area))

    # determine offset (basically the bin centers) and add to the index
    start = df['RE'][0] - 0.5
    offset_hours = (int(bin_width / 2) + int(start * 86400)) // 3600
    offset_minutes = (int(bin_width / 2) + int(start * 86400) - offset_hours * 3600) // 60
    offset_seconds = int(bin_width / 2) + int(start * 86400) - offset_hours * 3600 - offset_minutes * 60
    offset = offset_hours * Hour() + offset_minutes * Minute() + offset_seconds * Second()
    flux_ts.index += offset

    # filter out unfilled bins
    for i in range(len(flux_ts)):
        if i == 0 and (flux_ts[i] == 0 or flux_ts[i+1] == 0):
            flux_ts[i] = 'nan'
        if i > 0 and i < len(flux_ts) - 1 and (flux_ts[i-1] == 0 or flux_ts[i] == 0 or flux_ts[i+1] == 0):
            flux_ts[i] = 'nan'
        if i == len(flux_ts) - 1 and (flux_ts[i-1] == 0 or flux_ts[i] == 0):
            flux_ts[i] = 'nan'

    flux_ts = flux_ts.interpolate()

    return flux_ts


# good smoothing function, leaves some jaggedness
def time_series_smoothing(flux_time_series):
    # smooths time series by various methods
    choice = int(raw_input('Use fft smoothing? 1 for yes, 0 for no: '))
    if choice == 1:
        # perform fft and plot frequencies
        rft = fft.rfft(flux_time_series)
        response = 0

        plt.plot(rft)
        plt.show()

        while response == 0:
            new_rft = []
            # allow user to inspect and choose new cutoff frequency. All frequencies above this will be removed
            cutoff = int(raw_input('Choose cutoff frequency: '))
            for i in range(cutoff):
                new_rft.append(rft[i])
            while len(new_rft) < len(rft):
                new_rft.append(0)
            plt.plot(fft.ifft(new_rft))
            plt.show()
            response = int(raw_input('Is this satisfactory? 0 for no, 1 for yes, quit to give up: '))  # if the result is no good, try again
        if response != 'quit':
            flux_time_series = fft.ifft(new_rft)

    choice = int(raw_input('Perform running average smoothing? 0 for no, 1 for yes: '))
    if choice == 1:
        response = 0
        while response == 0:
            span = int(raw_input('Choose time to average over: '))
            flux_rolling_mean = pd.rolling_mean(flux_time_series,span)
            plt.plot(flux_rolling_mean)
            plt.show()
            response = int(raw_input('Is this satisfactory? 0 for no, 1 for yes, quit to give up: '))
        if response != 'quit':
            flux_time_series = flux_rolling_mean

    return flux_time_series


# smoothest smoothing function
def smooth(x,window_len=11,window='hanning'):
    # function to smooth data using window with requested size
    # Method based on convolution of scaled window with signal
    # inputs are x: signal
    #            window_len: odd integer dimension of smoothing window
    #            window: type of window from 'flat','hanning','bartlett','blackman'
    #                    flat window will produce a moving average smoothing
    # output is smoothed signal

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays"
    if x.size < window_len:
        raise ValueError, "input vector needs to be bigger than window size"
    if window_len < 3:
        return x
    if not window in ['flat','hanning','hamming','bartlett','blackman']:
        raise ValueError, "Window is one of flat, hanning, hamming, bartlett, blackman"

    s = np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    # print(len(s))
    if window == 'flat':
        w = np.ones(window_len,'d')
    else:
        w = eval('np.'+window+'(window_len)')

    y = np.convolve(w/w.sum(),s,mode='valid')
    return y, y[(window_len/2-1):-(window_len/2)]


def join_flux_with_data(flux_ts, data, times, key):
    # creates data frame with flux data and other data of interest
    # times and data should be the same length
    # times is assumed to be list of datetime objects (could be created using pandas.to_datetime)
    # key is the label you want for the other variable
    # other_series will be binned the same way as flux and averaged
    # Note: planning to add support for more statistics

    # load data into a series, resample using bins from flux_ts
    other_series = pd.Series(data=data,index=times)
    other_series.name = key

    # bin the data and average
    bin_width = flux_ts.index[1] - flux_ts.index[0]
    other_series = other_series.resample(bin_width).mean()
    bin_offset = flux_ts.index[0] - other_series.index[0]
    other_series.index += bin_offset

    # combine into a single df
    combined_df = pd.concat([flux_ts,other_series])

    return other_series


names = ['sec','rate1','err1','rate2','err2','rate3','err3','rate4','err4','trig','trigerr','pressure','temp','voltage','nGPS']
skiprows = f.linesToSkip('data/bless/6148.2016.0518.0.bless')
datafile = pd.read_csv('data/bless/6148.2016.0518.0.bless',names=names,skiprows=skiprows,delimiter='\t')
dates = []

for i in range(len(datafile['sec'])):
    jd = sum(gcal2jd(2016,5,18))
    datetime = f.get_date_time(jd+datafile['sec'][i]/86400)
    dates.append(datetime)

dates = pd.to_datetime(dates)
datas = datafile['temp']

flux_ts = create_flux_ts('6148.2016.0518.1',900,0.07742)
combine = join_flux_with_data(flux_ts,datas,dates,'temp')
print combine.head()