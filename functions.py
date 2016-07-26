"""
Author: Nathan Knauf, Thomas Hein
"""
import shutil
import os
import datetime as dt
import jdcal
import numpy as np


def get_date_time(julian_day):
    # take in floating Julian day and return a date and time as a single string
    diff = julian_day - 240000.5
    date = jdcal.jd2gcal(240000.5, diff)
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

    return fulldate + ' ' + time


def get_julian_day(date,time):
    # takes date and time and returns fractional julian day
    # date should be written as 'MM/DD/YYYY' or 'MM/DD/YY' and time as 'HH:MM:SS'
    # can also accept seconds with trailing decimals
    month = int(date[0:2])
    day = int(date[3:5])
    year = int(date[6:])
    if len(date[6:]) == 2:
        year += 2000
    jul_day = sum(jdcal.gcal2jd(year,month,day))

    # use 86400 sec/day to calculate partial day
    seconds = float(time[0:2])*3600 + float(time[3:5])*60 + float(time[6:])
    partial = seconds/86400.0

    return jul_day + partial


# function combines desired files in a directory
# file_type is the extension of the form '0.thresh' i.e. must include channel num
# num is the detector number of files to be combined
# dates is a list of starting and ending dates inclusive formatted as ['YYYY.MMDD','YYYY.MMDD'] like in the file name
# from_dir is the directory from which files should be combined
# identifier defaults to __, but may be any string of two characters (limit imposed to make other files read correctly
# to_dir is the directory to save to, will default to data/combined_files
def combine_files(file_type, num, dates, from_dir, identifier='__', to_dir=None):
    while len(identifier) != 2:
        identifier = raw_input('Identifier must be only two characters: ')

    out = num + '.combine' + identifier + '.' + file_type
    if to_dir is None:
        out_name = from_dir + out
    else:
        out_name = to_dir + '/' + out
    header = None
    # turns start and end dates into datetime objects for easy comparison
    start = dt.date(int(dates[0][0:4]),int(dates[0][5:7]),int(dates[0][7:9]))
    stop = dt.date(int(dates[1][0:4]),int(dates[1][5:7]),int(dates[1][7:9]))

    with open(out_name, 'w') as outfile:
        for i in os.listdir(from_dir):
            # flags to filter out unwanted files
            date_valid = False
            content_valid = False

            # check detector number and file type
            if i.endswith(file_type) and i.startswith(num):
                content_valid = True

            # check that date is within date range
            datei = dt.date(int(i[5:9]),int(i[10:12]),int(i[12:14]))
            if datei >= start and datei <=stop:
                date_valid = True


            if date_valid and content_valid:
                with open(from_dir+i, 'r') as readfile:
                    # the following loop will filter out comments from the files
                    iscomment = True
                    while iscomment:
                        pos = readfile.tell()
                        line = readfile.readline()
                        if line.startswith('#'):
                            if header is None:
                                header = line
                                outfile.write(header)
                            continue
                        else:
                            readfile.seek(pos)
                            iscomment = False
                    shutil.copyfileobj(readfile, outfile)

    return out_name


def linesToSkip(file):
    # Give a file, it will return a list of commented lines to skip
    line_list = []
    pos = 0
    with open(file,'r') as f:
        for line in f:
            if line.startswith('#'):
                line_list.append(pos)
                pos += 1
            else:
                break
    return line_list


def peek_line(open_file):
    # reads the current line of a file without changing its state
    pos = open_file.tell()
    line = open_file.readline()
    open_file.seek(pos)
    return line


def get2attr(obj, attr1, attr2, opt_arg=None):
    # helper function, calls getattr twice
    if opt_arg is not None:
        return getattr(getattr(obj, attr1), attr2)(opt_arg)
    if opt_arg is None:
        return getattr(getattr(obj, attr1), attr2)


def is_comment(s):
    # helper function for identifying comments while sorting
    return s.startswith('#')
