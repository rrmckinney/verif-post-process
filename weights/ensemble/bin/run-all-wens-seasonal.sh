#!/bin/bash -l
#start_date=('22101600' '22111600' '22121600' '23011600' '23021600' '23031600' '23041600' '23051600' '23061600' '23071600' '23081600' '23091600' '23101600')
#end_date=('22101812' '22111812' '22121812' '23011812' '23021812' '23031812' '23041812' '23051812' '23061812' '23071812' '23081812' '23091812' '23101812')
#var='PCPTOT'
start_date='221001'
end_date='221003'
domain='small'
weight_type='seasonal'
k=100
time_domain='60hr'



source /home/verif/.bash_profile
conda activate verification

cd /home/verif/verif-post-process/weights/ensemble/src

while [ $((start_date)) -lt `date --date="7 days ago" +"%y%m%d"` ]
do
	for v in 'PCPTOT' 'SFCTC' 'SFCTC_KF' 'SFCWSPD' 'SFCWSPD_KF'
	do	

	 	echo ${start_date[$i]}	
		python3 mk_weighted_ensemble.py ${start_date[$i]}00 ${end_date[$i]}12 $v $domain $weight_type $x $time_domain $s
	done	
	start_date=$(date -d $start_date"+7 days" +%y%m%d)
        end_date=$(date -d $end_date"+7days" +%y%m%d)
done
