#!/usr/bin/bash

source /home/verif/.bash_profile

conda activate verification 

cd /home/verif/verif-post-process/weights/LF/src

k=(10 40 80 100 150 200 500 1000)

for i in {0..7}
do
	for x in 'CAT_' 'MAE_' 'spcorr_' 'RMSE_'  
	do 
		python3 weights-lf2.py '211001' '221001' small ${k[$i]} $x
	done		

done
