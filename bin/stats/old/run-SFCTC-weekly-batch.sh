#running on Sundays, this should always be for Sunday-Saturday (7 days)
  
source /home/verif/.bash_profile

#start_date=`date --date="-14 days" +%y%m%d`
#end_date=`date --date="-8 days" +%y%m%d`

conda activate verification

cd /home/verif/verif-post-process/src/

start_date='220415'
end_date='220421'

while [ $((start_date)) -lt `date +"%y%m%d"` ] 
do

        python3 leaderboards-txt-sqlite2.py $start_date $end_date SFCTC small > log/lb_txt_SFCTC_sm.log

        python3 leaderboards-txt-sqlite2.py $start_date $end_date SFCTC large > log/lb_txt_SFCTC_lrg.log

	start_date=$(date -d $start_date"+7 days" +%y%m%d)
	end_date=$(date -d $end_date"+7 days" +%y%m%d)
done