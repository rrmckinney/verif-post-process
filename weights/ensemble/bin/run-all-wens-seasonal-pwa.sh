#!/bin/bash -l
#start_date=('22101600' '22111600' '22121600' '23011600' '23021600' '23031600' '23041600' '23051600' '23061600' '23071600' '23081600' '23091600' '23101600')
#end_date=('22101812' '22111812' '22121812' '23011812' '23021812' '23031812' '23041812' '23051812' '23061812' '23071812' '23081812' '23091812' '23101812')
#var='PCPTOT'
start_date='230610'
end_date='230612'
domain='small'
weight_type='seasonal'
k=100
time_domain='60hr'
x='CAT_'
s='PSS'


source /home/verif/.bash_profile
conda activate verification

cd /home/verif/verif-post-process/weights/ensemble/src

#while [ $((start_date)) -lt `date --date="7 days ago" +"%y%m%d"` ]
while [ $((start_date)) -lt 231101 ]
do
	
	for st in '403' '413' '395' '424' 442' 594' '415' '416' '444' '3548' '2793' '426' '3545' '3591' '3599' '617' '412' '2631' '447' '645' '417' '410' '3576' '3341' '2014' '681' '392' '3522' '407' '635' '2061' '401' '2104' '582' '3558' '396' '615' '641' '654' '649' '3557' '3559' '593' '3560' '650' '399' '671' '2632' '3561' '657' '626' '655' '419' '420' '398' '579' '3567' '2738' '3510' '428' '628' '411' '597' '3569' '2157' '638' '598' '676' '673' '674' '440'
	do
	
		for v in 'PCPTOT' 'SFCWSPD_KF'
		do	

	 		echo ${start_date[$i]}	
			python3 mk_weighted_ensemble_pwa.py ${start_date[$i]}00 ${end_date[$i]}12 $v $domain $weight_type $x $time_domain $s $st
		done	
	done
	start_date=$(date -d $start_date"+7 days" +%y%m%d)
        end_date=$(date -d $end_date"+7days" +%y%m%d)
done
