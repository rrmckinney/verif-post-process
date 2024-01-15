#!/usr/bin python

"""
Created in 2024 by Reagan McKinney

These are the functions that feed into the sliding_window.py file. This script holds all the functions
that create the weigted ensemble and then estblish stats to compare it to our current ensemble performance. 

"""

import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
import math
import sqlite3
import warnings
import matplotlib.pyplot as plt
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

#folder where the stats save
textfile_folder = '/verification/Statistics/'

save_folder='/home/verif/verif-post-process/weights/sliding_window/output/'

###########################################################
### -------------------- INPUTS -- ------------------------
###########################################################

# thresholds for discluding erroneous data 
precip_threshold = 250 #recorded at Buffalo Gap 1961 https://www.canada.ca/en/environment-climate-change/services/water-overview/quantity/floods/events-prairie-provinces.html
wind_threshold = 400 #recorded Edmonton, AB 1987 http://wayback.archive-it.org/7084/20170925152846/https://www.ec.gc.ca/meteo-weather/default.asp?lang=En&n=6A4A3AC5-1#tab5
temp_min = -63 #recorded in Snag, YT 1947 http://wayback.archive-it.org/7084/20170925152846/https://www.ec.gc.ca/meteo-weather/default.asp?lang=En&n=6A4A3AC5-1#tab5
temp_max = 49.6 #recorded in Lytton, BC 2021 https://www.canada.ca/en/environment-climate-change/services/top-ten-weather-stories/2021.html#toc2

# weight outlook: the forecast outlook the weights are based upon, 60hr is the only outlook that has all 51 members
weight_outlook = '60hr'

#editting mode for textfile
wm = 'w'

###########################################################
### -------------------- FUNCTIONS ------------------------
###########################################################


# makes a list of the dates you want from start to end, used to make sure the models and obs have the right dates
# obs get their own list because it will be different days than the initializition dates from the models for anything
#   past hours 0-24
def listofdates(start_date, end_date, obs = False):
    if obs == False:
        start = datetime.strptime(start_date, "%y%m%d%H")
        end = datetime.strptime(end_date, "%y%m%d%H")

    elif obs == True:
        startday = 0 #forhour 1
        endday = 7 #for hour 180

        start = datetime.strptime(start_date, "%y%m%d%H")#.date() + timedelta(days=startday)
        end = datetime.strptime(end_date, "%y%m%d%H")#.date() + timedelta(days=startday

    numdays = int((end-start).total_seconds()/(60*60))
    date_list = [(start + timedelta(hours=x)).strftime("%y%m%d%H") for x in range(numdays+1)]

    return(date_list)

#lists the hour filenames that we are running for
def get_filehours(hour1,hour2):

    hours_list = []
    for i in range(hour1,hour2+1):
        i = i-1
        if i < 10:
            hour = "0" + str(i)
        else:
            hour = str(i)
        hours_list.append(hour)

    return(hours_list)


def check_variable(variable, station, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6):

    flag = False

    if variable == 'SFCTC_KF' or variable == 'SFCTC':

        if str(station) in stations_with_SFCTC:
            flag=True

    elif variable == 'SFCWSPD_KF' or variable == 'SFCWSPD':

        if str(station) in stations_with_SFCWSPD:
            flag=True

    elif variable == "PCPTOT":

        if str(station) in stations_with_PCPTOT:
            flag=True

    elif variable == "PCPT6":

        if str(station) in stations_with_PCPTOT or str(station) in stations_with_PCPT6:
            flag=True


    return(flag)

# checks to see if the right amount of dates exist, which is used for when new models/stations are added
# default station exists for when a new model is added (instead of new station)
def check_dates(start_date, delta, filepath, variable, station):
    flag = True

    if len(station) < 4:
        station = "0" +station
    if "PCPT" in variable:
        variable = "PCPTOT"

    sql_path = filepath + station + ".sqlite"
    sql_con = sqlite3.connect(sql_path)

    cursor = sql_con.cursor()
    cursor.execute("SELECT DISTINCT Date from 'All'")
    sql_result = cursor.fetchall()
    sql_result = [x[0] for x in sql_result]

    if len(sql_result) < delta+1:
        print( "  Not enough dates available for this model/station/variable")
        flag = False

    cursor.close()

    return(flag)

