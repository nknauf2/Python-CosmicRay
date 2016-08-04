import glob
from flux import FluxMain

# Program that asks a user what data file you would like to access and then opens the corresponding flux plot

options = []
for newfile in glob.glob('data/thresh/*'):
    options.append(newfile[19:27])
x = len(options)
while x > 0:
    if options[x-1][0].isalpha():
        options.remove(options[x-1])
    else:
        options[x-1] = options[x-1][3:5]+"/"+options[x-1][5:7]+"/"+options[x-1][0:2]
    x -= 1
print list(set(options))

# finds the files that have a date attached and shows which dates you can choose from

date = raw_input("Which date would you like data from?\n")

# asks what date you would like the data for

if date[6:] == "15":
    threshfile = "6432.20"
elif date[6:] == "16":
    threshfile = "6148.20"
else:
    threshfile = 0
threshfile += date[6:]
threshfile += "."
threshfile += date[:2]
threshfile += date[3:5]

# creates filename string with date

datachoice = []
for choice in glob.glob('data/thresh/'+threshfile+'*'):
    datachoice.append(choice)
print datachoice

# shows options for files with that date

specific = raw_input("which file would you like to access\n\t0 through "+str(len(datachoice)-1)+"\n")

threshfile += "."
threshfile += specific
threshfile += ".thresh"

# converts given date and chosen file into filename

print threshfile
FluxMain(threshfile, 1, 60)

# displays file name and opens flux graph
