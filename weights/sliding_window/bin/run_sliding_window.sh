#!/bin/bash -l
start_date='211001'
end_date='211003'
domain='small'
weight_type='MAE'
time_domain='60hr'
window_type='weekly'

source /home/verif/.bash_profile
conda activate verification

cd /home/verif/verif-post-process/weights/sliding_window/src

while [ $((start_date)) -lt `date --date="7 days ago" +"%y%m%d"` ]
do
	for v in 'PCPTOT' 'SFCTC' 'SFCTC_KF' 'SFCWSPD' 'SFCWSPD_KF'
	do	

	 	echo python3 sliding_window.py ${start_date[$i]}00 ${end_date[$i]}12 $window_type $v $time_domain $weight_type
		
		python3 sliding_window.py ${start_date[$i]}00 ${end_date[$i]}12 $window_type $v $time_domain $weight_type
	done	
	start_date=$(date -d $start_date"+7 days" +%y%m%d)
        end_date=$(date -d $end_date"+7days" +%y%m%d)
done
