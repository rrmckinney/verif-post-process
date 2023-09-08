import pandas as pd
import numpy as np
f = 'output/weights-seasonal/10/CAT_/weights_CSI_60hr_PCPT6_fall'
model_df_name = 'MM5NAM36*^'
weight_file = pd.read_csv(f, sep = "\s+|,", usecols=[model_df_name])

ar = pd.DataFrame([1,2,3,4,5,6])

val = weight_file.loc[1:0]

#r = [i * val for i in ar]
ar['result'] = ar * val

print(ar)
