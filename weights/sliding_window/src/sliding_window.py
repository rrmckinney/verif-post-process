#!/usr/bin python

"""
Created in 2024 by Reagan McKinney

Input: sliding window (week, month), variable, domain size.
    variable options: SFCTC_KF, SFCTC, PCPTOT, PCPT6, SFCWSPD_KF, SFCWSPD
    domain options: small *weights have only been calculated for the small domain
    
This code is used to weight all 51 forecasting members using a sliding window technique. Weights are based on the rank of each member given the previous week or month and selected in the input. Weights are based on the LF ranked-based weighting system.

"""

import os
import pandas as pd
import numpy as np
from datetime import datetime 
from datetime import timedelta
import sys
import copy
import matplotlib.pyplot as plt
import time
from utl.funcs import *
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from scipy import stats
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
models_file = '/home/verif/verif-post-process/input/model_list_weights.txt'

#output folder for txt files after weighted ensemble is made
save_folder = '/home/verif/verif-post-process/weights/sliding_window/output/'


###########################################################
### -------------------- INPUT ----------------------------
###########################################################

# takes an input date for the first and last day you want calculations for, must be a range of 7 or 30 days apart
if len(sys.argv) == 8:
    
    date_entry1 = sys.argv[1]    #input date YYMMDD
    start_date = str(date_entry1) 
    input_startdate = datetime.strptime(start_date, "%y%m%d%H")
    
    date_entry2 = sys.argv[2]    #input date YYMMDD
    end_date = str(date_entry2)
    input_enddate = datetime.strptime(end_date, "%y%m%d%H")
    
    delta = (input_enddate-input_startdate).total_seconds()/(60*60)
    if delta == 60: # 6 is weekly bc it includes the start and end date (making 7)
        print("Performing Yearly calculation for " + start_date + " to " + end_date)
        savetype = 'weekly'

    else:
       raise Exception("Invalid date input entries. Start and end date must be 60 hours apart. Entered range was: " + str(delta+1) + " hours")

    
    window_type = sys.argv[3]
    if window_type not in ['weekly','monthly']:
        raise Exception("Invalid variable input entries. Current options: weekly, monthly.")
    
    input_variable = sys.argv[4]
    if input_variable not in ['SFCTC_KF', 'SFCTC', 'PCPTOT', 'PCPT6', 'SFCWSPD_KF', 'SFCWSPD']:
        raise Exception("Invalid variable input entries. Current options: SFCTC_KF, SFCTC, PCPTOT, PCPT6, SFCWSPD_KF, SFCWSPD. Case sensitive.")

    time_domain = sys.argv[5]
    if time_domain not in ['60hr','84hr', '120hr', '180hr', 'day1', 'day2', 'day3', 'day4', 'day5', 'day6', 'day7']:
        raise Exception("Invalid time domain. Options: '60hr','84hr', '120hr', '180hr', 'day1', 'day2', 'day3', 'day4', 'day5', 'day6', 'day7'")

    weight_type = sys.argv[6]
    if weight_type not in ['MAE', 'RMSE', 'corr']:
        raise Exception("Invalid weight type. Options: MAE, RMSE, and corr (spearman rank correlation)")
    input_station = sys.argv[7]
else:
    raise Exception("Invalid input entries. Needs 2 YYMMDD entries for start and end dates, window type, variable name, time domain, and weight type.")

input_domain = 'small'

# list of model names as strings (names as they are saved in www_oper and my output folders)

models = np.loadtxt(models_file,usecols=0,dtype='str')
grids = np.loadtxt(models_file,usecols=1,dtype='str') #list of grid sizings (g1, g2, g3 etc) for each model
gridres = np.loadtxt(models_file,usecols=2,dtype='str') #list of grid resolution in km for each model
hours = np.loadtxt(models_file,usecols=3,dtype='str') #list of max hours for each model


station_df = pd.read_csv(station_file)
'''
stations_with_SFCTC = np.array(station_df.query("SFCTC==1")["Station ID"],dtype=str)
stations_with_SFCWSPD = np.array(station_df.query("SFCWSPD==1")["Station ID"],dtype=str)
stations_with_PCPTOT = np.array(station_df.query("PCPTOT==1")["Station ID"],dtype=str)
stations_with_PCPT6 = np.array(station_df.query("PCPT6==1")["Station ID"],dtype=str)

all_stations = np.array(station_df.query("`Small domain`==1")["Station ID"],dtype=str)
'''

##########################################################
###-------------------- FOR TESTING ---------------------
##########################################################
#input_station = sys.argv[7]
stations_with_SFCTC = [input_station]
stations_with_SFCWSPD = [input_station]
stations_with_PCPTOT = [input_station]
stations_with_PCPT6 = [input_station]

