#!/bin/bash -l
start_date='211001'
end_date='221001'
var='PCPTOT'
domain='small'
weight_type='yearly'
stat_type='MAE_'
time_domain='60hr'
stat_cat='PSS'

source /home/verif/.bash_profile
conda activate verification

cd /home/verif/verif-post-process/weights/ensemble/src


python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain $weight_type $stat_type $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain yearly MAE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain yearly MAE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain yearly MAE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain yearly MAE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain yearly MAE_ $time_domain NA

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain yearly spcorr_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain yearly spcorr_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain yearly spcorr_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain yearly spcorr_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain yearly spcorr_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain yearly spcorr_ $time_domain NA

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain yearly RMSE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain yearly RMSE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain yearly RMSE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain yearly RMSE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain yearly RMSE_ $time_domain NA
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain yearly RMSE_ $time_domain NA

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain yearly CAT_ $time_domain POD
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain yearly CAT_ $time_domain POD
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain yearly CAT_ $time_domain POD
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain yearly CAT_ $time_domain POD
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain yearly CAT_ $time_domain POD
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain yearly CAT_ $time_domain POD

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain yearly CAT_ $time_domain POFD
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain yearly CAT_ $time_domain POFD
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain yearly CAT_ $time_domain POFD
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain yearly CAT_ $time_domain POFD
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain yearly CAT_ $time_domain POFD
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain yearly CAT_ $time_domain POFD

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain yearly CAT_ $time_domain PSS
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain yearly CAT_ $time_domain PSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain yearly CAT_ $time_domain PSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain yearly CAT_ $time_domain PSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain yearly CAT_ $time_domain PSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain yearly CAT_ $time_domain PSS

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain yearly CAT_ $time_domain HSS
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain yearly CAT_ $time_domain HSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain yearly CAT_ $time_domain HSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain yearly CAT_ $time_domain HSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain yearly CAT_ $time_domain HSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain yearly CAT_ $time_domain HSS

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain yearly CAT_ $time_domain GSS
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain yearly CAT_ $time_domain GSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain yearly CAT_ $time_domain GSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain yearly CAT_ $time_domain GSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain yearly CAT_ $time_domain GSS
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain yearly CAT_ $time_domain GSS

python3 mk_weighted_ensemble.py $start_date $end_date PCPTOT $domain yearly CAT_ $time_domain CSI
python3 mk_weighted_ensemble.py $start_date $end_date PCPT6 $domain yearly CAT_ $time_domain CSI
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC $domain yearly CAT_ $time_domain CSI
python3 mk_weighted_ensemble.py $start_date $end_date SFCTC_KF $domain yearly CAT_ $time_domain CSI
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD $domain yearly CAT_ $time_domain CSI
python3 mk_weighted_ensemble.py $start_date $end_date SFCWSPD_KF $domain yearly CAT_ $time_domain CSI


