#!/bin/bash -l
start_date='211008' #should not change, first day of stats calcs
#end_date=`date --date"-14 days" +%y%m%d`
end_date='230907'

source /home/verif/.bash_profile

conda activate verification

cd /home/verif/verif-post-process/src

python3 time_series.py $start_date $end_date weekly small
python3 time_series.py $start_date $end_date weekly large
#python3 time_series.py $start_date $end_date monthly small
#python3 time_series.py $start_date $end_date weekly large
