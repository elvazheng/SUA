import glob
import pandas as pd
import numpy as np
from datetime import timedelta

PATH = r'Z:\Raw ND Data'

def read_sub(sub):
    ''' Read all the 10 hz files for one subject
    
    Arguments:
    a subject number is passed into the function as a string like: '001'
    Returns:
    The complete data frame of all a subject's runs is returned
    '''
    filenames = glob.glob(PATH + "\*001*\*\data 10hz*.csv")
    frame = pd.DataFrame()
    dflist = [] 
    count=0
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
        df=df.drop_duplicates(subset=['gpstime','latitude','longitude',
        'gpsspeed', 'heading', 'pdop', 'hdop', 'vdop','fix_type', 'num_sats', 
        'acc_x', 'acc_y', 'acc_z','throttle', 'obdspeed', 'rpm'],
        keep='first')
        df=df[df.gpstime.notnull()]
              
        # add column 'speed' and 'trip', delete 'gpsspeed' and 'obdspeed' 
        if any(pd.notnull(df.obdspeed)):
            df['speed']=np.where(df['num_sats']>=4,df.gpsspeed,df.obdspeed)
        else:
            df['speed']=df.gpsspeed
        df['trip']=df['subject_id'].map(lambda x:filename[-8:-4])   
        df=df.drop(['gpsspeed','obdspeed'], 1)   
            
        #if contains repeating or empty data, replace the wrong time by gpstime
        if filename[-8:-4] in open(PATH +'\problem files.txt').read():
            for ind in range(len(df)-1):
                delta1=df.gpstime.iloc[[ind]]-df.time.iloc[[ind]]
                delta2=df.time.iloc[[ind]]-df.gpstime.iloc[[ind]]
                if any(delta1>timedelta(seconds=1.5)):
                    df.time.iloc[[ind]] = df.gpstime.iloc[[ind]]
                    count +=1
                if any(delta2>timedelta(seconds=1.5)):
                    df.time.iloc[[ind]] = df.gpstime.iloc[[ind]]
                    count +=1 
        #if less than 60 seconds, delete the file
        if len(df)<=600:
            df=df[0:0]
            print "gps less than 60 sec"  
        dflist.append(df)               
    frame = pd.concat(dflist,axis=0)
    print 'weird rows that time and gpstime not match: ',count,', total final rows: ',len(frame)     
    frame.to_csv('H:\SUA\SUA\Organized Files'+'\sub_'+filename[17:20]+'.csv',index=None) 
    #save row count to txt file  
    f=open(PATH +'\countRows.txt','a') 
    f.write('\nsub_'+filename[17:20]+'   '+str(len(frame)))
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
    ismovingG = np.where(df.gpsspeed > 0)[0]
    ismovingO = np.where(df.obdspeed > 0)[0]
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
    print(timeit.timeit("read_sub('sub')", number=1, setup="from __main__ import read_sub"))
