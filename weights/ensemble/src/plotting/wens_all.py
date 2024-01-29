
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


input_rcut30 = '/home/verif/verif-post-process/weights/ensemble/output/output-rcut30/'
input_rcut15 = '/home/verif/verif-post-process/weights/ensemble/output/output-rcut15/'
input_pwa = '/home/verif/verif-post-process/weights/ensemble/output/output-pwa/'
input_k40 = '/home/verif/verif-post-process/weights/ensemble/output/output-40/'
input_k200 = '/home/verif/verif-post-process/weights/ensemble/output/output-200/'
input_k100 = '/home/verif/verif-post-process/weights/ensemble/output/output-100/'
input_week = '/home/verif/verif-post-process/weights/sliding_window/output/weekly/'
input_month = '/home/verif/verif-post-process/weights/sliding_window/output/monthly/'

save_folder = '/home/verif/verif-post-process/weights/ensemble/imgs/img-wens-all/'

wens_type = [input_k40,input_k100,input_k200,input_pwa,input_rcut30, input_rcut15,input_week,input_month]

wens_names = ['VLF-k=40','VLF-k=100', 'VLF-k=200','IEM','RLF-rcut30', 'RLF-rcut15', 'SW-Weekly', 'SW-Monthly','SREF']

variables = ['SFCTC_KF', 'SFCWSPD_KF','PCPTOT']
variable_name = ['Temperature-KF','Wind Speed-KF', 'Hourly Precipitation']
variable_unit = ['[°C]','[km/hr]', '[mm/hr]']

stats = ['MAE', 'RMSE', 'spcorr']
stats_plot = ['MAE', 'RMSE', 'SRC']
stat_names = ['Mean Absolute Error (MAE)', 'Root Mean Square Error (RMSE)', 'Spearman Rank Correlation (SRC)']

def get_data(f, s):
            
    df = pd.read_csv(f,sep = "\s+|,")
    if s ==2:
        df.columns = ['start_date','end_date','ENS_W','w_pvalue','ENS_M','m_pvalue']
    else:
        df.columns = ['start_date','end_date','ENS_W','ENS_M']
    df['start_date'] = pd.to_datetime(df['start_date'], format='%y%m%d%H')
    mval = round(df['ENS_W'].mean(),4)
    
    return(df, mval)


v_i = 0
for v in variables:
    var_name = variable_name[v_i]
    var_unit = variable_unit[v_i]
    
    fig, ax = plt.subplots(3, figsize=(40,30))
    plt.rcParams.update({'font.size': 30})
    
    for s in range(len(stats)):
        n_i = 0
        mvals, lines = [],[]
        num_colors = len(wens_names)
        cm=plt.get_cmap('tab10')
        ax[s].set_prop_cycle(color=[cm(1.*i/num_colors) for i in range(num_colors)])
        
        for i in wens_type:
            
            f = i + stats[s] + '_' + v + '_seasonal.txt'
            df, mval = get_data(f,s)
            
            mvals.append(mval)
            
            lines += ax[s].plot(df['start_date'], df['ENS_W'])
            ax[s].set_title(stat_names[s], fontsize=40)
            ax[s].set_ylabel(var_name +" "+stats_plot[s]+" "+var_unit,fontsize=30)
            ax[s].set_xlim(pd.to_datetime('221001', format='%y%m%d'), pd.to_datetime('230930', format='%y%m%d'))
            print(i)
        
        lines += ax[s].plot(df['start_date'], df['ENS_M'])
        plt.legend(lines,wens_names,loc='upper center', bbox_to_anchor=(0.5,-0.1), ncol=3, fontsize=40)
        n_i += 1
   
    plt.savefig(save_folder+'WENS_all_'+v, bbox_inches="tight")
    
    v_i += 1