all_stations = [input_station]
station_df = pd.read_csv(station_file)
'''
models = ['MM5']
grids = grids = np.loadtxt(models_file,usecols=1,dtype='str',max_rows = 2) 
gridres = gridres = np.loadtxt(models_file,usecols=2,dtype='str',max_rows = 2)
hours = hours = np.loadtxt(models_file,usecols=3,dtype='str', max_rows = 2)
'''
###########################################################

# this loop makes the names for each model/grid pair that will go in the legend
legend_labels = []
for i in range(len(models)):
    for grid in gridres[i].split(","):
        model = models[i]

        if "_" in model: #only for ENS models, which don't have grid res options
            legend_labels.append(model.replace("_"," "))
        else:
            legend_labels.append(model + grid)
###########################################################
### -------------------- MAIN FUNCTION --------------------
###########################################################

def main(args):

    t = time.time() #get how long it takes to run

    #sys.stdout = open(logfilepath, "w") #opens log file

    date_list = listofdates(start_date, end_date, obs=False)
    date_list_obs = listofdates(start_date, end_date, obs=True)

    if input_variable == 'SFCTC_KF' or input_variable == 'SFCTC':
        station_list = copy.deepcopy(stations_with_SFCTC)
    elif input_variable == 'SFCWSPD_KF' or input_variable == 'SFCWSPD':
        station_list = copy.deepcopy(stations_with_SFCWSPD)

    elif input_variable == "PCPTOT":
        if input_variable == "PCPT6":
            station_list = [st for st in stations_with_PCPTOT if st not in stations_with_PCPT6 ]
        else:
            station_list = copy.deepcopy(stations_with_PCPTOT)

    elif input_variable == "PCPT6":
        station_list = copy.deepcopy(stations_with_PCPT6)

    for s in range(len(station_list)):

        station = station_list[s]
        print( "    Now on station " + station)

        if check_variable(input_variable, station, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6) == False:
            print("   Skipping station " + station + " (no " + input_variable + " data)")
            continue

        #if len(station) < 4:
        #    station = "0" + str(station)
        
        #get obserational data in dataframe
        if input_variable == "PCPT6":
            obs_df = PCPT_obs_df_6(date_list_obs, delta, input_variable, station, start_date, end_date, all_stations)

        else:
            obs_df = get_all_obs(delta, station,  input_variable, start_date, end_date, date_list_obs, all_stations)

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

                if check_dates(start_date, delta, filepath, input_variable, station) == False:
                    print("   Skipping model " + model + gridname + " (check_dates flag)")
                    continue

                # if it can't find the folder for the model/grid pair
                if not os.path.isdir(filepath):
                    raise Exception("Missing grid/model pair (or wrong base filepath for" + model + gridname)

                print("Now on.. " + model + gridname + " for " + input_variable)
                
                #read in forecast data to use in making ensemble
                fcst, model_df_name = fcst_grab(station_df, savetype,  weight_type, filepath, delta, input_domain,  \
                    date_entry1, date_entry2, input_variable, date_list, model, grid, maxhour, gridname, filehours, \
                    obs_df, station)


                fcst_all = fcst_all.merge(fcst, on='datetime',how='left')
 
        #rank each forecast based on previous performance
        MAE_list, RMSE_list, correlation_list, modelnames, modelcolors, edit_modelnames, skipped_modelnames, numofstations = rank_models(delta, input_startdate, input_variable, time_domain, input_domain, models, grids, window_type, legend_labels)
        
        #create weights based on rank of each model performance
        weights = make_weights(MAE_list, RMSE_list, correlation_list, weight_type, modelnames)
        
        #apply weights to ensemble
        df = mk_ensemble(weights, start_date, end_date, input_variable, fcst_all)
        
        #combine weighted ensemble and obs
        df = df.to_frame()
        df1 = df.join(obs_df)

        #create regular ensemble and add it to dataframes with weighted and obs
        ENS_M = fcst_all.mean(axis=1)
        ENS_M = ENS_M.to_frame()
        ENS_M.columns = ['ENS_M']
        
        df1 = df1.join(ENS_M, how='right')
        #df1.columns = ['ENS_W', 'Obs', 'ENS_M']
        df1 =df1.dropna()
        
        df1.to_csv(save_folder+window_type+'/ENSW_'+input_variable+'.txt',mode='a',header=False)
        #ttest(df1, date_entry1, date_entry2, weight_type, window_type,input_variable)
        
        #write_stats(station,df1, date_entry1, date_entry2, input_variable, weight_type, window_type)

        elapsed = time.time() - t #closes log file
        print("It took " + str(round(elapsed/60)) + " minutes to run")

if __name__ == "__main__":
     main(sys.argv)
