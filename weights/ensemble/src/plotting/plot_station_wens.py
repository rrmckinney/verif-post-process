import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import pandas as pd
import numpy as np
import re
import os

#### INPUT ##########

station_output = '/home/verif/verif-post-process/weights/ensemble/output-100/'
#station_output = '/home/verif/verif-post-process/weights/sliding_window/output/weekly/'

input_file = '/home/verif/verif-post-process/input/station_list_small_loc.csv'

score = 'MAE'
var = 'SFCTC_KF'
wens = 'VLFk100'
file_insert = 'seasonal'
title = 'Temperature (KF) [°C]'
#title = 'Wind Speed (KF) [km/hr]'
#title = 'Precipitation [mm/hr]'
cb_title = r'$MAE_{VLFk100} - MAE_{SREF}$'
##### FUNCTIONS ######
def convert(deg):
    a,b,c,d,e,f,g = re.split('[ \'"°]',deg)
    ans = float(a) + (float(b.strip("'")) / 60) + (float(d.strip('"')) / 3600)
    return float(ans)

def get_latlon(input_file):
    locs = pd.read_csv(input_file)

    lats = locs['Latitude']
    lons = locs['Longitude']

    for l in range(len(lats)):

        lats[l] = convert(lats[l])
        lons[l] = convert(lons[l])*-1

    lons=lons.to_numpy()
    lats=lats.to_numpy()
    return(locs,lats,lons)

def get_station_data(locs):
    plot_diff = []
    stations = locs['Station ID']
    for s in stations:
        f = station_output+score+'_'+var+'_'+file_insert+'_'+str(s)+'.txt'
        if os.path.isfile(f):
            dat = pd.read_csv(station_output+score+'_'+var+'_'+file_insert+'_'+str(s)+'.txt',sep = "\s+|,")
            dat.columns = ['start','end','ENS_W','ENS_M']
            diff = np.nanmean(abs(dat['ENS_W'])-abs(dat['ENS_M']))
            plot_diff.append(diff)
        else:
            diff = np.nan
            plot_diff.append(diff)
    return(plot_diff)
    
def mk_plot(lats,lons,plot_diff):

    fig = plt.gcf()
    fig.set_size_inches(8,6.5)
    plt.rcParams.update({'font.size': 16})

    m = Basemap(projection='merc', \
            llcrnrlat=48, urcrnrlat=51, \
            llcrnrlon=-126, urcrnrlon=-120, \
            lat_ts=20, \
            resolution='h')

    #m.bluemarble(scale=1)   # full scale will be overkill
    m.drawcoastlines(color='white', linewidth=0.2)  # add coastlines
    m.drawmapboundary(fill_color='lightgrey')
    m.fillcontinents(color='darkgrey', lake_color='gray')
    #m.etopo(scale=0.5, alpha=0.5)

    x, y = m(lons, lats)

    sc = plt.scatter(x, y,50,marker='o',edgecolors='black',c=plot_diff,zorder=4,cmap='RdBu')
    fig.colorbar(sc,label = cb_title)
    plt.title(title)
    plt.savefig('map_'+wens+'_'+score+'_'+var)

##### RUN FUNCTIONS #####

locs, lats, lons = get_latlon(input_file)
plot_diff = get_station_data(locs)
print(plot_diff)
mk_plot(lats,lons,plot_diff)

########################
