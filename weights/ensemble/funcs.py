#!/usr/bin python

"""
Created in 2023 adapted from code by Eva Gnegy (2021)
@author: Reagan McKinney

These are the functions that feed into the mk_weighted_ensemble.py file. This script holds all the functions
that create the weigted ensemble and then estblish stats to compare it to our current ensemble performance. 

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

#folder where the stats save
textfile_folder = '/verification/weighted-Statistics/'

#folder where the weights are located
weights_folder = '/home/verif/verif-post-process/weights/LF/output/'

###########################################################
### -------------------- INPUTS -- ------------------------
###########################################################

# thresholds for discluding erroneous data 
precip_threshold = 250 #recorded at Buffalo Gap 1961 https://www.canada.ca/en/environment-climate-change/services/water-overview/quantity/floods/events-prairie-provinces.html
wind_threshold = 400 #recorded Edmonton, AB 1987 http://wayback.archive-it.org/7084/20170925152846/https://www.ec.gc.ca/meteo-weather/default.asp?lang=En&n=6A4A3AC5-1#tab5
temp_min = -63 #recorded in Snag, YT 1947 http://wayback.archive-it.org/7084/20170925152846/https://www.ec.gc.ca/meteo-weather/default.asp?lang=En&n=6A4A3AC5-1#tab5
temp_max = 49.6 #recorded in Lytton, BC 2021 https://www.canada.ca/en/environment-climate-change/services/top-ten-weather-stories/2021.html#toc2

#the 6 categorical scores; do not need tailing '_'
stats_cat = ['POD', 'POFD', 'PSS', 'HSS', 'CSI', 'GSS']

# seasons are set as Meteorological Seasons; fall has two sets as data starts in oct so sept data is a year older
winter = ['211201','220228']
spring = ['220301','220531']
summer = ['220601','220831']
fall = ['211001','211130', '220901','220930']
seasons_dates = [winter,spring,summer,fall]
seasons = ['winter', 'spring', 'summer', 'fall']

# logistic curve steepness (stated in file names)
k = '100'

# weight outlook: the forecast outlook the weights are based upon, 60hr is the only outlook that has all 51 members
weight_outlook = '60hr'

#editting mode for textfile
wm = 'a'

###########################################################
### -------------------- FUNCTIONS ------------------------
###########################################################


# makes a list of the dates you want from start to end, used to make sure the models and obs have the right dates
# obs get their own list because it will be different days than the initializition dates from the models for anything
#   past hours 0-24
def listofdates(start_date, end_date, obs = False):
    if obs == False:
        start = datetime.strptime(start_date, "%y%m%d").date()
        end = datetime.strptime(end_date, "%y%m%d").date()

    elif obs == True:
        startday = 0 #forhour 1
        endday = 7 #for hour 180
        
        start = datetime.strptime(start_date, "%y%m%d").date() + timedelta(days=startday)
        end = datetime.strptime(end_date, "%y%m%d").date() + timedelta(days=endday)
    
    numdays = (end-start).days 
    date_list = [(start + timedelta(days=x)).strftime("%y%m%d") for x in range(numdays+1)]

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
    elif int("20" + start_date) < int(sql_result[0]):
        print("    Model collection started " + str(sql_result[0]) + ", which is after input start_date")
        flag = False
    cursor.close()
    
    return(flag)

# makes a dataframe with all hours and dates to compare to actual data; allows us to add in nans where needed
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
    df_new.drop(['date','time'], axis='columns',inplace=True)
    return(df_new)

def get_all_obs(delta, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6, all_stations, variable, start_date, end_date, date_list_obs):
    
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

        final_obs = np.array(obs_all).T #84 x 7   (30) 

        obs_df[station] = final_obs.flatten()
    
    return(obs_df)

# returns the fcst data for the given model/grid
def get_fcst(stat_type, k,maxhour, station, filepath, variable, date_list, filehours, start_date, end_date, weight_type, model_df_name):
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
    df_all = df_new.join(fcst, on='datetime')
    df_all.drop(['Date','Offset'], axis='columns',inplace = True)
    df_all.columns = [ model_df_name]
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

def make_textfile(model, grid, input_domain, savetype, date_entry1, date_entry2, time_domain, variable, filepath, MAE, RMSE, corr, len_fcst, numstations):
   
    if "ENS" in model:
        modelpath= model + '/'
    else:
        modelpath = model + '/' + grid + '/'
    f1 = open(textfile_folder + modelpath + input_domain + '/' + variable + '/' + "MAE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",wm+"+")       
    read_f1 = np.loadtxt(textfile_folder +  modelpath + input_domain + '/' + variable + '/' + "MAE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",dtype=str)  
    if date_entry1 not in read_f1 and date_entry2 not in read_f1:
        f1.write(str(date_entry1) + " " + str(date_entry2) + "   ")
        
        f1.write("%3.3f   " % (MAE))
        f1.write(len_fcst + "   ")
        f1.write(numstations + "\n")
    
        f1.close()    
            
    
    f2 = open(textfile_folder +  modelpath + input_domain + '/' + variable + '/' + "RMSE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",wm+"+")       
    read_f2 = np.loadtxt(textfile_folder +  modelpath  + input_domain + '/' + variable + '/' + "RMSE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",dtype=str)  
    if date_entry1 not in read_f2 and date_entry2 not in read_f2:
        f2.write(str(date_entry1) + " " + str(date_entry2) + "   ")
        
        f2.write("%3.3f   " % (RMSE))
        f2.write(len_fcst + "   ")
        f2.write(numstations + "\n")
        
        f2.close()  
    
    
    f3 = open(textfile_folder +  modelpath + input_domain + '/' + variable + '/' + "spcorr_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",wm+"+") 
    read_f3 = np.loadtxt(textfile_folder +  modelpath + input_domain + '/' + variable + '/' + "spcorr_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",dtype=str)  
    if date_entry1 not in read_f3 and date_entry2 not in read_f3:
        f3.write(str(date_entry1) + " " + str(date_entry2) + "   ")
        
        f3.write("%3.3f   " % (corr))
        f3.write(len_fcst + "   ")
        f3.write(numstations + "\n")
        
        f3.close()  


def mk_ensemble(weight_type, stat_type, model_df_name, start_date, end_date, df_all, variable):
    
    start_date = datetime.strptime(start_date, '%y%m%d')
    end_date = datetime.strptime(end_date, '%y%m%d')

    if weight_type == 'seasonal':
        if stat_type == 'CAT_' and variable not in ['SFCTC', 'SFCTC_KF']:
            for s in range(len(stats_cat)):
                for w in range(len(seasons_dates)):
                
                    f = weights_folder + "weights-seasonal/" + k + '/' + stat_type + '/weights_' \
                        + stats_cat[s] + '_' + weight_outlook + '_' + variable + '_' + seasons[w]
                    weight_file = pd.read_csv(f, sep = "\s+|,", usecols=[model_df_name])
                    weight = float(weight_file.iloc[:,0])
                    print(weight)

                    if len(seasons_dates[w]) == 2:
                        date1 = datetime.strptime(seasons_dates[w][0], '%y%m%d')
                        date2 = datetime.strptime(seasons_dates[w][1], '%y%m%d')
                        
                        df3 = df_all[(df_all.index >= date1) & (df_all.index < date2)]
                        df3 = df3*weight

                    elif len(seasons_dates[w]) > 2:
                        date1 = datetime.strptime(seasons_dates[w][0], '%y%m%d')
                        date2 = datetime.strptime(seasons_dates[w][1], '%y%m%d')
                        date3 = datetime.strptime(seasons_dates[w][2], '%y%m%d')
                        date4 = datetime.strptime(seasons_dates[w][3], '%y%m%d')
                        
                        df = df_all[(df_all.index >= date1) & (df_all.index < date2)]
                        df2 = df_all[(df_all.index >= date3) & (df_all.index < date4)]
                        df3 = pd.merge(df, df2)
                        df3 = df3*weight
        else:
            for w in range(len(seasons_dates)):
                    f = weights_folder + "weights-seasonal/" + k + '/' + stat_type + '/weights_all' \
                        + '_' + weight_outlook + '_' + variable + '_' + seasons[w]
                    
                    weight_file = pd.read_csv(f, sep = "\s+|,", usecols=[model_df_name])
                    weight = float(weight_file.iloc[:,0])
                    print(weight)

                    if len(seasons_dates[w]) == 2:
                        date1 = datetime.strptime(seasons_dates[w][0], '%y%m%d')
                        date2 = datetime.strptime(seasons_dates[w][1], '%y%m%d')
                        
                        df3 = df_all[(df_all.index >= date1) & (df_all.index < date2)]
                        df3 = df3*weight

                    #fall has four dates as september is a year later than oct/nov as stats started in oct
                    elif len(seasons_dates[w]) > 2:
                        date1 = datetime.strptime(seasons_dates[w][0], '%y%m%d')
                        date2 = datetime.strptime(seasons_dates[w][1], '%y%m%d')
                        date3 = datetime.strptime(seasons_dates[w][2], '%y%m%d')
                        date4 = datetime.strptime(seasons_dates[w][3], '%y%m%d')
                        
                        df = df_all[(df_all.index >= date1) & (df_all.index < date2)]
                        df2 = df_all[(df_all.index >= date3) & (df_all.index < date4)]
                        df3 = pd.merge(df, df2)
                        df3 = df3*weight

    elif weight_type == 'yearly':
        if stat_type == 'CAT_' and variable not in ['SFCTC', 'SFCTC_KF']:
            for s in range(len(stats_cat)):
                f = weights_folder + "weights-yearly/" + k + '/' + stat_type + '/weights_' \
                    + stats_cat[s] + '_' + weight_outlook + '_' + variable
                weight_file = pd.read_csv(f, sep = "\s+|,", usecols=[model_df_name])
                weight = float(weight_file.iloc[:,0])
                print(weight)

                df3 = df_all[(df_all.index >= start_date) & (df_all.index < end_date)]
                df3 = df3*weight
                
        else:
                f = weights_folder + "weights-yearly/" + k + '/' + stat_type + '/weights_all' \
                    + '_' + weight_outlook + '_' + variable 
                    
                weight_file = pd.read_csv(f, sep = "\s+|,", usecols=[model_df_name])
                weight = float(weight_file.iloc[:,0])
                print(weight)

                df3 = df_all[(df_all.index >= start_date) & (df_all.index < end_date)]
                df3 = df3*weight
    return(df3)
    

def get_statistics(delta, model,grid, input_domain, savetype, date_entry1, date_entry2, maxhour,hour,length,\
        fcst_allstations,obs_allstations,num_stations,totalstations,time_domain,variable,filepath):
    
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
            model_not_available(model, grid, delta, input_domain, date_entry1, date_entry2, savetype, maxhour,hour,\
            length,totalstations,time_domain,variable,filepath)
        
        else:
            MAE = mean_absolute_error(obs_rounded,fcst_rounded)
            MSE = mean_squared_error(obs_rounded,fcst_rounded)
            RMSE = math.sqrt(MSE)
            corr = stats.spearmanr(obs_rounded,fcst_rounded)[0]
            
            if variable == "PCPT6":
                length = int(length/6)

            else:
                length = length            
            
            len_fcst = str(len(fcst_noNaNs)) + "/" + str(length)   
            numstations = str(num_stations) + "/" + str(totalstations)
                
            make_textfile(model, grid, input_domain, savetype, date_entry1, date_entry2, time_domain, variable, \
                          filepath, MAE, RMSE, corr, len_fcst, numstations)

def model_not_available(model, grid, delta, input_domain, date_entry1, date_entry2, savetype,\
            maxhour,hour,length,totalstations,time_domain,variable,filepath):
    
    if "ENS" in model:
        modelpath = model + '/'
    else:
        modelpath = model + '/' + grid + '/'

    if int(maxhour) >= hour:  
        if variable == "PCPT6":
            if int(maxhour) == int(hour):
                total_length = int(((length*(delta+1))/6)-(delta+1))
            else:
                total_length = int((length*(delta+1))/6)

        else:
            total_length = int(length*(delta+1))
                
        len_fcst = "0/" + str(total_length)
        numstations = "0/" + str(totalstations)
        
        f1 = open(textfile_folder +  modelpath  + input_domain + '/' + variable + '/' + "MAE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",wm+"+")       
        read_f1 = np.loadtxt(textfile_folder +  modelpath  + input_domain + '/' + variable + '/' + "MAE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",dtype=str)  
        if date_entry1 not in read_f1 and date_entry2 not in read_f1:
            f1.write(str(date_entry1) + " " + str(date_entry2) + "   ")
            
            f1.write("nan   ") #MAE
            f1.write(len_fcst + "   ")
            f1.write(numstations + "\n")
        
            f1.close()    
                
        
        f2 = open(textfile_folder +  modelpath  + input_domain + '/' + variable + '/' + "RMSE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",wm+"+")       
        read_f2 = np.loadtxt(textfile_folder +  modelpath  + input_domain + '/' + variable + '/' + "RMSE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",dtype=str)  
        if date_entry1 not in read_f2 and date_entry2 not in read_f2:
            f2.write(str(date_entry1) + " " + str(date_entry2) + "   ")
            
            f2.write("nan   ") #RMSE
            f2.write(len_fcst + "   ")
            f2.write(numstations + "\n")
            
            f2.close()  
        
        f3 = open(textfile_folder +  modelpath  + input_domain + '/' + variable + '/' + "spcorr_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",wm+"+") 
        read_f3 = np.loadtxt(textfile_folder +  modelpath  + input_domain + '/' + variable + '/' + "spcorr_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt",dtype=str)  
        if date_entry1 not in read_f3 and date_entry2 not in read_f3:
            f3.write(str(date_entry1) + " " + str(date_entry2) + "   ")
            
            f3.write("nan   ") #corr
            f3.write(len_fcst + "   ")
            f3.write(numstations + "\n")
            
            f3.close()  

def fcst_grab(savetype, stat_type, k, weight_type, filepath, delta, input_domain, date_entry1, date_entry2, \
              all_stations, station_df, variable, date_list, model, grid, maxhour, gridname, filehours, \
                obs_df, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6):
    
    if os.path.isdir(textfile_folder +  filepath) == False:
        os.makedirs(textfile_folder +  filepath)
            
    # open the file for the current model and get all the stations from it
    model_df_name = model+gridname
    stations_in_domain = np.array(station_df.query(model_df_name+"==1")["Station ID"],dtype='str')

    totalstations = 0
    num_stations = 0
    
    for station in stations_in_domain:

        if station not in all_stations:
            #print("   Skipping station " + station + ")
            continue

        if check_variable(variable, station, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6) == False:                  
            #print("   Skipping station " + station + " (no " + variable + " data)")
            continue
        
        if len(station) < 4:
            station = "0" + str(station)
        
        if check_dates(date_entry1, delta, filepath, variable, station) == False:
            print("   Skipping station " + station + " (not enough dates yet)")
            continue

        
        # total stations that should be included in each model/grid
        totalstations = totalstations+1
            
        all_fcst = get_fcst(stat_type,k,maxhour, station, filepath, variable, date_list,filehours, date_entry1, date_entry2, weight_type, model_df_name)    #goes to maxhour       

        
        #checks 180 hour only
        #if pd.isna(all_fcst).all() == True:    
        #    print("   Skipping station " + station + " (No forecast data)")
        #    continue
        
        #if pd.isna(obs_df).all() == True:    
        #   print("   Skipping station " + station + " (No obs data)")
        #    continue
        
        # total stations that ended up being included (doesn't count ones with no data)
        num_stations = num_stations+1

    #sometimes theres no forecast data for a model
    if num_stations == 0:
        print("   NO FORECAST DATA FOR " + model + grid) 

    else:
        return(all_fcst, model_df_name)

def PCPT_obs_df_6(date_list_obs, delta, input_variable, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6,\
                    all_stations, start_date, end_date):

    # get the hourly precip values
    obs_df_1 = get_all_obs(delta, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6, \
        all_stations, "PCPTOT", start_date, end_date, date_list_obs)
    
    # grab the extra hour on the last outlook day
    obs_df_1 = obs_df_1.append(obs_df_1.iloc[60],ignore_index=True)
 
    
    # remove the first hour (0 UTC)
    obs_df_1 = obs_df_1.iloc[1:].reset_index(drop=True)

    # sum every 6 hours (1-6 UTC, 7-12 UTC etc). report NaN if any of the 6 hours is missing
    obs_df_1_trimmed = obs_df_1.groupby(obs_df_1.index // 6).apply(pd.DataFrame.sum,skipna=False)

    #grab the 6-hr accum precip values
    obs_df_6 = get_all_obs(delta, stations_with_SFCTC, stations_with_SFCWSPD, stations_with_PCPTOT, stations_with_PCPT6, \
        all_stations, "PCPT6", start_date, end_date, date_list_obs)
        
    # grab the extra hour on the last outlook day
    obs_df_6 = obs_df_6.append(obs_df_6.iloc[60],ignore_index=True)

    # remove all values except the ones every 6 hours (6 UTC, 12 UTC, etc. (skipping the first))
    obs_df_6_trimmed = obs_df_6.iloc[::6, :][1:].reset_index(drop=True) #grabs every 6 hours (skipping hour 0)

    #combine the obs from manually accumulating 6 hours from hourly, and the pre-calculated 6 hours
    obs_df = pd.concat([obs_df_1_trimmed, obs_df_6_trimmed],axis=1)


    return(obs_df)
