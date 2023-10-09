#!/bin/bash -l
start_date='211001'
end_date='221001'
var='PCPTOT'
domain='small'
weight_type='yearly'
stat_type='MAE_'
k=100
time_domain='60hr'
stat_cat='PSS'

source /home/verif/.bash_profile
conda activate verification

cd /home/verif/verif-post-process/weights/ensemble/src

for x in 'MAE_' 'RMSE_' 'spcorr_' 'CAT_'
do	
    if [x = 'CAT_']
    do
        for s in 'POD' 'POFD' 'PSS' 'HSS' 'CSI' 'GSS'
        do
            for v in 'PCPTOT' 'SFCTC' 'SFCTC_KF' 'SFCWSPD' 'SFCWSPD_KF' 'PCPT6'
            do 
            python3 mk_weighted_ensemble.py $start_date $end_date $v $domain $weight_type $x $k $time_domain $s
            done
        done
    done
    else
    do
        for v in 'PCPTOT' 'SFCTC' 'SFCTC_KF' 'SFCWSPD' 'SFCWSPD_KF' 'PCPT6'
        do 
            stat_cat='NA'
            python3 mk_weighted_ensemble.py $start_date $end_date $v $domain $weight_type $x $k $time_domain $stat_cat
        done
    done
done
