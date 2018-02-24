##############################################################################
#
# Program:           linreg.py
# Author:            Jason Van Kerkhoven
# Date of Update:    24/02/2018
# Version:           1.0.0
#
# Purpose:           TODO
#
# Arguments:         SAMPLE_START SAMPLE_END ~PATH/database.db
#
#                    SAMPLE_START, SAMPLE_END must be form yyyy-mm-dd
#                    [start in INCLUSIVE, end is EXCLUSIVE]
#
#                    RESULT_TABLE_NAME is where the resulting dataset is stored
#
# Flags:             -v         ==> toggles verbose on
#                    -a         ==> enable audible beeping for completion
#                    -f str     ==> set path for figure dump, default use current directory
#
##############################################################################


# import libraries
import numpy as np
import sys
import sqlite3
import time
import matplotlib.pyplot as plotter
import matplotlib.dates as dates
import platform
from scipy import stats
from time import localtime, strftime



###############################################################################
# DECLARING FUNCTIONS
###############################################################################

# verbose print
def printv(string):
    if verbose:
        print(string)

# beep 'done' in morse code at aprox. 20wpm
def beepbeep(freq):
    for blip in (True,False,False,True,True,True,True,False,False):
        if (blip):
            beep(freq, 0.2)
        else:
            beep(freq, 0.1)

# beep
def beep(freq, dur):
    # for windows
    if (platform.system() == 'Windows'):
        import winsound
        winsound.Beep(freq, dur*1000)
    # linux and mac OS
    else:
        import os
        os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (dur, freq))




###############################################################################
# PROGRAM START
###############################################################################
# initialize parameters
verbose = False
figPath = ''
beepFlag = False

# load arguments
printv('Running ' + sys.argv[0] + ' ...')
startTime = str(sys.argv[1])
endTime = str(sys.argv[2])
dbPath = str(sys.argv[3])

# check for flags
flags = sys.argv
for i in range(0, 4):
    del flags[0]
while (len(flags) > 0):
    flag = flags.pop(0)
    # verbose flag
    if (flag == '-v' or flag == '--verbose'):
        verbose = True
    # set path for figure
    elif (flag == '-f' or flag == '--fig'):
        figPath = flags.pop(0)+'/'
    # enable beeps (good for long jobs)
    elif (flag == '-a' or flag == '-audible'):
        beepFlag = True
    else:
        print ('ERROR: Unknown flag')
        sys.exit()

# connect to database and create table
printv('Accessing database...')
dbConnection = sqlite3.connect(dbPath, 60)
db = dbConnection.cursor()

# convert yyyy-mm-dd to unix timstamps
unixStart = int(time.mktime(time.strptime(startTime, '%Y-%m-%d')))
unixEnd = int(time.mktime(time.strptime(endTime, '%Y-%m-%d')))-1

# get data in range
printv('Fetching data...')
sql = "SELECT time_stamp,usage FROM usages WHERE time_stamp BETWEEN " + str(unixStart) + " AND " + str(unixEnd) + " ORDER BY time_stamp;"
rows = db.execute(sql);

# format data into usable array
x = []
y = []
orginalData = []
for row in rows:
    x.append(int(row[0]))       # TODO x values need to be changed or scaled
    y.append(float(row[1]))
    orginalData.append((int(row[0]), float(row[1])))
printv('Done! ' + str(len(x)) + ' data points found in range [' + str(startTime) + ', ' + str(endTime) + ')')

# apply linear regression
printv('Computing least-squares...')
runTime = time.time();
m, b, r, p, stdErr = stats.linregress(x,y)
runTime = time.time() - runTime
printv('Done!')
printv('Computation time: %.4f sec' % runTime)

# round numbers to precision
m = round(m, 4)
b = round(b, 4)
r = round(r, 4)
p = round(p, 4)
stdErr = round(stdErr, 4)

# print ending details
print('---------------- RESULTS ----------------')
print('Slope:                             ' + str('%.4f' % m))
print('Y-Intercept:                       ' + str('%.4f' % b))
print('Coeff Correlation   (r):           ' + str('%.4f' % r))
print('Coeff Determination (r^2)):        ' + str('%.4f' % r**2))
print('Two-Tailed p Value:                ' + str('%.4f' % p))
print('   for null hypothesis of m=0')
print('Estimator Error:                   ' + str('%.4f' % stdErr))

print('\u001b[32mf(x) = ' + str('%.4f' % m) + '*x + ' + str('%.4f' % b) + '\u001b[0m')
print('-----------------------------------------')

# print graph
figName = 'linreg_' + strftime("%y-%m-%d-%H-%M-%S", localtime()) + '.png'
printv('Generating Plot @ ' + figPath+figName + ' ...')
fig = plotter.figure(figsize=(16,9))
p1 = fig.add_subplot(111)
p1.scatter(*zip(*orginalData), s=3.3**2, marker="o", label='Original Data')

# configure plot TODO show the line
p1.legend()
p1.set_title('Usages in range [' + startTime + ', ' + endTime + ') with Linear Regression')
p1.set_xlabel('Time')           # TODO change when x is changed
p1.set_ylabel('Usage (kWh)')
plotter.savefig(figPath + figName, format='png', bbox_inches='tight')
printv('Done!')

# notify and show figure
if(beepFlag):
    beepbeep(550)
if verbose:
    plotter.show()
