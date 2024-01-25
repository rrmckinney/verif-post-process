import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

save_folder = '/home/verif/verif-post-process/weights/ensemble/output/ttest_output/'

input_rcut30 = '/home/verif/verif-post-process/weights/ensemble/output/output-rcut30/'
input_rcut15 = '/home/verif/verif-post-process/weights/ensemble/output/output-rcut15/'
input_pwa = '/home/verif/verif-post-process/weights/ensemble/output/output-pwa/'
input_k40 = '/home/verif/verif-post-process/weights/ensemble/output/output-40/'
input_k200 = '/home/verif/verif-post-process/weights/ensemble/output/output-200/'
input_k100 = '/home/verif/verif-post-process/weights/ensemble/output/output-100/'
input_week = '/home/verif/verif-post-process/weights/sliding_window/output/weekly/'
input_month = '/home/verif/verif-post-process/weights/sliding_window/output/monthly/'

wens_type = [input_k40,input_k100,input_k200,input_pwa,input_rcut30, input_rcut15,input_week,input_month]

wens_f = ['k40','k100','k200','pwa','rcut30','rcut15','sw_week','sw_month']

wens_names = ['VLF-k=40','VLF-k=100', 'VLF-k=200','IEM','RLF-rcut30', 'RLF-rcut15', 'SW-Weekly', 'SW-Monthly','SREF']

variables = ['SFCTC', 'SFCTC_KF', 'SFCWSPD','SFCWSPD_KF','PCPTOT']
variable_name = ['Temperature-Raw','Temperature-KF', 'Wind Speed-Raw','Wind Speed-KF', 'Hourly Precipitation']
variable_unit = ['[C]','[C]','[km/hr]', '[km/hr]', '[mm/hr]']

#stat = ['MAE', 'RMSE', 'spcorr']
stat = ['MAE','RMSE']
stat_names = ['Mean Absolute Error (MAE)', 'Root Mean Square Error (RMSE)']
#stat_names = ['Mean Absolute Error (MAE)', 'Root Mean Square Error (RMSE)', 'Spearman Rank Correlation (spcorr)']


def ttest(f, s,i,v ):

    df = pd.read_csv(f,sep = "\s+|,")
    if s ==2:
        df.columns = ['start_date','end_date','ENS_W','w_pvalue','ENS_M','m_pvalue']
    else:
        df.columns = ['start_date','end_date','ENS_W','ENS_M']
    
    df['start_date'] = pd.to_datetime(df['start_date'], format='%y%m%d%H')
    '''
    for d in range(len(df.start_date)):
        print(df.ENS_W[d])
        print(df.ENS_M[d])
        print(df.start_date[d])
    '''
    ttest_res = stats.ttest_ind(df.ENS_W, df.ENS_M)

    ttest_file = open(save_folder + "ttest_"+wens_f[i]+"_"+v+stat[s]+"_results.txt", 'w')
    ttest_file.write(str(df.start_date[0]) + " ")
    ttest_file.write("%3.3f " % (ttest_res.statistic) + " ")
    ttest_file.write("%3.3f " % (ttest_res.pvalue) + "\n")
    ttest_file.close()

    return(df)

v_i = 0
for v in variables:
    var_name = variable_name[v_i]
    var_unit = variable_unit[v_i]
    
    if 'PCPT' not in v:
        continue
    
    fig, ax = plt.subplots(len(stat), figsize=(15,10), sharex=True)
    plt.rcParams.update({'font.size': 16})
    
    for s in range(len(stat)):
        data = []
        
        for i in range(len(wens_type)):
            f = wens_type[i] + stat[s] + '_' + v + '_seasonal.txt'
            df = ttest(f,s,i,v)
            df = df.dropna()
            data.append(df['ENS_W'])
        
        data.append(df.ENS_M) 
        ax[s].boxplot(data)
        
        plt.xticks(ticks=[1,2,3,4,5,6,7,8,9], labels=wens_names, rotation=45, fontsize=14)
        ax[s].set_title(stat_names[s], fontsize=14)
        ax[s].set_ylabel(stat[s] + ' '+ var_name+' ' + var_unit, fontsize=14)

    plt.savefig(save_folder + 'boxplots_' +v)
    v_i += 1
