#!/usr/bin python

"""
Created in 2023 adapted from code by Eva Gnegy (2021)
@author: Reagan McKinney

These are the functions that feed into the mk_weighted_ensemble.py file. This script holds all the functions
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
textfile_folder = '/verification/weighted-Statistics/'

save_folder='/home/verif/verif-post-process/weights/ensemble/src/output_ens_num/'
###########################################################
### -------------------- INPUTS -- ------------------------
###########################################################
# thresholds for discluding erroneous data 
precip_threshold = 250 #recorded at Buffalo Gap 1961 https://www.canada.ca/en/environment-climate-change/services/water-overview/quantity/floods/events-prairie-provinces.html
wind_threshold = 400 #recorded Edmonton, AB 1987 http://wayback.archive-it.org/7084/20170925152846/https://www.ec.gc.ca/meteo-weather/default.asp?lang=En&n=6A4A3AC5-1#tab5
temp_min = -63 #recorded in Snag, YT 1947 http://wayback.archive-it.org/7084/20170925152846/https://www.ec.gc.ca/meteo-weather/default.asp?lang=En&n=6A4A3AC5-1#tab5
temp_max = 49.6 #recorded in Lytton, BC 2021 https://www.canada.ca/en/environment-climate-change/services/top-ten-weather-stories/2021.html#toc2

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