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
import sys
from math import exp
import warnings
warnings.filterwarnings("ignore",category=RuntimeWarning)
###########################################################
### -------------------- FILEPATHS ------------------------
###########################################################

#location to save the images internally
save_folder = "/home/verif/verif-post-process/weights/LF/output/weights-yearly/"

#description file for stations
station_file = '/home/verif/verif-post-process/input/station_list.txt'

#description file for models
models_file = '/home/verif/verif-post-process/input/model_list_weights.txt'

textfile_folder = '/verification/Statistics/'

###########################################################
### -------------------- INPUT ------------------------
###########################################################

# takes an input date for the last day of the week you want to include
if len(sys.argv) == 6:
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
         
else:
    raise Exception("Invalid input entries. Needs YYMMDD for start and end dates")



time_domains = ['60hr','84hr','120hr','180hr','day1','day2','day3','day4','day5','day6','day7']

time_labels = ['outlook hours 1-60','outlook hours 1-84','outlook hours 1-120','outlook hours 1-180',
               'day 1 outlook (hours 1-24)','day 2 outlook (hours 25-48)','day 3 outlook (hours 49-72)',
               'day 4 outlook (hours 73-96)','day 5 outlook (hours 97-120)','day 6 outlook (hours 121-144)',
               'day 7 outlook (hours 145-168)']

#stations = np.loadtxt(station_file,usecols=0,delimiter=',',dtype='str')

variables = ['SFCTC', 'SFCTC_KF']
variable_names = ['Temperature-Raw', 'Temperature-KF']
variable_units = ['[C]','[C]']

# list of model names as strings (names as they are saved in www_oper and my output folders)
models = np.loadtxt(models_file,usecols=0,dtype='str')

grids = np.loadtxt(models_file,usecols=1,dtype='str') #list of grid sizings (g1, g2, g3 etc) for each model
gridres = np.loadtxt(models_file,usecols=2,dtype='str') #list of grid resolution in km for each model
model_names = np.loadtxt(models_file,usecols=4,dtype='str') #longer names, used for legend

# this loop makes the names for each model/grid pair that will go in the legend
legend_labels = []
for i in range(len(model_names)):
    for grid in gridres[i].split(","):
        model = model_names[i]

        if "_" in model: #only for ENS models, which don't have grid res options
            legend_labels.append(model.replace("_"," "))
        else:
            legend_labels.append(model + grid)


#colors to plot, must be same length (or longer) than models list
model_colors = ['C0','C1','C2','C3','C4','C5','C6','C7','C8','C9','#ffc219','#CDB7F6','#65fe08','#fc3232','#754200','#00FFFF','#fc23ba','#a1a1a1','#000000','#000000','#000000','#000000']

# The stat you want to base your weights off of:
#choose "MAE_", "RMSE_" or "SPCORR_"
stat_type = sys.argv[5]
# weighting curve steepness, now user input, testing several values
k = int(sys.argv[4])

print(k)
###########################################################
### -------------------- FUNCTIONS ------------------------
###########################################################

