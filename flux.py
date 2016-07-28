# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 15:07:24 2016

@author: Nathan Knauf, Thomas Hein
"""
# Purpose of this script is to take as its input a file for analysis, various
# tools are provided :)
from __future__ import division
import numpy as np
import pandas as pd
import functions as f
from fluxplot import *


def fluxAnalyze(file_name, area, bin_size , from_dir='data/thresh/', to_dir='data/flux/'):
    # function taking in arguments and producing flux files. File name assumed to be of the form ####.####.####.#.thresh
    # area is in square meters, bin size is in seconds
    # Output will be in the form ####.####.####.#.flux

    bin_width = bin_size/86400  # express bin_width in units of days
    # read in data with pandas
    skip_lines = f.linesToSkip(from_dir+file_name)
    df = pd.read_csv(from_dir+file_name, header=None, usecols=[0,1,2,3], names=['id','jul','RE','FE'], delim_whitespace=True,skiprows=skip_lines)

    df['times'] = df['jul'] + df['RE']
    start = df['times'][0]
    stop = df['times'][len(df['times'])-1] + bin_width

    # create the bins array
    bins = []
    count = start
    while count < stop:
        bins.append(count)
        count += bin_width

    # use histogram function for easy binning of data
    hist, edges = np.histogram(df['times'], bins=bins)
    flux = hist/((bin_width*86400/60)*area)
    err = np.sqrt(hist)/((bin_width*86400/60)*area)
    mids = [(edges[j]+edges[j+1])/2 for j in range(len(hist))]

    out_file = open(to_dir + file_name[0:16] + '.flux', 'w')
    out_file.write('#DATE  TIME(UTC)  FLUX(m^-2*min^-1)  ERROR\n')

    # filters out empty bins and bins adjacent to empty bins (which are likely not full). Currently have not written in
    # filtering of file ends, which may be another concern
    for i in range(len(flux)-1):
        if i == 0 and (flux[i] == 0 or flux[i+1] == 0):
            continue
        elif i > 0 and i < (len(flux) - 1) and flux[i-1] == 0 and flux[i] == 0 and flux[i+1] == 0:
            continue

        datetime = f.get_date_time(mids[i])
        line = datetime + ' ' + '{0:.6f} '.format(flux[i]) + '{0:.6f}\n'.format(err[i])
        out_file.write(line)

    out_file.close()
    return to_dir+file_name[0:16]+'.flux'


def FluxMain(file_name, area, bin_size):
    # anticipates .thresh file
    # will immediately call both flux.py and then FluxPlotter
    fluxAnalyze(file_name, area, bin_size)
    FluxPlotter(file_name[0:16]+'.flux')
