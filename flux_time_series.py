from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import functions as f
import pandas as pd
import scipy.fftpack as fft
from pandas.tseries.offsets import Hour, Minute, Second
from scipy.interpolate import interp1d
from scipy.stats import binned_statistic
import json
from datetime import datetime
dt = datetime


def create_flux_ts(thresh_file, bin_width, area,from_dir='data/thresh/'):
    # creates a time series of flux data
    # returns time series object of flux
    # bin_width is time bin size in seconds, area is area of detector in square meters

    # read in data from threshold file
    names = ['id', 'jul', 'RE', 'FE', 'FLUX']
    skiprows = f.linesToSkip(from_dir + thresh_file + '.thresh')
    df = pd.read_csv(from_dir + thresh_file + '.thresh', skiprows=skiprows, names=names, delim_whitespace=True)

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
    # uses the smoothing function in functions.py to return a series with the data smoothed and the index left alone
    data = series_data.values
    indices = series_data.index

    smooth_data = f.smooth(data, window_len, window)[1]  # uses numpy function convolve
    smooth_ts = pd.Series(data=smooth_data, index=indices)

    return smooth_ts


def join_flux_with_data(flux_ts, Q_data, Q_times, Q_name):
    # creates data frame with flux data and other data of interest and a combined time_series of the two
    # times and data should be the same length
    # times is assumed to be list of datetime objects (could be created using pandas.to_datetime)
    # (IE format is 'YYYY-MM-DD HH:MM:SS'...blame datetime documentation)
    # Q_name is the label you want for the other variable
    # other data will be interpolated in order to determine other values
    # Note: planning to add support for more statistics

    # get the flux_times and data times as julian days for interpolation purposes
    flux_times = [f.JD_from_dt_object(T) for T in flux_ts.index]
    other_times = [f.JD_from_dt_object(T) for T in Q_times]

    # create the interpolating function and interpolated series
    Q_interp = interp1d(other_times, Q_data, fill_value='extrapolate', kind='linear')
    Q_list = Q_interp(flux_times)
    Q_series = pd.Series(data=Q_list, index=flux_ts.index)
    Q_series.name = Q_name

    # create combined series
    combined_ts = pd.concat([Q_series, flux_ts], axis=1, join_axes=[flux_ts.index], keys=[Q_name,'FLUX'])

    return combined_ts


def MainFluxTSA(file_name, area, bin_width, Q_name, Q_data, Q_times, window_len=11, window='hanning', smooth=True,
                from_dir='data/thresh/', to_dir='data/analysis_files/'):
    # Q is other data! Chosen because it's not common/still could be parameter!
    # Opens a thresh file, then calculates flux, bins with Q_data, and writes to a file. Data is smoothed before
    # writing by default. Q is variable that is interpolated to line up with flux,
    # area is detector area in square meters, bin_width is time bin width in seconds. Q_data and Q_times are
    # lists of equal length. Q_times should have data in the
    # form of datetime objects as would be generated by pandas.to_datetime. file_name should be given in the form
    # XXXX.XXXX.XXXX.X
    # Hopefully this will be relaxed to allow other data to be read in from a file, but it is in
    # this form to allow for data to come from any source as long as it has a time attached to it for now

    # get channel and detector ID
    id_num = file_name[0:4]
    channel_num = file_name[-1]

    # get time series and smooth it
    flux_ts = create_flux_ts(file_name, bin_width, area)
    start = flux_ts.index[0]
    end = flux_ts.index[-1]

    # estimate errors
    # first error is the error from binning the flux
    flux_error = [np.sqrt(flux/((bin_width/60)*area)) for flux in flux_ts.values]  # bin error

    # find error in interpolation as approx 0.25* h^2 * Q'' (Q'' is the second derivative of data, h is the difference
    # between the existing data points
    # this is very roughly the leading order error on in the interpolation of the data values

    # need average time step:
    h = (Q_times[-1] - Q_times[0]).total_seconds()/len(Q_times)
    dQ_dt = np.diff(Q_data)/h
    # crude estimate of the derivative of Q (the data)
    d2Q_dt2 = np.mean(np.diff(dQ_dt)/h)
    # VERY crude estimate on the mean of the second derivative of the data
    Q_error = 0.25 * abs(d2Q_dt2) * h
    # used means so it is not a list, same for all values

    if smooth is True:
        flux_ts = smooth_series(flux_ts, window_len, window)

    # analyze flux with other variable
    combined_ts = join_flux_with_data(flux_ts, Q_data, Q_times, Q_name)

    # write file
    out_name = id_num
    if channel_num != '0':
        out_name += '.' + channel_num
    out_name += '.Fluxvs' + Q_name
    out_name += '.flux'
    out_file = open(to_dir+out_name,'w')

    line1 = '#' + 'Flux vs. ' + Q_name + ' ' + id_num
    if channel_num != '0':
        line1 += '.' + channel_num
    line1 += '\n'
    line1 += '#From ' + str(start) + ' to ' + str(end) + '\n'
    out_file.write(line1)
    header = '#' + Q_name + '    '+ Q_name + 'Err'+'      Flux        FluxErr\n'
    out_file.write(header)
    # write lines
    for i in range(len(combined_ts.values)):
        line = '{0:.4f}   '.format(combined_ts[Q_name][i]) + '{0:.6f}   '.format(Q_error) + \
               '{0:.6f}   '.format(combined_ts['FLUX'][i]) + '{0:.6f}\n'.format(flux_error[i])
        out_file.write(line)
    out_file.close()
    return to_dir + out_name


