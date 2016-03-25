import glob
import pandas as pd
import numpy as np

from pandas import DataFrame
from pylab import *

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
    figure(1)
    
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

        #Comparing gpsspeed with obdspeed

        list_time = df.gpstime.tolist()
        list_gps = df.gpsspeed.tolist()
        list_obd = df.obdspeed.tolist()
        list_satT = df.num_sats.tolist()
        list_heading = df.heading.tolist()
        list_sat = []
        for num in list_satT:
            if num >3:
                num = num
            else:
                num = 0
            list_sat.append(num)       
        array_time = array(list_time)
        array_gps = array(list_gps)
        array_obd = array(list_obd)
        array_sat = array(list_sat)
        array_heading = array(list_heading)/5  #because the value of heading is too big, divides it by 5 to see trend
        
        a_time = array(range(len(list_gps)))
        
        if len(a_time)>600:
            ind_plot = ind_plot+1
        
            if ind_plot < 27:
            
                subplot(6,5,ind_plot)
                plot(a_time,array_gps,'b-')
                plot(a_time,array_obd,'g-')
                plot(a_time,array_sat,'r-')
                plot(a_time,array_heading,'y-')
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
    ismovingG = where(df.gpsspeed > 0)[0]
    ismovingO = where(df.obdspeed > 0)[0]
    if ismovingO != []:
        if ismovingG[0] > ismovingO[0]:       
            ismoving = df.obdspeed > 0 
        else:
            ismoving = df.gpsspeed > 0
    else:
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