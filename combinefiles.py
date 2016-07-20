"""
Author: Nathan Knauf, Thomas Hein
"""
# This script is for use in combining files of the same type
import shutil
import os
import datetime as dt


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


