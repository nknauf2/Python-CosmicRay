"""
Author: Nathan Knauf, Thomas Hein
"""
import shutil
import os
import datetime as dt
import jdcal


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
    # Give a file, it will return the number of lines that have # at the beginning
    f = open(file, 'r')
    lines = f.readlines()
    numberWithContent = 0
    for currentLine in lines:
        numberWithContent += 1
        if currentLine[:1] != "#":
            break
    f.close()
    return numberWithContent - 1


def whisper(open_file):
    # reads the current line of a file without changing its state
    pos = open_file.tell()
    line = open_file.readline()
    open_file.seek(pos)
    return line


def get_date_time(julian_day):
    # take in floating Julian day and return a date and time
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

    return fulldate, time