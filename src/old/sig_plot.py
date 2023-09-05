#!/usr/bin python

"""
Created in summer 2021

@author: evagnegy

This script is for the weekly leadership board 
 
"""

import matplotlib.pyplot as plt
import os
import numpy as np
import datetime #import datetime, timedelta
import sys


import warnings
warnings.filterwarnings("ignore",category=RuntimeWarning)
###########################################################
### -------------------- FILEPATHS ------------------------
###########################################################


#path to save the log/output
#logfilepath = "/home/egnegy/python_plotting/log/plot_leaderboards.log"

#location to save the images
#save_folder = '/www/results/verification/images/leaderboards/'
save_folder = '/verification/Statistics/img/monthly/'

#description file for stations
#station_file = '/home/egnegy/ensemble-verification/testing_stations/input/station_list_leaderboards.txt'

#description file for models
models_file = '/home/verif/verif-post-process/input/model_list.txt'

textfile_folder = '/verification/Statistics/t_test/'

###########################################################
### -------------------- INPUT ------------------------
###########################################################

# takes an input date for the last day of the week you want to include
if len(sys.argv) == 4:
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

variables = ['SFCTC_KF','PCPTOT', 'SFCWSPD_KF',  'PCPT6']
variable_names = ['Temperature-KF','Hourly Precipitation', 'Wind Speed-KF ', '6-Hour Accumulated Precipitation']
variable_units = ['[C]', '[mm/hr]','[km/hr]', '[mm/6hr]']



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


###########################################################
### -------------------- FUNCTIONS ------------------------
###########################################################



def get_rankings(variable,time_domain):
    
     t_test_list,modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations = [],[],[],[],[],[],
     
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
                        
            
            print("Now on.. " + model + gridname + "   " + variable)
            
            if os.path.isfile(textfile_folder +  modelpath  + input_domain + '/' + variable + '/' + "t_test_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt"):
                #open the t_test file
                with open(textfile_folder +  modelpath  + input_domain + '/' + variable + '/' + "t_test_" + savetype + "_" + variable + "_" + time_domain + "_" + input_domain + ".txt") as f:
                    t_lines = f.readlines()
        
                data_check = False
                #find the line for the given dates
                for t_line in t_lines:
                    if date_entry1 in t_line and date_entry2 in t_line:
                        t_test = t_line.split("   ")[1]
                        dataratio = t_line.split("   ")[2]
                        numstations = t_line.split("   ")[3].strip()
                        data_check = True


                if data_check == False:
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
                
 
                t_test_list.append(float(t_test))
                modelcolors.append(model_colors[color_count])
                
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
             
     return(t_test_list,modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations)
 
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


def make_leaderboard_sorted(var, var_name, var_unit, time_domain, time_label,t_test,modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations):     

    #sorts them greatest to least/least to greatest
    t_test_sorted, modelnames_sortedt,modelcolors_sortedt = zip(*sorted(zip(t_test, modelnames,modelcolors),reverse=True))

    #plotting
    x = np.arange(len(modelnames))
    width = 0.6
       
    fig, ax1 = plt.subplots(1, figsize=(25,17),dpi=150)
    plt.tight_layout(w_pad=20)
    plt.subplots_adjust(top=0.9)
    
    obs_dates = get_obs_dates(time_domain)
    
    fig.suptitle(var_name + ' ' + savetype + ' stats from ' + str(obs_dates) + " for " + time_label + "  [model init. dates: " + str(print_startdate) + '-' + str(print_enddate) + " (" + str(delta+1) + " days)]",fontsize=25)
    
    ax1.barh(x, t_test_sorted, width,color=modelcolors_sortedt,edgecolor='k',linewidth=2.5)
    ax1.set_yticks(x)
    ax1.set_yticklabels(modelnames_sortedt,fontsize=18)
    ax1.set_title("T-Test ",fontsize=18)
    ax1.set_xlabel(var_name + " t_test " + var_unit,fontsize=20)
    
    
    for ax in ax1:
        ax.tick_params(axis='x', labelsize=20)
        ax.set_ylim(-0.9,len(modelnames)-width*0.5)
        ax.set_axisbelow(True)
        ax.grid(True,axis='x')
      
    if edited_modelnames != []:    
        plt.text(-3, -4, "*Missing model data:", fontsize=18)
        for x in range(len(edited_modelnames)):
            plt.text(-3, -5 -x, "            " + edited_modelnames[x], fontsize=18)
    
    if numofstations != []:  
        plt.text(-2, -4, "^Number of stations averaged:", fontsize=18)
        
        if len(numofstations) > 25:
           for x in range(25):
                plt.text(-2, -5 -x, "            " + numofstations[x], fontsize=18) 
           for x in range(len(numofstations)-25):
                plt.text(-1.3, -5 -x, "            " + numofstations[x+25], fontsize=18)
        else:
            for x in range(len(numofstations)):
                plt.text(-2, -5 -x, "            " + numofstations[x], fontsize=18)
        
            
    if skipped_modelnames != []:    
        plt.text(0, -4, "Skipped models (<50% datapoints):", fontsize=18)
        for x in range(len(skipped_modelnames)):
            plt.text(0, -5 -x, "            " + skipped_modelnames[x], fontsize=18)
    

    plt.savefig(save_folder + 'continuous/' + start_date[:-2] + '/' + input_domain + '_' + var + '_' + savetype + '_' + time_domain + '.png',bbox_inches='tight')
    

def main(args):
   # sys.stdout = open(logfilepath, "w") #opens log file
        
    var_i = 0
    for var in variables: #loop through variables
        
        time_count = 0
        for time_domain in time_domains:
            
            time_label = time_labels[time_count]
            
            if var == "APCP24" and time_domain in ['60hr','84hr','120hr','180hr']:
                time_count = time_count+1
                continue
            
            #these returned variables are lists that contain one stat for each model (so length=#num of models)
            t_test,modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations = get_rankings(var,time_domain)
            
            
            make_leaderboard_sorted(var, variable_names[var_i], variable_units[var_i], time_domain,time_label, t_test, modelnames,modelcolors,edited_modelnames,skipped_modelnames,numofstations)
           # make_leaderboard_unsorted(var, variable_names[var_i], variable_units[var_i], time_domain)
           # make_leaderboard_gridsize(var, variable_names[var_i], variable_units[var_i], time_domain)
           
            time_count = time_count+1

        var_i=var_i+1
            
    #sys.stdout.close() #close log file

if __name__ == "__main__":
    main(sys.argv)

