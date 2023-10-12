source /home/verif/.bash_profile

#start_date=`date --date="-1 months -7 days" +%y%m%d`
#end_date=`date --date="-7 days" +%y%m%d`

start_date='230819'
end_date='230825'
d='small'

conda activate verification

cd /home/verif/verif-post-process/src/

for v in PCPTOT PCPT6 SFCWSPD SFCWSPD_KF
do
	python3 precip_wind_verif.py $start_date $end_date $v $d > log/cat.log
	
done
