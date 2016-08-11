#Pandas with parsed, weather data acquisition#

import numpy as np
import matplotlib.pyplot as plt
import os.path
import functions as f
import json as js

with open('/Users/kevinbryson/Desktop/anaconda/Weather-Data.js', 'r') as Weather:
        parsed = js.load(Weather)

print parsed['data']['weather'][0]['hourly'][0]['UTCdate']

f.num