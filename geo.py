
# will need to be modified to return geometry data for a range of dates, exceptions should be raised if flux data is analyzed without
# existing geometry data
def geoExtration(Filename):
    with open(Filename) as f:
        lines = f.read().splitlines()
        print "Latitude: " + lines[1]
        print "Longitude: " + lines[2]
        print "Altitude: " + lines[3]
        if (lines[4] == "1"):
            print "Stacked"
        else:
            print "Not Stacked"
        Area = []
        for i in range(5, 9):
            digits = lines[i].split()
            Area.append(digits[3])
        print "Areas:", Area
    return 1
