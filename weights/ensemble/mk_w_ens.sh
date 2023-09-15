#!/bin/bash -l
start_date='211001'
end_date='221001'
var='PCPT6'
domain='small'
weight_type='seasonal'
stat_type='CAT_'
k=100
time_domain='60hr'
stat_cat='PSS'

source /home/verif/.bash_profile
conda activate verification

cd /home/verif/verif-post-process/weights/ensemble


python3 mk_weighted_ensemble.py $start_date $end_date $var $domain $weight_type $stat_type $k $time_domain $stat_cat