def join_n_series(flux_ts, data_lists, data_times, data_names):
    # Produces a data frame combining flux and other variables through the same methods as join_flux_with data.
    # Data_lists, Data_times, data_names are all lists of lists with corresponding entries. Data_lists
    # contains data to be interpolated, data_times is a list of lists of datetime objects corresponding to the data
    # Returns full data frame with column names according to data_names, indexed the same as the flux_ts

    # allocate empty dictionary
    cols = {}
    # create times over which to interpolate
    interp_times = [f.JD_from_dt_object(T) for T in flux_ts.index]

    # fill dictionary with interpolated data for each variable
    for i in range(len(data_names)):
        other_times = [f.JD_from_dt_object(T) for T in data_times[i]]
        interp_data_func = interp1d(other_times, data_lists[i],fill_value='extrapolate')
        interp_data = interp_data_func(interp_times)
        cols[data_names[i]] = interp_data

    # add flux to the dictionary
    cols['Flux'] = flux_ts.values
    index = flux_ts.index

    # create pandas data frame
    totaldf = pd.DataFrame(cols,index=index)

    return totaldf


def MainFluxTSA_Ndim(file_name, area, bin_width, data_names, data_lists, data_times, window_len=11, window='hanning',
                     smooth=True, from_dir='data/thresh/', to_dir='data/analysis_files/'):
    # same as MainFluxTSA but adds compatibility for multiple other types of data

    # get channel num and detector id
    id_num = file_name[0:4]
    channel = file_name[-1]

    # create and smooth flux time series
    flux_ts = create_flux_ts(file_name, bin_width, area,from_dir=from_dir)
    start = flux_ts.index[0]
    end = flux_ts.index[-1]
    if smooth is True:
        flux_ts = smooth_series(flux_ts,window_len,window)

    # create full data frame
    df = join_n_series(flux_ts, data_lists, data_times, data_names)
    # get flux errors
    Err = [np.sqrt(flux/(area*bin_width/60)) for flux in flux_ts.values]
    df['FluxErr'] = Err
    # write file
    out_name = to_dir + id_num + '.' + channel + '.' + 'flux_variables.flux'
    out = open(out_name,'w')
    line1 = '#Flux vs. '
    for name in data_names:
        line1 += name + ' '
    line1 += '\n'
    out.write(line1)

    line2 = '#From ' + str(start) + ' to ' + str(end) + '\n'
    out.write(line2)

    line3 = '#Date  Time  '
    for name in data_names:
        line3 += name + '  '
    line3 += 'Flux  FluxErr\n'
    out.write(line3)

    for i in range(len(df['Flux'])):
        line = str(df.index[i]) + '  '
        for name in data_names:
            line += '{0:.4f}  '.format(df[name][i])
        line += '{0:.4f}  '.format(df['Flux'][i]) + '{0:.4f}\n'.format(Err[i])
        out.write(line)
    out.close()

    return df


def mean_flux(multiDF, sort_variable):

    flux_list = list(multiDF['Flux'])
    sort_list = list(multiDF[sort_variable])

    hist, edges, nums = binned_statistic(sort_list,flux_list,'mean',bins=sort_list)
    mids = [(edges[i]+edges[i+1])/2 for i in range(hist)]
    return hist, mids


def weather_series(infile, start_end):
    # loads entire weather json weather file into data frame, returns date time range specified by start_end list.
    # list includes calendar date (utc) to start and end inclusive. Uses weather forecast API. Start_end is a list with
    # date time objects used to choose the data frame to be selected. By pandas convention, the ends are included.
    # Currently set to work with API from worldweatheronline.com

    # parse json file
    with open(infile, 'r') as weather:
        parsed = json.load(weather)

    # create dictionary for weather data frame, time lists
    cols = {'tempC': [], 'weatherCode': [], 'precipMM': [], 'humidity': [], 'pressure': [], 'cloudcover': []}
    time_index = []

    # load each dictionary key and index
    for i in range(len(parsed['data']['weather'])):
        for j in range(len(parsed['data']['weather'][i]['hourly'])):
            cols['tempC'].append(parsed['data']['weather'][i]['hourly'][j]['tempC'])
            cols['weatherCode'].append(parsed['data']['weather'][i]['hourly'][j]['weatherCode'])
            cols['precipMM'].append(parsed['data']['weather'][i]['hourly'][j]['precipMM'])
            cols['humidity'].append(parsed['data']['weather'][i]['hourly'][j]['humidity'])
            cols['pressure'].append(parsed['data']['weather'][i]['hourly'][j]['pressure'])
            cols['cloudcover'].append(parsed['data']['weather'][i]['hourly'][j]['cloudcover'])
            date = parsed['data']['weather'][i]['hourly'][j]['UTCdate']
            time = f.num_to_time(parsed['data']['weather'][i]['hourly'][j]['UTCtime'])
            time_index.append(pd.to_datetime(date+' '+time))

    # create data frame
    df = pd.DataFrame(data=cols,index=time_index)
    return df[start_end[0]:start_end[1]]





