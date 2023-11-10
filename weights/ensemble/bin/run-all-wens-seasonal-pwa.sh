#!/bin/bash -l
start_date=('22101600' '22111600' '22121600' '23011600' '23021600' '23031600' '23041600' '23051600' '23061600' '23071600' '23081600' '23091600' '23101600')
end_date=('22101812' '22111812' '22121812' '23011812' '23021812' '23031812' '23041812' '23051812' '23061812' '23071812' '23081812' '23091812' '23101812')
var='PCPTOT'
domain='small'
weight_type='seasonal'
stat_type='CAT_'
time_domain='60hr'
stat_cat='NA'

source /home/verif/.bash_profile
conda activate verification

cd /home/verif/verif-post-process/weights/ensemble/src

for x in  'CAT_'
do 
	if [ "$x" = "$stat_type" ]
	then
		for s in 'POD' 'POFD' 'PSS' 'HSS' 'CSI' 'GSS'
		do
			for v in 'PCPTOT' 'SFCTC' 'SFCTC_KF' 'SFCWSPD' 'SFCWSPD_KF' 'PCPT6'
			do
				for i in {0..12}
				do
					python3	mk_weighted_ensemble_pwa.py ${start_date[$i]} ${end_date[$i]} $v $domain $weight_type $x $time_domain $s
				done
			done
		done
	else
		for v in 'PCPTOT' 'SFCTC' 'SFCTC_KF' 'SFCWSPD' 'SFCWSPD_KF' 'PCPT6'
		do
			for i in {0..12}
			do
			python3 mk_weighted_ensemble_pwa.py ${start_date[$i]} ${end_date[$i]} $v $domain $weight_type $x $time_domain 'NA'
			done
		done
	fi
done

