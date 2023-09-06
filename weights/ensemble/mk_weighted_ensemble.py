#!/usr/bin python

"""
Created in 2023 by Reagan McKinney

Input: start date (YYMMDD), end date (YYMMDD), variable, domain size
    Start and end date must be a year stretch (365 days)
    variable options: SFCTC_KF, SFCTC, PCPTOT, PCPT6, SFCWSPD_KF, SFCWSPD
    domain options: small *weights have only been calculated for the small domain
    weight type: seasonal or yearly
    
This code is used to weight all 51 forecasting members with the weights developed in the LF scheme. 
To learn more about the LF scheme, go to the parent directory of this folder and navigate to /LF. 

"""
import os
import pandas as pd
import numpy as np
import datetime 
from datetime import timedelta
import sys
import math
import copy
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from scipy import stats
import sqlite3
from utl.funcs import *
import warnings
warnings.filterwarnings("ignore",category=RuntimeWarning)


###########################################################
### -------------------- FILEPATHS ------------------------
###########################################################

#location where obs files are (all sql databases should be in this directory)
obs_filepath = "/verification/Observations/"

#location where forecast files are (immediately within this directory should be model folders, then grid folders, then the sql databases)
fcst_filepath = "/verification/Forecasts/"

#description file for stations
station_file = '/home/verif/verif-post-process/input/station_list_master.txt'

#description file for models
models_file = '/home/verif/verif-post-process/input/model_list.txt'

#folder where stats save
textfile_folder = '/verification/weighted-Statistics/'

#folder where the weights are located
weights_folder = '/home/verif/verif-post-process/weights/LF/output/'

###########################################################
### -------------------- INPUT ----------------------------
###########################################################

# takes an input date for the first and last day you want calculations for, must be a range of 7 or 30 days apart
if len(sys.argv) == 6:
    date_entry1 = sys.argv[1]    #input date YYMMDD
    start_date = str(date_entry1) 
    input_startdate = datetime.datetime.strptime(start_date, "%y%m%d").date()
    
    date_entry2 = sys.argv[2]    #input date YYMMDD
    end_date = str(date_entry2)
    input_enddate = datetime.datetime.strptime(end_date, "%y%m%d").date()
    
    #subtract 6 to match boreas time, might need to change in future
    today = datetime.datetime.now() - datetime.timedelta(hours=6) 
    needed_date = today - datetime.timedelta(days=8) #might need to change to 7
    if input_startdate > needed_date.date():
        raise Exception("Date too recent. Need start date to be at least 8 days ago.")

    delta = (input_enddate-input_startdate).days

    if delta == 365: # 6 is weekly bc it includes the start and end date (making 7)
        print("Performing Yearly calculation for " + start_date + " to " + end_date)

    else:
        raise Exception("Invalid date input entries. Start and end date must be 7 or 28-31 days apart (for weekly and monthly stats) Entered range was: " + str(delta+1) + " days")


    input_variable = sys.argv[3]
    if input_variable not in ['SFCTC_KF', 'SFCTC', 'PCPTOT', 'PCPT6', 'SFCWSPD_KF', 'SFCWSPD']:
        raise Exception("Invalid variable input entries. Current options: SFCTC_KF, SFCTC, PCPTOT, PCPT6, SFCWSPD_KF, SFCWSPD. Case sensitive.")

    input_domain = sys.argv[4]
    if input_domain not in ['small']:
        raise Exception("Invalid domain input entries. Current options: small. Case sensitive.")

    weight_type = sys.argv[5]
    if weight_type not in ['yearly', 'seasonal']:
        raise Exception("Invalid weight tyoe input entries. Options: yearly, seasonal. Case sensitive")
            
else:
    raise Exception("Invalid input entries. Needs 2 YYMMDD entries for start and end dates, a variable name, domain size and weight type")

# list of model names as strings (names as they are saved in www_oper and my output folders)
models = np.loadtxt(models_file,usecols=0,dtype='str')
grids = np.loadtxt(models_file,usecols=1,dtype='str') #list of grid sizings (g1, g2, g3 etc) for each model
gridres = np.loadtxt(models_file,usecols=2,dtype='str') #list of grid resolution in km for each model
hours = np.loadtxt(models_file,usecols=3,dtype='str') #list of max hours for each model

station_df = pd.read_csv(station_file)

