'''
This is for processing pressure transducer data from our well

This script successively reads in the data from a previously programmed array,
feeds it into a csv file. Basically convert a list of merged lists 4x3 into
a csv file. Reprogram multi_transducer function so that it reads in a csv file
to specify the target files rather than doing it the dumb way via manual input.

CSV INPUT FILE FORMAT IS:
    Info for one well for each row:
        Col 1 = level-logger csv data file name (str)
        Col 2 = well paramater file associated with level_logger (str)
        Col 3 = desired title of well 'str'

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



def write_file(full):
    r = len(full) #number of rows in input file
    c = int(np.size(full)/r) #number of columns in input file

    print('Your number of rows are %s, number of columns are %s' %(r, c))
    output = open('test_wells.csv', 'w')

    for i in range(r):
        for j in range(c):
            output.write('%s,' % full[i][j])
      
        output.write('\n') 

    output.close()
    return (r,c)

def well_download(all_data):
    merged = []
    
    with open(all_data) as csvfile:
            readCSV = csv.reader(csvfile, delimiter = ',')
            for row in readCSV:
                 print(row)
                 merged.append(row)
         
    return merged
     

if __name__ == '__main__':
    print('Hello world')
    target_file = 'test_wells.csv'
    b = well_download(target_file)



#CODE BELOW IS ARTIFCAT: WAS USED TO MERGE THE FILES AND CREATE CSV USING FXN
#    f_inp1 = ['3nw_20171207_amended.csv', 'well_3nw_pars.csv', 'Well 3N-W'] # input file 1 and well pars
#    f_inp2 = ['3ne_20171207_amended.csv', 'well_3ne_pars.csv', 'Well 3N-E']  # input file 2 and well pars
#    f_inp3 = ['5nw_20171207_amended.csv', 'well_5nw_pars.csv', 'Well 5N-W']  # input file 3 and well pars
#    f_inp4 = ['5ne_20171207_amended.csv', 'well_5ne_pars.csv', 'Well 5N-E']  # input file 4 and well pars
#    merged_files = [f_inp1, f_inp2, f_inp3, f_inp4]
#    
#    a = write_file(merged_files)
    