# makes a dataframe with all hours and dates to compare to actual data; allows us to add in nans where needed
def make_df(date_list_obs, start_date, end_date):
    date_list_obs = listofdates(start_date, end_date, obs=True)
    df_new = pd.DataFrame()
    '''
    for day in date_list_obs:
        filehours_obs = get_filehours(1, 24)

        df = pd.DataFrame({'date': day, 'time': filehours_obs})
        df['datetime'] = pd.to_datetime(df['date'], format = '%y%m%d%H')

        df_new = pd.concat([df_new, df])
    df_new = df_new.set_index('datetime')
    df_new.drop(['date','time'], axis='columns',inplace=True)
    '''
    date_list_obs = pd.to_datetime(date_list_obs, format='%y%m%d%H')
    df_new['datetime'] = date_list_obs
    df_new = df_new.set_index('datetime')
    return(df_new)

def get_all_obs(delta, station, variable, start_date, end_date, date_list_obs, all_stations):

    print("Reading observational dataframe for " + variable + ".. ")

    df_new = make_df(date_list_obs, start_date, end_date)

    #KF variables are the same as raw for obs
    if "_KF" in variable:
        variable = variable[:-3]

    obs_df = pd.DataFrame()


    if station not in all_stations:
        #print("   Skipping station " + station)
        return()

    if len(station) < 4:
        station = "0" +station

    if "PCPT" in variable:
        if check_dates(start_date, delta, fcst_filepath + 'ENS/' + variable + '/fcst.t/', "PCPTOT", station) == False:
            print("   Skipping station " + station + " (not enough dates yet)")
            return()
    else:
        if check_dates(start_date, delta, fcst_filepath + 'ENS/' + variable + '/fcst.t/', variable, station) == False:
            print("   Skipping station " + station + " (not enough dates yet)")
            return()

    sql_con = sqlite3.connect(obs_filepath + variable + "/" + station + ".sqlite")
    sql_query = "SELECT * from 'All' WHERE date BETWEEN 20" +str(date_list_obs[0])[:-2] + " AND 20" + str(date_list_obs[len(date_list_obs)-1])[:-2]
    obs = pd.read_sql_query(sql_query, sql_con)
    obs['datetime'] = None

    for y in range(len(obs['Time'])):
        hour = int(obs['Time'][y])/100
        obs.loc[y,'datetime'] = pd.to_datetime(obs.loc[y,'Date'], format='%Y%m%d') + timedelta(hours=hour)

    obs = obs.set_index('datetime')
    obs = obs[0:61]
    obs_all = df_new.join(obs, on='datetime')
    obs_all.drop(['Date','Time'], axis='columns',inplace=True)
    # remove data that falls outside the physical bounds (higher than the verified records for Canada
    for i in range(len(obs_all)):

        if variable == 'SFCTC_KF' or variable == 'SFCTC':
            if obs_all.Val[i] > temp_max:
                obs_all.Val[i] = np.nan
            if obs_all.Val[i] < temp_min:
                obs_all.Val[i] = np.nan

        if variable == 'SFCWSPD_KF' or variable == 'SFCWSPD':
            if obs_all.Val[i] > wind_threshold:
                obs_all.Val[i] = np.nan

        if variable == 'PCPTOT':
            if obs_all.Val[i] > precip_threshold:
                obs_all.Val[i] = np.nan

    # final_obs = np.array(obs_all).T #84 x 7   (30)

    # obs_df[station] = final_obs.flatten()
    return(obs_all)

