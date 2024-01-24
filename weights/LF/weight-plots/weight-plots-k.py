#!/usr/bin python

"""
Created in winter 2023

@author: reagan mckinney

This script is for plotting the k weights for each model.
 
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
#logfilepath = "/home/egnegy/python_plotting/log/plot_leaderboards.log"

#location to save the images
save_folder = '/home/verif/verif-post-process/weights/LF/weight-plots/'
#save_folder = '/verification/Statistics/img/monthly/'

#description file for stations
#station_file = '/home/egnegy/ensemble-verification/testing_stations/input/station_list_leaderboards.txt'

#description file for models
models_file = '/home/verif/verif-post-process/input/model_list_weights.txt'

textfile_folder = '/home/verif/verif-post-process/weights/LF/output/weights-seasonal/'
weight_type = 'VLF'
###########################################################
### -------------------- INPUT ------------------------
###########################################################

# takes an input date for the last day of the week you want to include
#time_domains = ['60hr','84hr','120hr','180hr','day1','day2','day3','day4','day5','day6','day7']

#time_labels = ['outlook hours 1-60','outlook hours 1-84','outlook hours 1-120','outlook hours 1-180',
#               'day 1 outlook (hours 1-24)','day 2 outlook (hours 25-48)','day 3 outlook (hours 49-72)',
#               'day 4 outlook (hours 73-96)','day 5 outlook (hours 97-120)','day 6 outlook (hours 121-144)',
#               'day 7 outlook (hours 145-168)']
#stations = np.loadtxt(station_file,usecols=0,delimiter=',',dtype='str')
time_domains=['60hr']
time_labels=['outlook hours 1-60']
variables = ['SFCTC_KF', 'PCPTOT', 'SFCWSPD_KF']
variable_names = ['Temperature-KF', 'Hourly Precipitation', 'Wind Speed-KF ']
#variable_units = ['[C]','[C]', '[mm/hr]','[km/hr]', '[km/hr]', '[mm/6hr]']

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
model_colors = ['C0','C1','C2','C3','C4','C5','C6','C7','C8','C9','#ffc219','#CDB7F6','#65fe08','#fc3232','#754200','#00FFFF','#fc23ba','#a1a1a1']
input_domain = 'small'
###########################################################
### -------------------- FUNCTIONS ------------------------
###########################################################



def get_rankings(variable,time_domain):
    
     MAE_40_list,MAE_100_list,MAE_200_list,modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations = [],[],[],[],[],[],[],[]
     
     leg_count = 0
     color_count = 0
    
     for i in range(len(models)):
        model = models[i] #loops through each model
        
        for grid in grids[i].split(","): #loops through each grid size for each model
        
            print("Now on.. " + model + grid + "   " + variable)
            print(textfile_folder +  "40/MAE_/" + "weights_all_" +time_domain+'_'+ variable + "_fall")
            if os.path.isfile(textfile_folder +  "40/MAE_/" + "weights_all_" +time_domain+'_'+ variable + "_fall"):
                #open the MAE 40 file
                f = textfile_folder +  "40/MAE_/" + "weights_all_" +time_domain+'_'+ variable + "_fall"
                MAE_40 = pd.read_csv(f, sep=",")
                if model+'_'+grid in MAE_40.columns:
                    MAE_40 = MAE_40[model+'_'+grid].values[0]
                else:
                    MAE_40 = 0
                
                print(MAE_40) 
                #open the MAE 100 file
                f = textfile_folder +  "100/MAE_/" + "weights_all_" +time_domain+'_'+ variable + "_fall"
                MAE_100 = pd.read_csv(f, sep=",")
                if model+'_'+grid in MAE_100.columns:
                    MAE_100 = MAE_100[model+'_'+grid].values[0]
                else:
                    MAE_100 = 0
                
                #open MAE 200 file
                f = textfile_folder +  "200/MAE_/" + "weights_all_" +time_domain+'_'+ variable + "_fall"
                MAE_200 = pd.read_csv(f, sep=",")
                if model+'_'+grid in MAE_200.columns:
                    MAE_200 = MAE_200[model+'_'+grid].values[0]
                else:
                    MAE_200 = 0
                 
                MAE_40_list.append(float(MAE_40))
                MAE_100_list.append(float(MAE_100))
                MAE_200_list.append(float(MAE_200))
                modelcolors.append(model_colors[color_count])
                modelnames.append(model+'_'+grid)
     
        color_count = color_count+1
             
     return(MAE_40_list,MAE_100_list,MAE_200_list,modelnames,modelcolors)

def make_leaderboard_sorted(var, var_name, time_domain, time_label,MAE_40,MAE_100,MAE_200,modelnames,modelcolors):
    #sorts them greatest to least/least to greatest
    MAE40_sorted, modelnames_sortedMAE40,modelcolors_sortedMAE40 = zip(*sorted(zip(MAE_40, modelnames,modelcolors)))
    MAE100_sorted, modelnames_sortedMAE100,modelcolors_sortedMAE100 = zip(*sorted(zip(MAE_100, modelnames,modelcolors)))
    MAE200_sorted, modelnames_sortedMAE200,modelcolors_sortedMAE200 = zip(*sorted(zip(MAE_200, modelnames,modelcolors)))
   
    #plotting
    x = np.arange(len(modelnames))
    width = 0.6
       
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3,figsize=(25,17),dpi=150)
    plt.tight_layout(w_pad=20)
    plt.subplots_adjust(top=0.9)
    
    #fig.suptitle(var_name + ' ' + savetype + ' stats from ' + str(obs_dates) + " for " + time_label + "  [model init. dates: " + str(print_startdate) + '-' + str(print_enddate) + " (" + str(delta+1) + " days)]",fontsize=25)
    
    ax1.barh(x, MAE40_sorted, width,color=modelcolors_sortedMAE40,edgecolor='k',linewidth=2.5)
    ax1.set_yticks(x)
    ax1.set_yticklabels(modelnames_sortedMAE40,fontsize=18)
    ax1.set_title("k = 40",fontsize=18)
    ax1.set_xlabel(var_name + " and Mean Absolute Error Weight",fontsize=20)
    ax1.set_xlim(0.015,0.02)
    ax2.barh(x, MAE100_sorted, width,color=modelcolors_sortedMAE100,edgecolor='k',linewidth=2.5)
    ax2.set_yticks(x)
    ax2.set_yticklabels(modelnames_sortedMAE100,fontsize=18)
    ax2.set_title("k = 100",fontsize=18)
    ax2.set_xlim(0.015,0.02)
    ax2.set_xlabel(var_name + " and Mean Absolute  Error Weight",fontsize=20)
    
    left_lim=0
    
    #if any(np.array(MAE200_sorted)<0):
    #    left_lim = np.nanmin(MAE200_sorted) - 0.05

        
    ax3.barh(x, MAE200_sorted, width,color=modelcolors_sortedMAE200,edgecolor='k',linewidth=2.5)
    ax3.set_yticks(x)
    ax3.set_yticklabels(modelnames_sortedMAE200,fontsize=18)
    ax3.set_title("k = 200",fontsize=18)
    ax3.set_xlim(0.015,0.02)
    ax3.set_xlabel(var_name + " and Mean Absolute Error Weight",fontsize=20)
    
    
    for ax in [ax1, ax2, ax3]:
        ax.tick_params(axis='x', labelsize=20)
        ax.set_ylim(-0.9,len(modelnames)-width*0.5)
        ax.set_axisbelow(True)
        ax.grid(True,axis='x')
    
    plt.savefig(save_folder  + input_domain + '_' + var + '_' + time_domain + '_'+weight_type+'.png',bbox_inches='tight')
    
def main(args):
   # sys.stdout = open(logfilepath, "w") #opens log file
        
    var_i = 0
    for var in variables: #loop through variables
        
        time_count = 0
        for time_domain in time_domains:
            
            time_label = time_labels[time_count]
                                        
            #these returned variables are lists that contain one stat for each model (so length=#num of models)
            MAE_40_list,MAE_100_list,MAE_200_list,modelnames,modelcolors = get_rankings(var,time_domain)
            print(MAE_40_list)  
            make_leaderboard_sorted(var, variable_names[var_i], time_domain,time_label, MAE_40_list,MAE_100_list,MAE_200_list,modelnames,modelcolors)
           
            time_count = time_count+1

        var_i=var_i+1
            
    #sys.stdout.close() #close log file

if __name__ == "__main__":
    main(sys.argv)

