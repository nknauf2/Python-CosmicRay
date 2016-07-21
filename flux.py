# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 15:07:24 2016

@author: Nathan Knauf, Thomas Hein
"""
# Purpose of this script is to take as its input a file for analysis, various
# tools are provided
from __future__ import division
import numpy as np
import pandas as pd
from jdcal import jd2gcal
from fluxplot import FluxPlotter

def get_date_time(julian_day):
    # take in floating Julian day and return a date and time
    diff = julian_day - 240000.5
    date = jd2gcal(240000.5, diff)
    year = str(date[0])
    month = str(date[1])
    day = str(date[2])
    if len(month) == 1:
        month = '0' + month
    if len(day) == 1:
        day = '0' + day

    secs = int(round(date[3]*86400))
    hr = secs//3600
    minute = (secs - hr * 3600) // 60
    sec = secs - 3600*hr - 60*minute
    hr = str(hr)
    minute = str(minute)
    sec = str(sec)
    if len(sec) == 1:
        sec = '0' + sec
    if len(minute) == 1:
        minute = '0' + minute
    if len(hr) == 1:
        hr = '0' + hr

    fulldate = month + '/' + day + '/' + year
    time = hr + ':' + minute + ':' + sec

    return fulldate, time


def fluxAnalyze(file_name, area, bin_size , from_dir='data/thresh/', to_dir='data/flux/'):
    # function taking in arguments and producing flux files. File name is assumed to be of the form ####.####.####.#.thresh.
    # area is in square meters, bin size is in seconds
    # Output will be in the form ####.####.####.#.flux

    bin_width = bin_size/86400  # express bin_width in units of days
    # read in data with pandas
    df = pd.read_csv(from_dir+file_name, header=None, usecols=[0,1,2,3], names=['id','jul','RE','FE'], delim_whitespace=True)

    df['times'] = df['jul'] + df['RE']
    start = df['times'][0]
    stop = df['times'][len(df['times'])-1] + bin_width

    # create the bins array
    bins = []
    count = start
    while count < stop:
        bins.append(count)
        count += bin_width

    hist, edges = np.histogram(df['times'], bins=bins)
    flux = hist/((bin_width*86400/60)*area)
    err = np.sqrt(hist)/((bin_width*86400/60)*area)
    mids = [(edges[j]+edges[j+1])/2 for j in range(len(hist))]

    out_file = open(to_dir + file_name[0:16] + '.flux', 'w')
    out_file.write('#DATE  TIME(UTC)  FLUX(m^-2*min^-1)  ERROR\n')
    for i in range(len(flux)):
        write_valid = False
        if i == 0 and flux[i] != 0 and flux[i+1] != 0:
            write_valid = True
        elif i > 0 and i < (len(flux) - 1) and flux[i-1] != 0 and flux[i] != 0 and flux[i+1] != 0:
            write_valid = True
        elif i == (len(flux)-1) and flux[i-1] != 0 and flux[i] != 0:
            write_valid = True
        if write_valid:
            date, time = get_date_time(mids[i])
            line = date + ' ' + time + ' ' + '{0:.6f} '.format(flux[i]) + '{0:.6f}\n'.format(err[i])
            out_file.write(line)

    out_file.close()
    return to_dir+file_name[0:16]+'.flux'


def FluxMain(file_name, area, bin_size):
    # anticipates .thresh file
    # will immediately call both flux.py and then FluxPlotter
    fluxAnalyze(file_name, area, bin_size)
    FluxPlotter(file_name[0:16]+'.flux')


