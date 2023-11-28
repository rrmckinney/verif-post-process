#!/usr/bin python

"""
Created in 2023 adapted from code by Eva Gnegy (2021)
@author: Reagan McKinney

These are the functions that feed into the leaderboard-txt-sqlite2.py script that calculates the statistics 
to be plotted on the website. See that file for more info. 
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
import warnings
warnings.filterwarnings("ignore",category=RuntimeWarning)

###########################################################
### -------------------- FILEPATHS ------------------------
###########################################################

#location where obs files are (all sql databases should be in this directory)
obs_filepath = "/verification/Observations/"

#location where forecast files are 
fcst_filepath = "/home/verif/verif-post-process/weights/LF/output-rcut15/weights-seasonal/"

#description file for stations
station_file = '/home/verif/verif-post-process/input/station_list_master.txt'

#description file for models
models_file = '/home/verif/verif-post-process/input/model_list.txt'

#folder where the stats save
textfile_folder = '/home/verif/verif-post-process/weights/LF/output-rcut15/'

#editting mode for textfile

wm = 'w'
###########################################################
### -------------------- INPUTS -- ------------------------
###########################################################

# thresholds for discluding erroneous data 
precip_threshold = 250 #recorded at Buffalo Gap 1961 https://www.canada.ca/en/environment-climate-change/services/water-overview/quantity/floods/events-prairie-provinces.html
wind_threshold = 400 #recorded Edmonton, AB 1987 http://wayback.archive-it.org/7084/20170925152846/https://www.ec.gc.ca/meteo-weather/default.asp?lang=En&n=6A4A3AC5-1#tab5
temp_min = -63 #recorded in Snag, YT 1947 http://wayback.archive-it.org/7084/20170925152846/https://www.ec.gc.ca/meteo-weather/default.asp?lang=En&n=6A4A3AC5-1#tab5
temp_max = 49.6 #recorded in Lytton, BC 2021 https://www.canada.ca/en/environment-climate-change/services/top-ten-weather-stories/2021.html#toc2

###########################################################
### -------------------- FUNCTIONS ------------------------
###########################################################


# makes a list of the dates you want from start to end, used to make sure the models and obs have the right dates
# obs get their own list because it will be different days than the initializition dates from the models for anything
#   past hours 0-24
def listofdates(start_date, end_date, obs = False):
    if obs == False:
        start = datetime.datetime.strptime(start_date, "%y%m%d").date()
        end = datetime.datetime.strptime(end_date, "%y%m%d").date()

    elif obs == True:
        startday = 0 #forhour 1
        endday = 7 #for hour 180
        
        start = datetime.datetime.strptime(start_date, "%y%m%d").date() + timedelta(days=startday)
        end = datetime.datetime.strptime(end_date, "%y%m%d").date() + timedelta(days=endday)
    
    numdays = (end-start).days 
    date_list = [(start + datetime.timedelta(days=x)).strftime("%y%m%d") for x in range(numdays+1)]

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
 
    elif variable == "PCPT24":
        
        if str(station) in stations_with_PCPTOT or str(station) in stations_with_PCPT24:
            flag=True        
            
    return(flag)

# checks to see if the right amount of dates exist, which is used for when new models/stations are added
# default station exists for when a new model is added (instead of new station)
def check_dates(start_date, delta, filepath, station):
    
    flag = True
            
    check_dates = np.loadtxt(filepath + station + ".csv",usecols=0,dtype=str)
    
    start_date = pd.to_datetime(start_date, format='%y%m%d').strftime('%Y-%m-%d')
    print(start_date)
    if np.size(check_dates) < delta+1:
         print("    Not enough dates available for this model/station/variable")
         flag = False
            
    elif start_date not in check_dates:
        print("    Model collection started " + check_dates[1] + ", which is after input start_date")
        flag = False
        
    return(flag)
    

def make_df(date_list_obs, start_date, end_date):
    date_list_obs = listofdates(start_date, end_date, obs=True)
    df_new = pd.DataFrame()
    for day in date_list_obs:
        dates = [day] * 24
        filehours_obs = get_filehours(1, 24)
        
        df = pd.DataFrame({'date': dates, 'time': filehours_obs})
        df['datetime'] = pd.to_datetime(df['date']+' '+df['time'], format = '%y%m%d %H')
        
        df_new = pd.concat([df_new, df])
    df_new = df_new.set_index('datetime') 
    return(df_new)

def get_all_obs(delta, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6,  all_stations, variable, start_date, end_date, date_list_obs):
    
    print("Reading observational dataframe for " + variable + ".. ")
    
    df_new = make_df(date_list_obs, start_date, end_date)
    
    if variable == 'SFCTC_KF' or variable == 'SFCTC':
        station_list = copy.deepcopy(stations_with_SFCTC)              
    elif variable == 'SFCWSPD_KF' or variable == 'SFCWSPD':  
        station_list = copy.deepcopy(stations_with_SFCWSPD) 
    
    elif variable == "PCPTOT":
        if variable == "PCPT6":
            station_list = [st for st in stations_with_PCPTOT if st not in stations_with_PCPT6 ]
        elif variable == "PCPT24":
            station_list = [st for st in stations_with_PCPTOT if st not in stations_with_PCPT24 ]
        else:
            station_list = copy.deepcopy(stations_with_PCPTOT)        
    
    elif variable == "PCPT6":
        station_list = copy.deepcopy(stations_with_PCPT6) 
    
    
    elif variable == "PCPT24":
        station_list = copy.deepcopy(stations_with_PCPT24) 
        
    #KF variables are the same as raw for obs
    if "_KF" in variable:
        variable = variable[:-3]
        
    filehours_obs = get_filehours(1,24)
    
    obs_df_60hr = pd.DataFrame()  
    obs_df_84hr = pd.DataFrame()  
    obs_df_120hr = pd.DataFrame() 
    obs_df_180hr = pd.DataFrame() 
    obs_df_day1 = pd.DataFrame()
    obs_df_day2 = pd.DataFrame()
    obs_df_day3 = pd.DataFrame()  
    obs_df_day4 = pd.DataFrame()  
    obs_df_day5 = pd.DataFrame()  
    obs_df_day6 = pd.DataFrame()  
    obs_df_day7 = pd.DataFrame() 
    
    for station in station_list:
        print( "    Now on station " + station) 
         
        if station not in all_stations:
            #print("   Skipping station " + station)
            continue
        if len(station) < 4:
            station = "0" +station
        
        # for hour in filehours_obs:
        #     if float(hour) < 1000:
        #             hour = str(hour).lstrip('0')
        sql_con = sqlite3.connect(obs_filepath + variable + "/" + station + ".sqlite")
        sql_query = "SELECT * from 'All' WHERE date BETWEEN 20" +str(date_list_obs[0]) + " AND 20" + str(date_list_obs[len(date_list_obs)-1])       
        obs = pd.read_sql_query(sql_query, sql_con)
        obs['datetime'] = None
        
        for y in range(len(obs['Time'])):
            hour = int(obs['Time'][y])/100
            obs.loc[y,'datetime'] = pd.to_datetime(obs.loc[y,'Date'], format='%Y%m%d') + timedelta(hours=hour)
        
        obs = obs.set_index('datetime')
        
        df_all = df_new.join(obs, on='datetime')
        
        obs_all = df_all['Val']
        # remove data that falls outside the physical bounds (higher than the verified records for Canada
        for i in range(len(obs_all)):
            
            if variable == 'SFCTC_KF' or variable == 'SFCTC':
                if obs_all[i] > temp_max:
                    obs_all[i] = np.nan
                if obs_all[i] < temp_min:
                    obs_all[i] = np.nan
            
            if variable == 'SFCWSPD_KF' or variable == 'SFCWSPD':
                if obs_all[i] > wind_threshold:
                    obs_all[i] = np.nan
            
            if variable == 'PCPTOT':
                if obs_all[i] > precip_threshold:
                    obs_all[i] = np.nan

        hr60_obs = obs_all[:60]     #84 x 7   (30) 
        hr84_obs = obs_all[:84]     #84 x 7   (30)     
        hr120_obs = obs_all[:120]   #120 x 7  (30) 
        day1_obs = obs_all[:24]     #24 x 7   (30)   
        day2_obs = obs_all[24:48]   #24 x 7   (30)   
        day3_obs = obs_all[48:72]   #24 x 7   (30)     
        day4_obs = obs_all[72:96]   #24 x 7   (30)  
        day5_obs = obs_all[96:120]  #24 x 7   (30)  
        day6_obs = obs_all[120:144] #24 x 7   (30)  
        day7_obs = obs_all[144:168] #24 x 7   (30)  
            
        final_obs_180hr = np.array(obs_all).T
        final_obs_60hr = np.array(hr60_obs).T
        final_obs_84hr = np.array(hr84_obs).T
        final_obs_120hr = np.array(hr120_obs).T
        final_obs_day1 = np.array(day1_obs).T
        final_obs_day2 = np.array(day2_obs).T
        final_obs_day3 = np.array(day3_obs).T
        final_obs_day4 = np.array(day4_obs).T
        final_obs_day5 = np.array(day5_obs).T
        final_obs_day6 = np.array(day6_obs).T
        final_obs_day7 = np.array(day7_obs).T

        obs_df_180hr[station] = final_obs_180hr.flatten() # 1260 (180x7) for each station for weekly
        obs_df_60hr[station] = final_obs_60hr.flatten()
        obs_df_84hr[station] = final_obs_84hr.flatten()   # 588 (84x7)
        obs_df_120hr[station] = final_obs_120hr.flatten() # 840 (120x7)
        obs_df_day1[station] = final_obs_day1.flatten()   # 168 (24x7) 
        obs_df_day2[station] = final_obs_day2.flatten()   # 168 (24x7) 
        obs_df_day3[station] = final_obs_day3.flatten()   # 168 (24x7) 
        obs_df_day4[station] = final_obs_day4.flatten()   # 168 (24x7) 
        obs_df_day5[station] = final_obs_day5.flatten()   # 168 (24x7) 
        obs_df_day6[station] = final_obs_day6.flatten()   # 168 (24x7) 
        obs_df_day7[station] = final_obs_day7.flatten()   # 168 (24x7) 
        
        #extra_point_df[station] = np.array([extra_point])
        # output is a dataframe with the column names as the station, with 420 rows for 60x7 or 60x30
    return(obs_df_60hr,obs_df_84hr,obs_df_120hr,obs_df_180hr,obs_df_day1,obs_df_day2,obs_df_day3,obs_df_day4,obs_df_day5,obs_df_day6,obs_df_day7)

# returns the fcst data for the given model/grid
def get_fcst(station, filepath, variable, date_list,filehours):
    
    fcst = []

# pulls out a list of the files for the given station+variable+hour wanted   
    
    file = 'weights_all_60hr_'+variable+'_fall'

    all_dates = np.loadtxt(filepath + file,usecols=0,skiprows = 1, dtype=str)
    all_dates = pd.to_datetime(all_dates, format='%Y-%m-%d').strftime('%y%m%d')

    # gets the indices for the dates we want to select
    indices = []
    [indices.append(list(all_dates).index(date)) for date in date_list]

    select_dates = all_dates[indices]

    if all(select_dates != date_list):
        raise Exception("fcst error: " + filepath + file + " has the wrong dates")
    
    # collects all fcst data for the given dates range
    # contains a list for every hour, each containing all of the wanted dates for that hour  
    print(indices) 
    open_fcst = np.loadtxt(filepath + file,usecols=1,delimiter=',', skiprows=indices[0]+1, max_rows=len(filehours), dtype=str)
    
    new_fcst = np.where(open_fcst == "?", np.nan, open_fcst) #sometimes ENS reads as ?
                
    fcst.append(new_fcst.astype(np.float))

    return(fcst)       



# this removes (NaNs) any fcst data where the obs is not recorded, or fcst is -999
def remove_missing_data(fcst, obs):
    print(len(fcst))
    print(len(obs))
    for i in range(len(fcst)):        
        if math.isnan(obs[i]) == True:
            fcst[i] = np.nan
            
        if fcst[i] == -999:
            fcst[i] = np.nan
            obs[i] = np.nan
                
    return(fcst,obs) 

def make_textfile(stat_type, weight_type,  input_domain, savetype, date_entry1, date_entry2, time_domain, variable, filepath, MAE, RMSE, corr, len_fcst, numstations):
   
    path = weight_type + '/' + input_domain + '/' + stat_type + '/'
    f1 = open(textfile_folder + path  + variable + '/' + "MAE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",wm+"+")       
    read_f1 = np.loadtxt(textfile_folder +  path  + variable + '/' + "MAE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",dtype=str)  
    if date_entry1 not in read_f1 and date_entry2 not in read_f1:
    
        f1.write(str(date_entry1) + " " + str(date_entry2) + "   ")
        
        f1.write("%3.3f   " % (MAE))
        f1.write(len_fcst + "   ")
        f1.write(numstations + "\n")
    
        f1.close()    
    
    f2 = open(textfile_folder +  path  + variable + '/' + "RMSE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",wm+"+")       
    read_f2 = np.loadtxt(textfile_folder +  path  + variable + '/' + "RMSE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",dtype=str)  
    if date_entry1 not in read_f2 and date_entry2 not in read_f2:
        f2.write(str(date_entry1) + " " + str(date_entry2) + "   ")
        
        f2.write("%3.3f   " % (RMSE))
        f2.write(len_fcst + "   ")
        f2.write(numstations + "\n")
        
        f2.close()  
    
    
    f3 = open(textfile_folder +  path +  variable + '/' + "spcorr_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",wm+"+") 
    read_f3 = np.loadtxt(textfile_folder +  path +  variable + '/' + "spcorr_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",dtype=str)  
    if date_entry1 not in read_f3 and date_entry2 not in read_f3:
        f3.write(str(date_entry1) + " " + str(date_entry2) + "   ")
        
        f3.write("%3.3f   " % (corr))
        f3.write(len_fcst + "   ")
        f3.write(numstations + "\n")
        
        f3.close()  


def trim_fcst(all_fcst,obs_df,station,start,end,variable,filepath,date_list,filehours,all_fcst_KF,maxhour, delta, input_domain):

    print(start)
    print(end)
    if variable == "PCPT6":
        if int(end)==int(maxhour):
            trimmed_fcst = all_fcst[0][start+1:end-5] 
        else:
            trimmed_fcst = all_fcst[0][start+1:end+1]  
    else:
        trimmed_fcst = all_fcst[0][start:end]   
    
    
    fcst_final = np.array(trimmed_fcst).T
    fcst_flat = fcst_final.flatten() 
    
    if variable == "PCPT6":
        fcst_flat = np.reshape(fcst_flat, (-1, 6)).sum(axis=-1) #must be divisible by 6

    obs_flat = np.array(obs_df[station])
    if len(np.shape(obs_flat)) > 1:
        obs_flat = obs_flat[:,1]
    
    # removes (NaNs) fcst data where there is no obs
    fcst_NaNs,obs_NaNs = remove_missing_data(fcst_flat, obs_flat)  

     
    if input_domain == "small" and variable in ["SFCTC","SFCWSPD"] and all_fcst_KF == True:
        trimmed_fcst_KF = all_fcst_KF[start:end]   
        fcst_final_KF = np.array(trimmed_fcst_KF).T
        fcst_flat_KF = fcst_final_KF.flatten() 
        
        fcst_NaNs,_ = remove_missing_data(fcst_flat, fcst_flat_KF) 
    

    return(fcst_NaNs, obs_NaNs)

def get_statistics(delta, stat_type, weight_type,  input_domain, savetype, date_entry1, date_entry2, maxhour,hour,length,fcst_allstations,obs_allstations,num_stations,totalstations,time_domain,variable,filepath):
    
    if int(maxhour) >= hour:
        fcst_avg = np.nanmean(fcst_allstations,axis=0) 
        obs_avg = np.nanmean(obs_allstations,axis=0)
        fcst_noNaNs, obs_noNaNs = [],[]
        
        for l in range(len(fcst_avg)):
            if np.isnan(fcst_avg[l]) == False:
                fcst_noNaNs.append(fcst_avg[l])
                obs_noNaNs.append(obs_avg[l])
              
        # rounds each forecast and obs to one decimal
        obs_rounded = np.round(obs_noNaNs,1)
        fcst_rounded = np.round(fcst_noNaNs,1)
        
        if len(fcst_rounded) == 0:
            model_not_available(stat_type, weight_type,  delta, input_domain, date_entry1, date_entry2, savetype, maxhour,hour,length,totalstations,time_domain,variable,filepath)
        
        else:
            MAE = mean_absolute_error(obs_rounded,fcst_rounded)
            MSE = mean_squared_error(obs_rounded,fcst_rounded)
            RMSE = math.sqrt(MSE)
            corr = stats.spearmanr(obs_rounded,fcst_rounded)[0]
            
            if variable == "PCPT6":
                length = int(length/6)
            
            elif variable == "PCPT24":
                length = int(length/24)
            else:
                length = length            
            
            len_fcst = str(len(fcst_noNaNs)) + "/" + str(length)   
            numstations = str(num_stations) + "/" + str(totalstations)
            
            make_textfile(stat_type, weight_type,  input_domain, savetype, date_entry1, date_entry2, time_domain, variable, filepath, MAE, RMSE, corr, len_fcst, numstations)

def model_not_available(stat_type, weight_type,  delta, input_domain, date_entry1, date_entry2, savetype, maxhour,hour,length,totalstations,time_domain,variable,filepath):

    path = weight_type + '/' + input_domain + '/' + stat_type + '/'

    if int(maxhour) >= hour:  
        if variable == "PCPT6":
            if int(maxhour) == int(hour):
                total_length = int(((length*(delta+1))/6)-(delta+1))
            else:
                total_length = int((length*(delta+1))/6)
        elif variable == "PCPT24":
            if int(maxhour) == int(hour):
                total_length = int(((length*(delta+1))/24)-(delta+1))
            else:
                total_length = int((length*(delta+1))/24)
        else:
            total_length = int(length*(delta+1))
                
        len_fcst = "0/" + str(total_length)
        numstations = "0/" + str(totalstations)
        
        
        f1 = open(textfile_folder +  path   + variable + '/' + "MAE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",wm+"+")       
        read_f1 = np.loadtxt(textfile_folder +  path  +  variable + '/' + "MAE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",dtype=str)  
        if date_entry1 not in read_f1 and date_entry2 not in read_f1:
            f1.write(str(date_entry1) + " " + str(date_entry2) + "   ")
            
            f1.write("nan   ") #MAE
            f1.write(len_fcst + "   ")
            f1.write(numstations + "\n")
        
            f1.close()    
                
        
        f2 = open(textfile_folder +  path  +  variable + '/' + "RMSE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",wm+"+")       
        read_f2 = np.loadtxt(textfile_folder +  path  +  variable + '/' + "RMSE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",dtype=str)  
        if date_entry1 not in read_f2 and date_entry2 not in read_f2:
            f2.write(str(date_entry1) + " " + str(date_entry2) + "   ")
            
            f2.write("nan   ") #RMSE
            f2.write(len_fcst + "   ")
            f2.write(numstations + "\n")
            
            f2.close()  
            
        
        f3 = open(textfile_folder +  path  +  variable + '/' + "spcorr_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",wm+"+") 
        read_f3 = np.loadtxt(textfile_folder +  path  + variable + '/' + "spcorr_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",dtype=str)  
        if date_entry1 not in read_f3 and date_entry2 not in read_f3:
            f3.write(str(date_entry1) + " " + str(date_entry2) + "   ")
            
            f3.write("nan   ") #corr
            f3.write(len_fcst + "   ")
            f3.write(numstations + "\n")
            
            f3.close()  

def get_rankings(filepath, delta, input_domain, date_entry1, date_entry2, savetype, all_stations, station_df, variable, date_list, stat_type, weight_type,  maxhour, filehours, obs_df_60hr,obs_df_84hr,obs_df_120hr,obs_df_180hr,obs_df_day1,obs_df_day2,obs_df_day3,obs_df_day4,obs_df_day5,obs_df_day6,obs_df_day7, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6):
    
  
    if os.path.isdir(filepath) == False:
        os.makedirs(filepath)

    #these variables will contain all the fcst and obs for the stations that exist for each model
    obs_allstations_180hr, fcst_allstations_180hr = [],[]
    obs_allstations_120hr, fcst_allstations_120hr = [],[]
    obs_allstations_84hr, fcst_allstations_84hr = [],[]
    obs_allstations_60hr, fcst_allstations_60hr = [],[]
    obs_allstations_day1, fcst_allstations_day1 = [],[]
    obs_allstations_day2, fcst_allstations_day2 = [],[]
    obs_allstations_day3, fcst_allstations_day3 = [],[]
    obs_allstations_day4, fcst_allstations_day4 = [],[]
    obs_allstations_day5, fcst_allstations_day5 = [],[]
    obs_allstations_day6, fcst_allstations_day6 = [],[]
    obs_allstations_day7, fcst_allstations_day7 = [],[]
    
    totalstations = 0
    num_stations = 0
    
    if 'SFCTC' in variable:
        stations_in_var = stations_with_SFCTC
    elif 'SFCWSPD' in variable:
        stations_in_var = stations_with_SFCWSPD
    elif 'PCPTOT' in variable:
        stations_in_var = stations_with_PCPTOT
    elif 'PCPT6' in variable:
        stations_in_var = stations_with_PCPT6

    for station in stations_in_var:

        if station not in all_stations:
            #print("   Skipping station " + station + ")
            continue

        if check_variable(variable, station, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6) == False:                  
            #print("   Skipping station " + station + " (no " + variable + " data)")
            continue
        
        if len(station) < 4:
            station = "0" +str(station)
        
        if check_dates(date_entry1, delta, filepath, station) == False:
            print("   Skipping station " + station + " (not enough dates yet)")
            continue

        
        # total stations that should be included in each model/grid
        totalstations = totalstations+1

        all_fcst_KF = False
            
        all_fcst = get_fcst(station, filepath, variable, date_list,filehours)    #goes to maxhour       
       
        fcst_final_all = np.array(all_fcst).T
        fcst_flat_all = fcst_final_all.flatten()
        
        obs_flat_all = np.array(obs_df_180hr[station])
            
        #checks 180 hour only
        if pd.isna(fcst_flat_all).all() == True:    
            print("   Skipping station " + station + " (No forecast data)")
            continue
        
        if pd.isna(obs_flat_all).all() == True:    
            print("   Skipping station " + station + " (No obs data)")
            continue
    
        # total stations that ended up being included (doesn't count ones with no data)
        num_stations = num_stations+1
      
        if int(maxhour) >= 180:
            fcst_NaNs_180hr, obs_flat_180hr = trim_fcst(all_fcst,obs_df_180hr,station,0,180,variable,filepath,date_list,filehours,all_fcst_KF,maxhour, delta, input_domain)                            
            fcst_allstations_180hr.append(fcst_NaNs_180hr)
            obs_allstations_180hr.append(obs_flat_180hr)
            
         
        if int(maxhour) >= 168:        
            fcst_NaNs_day7,  obs_flat_day7  = trim_fcst(all_fcst,obs_df_day7,station,144,168,variable,filepath,date_list,filehours,all_fcst_KF,maxhour, delta, input_domain)  
            fcst_allstations_day7.append(fcst_NaNs_day7)
            obs_allstations_day7.append(obs_flat_day7)
            
        if int(maxhour) >= 144:
            fcst_NaNs_day6,  obs_flat_day6  = trim_fcst(all_fcst,obs_df_day6,station,120,144,variable,filepath,date_list,filehours,all_fcst_KF,maxhour, delta, input_domain)  
            fcst_allstations_day6.append(fcst_NaNs_day6)
            obs_allstations_day6.append(obs_flat_day6)
            
        if int(maxhour) >= 120:
            
            fcst_NaNs_day5,  obs_flat_day5  = trim_fcst(all_fcst,obs_df_day5,station,96,120,variable,filepath,date_list,filehours,all_fcst_KF,maxhour, delta, input_domain)  
            fcst_allstations_day5.append(fcst_NaNs_day5)
            obs_allstations_day5.append(obs_flat_day5)

        if int(maxhour) >= 96:
            fcst_NaNs_day4,  obs_flat_day4  = trim_fcst(all_fcst,obs_df_day4,station,72,96,variable,filepath,date_list,filehours,all_fcst_KF,maxhour, delta, input_domain)  
            fcst_allstations_day4.append(fcst_NaNs_day4)
            obs_allstations_day4.append(obs_flat_day4)
            
        if int(maxhour) >= 84:            
            fcst_NaNs_84hr,  obs_flat_84hr  = trim_fcst(all_fcst,obs_df_84hr,station,0,84,variable,filepath,date_list,filehours,all_fcst_KF,maxhour, delta, input_domain)  
            fcst_allstations_84hr.append(fcst_NaNs_84hr)
            obs_allstations_84hr.append(obs_flat_84hr)
            
        if int(maxhour) >= 72:
            fcst_NaNs_day3,  obs_flat_day3  = trim_fcst(all_fcst,obs_df_day3,station,48,72,variable,filepath,date_list,filehours,all_fcst_KF,maxhour, delta, input_domain)  
            fcst_allstations_day3.append(fcst_NaNs_day3)
            obs_allstations_day3.append(obs_flat_day3)
            
 
        fcst_NaNs_60hr,  obs_flat_60hr  = trim_fcst(all_fcst,obs_df_60hr,station,0,60,variable,filepath,date_list,filehours,all_fcst_KF,maxhour, delta, input_domain)  
        fcst_allstations_60hr.append(fcst_NaNs_60hr)
        obs_allstations_60hr.append(obs_flat_60hr)
                    
        fcst_NaNs_day1,  obs_flat_day1  = trim_fcst(all_fcst,obs_df_day1,station,0,24,variable,filepath,date_list,filehours,all_fcst_KF,maxhour, delta, input_domain)  
        fcst_allstations_day1.append(fcst_NaNs_day1)
        obs_allstations_day1.append(obs_flat_day1)
        
        fcst_NaNs_day2,  obs_flat_day2  = trim_fcst(all_fcst,obs_df_day2,station,24,48,variable,filepath,date_list,filehours,all_fcst_KF,maxhour, delta, input_domain)  
        fcst_allstations_day2.append(fcst_NaNs_day2)
        obs_allstations_day2.append(obs_flat_day2)

    #sometimes theres no forecast data for a model
    if num_stations == 0:
        print("   NO FORECAST DATA FOR " + stat_type + '-' + weight_type)
             
     
        model_not_available(stat_type, weight_type, delta, input_domain, date_entry1, date_entry2, savetype, maxhour,180,180,totalstations,'180hr',variable,filepath)
        model_not_available(stat_type, weight_type,  delta, input_domain, date_entry1, date_entry2, savetype, maxhour,120,120,totalstations,'120hr',variable,filepath)
        model_not_available(stat_type, weight_type,  delta, input_domain, date_entry1, date_entry2, savetype, maxhour,84,84,totalstations,'84hr',variable,filepath)
        model_not_available(stat_type, weight_type,  delta, input_domain, date_entry1, date_entry2, savetype, maxhour,60,60,totalstations,'60hr',variable,filepath)
    
        model_not_available(stat_type, weight_type,  delta, input_domain, date_entry1, date_entry2, savetype, maxhour,168,24,totalstations,'day7',variable,filepath)
        model_not_available(stat_type, weight_type,  delta, input_domain, date_entry1, date_entry2, savetype, maxhour,144,24,totalstations,'day6',variable,filepath)
        model_not_available(stat_type, weight_type,  delta, input_domain, date_entry1, date_entry2, savetype, maxhour,120,24,totalstations,'day5',variable,filepath)
        model_not_available(stat_type, weight_type,  delta, input_domain, date_entry1, date_entry2, savetype, maxhour,96,24,totalstations,'day4',variable,filepath)
        model_not_available(stat_type, weight_type,  delta, input_domain, date_entry1, date_entry2, savetype, maxhour,72,24,totalstations,'day3',variable,filepath)
        model_not_available(stat_type, weight_type,  delta, input_domain, date_entry1, date_entry2, savetype, maxhour,48,24,totalstations,'day2',variable,filepath)
        model_not_available(stat_type, weight_type,  delta, input_domain, date_entry1, date_entry2, savetype, maxhour,24,24,totalstations,'day1',variable,filepath)
        
    else:
    

        get_statistics(delta, stat_type, weight_type,  input_domain, savetype, date_entry1, date_entry2,maxhour,180,180,fcst_allstations_180hr,obs_allstations_180hr,num_stations,totalstations,'180hr',variable,filepath)
        get_statistics(delta,stat_type, weight_type, input_domain, savetype, date_entry1, date_entry2,maxhour,120,120,fcst_allstations_120hr,obs_allstations_120hr,num_stations,totalstations,'120hr',variable,filepath)
        get_statistics(delta,stat_type, weight_type, input_domain, savetype, date_entry1, date_entry2,maxhour,84,84,fcst_allstations_84hr,obs_allstations_84hr,num_stations,totalstations,'84hr',variable,filepath)
        get_statistics(delta,stat_type, weight_type,  input_domain, savetype, date_entry1, date_entry2,maxhour,60,60,fcst_allstations_60hr,obs_allstations_60hr,num_stations,totalstations,'60hr',variable,filepath)

                
        get_statistics(delta,stat_type, weight_type,  input_domain, savetype, date_entry1, date_entry2,maxhour,168,24,fcst_allstations_day7,obs_allstations_day7,num_stations,totalstations,'day7',variable,filepath)
        get_statistics(delta,stat_type, weight_type,  input_domain, savetype, date_entry1, date_entry2,maxhour,144,24,fcst_allstations_day6,obs_allstations_day6,num_stations,totalstations,'day6',variable,filepath)
        get_statistics(delta,stat_type, weight_type, input_domain, savetype, date_entry1, date_entry2,maxhour,120,24,fcst_allstations_day5,obs_allstations_day5,num_stations,totalstations,'day5',variable,filepath)
        get_statistics(delta,stat_type, weight_type,  input_domain, savetype, date_entry1, date_entry2,maxhour,96,24,fcst_allstations_day4,obs_allstations_day4,num_stations,totalstations,'day4',variable,filepath)
        get_statistics(delta,stat_type, weight_type,  input_domain, savetype, date_entry1, date_entry2,maxhour,72,24,fcst_allstations_day3,obs_allstations_day3,num_stations,totalstations,'day3',variable,filepath) 
        get_statistics(delta,stat_type, weight_type,  input_domain, savetype, date_entry1, date_entry2,maxhour,48,24,fcst_allstations_day2,obs_allstations_day2,num_stations,totalstations,'day2',variable,filepath)
        get_statistics(delta,stat_type, weight_type,  input_domain, savetype, date_entry1, date_entry2,maxhour,24,24,fcst_allstations_day1,obs_allstations_day1,num_stations,totalstations,'day1',variable,filepath)

def PCPT_obs_df_6(date_list_obs, delta, input_variable, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6,\
                  all_stations, start_date, end_date):

    # get the hourly precip values
    obs_df_60hr_1,obs_df_84hr_1,obs_df_120hr_1,obs_df_180hr_1,obs_df_day1_1,obs_df_day2_1,obs_df_day3_1,obs_df_day4_1,obs_df_day5_1,obs_df_day6_1,obs_df_day7_1 = get_all_obs(delta, \
        stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6, all_stations, "PCPTOT", \
    start_date, end_date, date_list_obs)
    
    # grab the extra hour on the last outlook day
    obs_df_60hr_1 = obs_df_60hr_1.append(obs_df_180hr_1.iloc[60],ignore_index=True)
    obs_df_84hr_1 = obs_df_84hr_1.append(obs_df_180hr_1.iloc[84],ignore_index=True)
    obs_df_120hr_1 = obs_df_120hr_1.append(obs_df_180hr_1.iloc[ 120],ignore_index=True)
    obs_df_day1_1 = obs_df_day1_1.append(obs_df_180hr_1.iloc[24],ignore_index=True)
    obs_df_day2_1 = obs_df_day2_1.append(obs_df_180hr_1.iloc[48],ignore_index=True)
    obs_df_day3_1 = obs_df_day3_1.append(obs_df_180hr_1.iloc[72],ignore_index=True)
    obs_df_day4_1 = obs_df_day4_1.append(obs_df_180hr_1.iloc[96],ignore_index=True)
    obs_df_day5_1 = obs_df_day5_1.append(obs_df_180hr_1.iloc[120],ignore_index=True)
    obs_df_day6_1 = obs_df_day6_1.append(obs_df_180hr_1.iloc[144],ignore_index=True)
    obs_df_day7_1 = obs_df_day7_1.append(obs_df_180hr_1.iloc[168],ignore_index=True)
    
      
    # remove the first hour (0 UTC)
    obs_df_60hr_1 = obs_df_60hr_1.iloc[1:].reset_index(drop=True)
    obs_df_84hr_1 = obs_df_84hr_1.iloc[1:].reset_index(drop=True)
    obs_df_120hr_1 = obs_df_120hr_1.iloc[1:].reset_index(drop=True)
    obs_df_180hr_1 = obs_df_180hr_1.iloc[1:-5].reset_index(drop=True)
    obs_df_day1_1 = obs_df_day1_1.iloc[1:].reset_index(drop=True)
    obs_df_day2_1 = obs_df_day2_1.iloc[1:].reset_index(drop=True)
    obs_df_day3_1 = obs_df_day3_1.iloc[1:].reset_index(drop=True)
    obs_df_day4_1 = obs_df_day4_1.iloc[1:].reset_index(drop=True)
    obs_df_day5_1 = obs_df_day5_1.iloc[1:].reset_index(drop=True)
    obs_df_day6_1 = obs_df_day6_1.iloc[1:].reset_index(drop=True)
    obs_df_day7_1 = obs_df_day7_1.iloc[1:].reset_index(drop=True)
    
    
    # sum every 6 hours (1-6 UTC, 7-12 UTC etc). report NaN if any of the 6 hours is missing
    obs_df_60hr_1_trimmed = obs_df_60hr_1.groupby(obs_df_60hr_1.index // 6).apply(pd.DataFrame.sum,skipna=False)
    obs_df_84hr_1_trimmed = obs_df_84hr_1.groupby(obs_df_84hr_1.index // 6).apply(pd.DataFrame.sum,skipna=False)
    obs_df_120hr_1_trimmed = obs_df_120hr_1.groupby(obs_df_120hr_1.index // 6).apply(pd.DataFrame.sum,skipna=False)
    obs_df_180hr_1_trimmed = obs_df_180hr_1.groupby(obs_df_180hr_1.index // 6).apply(pd.DataFrame.sum,skipna=False)
    obs_df_day1_1_trimmed = obs_df_day1_1.groupby(obs_df_day1_1.index // 6).apply(pd.DataFrame.sum,skipna=False)
    obs_df_day2_1_trimmed = obs_df_day2_1.groupby(obs_df_day2_1.index // 6).apply(pd.DataFrame.sum,skipna=False)
    obs_df_day3_1_trimmed = obs_df_day3_1.groupby(obs_df_day3_1.index // 6).apply(pd.DataFrame.sum,skipna=False)
    obs_df_day4_1_trimmed = obs_df_day4_1.groupby(obs_df_day4_1.index // 6).apply(pd.DataFrame.sum,skipna=False)
    obs_df_day5_1_trimmed = obs_df_day5_1.groupby(obs_df_day5_1.index // 6).apply(pd.DataFrame.sum,skipna=False)
    obs_df_day6_1_trimmed = obs_df_day6_1.groupby(obs_df_day6_1.index // 6).apply(pd.DataFrame.sum,skipna=False)
    obs_df_day7_1_trimmed = obs_df_day7_1.groupby(obs_df_day7_1.index // 6).apply(pd.DataFrame.sum,skipna=False)


    #grab the 6-hr accum precip values
    obs_df_60hr_6,obs_df_84hr_6,obs_df_120hr_6,obs_df_180hr_6,obs_df_day1_6,obs_df_day2_6,obs_df_day3_6,obs_df_day4_6,obs_df_day5_6,\
        obs_df_day6_6,obs_df_day7_6 = get_all_obs(delta, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6, \
                                                   all_stations, "PCPT6", start_date, end_date, date_list_obs)
        
    # grab the extra hour on the last outlook day
    obs_df_60hr_6 = obs_df_60hr_6.append(obs_df_180hr_6.iloc[60],ignore_index=True)
    obs_df_84hr_6 = obs_df_84hr_6.append(obs_df_180hr_6.iloc[84],ignore_index=True)
    obs_df_120hr_6 = obs_df_120hr_6.append(obs_df_180hr_6.iloc[120],ignore_index=True)
    obs_df_day1_6 = obs_df_day1_6.append(obs_df_180hr_6.iloc[24],ignore_index=True)
    obs_df_day2_6 = obs_df_day2_6.append(obs_df_180hr_6.iloc[48],ignore_index=True)
    obs_df_day3_6 = obs_df_day3_6.append(obs_df_180hr_6.iloc[72],ignore_index=True)
    obs_df_day4_6 = obs_df_day4_6.append(obs_df_180hr_6.iloc[96],ignore_index=True)
    obs_df_day5_6 = obs_df_day5_6.append(obs_df_180hr_6.iloc[120],ignore_index=True)
    obs_df_day6_6 = obs_df_day6_6.append(obs_df_180hr_6.iloc[144],ignore_index=True)
    obs_df_day7_6 = obs_df_day7_6.append(obs_df_180hr_6.iloc[168],ignore_index=True)
    
    
    # remove all values except the ones every 6 hours (6 UTC, 12 UTC, etc. (skipping the first))
    obs_df_60hr_6_trimmed = obs_df_60hr_6.iloc[::6, :][1:].reset_index(drop=True) #grabs every 6 hours (skipping hour 0)
    obs_df_84hr_6_trimmed = obs_df_84hr_6.iloc[::6, :][1:].reset_index(drop=True)
    obs_df_120hr_6_trimmed = obs_df_120hr_6.iloc[::6, :][1:].reset_index(drop=True)
    obs_df_180hr_6_trimmed = obs_df_180hr_6.iloc[::6, :][1:].reset_index(drop=True)
    obs_df_day1_6_trimmed = obs_df_day1_6.iloc[::6, :][1:].reset_index(drop=True)
    obs_df_day2_6_trimmed = obs_df_day2_6.iloc[::6, :][1:].reset_index(drop=True)
    obs_df_day3_6_trimmed = obs_df_day3_6.iloc[::6, :][1:].reset_index(drop=True)
    obs_df_day4_6_trimmed = obs_df_day4_6.iloc[::6, :][1:].reset_index(drop=True)
    obs_df_day5_6_trimmed = obs_df_day5_6.iloc[::6, :][1:].reset_index(drop=True)
    obs_df_day6_6_trimmed = obs_df_day6_6.iloc[::6, :][1:].reset_index(drop=True)
    obs_df_day7_6_trimmed = obs_df_day7_6.iloc[::6, :][1:].reset_index(drop=True)
    
    
    #combine the obs from manually accumulating 6 hours from hourly, and the pre-calculated 6 hours
    obs_df_60hr_all = pd.concat([obs_df_60hr_1_trimmed, obs_df_60hr_6_trimmed],axis=1)
    obs_df_84hr_all = pd.concat([obs_df_84hr_1_trimmed, obs_df_84hr_6_trimmed],axis=1)
    obs_df_120hr_all = pd.concat([obs_df_120hr_1_trimmed, obs_df_120hr_6_trimmed],axis=1)
    obs_df_180hr_all = pd.concat([obs_df_180hr_1_trimmed, obs_df_180hr_6_trimmed],axis=1)
    obs_df_day1_all = pd.concat([obs_df_day1_1_trimmed, obs_df_day1_6_trimmed],axis=1)
    obs_df_day2_all = pd.concat([obs_df_day2_1_trimmed, obs_df_day2_6_trimmed],axis=1)
    obs_df_day3_all = pd.concat([obs_df_day3_1_trimmed, obs_df_day3_6_trimmed],axis=1)
    obs_df_day4_all = pd.concat([obs_df_day4_1_trimmed, obs_df_day4_6_trimmed],axis=1)
    obs_df_day5_all = pd.concat([obs_df_day5_1_trimmed, obs_df_day5_6_trimmed],axis=1)
    obs_df_day6_all = pd.concat([obs_df_day6_1_trimmed, obs_df_day6_6_trimmed],axis=1)
    obs_df_day7_all = pd.concat([obs_df_day7_1_trimmed, obs_df_day7_6_trimmed],axis=1)

    return(obs_df_60hr_all,obs_df_84hr_all,obs_df_120hr_all,obs_df_180hr_all,obs_df_day1_all,obs_df_day2_all,obs_df_day3_all,obs_df_day4_all,\
           obs_df_day5_all,obs_df_day6_all,obs_df_day7_all)
