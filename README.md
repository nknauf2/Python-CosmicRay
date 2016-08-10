# Python-CosmicRay [![](https://circleci.com/gh/onlineth/Python-CosmicRay.svg?&style=shield)](https://circleci.com/gh/onlineth/Python-CosmicRay/)

A Python project to interpret, analyze, and graph Cosmic Ray data files from the Quarknet Cosmic Ray database.

# IMPORTANT NOTES ABOUT THIS REPO
-This code assumes that the file structure is the same as on this repo. It is not difficult to modify but it should be known that running the functions as is without accounting for this will lead to error. This sort of arose out of conveinance for us writting it, but you may prefer a totally different setup.

-On the i2u2 site, DAQ files are given the extensions '.0','.1',... to index files added on the same day. We were not aware of this when we started so we adopted something different. Going from DAQ to threshold it doesn't matter what this number is. When the threshold files are split, this number is changed to 1,2,3,4 to note the channel number! Beware that some of the plotting functions will read this number to give proper labels.

-There should be a guide file that runs through a couple functions to make sure everything is working properly.

-flux.py will bin the data by the same convention of indexing the data by bin middle. flux_time_series.py indexes the flux at the right side of the bin to match it up with the weather observed at that time.
