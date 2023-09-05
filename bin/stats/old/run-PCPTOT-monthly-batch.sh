#running on Sundays, this should always be for Sunday-Saturday (7 days)
  
source /home/verif/.bash_profile

#start_date=`date --date="-14 days" +%y%m%d`
#end_date=`date --date="-8 days" +%y%m%d`

conda activate verification

cd /home/verif/verif-post-process/src/

start_date=('220401' '220501' '220601' '220701' '220801' '220901' '221001' '221101' '221201')
end_date=('220430' '220531' '220630' '220731' '220831' '220930' '221031' '221130' '221231')

for i in {0..9}
do

        python3 leaderboard-txt-sqlite2-monthly.py ${start_date[$i]} ${end_date[$i]} PCPTOT small > log/lb_txt_PCPTOT_sm.log

        python3 leaderboard-txt-sqlite2-monthly.py ${start_date[$i]} ${end_date[$i]} PCPTOT large > log/lb_txt_PCPTOT_lrg.log

done
