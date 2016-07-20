"""
Author: Nathan Knauf, Thomas Hein
"""


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
