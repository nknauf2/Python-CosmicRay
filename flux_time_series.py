from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import functions as f
import pandas as pd
import scipy.fftpack as fft
from pandas.tseries.offsets import Hour, Minute, Second
from scipy.stats import binned_statistic
from statsmodels.tsa.seasonal import seasonal_decompose


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
    flux_ts.name = 'FLUX'

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

        plt.semilogx(rft)
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


def smooth_series(series_data, window_len=11, window='hanning'):
    # uses the smoothing function in functions.py to return a ts with the data smoothed and the index left alone
    data = series_data.values
    indices = series_data.index

    smooth_data = f.smooth(data, window_len, window)[1]
    smooth_ts = pd.Series(data=smooth_data, index=indices)

    return smooth_ts


def join_flux_with_data(flux_ts, data, times, key, bin_width):
    # creates data frame with flux data and other data of interest and a combined time_series of the two
    # times and data should be the same length
    # times is assumed to be list of datetime objects (could be created using pandas.to_datetime)
    # key is the label you want for the other variable
    # other_series will be binned the same way as flux and averaged
    # Note: planning to add support for more statistics

    # load data into a series, resample using bins from flux_ts
    other_series = pd.Series(data=data, index=times)
    other_series.name = key
    # bin the data and average
    bins = str(int(bin_width/60)) + 'T'
    other_series = other_series.resample(bins).mean()
    bin_offset = flux_ts.index[0] - other_series.index[0]
    other_series.index += bin_offset

    # combine into a single ts
    combined_ts = pd.concat([flux_ts, other_series], axis=1, join_axes=[flux_ts.index])
    # create another frame with flux averaged and sorted into regularly spaced bins of the other variable

    binned_flux, edges, counts = binned_statistic(list(combined_ts[key]), list(combined_ts[0]), 'mean', bins=20)
    key_mids = [(edges[i] + edges[i+1])/2 for i in range(len(binned_flux))]
    sorted_df = pd.Series(data=binned_flux, index=key_mids)
    sorted_df = sorted_df.dropna()
    return combined_ts, sorted_df


def tsa_tools(ts_data):
    # performs various functions on a given time series
    return 0


def MainFluxTSA(file_name, area, bin_width, key, other_data, other_times, window_len=11, window='hanning', smooth=True, from_dir='data/thresh/', to_dir='data/analysis_files/'):
    # opens a thresh file, then calculates flux, bins with other data, and writes to a file. Data is smoothed before writing
    # by default. Key is variable to be binned with, area is detector area in square meters, bin_width is flux resolution
    # in seconds. Other_data and other_times are lists of equal length. Other times should have data in the form of datetime
    # objects as would be generated by pandas.to_datetime. file_name should be given in the form ####.####.####.#
    # Hopefully this will be loosened up to allow other data to come from any file, but it is in this form to allow for data
    # to come from any source as long as it has a time attached to it

    # get channel and detector ID
    id_num = file_name[0:4]
    channel_num = file_name[-1]

    # get time series and smooth it
    flux_ts = create_flux_ts(file_name, bin_width, area)
    start = flux_ts.index[0]
    end = flux_ts.index[-1]
    error1 = [np.sqrt(flux/((bin_width/60)*area)) for flux in flux_ts.values]
    average_error = np.mean(error1)

    if smooth is True:
        flux_ts = smooth_series(flux_ts,window_len,window)

    # analyze flux with other variable
    joined_ts = join_flux_with_data(flux_ts, other_data, other_times, key, bin_width)[1]

    # estimate error
    error2 = [np.sqrt(flux/(area*bin_width/60)) for flux in joined_ts.values]
    tot_error = [np.sqrt(average_error**2 + err**2) for err in error2]

    # write file
    out_name = id_num
    if channel_num != '0':
        out_name += '.' + channel_num
    out_name += 'FluxVs' + key
    out_name += '.flux'
    out_file = open(to_dir+out_name,'w')

    line1 = '#' + 'Flux vs. ' + key + ' detector ' + id_num
    if channel_num != '0':
        line1 += '.'+channel_num
    line1 += '\n'
    line1 += '#From ' + str(start) + ' to ' + str(end) + '\n'
    out_file.write(line1)
    header = '#' + key + '      Flux        Error\n'
    out_file.write(header)
    # write lines
    for i in range(len(joined_ts.values)):
        line = '{0:.4f}   '.format(joined_ts.index[i]) + '{0:.6f}   '.format(joined_ts.values[i]) + '{0:.6f}\n'.format(tot_error[i])
        out_file.write(line)
    return to_dir + out_name

