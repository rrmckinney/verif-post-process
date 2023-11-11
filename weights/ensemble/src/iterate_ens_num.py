#!/usr/bin python

"""
Created in 2023 by Reagan McKinney

Input: start date (YYMMDD), end date (YYMMDD), variable, domain size
    Start and end date must be a year stretch (365 days)
    variable options: SFCTC_KF, SFCTC, PCPTOT, PCPT6, SFCWSPD_KF, SFCWSPD
    domain options: small *weights have only been calculated for the small domain
    weight type: seasonal or yearly
    
This code is used create ensembles using 1-51 members based on ranks. This will test the sensitivity of the
ensemble to a number of models. 

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
from funcs import *
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

#output folder for sql tables after weighted ensemble is made
save_folder = '/home/verif/verif-post-process/weights/ensemble/output_ens_num/'

###########################################################
### -------------------- INPUT ----------------------------
###########################################################

# takes an input date for the first and last day you want calculations for, must be a range of 7 or 30 days apart
if len(sys.argv) == 6:
    date_entry1 = sys.argv[1]    #input date YYMMDD
    start_date = str(date_entry1) 
    input_startdate = datetime.strptime(start_date, "%y%m%d%H")
    
    date_entry2 = sys.argv[2]    #input date YYMMDD
    end_date = str(date_entry2)
    input_enddate = datetime.strptime(end_date, "%y%m%d%H")
    
    delta = (input_enddate-input_startdate).total_seconds()/(60*60)
    print(delta)
    if delta == 60: # 6 is weekly bc it includes the start and end date (making 7)
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

    stat_type = sys.argv[5]

else:
    raise Exception("Invalid input entries. Needs 2 YYMMDD entries for start and end dates, a variable name, domain size, weight type, k, and time domain")

time_domain = '60hr'

# list of model names as strings (names as they are saved in www_oper and my output folders)
models = np.loadtxt(models_file,usecols=0,dtype='str')
grids = np.loadtxt(models_file,usecols=1,dtype='str') #list of grid sizings (g1, g2, g3 etc) for each model
gridres = np.loadtxt(models_file,usecols=2,dtype='str') #list of grid resolution in km for each model
hours = np.loadtxt(models_file,usecols=3,dtype='str') #list of max hours for each model

station_df = pd.read_csv(station_file)

#stations_with_SFCTC = np.array(station_df.query("SFCTC==1")["Station ID"],dtype=str)
#stations_with_SFCWSPD = np.array(station_df.query("SFCWSPD==1")["Station ID"],dtype=str)
#stations_with_PCPTOT = np.array(station_df.query("PCPTOT==1")["Station ID"],dtype=str)
#stations_with_PCPT6 = np.array(station_df.query("PCPT6==1")["Station ID"],dtype=str)

#all_stations = np.array(station_df.query("`Small domain`==1")["Station ID"],dtype=str)

model_list = ['WRFRDPS_g3','WRF4NAM_g4', 'WRF4NAM_g3','WRF4NAM_g2','WRF3GFSgc01_g2', 'WRF3ARPEGE_g2', 'WRF3ARPEGE_g3','WRF3NAM_g4', \
              'MM5_g3', 'MPAS25_g2', 'WRF3NAM_g3', 'MM5_g4', 'MM5_g2', 'MPAS25_g1', 'WRF3GEM_g2', 'WRF2GFS81_g3', 'WRF3NAVGEM_g3', \
              'WRF3NAM_g2', 'WRF2GFS81_g2', 'WRF2NAM81_g3', 'WRF2NAM81_g2', 'WRF3NAVGEM_g2', 'WRF3GFS_g2', 'MM5G_g2', 'NMM3GFS_g2', \
              'WRF2GFS_g2', 'WRF2GFS81_g1', 'WRF2NAM_g2', 'NMM3NAM_g4', 'NMM3NAM_g2', 'WRF2GFS_g1', 'WRF2NAM81_g1', 'WRF2GFS_g3', \
              'WRF4RDPS_g4', 'WRF2NAM_g3', 'NMM3GFS_g3', 'WRF4ICON_g2', 'MM5G_g3', 'WRF2NAM_g1', 'NMM3NAM_g3', 'WRF3NAVGEM_g4', \
              'MM5G_g5', 'MM5G_g5', 'WRF3GFSgc01_g3', 'WRF3GEM_g3', 'WRF3GFS_g3', 'WRF4ICON_g3', 'WRF4RDPS_g5','WRF3GEM_g4', \
              'WRF3GFS_g4', 'WRF3GFS_g5']
##########################################################
###-------------------- FOR TESTING ---------------------
##########################################################
stations_with_SFCTC = ['3510']
stations_with_SFCWSPD = ['3510']
stations_with_PCPTOT = ['3510']
stations_with_PCPT6 = ['3510']

all_stations = ['3510']

#models = ['MM5']
#grids = grids = np.loadtxt(models_file,usecols=1,dtype='str',max_rows = 2) 
#gridres = gridres = np.loadtxt(models_file,usecols=2,dtype='str',max_rows = 2)
#hours = hours = np.loadtxt(models_file,usecols=3,dtype='str', max_rows = 2)

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

        if len(station) < 4:
            station = "0" + str(station)

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

                fcst, model_df_name = fcst_grab(station_df, savetype,  stat_type, filepath, delta, input_domain,  \
                    date_entry1, date_entry2, input_variable, date_list, model, grid, maxhour, gridname, filehours, \
                    obs_df, station)
                    
        
                fcst_all = fcst_all.merge(fcst, on='datetime',how='left')
        #path = '/home/verif/verif-post-process/weights/ensemble/src/'
        #fcst_all.to_csv(path+fcst_all+'.csv', mode = 'w')
        #print(fcst_all)
        
        #Combine Weighted ensemble and obs
        for i in range(len(model_list)):
            names = model_list[:i]
            ENS = fcst_all[names]
        
            ENS_num = ENS.mean(axis=1)
            ENS_num = ENS_num.to_frame() 
            df = ENS_num.join(obs_df)
            
            #create regular ensemble and at it to dataframe with other (also need to drop nans for calcs)
            #fcst_all.drop(['WRF3GEM_g3','WRF3GFS_g3', 'WRF4RDPS_g4','WRF3GFS_g3','WRF4ICON_g3','WRF4RDPS_g5','WRF3GEM_g4','WRF3GFS_g4','WRF3GFS_g5'], axis='columns',inplace = True)
            ENS_M = fcst_all.mean(axis=1)
            ENS_M = ENS_M.to_frame()
            df = df.join(ENS_M)
            df.columns = ['ENS_num','Obs','ENS_M']
            df = df.dropna()
            print(df)
            
            print(stats.ttest_ind(df.ENS_num, df.ENS_M))

            #stats for weighted ensemble
            ENS_num_spcorr = stats.spearmanr(df.ENS_num, df.Obs, nan_policy='omit')
            ENS_num_MAE = mean_absolute_error(df.Obs, df.ENS_num)
            ENS_num_RMSE = mean_squared_error(df.Obs, df.ENS_num, squared=False)
            #ENS_num.to_csv(path+station+input_variable+'.csv') 
            

            #stats for standard ensemble
            ENS_M_spcorr = stats.spearmanr(df.ENS_M, df.Obs, nan_policy='omit')
            ENS_M_MAE = mean_absolute_error(df.Obs, df.ENS_M)
            ENS_M_RMSE = mean_squared_error(df.Obs, df.ENS_M, squared=False)
            #ENS_num.to_csv(path+station+input_variable+'.csv') 
        
            #write stats to textfiles
            mae_f = open('MAE_'+input_variable+'_'+str(i)+'_num_.txt','a')
            mae_f.write(str(date_entry1) + " " + str(date_entry2) + "   ")
            mae_f.write("%3.3f  " % (ENS_num_MAE))
            mae_f.write("%3.3f  " % (ENS_M_MAE) + "\n")
            mae_f.close()

            rmse_f = open('RMSE_'+input_variable+'_'+str(i)+'_num_.txt','a')
            rmse_f.write(str(date_entry1) + " " + str(date_entry2) + "   ")
            rmse_f.write("%3.3f  " % (ENS_num_RMSE))
            rmse_f.write("%3.3f  " % (ENS_M_RMSE) + "\n")
            rmse_f.close()

            spcorr_f = open('spcorr_'+input_variable+'_'+str(i)+'_num_.txt','a')
            spcorr_f.write(str(date_entry1) + " " + str(date_entry2) + "   ")
            spcorr_f.write("%3.3f  " % (ENS_num_spcorr.statistic))
            spcorr_f.write("%3.3f  " % (ENS_num_spcorr.pvalue))
            spcorr_f.write("%3.3f  " % (ENS_M_spcorr.statistic))
            spcorr_f.write("%3.3f  " % (ENS_M_spcorr.pvalue) + "\n")
            spcorr_f.close()

            fig, axs = plt.subplots(2, figsize=(50,10))
            
            axs[0].plot(df.ENS_num, 'ko')
            
            axs[0].plot(fcst_all)
            axs[1].plot(df.ENS_num, 'ko')
            axs[1].plot(df.ENS_M, 'bo')
            axs[1].plot(df.Obs,'ro')

            plt.savefig('all_ens_'+input_variable+'_'+str(i)+'_num_'+station)
            
            elapsed = time.time() - t #closes log file
        
            
            #print(elapsed)
            print("It took " + str(round(elapsed/60)) + " minutes to run")

if __name__ == "__main__":
    main(sys.argv)
