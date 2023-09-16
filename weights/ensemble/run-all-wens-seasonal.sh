#!/bin/bash -l
start_date='211001'
end_date='221001'
var='PCPTOT'
domain='small'
weight_type='seasonal'
stat_type='MAE_'
k=100
time_domain='60hr'
stat_cat='PSS'

source /home/verif/.bash_profile
conda activate verification

cd /home/verif/verif-post-process/weights/ensemble


python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain $weight_type $stat_type $k $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal MAE_ $k $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal MAE_ $k $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal MAE_ $k $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal MAE_ $k $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal MAE_ $k $time_domain NA

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain seasonal spcorr_ $k $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal spcorr_ $k $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal spcorr_ $k $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal spcorr_ $k $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal spcorr_ $k $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal spcorr_ $k $time_domain NA

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain seasonal RMSE_ $k $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal RMSE_ $k $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal RMSE_ $k $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal RMSE_ $k $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal RMSE_ $k $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal RMSE_ $k $time_domain NA

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain seasonal CAT_ $k $time_domain POD
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal CAT_ $k $time_domain POD
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal CAT_ $k $time_domain POD
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal CAT_ $k $time_domain POD
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal CAT_ $k $time_domain POD
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal CAT_ $k $time_domain POD

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain seasonal CAT_ $k $time_domain POFD
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal CAT_ $k $time_domain POFD
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal CAT_ $k $time_domain POFD
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal CAT_ $k $time_domain POFD
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal CAT_ $k $time_domain POFD
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal CAT_ $k $time_domain POFD

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain seasonal CAT_ $k $time_domain PSS
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal CAT_ $k $time_domain PSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal CAT_ $k $time_domain PSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal CAT_ $k $time_domain PSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal CAT_ $k $time_domain PSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal CAT_ $k $time_domain PSS

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain seasonal CAT_ $k $time_domain HSS
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal CAT_ $k $time_domain HSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal CAT_ $k $time_domain HSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal CAT_ $k $time_domain HSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal CAT_ $k $time_domain HSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal CAT_ $k $time_domain HSS

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain seasonal CAT_ $k $time_domain GSS
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal CAT_ $k $time_domain GSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal CAT_ $k $time_domain GSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal CAT_ $k $time_domain GSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal CAT_ $k $time_domain GSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal CAT_ $k $time_domain GSS

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain seasonal CAT_ $k $time_domain CSI
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal CAT_ $k $time_domain CSI
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal CAT_ $k $time_domain CSI
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal CAT_ $k $time_domain CSI
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal CAT_ $k $time_domain CSI
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal CAT_ $k $time_domain CSI

