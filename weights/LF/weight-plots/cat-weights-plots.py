#!/usr/bin python

"""
Created in winter 2023

@author: reagan mckinney

This script is for plotting the weights for each model.
 
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

textfile_folder = '/home/verif/verif-post-process/weights/PWA/output/weights-seasonal/'
weight_type = 'pwa'
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
variables = [ 'PCPTOT', 'SFCWSPD_KF']
variable_names = [ 'Hourly Precipitation', 'Wind Speed-KF ']
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
    
     POD_list, POFD_list, PSS_list, HSS_list, CSI_list, GSS_list,MAE_list,RMSE_list,correlation_list,modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations = [],[],[],[],[],[],[],[],[],[],[],[],[],[]
     
     leg_count = 0
     color_count = 0
    
     for i in range(len(models)):
        model = models[i] #loops through each model
        
        for grid in grids[i].split(","): #loops through each grid size for each model
        
            print("Now on.. " + model + grid + "   " + variable)
            
            if os.path.isfile(textfile_folder +  "MAE_/" + "weights_all_" +time_domain+'_'+ variable + "_fall"):
                #open the MAE file
                f = textfile_folder +  "MAE_/" + "weights_all_" +time_domain+'_'+ variable + "_fall"
                MAE = pd.read_csv(f, sep=",")
                if model+'_'+grid in MAE.columns:
                    MAE = MAE[model+'_'+grid].values[0]
                else:
                    MAE = 0
                #open the RMSE file
                f = textfile_folder +  "RMSE_/" + "weights_all_" +time_domain+'_'+ variable + "_fall"
                RMSE = pd.read_csv(f, sep=",")
                if model+'_'+grid in RMSE.columns:
                    RMSE = RMSE[model+'_'+grid].values[0]
                else:
                    RMSE = 0
                #open spcorr file
                f = textfile_folder +  "spcorr_/" + "weights_all_" +time_domain+'_'+ variable + "_fall"
                spcorr = pd.read_csv(f, sep=",")
                if model+'_'+grid in spcorr.columns:
                    spcorr = spcorr[model+'_'+grid].values[0]
                else:
                    spcorr = 0

                MAE_list.append(float(MAE))
                RMSE_list.append(float(RMSE))
                correlation_list.append(float(spcorr))
                modelcolors.append(model_colors[color_count])
                modelnames.append(model+'_'+grid)
            
            
            
                #open CSI file
                f = textfile_folder +  "CAT_/" + "weights_CSI_" +time_domain+'_'+ variable + "_fall"
                CSI = pd.read_csv(f, sep=",")
                if model+'_'+grid in CSI.columns:
                    CSI = CSI[model+'_'+grid].values[0]
                else:
                    CSI = 0

                #open POD file
                f = textfile_folder +  "CAT_/" + "weights_POD_" +time_domain+'_'+ variable + "_fall"
                POD = pd.read_csv(f, sep=",")
                if model+'_'+grid in POD.columns:
                    POD = POD[model+'_'+grid].values[0]
                else:
                    POD = 0
                
                f = textfile_folder +  "CAT_/" + "weights_POFD_" +time_domain+'_'+ variable + "_fall"
                POFD = pd.read_csv(f, sep=",")
                if model+'_'+grid in POFD.columns:
                    POFD = POFD[model+'_'+grid].values[0]
                else:
                    POFD = 0
                
                f = textfile_folder +  "CAT_/" + "weights_PSS_" +time_domain+'_'+ variable + "_fall"
                PSS = pd.read_csv(f, sep=",")
                if model+'_'+grid in PSS.columns:
                    PSS = PSS[model+'_'+grid].values[0]
                else:
                    PSS = 0
                
                f = textfile_folder +  "CAT_/" + "weights_HSS_" +time_domain+'_'+ variable + "_fall"
                HSS = pd.read_csv(f, sep=",")
                if model+'_'+grid in HSS.columns:
                    HSS = HSS[model+'_'+grid].values[0]
                else:
                    HSS = 0
                
                f = textfile_folder +  "CAT_/" + "weights_GSS_" +time_domain+'_'+ variable + "_fall"
                GSS = pd.read_csv(f, sep=",")
                if model+'_'+grid in GSS.columns:
                    GSS = GSS[model+'_'+grid].values[0]
                else:
                    GSS = 0
                
                POD_list.append(float(POD))
                POFD_list.append(float(POFD))
                PSS_list.append(float(PSS))
                HSS_list.append(float(HSS))
                CSI_list.append(float(CSI))
                GSS_list.append(float(GSS))
        
        color_count = color_count+1
             
     return(POD_list,POFD_list,PSS_list, HSS_list, CSI_list, GSS_list, MAE_list,RMSE_list,correlation_list,modelnames,modelcolors)

def make_leaderboard_sorted(POD,POFD,PSS, HSS, CSI, GSS,var, var_name, time_domain, time_label,MAE,RMSE,corr,modelnames,modelcolors):
    #sorts them greatest to least/least to greatest
    MAE_sorted, modelnames_sortedMAE,modelcolors_sortedMAE = zip(*sorted(zip(MAE, modelnames,modelcolors)))
    RMSE_sorted, modelnames_sortedRMSE,modelcolors_sortedRMSE = zip(*sorted(zip(RMSE, modelnames,modelcolors)))
    corr_sorted, modelnames_sortedcorr,modelcolors_sortedcorr = zip(*sorted(zip(corr, modelnames,modelcolors)))
    POD_sorted, modelnames_sortedPOD,modelcolors_sortedPOD = zip(*sorted(zip(POD, modelnames,modelcolors)))
    POFD_sorted, modelnames_sortedPOFD,modelcolors_sortedPOFD = zip(*sorted(zip(POFD, modelnames,modelcolors),reverse=True))
    PSS_sorted, modelnames_sortedPSS,modelcolors_sortedPSS = zip(*sorted(zip(PSS, modelnames,modelcolors)))
    HSS_sorted, modelnames_sortedHSS,modelcolors_sortedHSS = zip(*sorted(zip(HSS, modelnames,modelcolors)))
    CSI_sorted, modelnames_sortedCSI,modelcolors_sortedCSI = zip(*sorted(zip(CSI, modelnames,modelcolors)))
    GSS_sorted, modelnames_sortedGSS,modelcolors_sortedGSS = zip(*sorted(zip(GSS, modelnames,modelcolors)))

    print(MAE_sorted)
    #plotting
    x = np.arange(len(modelnames))
    width = 0.6
       
    fig, (ax4,ax5,ax6) = plt.subplots(1, 3,figsize=(25,17),dpi=150)
    plt.rcParams.update({'font.size': 30})
    plt.tight_layout(w_pad=5)
    plt.subplots_adjust(top=0.9)
    
    #fig.suptitle(var_name + ' ' + savetype + ' stats from ' + str(obs_dates) + " for " + time_label + "  [model init. dates: " + str(print_startdate) + '-' + str(print_enddate) + " (" + str(delta+1) + " days)]",fontsize=25)
    '''
    ax1.barh(x, MAE_sorted, width,color=modelcolors_sortedMAE,edgecolor='k',linewidth=2.5)
    ax1.set_yticks(x)
    ax1.set_yticklabels(modelnames_sortedMAE,fontsize=40)
    #ax1.set_title("Mean Absolute Error (MAE)",fontsize=18)
    ax1.set_xlabel(var_name + " and MAE Weight",fontsize=40)
    #ax1.set_xlim(0.015,0.02)

    ax2.barh(x, RMSE_sorted, width,color=modelcolors_sortedRMSE,edgecolor='k',linewidth=2.5)
    ax2.set_yticks(x)
    ax2.set_yticklabels(modelnames_sortedRMSE,fontsize=40)
    #ax2.set_title("Root Mean Square Error (RMSE)",fontsize=18)
    ax2.set_xlabel(var_name + " and RMSE Weight",fontsize=40)
    #ax2.set_xlim(0.015,0.02)
    #left_lim=0
    
    #if any(np.array(corr_sorted)<0):
    #    left_lim = np.nanmin(corr_sorted) - 0.05

        
    ax3.barh(x, corr_sorted, width,color=modelcolors_sortedcorr,edgecolor='k',linewidth=2.5)
    ax3.set_yticks(x)
    ax3.set_yticklabels(modelnames_sortedcorr,fontsize=40)
    #ax3.set_title("Spearman Correlation",fontsize=18)
    #ax3.set_xlim(0.015,0.025)
    ax3.set_xlabel(var_name + " and SPCORR Weight",fontsize=40)
    
    ax6.barh(x, POD_sorted, width,color=modelcolors_sortedPOD,edgecolor='k',linewidth=2.5)
    ax6.set_yticks(x)
    ax6.set_yticklabels(modelnames_sortedPOD,fontsize=40)
    #ax6.set_title("Probability of Detection (POD)",fontsize=18)
    #ax6.set_xlim(0,1)
    ax6.set_xlabel(var_name + " and POD Weight",fontsize=40)
    
    ax7.barh(x, POFD_sorted, width,color=modelcolors_sortedPOFD,edgecolor='k',linewidth=2.5)
    ax7.set_yticks(x)
    ax7.set_yticklabels(modelnames_sortedPOFD,fontsize=40)
    #ax7.set_title("Probability of False Detection (POFD)",fontsize=18)
    #ax7.set_xlim(0,1)
    ax7.set_xlabel(var_name + " and POFD Weight",fontsize=40)
    ''' 
    ax4.barh(x, PSS_sorted, width,color=modelcolors_sortedPSS,edgecolor='k',linewidth=2.5)
    ax4.set_yticks(x)
    ax4.set_yticklabels(modelnames_sortedPSS,fontsize=18)
    #ax4.set_title("Pierce Skill Score (PSS)",fontsize=18)
    #ax4.set_xlim(-1,1)
    ax4.set_xlabel(var_name + " and PSS Weight",fontsize=20)
    
    ax5.barh(x, HSS_sorted, width,color=modelcolors_sortedHSS,edgecolor='k',linewidth=2.5)
    ax5.set_yticks(x)
    ax5.set_yticklabels(modelnames_sortedHSS,fontsize=18)
    #ax5.set_title("Heidke Skill Score (HSS)",fontsize=18)
    #ax5.set_xlim(-1, 1)
    ax5.set_xlabel(var_name + " and HSS Weight",fontsize=20)
    '''
    ax9.barh(x, CSI_sorted, width,color=modelcolors_sortedCSI,edgecolor='k',linewidth=2.5)
    ax9.set_yticks(x)
    ax9.set_yticklabels(modelnames_sortedCSI,fontsize=40)
    #ax.set_title("Critical Success Index (CSI)",fontsize=18)
    #ax9.set_xlim(0,1)
    ax9.set_xlabel(var_name + " and CSI Weight",fontsize=40)
    '''
    ax6.barh(x, GSS_sorted, width,color=modelcolors_sortedGSS,edgecolor='k',linewidth=2.5)
    ax6.set_yticks(x)
    ax6.set_yticklabels(modelnames_sortedGSS,fontsize=18)
    #ax6.set_title("Gilbert Skill Score (GSS)",fontsize=18)
    #ax9.set_xlim(-1,1)
    ax6.set_xlabel(var_name + " and GSS Weight",fontsize=20)
    
    for ax in [ax4,ax5,ax6]:
        ax.tick_params(axis='x',labelsize=16)
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
            POD,POFD,PSS, HSS, CSI, GSS,MAE,RMSE,corr,modelnames,modelcolors = get_rankings(var,time_domain)
            #print(MAE) 
            make_leaderboard_sorted(POD,POFD,PSS, HSS, CSI, GSS,var, variable_names[var_i], time_domain,time_label, MAE,RMSE,corr,modelnames,modelcolors)
           
            time_count = time_count+1

        var_i=var_i+1
            
    #sys.stdout.close() #close log file

if __name__ == "__main__":
    main(sys.argv)

