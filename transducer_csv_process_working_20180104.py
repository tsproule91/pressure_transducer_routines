'''
VARIANT OF THE TRANSDUCER CSV FILE. GOAL IS TO SIMPLY USE A START AND
END DATETIME SYSTEM RATHER THAN COMPLICATED DATA MATCHING

Goal of this routine is to download data from solinst pressure transducers and
prepare the dataset for normalization, plotting, curve fitting etc. 
The target file will be designated via user input text entry. The user will
specify if the datalogger is a barometric or level-logger
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
from datetime_index_working_20180104 import search_datetime

#IMPORT SINGLE LOGGER DATA AND FORMAT DATE-TIMES TO BE PYTHON READY
def logger_data_download(dl_type, logger_file):
    sr = [] #start row (sr) variable that denotes which row to start on...
    #dependent on whether the data is from a baro or watter logger
    #this is due to the csv file output formatting from solinst
    governing_time = False
    if dl_type == 'b':
        sr = 11
        governing_time = True
    elif dl_type == 'w':
        sr = 12
    print('Your sr value is %s' %sr)
    pressures = [] #pressure vectors in kpa
    temperatures = [] #temperature vector in degrees C
    datetimes = []
    with open(logger_file) as csvfile:
        readCSV = csv.reader(csvfile, delimiter = ',')
        for row in readCSV:
             pressure = row[3]
             temperature= row[4]
             pressures.append(pressure)
             temperatures.append(temperature)
             datetimes.append('%s %s' %(row[0], row[1]))
             
        pressures = list(map(float, pressures[sr:len(pressures)]))
        temperatures = list(map(float, temperatures[sr:len(temperatures)]))
        datetimes = datetimes[sr:len(datetimes)]
        
        datetimes_final = []
        for i in range(0, len(datetimes)):
            datetimes_final.append(datetime.strptime(datetimes[i], '%m/%d/%Y %I:%M:%S %p'))
     #Exports are: datetime, pressure (kpa), temp (C), dl type ('w' or 'b'), and governing time boolean).
     #The governing time boolean is to distinguish if this was a barometric logger.
     #If logger is baro, then this datetime array will be used for all loggers
    return (datetimes_final, pressures, temperatures)

#SPECIFY LOGGER TYPE BELOW VIA USER INPUT
def scan_logger():
    dl = input('Is your logger for (b)arometric or (w)ater pressure? Enter (b/w)') #datalogger type
    dl_file = input('Enter the name of the file you want to process. Include the .csv extension please')

#THIS SHOULD BE OBSOLETE NOW... DELETE LATER
# def copasetic(baro_dt, level_dt):           #inputs are baro and level logger vector date-times
#     if baro_dt[0] == level_dt[0] and baro_dt[-1] == level_dt[-1]:
#         consistent = True #checks that first and last element of time vectors match
#         print('Datetime vectors are synchronized between loggers')
#         return (consistent, len(baro_dt))
# #    else:
# #        consistent = False
# #        print('Datetime vector dimensions between loggers are inconsistent. Check dataset and try again.')
#     else:
#         find_smallest = min([len(baro_dt), len(level_dt)])
#         print(find_smallest)
#         consistent = False
#         print('The logger datetimes were not synchronized. Adjustments were made using the copasetic function.')
#         return (consistent, find_smallest)

# '''
# Section that scans a well parameter CSV file.
# Returned elements of the well-par vector respectivley are:
# [0] = TOC in m
# [1] = casing aboveground in m
# [2] = DTW in m
# *Update this list later if anything changes
# '''

def scan_well_pars(call_file):
#    call_file = input('Please enter the well parameter file including the .csv extension:')
#    call_file = 'well_3nw_pars.csv' #test case for running code; change to input file later   
    well_pars = []
    with open(call_file) as csvfile:
        readCSV = csv.reader(csvfile, delimiter = ',')
                
        for column in readCSV:
            well_pars.append(column)
            #future note: maybe associate the time index of the dtw measurement?
            
        for i in range(0,len(well_pars)):
            well_pars[i] = list(map(float, well_pars[i]))
        
    return well_pars

#SCAN USER INPUT TO TELL PROGRAM WHICH ROUTINE TO TAKE
def logger_type(dl):
    if dl == 'b':
        print('This confirms that you specified a barometric datalogger')
    elif dl == 'w':
        print('This confirms that you specified a water level-logger')
    else:
        print('Invalid entry. Please restart the script entering eith b or w')        
    if dl == 'b' or dl == 'w':
        print(dl)
        return dl

