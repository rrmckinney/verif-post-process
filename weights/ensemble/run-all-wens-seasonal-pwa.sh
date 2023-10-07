#!/bin/bash -l
start_date='211001'
end_date='221001'
var='PCPTOT'
domain='small'
weight_type='seasonal'
stat_type='MAE_'
time_domain='60hr'
stat_cat='PSS'

source /home/verif/.bash_profile
conda activate verification

cd /home/verif/verif-post-process/weights/ensemble


python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain $weight_type $stat_type $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal MAE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal MAE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal MAE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal MAE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal MAE_ $time_domain NA

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain seasonal spcorr_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal spcorr_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal spcorr_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal spcorr_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal spcorr_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal spcorr_ $time_domain NA

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain seasonal RMSE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal RMSE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal RMSE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal RMSE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal RMSE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal RMSE_ $time_domain NA

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain seasonal CAT_ $time_domain POD
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal CAT_ $time_domain POD
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal CAT_ $time_domain POD
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal CAT_ $time_domain POD
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal CAT_ $time_domain POD
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal CAT_ $time_domain POD

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain seasonal CAT_ $time_domain POFD
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal CAT_ $time_domain POFD
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal CAT_ $time_domain POFD
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal CAT_ $time_domain POFD
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal CAT_ $time_domain POFD
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal CAT_ $time_domain POFD

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain seasonal CAT_ $time_domain PSS
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal CAT_ $time_domain PSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal CAT_ $time_domain PSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal CAT_ $time_domain PSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal CAT_ $time_domain PSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal CAT_ $time_domain PSS

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain seasonal CAT_ $time_domain HSS
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal CAT_ $time_domain HSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal CAT_ $time_domain HSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal CAT_ $time_domain HSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal CAT_ $time_domain HSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal CAT_ $time_domain HSS

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain seasonal CAT_ $time_domain GSS
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal CAT_ $time_domain GSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal CAT_ $time_domain GSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal CAT_ $time_domain GSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal CAT_ $time_domain GSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal CAT_ $time_domain GSS

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain seasonal CAT_ $time_domain CSI
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain seasonal CAT_ $time_domain CSI
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain seasonal CAT_ $time_domain CSI
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain seasonal CAT_ $time_domain CSI
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain seasonal CAT_ $time_domain CSI
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain seasonal CAT_ $time_domain CSI

