#!/usr/bin python

"""
Created in summer 2023

@author: Reagan McKinney

This script is based on a logistic curve weighting scheme.
"""

import os
import numpy as np
import pandas as pd
import datetime #import datetime, timedelta
from datetime import timedelta
import sys
from math import exp
from statistics import mean 
import copy
import warnings
import sqlite3
warnings.filterwarnings("ignore",category=RuntimeWarning)
###########################################################
### -------------------- FILEPATHS ------------------------
###########################################################

#location to save the images internally
save_folder = "/home/verif/verif-post-process/weights/LF/output/weights-seasonal/"

#description file for stations
station_file = '/home/verif/verif-post-process/input/station_list.txt'

#description file for models
models_file = '/home/verif/verif-post-process/input/model_list_weights.txt'

#location where obs files are (all sql databases should be in this directory)
obs_filepath = "/verification/Observations/"

#location where forecast files are (immediately within this directory should be model folders, then grid folders, then the sql databases)
fcst_filepath = "/verification/Forecasts/"

###########################################################
### -------------------- INPUT ------------------------
###########################################################

# takes an input date for the last day of the week you want to include
if len(sys.argv) == 5:
    date_entry1 = sys.argv[1]    #input date YYMMDD
    start_date = str(date_entry1) + '00'  
    input_startdate = datetime.datetime.strptime(start_date, "%y%m%d%H").date()
    print_startdate = datetime.datetime.strftime(input_startdate,"%m/%d/%y")
    
    date_entry2 = sys.argv[2]    #input date YYMMDD
    end_date = str(date_entry2) + '00'  
    input_enddate = datetime.datetime.strptime(end_date, "%y%m%d%H").date()
    print_enddate = datetime.datetime.strftime(input_enddate,"%m/%d/%y")

    delta = (input_enddate-input_startdate).days

    if delta == 6: # 6 is weekly bc it includes the start and end date (making 7)
        print("Performing WEEKLY calculation for " + start_date + " to " + end_date)
        savetype = "weekly"
        
    elif delta == 27 or delta == 28 or delta == 29 or delta == 30: # 29 is monthly bc it includes the start and end date (making 30)
        print("Performing MONTHLY calculation for " + start_date + " to " + end_date)
        savetype = "monthly"
    
    elif delta == 365: #yearly
        print("Performing YEARLY calculation for " + start_date + " to " + end_date)
        savetype="weekly"

    else:
        raise Exception("Invalid date input entries. Start and end date must be 7 or 28/29/30/31 days apart (for weekly and monthly stats) Entered range was: " + str(delta+1) + " days")
   

    input_domain = sys.argv[3]
    if input_domain not in ['large','small']:
        raise Exception("Invalid domain input entries. Current options: large, small. Case sensitive.")
    
    # weighting curve steepness, now user input, testing several values
    k = int(sys.argv[4])
    if input_domain not in ['40','80', '100', '150', '200', '500','1000']:
        raise Exception("Invalid domain input entries. Current options:'40','80', '100', '150', '200', '500','1000'. Case sensitive.")
    
else:
    raise Exception("Invalid input entries. Needs YYMMDD for start and end dates, domain size, and k")


winter = ['211201','220228']
spring = ['220301','220531']
summer = ['220601','220831']
fall = ['211001','211130', '220901','220930']
seasons = [winter,spring,summer,fall]

time_domain = '60hr'
#stations = np.loadtxt(station_file,usecols=0,delimiter=',',dtype='str')

variables = ['SFCTC', 'SFCTC_KF', 'SFCWSPD', 'SFCWSPD_KF', 'PCPTOT', 'PCPT6']
variable_names = ['Temperature-Raw', 'Temperature-KF', 'Wind Speed-Raw', 'Wind Speed-KF', 'Hourly Precipitation','6-Hour Accumulated Precipitation']
variable_units = ['[C]','[C]','[km/hr]','[km/hr]', '[mm/hr]','[mm/6hr]']

# list of model names as strings (names as they are saved in www_oper and my output folders)
models = np.loadtxt(models_file,usecols=0,dtype='str')

grids = np.loadtxt(models_file,usecols=1,dtype='str') #list of grid sizings (g1, g2, g3 etc) for each model
gridres = np.loadtxt(models_file,usecols=2,dtype='str') #list of grid resolution in km for each model
model_names = np.loadtxt(models_file,usecols=4,dtype='str') #longer names, used for legend

# thresholds for discluding erroneous data 
precip_threshold = 250 #recorded at Buffalo Gap 1961 https://www.canada.ca/en/environment-climate-change/services/water-overview/quantity/floods/events-prairie-provinces.html
wind_threshold = 400 #recorded Edmonton, AB 1987 http://wayback.archive-it.org/7084/20170925152846/https://www.ec.gc.ca/meteo-weather/default.asp?lang=En&n=6A4A3AC5-1#tab5
temp_min = -63 #recorded in Snag, YT 1947 http://wayback.archive-it.org/7084/20170925152846/https://www.ec.gc.ca/meteo-weather/default.asp?lang=En&n=6A4A3AC5-1#tab5
temp_max = 49.6 #recorded in Lytton, BC 2021 https://www.canada.ca/en/environment-climate-change/services/top-ten-weather-stories/2021.html#toc2

