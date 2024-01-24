
import pandas as pd
import matplotlib.pyplot as plt



monthly = '/home/verif/verif-post-process/weights/sliding_window/output/monthly/'
weekly = '/home/verif/verif-post-process/weights/sliding_window/output/weekly/'

ens_type = [monthly,weekly]
ens_names = ['SW-monthly', 'SW-weekly', 'SREF']

variables = ['SFCTC', 'SFCTC_KF', 'SFCWSPD','SFCWSPD_KF','PCPTOT']
variable_name = ['Temperature-Raw','Temperature-KF', 'Wind Speed-Raw','Wind Speed-KF', 'Hourly Precipitation']
variable_unit = ['[C]','[C]','[km/hr]', '[km/hr]', '[mm/hr]']
stats = ['MAE', 'RMSE', 'spcorr']
stat_names = ['Mean Absolute Error (MAE)', 'Root Mean Square Error (RMSE)', 'Spearman Rank Correlation (spcorr)']

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
        num_colors = len(ens_names)
        cm=plt.get_cmap('tab10')
        ax[s].set_prop_cycle(color=[cm(1.*i/num_colors) for i in range(num_colors)])
        
        for i in ens_type:
            
            f = i + stats[s] + '_' + v + '_seasonal.txt'
            df, mval = get_data(f,s)
            
            mvals.append(mval)
            
            lines += ax[s].plot(df['start_date'], df['ENS_W'])
            ax[s].set_title(stat_names[s])
            ax[s].set_ylabel(var_name +" "+stats[s]+" "+var_unit)
        
        lines += ax[s].plot(df['start_date'], df['ENS_M'])
        plt.legend(lines,ens_names,loc='upper center', bbox_to_anchor=(0.5,-0.1), ncol=6)
        n_i += 1
   
    plt.savefig('SW_all_'+v, bbox_inches="tight")
    
    v_i += 1
