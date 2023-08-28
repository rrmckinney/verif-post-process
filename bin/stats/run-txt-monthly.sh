source /home/verif/.bash_profile

#start_date=`date --date="-1 months -7 days" +%y%m%d`
#end_date=`date --date="-8 days" +%y%m%d`

conda activate verification

cd /home/verif/verif-post-process/src/

start_date='211001'
end_date='211031'

python3 leaderboard-txt-sqlite2-monthly.py $start_date $end_date SFCTC_KF large > log/lb_txt_SFCTC_KF_lrg_monthly.log

python3 leaderboard-txt-sqlite2-monthly.py $start_date $end_date SFCTC_KF small > log/lb_txt_SFCTC_KF_sm_monthly.log

