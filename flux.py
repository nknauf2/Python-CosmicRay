# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 15:07:24 2016

@author: Nathan Knauf, Thomas Hein
"""
# Purpose of this script is to take as its input a file for analysis, various
# tools are provided
from __future__ import division
import numpy as np
import os
import pandas as pd
from jdcal import jd2gcal
from math import sqrt
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


def frequency_analyze(num, data, bin_width, span, area, firstJD):
    if len(data) != 0:
        throw_out_last = num
        bin_array = [data[0]]

        count = data[0] + bin_width
        while count < (span[1]-bin_width):
            bin_array.append(count)
            count += bin_width

        hist, edges = np.histogram(data, bin_array)

        flux = [i/((bin_width*86400/60)*area) for i in hist]
        error = [sqrt(i)/((bin_width*86400/60)*area) for i in hist]
        text_out = []

        for i in range(len(hist)):
            # these if statements will filter out empty bins and any bins adjacent to empty bins, because they likely are
            # not filled
            write_valid = False
            if i == 0 and hist[i] != 0 and hist[i+1] != 0:
                write_valid = True
            elif i < (len(hist) - 1) and hist[i-1] != 0 and hist[i] != 0 and hist[i+1] != 0:
                write_valid = True
            elif i == (len(hist) - 1) and hist[i] != 0 and hist[i-1] != 0:
                write_valid = True
            if write_valid:
                mid = (edges[i] + edges[i+1])/2
                date, time = get_date_time(mid+firstJD)
                text_out.append(date + ' ' + time + ' ' + '{0:.6f} '.format(flux[i])+'{0:.6f}\n'.format(error[i]))
        if throw_out_last == 0:
            text_out.pop()

        return text_out
    else:
        return ''


def fluxOut(file_name, area, bin_width, file_path=os.getcwd()):
    # takes in full or split thresh file. Right now, split thresh files have extension .[chan]

    bin_width /= 86400  # threshold files are in terms of days, so convert bin size to days

    df = pd.read_csv('data/thresh/'+file_name, header=None, delim_whitespace=True, usecols=[0,1,2,3], names=['id', 'Jul', 'Re', 'Fe'])
    # process data
    [id_num, chan] = str(df['id'][0]).split('.')
    data = []
    day_num = 0
    firstRE = None
    firstJD = None
    bins_per_day = None
    offset = None
    span = None
    out = open('data/flux/'+file_name[:-6]+'flux','w')
    for i in range(len(df['Jul'])):
        if firstRE is None:
            firstRE = df['Re'][i]
        if firstJD is None:
            firstJD = df['Jul'][i]
        if bins_per_day is None:
            bins_per_day = (1 + int(1.0/float(bin_width)))
        if offset is None:
            offset = (bins_per_day) * (bin_width)
        if span is None:
            span = [firstRE + (day_num)*(offset), firstRE + (1+day_num)*(offset)]

        if (df['Jul'][i] - firstJD + df['Re'][i]) <= span[1] and (df['Jul'][i] - firstJD + df['Re'][i]) >= span[0]:
            data.append(df['Re'][i] + df['Jul'][i] - firstJD)
        elif (df['Jul'][i] - firstJD + df['Re'][i]) >= span[1]:
            if (df['Jul'][i] - firstJD + df['Re'][i]) > (span[1] + bin_width):
                text_out = frequency_analyze(1, data, bin_width, span, area, firstJD)
                for line in text_out:
                    out.write(line)
            else:
                text_out = (frequency_analyze(0, data, bin_width, span, area, firstJD))
                for line in text_out:
                    out.write(line)
            data = []
            day_num = int((df['Jul'][i] + df['Re'][i] - firstJD - firstRE)/offset)
            span = [firstRE + (day_num)*offset, firstRE + (1+day_num)*offset]
            data.append(firstRE+df['Jul'][i]-firstJD)
        # elif (df['Jul'][i] - firstJD + df['Re'][i]) < span[0]:
            # error: data not sorted
    text_out = frequency_analyze(1, data, bin_width, span, area, firstJD)
    for line in text_out:
        out.write(line)
    out.close()

fluxOut('6148.2016.0517.1.thresh',0.07742,7200)


