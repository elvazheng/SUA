import glob
import os
import nddata

PATH = os.getenv('SuaData')

def process_subs():
    dirs = glob.glob(PATH + "\*")
    for dir in dirs:
        sub = os.path.split(dir)[1][2:5]
        nddata.read_sub(sub)
        
if __name__ == '__main__':
    process_subs()