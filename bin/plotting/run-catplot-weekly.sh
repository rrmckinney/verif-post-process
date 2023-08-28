source /home/verif/.bash_profile

#start_date=`date --date="-15 days" +%y%m%d`
#end_date=`date --date="-9 days" +%y%m%d`

start_date='211015'
end_date='211021'

conda activate verification

cd /home/verif/verif-post-process/src/

while [ $((start_date)) -lt 230731 ] 
do

	python3 categorical-plots.py $start_date $end_date small > log/lb_plots_sm.log
	#python3 categorical-plots.py $start_date $end_date large > log/lb_plots_lrg.log
	#python3 leaderboard-avg-ranking.py weekly small > log/lb_avg_ranking_sm.log
	#python3 leaderboard-avg-ranking.py weekly large > log/lb_avg_ranking_lrg.log
	
	start_date=$(date -d $start_date"+7 days" +%y%m%d)
	end_date=$(date -d $end_date"+7 days" +%y%m%d)
done
