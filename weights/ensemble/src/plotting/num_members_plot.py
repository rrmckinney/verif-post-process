
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


output_file = '/home/verif/verif-post-process/weights/ensemble/output/output-num/'

save_folder='/home/verif/verif-post-process/weights/ensemble/imgs/num-mem/'

variables = ['SFCTC', 'SFCTC_KF', 'SFCWSPD','SFCWSPD_KF','PCPTOT']
variable_name = ['Temperature-Raw','Temperature-KF', 'Wind Speed-Raw','Wind Speed-KF', 'Hourly Precipitation']
variable_unit = ['[C]','[C]','[km/hr]', '[km/hr]', '[mm/hr]']
stats = ['MAE', 'RMSE', 'spcorr']

v_i = 0
for v in variables:
    var_name = variable_name[v_i]
    var_unit = variable_unit[v_i]
    mae_W_all, rmse_W_all, spcorr_W_all = [], [], []
    for i in range(1,50):
        for s in stats:
            if s == "MAE":
                mae = pd.read_csv(output_file + s + '_' + v +'_'+str(i)+'_num_.txt',sep = "\s+|,")
                mae.columns = ['start_date','end_date','ENS_W','ENS_M']
                mae['start_date'] = pd.to_datetime(mae['start_date'], format='%y%m%d%H')
                mae_W = round(mae['ENS_W'].mean(),4)
                mae_M = round(mae['ENS_M'].mean(),4)
                mae_W_all.append(mae.ENS_W)
            elif s == "RMSE":
                rmse = pd.read_csv(output_file + s + '_' + v + '_'+str(i)+'_num_.txt',sep = "\s+|,")
                rmse.columns = ['start_date','end_date','ENS_W','ENS_M']
                rmse['start_date'] = pd.to_datetime(rmse['start_date'], format='%y%m%d%H')
                rmse_W = round(rmse['ENS_W'].mean(),4)
                rmse_M = round(rmse['ENS_M'].mean(),4)
                rmse_W_all.append(rmse.ENS_W)
            elif s == "spcorr":
                spcorr = pd.read_csv(output_file + s + '_' + v +'_'+str(i)+'_num_.txt',sep = "\s+|,")
                spcorr.columns = ['start_date','end_date','ENS_W','w_pvalue','ENS_M','m_pvalue']
                spcorr['start_date'] = pd.to_datetime(spcorr['start_date'], format='%y%m%d%H') 
                spcorr_W = round(spcorr['ENS_W'].mean(),4)
                spcorr_M = round(spcorr['ENS_M'].mean(),4)
                spcorr_W_all.append(spcorr.ENS_W)
    fig, ax = plt.subplots(3, figsize=(40,30))
    plt.rcParams.update({'font.size': 25})
    lines = []
    num_colors = 50
    cm=plt.get_cmap('gist_rainbow')
    ax[0].set_prop_cycle(color=[cm(1.*i/num_colors) for i in range(num_colors)])
    ax[1].set_prop_cycle(color=[cm(1.*i/num_colors) for i in range(num_colors)])            
    ax[2].set_prop_cycle(color=[cm(1.*i/num_colors) for i in range(num_colors)])
    
    for x in range(len(mae_W_all)):
        lines += ax[0].plot(mae['start_date'], mae_W_all[x])
    lines += ax[0].plot(mae['start_date'], mae['ENS_M'],'ko')
    ax[0].set_title('Mean Absolute Error (MAE)')
    ax[0].set_ylabel(var_name +" MAE "+var_unit)
    #ax[0].legend(lines, labels, loc='best')
    
    for x in range(len(rmse_W_all)):
        ax[1].plot(rmse['start_date'], rmse_W_all[x])
    ax[1].plot(rmse['start_date'], rmse['ENS_M'],'ko')
    ax[1].set_title('Root Mean Square Error (RMSE)')
    ax[1].set_ylabel(var_name + " RMSE "+var_unit)
    #ax[1].legend(loc='best')
    
    for x in range(len(spcorr_W_all)):
        ax[2].plot(spcorr['start_date'], spcorr_W_all[x])
    ax[2].plot(spcorr['start_date'], spcorr['ENS_M'],'ko')
    ax[2].set_title('Spearman Rank Correlation (spcorr)')
    ax[2].set_ylabel(var_name+" spcorr "+var_unit)
    #ax[2].legend(["ENS_W: "+str(spcorr_W),"ENS_M: "+str(spcorr_M)],loc='best')
    
    labels = [str(l+1) + " members" for l in range(len(lines))]
    plt.legend(lines, labels, loc='upper center',bbox_to_anchor=(0.5, -0.1), ncol=10)
    plt.savefig(save_folder+'ENS_W_vs_ENS_M_'+v+'_'+str(i), bbox_inches="tight")
    
    v_i += 1


