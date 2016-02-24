from nddata import read_sub
from pylab import *
import pandas as pd
import math

NMI = 1852.0
D2R = math.pi/180.0

def main():
    df = read_sub('001')
    (px, py) = cart(df)
    figure()
    gca().axes.invert_xaxis()
    plot(px, py, 'ro')
    xlabel('east-west (meters)')
    ylabel('south_north (meters)')
    grid()
    axis('equal')
    show()
    
def cart(df):
    lat_rad = df.latitude * D2R
    py = (df.latitude - min(df.latitude)) * NMI * 60.0
    px = (df.longitude - min(df.longitude)) * NMI * 60.0 * \
        lat_rad.apply(math.cos)
    return px, py
    
if __name__ == '__main__':
    main()