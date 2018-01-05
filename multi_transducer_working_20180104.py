'''
VARIANT FILE OF THE MULTIPLE TRANSDUCER CORRELATION FILE.
TRY TO JUST USE DATE START AND END TIMES FOR SIMPLICITY RATHER
THAN OVERLY COMPLICATED REFORMATTING

Purpose of this code is to utilize the transducer_csV_process.py script to bring in 
multiple processed pressure transducer datasets and analyze them altogher. 

Plot a best of fit line, etc. Write more here later.

Written by Tyler Sproule
Current working version as of 04 January 2018
This must be used in conjunction with the the following files:
    transducer_csv_process_working_20180104.py
    datetime_index_working_20180104.py;
    well_file_processing_working_20180104.py

This version was last reviewd and edited 04 January 2018
Written by Tyler Sproule
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
from transducer_csv_process_working_20180104 import master_process
from datetime_index_working_20180104 import search_datetime
from dtw_predict_working_20180104 import depth_calculate, write_prediction
from well_file_processing_working_20180104 import well_download

'''
Function normalizes the data so that all starting pressures are 0; 
Allows data trends to be closely, will eventually add a trendline fit
'''
def normalize(pt_data):
    fixed_value = pt_data[1][0] #first pressure value; deduct from all other elements to start from 0
    for z in range(0,len(pt_data[1])): #loop through each element of pressure data vectoe
        pt_data[1][z] = pt_data[1][z] - fixed_value
    return pt_data


'''
Loops through to plot all components of a master dataset
Master dataset has 3 levels: PT file -> datetime and pressure

4th arg is the well input (csv) file 
'''
def plot_multiple(xy, n, title_choice, well_file):
    fig1, ax1 = plt.subplots(figsize = (18,10), dpi = 75)
    polynomial_storage = []
    color_pallet = ['b', 'r', 'k', 'g']
    well_legend = []

    for i in range(0,n):    
        ax1.plot(xy[i][0], xy[i][1], color_pallet[i])
        line_base = np.polyfit(mdates.date2num(xy[i][0]), xy[i][1],1) #initiate polynomial function, note date2num
        line_plot = np.poly1d(line_base) #create line of polynomial
        ax1.plot(xy[i][0], line_plot(mdates.date2num(xy[i][0])), color_pallet[i]+'--') #plot the best fit line for each pressure record
        polynomial_storage.append(line_plot) #stores polynomial values for additional processing
        well_legend.append('%s data' %well_file[i][2])
        well_legend.append('%s fit' %well_file[i][2])

    ax1.legend(well_legend)
    pylab.xlabel('Date-time', size = 14)
    plt.xticks(rotation = 90, size = 14)
    plt.yticks(size = 14)
    ax = plt.gca()
    ax.grid(True)

    if title_choice == False:
        pylab.ylabel('Relative GW Elevation (m)', size = 16)
        pylab.title('Multiple adjusted pressure transducer records', size = 16)
    elif title_choice == True:
        pylab.ylabel('Normalized GW Elevation(m)', size = 16)
        pylab.title('Normalized Pressure Transducer Records', size = 16)

    fig1.tight_layout()
    print('Your plots appear to be running successfully')
    plt.show()
    return(polynomial_storage) #return the 1d polynomial equations for each line to process with dtw_predict

if __name__ == '__main__':
    print('Hello  world')
    os.chdir('G:/My Drive/LomaBlanca/07_Wells/PT_data/collection_20180103') #INDEPENDENT
    print(os.getcwd())
    output_folder = 'G:/My Drive/LomaBlanca/07_Wells/PT_data/processed_data'
    #define user input parameters below
    barometric_file = '3nw_baro_20180103_fullVented.csv' #INDEPENDENT
    #EARLY INPUT DATA HERE
    reference_time = datetime(2017, 12, 7, 9, 30) #INDEPENDENT
    first_dt = datetime(2017, 11, 28, 0, 0)
    last_dt = datetime(2017, 12, 7, 10, 30)
    #PREVIOUS PLOT DATES BELOW
    # reference_time = datetime(2017, 12, 7, 9, 30) #INDEPENDENT
    # first_dt = datetime(2017, 12, 2, 0, 0)
    # last_dt = datetime(2018, 1, 3, 11, 50)
    # contains all test well level data and designations
    base_file = 'well_input_20180103_test.csv' #INDEPENDENT

    f_inp = well_download(base_file) #main file input, downloaded from the base_file variable
    pt_final = []

    for z in range(0, len(f_inp)):
        pt_final.append(master_process(barometric_file, f_inp[z][0], f_inp[z][1], reference_time, first_dt, last_dt))

    title_reformat = False
    master_file_list = pt_final

    #Normalizes gw elevations... comment out to see relative elevations
    for j in range(0,len(master_file_list)):    #normalize to 0 for comparison
        master_file_list[j] = normalize(master_file_list[j]) #comment this loop out for usual relative data
        title_reformat = True


    #PLOT ALL BELOW, MAIN OUTPUT CALL HERE
    poly_store = plot_multiple(master_file_list, len(master_file_list), title_reformat, f_inp)
    # plt.savefig('%s/pt_plot_%s_to_%s.jpg' %(output_folder, first_dt.strftime('%Y%m%d'), last_dt.strftime('%Y%m%d')))
    # In addition to plotting, store plotting polynomials for the dtw_predict function
    # Use this function to predict future water levels given specified input pars
    
    elapsed_days = 30 #INDEPENDENT
    gw_scoping = [] # decline in water
    name_storage = [] # well name storage
    poly_eqns = [] #polynomial equation storage
#    gw_scoping = depth_calculate(poly_store[1], elapsed_days)
#    print(gw_scoping)

    for p in range(len(f_inp)):
        gw_scoping.append(depth_calculate(poly_store[p], elapsed_days))
        poly_eqns.append(poly_store[p])
        
    for e in range(len(gw_scoping)):
        name_storage.append(f_inp[e][2])
        print('Predicted change for %s in head is %s over %s days' %(f_inp[e][2], gw_scoping[e], elapsed_days))
    
    merged_scope = [name_storage, gw_scoping, poly_store]
    
    write_my_output = write_prediction(merged_scope, output_folder, first_dt, last_dt, elapsed_days)
    



