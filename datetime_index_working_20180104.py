'''
Function to use in transducer_csv_process to designate start and end times
of pressure transducer data examination
'''

import numpy as np
import matplotlib.pyplot as plt
import pylab
import pandas as pd
from datetime import datetime

#input is a datetime value. is input file and index
#input value example: datetime(2017, 11, 29, 9, 30)
def search_datetime(d_file, d): #function to search for a specified date-time value
    f = 'f'
    find_dt = d_file.index(d)
#    print(find_dt)
    return(find_dt)
         
def test_import(data_file):
    dates = [] 
    times = []
    with open(data_file) as csvfile:
        readCSV = csv.reader(csvfile, delimiter = ',')
        for row in readCSV:
             dates.append(row[0])
             times.append(row[1])
    
    header1 = dates.index('Date')       
    header2 = times.index('Time')  
    
    del dates[header1]
    del times[header2]
    
    dt = [] #merge datetimes
    
    for i in range(0,len(dates)):
        dt.append('%s %s' %(dates[i], times[i])) #merge dates and times

    for j in range(0,len(dt)):
        dt[j] = datetime.strptime(dt[j], '%m/%d/%Y %I:%M:%S %p')
        
    return dt

if __name__ == '__main__':
    print('Hello world')
    #test case below for just this function
    mainpath = 'C:/Users/Tyler/Desktop/python_20171226/'
    file1 = 'date_practice.csv'
    follow_me = os.path.join(mainpath,file1)
    test1 = test_import(follow_me)
    test_date = datetime(2018, 1, 3, 11, 30)
    final_test = search_datetime(test1, test_date)
    
    
    