def PCPT_obs_df_6(date_list_obs, delta, variable, station, start_date, end_date,all_stations):

    # get the hourly precip values
    obs_df_1 = get_all_obs(delta, station,  'PCPTOT', start_date, end_date, date_list_obs, all_stations)
    
    # grab the extra hour on the last outlook day
    obs_df_1 = obs_df_1.append(obs_df_1.iloc[60],ignore_index=True)
 
    
    # remove the first hour (0 UTC)
    obs_df_1 = obs_df_1.iloc[1:].reset_index(drop=True)

    # sum every 6 hours (1-6 UTC, 7-12 UTC etc). report NaN if any of the 6 hours is missing
    obs_df_1_trimmed = obs_df_1.groupby(obs_df_1.index // 6).apply(pd.DataFrame.sum,skipna=False)

    #grab the 6-hr accum precip values
    obs_df_6 = get_all_obs(delta, station,  'PCPT6', start_date, end_date, date_list_obs, all_stations)
        
    # grab the extra hour on the last outlook day
    obs_df_6 = obs_df_6.append(obs_df_6.iloc[60],ignore_index=True)

    # remove all values except the ones every 6 hours (6 UTC, 12 UTC, etc. (skipping the first))
    obs_df_6_trimmed = obs_df_6.iloc[::6, :][1:].reset_index(drop=True) #grabs every 6 hours (skipping hour 0)

    #combine the obs from manually accumulating 6 hours from hourly, and the pre-calculated 6 hours
    obs_df = pd.concat([obs_df_1_trimmed, obs_df_6_trimmed],axis=1)


    return(obs_df)

# returns the fcst data for the given model/grid
def get_fcst( maxhour, station, filepath, variable, date_list, filehours, start_date, end_date, weight_type, model_df_name):
    df_new = make_df(date_list, start_date, end_date)
    if "PCPT" in variable:
        variable = "PCPTOT"
    # pulls out a list of the files for the given station+variable+hour wanted
    sql_con = sqlite3.connect(filepath + station + ".sqlite")
    sql_query = "SELECT * from'All' WHERE date BETWEEN 20" + str(date_list[0])[:-2] + " AND 20" + str(date_list[len(date_list)-1])[:-2]
    fcst = pd.read_sql_query(sql_query, sql_con)

    fcst['datetime'] = None
    fcst = fcst[0:61]

    for x in range(len(fcst['Offset'])):
        y = fcst.loc[x,'Offset']
        fcst.loc[x, 'datetime'] = pd.to_datetime(fcst.loc[x,'Date'], format='%Y%m%d') + timedelta(hours=int(y))

    fcst = fcst.set_index('datetime')
    df_all = df_new.join(fcst, on='datetime')
    df_all.drop(['Date','Offset'], axis='columns',inplace = True)
    df_all.columns = [model_df_name]
    return(df_all)


# this removes (NaNs) any fcst data where the obs is not recorded, or fcst is -999
def remove_missing_data(fcst, obs):
    for i in range(len(fcst)):
        if math.isnan(obs[i]) == True:
            fcst[i] = np.nan

        if fcst[i] == -999:
            fcst[i] = np.nan
            obs[i] = np.nan

    return(fcst,obs)

def fcst_grab(station_df, savetype, weight_type, filepath, delta, input_domain,  \
                    date_entry1, date_entry2, variable, date_list, model, grid, maxhour, gridname, filehours, \
                    obs_df, station):
            
    # open the file for the current model and get all the stations from it
    model_df_name = model+gridname
    #
    # depreciated, meant for large domain when not all stations are in the model domains, when using small domain though
    # don't need to worry about this
    stations_in_domain = np.array(station_df.query(model_df_name+"==1")["Station ID"],dtype='str')

    totalstations = 0
    num_stations = 0
    
    if station not in stations_in_domain:
        print("   Skipping station " + station)
        return()

    if check_dates(date_entry1, delta, filepath, variable, station) == False:
        print("   Skipping station " + station + " (not enough dates yet)")
        return()

    # total stations that should be included in each model/grid
    totalstations = totalstations+1
        
    all_fcst = get_fcst(maxhour, station, filepath, variable, date_list,filehours, date_entry1, \
                        date_entry2, weight_type, model_df_name)    #goes to maxhour       

    
    num_stations = num_stations+1

    #sometimes theres no forecast data for a model
    if num_stations == 0:
        print("   NO FORECAST DATA FOR " + model + grid) 

    else:
        return(all_fcst, model_df_name)

def rank_models(input_startdate, variable, time_domain, input_domain, models, grids, window_type):
    MAE_list,RMSE_list,correlation_list,modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations = [],[],[],[],[],[],[],[]
    
    if window_type = 'weekly':
        startdate = input_startdate - timedelta(days=7)
        enddate = startdate + timedelta(days=6)
    
    if window_type = 'monthly':
        date = input_startdate - timedelta(months=1)
        startdate = date.replace(day=1)
        end_date = startdate + timedelta(months=1) - timedelta(days=1)
    
    leg_count = 0
    color_count = 0

    for i in range(len(models)):
        model = models[i] #loops through each model

        for grid in grids[i].split(","): #loops through each grid size for each model


            #ENS only has one grid (and its not saved in a g folder)
            if "ENS" in model:
                modelpath = model + '/'
                gridname = ""
            else:
                modelpath = model + '/' + grid + '/'
                gridname = "_" + grid


            print("Now on.. " + model + gridname + "   " + variable)

            if os.path.isfile(textfile_folder +  modelpath  + input_domain + '/' + variable + '/' + "MAE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt"):
                #open the MAE file
                with open(textfile_folder +  modelpath  + input_domain + '/' + variable + '/' + "MAE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt") as f:
                    MAE_lines = f.readlines()

                data_check = False
                #find the line for the given dates
                for MAE_line in MAE_lines:
                    if date_entry1 in MAE_line and date_entry2 in MAE_line:
                        MAE = MAE_line.split("   ")[1]
                        dataratio = MAE_line.split("   ")[2]
                        numstations = MAE_line.split("   ")[3].strip()
                        data_check = True


                if data_check == False:
                    print("   **Skipping " + model + grid + ", no data yet**")
                    skipped_modelnames.append(legend_labels[leg_count] + ":  (none)")
                    leg_count = leg_count+1
                    continue


                #open the RMSE file
                with open(textfile_folder +  modelpath  + input_domain + '/' + variable + '/' + "RMSE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt") as f:
                    RMSE_lines = f.readlines()

                #find the line for the given dates
                for RMSE_line in RMSE_lines:
                    if date_entry1 in RMSE_line and date_entry2 in RMSE_line:
                        RMSE = RMSE_line.split("   ")[1]

                #open the MAE file
                with open(textfile_folder +  modelpath  + input_domain + '/' + variable + '/' + "spcorr_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt") as f:
                    spcorr_lines = f.readlines()

                #find the line for the given dates
                for spcorr_line in spcorr_lines:
                    if date_entry1 in spcorr_line and date_entry2 in spcorr_line:
                        spcorr = spcorr_line.split("   ")[1]

                #this removes models if more than half of data points are missing
                if int(dataratio.split("/")[0]) < int(dataratio.split("/")[1])/2:
                    print("   **Skipping " + model + grid + ", less than 50% of data points**")
                    skipped_modelnames.append(legend_labels[leg_count] + ":  (" + dataratio + ")")
                    leg_count = leg_count+1
                    continue

                #only applies for the hrs and day 1 (not day2-7)
                if model + gridname in ["WRF3GEM_g3","WRF3GFS_g3","WRF3GFSgc01_g3","WRF4ICON_g3"]:
                    removed_hours = 3
                elif model + gridname in ["WRF3GEM_g4","WRF3GFS_g4"]:
                    removed_hours = 6
                elif model + gridname == "WRF3GFS_g5":
                    removed_hours = 9
                else:
                    removed_hours = 0

                # this checks how many stations were used in each average
                if int(numstations.split("/")[0]) < int(numstations.split("/")[1]):
                    numofstations.append(legend_labels[leg_count] + ": (" + numstations + ")")


                MAE_list.append(float(MAE))
                RMSE_list.append(float(RMSE))
                correlation_list.append(float(spcorr))
                modelcolors.append(model_colors[color_count])

                if int(dataratio.split("/")[0]) < int(dataratio.split("/")[1])-removed_hours*(delta+1):
                    if int(numstations.split("/")[0]) != int(numstations.split("/")[1]):
                        modelnames.append(legend_labels[leg_count] + "*^")
                    else:
                        modelnames.append(legend_labels[leg_count] + "*")
                    edited_modelnames.append(legend_labels[leg_count] + ":  (" + dataratio + ")")

                else:
                    if int(numstations.split("/")[0]) != int(numstations.split("/")[1]):
                        modelnames.append(legend_labels[leg_count] + "^")
                    else:
                        modelnames.append(legend_labels[leg_count])

            #else:
            #    print("   Skipping  " + model + gridname + "   " + time_domain + " (doesn't exist)")


            leg_count = leg_count+1

        color_count = color_count+1

     return(MAE_list,RMSE_list,correlation_list,modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations)

def make_weights(MAE, RMSE, correlation):

    r_half = 16
    r_cut = 30
    if stat_type == "MAE_":
        MAE_weights = []
        MAE_sorted, modelnames_sortedMAE = zip(*sorted(zip(MAE, modelnames)))
        
        for i in range(len(MAE_sorted)):
            f = exp(-6*(i-r_half)/(r_cut-r_half))
            MAE_weight = f/(1+f)
            MAE_weights.append(MAE_weight)        
        
        MAE_weights = [i/sum(MAE_weights) for i in MAE_weights]
        MAE_w = pd.DataFrame(MAE_weights, columns = modelnames_sortedMAE)
        return(MAE_w)

    elif stat_type == "RMSE_":
    
        RMSE_weights = []
        RMSE_sorted, modelnames_sortedRMSE = zip(*sorted(zip(RMSE, modelnames)))
        
        for i in range(len(RMSE_sorted)):
            f = exp(-6*(i-r_half)/(r_cut-r_half))            
            RMSE_weight = f/(1+f)
            RMSE_weights.append(RMSE_weight)
        RMSE_weights = [i/sum(RMSE_weights) for i in RMSE_weights]
        RMSE_w = pd.DataFrame(RMSE_weights, columns = modelnames_sorted RMSE)
        return(RMSE_w)

    elif stat_type == "spcorr_":
    
        SPCORR_weights = []
        SPCORR_sorted, modelnames_sortedSPCORR = zip(*sorted(zip(SPCORR, modelnames),reverse=True))
         
        for i in range(len(SPCORR_sorted)):
            f = exp(-6*(i-r_half)/(r_cut-r_half))
            spcorr_weight = f/(1+f)
            SPCORR_weights.append(spcorr_weight)

        SPCORR_weights = [i/sum(SPCORR_weights) for i in SPCORR_weights]
        corr_w = pd.DataFrame(scporr_weights, columns = modelnames_sortedSPCORR)
        return(corr_w)
    
def mk_ensemble(MAE_w, RMSE_w,,corr_w, start_date, end_date, variable, fcst_all):

    for m in range(len(fcst_all.columns)):
        MAE_weight = MAE_w.loc[:,fcst_all.columns[m]][0]
        MAE_df = fcst_all[fcst_all.columns[m]]*weight

        RMSE_weight = RMSE_w.loc[:,fcst_all.columns[m]][0]
        RMSE_df = fcst_all[fcst_all.columns[m]]*weight

        corr_weight = corr_w.loc[:,fcst_all.columns[m]][0]
        corr_df = fcst_all[fcst_all.columns[m]]*weight
    
    return(MAE_df, RMSE_df_corr_df)


def ttest(df1.ENS_W, df1.ENS_M, date_entry1, dateentry2):
    ttest_res = stats.ttest_ind(i.ENS_W, i.ENS_M)

    ttest_file = open(save_folder + "ttest_"+i+"_results.txt", 'a')
    ttest_file.write(str(date_entry1) + " " + str(date_entry2) + "   ")
    ttest_file.write("%3.3f " % (ttest_res.statistic) + " ")
    ttest_file.write("%3.3f " % (ttest_res.pvalue) + "\n")
    ttest_file.close()

    return()

def write_stats(df):
        
    #stats for weighted ensemble
    ENS_W_spcorr = stats.spearmanr(df.ENS_W, df.Obs, nan_policy='omit')
    ENS_W_MAE = mean_absolute_error(df.Obs, df.ENS_W)
    ENS_W_RMSE = mean_squared_error(df.Obs, df.ENS_W, squared=False)
        

    #stats for standard ensemble
    ENS_M_spcorr = stats.spearmanr(df.ENS_M, df.Obs, nan_policy='omit')
    ENS_M_MAE = mean_absolute_error(df.Obs, df.ENS_M)
    ENS_M_RMSE = mean_squared_error(df.Obs, df.ENS_M, squared=False)
       
    #write stats to textfiles
    mae_f = open(save_folder + 'MAE_'+input_variable+'_'+weight_type+'.txt','a')
    mae_f.write(str(date_entry1) + " " + str(date_entry2) + "   ")
    mae_f.write("%3.3f  " % (ENS_W_MAE))
    mae_f.write("%3.3f  " % (ENS_M_MAE) + "\n")
    mae_f.close()

    rmse_f = open(save_folder + 'RMSE_'+input_variable+'_'+weight_type+'.txt','a')
    rmse_f.write(str(date_entry1) + " " + str(date_entry2) + "   ")
    rmse_f.write("%3.3f  " % (ENS_W_RMSE))
    rmse_f.write("%3.3f  " % (ENS_M_RMSE) + "\n")
    rmse_f.close()

    spcorr_f = open(save_folder + 'spcorr_'+input_variable+'_'+weight_type+'.txt','a')
    spcorr_f.write(str(date_entry1) + " " + str(date_entry2) + "   ")
    spcorr_f.write("%3.3f  " % (ENS_W_spcorr.statistic))
    spcorr_f.write("%3.3f  " % (ENS_W_spcorr.pvalue))
    spcorr_f.write("%3.3f  " % (ENS_M_spcorr.statistic))
    spcorr_f.write("%3.3f  " % (ENS_M_spcorr.pvalue) + "\n")
    spcorr_f.close()

    return()
