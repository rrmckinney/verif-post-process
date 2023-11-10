This folder houses all the code that runs the verification and plotting for the https://weather.eos.ubc.ca/wxfcst/verification/

# BIN

This folder is the executed code for the website stats and plots. ONLY the Bash scripts in this folder should be run
operationally. 

within this folder you will find: 

**run-time-series.sh** : updates the time series plot for each model on the website requires more than two weeks of data to run. cron has this run on the 11th of each month.
**run-meteograms.sh** : creates meteograms for the UBC rooftop station for the different initialization times and variables. cron has this run every day at 2300 server time.

## stats
**run-cont-weekly.sh** : calculates the stats for each week for all variables. cron has this running every Sunday for the previous Friday-Thurs
**run-cont-monthly.sh** : calculates the stats for each month for all variables.cron has this running the 7th of every month for the previous month 
					
**run-cat-weekly.sh** : NOT OPERATIONAL. can be run if you want categorial stats for wind and precip variables
**run-cat-monthly.sh** : NOT OPERATIONAL. can be run if you want categorial stats for wind and precip variables

## plotting
**run-plot-weekly.sh** : runs the plots for each week and all variables. can only be run for a week AFTER the stats have been calculated. cron has this running every tues for the following Friday-Thurs.
**run-plot-monthly.sh** : runs the plots for each month and all variables. can only be run for a month AFTER the stats have been calculated. cron has this running every 10th of each month for the previous month. 

**run-catplot-weekly.sh** : NOT OPERATIONAL. can be run if you want categorial stats for wind and precip variables
**run-catplot-monthly.sh** : NOT OPERATIONAL. can be run if you want categorial stats for wind and precip variables


# input

This folder is all the input for the src files. It houses lists of the all the models and stations. As well as what 
variables and other characteristics each station and model holds.

# qc

This is the quality check folder. Currenlty has a script that examines the distributions of the obs data at all stations.
This script was used to manually examine the data before implementing qc in the operational scripts. It is not used operationally

#src

this is where all the source code run for the BIN are located.

**leaderboards-txt-sqlite2.py** : main code for running the continuous stats (MAE, RMSE, correlation. relies on utl/funcs.py for all its functions. 
**precip_wind_verif.py** : NOT OPERATIONAL. main code for the categorical stats (POD, POFD, PSS, HSS, CSI, GSS). relies on cat_funcs.py for its fucntions. 

**leaderboards-plots.py** : main code for running the plots of the continuous stats. does not have a fucntion script.
**leaderboard-avg-ranking.py** : main code for the rankings plots on the website for continuous stats. does not have a function script.
**categorical-plots.py** : NOT OPERATIONAL. main code for running the plots of the categorical stats. does not have a fucntion script.


**ibcs_meteograms.py** : main code for the ibcs plots on the website. does not have a fucntion script.
**meteograms.py** : runs the station=3510 meteograms for the website. does not have a function script.
**time_series.py** : runs the time series plot for station=3510 for the website. does not have a function script. 
**accum_error_alldays.py** : NOT OPERATIONAL. main code for running the accumulated error. does not have a function script.


 