'''
Function that scans through the data and returns the index associated with the data correction date. 
Data correction translates the PT depth in kPa into a groundwater elevation measurement using
the well paramaters and measured depth to water at a given time
'''


def data_correction(timeline_b, timeline_w, baro_pressure, level_pressure, well_parameters, ref_time, start_dt, end_dt):
    b_start = search_datetime(timeline_b, start_dt) #start index of baro datetime
    b_end = search_datetime(timeline_b, end_dt) #end index of baro datetime
    w_start = search_datetime(timeline_w, start_dt) #start index of level datetime
    w_end = search_datetime(timeline_w, end_dt) #end index of level datetime
                            
    toc = well_parameters[0][0] #top of casing elevation  value in meters
    cag = well_parameters[0][1] #casing above ground in m
    dtw = well_parameters[0][2] #depth to water value in meters from toc
    
    b_pressure = baro_pressure[b_start:b_end] #specified barometric pressure values
    l_pressure = level_pressure[w_start:w_end] #specified water level pressure values
    b_time = timeline_b[b_start:b_end]
    l_time = timeline_w[w_start:w_end]
    
    if len(b_pressure) != len(l_pressure):
        return(print('Your barometric and level pressure datasets are not in sync. Try again.'))
    
    raw_heads = [] #variable for raw head values

    calib_index = search_datetime(l_time, ref_time) #designate index of head calibration value

    for r in range(0, len(l_pressure)):
        temp = (l_pressure[r] - b_pressure[r])*0.101972 #compensate pressure, convert from kpa to m water
        raw_heads.append(temp)    
    
    calib_head = raw_heads[calib_index] #designate calibration head
    
    comp_heads = []
    
    for h in range(0, len(raw_heads)): #converts to a relative groundwater elevation
        comp_heads.append(raw_heads[h] + toc -cag - dtw - calib_head) 


    return (l_time, comp_heads) #return formatted time and groundwater elevations


#ORIGINAL VERSION OF DATA CORRECTION BELOW, REVERT IF NECESSARY
#def data_correction(timeline_b, timeline_w, level_pressure, well_parameters, ref_date):
##    master_index = np.where(timeline == datetime(2017, 12, 7, 9, 30)) #try to get this working later
#    if len(timeline_b) > len(timeline_w):
#        timeline = timeline_w
#    elif len(timeline_w) > len(timeline_b):
#        timeline = timeline_b
#    elif len(timeline_w) == len(timeline_b):
#        timeline = timeline_b
#                            
#    toc = well_parameters[0][0] #top of casing elevation  value in meters
#    cag = well_parameters[0][1] #casing above ground in m
#    dtw = well_parameters[0][2] #depth to water value in meters from toc
#
#    test_case = False
#    for i in range(0,len(timeline)):
#        if timeline[i] == ref_date:
#            test_case = True
#            master_index = i
#    if test_case == True:
#        print('The reference date of %s has an associated index of %s' %(ref_date, master_index))
#    
#    raw_heads = level_pressure #raw compensated pressure data... depth above PT
#    calibration_head = raw_heads[master_index] #use the relevant index
##    raw_heads = list(map(float, raw_heads)) - calibration_head #index head will be 0
##    print(len(raw_heads))
##    return ('bye')
##do a better job of this later, use a parameter reference file
##    lazy_pars = 985.802 - 0.717 - 8.72 #parameters specific to 3nw in m
#    #3 parameters are: TOC elvtn, casing abv grd, and dtw at master_index
#    for i in range(0,len(raw_heads)):
#        raw_heads[i] = raw_heads[i]- calibration_head + toc - cag -dtw
##    plt.plot(timeline, raw_heads)
##    print(raw_heads)
##    print(calibration_head)
#    return (timeline, raw_heads)
        
'''
Function inputs are the barometric and level-logger times and pressures.
Returns depth of the level-logger pressure data in m head.
Does not have any corrections for groundwater elevation or where the water 
table was at a given instant.
'''

