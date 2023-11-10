#!/bin/bash -l
start_date='211015' #should not change, first day of stats calcs; must be the first of the month
end_date=`date -d "-6 days" +%y%m%d`
#end_date='231102'
#echo $end_date
source /home/verif/.bash_profile

conda activate verification

cd /home/verif/verif-post-process/src

#python3 time_series.py $start_date $end_date weekly small
#python3 time_series.py $start_date $end_date weekly large

#monthly date must start and end on first/end of month, so different end date given here
start_month='211001'
DATE=`date +%y%m%d`
day=`date '+%d'`	
echo $(day)
end_month=$(date +%y%m%d -d "$DATE -8 days")
echo $start_month
echo $end_month
python3 time_series.py $start_month $end_month monthly small
python3 time_series.py $start_month $end_month monthly large

	
