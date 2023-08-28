#!/usr/bin python

"""
Created on Tue Jun 1 2021

@author: evagnegy

This script creates a T, P, and wind speed meterogram for every station.

"""

import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime, timedelta
import sys
import time
import math
import copy
import shutil
import sqlite3
import pandas as pd
###########################################################
### -------------------- FILEPATHS ------------------------
###########################################################

#path to save the log/output
logfilepath = "/home/verif/verif-post-process/bin/log/ibcs_meteogram.log"

#location to save the images
save_folder = '/www/results/verification/images/ibcs_meteograms/'
#save_folder = '/scratch/egnegy/verification/python_plots/station_plots/'

#location where obs files are (all textfiles should be in this directory)
obs_filepath = "/verification/Observations/"

#location where forecast files are (immediately within this directory should be model folders, then grid folders, then the textfiles)
fcst_filepath = '/verification/ibcs/ibcs/'

#description file for stations
station_file = '/home/verif/verif-post-process/input/station_list.txt'


###########################################################
### -------------------- INPUT ------------------------
###########################################################

# takes an input date should be date (YYMMDD) as a 
if len(sys.argv) == 2:
    date_entry = sys.argv[1]    #input date YYMMDD
    start_date = str(date_entry)
    input_date = datetime.strptime(start_date, "%y%m%d").date()

else:
    raise Exception("Invalid input entries")
 
  
# =============================================================================
# # list of strings of the station IDs
# stations = np.loadtxt(station_file,usecols=0,delimiter=',',dtype='str')
# 
# # info about the stations used in plot titles
# stations_longname = np.loadtxt(station_file,usecols=1,delimiter=',',dtype='str')
# stations_shortname = np.loadtxt(station_file,usecols=2,delimiter=',',dtype='str')
# 
# # makes the plot titles from the long names, short names, and station IDs
# station_names = [long + ' (' + short + ':' + ID + ')' for long, short, ID in zip(stations_longname, stations_shortname, stations)]
# 
# # variables to read and plot
# variables = ['SFCTC', 'APCP', 'SFCWSPD']
# yaxis_labels = ['2m Temperature [C]', 'Accumulated Precipitation [mm]', 'Wind Speed [km/hr]']
# =============================================================================

# this section is for testing purposes 
stations = ['3510']

# needs to be in same order as list above
station_names = ['UBC ESB Rooftop (UBC_RS:3510)']

variables = ['SFCTC', 'APCP', 'SFCWSPD']
yaxis_labels = ['2m Temperature [C]', 'Accumulated Precipitation [mm]', 'Wind Speed [km/hr]']



# ENS currently isn't saved as output
models = ['NAM/AWIP32','GFS/GFS0p25','GFS/GFS0p5']
legend_labels =  ['NAM-AWIP32','GFS0p25','GFS0p5']


#colors to plot, must be same length (or longer) than models
model_colors = ['C0','C1','C2']

#these are the stations that only record precip data every 6 hours
precip6hrs_stations = ['597','604','583','600','606','601','607','610','612','603']

# num of days to go forward on plot
days = 10  

### --------------------------------------------------------------------------------------
# turns any missing data (valued at -999) into NaNs
# these plot as gaps 
# also turns bad data into NaNs
def remove_missing_data(data):
    
    #finds forecast values that are equal to -999 or bad data thats really large
    for i in range(len(data)):
        if data[i] == -999 or abs(data[i]) > 10000: 
            print("      removing datapoint: " + str(data[i]))
            data[i] = np.nan           
            
    return(data)

# this removes any fcst data where the obs is not recorded
def remove_missing_obs(fcst, obs):
    
    if len(fcst) > len(obs):
        length = len(obs)
    else:
        length = len(fcst)
        
    for i in range(length):        
        if math.isnan(obs[i]) == True:
            fcst[i] = np.nan
                
    return(fcst)

# a function that takens in a list and returns True if the list contains all consecutive numbers
# this is used to make sure theres no missing files for each set of variable/model/grid/station
def checkConsecutive(hours_list):
    return sorted(hours_list) == list(range(min(hours_list), max(hours_list)+1))


