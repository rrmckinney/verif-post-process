source /home/verif/.bash_profile

#start_date=`date --date="-1 months -8" +%y%m%d`
#end_date=`date --date="-9 days" +%y%m%d`
start_date='230701'
end_date='230731'

conda activate verification

cd /home/verif/verif-post-process/src/


python3 leaderboards-plots.py ${start_date[$i]} ${end_date[$i]} small > log/lb_plots_sm_monthly.log
python3 leaderboards-plots.py ${start_date[$i]} ${end_date[$i]} large > log/lb_plots_lrg_monthly.log
python3 leaderboard-avg-ranking.py monthly small > log/lb_avg_ranking_sm_monthly.log
python3 leaderboard-avg-ranking.py monthly large > log/lb_avg_ranking_lrg_monthly.log


