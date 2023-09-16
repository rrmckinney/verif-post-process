
source /home/verif/.bash_profile

#start_date=`date --date="-14 days" +%y%m%d`
#end_date=`date --date="-8 days" +%y%m%d`

conda activate verification

cd /home/verif/verif-post-process/src/

start_date='230804'
end_date='230810'


python3 leaderboards-txt-sqlite2.py $start_date $end_date SFCTC_KF small > log/lb_txt_SFCTC_KF_sm.log

python3 leaderboards-txt-sqlite2.py $start_date $end_date SFCTC_KF large > log/lb_txt_SFCTC_KF_lrg.log

