
import pandas as pd
import matplotlib.pyplot as plt



input_file = '/home/verif/verif-post-process/weights/ensemble/output/output-pwa/'

save_folder = '/home/verif/verif-post-process/weights/ensemble/imgs/img-pwa/'

variables = ['SFCTC', 'SFCTC_KF', 'SFCWSPD','SFCWSPD_KF','PCPTOT']
variable_name = ['Temperature-Raw','Temperature-KF', 'Wind Speed-Raw','Wind Speed-KF', 'Hourly Precipitation']
variable_unit = ['[C]','[C]','[km/hr]', '[km/hr]', '[mm/hr]']
stats = ['MAE', 'rmse', 'spcorr']

v_i = 0
for v in variables:
    var_name = variable_name[v_i]
    var_unit = variable_unit[v_i]
    for s in stats:
        if s == "MAE":
            mae = pd.read_csv(input_file + s + '_' +v + '_seasonal_PWA_MAE__NA.txt',sep = "\s+|,")
            mae.columns = ['start_date','end_date','ENS_W','ENS_M']
            mae['start_date'] = pd.to_datetime(mae['start_date'], format='%y%m%d%H')
            mae_W = round(mae['ENS_W'].mean(),4)
            mae_M = round(mae['ENS_M'].mean(),4)
        elif s == "rmse":
            rmse = pd.read_csv(input_file + s + '_' +v + '_seasonal_PWA_MAE__NA.txt',sep = "\s+|,")
            rmse.columns = ['start_date','end_date','ENS_W','ENS_M']
            rmse['start_date'] = pd.to_datetime(rmse['start_date'], format='%y%m%d%H')
            rmse_W = round(rmse['ENS_W'].mean(),4)
            rmse_M = round(rmse['ENS_M'].mean(),4)
        elif s == "spcorr":
            spcorr = pd.read_csv(input_file + s + '_' +v + '_seasonal_PWA_MAE__NA.txt',sep = "\s+|,")
            spcorr.columns = ['start_date','end_date','ENS_W','w_pvalue','ENS_M','m_pvalue']
            spcorr['start_date'] = pd.to_datetime(spcorr['start_date'], format='%y%m%d%H') 
            spcorr_W = round(spcorr['ENS_W'].mean(),4)
            spcorr_M = round(spcorr['ENS_M'].mean(),4)

    fig, ax = plt.subplots(3, figsize=(40,30))
    plt.rcParams.update({'font.size': 25})
    ax[0].plot(mae['start_date'], mae['ENS_W'], 'm')
    ax[0].plot(mae['start_date'], mae['ENS_M'],'b')
    ax[0].set_title('Mean Absolute Error (MAE)')
    ax[0].set_ylabel(var_name +" MAE "+var_unit)
    #ax[0].legend(["ENS_W: "+str(mae_W),"ENS_M: "+str(mae_M)],loc='best')

    ax[1].plot(rmse['start_date'], rmse['ENS_W'], 'm')
    ax[1].plot(rmse['start_date'], rmse['ENS_M'],'b')
    ax[1].set_title('Root Mean Square Error (RMSE)')
    ax[1].set_ylabel(var_name + " RMSE "+var_unit)
    #ax[1].legend(["ENS_W: "+str(rmse_W),"ENS_M: "+str(rmse_M)],loc='best')
    
    ax[2].plot(spcorr['start_date'], spcorr['ENS_W'], 'm')
    ax[2].plot(spcorr['start_date'], spcorr['ENS_M'],'b')
    ax[2].set_title('Spearman Rank Correlation (spcorr)')
    ax[2].set_ylabel(var_name+" spcorr "+var_unit)
    #ax[2].legend(["ENS_W: "+str(spcorr_W),"ENS_M: "+str(spcorr_M)],loc='best')

    #plt.legend(["PWA","SREF"],loc='best')
    plt.legend(["PWA","SREF"],loc='upper center', bbox_to_anchor=(0.5,-0.1), ncol=6)
    plt.savefig(save_folder+'ENS_W_vs_ENS_M_pwa_'+v, bbox_inches="tight")
    
    v_i += 1