def get_rankings(variable,time_domain):
    
     MAE_list, RMSE_list, SPCORR_list, modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations = [],[],[],[],[],[],[],[]
     
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
                     
            print("Now on.. " + model + gridname + "   " + variable + " " + str(k))
            if os.path.isfile(textfile_folder +  modelpath  + input_domain + '/' + variable + '/' + stat_type + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt"):
                #open the CAT file
                with open(textfile_folder +  modelpath  + input_domain + '/' + variable + '/' + stat_type + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt") as f:
                    lines = f.readlines()
                
                if stat_type == "MAE_":
                    MAE_mean = []
                    for line in lines:
                        if date_entry1 <= line.split("   ")[0][0:6] and date_entry2 not in line:
                            MAE = line.split("   ")[1]
                            dataratio = line.split("   ")[2]
                            numstations = line.split("   ")[3].strip()

                            MAE_mean.append(float(MAE))
                    MAE = np.nanmean(MAE_mean)
                
                elif stat_type == "RMSE_":
                    RMSE_mean = []
                    for line in lines:
                        if date_entry1 <= line.split("   ")[0][0:6] and date_entry2 not in line:
                            RMSE = line.split("   ")[1]
                            dataratio = line.split("   ")[2]
                            numstations = line.split("   ")[3].strip()

                            RMSE_mean.append(float(RMSE))
                    RMSE = np.nanmean(RMSE_mean)
                
                elif stat_type == "spcorr_":
                    SPCORR_mean = []
                    for line in lines:
                        if date_entry1 <= line.split("   ")[0][0:6] and date_entry2 not in line:
                            SPCORR = line.split("   ")[1]
                            dataratio = line.split("   ")[2]
                            numstations = line.split("   ")[3].strip()

                            SPCORR_mean.append(float(SPCORR))
                    SPCORR = np.nanmean(SPCORR_mean)
                
                else:
                    print("   **Skipping " + model + grid + ", no data yet**")
                    skipped_modelnames.append(legend_labels[leg_count] + ":  (none)")
                    leg_count = leg_count+1
                    continue
                    
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
                
                if stat_type == "MAE_":
                    MAE_list.append(float(MAE))
                
                elif stat_type == "RMSE_":
                    RMSE_list.append(float(RMSE))
                
                elif stat_type == "spcorr_":
                    SPCORR_list.append(float(SPCORR))

                if int(dataratio.split("/")[0]) < int(dataratio.split("/")[1])-removed_hours*(delta+1):
                    if int(numstations.split("/")[0]) != int(numstations.split("/")[1]): 
                        modelnames.append(model + gridname)
                    else:
                        modelnames.append(model + gridname)
              
                else:
                    if int(numstations.split("/")[0]) != int(numstations.split("/")[1]): 
                        modelnames.append(model+gridname)
                    else:
                        modelnames.append(model+gridname)
                   

            leg_count = leg_count+1
         
        color_count = color_count+1
             
     return(MAE_list, RMSE_list, SPCORR_list, modelnames)
 
def get_obs_dates(time_domain):
    
    def obs_days(add_start,add_end):
        obs_startdate = input_startdate + datetime.timedelta(days=add_start)
        obs_enddate = input_enddate + datetime.timedelta(days=add_end)       
        start = datetime.datetime.strftime(obs_startdate,"%b. %d, %Y")
        end = datetime.datetime.strftime(obs_enddate,"%b. %d, %Y")
        
        return(start + ' to ' + end)

    if time_domain == '60hr':
        obs_dates = obs_days(0,3)      
    elif time_domain == '84hr':
        obs_dates = obs_days(0,4)
    elif time_domain == '120hr':
        obs_dates = obs_days(0,5)       
    elif time_domain == '180hr':
        obs_dates = obs_days(0,8)      
    elif time_domain == 'day1':
        obs_dates = obs_days(0,0)
    elif time_domain == 'day2':
        obs_dates = obs_days(1,1)
    elif time_domain == 'day3':
        obs_dates = obs_days(2,2)
    elif time_domain == 'day4':
        obs_dates = obs_days(3,3)
    elif time_domain == 'day5':
        obs_dates = obs_days(4,4)
    elif time_domain == 'day6':
        obs_dates = obs_days(5,5)
    elif time_domain == 'day7':
        obs_dates = obs_days(6,6)        
    
    return(obs_dates)

def make_weights(MAE, RMSE, SPCORR, modelnames):

    if stat_type == "MAE_":
        
        MAE_weights = []
        MAE_sorted, modelnames_sortedMAE = zip(*sorted(zip(MAE, modelnames)))
        
        MAE_xo = np.mean(MAE_sorted)
        for i in range(len(MAE_sorted)):
            MAE_weight = 1/(1+exp(-k*(MAE_sorted[i]-MAE_xo)))
            MAE_weights.append(MAE_weight)        
        
        MAE_weights = [i/sum(MAE_weights) for i in MAE_weights]
        return(MAE_weights, modelnames_sortedMAE)

    elif stat_type == "RMSE_":
    
        RMSE_weights = []
        RMSE_sorted, modelnames_sortedRMSE = zip(*sorted(zip(RMSE, modelnames)))
        
        RMSE_xo = np.mean(RMSE_sorted)
        for i in range(len(RMSE_sorted)):
            RMSE_weight = 1/(1+exp(-k*(RMSE_sorted[i]-RMSE_xo)))
            RMSE_weights.append(RMSE_weight)

        RMSE_weights = [i/sum(RMSE_weights) for i in RMSE_weights]
        return(RMSE_weights, modelnames_sortedRMSE)

    elif stat_type == "spcorr_":
    
        SPCORR_weights = []
        SPCORR_sorted, modelnames_sortedSPCORR = zip(*sorted(zip(SPCORR, modelnames)))
        
        SPCORR_xo = np.mean(SPCORR_sorted)
        for i in range(len(SPCORR_sorted)):
            SPCORR_weight = 1/(1+exp(-k*(SPCORR_sorted[i]-SPCORR_xo)))
            SPCORR_weights.append(SPCORR_weight)

        SPCORR_weights = [i/sum(SPCORR_weights) for i in SPCORR_weights]
        return(SPCORR_weights, modelnames_sortedSPCORR)
        
def main(args):
   
    var_i = 0
    for var in variables: #loop through variables
        
        time_count = 0
        for time_domain in time_domains:
                        
            #these returned variables are lists that contain one stat for each model (so length=#num of models)
            MAE, RMSE, SPCORR, modelnames = get_rankings(var,time_domain)
           
            if stat_type == "MAE_":
                MAE_weight, modelnames_sortedMAE = make_weights(MAE, RMSE, SPCORR, modelnames)
                weights_all = pd.DataFrame([MAE_weight], columns = modelnames_sortedMAE)
                weights_all.to_csv(save_folder +str(k) + '/' + stat_type + '/weights_all_'+time_domain+'_'+var)

            elif stat_type == "RMSE_":
                RMSE_weight, modelnames_sortedRMSE = make_weights(MAE, RMSE, SPCORR, modelnames)
                weights_all = pd.DataFrame([RMSE_weight], columns = modelnames_sortedRMSE)
                weights_all.to_csv(save_folder +str(k) + '/' + stat_type + '/weights_all_'+time_domain+'_'+var)
            
            elif stat_type == "spcorr_":
                SPCORR_weight, modelnames_sortedSPCORR = make_weights(MAE, RMSE, SPCORR, modelnames)
                weights_all = pd.DataFrame([SPCORR_weight], columns = modelnames_sortedSPCORR)
                weights_all.to_csv(save_folder+str(k) + '/' + stat_type + '/weights_all_'+time_domain+'_'+var)
            
            time_count = time_count+1
            

        var_i=var_i+1
            
    #sys.stdout.close() #close log file

if __name__ == "__main__":
    main(sys.argv)

