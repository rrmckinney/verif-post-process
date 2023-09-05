#!/usr/bin python

"""
Created in summer 2023

@author: Reagan McKinney

This script is based on section 4 of https://journals.ametsoc.org/view/journals/wefo/23/6/2008waf2007078_1.xml 
"""

import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import datetime #import datetime, timedelta
import sys
from sklearn import preprocessing
from math import exp
import warnings
warnings.filterwarnings("ignore",category=RuntimeWarning)
###########################################################
### -------------------- FILEPATHS ------------------------
###########################################################


#path to save the log/output
#logfilepath = "/home/egnegy/python_plotting/log/plot_leaderboards.log"

#location to save the images for the website
#save_folder = '/www/results/verification/images/leaderboards/'

#location to save the images internally
save_folder = "/home/verif/verif-post-process/weights/LF/weights-seasonal/"

#description file for stations
station_file = '/home/verif/verif-post-process/input/station_list.txt'

#description file for models
models_file = '/home/verif/verif-post-process/input/model_list_weights.txt'

textfile_folder = '/verification/Statistics/'

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
         
else:
    raise Exception("Invalid input entries. Needs YYMMDD for start and end dates")



time_domains = ['60hr','84hr','120hr','180hr','day1','day2','day3','day4','day5','day6','day7']

time_labels = ['outlook hours 1-60','outlook hours 1-84','outlook hours 1-120','outlook hours 1-180',
               'day 1 outlook (hours 1-24)','day 2 outlook (hours 25-48)','day 3 outlook (hours 49-72)',
               'day 4 outlook (hours 73-96)','day 5 outlook (hours 97-120)','day 6 outlook (hours 121-144)',
               'day 7 outlook (hours 145-168)']

winter = ['211201','220228']
spring = ['220301','220531']
summer = ['220601','220831']
fall = ['211001','211130', '220901','220930']
seasons = [winter,spring,summer,fall]

#stations = np.loadtxt(station_file,usecols=0,delimiter=',',dtype='str')

variables = ['PCPTOT', 'SFCWSPD_KF', 'SFCWSPD', 'PCPT6']
variable_names = ['Hourly Precipitation', 'Wind Speed-KF ', 'Wind Speed-Raw', '6-Hour Accumulated Precipitation']
variable_units = ['[mm/hr]','[km/hr]','[km/hr]', '[mm/6hr]']

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
#choose "CAT_" for categorical scores (PCPT6, PCPTOT, SFCWSPD, SFCWSPD_KF) only, "MAE_", "RMSE_" or "SPCORR_"
stat_type = "CAT_"

# weighting curve steepness, Stull chose 100, so will test with that
k = int(sys.argv[4])

print(k)
###########################################################
### -------------------- FUNCTIONS ------------------------
###########################################################



