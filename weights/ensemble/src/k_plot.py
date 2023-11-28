
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


output_15 = '/home/verif/verif-post-process/weights/ensemble/src/output-40/'
output_30 = '/home/verif/verif-post-process/weights/ensemble/src/output-200/'
variables = ['SFCTC', 'SFCTC_KF', 'SFCWSPD','SFCWSPD_KF','PCPTOT']
variable_name = ['Temperature-Raw','Temperature-KF', 'Wind Speed-Raw','Wind Speed-KF', 'Hourly Precipitation']
variable_unit = ['[C]','[C]','[km/hr]', '[km/hr]', '[mm/hr]']
stats = ['MAE', 'RMSE', 'spcorr']

v_i = 0
for v in variables:
    var_name = variable_name[v_i]
    var_unit = variable_unit[v_i]
    mae15_W_all, mae30_W_all, rmse15_W_all,rmse30_W_all, spcorr15_W_all, spcorr30_W_all = [], [], [], [],[], []
    for s in stats:
        if s == "MAE":
            mae15 = pd.read_csv(output_15 + s + '_' + v +'_seasonal_LF_.txt',sep = "\s+|,")
            mae15.columns = ['start_date','end_date','ENS_W','ENS_M']
            mae15['start_date'] = pd.to_datetime(mae15['start_date'], format='%y%m%d%H')
            mae15_W = round(mae15['ENS_W'].mean(),4)
            mae15_M = round(mae15['ENS_M'].mean(),4)
            mae15_W_all.append(mae15.ENS_W)

            mae30 = pd.read_csv(output_30 + s + '_' + v +'_seasonal_LF_200.txt',sep = "\s+|,")
            mae30.columns = ['start_date','end_date','ENS_W','ENS_M']
            mae30['start_date'] = pd.to_datetime(mae30['start_date'], format='%y%m%d%H')
            mae30_W = round(mae30['ENS_W'].mean(),4)
            mae30_M = round(mae30['ENS_M'].mean(),4)
            mae30_W_all.append(mae30.ENS_W)
        
        elif s == "RMSE":
            rmse15 = pd.read_csv(output_15 + s + '_' + v +'_seasonal_LF_.txt',sep = "\s+|,")
            rmse15.columns = ['start_date','end_date','ENS_W','ENS_M']
            rmse15['start_date'] = pd.to_datetime(rmse15['start_date'], format='%y%m%d%H')
            rmse15_W = round(rmse15['ENS_W'].mean(),4)
            rmse15_M = round(rmse15['ENS_M'].mean(),4)
            rmse15_W_all.append(rmse15.ENS_W)

            rmse30 = pd.read_csv(output_30 + s + '_' + v +'_seasonal_LF_200.txt',sep = "\s+|,")
            rmse30.columns = ['start_date','end_date','ENS_W','ENS_M']
            rmse30['start_date'] = pd.to_datetime(rmse30['start_date'], format='%y%m%d%H')
            rmse30_W = round(rmse30['ENS_W'].mean(),4)
            rmse30_M = round(rmse30['ENS_M'].mean(),4)
            rmse30_W_all.append(rmse30.ENS_W)

        elif s == "spcorr":
            spcorr15 = pd.read_csv(output_15 + s + '_' + v +'_seasonal_LF_.txt',sep = "\s+|,")
            spcorr15.columns = ['start_date','end_date','ENS_W','w_pvalue','ENS_M','m_pvalue']
            spcorr15['start_date'] = pd.to_datetime(spcorr15['start_date'], format='%y%m%d%H') 
            spcorr15_W = round(spcorr15['ENS_W'].mean(),4)
            spcorr15_M = round(spcorr15['ENS_M'].mean(),4)
            spcorr15_W_all.append(spcorr15.ENS_W)
            
            spcorr30 = pd.read_csv(output_30 + s + '_' + v +'_seasonal_LF_200.txt',sep = "\s+|,")
            spcorr30.columns = ['start_date','end_date','ENS_W','w_pvalue','ENS_M','m_pvalue']
            spcorr30['start_date'] = pd.to_datetime(spcorr30['start_date'], format='%y%m%d%H')
            spcorr30_W = round(spcorr30['ENS_W'].mean(),4)
            spcorr30_M = round(spcorr30['ENS_M'].mean(),4)
            spcorr30_W_all.append(spcorr30.ENS_W)    
    
    
    fig, ax = plt.subplots(3, figsize=(40,30))
    plt.rcParams.update({'font.size': 25})       
    lines = []
    num_colors = 2
    cm=plt.get_cmap('gist_rainbow')
    ax[0].set_prop_cycle(color=[cm(1.*i/num_colors) for i in range(num_colors)])
    ax[1].set_prop_cycle(color=[cm(1.*i/num_colors) for i in range(num_colors)])            
    ax[2].set_prop_cycle(color=[cm(1.*i/num_colors) for i in range(num_colors)])
    
    lines += ax[0].plot(mae15['start_date'], mae15['ENS_W'])
    lines += ax[0].plot(mae30['start_date'], mae30['ENS_W'])
    ax[0].set_title('Mean Absolute Error (MAE)')
    ax[0].set_ylabel(var_name +" MAE "+var_unit)
    #ax[0].legend(lines, labels, loc='best')
    
    ax[1].plot(rmse15['start_date'], rmse15['ENS_W'])
    ax[1].plot(rmse30['start_date'], rmse30['ENS_W'])
    ax[1].set_title('Root Mean Square Error (RMSE)')
    ax[1].set_ylabel(var_name + " RMSE "+var_unit)
    #ax[1].legend(loc='best')
    
    ax[2].plot(spcorr15['start_date'], spcorr15['ENS_W'])
    ax[2].plot(spcorr30['start_date'], spcorr30['ENS_W'])
    ax[2].set_title('Spearman Rank Correlation (spcorr)')
    ax[2].set_ylabel(var_name+" spcorr "+var_unit)
    #ax[2].legend(["ENS_W: "+str(spcorr_W),"ENS_M: "+str(spcorr_M)],loc='best')
    
    labels = ['k = 40', 'k = 200']
    plt.legend(lines, labels, loc='upper center',bbox_to_anchor=(0.5, -0.1), ncol=10)
    plt.savefig('ENS_W_vs_ENS_M_'+v+'_diffk', bbox_inches="tight")
    
    v_i += 1


