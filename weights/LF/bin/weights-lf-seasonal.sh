#!/usr/bin/bash

source /home/verif/.bash_profile

conda activate verification 

cd /home/verif/verif-post-process/weights/LF/src

k=(200)

for i in {0..1}
do	
        for x in 'CAT_' 
	do	
		python3 weights-seasonal-lf.py '211001' '221001' small ${k[$i]}
	done
done
