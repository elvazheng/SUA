import glob
import pandas as pd
import numpy as np
import os
from datetime import timedelta

PATH = os.getenv('SuaData')

def read_sub(sub):
    ''' Read all the 10 hz files for one subject
    
    Arguments:
    a subject number is passed into the function as a string like: '001'
    Returns:
    The complete data frame of all a subject's runs is returned
    '''
    #filenames = glob.glob(PATH + "\*001*\*\data 10hz*.csv")
    #filenames = glob.glob(PATH + "\*" + sub + "*\*\data 10hz*.csv")
    filenames = glob.glob(os.path.join(PATH,'*'+sub+'*','*','data 10hz*.csv'))
    frame = pd.DataFrame()
    dflist = [] 
    count=0
    for filename in filenames:
        print filename
        trip = filename[-8:-4]
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
            print 'read_csv failed on: ' + filename
            continue
        if reject_file(df):
            continue
            
        # trim size of file by getting rid of empty rows, duplicates, and null times
        df = trim_file(df)
        df=df.drop_duplicates(subset=['gpstime','latitude','longitude',
            'gpsspeed', 'heading', 'pdop', 'hdop', 'vdop','fix_type', 'num_sats', 
            'acc_x', 'acc_y', 'acc_z','throttle', 'obdspeed', 'rpm'],
            keep='first')
        df=df[df.gpstime.notnull()]
        #for known problem files, replace the wrong time by gpstime
        if trip in open('problem files.txt').read():
            df, numfixed = replace_time(df)
            count += numfixed
              
        # add column 'speed' and 'trip', delete 'gpsspeed' and 'obdspeed' 
        if any(pd.notnull(df.obdspeed)):
            df['speed']=np.where(df['num_sats']>=4,df.gpsspeed,df.obdspeed)
        else:
            df['speed']=df.gpsspeed
        df['trip']=df['subject_id'].map(lambda x:trip)   
        df=df.drop(['gpsspeed','obdspeed'], 1)   
        
        #if less than 60 seconds, delete the file
        if len(df)<=600:
            df=df[0:0]
            print "gps less than 60 sec"
            
        dflist.append(df)             
          
    frame = pd.concat(dflist,axis=0)
    
    print 'weird rows that time and gpstime not match: ',count,', total final rows: ',len(frame)

    frame.to_csv(os.path.join(os.getenv('SuaProcessed'), 'sub_' + sub + '.csv'), index=None)
    
    #save row count to txt file  
    f=open('countRows.txt','a') 
    f.write('\nsub_'+sub+'   '+str(len(frame)))
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
    
def replace_time(df):
    ''' Replace time for any rows that have missing or repeated data '''
    count = 0
    for ind in range(len(df)-1):
        delta1=df.gpstime.iloc[[ind]] - df.time.iloc[[ind]]
        delta2=df.time.iloc[[ind]] - df.gpstime.iloc[[ind]]
        if any(delta1 > timedelta(seconds=1.5)):
            df.time.iloc[[ind]] = df.gpstime.iloc[[ind]]
            count +=1
        if any(delta2 > timedelta(seconds=1.5)):
            df.time.iloc[[ind]] = df.gpstime.iloc[[ind]]
            count +=1 
    return df, count

if __name__ == '__main__':
    import timeit
    print(timeit.timeit("read_sub('001')", number=1, setup="from __main__ import read_sub"))
