"""
Authors: Luis Vasquez, Nate Knauf
"""

# will need to be modified to return geometry data for a range of dates, exceptions should be raised if flux data is analyzed without
# existing geometry data


def geoExtraction(Filename):
    # prints geometry information. Returns a dictionary containing the entries 'Latitude','Longitude','Altitude',
    # 'Stacked', 'Areas'

    geo_dictionary = {}
    with open(Filename) as f:
        # print data, load dictionary to access arguments in other files
        lines = f.read().splitlines()
        print "Latitude: " + lines[1]
        geo_dictionary['Latitude'] = lines[1]

        print "Longitude: " + lines[2]
        geo_dictionary['Longitude'] = lines[2]

        print "Altitude: " + lines[3]
        geo_dictionary['Altitude'] = lines[3]

        if (lines[4] == "1"): # indicate if detectors are stacked
            print "Stacked"
            geo_dictionary['Stacked'] = True
        else:
            print "Not Stacked"
            geo_dictionary['Stacked'] = False
        # load areas
        Area = []
        for i in range(5, 9):
            digits = lines[i].split()
            Area.append(float(digits[3]))
        print "Areas:", Area
        geo_dictionary['Areas'] = Area
    return geo_dictionary