#DO AWAY WITH THIS FOR NOW... SEE IF I NEED TO BRING IT BACK LATER
#def compensate_pressure(baro_data, level_data):
#    small_index = copasetic(baro_data[0], level_data[0]) #use fxn to make sure datetimes line up
#    data_index = small_index[1] #smallest dataset value... use correction
#    bp = baro_data[1][0:data_index] #barometric pressure data
#    lp = level_data[1][0:data_index] #level-logger pressure data
#    comp_pressure = []
#    
#    for i in range(0,len(lp)):
#        p_i = (lp[i] - bp[i])*.101972 #convert kpa to m head
#        comp_pressure.append(p_i)
#    return comp_pressure         

#SET UP THE BOTTOM FUNCTION BETTER FOR AN INDIVIDUAL TEST CASE
def plot_pt_data(x,y,file_title): #inputs are datetimes and corrected heads, respectively
    fig1, ax1 = plt.subplots(figsize = (10,6), dpi = 75)
    ax1.plot(x,y)
    pylab.xlabel('Date-time')
    pylab.ylabel('Relative head (m)')
    pylab.title('Pressure for file: %s' %file_title)
    plt.xticks(rotation = 90)
    # plt.show() #statement supressed so that it can be utilized in merged function

'''
GOVERNING FUNCTION: master_process
Approximate flow is: 
i) Specify logger types for the baro and level logger data files, respectively
ii) use logger_data_download on barometric data:
    *this takes in the logger type ('b' or 'w') and barometric data csv file
    *returns correctly formatted datetimes, raw depth pressure, and temperatures
iii) use 'logger_data_download' function on level-logger data: same outputs as in step .ii
iv) use 
'''

#above reference for the compensation script
#data_correction(timeline_b, timeline_w, baro_pressure, level_pressure, well_parameters, ref_time, start_dt, end_dt):
def master_process(baro_data, level_data, well_data, reference_datetime, start, finish):
    bt = logger_type('b') #define barometric logger type criteria
    lt = logger_type('w') #define level logger  type criteria
    baro_raw = logger_data_download(bt, baro_data) #download and date formatting
    level_raw = logger_data_download(lt, level_data) #downloda and date formatting
#    pre_proc = compensate_pressure(baro_raw, level_raw) #OBSOLETE
    well_pars = scan_well_pars(well_data) #scans in well parameter file
    final_head = data_correction(baro_raw[0], level_raw[0], baro_raw[1], level_raw[1], well_pars, reference_datetime, start, finish)
    # plot_pt_data(final_head[0], final_head[1], level_data) #supress for use in the master script
    return (final_head)

#REPURPOSE THIS LATER SO THAT IT WORKS BETTER
def single_plot(x,y):
    fig1, ax1 = plt.subplots(figsize = (10, 5), dpi = 75)
    plt.plot(x,y)
    plt.xticks(rotation = 90)
    pylab.xlabel('Date')
    pylab.ylabel('Relative groundwater elevatIONn (m)')
    fig1.tight_layout()
    plt.show()

'''
This code is now being used as a sub-routine of the 'multiple_transducer_correlation.py' code.
The functions in here are used to download and format the csv data appropriately
The associated super-routine takes the data from multiple files, drawing specifically from the
master_process governing function
'''

#REWORK THIS MAIN BLOCK SO THAT ITS EASIER TO ANALYZE A SINGLE TRANSDUCER
#SHOULD PROBABLY FOLLOW A PATTERN SIMILAR TO THAT IN THE MULTI-TRANSDUCER SCRIPT
if __name__ == '__main__':
    print('Hello')
    barometric_file = '3nw_baro_20171207_amended.csv'
    reference_time = datetime(2017, 12, 7, 9, 30)
    f_inp1 = ['3nw_20171207_amended.csv', 'well_3nw_pars.csv'] #input file 1 and well pars
    f_inp2 = ['3ne_20171207_amended.csv', 'well_3ne_pars.csv'] #input file 2 and well pars
    f_inp3 = ['5nw_20171207_amended.csv', 'well_5nw_pars.csv'] #input file 3 and well pars
    f_inp4 = ['5ne_20171207_amended.csv', 'well_5ne_pars.csv'] #input file 4 and well pars
#    master_process(barometric_file, f_inp1[0], f_inp1[1])
    full_result = master_process(barometric_file, f_inp4[0], f_inp4[1], reference_time)
    single_plot(full_result[0], full_result[1])

    '''
    TEST FINAL SEQUENCE IS BELOW... SAVE THIS FOR A WHILE
    '''

