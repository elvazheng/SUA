import glob
import pandas as pd
import numpy as np

from pandas import DataFrame
from pylab import *
from scipy import signal
from numpy import array, diff, insert

PATH = r'Z:\Raw ND Data'

def read_sub(sub):
    ''' Read all the 10 hz files for one subject
    
    Arguments:
    a subject number is passed into the function as a string like: '001'
    Returns:
    The complete data frame of all a subject's runs is returned
    '''
    filenames = glob.glob(PATH + "\*" + sub + "*\*\data 10hz*.csv")
    frame = pd.DataFrame()
    dflist = []
    #set an index to order the plots
    ind_plot = 0
    
    for filename in filenames:
        print filename
        try:
            df = pd.read_csv(filename, 
                usecols=['subject_id', 'time', 'gpstime', 'latitude', 
                    'longitude', 'gpsspeed', 'heading', 'pdop', 'hdop', 'vdop', 
                    'fix_type', 'num_sats', 'acc_x', 'acc_y', 'acc_z', 
                    'throttle', 'obdspeed', 'rpm'],
                parse_dates=[1, 2], 
                infer_datetime_format=True, 
                error_bad_lines=False)
        except Exception:
            continue
        if reject_file(df):
            continue   
        df = trim_file(df)
        df.run = filename[-8:-4]
        dflist.append(df)

        #Comparing with variables acc_x,acc_y,acc_z
        cKPH2MPS = 1/3.6
        Fs = 10
        #list_time = df.gpstime.tolist()
        list_gps = df.gpsspeed.tolist()
        #list_acx = df.acc_x.tolist()
        list_acy = df.acc_y.tolist()            
        #list_acz = df.acc_z.tolist()
        #array_time = array(list_time)
        a_time = array(range(len(list_gps)))
        array_gps = array(list_gps)/100
        #array_acx = array(list_acx)
        array_acy = array(list_acy)
        
        b,a = signal.butter(2,0.2)
        temp_gps_mps = array(list_gps) * cKPH2MPS
        array_gps_mps = signal.filtfilt(b,a,temp_gps_mps)    
        array_acc = diff(array_gps_mps)*10/9.8
        array_acc = insert(array_acc,0,0)
        
        #array_acz = array(list_acz)
        
        #if len(a_time)>600:
        ind_plot = ind_plot+1
        
        if ind_plot <= 30:
            figure(1)
            subplot(6,5,ind_plot)
            plot(a_time,array_gps)
       #     plot(array_time,array_acx)
            plot(a_time,array_acy,a_time+35,array_acc)
       #     plot(array_time,array_acz)
            show() 
            
        if 31 <= ind_plot <=60:
            figure(2)
            subplot(6,5,ind_plot-30)
            plot(a_time,array_gps)
      #      plot(array_time,array_acx)
            plot(a_time,array_acy,a_time+35,array_acc)
      #      plot(array_time,array_acz)
            show() 
            #if ind_plot == 31:
                #print array_acc
        
        if 61 <= ind_plot <= 90 :
            figure(3)
            subplot(6,5,ind_plot-60)
            plot(a_time,array_gps)
      #      plot(array_time,array_acx)
            plot(a_time,array_acy,a_time+35,array_acc)
     #       plot(array_time,array_acz)
            show() 
            
        if 91 <= ind_plot <= 107:
            figure(4)
            subplot(6,5,ind_plot-90)
            plot(a_time,array_gps)
       #     plot(array_time,array_acx)
            plot(a_time,array_acy,a_time+35,array_acc)
      #      plot(array_time,array_acz)
            show() 
    
    frame = pd.concat(dflist)
       
    return frame
    
def reject_file(df):
    ''' Reject a file if there is no gps movement '''
    if not(any(pd.notnull(df.gpsspeed))):
        print "gps no values"
        return True
    if max(df.gpsspeed[pd.notnull(df.gpsspeed)]) == 0:
        print "gps not moving"
        return True
    return False
  
def trim_file(df):
    ''' Trim the beginning and end of a file based on speed '''
    ismoving = df.gpsspeed > 0
    idx_first = np.where(ismoving)[0][0]
    idx_last = np.where(ismoving)[0][-1]
    try:
        df = df[idx_first:idx_last+1]
    except Exception:
        df = df[idx_first:idx_last]     
    return df   
    
if __name__ == '__main__':
    import timeit
    print(timeit.timeit("read_sub('001')", number=1, setup="from __main__ import read_sub"))