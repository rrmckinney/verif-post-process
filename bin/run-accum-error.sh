#!/bin/bash -l
#plot_date=`date --date="-7 days" +%y%m%d`
plot_date='230701'


conda activate verification

python3 /home/verif/verif-post-process/src/accum_error_alldays.py $plot_date



#mailx -s "accum_error log $plot_date" rmckinney@eoas.ubc.ca < /home/verif/verif-post-process/log/accum_error.log

