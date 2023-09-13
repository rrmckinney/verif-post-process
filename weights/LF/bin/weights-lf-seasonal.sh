#!/usr/bin/bash

source /home/verif/.bash_profile

conda activate verification 

cd /home/verif/verif-post-process/weights/LF/src

k=(10 40 80 100 150 200 500 1000)

for i in {0..7}
do	
        for x in 'CAT_' 
	do	
		python3 weights-lf-seasonal.py '211001' '221001' small ${k[$i]} $x
	done
done