# this function accumulates every 6 hours (skipping the first hour)
# so there is a 6hr cum. sum at 6:00, 12:00, 18:00, 24:00 etc
def accum_6hr(fcst):
    fcst_acc6hr = np.add.reduceat(fcst[1:], np.arange(0, len(fcst[1:]), 6))

    if len(fcst[1:])%6 !=0:
        fcst_acc6hr = fcst_acc6hr[:-1]
        
    newfcst = [np.nan] * len(fcst)
    j=0
    for i in range(len(fcst)):
        
        if i%6 == 0 and i!=0:
    
            newfcst[i] = fcst_acc6hr[j]
            j=j+1
            
    return(newfcst)

#function that checks if all values of an array are the same (used for dates)
def areEqual(arr):
   
    first = arr[0];
     
    for i in range(1, len(arr)):
        if (arr[i] != first):
            return False;
           
    return True;

# gets the initializtion date and the array of hours, obs, and fcst for plotting
def get_data(filepath, station, variable, check_date, obs):
    
    file_list, hours = [], []
    
    # goes through the entire directory for each model+grid and and 
    # pulls out a list of the ones for the given station+variable wanted
    # Also pulls out the forecast hours that were collected from the filenames
    for all_files in os.listdir(filepath):
        if all_files.startswith(station + "." + variable + "."):
            file_list.append(all_files)
            hours.append(all_files[-7:-4])
            
    
    file_list.sort() # sorts the forecast hour in the file, since the station and variable are constant
    hours.sort() # list of hours that exist from filenames
    hours_int = [int(i) for i in hours] # convert hours from str to int

    # subtract one for plotting purposes because 001 is 00 UTC
    #hours_int = np.subtract(hours_int,1)

    dates = np.loadtxt(filepath + file_list[0],usecols=0,dtype=str)
    index = list(dates).index(start_date)

    fcst = []
    for i in range(len(file_list)):

        date = str(np.loadtxt(filepath + file_list[i],usecols=0)[index])

        if date == start_date + ".0":

            if variable == "SFCTC":
                fcst.append(float(np.loadtxt(filepath + file_list[i],usecols=1)[index])-273.15)
            elif variable == "APCP":
                fcst.append(float(np.loadtxt(filepath + file_list[i],usecols=1)[index]))

        else:
            fcst.append(np.nan)
            print("      WARNING: Wrong date for " + file_list[i] + ": should be " + start_date + " but is " + date)
            print("      removing data point from that hour for " + filepath )
    
    #removes bad data
    fcst = remove_missing_data(fcst)
    
    if station in precip6hrs_stations and variable == "APCP":
        fcst = accum_6hr(fcst)

    fcst = remove_missing_obs(fcst, obs)
    
    return(hours_int, fcst)

# gets the initializtion date and the array of hours, obs, and fcst for plotting
def get_winddata(filepath, station, variable, check_date, obs):
    
    file_list_u, hours_u = [], []
    file_list_v, hours_v = [], []
    
    # goes through the entire directory for each model+grid and and 
    # pulls out a list of the ones for the given station+variable wanted
    # Also pulls out the forecast hours that were collected from the filenames
    for all_files in os.listdir(filepath):
        if all_files.startswith(station + ".WIND_10U."):
            file_list_u.append(all_files)
            hours_u.append(all_files[-7:-4])
        if all_files.startswith(station + ".WIND_10V."):
            file_list_v.append(all_files)
            hours_v.append(all_files[-7:-4])
            
    
    file_list_u.sort(); file_list_v.sort() # sorts the forecast hour in the file, since the station and variable are constant
    hours_u.sort(); hours_v.sort() # list of hours that exist from filenames
    hours_int_u = [int(i) for i in hours_u]; hours_int_v = [int(i) for i in hours_v] # convert hours from str to int

    # subtract one for plotting purposes because 001 is 00 UTC
    #hours_int = np.subtract(hours_int,1)

    dates_u = np.loadtxt(filepath + file_list_u[0],usecols=0,dtype=str)
    index_u = list(dates_u).index(start_date)

    fcst_u = []
    for i in range(len(file_list_u)):

        date = str(np.loadtxt(filepath + file_list_u[i],usecols=0)[index_u])

        if date == start_date + ".0":

            fcst_u.append(float(np.loadtxt(filepath + file_list_u[i],usecols=1)[index_u]))

        
        else:
            fcst_u.append(np.nan)
            print("      WARNING: Wrong date for " + file_list_u[i] + ": should be " + start_date + " but is " + date)
            print("      removing data point from that hour for " + filepath )
    
    #removes bad data
    fcst_u = remove_missing_data(fcst_u)
    fcst_u = remove_missing_obs(fcst_u, obs)