#station_info
station_df = pd.read_csv(station_file)

stations_with_SFCTC = np.array(station_df.query("SFCTC==1")["Station ID"],dtype=str)
stations_with_SFCWSPD = np.array(station_df.query("SFCWSPD==1")["Station ID"],dtype=str)
stations_with_PCPTOT = np.array(station_df.query("PCPTOT==1")["Station ID"],dtype=str)
stations_with_PCPT6 = np.array(station_df.query("PCPT6==1")["Station ID"],dtype=str)
stations_with_PCPT24 = np.array(station_df.query("PCPT24==1")["Station ID"],dtype=str)

all_stations = np.array(station_df.query("`Small domain`==1")["Station ID"],dtype=str)
    
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


def check_variable(variable, station, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6, stations_with_PCPT24):

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
    elif int("20" + start_date) < int(sql_result[0]):
        print("    Model collection started " + str(sql_result[0]) + ", which is after input start_date")
        flag = False
    cursor.close()
    
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

def get_all_obs(delta, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6, period, all_stations, variable, start_date, end_date, date_list_obs):
    
    print("Reading observational dataframe for " + variable + ".. ")
    
    df_new = make_df(date_list_obs, start_date, end_date)
    
    if variable == 'SFCTC_KF' or variable == 'SFCTC':
        station_list = copy.deepcopy(stations_with_SFCTC)              
    elif variable == 'SFCWSPD_KF' or variable == 'SFCWSPD':  
        station_list = copy.deepcopy(stations_with_SFCWSPD) 
    elif variable == "PCPTOT":
        if variable == "PCPT6":
            station_list = [st for st in stations_with_PCPTOT if st not in stations_with_PCPT6 ]
        else:
            station_list = copy.deepcopy(stations_with_PCPTOT)        
    
    elif variable == "PCPT6":
        station_list = copy.deepcopy(stations_with_PCPT6) 

    #KF variables are the same as raw for obs
    if "_KF" in variable:
        variable = variable[:-3]
            
    obs_df = pd.DataFrame()  

    
    for station in station_list:
        print( "    Now on station " + station) 
         
        if station not in all_stations:
            #print("   Skipping station " + station)
            continue
        if len(station) < 4:
            station = "0" +station
        
        if "PCPT" in variable:
            if check_dates(start_date, delta, fcst_filepath + 'ENS/' + variable + '/fcst.t/', "PCPTOT", station) == False:
                print("   Skipping station " + station + " (not enough dates yet)")
                continue
        else:
            if check_dates(start_date, delta, fcst_filepath + 'ENS/' + variable + '/fcst.t/', variable, station) == False:
                print("   Skipping station " + station + " (not enough dates yet)")
                continue        

        sql_con = sqlite3.connect(obs_filepath + variable + "/" + station + ".sqlite")
        sql_query = "SELECT * from 'All' WHERE date BETWEEN 20" +str(start_date) + " AND 20" + str(end_date)       
        obs = pd.read_sql_query(sql_query, sql_con)
        obs['datetime'] = None

        if len(period) >2:
            sql_query = "SELECT * from 'All' WHERE date BETWEEN 20" +str(fall[2]) + " AND 20" + str(fall[3])       
            obs2 = pd.read_sql_query(sql_query, sql_con)
            obs2['datetime'] = None
            obs = pd.concat(obs, obs2)

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
   
        final_obs = np.array(obs_all).T
        obs_df[station] = final_obs.flatten() 

    return(obs_df)

# returns the fcst data for the given model/grid
def get_fcst(station, filepath, variable, date_list,start_date, end_date):
    
    fcst_df = pd.DataFrame()  

    for station in all_stations:

        df_new = make_df(date_list, start_date, end_date)

        if "PCPT" in variable:
            variable = "PCPTOT"
        # pulls out a list of the files for the given station+variable+hour wanted   
        sql_con = sqlite3.connect(filepath + station + ".sqlite")
        sql_query = "SELECT * from 'All' WHERE date BETWEEN 20" + str(date_list[0]) + " AND 20" + str(date_list[len(date_list)-1])
        fcst = pd.read_sql_query(sql_query, sql_con)
        
        fcst['datetime'] = None 
        for x in range(len(fcst['Offset'])):
            fcst.loc[x, 'datetime'] = pd.to_datetime(start_date, format='%y%m%d') + timedelta(hours=int(x))
        
        fcst = fcst.set_index('datetime')
        fcst_all = df_new.join(fcst, on='datetime')
    
        final_obs = np.array(fcst_all).T
        fcst_df[station] = final_obs.flatten() 
    
    return(fcst_df)

