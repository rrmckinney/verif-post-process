
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

#wens_type = [input_k40,input_k100,input_k200,input_pwa,input_rcut30, input_rcut15,input_week,input_month]

wens_type = [input_k40,input_k100,input_k200,input_rcut30, input_rcut15,input_week,input_month]

#wens_names = ['VLF-k=40','VLF-k=100', 'VLF-k=200','IEM','RLF-rcut30', 'RLF-rcut15', 'Sliding Window-Weekly', 'Sliding Window-Monthly','SREF']
wens_names = ['VLF-k=40','VLF-k=100', 'VLF-k=200','RLF-rcut30', 'RLF-rcut15', 'Sliding Window-Weekly', 'Sliding Window-Monthly','SREF','Observations']

variables = [ 'SFCTC_KF','SFCWSPD_KF','PCPTOT']
variable_name = ['Temperature-KF', 'Wind Speed-KF', 'Hourly Precipitation']
variable_unit = ['[°C]', '[km/hr]', '[mm/hr]']
'''
variables = [ 'SFCWSPD_KF','PCPTOT']
variable_name = [ 'Wind Speed-KF', 'Hourly Precipitation']
variable_unit = [ '[km/hr]', '[mm/hr]']
'''
stats = ['MAE', 'RMSE', 'spcorr']
stat_names = ['Mean Absolute Error (MAE)', 'Root Mean Square Error (RMSE)', 'Spearman Rank Correlation (spcorr)']

def get_data(f):
    
    df = pd.read_csv(f,sep = ",")
    df.columns = ['start_date','ENS_W','obs','ENS_M']
    df['start_date'] = pd.to_datetime(df['start_date'], format='%Y-%m-%d %H:%M:%S')
    print(df)
    #mval = round(df['ENS_W'].mean(),4)
    
    return(df)


v_i = 0
for v in variables:
    var_name = variable_name[v_i]
    var_unit = variable_unit[v_i]
    
    fig, ax = plt.subplots(1, figsize=(40,15))
    plt.rcParams.update({'font.size': 20})
    
    lines = []
    num_colors = len(wens_names)
    cm=plt.get_cmap('tab10')
    ax.set_prop_cycle(color=[cm(1.*i/num_colors) for i in range(num_colors)])
        
    for i in wens_type:       
        print(i) 
        f = i +  'ENSW_' + v + '.txt'
        df = get_data(f)
            
        lines += ax.plot(df['start_date'], df['ENS_W'])
    
    ax.set_ylabel(var_name +" "+var_unit, fontsize=22)
    ax.set_xlabel('Date',fontsize=22)
    lines += ax.plot(df['start_date'], df['ENS_M'])
    lines += ax.plot(df['start_date'], df['obs'])
    plt.legend(lines,wens_names,loc='upper center', bbox_to_anchor=(0.5,-0.05), ncol=3)
    plt.yticks(fontsize=18)
    plt.xticks(fontsize=18)
    plt.savefig(save_folder+'WENS_time_series_'+v, bbox_inches="tight")
    
    v_i += 1