# =============================================================================
#     if station in precip6hrs_stations and variable == "APCP":
#         fcst = accum_6hr(fcst)
# =============================================================================

    dates_v = np.loadtxt(filepath + file_list_v[0],usecols=0,dtype=str)
    index_v= list(dates_v).index(start_date)

    fcst_v= []
    for i in range(len(file_list_v)):

        date = str(np.loadtxt(filepath + file_list_v[i],usecols=0)[index_v])

        if date == start_date + ".0":

            fcst_v.append(float(np.loadtxt(filepath + file_list_v[i],usecols=1)[index_v]))

        
        else:
            fcst_v.append(np.nan)
            print("      WARNING: Wrong date for " + file_list_v[i] + ": should be " + start_date + " but is " + date)
            print("      removing data point from that hour for " + filepath )
    
    #removes bad data
    fcst_v = remove_missing_data(fcst_v)    
    fcst_v = remove_missing_obs(fcst_v, obs)

    fcst = np.sqrt((np.array(fcst_u) ** 2) + (np.array(fcst_v) ** 2)) * 3.6 #convert from m/s to km/hr
    
    return(hours_int_u, fcst)

# same function as get_data but only picks up the obs for each station
def get_obs(filepath,station,variable):    
     
    if variable == "APCP":
        variable = "PCPTOT"
             
    delta = timedelta(days=days-1)
    end_date = (input_date + delta).strftime("%y%m%d")
    
    # ignore the "KF" in the variable list, since its the same thing as the non-KF variable for obs
    if "_KF" in variable:
        variable = variable[:-3]

    if len(station) < 4:
        station = "0" + station

    if "PCPT" in variable:
        variable = "PCPTOT"

    sql_con = sqlite3.connect(obs_filepath + variable + '/' + station + ".sqlite")
    sql_query = "SELECT * from 'All' WHERE date BETWEEN 20" +str(start_date) + " AND 20" +str(end_date)
    obs = pd.read_sql_query(sql_query, sql_con)

    obs['datetime'] = None
    
    hours = []
    hr = 0
    for y in range(len(obs['Time'])):
        hour = int(obs['Time'][y])/100
        obs.loc[y,'datetime'] = pd.to_datetime(obs.loc[y,'Date'],format='%Y%m%d') + timedelta(hours=hour)
        hr = hr+1
        hours.append(hr)
    
    #obs = obs.set_index('datetime')     
    
    return(np.hstack(hours), np.hstack(obs['Val']))


# returns True if that file exists, False if not
def check_data_exists(filepath, station, variable):
    flag = False
    
    if variable == "SFCWSPD":
        variable = "WIND_10U"
        
    for all_files in os.listdir(filepath):    
        if station + "." + variable in all_files:
            flag=True
    return(flag)
       
        
