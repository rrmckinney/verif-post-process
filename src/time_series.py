#!/usr/bin python

"""
Created in summer 2021 @author: evagnegy

Adapted summer 2023 by rmckinney to new file system on specter.

This script is for the weekly leadership time series board that is not quite operational.
 
"""

import matplotlib.pyplot as plt
import os
import numpy as np
import datetime #import datetime, timedelta
import sys
import pandas as pd

import warnings
warnings.filterwarnings("ignore",category=RuntimeWarning)
###########################################################
### -------------------- FILEPATHS ------------------------
###########################################################


#path to save the log/output
#logfilepath = "/home/egnegy/python_plotting/log/time_series.log"

#location to save the images
save_folder = '/www/results/verification/images/leaderboards/time_series/'

#description file for models
models_file = '/home/verif/verif-post-process/input/model_list.txt'

stats_folder = '/verification/Statistics/'

textfile_folder = '/verification/Statistics/'

###########################################################
### -------------------- INPUT ------------------------
###########################################################

# takes 2 input dates (start and end), weekly/monthly,domain
if len(sys.argv) == 5:
    date_entry1 = sys.argv[1]    #input date YYMMDD 
    
    date_entry2 = sys.argv[2]    #input date YYMMDD 
    
    savetype = sys.argv[3]
    if savetype not in ['weekly','monthly']:
        raise Exception("Invalid time input entry. Current options: weekly, monthly. Case sensitive.")
         
    input_domain = sys.argv[4]
    if input_domain not in ['large','small']:
        raise Exception("Invalid domain input entry. Current options: large, small. Case sensitive.")
         

else:
    raise Exception("Invalid input entries. Needs YYMMDD for start and end dates, a weekly/monthly option, and a domain")


time_domains = ['60hr','84hr','120hr','180hr','day1','day2','day3','day4','day5','day6','day7']

variables = ['SFCTC_KF','SFCTC','PCPTOT', 'SFCWSPD_KF', 'SFCWSPD', 'PCPT6']
variable_names = ['Temperature-KF', 'Temperature-Raw','Hourly Precipitation', 'Wind Speed-KF ', 'Wind Speed-Raw', '6-Hour Accumulated Precipitation']
variable_units = ['[C]','[C]', '[mm/hr]','[km/hr]','[km/hr]', '[mm/6hr]']


# list of model names as strings (names as they are saved in www_oper and my output folders)
models = np.loadtxt(models_file,usecols=0,dtype='str')

grids = np.loadtxt(models_file,usecols=1,dtype='str') #list of grid sizings (g1, g2, g3 etc) for each model
gridres = np.loadtxt(models_file,usecols=2,dtype='str') #list of grid resolution in km for each model
model_names = np.loadtxt(models_file,usecols=4,dtype='str') #longer names, used for legend

# this loop makes the names for each model/grid pair that will go in the legend
legend_labels = []
model_colors = []
model_lines = []

colors = ['C0','C1','C2','C3','C4','C5','C6','C7','C8','C9','#ffc219','#CDB7F6','#65fe08','#fc3232','#754200','#00FFFF','#fc23ba','#a1a1a1','#000000','#000000','#000000','#000000']
grid_lines = ["-","--",":","-.","-"]
for i in range(len(model_names)):
    for j in range(len(gridres[i].split(","))):
        grid = gridres[i].split(",")[j]
        model = model_names[i]
        
        if model == "SREF" or "ENS_" in model:
            grid = ""
        print(model+grid)
        legend_labels.append(model + grid)
        
        model_colors.append(colors[i])
        model_lines.append(grid_lines[j])


model_lines[-4:] = ["-","--",":","-."]

###########################################################
### -------------------- FUNCTIONS ------------------------
###########################################################



