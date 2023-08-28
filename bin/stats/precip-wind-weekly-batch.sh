#running on Sundays, this should always be for Sunday-Saturday (7 days)

source /home/verif/.bash_profile

#start_date=`date --date="-14 days" +%y%m%d`
#end_date=`date --date="-8 days" +%y%m%d`

conda activate verification

cd /home/verif/verif-post-process/src/

start_date='230729'
end_date='230804'

while [ $((start_date)) -lt `date  +"%y%m%d"` ]
do 
	python3 precip_wind_verif.py $start_date $end_date SFCWSPD small > log/lb_txt_SFCWSPD_sm.log
	python3 precip_wind_verif.py $start_date $end_date SFCWSPD_KF small > log/lb_txt_SFCWSPD_KF_sm.log
	python3 precip_wind_verif.py $start_date $end_date PCPTOT small > log/lb_txt_PCPTOT_sm.log 
	python3 precip_wind_verif.py $start_date $end_date PCPT6 small > log/lb_txt_PCPT6_sm.log

	start_date=$(date -d $start_date"+7 days" +%y%m%d)
        end_date=$(date -d $end_date"+7 days" +%y%m%d)

done
