
source /home/verif/.bash_profile

#start_date=`date --date="-14 days" +%y%m%d`
#end_date=`date --date="-8 days" +%y%m%d`

conda activate verification

cd /home/verif/verif-post-process/src/

start_date='230811'
end_date='230817'
:q


#python3 leaderboards-txt-sqlite2.py $start_date $end_date SFCTC small > log/lb_txt_SFCTC_sm.log
#python3 leaderboards-txt-sqlite2.py $start_date $end_date SFCTC_KF small > log/lb_txt_SFCTC_KF_sm.log
#python3 leaderboards-txt-sqlite2.py $start_date $end_date SFCWSPD small > log/lb_txt_SFCWSPD_sm.log
python3 leaderboards-txt-sqlite2.py $start_date $end_date SFCWSPD_KF small > log/lb_txt_SFCWSPD_KF_sm.logP
#python3 leaderboards-txt-sqlite2.py $start_date $end_date PCPTOT small > log/lb_txt_PCPTOT_sm.log

#python3 leaderboards-txt-sqlite2.py $start_date $end_date SFCTC large > log/lb_txt_SFCTC_lrg.log
#python3 leaderboards-txt-sqlite2.py $start_date $end_date SFCTC_KF large > log/lb_txt_SFCTC_KF_lrg.log
#python3 leaderboards-txt-sqlite2.py $start_date $end_date SFCWSPD large > log/lb_txt_SFCWSPD_lrg.log
python3 leaderboards-txt-sqlite2.py $start_date $end_date SFCWSPD_KF large > log/lb_txt_SFCWSPD_KF_lrg.log
#python3 leaderboards-txt-sqlite2.py $start_date $end_date PCPTOT large > log/lb_txt_PCPTOT_lrg.log