stations_with_SFCTC = np.array(station_df.query("SFCTC==1")["Station ID"],dtype=str)
stations_with_SFCWSPD = np.array(station_df.query("SFCWSPD==1")["Station ID"],dtype=str)
stations_with_PCPTOT = np.array(station_df.query("PCPTOT==1")["Station ID"],dtype=str)
stations_with_PCPT6 = np.array(station_df.query("PCPT6==1")["Station ID"],dtype=str)

all_stations = np.array(station_df.query("`Small domain`==1")["Station ID"],dtype=str)
    
###########################################################
### -------------------- MAIN FUNCTION --------------------
###########################################################

def main(args):
    #sys.stdout = open(logfilepath, "w") #opens log file

    date_list = listofdates(start_date, end_date, obs=False)
    date_list_obs = listofdates(start_date, end_date, obs=True)
    if input_variable == "PCPT6":       
        obs_df_60hr,obs_df_84hr,obs_df_120hr,obs_df_180hr,obs_df_day1,obs_df_day2,obs_df_day3,obs_df_day4,obs_df_day5,obs_df_day6,obs_df_day7 = \
            PCPT_obs_df_6(date_list_obs, delta, input_variable, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6,\
                all_stations, start_date, end_date)
        
    else:
        obs_df_60hr,obs_df_84hr,obs_df_120hr,obs_df_180hr,obs_df_day1,obs_df_day2,obs_df_day3,obs_df_day4,obs_df_day5,obs_df_day6,obs_df_day7 = get_all_obs(delta, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6,  all_stations, input_variable, start_date, end_date, date_list_obs)
   
    for i in range(len(models)):
       model = models[i] #loops through each model
       
       for grid_i in range(len(grids[i].split(","))): #loops through each grid size for each model
           
           grid = grids[i].split(",")[grid_i]
           maxhour = hours[i].split(",")[grid_i] # the max hours that are in the current model/grid
           
           if "_KF" in input_variable:
              file_var = input_variable[:-3]
           else:
               file_var = input_variable

           filehours = get_filehours(1, int(maxhour))
           #ENS only has one grid (and its not saved in a g folder)
           if model == 'ENS' and '_KF' in input_variable:    
               filepath = fcst_filepath + model + '/' + file_var + '/fcst.KF_MH.t/'
               gridname = ''
           elif model == 'ENS':
               filepath = fcst_filepath + model + '/' + file_var + '/fcst.t/'
               gridname = ''
           elif model == "ENS_LR" and "_KF" in input_variable:
               filepath = fcst_filepath +model[:-3] + '/' + file_var + '/fcst.LR.KF_MH.t/'
               gridname = ''
           elif model == "ENS_lr" and "_KF" in input_variable:
               filepath = fcst_filepath+model[:-3] + '/' + file_var + '/fcst.lr.KF_MH.t/'
               gridname = ''
           elif model == "ENS_hr" and "_KF" in input_variable:
               filepath = fcst_filepath +model[:-3] + '/' + file_var + '/fcst.hr.KF_MH.t/'
               gridname = ''
           elif model =="ENS_hr":
               filepath = fcst_filepath +model[:-3] + '/' + file_var + "/fcst.hr.t/"
               gridname = ''
           elif model =="ENS_lr":
               filepath = fcst_filepath +model[:-3] + '/' + file_var + "/fcst.lr.t/"
               gridname = ''
           elif model =="ENS_LR":
               filepath = fcst_filepath +model[:-3] + '/' + file_var + "/fcst.LR.t/"
               gridname = ''
           elif "_KF" in input_variable:
               filepath = fcst_filepath +model + '/' + grid + '/' + file_var + "/fcst.KF_MH/"          
               gridname = "_" + grid
           else:
               filepath = fcst_filepath + model + '/' + grid + '/' + file_var + '/fcst.t/'
               gridname = "_" + grid
           
           if check_dates(start_date, delta, filepath, input_variable, station='3510') == False:
               print("   Skipping model " + model + gridname + " (check_dates flag)")
               continue
       
           # if it can't find the folder for the model/grid pair 
           if not os.path.isdir(filepath):
               raise Exception("Missing grid/model pair (or wrong base filepath for" + model + gridname)
           
           print("Now on.. " + model + gridname + " for " + input_variable)

           
           get_rankings(weight_type, filepath, delta, input_domain, date_entry1, date_entry2, all_stations, station_df, input_variable, date_list, model, grid, maxhour, gridname, filehours, obs_df_60hr,obs_df_84hr,obs_df_120hr,obs_df_180hr,obs_df_day1,obs_df_day2,obs_df_day3,obs_df_day4,obs_df_day5,obs_df_day6,obs_df_day7, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6)

if __name__ == "__main__":
    main(sys.argv)