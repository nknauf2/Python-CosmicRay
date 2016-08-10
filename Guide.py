# This program exists to do a short test drive of the functions with an included data file to ensure that everything is
# running as intended.
import threshold
import flux_time_series
from datetime import datetime
import fluxplot


# First, a DAQ file will be read and a threshold file will be written. I will create a new folder for this to appear in
# so it doesn't overwrite the existing files. This way the user can compare the two.
fn = '6148.2016.0613.0'
threshold.AllThresholdFiles(fn,path='test_folder/')

# The result should be a new folder appearing in your working directory called 'test_folder/' with the following
# files inside '6148.2016.0613.0.thresh', '6148.2016.0613.1.thresh', '6148.2016.0613.2.thresh', '6148.2016.0613.3.thresh',
# '6148.2016.0613.4.thresh'
# These are the threshold files for each channel.

# Now, let's take this with some weather data from the same location (zip code 60510), and create a binned flux file
# First let's get some weather
weather_file = 'data/weather_data/June60510.js'
weather = flux_time_series.weather_series(weather_file,[datetime(2016,6,13),datetime(2016,6,14)])

# For the next function to work, we must put the names of the variables we want, their times, and their values in
# separate lists like so
times = [list(weather.index), list(weather.index)]
names = ['tempC', 'pressure']
data = [list(weather['tempC'].values),list(weather['pressure'].values)]
area = 0.07742
# Now write all of this to a file
flux_time_series.MainFluxTSA_Ndim('6148.2016.0613.1',area,3600,names,data,times,from_dir='test_folder/',to_dir='test_folder/')

# Finally, let's see a plot of Flux vs. Pressure
new_file = '6148.1.flux_variables.flux'
fluxplot.plot_flux_vs_Q(new_file,'tempC',path='test_folder/',pathexport='test_folder/')