def get_rankings(variable,time_domain,season):
    
     POD_list,POFD_list,PSS_list, HSS_list, CSI_list, GSS_list, MAE_list, RMSE_list, SPCORR_list, modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations = [],[],[],[],[],[],[],[], [], [], [],[],[],[]
     
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
                     
            print("Now on.. " + model + gridname + "   " + variable + " " + str(k) +" " +season[0] + " "+ season[1])
            
            if os.path.isfile(textfile_folder +  modelpath  + input_domain + '/' + variable + '/' + stat_type + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt"):
                
                #open the stat  file
                with open(textfile_folder +  modelpath  + input_domain + '/' + variable + '/' + stat_type + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt") as f:
                    lines = f.readlines()
                
                if stat_type == "CAT_":
                    POD_mean, POFD_mean, PSS_mean, HSS_mean, CSI_mean, GSS_mean = [],[],[],[],[],[]
                    for line in lines:
                        if float(season[0]) <= float(line.split("   ")[0][0:6]) and float(season[1]) >=float(line.split("  ")[1][0:6]):
                            
                            POD = line.split("   ")[5]
                            POFD = line.split("   ")[6]
                            PSS = line.split("   ")[7]
                            HSS = line.split("   ")[8]
                            CSI = line.split("   ")[9]
                            GSS = line.split("   ")[10]
                            dataratio = line.split("   ")[11]
                            numstations = line.split("   ")[12].strip()
                            data_check = True

                            POD_mean.append(float(POD))
                            POFD_mean.append(float(POFD))
                            PSS_mean.append(float(PSS))
                            HSS_mean.append(float(HSS))
                            CSI_mean.append(float(CSI))
                            GSS_mean.append(float(GSS))
                        
                            if len(season) > 2:
                                if float(season[2]) <= float(line.split("   ")[0][0:6]) and float(season[3]) >=float(line.split("   ")[1][0:6]):
                                
                                    POD = line.split("   ")[5]
                                    POFD = line.split("   ")[6]
                                    PSS = line.split("   ")[7]
                                    HSS = line.split("   ")[8]
                                    CSI = line.split("   ")[9]
                                    GSS = line.split("   ")[10]
                                    dataratio = line.split("   ")[11]
                                    numstations = line.split("   ")[12].strip()
                                    data_check = True

                                    POD_mean.append(float(POD))
                                    POFD_mean.append(float(POFD))
                                    PSS_mean.append(float(PSS))
                                    HSS_mean.append(float(HSS))
                                    CSI_mean.append(float(CSI))
                                    GSS_mean.append(float(GSS))
                            

                    POD = np.nanmean(POD_mean)
                    POFD = np.nanmean(POFD_mean)
                    PSS = np.nanmean(PSS_mean)
                    HSS = np.nanmean(HSS_mean)
                    CSI = np.nanmean(CSI_mean)
                    GSS = np.nanmean(GSS_mean)
                    
                elif stat_type == "MAE_":
                    MAE_mean = []
                    for line in lines:
                        if float(season[0]) <= float(line.split("   ")[0][0:6]) and float(season[1]) >=float(line.split("  ")[1][0:6]):
                            MAE = line.split("   ")[1]
                            dataratio = line.split("   ")[2]
                            numstations = line.split("   ")[3].strip()
                            data_check = True

                            MAE_mean.append(float(MAE))
                            
                            if len(season) > 2:
                                if float(season[2]) <= float(line.split("   ")[0][0:6]) and float(season[3]) >=float(line.split("   ")[1][0:6]):
                                    MAE = line.split("   ")[1]
                                    dataratio = line.split("   ")[2]
                                    numstations = line.split("   ")[3].strip()
                                    data_check = True

                                    MAE_mean.append(float(MAE))
                    
                    MAE = np.nanmean(MAE_mean)
                
                elif stat_type == "RMSE_":
                    RMSE_mean = []
                    for line in lines:
                        if float(season[0]) <= float(line.split("   ")[0][0:6]) and float(season[1]) >=float(line.split("  ")[1][0:6]):
                            RMSE = line.split("   ")[1]
                            dataratio = line.split("   ")[2]
                            numstations = line.split("   ")[3].strip()
                            data_check = True

                            RMSE_mean.append(float(RMSE))
                    
                            
                            if len(season) > 2:
                                if float(season[2]) <= float(line.split("   ")[0][0:6]) and float(season[3]) >=float(line.split("   ")[1][0:6]):
                                    RMSE = line.split("   ")[1]
                                    dataratio = line.split("   ")[2]
                                    numstations = line.split("   ")[3].strip()
                                    data_check = True

                                    RMSE_mean.append(float(RMSE))        
                    
                    RMSE = np.nanmean(RMSE_mean)
                
                elif stat_type == "spcorr_":
                    SPCORR_mean = []
                    for line in lines:
                        if float(season[0]) <= float(line.split("   ")[0][0:6]) and float(season[1]) >=float(line.split("  ")[1][0:6]):
                            SPCORR = line.split("   ")[1]
                            dataratio = line.split("   ")[2]
                            numstations = line.split("   ")[3].strip()
                            data_check = True

                            SPCORR_mean.append(float(SPCORR))

                            if len(season) > 2:
                                if float(season[2]) <= float(line.split("   ")[0][0:6]) and float(season[3]) >=float(line.split("   ")[1][0:6]):
                                    SPCORR = line.split("   ")[1]
                                    dataratio = line.split("   ")[2]
                                    numstations = line.split("   ")[3].strip()
                                    data_check = True

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
                
                if stat_type == "CAT_":
                    POD_list.append(float(POD))
                    POFD_list.append(float(POFD))
                    PSS_list.append(float(PSS))
                    HSS_list.append(float(HSS))
                    CSI_list.append(float(CSI))
                    GSS_list.append(float(GSS))
                    modelcolors.append(model_colors[color_count])
                
                elif stat_type == "MAE_":
                    MAE_list.append(float(MAE))
                
                elif stat_type == "RMSE_":
                    RMSE_list.append(float(RMSE))
                
                elif stat_type == "spcorr_":
                    SPCORR_list.append(float(SPCORR))

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
             
     return(POD_list,POFD_list,PSS_list, HSS_list, CSI_list, GSS_list,MAE_list, RMSE_list, SPCORR_list, modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations)
 
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

def make_weights(var, time_domain, time_label,POD,POFD,PSS, HSS, CSI, GSS,MAE, RMSE, SPCORR, modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations):
    if stat_type == "CAT_":
        POD_weights, POFD_weights, PSS_weights, HSS_weights, CSI_weights, GSS_weights = [],[],[],[],[],[]

        #sorts them greatest to least/least to greatest
        POD_sorted, modelnames_sortedPOD,modelcolors_sortedPOD = zip(*sorted(zip(POD, modelnames,modelcolors)))
        POFD_sorted, modelnames_sortedPOFD,modelcolors_sortedPOFD = zip(*sorted(zip(POFD, modelnames,modelcolors)))
        PSS_sorted, modelnames_sortedPSS,modelcolors_sortedPSS = zip(*sorted(zip(PSS, modelnames,modelcolors)))
        HSS_sorted, modelnames_sortedHSS,modelcolors_sortedHSS = zip(*sorted(zip(HSS, modelnames,modelcolors)))
        CSI_sorted, modelnames_sortedCSI,modelcolors_sortedCSI = zip(*sorted(zip(CSI, modelnames,modelcolors)))
        GSS_sorted, modelnames_sortedGSS,modelcolors_sortedGSS = zip(*sorted(zip(GSS, modelnames,modelcolors)))
    
        POD_xo = np.median(POD_sorted)
        for i in range(len(POD_sorted)):
            POD_weight = 1/(1+exp(-k*(POD_sorted[i]-POD_xo)))
            POD_weights.append(POD_weight)

        POFD_xo = np.median(POFD_sorted)
        for i in range(len(POFD_sorted)):
            POFD_weight = 1/(1+exp(-k*(POFD_sorted[i]-POFD_xo)))
            POFD_weights.append(POFD_weight)

        PSS_xo = np.median(PSS_sorted)
        for i in range(len(PSS_sorted)):
            PSS_weight = 1/(1+exp(-k*(PSS_sorted[i]-PSS_xo)))
            PSS_weights.append(PSS_weight)

        HSS_xo = np.median(HSS_sorted)
        for i in range(len(HSS_sorted)):
            HSS_weight = 1/(1+exp(-k*(HSS_sorted[i]-HSS_xo)))
            HSS_weights.append(HSS_weight)

        CSI_xo = np.median(CSI_sorted)
        for i in range(len(CSI_sorted)):
            CSI_weight = 1/(1+exp(-k*(CSI_sorted[i]-CSI_xo)))
            CSI_weights.append(CSI_weight)

        GSS_xo = np.median(GSS_sorted)
        for i in range(len(GSS_sorted)):
            GSS_weight = 1/(1+exp(-k*(GSS_sorted[i]-GSS_xo)))
            GSS_weights.append(GSS_weight)
        
        POD_weights = [i/sum(POD_weights) for i in POD_weights]        
        POFD_weights = [i/sum(POFD_weights) for i in POFD_weights]
        PSS_weights = [i/sum(PSS_weights) for i in PSS_weights]
        HSS_weights = [i/sum(HSS_weights) for i in HSS_weights]
        CSI_weights = [i/sum(CSI_weights) for i in CSI_weights]
        GSS_weights = [i/sum(GSS_weights) for i in GSS_weights]

        return(POD_weights, modelnames_sortedPOD, POFD_weights, modelnames_sortedPOFD, PSS_weights, modelnames_sortedPSS, HSS_weights, modelnames_sortedHSS, CSI_weights, modelnames_sortedCSI, GSS_weights, modelnames_sortedGSS)
    
    elif stat_type == "MAE_":
        
        MAE_weights = []
        MAE_sorted, modelnames_sortedMAE = zip(*sorted(zip(MAE, modelnames)))
        
        MAE_xo = np.median(MAE_sorted)
        for i in range(len(MAE_sorted)):
            MAE_weight = 1/(1+exp(-k*(MAE_sorted[i]-MAE_xo)))
            MAE_weights.append(MAE_weight)        
        
        MAE_weights = [i/sum(MAE_weights) for i in MAE_weights]
        return(MAE_weights, modelnames_sortedMAE)

    elif stat_type == "RMSE_":
    
        RMSE_weights = []
        RMSE_sorted, modelnames_sortedRMSE = zip(*sorted(zip(RMSE, modelnames)))
        
        RMSE_xo = np.median(RMSE_sorted)
        for i in range(len(RMSE_sorted)):
            RMSE_weight = 1/(1+exp(-k*(RMSE_sorted[i]-RMSE_xo)))
            RMSE_weights.append(RMSE_weight)
        
        RMSE_weights = [i/sum(RMSE_weights) for i in RMSE_weights]
        return(RMSE_weights, modelnames_sortedRMSE)

    elif stat_type == "spcorr_":
    
        SPCORR_weights = []
        SPCORR_sorted, modelnames_sortedSPCORR = zip(*sorted(zip(SPCORR, modelnames)))
        
        SPCORR_xo = np.median(SPCORR_sorted)
        for i in range(len(SPCORR_sorted)):
            SPCORR_weight = 1/(1+exp(-k*(SPCORR_sorted[i]-SPCORR_xo)))
            SPCORR_weights.append(SPCORR_weight)
        
        SPCORR_weights = [i/sum(SPCORR_weights) for i in SPCORR_weights]
        return(SPCORR_weights, modelnames_sortedSPCORR)
        
def main(args):
   # sys.stdout = open(logfilepath, "w") #opens log file
        
    var_i = 0
    for var in variables: #loop through variables
        
        time_count = 0
        for time_domain in time_domains:
            
            time_label = time_labels[time_count]
            
            for s in range(len(seasons)):
                
                if s == 0:
                    period = 'winter'
                elif s ==1:
                    period = 'spring'
                elif s ==2:
                    period = 'summer'
                elif s == 3:
                    period = 'fall'

                if var == "PCPT24" and time_domain in ['60hr','84hr','120hr','180hr']:
                    print('yes')
                    
                    time_count = time_count+1
                    continue
            
            #these returned variables are lists that contain one stat for each model (so length=#num of models)
                POD,POFD,PSS, HSS, CSI, GSS, MAE, RMSE, SPCORR, modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations = get_rankings(var,time_domain,seasons[s])
           
                if stat_type == "CAT_":
                    POD_weights, modelnames_sortedPOD, POFD_weights, modelnames_sortedPOFD, PSS_weights, modelnames_sortedPSS, HSS_weights, modelnames_sortedHSS, CSI_weights, modelnames_sortedCSI, GSS_weights, modelnames_sortedGSS = make_weights(var, time_domain, time_label,POD,POFD,PSS, HSS, CSI, GSS,MAE, RMSE, SPCORR, modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations)
                    weights_POD = pd.DataFrame([POD_weights], columns = modelnames_sortedPOD)
                    weights_POD.to_csv(save_folder + str(k) + '/' + stat_type + '/weights_POD_'+time_domain+'_'+var+'_'+period)
                
                    weights_POFD = pd.DataFrame([POFD_weights], columns = modelnames_sortedPOFD)
                    weights_POFD.to_csv(save_folder + str(k) + '/' + stat_type + '/weights_POFD_'+time_domain+'_'+var+ '_'+period)
                
                    weights_PSS = pd.DataFrame([PSS_weights], columns = modelnames_sortedPSS)
                    weights_PSS.to_csv(save_folder + str(k) + '/' + stat_type + '/weights_PSS_'+time_domain+'_'+var+'_'+period)
                
                    weights_HSS = pd.DataFrame([HSS_weights], columns = modelnames_sortedHSS)
                    weights_HSS.to_csv(save_folder + str(k) + '/' + stat_type + '/weights_HSS_'+time_domain+'_'+var+'_'+period)
                
                    weights_CSI = pd.DataFrame([CSI_weights], columns = modelnames_sortedCSI)
                    weights_CSI.to_csv(save_folder +str(k) + '/' + stat_type + '/weights_CSI_'+time_domain+'_'+var+'_'+period)
                
                    weights_GSS = pd.DataFrame([GSS_weights], columns = modelnames_sortedGSS)
                    weights_GSS.to_csv(save_folder +str(k) + '/' + stat_type + '/weights_GSS_'+time_domain+'_'+var+'_'+period)
            
                elif stat_type == "MAE_":
                    MAE_weight, modelnames_sortedMAE = make_weights(var, time_domain, time_label,POD,POFD,PSS, HSS, CSI, GSS, MAE, RMSE, SPCORR, modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations)
                    weights_all = pd.DataFrame([MAE_weight], columns = modelnames_sortedMAE)
                    weights_all.to_csv(save_folder +str(k) + '/' + stat_type + '/weights_all_'+time_domain+'_'+var+'_'+period)

                elif stat_type == "RMSE_":
                    RMSE_weight, modelnames_sortedRMSE = make_weights(var, time_domain, time_label,POD,POFD,PSS, HSS, CSI, GSS, MAE, RMSE, SPCORR, modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations)
                    weights_all = pd.DataFrame([RMSE_weight], columns = modelnames_sortedRMSE)
                    weights_all.to_csv(save_folder +str(k) + '/' + stat_type + '/weights_all_'+time_domain+'_'+var+'_'+period)
            
                elif stat_type == "spcorr_":
                    SPCORR_weight, modelnames_sortedSPCORR = make_weights(var, time_domain, time_label,POD,POFD,PSS, HSS, CSI, GSS, MAE, RMSE, SPCORR, modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations)
                    weights_all = pd.DataFrame([SPCORR_weight], columns = modelnames_sortedSPCORR)
                    weights_all.to_csv(save_folder+str(k) + '/' + stat_type + '/weights_all_'+time_domain+'_'+var+'_'+period)
            
            time_count = time_count+1
            


        var_i=var_i+1
            
    #sys.stdout.close() #close log file

if __name__ == "__main__":
    main(sys.argv)

