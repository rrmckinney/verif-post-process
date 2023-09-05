#running on Sundays, this should always be for Sunday-Saturday (7 days)
  
source /home/verif/.bash_profile

#start_date=`date --date="-14 days" +%y%m%d`
#end_date=`date --date="-8 days" +%y%m%d`

conda activate verification

cd /home/verif/verif-post-process/src/

start_date=('211101' '211201' '220101' '220201' '220301' 220401' 220501' 220601' '220701' '220801' '220901' 221001' '221101' '221201' '230101' '230201' '230301' '230401' '230501' '230601' '230701')
end_date=('211130' '211231' '220131' '220228' '220331' 220430' 220531' 220630' '220731' '220831' '220930' 221031' '221130' '221231' '230131' '230228' '230331' '230430' '230531' '230630' '230731')

for i in {0..20}
do

        python3 leaderboard-txt-sqlite2-monthly.py ${start_date[$i]} ${end_date[$i]} SFCTC small > log/lb_txt_SFCTC_sm.log

        python3 leaderboard-txt-sqlite2-monthly.py ${start_date[$i]} ${end_date[$i]} SFCTC large > log/lb_txt_SFCTC_lrg.log

done
