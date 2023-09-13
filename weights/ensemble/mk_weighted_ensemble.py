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
from datetime import datetime 
from datetime import timedelta
import sys
import math
import copy
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from scipy import stats
import sqlite3
from funcs import *
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

#output folder for sql tables after weighted ensemble is made
save_folder = '/home/verif/verif-post-process/weights/ensemble/output/'

###########################################################
### -------------------- INPUT ----------------------------
###########################################################

# takes an input date for the first and last day you want calculations for, must be a range of 7 or 30 days apart
if len(sys.argv) == 10:
    date_entry1 = sys.argv[1]    #input date YYMMDD
    start_date = str(date_entry1) 
    input_startdate = datetime.strptime(start_date, "%y%m%d").date()
    
    date_entry2 = sys.argv[2]    #input date YYMMDD
    end_date = str(date_entry2)
    input_enddate = datetime.strptime(end_date, "%y%m%d").date()
    
    #subtract 6 to match boreas time, might need to change in future
    today = datetime.now() - timedelta(hours=6) 
    needed_date = today - timedelta(days=8) #might need to change to 7
    if input_startdate > needed_date.date():
        raise Exception("Date too recent. Need start date to be at least 8 days ago.")

    delta = (input_enddate-input_startdate).days

    if delta == 365: # 6 is weekly bc it includes the start and end date (making 7)
        print("Performing Yearly calculation for " + start_date + " to " + end_date)
        savetype = 'weekly'

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
    
    stat_type = sys.argv[6]
    if stat_type not in ['CAT_', 'MAE_', 'RMSE_','spcorr_']:# statistic type used to get model: CAT_ includes 6 categorical scores within it, all these need tailing '_'
        raise Exception("Invalid stat type input entries. Options: CAT_, MAE_, RMSE_, spcorr_. Case sensitive and tailing '_' required")

    k = sys.argv[7]
    if k not in ['40','80','100','150','200','500','1000']:
        raise Exception("Invalid k value. Options: 40, 80, 100, 150, 200, 500, 1000.")
    
    time_domain = sys.argv[8]
    if time_domain not in ['60hr','84hr', '120hr', '180hr', 'day1', 'day2', 'day3', 'day4', 'day5', 'day6', 'day7']:
        raise Exception("Invalid time domain. Options: '60hr','84hr', '120hr', '180hr', 'day1', 'day2', 'day3', 'day4', 'day5', 'day6', 'day7'")
    
    stat_cat = sys.argv[9]
    if stat_cat not in ['POD', 'POFD', 'PSS', 'HSS', 'CSI', 'GSS']:
        raise Exception("Invalid CAT score type. Options: 'POD', 'POFD', 'PSS', 'HSS', 'CSI', 'GSS'; do not need tailing '_'")


    if stat_type == 'CAT_' and 'SFCTC' in input_variable:
        raise Exception("Invalid input options. CAT_ can only be used with precip and wind variables NOT temp.")

else:
    raise Exception("Invalid input entries. Needs 2 YYMMDD entries for start and end dates, a variable name, domain size, weight type, stat type and k.")

# list of model names as strings (names as they are saved in www_oper and my output folders)
#models = np.loadtxt(models_file,usecols=0,dtype='str')
#grids = np.loadtxt(models_file,usecols=1,dtype='str') #list of grid sizings (g1, g2, g3 etc) for each model
#gridres = np.loadtxt(models_file,usecols=2,dtype='str') #list of grid resolution in km for each model
#hours = np.loadtxt(models_file,usecols=3,dtype='str') #list of max hours for each model

station_df = pd.read_csv(station_file)

#stations_with_SFCTC = np.array(station_df.query("SFCTC==1")["Station ID"],dtype=str)
#stations_with_SFCWSPD = np.array(station_df.query("SFCWSPD==1")["Station ID"],dtype=str)
#stations_with_PCPTOT = np.array(station_df.query("PCPTOT==1")["Station ID"],dtype=str)
#stations_with_PCPT6 = np.array(station_df.query("PCPT6==1")["Station ID"],dtype=str)

#all_stations = np.array(station_df.query("`Small domain`==1")["Station ID"],dtype=str)


##########################################################
###-------------------- FOR TESTING ---------------------
##########################################################
stations_with_SFCTC = ['3510']
stations_with_SFCWSPD = ['3510']
stations_with_PCPTOT = ['3510']
stations_with_PCPT6 = ['3510']

all_stations = ['3510']

models = ['MM5']
grids = grids = np.loadtxt(models_file,usecols=1,dtype='str',max_rows = 2) 
gridres = gridres = np.loadtxt(models_file,usecols=2,dtype='str',max_rows = 2)
hours = hours = np.loadtxt(models_file,usecols=3,dtype='str', max_rows = 2)

###########################################################
### -------------------- MAIN FUNCTION --------------------
###########################################################

def main(args):
    #sys.stdout = open(logfilepath, "w") #opens log file

    date_list = listofdates(start_date, end_date, obs=False)
    date_list_obs = listofdates(start_date, end_date, obs=True)
    if input_variable == "PCPT6":       
        obs_df = PCPT_obs_df_6(date_list_obs, delta, input_variable, stations_with_SFCTC, stations_with_SFCWSPD, \
                stations_with_PCPTOT, stations_with_PCPT6, all_stations, start_date, end_date)
        
    else:
        obs_df = get_all_obs(delta, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, \
            stations_with_PCPT6,  all_stations, input_variable, start_date, end_date, date_list_obs)
   
    fcst_all = make_df(date_list_obs, start_date, end_date)
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

            fcst, model_df_name = fcst_grab(savetype, stat_type, k, weight_type, filepath, delta, input_domain, date_entry1, date_entry2, \
                all_stations, station_df, input_variable, date_list, model, grid, maxhour, gridname, filehours, \
                obs_df, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6)
             
            fcst_all = fcst_all.merge(fcst, on='datetime',how = 'left')
    
    ENS_W = mk_ensemble(stat_cat, weight_type, stat_type, model_df_name, start_date, end_date, fcst_all, input_variable)
    print(ENS_W)
    
    if stat_type == 'CAT_':
        
        path = save_folder + weight_type + '/' + stat_cat + '/' + input_variable + '/'
        if os.path.isdir(path) == false
            os.makedirs(path)
        
        conn = sqlite3.connect(path + station + '.sqlite')
        df.to_sql('All', conn, index=True)

    else:
        path = save_folder + weight_type + '/' + stat_type + '/' + input_variable + '/'
        if os.path.isdir(path) == false
            os.makedirs(path)
        conn = sqlite3.connect(path + station + '.sqlite')
        df.to_sql('All', conn, index=True)

if __name__ == "__main__":
    main(sys.argv)
