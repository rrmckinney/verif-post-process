#running on Sundays, this should always be for Sunday-Saturday (7 days)

source /home/verif/.bash_profile

#start_date=`date --date="-14 days" +%y%m%d`
#end_date=`date --date="-8 days" +%y%m%d`

conda activate verification

cd /home/verif/verif-post-process/src/

start_date='230728'
end_date='230803'

while [ $((start_date)) -lt 230813 ]
do
	python3 precip_wind_verif.py $start_date $end_date PCPT6 small > log/lb_txt_PCPT6_sm.log
 	python3 precip_wind_verif.py $start_date $end_date PCPT6 large > log/lb_txt_PCPT6_lrg.log	
	start_date=$(date -d $start_date"+7 days" +%y%m%d)
        end_date=$(date -d $end_date"+7 days" +%y%m%d)
done
