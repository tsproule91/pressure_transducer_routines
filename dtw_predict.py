'''
Given 1d polynomial equations for groundwater level fluctuation, predict future depth/decline in water level
'''

import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import pylab
import pandas as pd
from datetime import datetime
import matplotlib.dates as mdates
from scipy import stats
from transducer_csv_process import master_process


# def test_eqn():
#     x = np.linspace(1, 100, 100)
#     y = np.linspace(30, 12, 100)
#     poly_base = np.polyfit(x,y,1)
#     p = np.poly1d(poly_base)
#
#     here = p(30)
#     print('Testing %s' %here)
#
#     line_base = np.polyfit(mdates.date2num(xy[i][0]), xy[i][1], 1)  # initiate polynomial function, note date2num
#     line_plot = np.poly1d(line_base)  # create line of polynomial
#     print(x,y)
#     plt.plot(x,y)
#     plt.show()
#     return (p)

'''
Numbers as dates... 1.0 day  = 1.0 float. Decimals are straightforward.
0.5 = 0.5 day = 12 hours, etc
'''

def depth_calculate(eqn, days): # current inputs; polynomial equation and time
    li = eqn(0)
    le = eqn(days)
    print('Your predicted decline over a period of %s days is %s m' %(days, (li - le)))
    return (li-le)

if __name__ == '__main__':
    print('Hello from a a sub-world')
    time = input('Please enter the number of days elapsed you want to predict')
    time = float(time)
    # inp = test_eqn()
    # depth_calculate(inp, time)