#!/bin/bash -l
start_date='221001'
end_date='221003'
domain='small'
weight_type='MAE'
time_domain='60hr'
window_type='monthly'

#station=( '397' '404' '400' '2900' '403' '413' '395' '424' 442' 594' '415' '416' '444' '3548' '2793' '426' '3545' '3591' '3599' '617' '412' '2631' '447' '645' '417' '410' '3576' '3341' '2014' '681' '392' '3522' '407' '635' '2061' '401' '2104' '582' '3558' '396' '615' '641' '654' '649' '3557' '3559' '593' '3560' '650' '399' '671' '2632' '3561' '657' '626' '655' '419' '420' '398' '579' '3567' '2738' '3510' '428' '628' '411' '597' '3569' '2157' '638' '598' '676' '673' '674' '440')

source /home/verif/.bash_profile
conda activate verification

cd /home/verif/verif-post-process/weights/sliding_window/src

#while [ $((start_date)) -lt `date --date="7 days ago" +"%y%m%d"` ]
while [ $((start_date)) -lt 230930 ]
do
	for w in 'weekly' 'monthly'		
#	for t  in '400' '2900' '403' '413' '395' '424' 442' 594' '415' '416' '444' '3548' '2793' '426' '3545' '3591' '3599' '617' '412' '2631' '447' '645' '417' '410' '3576' '3341' '2014' '681' '392' '3522' '407' '635' '2061' '401' '2104' '582' '3558' '396' '615' '641' '654' '649' '3557' '3559' '593' '3560' '650' '399' '671' '2632' '3561' '657' '626' '655' '419' '420' '398' '579' '3567' '2738' '3510' '428' '628' '411' '597' '3569' '2157' '638' '598' '676' '673' '674' '440'
	do
		for v in 'PCPTOT' 'SFCTC_KF' 'SFCWSPD_KF'
		do	

	 		echo python3 sliding_window.py ${start_date[$i]}00 ${end_date[$i]}12 $window_type $v $time_domain $weight_type $t
		
			python3 sliding_window.py ${start_date[$i]}00 ${end_date[$i]}12 $w $v $time_domain $weight_type '3510'
		done	
	done
       		start_date=$(date -d $start_date"+7 days" +%y%m%d)
       		end_date=$(date -d $end_date"+7 days" +%y%m%d)
done