# returns one plot every time it is run
def time_series(station, variable, ylabel, title):
      
        
    plt.figure(figsize=(18, 6), dpi=150)
    color_i = 0 #variable for plotting
    
    hours_int_obs, obs = get_obs(obs_filepath,station,variable)

    if variable == "APCP":
        obs = np.array(obs)
        obs = obs*0 + np.nan_to_num(obs).cumsum()
            
                
    
    for model in models: #loops through each model

        filepath = fcst_filepath + model + '/'           
                    
        if check_data_exists(filepath, station, variable) == False:
            print("Skipping " + model + " (No files for " + variable + " at station: " + station + ")")
            continue
        
        if variable == "SFCWSPD":
            hrs, fcst = get_winddata(filepath, station, variable, start_date, obs)
        else:
            hrs, fcst = get_data(filepath, station, variable, start_date, obs)

        if model == 'NAM/AWIP32' and variable == "APCP":
            #fcst = np.nancumsum(fcst)
            fcst = np.array(fcst)
            fcst = fcst*0 + np.nan_to_num(fcst).cumsum()

       
        if station in precip6hrs_stations and variable == "APCP":
            fcst = np.array(fcst)
            mask = np.isfinite(fcst)
            plt.plot(hrs[mask], fcst[mask], label=legend_labels[color_i],color=model_colors[color_i])
        elif station == "597" and variable == "SFCWSPD":
            fcst = np.array(fcst)
            mask = np.isfinite(fcst)
            plt.plot(hrs[mask], fcst[mask], label=legend_labels[color_i],color=model_colors[color_i])
        else:
            plt.plot(hrs, fcst, label=legend_labels[color_i],color=model_colors[color_i])

        color_i=color_i+1 #only increase every model (not grid size)
 
    # plot the obs
    
    if station == "597" and variable == "SFCWSPD":
        obs = np.array(obs)
        mask = np.isfinite(obs)
        plt.plot(hours_int_obs[mask],obs[mask],color='k',linewidth=3,label='station obs')
    elif station in precip6hrs_stations and variable == "APCP":
        obs = np.array(obs)
        mask = np.isfinite(obs)
        mask[0] = False
        plt.plot(hours_int_obs[mask],obs[mask],color='k',linewidth=3,label='station obs')
    else:
        plt.plot(hours_int_obs,obs,color='k',linewidth=3,label='station obs')


    # add a vertical line every 24 hours
    xposition = [i*24 for i in range(1,days)]
    for xc in xposition:
        plt.axvline(x=xc, color='k', linestyle='-')
            
    # x-axis limit is in hours       
    plt.xlim([0,days*2*12])
     
    plt.xlabel('Date in 2022 [UTC]',fontsize=18)
    plt.ylabel(ylabel,fontsize=18)
    plt.yticks(fontsize=18)
    
    # convert the initialization date to a python date
    date = datetime.strptime(start_date, "%y%m%d")
    delta = timedelta(hours=12) # time iteratization for the x axis
    
    labels = [(date + i*delta).strftime("%H:00\n%a %b %d") for i in range(0,days*2+1)]
    
    for i in range(len(labels)):
        if labels[i].startswith('00:00'):
            labels[i] = '00:00\n'
   
    plt.xticks([i*12 for i in range(0,days*2+1)], labels, fontsize=15)
            
    plt.title(title, fontsize=18)
    plt.legend()
    
    plt.gca().yaxis.grid(True)
    
    if not os.path.exists(save_folder + start_date):
        os.makedirs(save_folder + start_date)

    if variable == "APCP":
        variable = "PCPTOT"
        
    plt.savefig(save_folder + start_date + '/' + station + "_" + variable  + '.png',bbox_inches='tight')
   
    plt.close()
    

def main(args):
    t = time.time() #get how long it takes to run
    sys.stdout = open(logfilepath, "w")
    
    print("Now on day: " + start_date)
    stations_i = 0
    for station in stations:
        var_i = 0
        print("  Now on STATION: " + station)
        for var in variables:
            
            #these are pairs that dont have obs
            if (var == 'SFCWSPD' or var == 'SFCWSPD_KF') and station in ['424', '416', '417']:
                print("    Skipping SFCWSPD for this station (no obs data)")
                var_i = var_i + 1
                continue
            
           # if var == 'PCPTOT' and station in ['597', '604', '583', '600', '606', '601', '607', '610', '612', '603', '721']:
            if var == 'APCP' and station in ['721']:
                print("    Skipping PCPTOT for this station (no obs data)")
                var_i = var_i + 1
                continue
            
            time_series(station, var, yaxis_labels[var_i], station_names[stations_i])

            var_i = var_i + 1
            
        stations_i = stations_i+1

    ###### this part moves files from /www_oper/ to scratch if they're over a 30 days old
    #last_month = (datetime.today()-timedelta(days=30)).strftime('%y%m%d')
    #original = save_folder + last_month + '/'
    #target = '/scratch/egnegy/verification/website_images/old_ibcs_meteograms/'
    
    #if os.path.isdir(original) and os.path.isdir(target):

     
     #shutil.move(original,target)
        
      #  print("\n\n MOVED " + original + " to " + target)

  
    elapsed = time.time() - t
    print("It took " + str(round(elapsed/60)) + " minutes to run")
    sys.stdout.close() #close log file
if __name__ == "__main__":
    main(sys.argv)