def make_weights(fcst, obs, modelname):
    weights_all = []
    for s in range(len(all_stations)):

        for i in range(len(fcst)):
            weight = 1/(1+exp(-k*(fcst[:,s][i]-obs[:,s][i])))
            weights_all.append(weight)

    weights = mean(weights_all)
    weights = pd.DataFrame(weight, columns = modelname)
    return(weights)
        
def main(args):
    
    var_i = 0
    for var in variables: #loop through variables
        
        time_count = 0
        weights_all = pd.DataFrame()
        for i in range(len(models)):
            model = models[i] #loops through each model
       
            for grid_i in range(len(grids[i].split(","))): #loops through each grid size for each model
                
                grid = grids[i].split(",")[grid_i]
                
                if "_KF" in var:
                    file_var = var[:-3]
                else:
                    file_var = var

                #ENS only has one grid (and its not saved in a g folder)
                if model == 'ENS' and '_KF' in var:    
                    filepath = fcst_filepath + model + '/' + file_var + '/fcst.KF_MH.t/'
                    gridname = ''
                    modelname = model + gridname
                elif model == 'ENS':
                    filepath = fcst_filepath + model + '/' + file_var + '/fcst.t/'
                    gridname = ''
                    modelname = model + gridname

                elif model == "ENS_LR" and "_KF" in var:
                    filepath = fcst_filepath +model[:-3] + '/' + file_var + '/fcst.LR.KF_MH.t/'
                    gridname = ''
                    modelname = model + gridname

                elif model == "ENS_lr" and "_KF" in var:
                    filepath = fcst_filepath+model[:-3] + '/' + file_var + '/fcst.lr.KF_MH.t/'
                    gridname = ''
                    modelname = model + gridname

                elif model == "ENS_hr" and "_KF" in var:
                    filepath = fcst_filepath +model[:-3] + '/' + file_var + '/fcst.hr.KF_MH.t/'
                    gridname = ''
                    modelname = model + gridname

                elif model =="ENS_hr":
                    filepath = fcst_filepath +model[:-3] + '/' + file_var + "/fcst.hr.t/"
                    gridname = ''
                    modelname = model + gridname

                elif model =="ENS_lr":
                    filepath = fcst_filepath +model[:-3] + '/' + file_var + "/fcst.lr.t/"
                    gridname = ''
                    modelname = model + gridname

                elif model =="ENS_LR":
                    filepath = fcst_filepath +model[:-3] + '/' + file_var + "/fcst.LR.t/"
                    gridname = ''
                    modelname = model + gridname

                elif "_KF" in var:
                    filepath = fcst_filepath +model + '/' + grid + '/' + file_var + "/fcst.KF_MH/"          
                    gridname = "_" + grid
                    modelname = model + gridname

                else:
                    filepath = fcst_filepath + model + '/' + grid + '/' + file_var + '/fcst.t/'
                    gridname = "_" + grid
                    modelname = model + gridname

                
                if check_dates(start_date, delta, filepath, var, station='3510') == False:
                    print("   Skipping model " + model + gridname + " (check_dates flag)")
                    continue
            
                # if it can't find the folder for the model/grid pair 
                if not os.path.isdir(filepath):
                    raise Exception("Missing grid/model pair (or wrong base filepath for" + model + gridname)
                
                print("Now on.. " + model + gridname + " for " + var)

                for s in range(len(seasons)):
                    
                    if s == 0:
                        period = 'winter'
                        start_date = winter[0]
                        end_date = winter[1]
                    elif s ==1:
                        period = 'spring'
                        start_date = spring[0]
                        end_date = spring[1]
                    elif s ==2:
                        period = 'summer'
                        start_date = summer[0]
                        end_date = summer[1]
                    elif s == 3:
                        period = 'fall'
                        start_date = fall[0]
                        end_date = fall[1]
                
                #these returned variables are lists that contain one stat for each model (so length=#num of models)
                    
                    date_list = listofdates(start_date, end_date, obs=False)
                    date_list_obs = listofdates(start_date, end_date, obs=True)
                    
                    obs = get_all_obs(delta, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6, period, all_stations, var, start_date, end_date, date_list_obs)
                    fcst = get_fcst(filepath, var, date_list, start_date, end_date)
            
                    weights= make_weights(fcst, obs,modelname)
                    weights_all = pd.concat([weights_all, weights], axis =1)
                    weights_all.to_csv(save_folder+str(k) + '/' + stat_type + '/weights_all_'+time_domain+'_'+var+'_'+period)
            
            time_count = time_count+1
            


        var_i=var_i+1
            
    #sys.stdout.close() #close log file

if __name__ == "__main__":
    main(sys.argv)