def get_statistics(variable,time_domain):
    
     
     leg_count = 0
     color_count = 0
    
     all_MAE_lists, all_RMSE_lists, all_spcorr_lists, all_startdate_lists,modelnames,skipped_modelnames,modelcolors = [],[],[],[],[],[],[]
     for i in range(len(models)):
        model = models[i] #loops through each model
        
        for grid in grids[i].split(","): #loops through each grid size for each model
        
        
            #ENS only has one grid (and its not saved in a g folder)
            if "ENS" in model:
                modelpath = model + '/' + input_domain + '/' + variable + '/'
            else:
                modelpath = model + '/' + grid + '/' + input_domain + '/' + variable + '/'
             
            MAE_file = textfile_folder +  modelpath + "MAE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt"
           #skips time_domains that dont exist for this model
            if os.path.isfile(MAE_file):
                MAE_txt = pd.read_csv(MAE_file, sep="   | ", names=['start', 'end','stat', 'num hours', 'num stations'])
                MAE_txt = MAE_txt.sort_values(by=['start'])
                MAE_txt = MAE_txt.drop_duplicates()
                
                data_check = False 
                
                MAE_start = MAE_txt['start'].to_numpy()
                MAE_end = MAE_txt['end'].to_numpy()
                
                if int(date_entry1) in MAE_start and int(date_entry2) in MAE_end:
                    data_check = True
                else:
                    print("   **Skipping " + model + grid + ", no data yet**")
                    skipped_modelnames.append(legend_labels[leg_count] + ":  (none)")
                    leg_count = leg_count+1
                    continue
                start_ind = np.where(MAE_start == int(date_entry1))
                end_ind = np.where(MAE_end == int(date_entry2))
                
                if np.size(start_ind)==0:
                    start_ind=[0]
                
                MAE_list = np.loadtxt(MAE_file,usecols=2,dtype=float)[start_ind[0][0]:end_ind[0][0]]
                startdate_list = np.loadtxt(MAE_file,usecols=0,dtype=str)[start_ind[0][0]:end_ind[0][0]]
    
                RMSE_file = textfile_folder +  modelpath + "RMSE_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt"
                RMSE_list = np.loadtxt(RMSE_file,usecols=2,dtype=float)[start_ind[0][0]:end_ind[0][0]]
                
                spcorr_file = textfile_folder +  modelpath + "spcorr_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt"               
                spcorr_list = np.loadtxt(spcorr_file,usecols=2,dtype=float)[start_ind[0][0]:end_ind[0][0]]
                  
                
                # the ratios are the same for each statistic, so only checked once
                dataratio = np.loadtxt(MAE_file,usecols=3,dtype=str)[start_ind[0][0]:end_ind[0][0]]
                expected = [i.split('/')[1] for i in dataratio]
                actual = [i.split('/')[0] for i in dataratio]
                
                #nans any value where less than half datapoints were there
                MAE_list[:] = ["nan" if int(actual[x]) < int(expected[x])/2 else MAE_list[x] for x in range(len(MAE_list))] 
                RMSE_list[:] = ["nan" if int(actual[x]) < int(expected[x])/2 else RMSE_list[x] for x in range(len(RMSE_list))] 
                spcorr_list[:] = ["nan" if int(actual[x]) < int(expected[x])/2 else spcorr_list[x] for x in range(len(spcorr_list))] 
                
                all_MAE_lists.append(MAE_list)
                all_RMSE_lists.append(RMSE_list)
                all_spcorr_lists.append(spcorr_list)
                print(all_MAE_lists)
                all_startdate_lists.append(startdate_list)
                modelnames.append(legend_labels[leg_count])
                modelcolors.append(model_colors[color_count])
                
            #else:
                #print("   Skipping  " + model + grid + "   " + time_domain + " (doesn't exist)")
               
            leg_count=leg_count+1
                
        color_count=color_count+1
        
     return(all_MAE_lists,all_RMSE_lists,all_spcorr_lists,all_startdate_lists,modelnames,modelcolors)
            
                   
def plot_timeseries(var, var_name, var_unit, time_domain, MAE,RMSE,spcorr,startdates,modelnames,modelcolors):
                           
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1,figsize=(25,17),dpi=150)
    total = len(modelnames)
    for i in range(total):
        model = modelnames[i]
        color = model_colors[i]
        line_type = model_lines[i]
        
        dates=[]
        for j in range(len(startdates[i])):
            input_date = datetime.datetime.strptime(str(startdates[i][j]), "%y%m%d").date()
            if savetype=="monthly":
                dates.append(datetime.datetime.strftime(input_date,"%m-%y"))
            elif savetype=="weekly":
                dates.append(datetime.datetime.strftime(input_date,"%m-%d-%y"))
        ax1.plot(dates,MAE[i],color=color,linestyle=line_type, marker='o', label = model)
        ax2.plot(dates,RMSE[i],color=color,linestyle=line_type, marker='o', label = model)
        ax3.plot(dates,spcorr[i],color=color,linestyle=line_type, marker='o', label = model)

    
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)
    
    #plt.legend(bbox_to_anchor=(1, -0.4),ncol=12)
    
    if savetype=="monthly":
        plt.xlabel('verification ' + savetype[:-2],fontsize=18)
    elif savetype=="weekly":
        plt.xlabel('verification ' + savetype[:-2] + ' (first initialization date of week)',fontsize=18)
        
    plt.xticks(fontsize=18,rotation=45)
    
    ax1.set_title('Mean absolute error',fontsize=18)
    ax1.tick_params(axis = 'both', labelsize = 18)
    ax1.set_ylabel(var_name + " MAE " + var_unit,fontsize=16)
    
    ax2.set_title('Root-mean-squared error',fontsize=18)
    ax2.tick_params(axis = 'both', labelsize = 18)
    ax2.set_ylabel(var_name + " RMSE " + var_unit,fontsize=16)
    
    ax3.set_title('Spearmans Correlation',fontsize=18)
    ax3.tick_params(axis = 'both', labelsize = 18)
    ax3.set_ylabel(var_name + " Spearmans Correlation",fontsize=16)


    plt.savefig(save_folder + input_domain + '_' + var + '_' + savetype + '_' + time_domain + '.png',bbox_inches='tight')


def main(args):
   # sys.stdout = open(logfilepath, "w") #opens log file
    
    var_i = 0
    for var in variables: #loop through variables
        
        for time_domain in time_domains:
            
            #these returned variables are lists that contain one stat for each model (so length=#num of models)
            MAE,RMSE,corr,startdates,modelnames,modelcolors = get_statistics(var,time_domain)
            plot_timeseries(var, variable_names[var_i], variable_units[var_i], time_domain, MAE,RMSE,corr,startdates,modelnames,modelcolors)

        var_i=var_i+1
            
    #sys.stdout.close() #close log file

if __name__ == "__main__":
    main(sys.argv)
