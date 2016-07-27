# all functions having to do with the rebinning of flux data with another variable
# NOTE THIS FILE IS CURRENTLY BEING SET ASIDE
from __future__ import division
import pandas as pd
import functions as f
import scipy.stats as stat
import numpy as np
from scipy.interpolate import interp1d
from seasonal import fit_seasons, adjust_seasons
import matplotlib.pyplot as plt
import jdcal

def filter_and_interpolate(x,y):
    # given some flux data y and some time data x, filters out unfilled bins, then creates an interpolator function
    #  Returns array of flux values with filtered data replaced by interpolated values
    filtered_x = []  # filter out unfilled bins
    filtered_y = []
    indices = [] # these are the indices that will be replaced
    for i in range(len(y)):
        if i == 0 and (y[i] == 0 or y[i+1] == 0):
            indices.append(i)
            continue
        elif i > 0 and i < (len(y) - 1) and (y[i-1] == 0 or y[i] == 0 or y[i+1] == 0):
            indices.append(i)
            continue
        elif i == len(y) - 1 and (y[i-1] == 0 or y[i] == 0):
            indices.append(i)
            continue
        else:
            filtered_x,append(x[i])
            filtered_y.append(y[i])

    interp_func = interp1d(filtered_x,filtered_y,kind='linear',bounds_error=False,fill_value='extrapolate')
    # populate new list with unfilled bins replaced
    new_y = []
    for i in range(len(x)):
        if i not in indices:
            new_y.append(y[i])
        else:
            new_y.append(interp_func(x[i]))

    return new_y


def collect_bins(file_name, time_res, area, bin_width, other_variable, other_times, key, outfile=None):
    # time_res is the width of time bins, file_name is intended to be a thresh file but typed without '.thresh'
    # other_variable and other_variable_time are lists. Times are JULIAN DAYS!
    # key is the name of the variable of interest. Bin_width is the bin width for the key variable
    # writes data to a file, returns list of binned flux and bin centers of key variable

    skiprows = f.linesToSkip('data/thresh/' + file_name + '.thresh')
    # read in flux data frame
    flux_df = pd.read_csv('data/thresh/'+file_name + '.thresh', header=None, delim_whitespace=True, names=['id','jul','RE','FE','timeover'], skiprows=skiprows)
    flux_df['times'] = flux_df['jul'] + flux_df['RE']
    # read in other data

    # create time bins
    start = flux_df['times'][0]
    stop = flux_df['times'][len(flux_df['jul'])-1]
    time_bins = []
    # convert time resolution to days
    time_res /= 86400

    count = start
    while count < stop + time_res:
        time_bins.append(count)
        count += time_res

    # bin flux
    hist,time_edges = np.histogram(flux_df['times'], time_bins)
    flux = hist/((time_res*86400/60)*area)
    # sort other variable into bins
    key_means, time_edges, nums = stat.binned_statistic(other_times, other_variable, 'mean',bins=time_bins)

    time_mids = [(time_bins[i]+time_bins[i+1])/2 for i in range(len(hist))]
    # bin mean flux and mean of key variable
    key_bins = []
    start = min(key_means)
    stop = max(key_means)
    count = start
    while count < stop + bin_width:
        key_bins.append(count)
        count += bin_width

    # filter out unfilled bins, then interpolate them
    interp_flux = filter_and_interpolate(time_mids, flux)
    # bin other variable and flux

    binned_flux,var_edges,nums = stat.binned_statistic(key_means, interp_flux, 'mean', bins=key_bins)
    key_mids = [(key_bins[i]+key_bins[i+1])/2 for i in range(len(binned_flux))]

    # approximate errors
    flux_errors = np.sqrt(binned_flux/((time_res*86400/60)*area))
    var_errors = np.sqrt(key_means)
    tot_errors = [np.sqrt(flux_errors[i]**2 + var_errors[i]**2) for i in range(len(flux_errors))]

    # write to file
    if outfile is None:
        outfile = file_name[:4] + 'flux' + '.' + 'vs'+key + '.flux'
    out = open('data/flux/' + outfile, 'w')
    out.write('#Flux  ' + key + '  Error\n')
    for i in range(len(binned_flux)):
        line = '{0:.6f}'.format(binned_flux[i]) + '  ' + '{0:.6f}'.format(key_mids[i]) + '  {0:.6f}\n'.format(tot_errors[i])
        out.write(line)
    out.close()

    return binned_flux, key_mids


def make_stationary(data):
    # data as a stationary time series
    seasons,trend = fit_seasons(data)
    adjusted = adjust_seasons(data,seasons=seasons)
    residual = adjusted-trend

    return residual,seasons,trend


skiprows = f.linesToSkip('data/bless/6148.2016.0518.0.bless')
names=['sec','rate1','err1','rate2','err2','rate3','err3','rate4','err4','trigrate','trigerr','pressure','temp','voltage','nGPS']
df = pd.read_csv('data/bless/6148.2016.0518.0.bless',names=names,delimiter='\t',header=None,skiprows=skiprows)
other_times = []
temps = []
for i in range(len(df['sec'])):
    other_times.append(sum(jdcal.gcal2jd(2016,5,18))+int(df['sec'][i])/86400)
    temps.append(df['temp'][i])

flux, mids = collect_bins('6148.2016.0518.1',1800,0.07742,.2,temps,other_times,'temp')
plt.plot(mids,flux)
plt.show()