##############################################################################
#
# Class:             clst-kmean.py
# Author:            Jason Van Kerkhoven
# Date of Update:    24/11/2017
# Version:           1.0.2
#
# Purpose:           TODO
#
# Arguments:         SAMPLE_START SAMPLE_END ~PATH/database.db TABLE_NAME
#
#                    SAMPLE_START, SAMPLE_END must be form yyyy-mm-dd
#                    **start in INCLUSIVE, end is EXCLUSIVE
#
#                    TABLE_NAME is where the resulting dataset is stored
#
# Flags:             -v         ==> toggles verbose on [use -vv for extra verbose]
#                    -p         ==> disable using multiple cores, default use all cores
#                    -a         ==> enable audible beeping for completion
#                    -k int     ==> set k value, default 10
#                    -l int     ==> number of full algorithm runs, default 1
#                    -i int     ==> max iterations per algorithm executions, default 500
#                    -f str     ==> set path for figure dump, default use current directory
#
##############################################################################


# import libraries
import numpy as np
from sklearn.cluster import KMeans
import sys
import sqlite3
import time
import matplotlib.pyplot as plotter
import matplotlib.dates as dates
import platform



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
xtrv = 0
verbose = False
k = 100
maxl = 1
maxi = 300
cpu = -1
figPath = ''
beepFlag = False

# load arguments
printv('Running ' + sys.argv[0] + ' ...')
startTime = str(sys.argv[1])
endTime = str(sys.argv[2])
dbPath = str(sys.argv[3])
tableName = str(sys.argv[4])

# check for flags
flags = sys.argv
for i in range(0, 5):
    del flags[0]
while (len(flags) > 0):
    flag = flags.pop(0)
    # verbose flag
    if flag == '-v':
        verbose = True
    # extra verbose flag
    elif flag == '-vv':
        xtrv = 1
        verbose = True
    # set k
    elif flag == '-k':
        k = int(flags.pop(0))
    # set maximum iterations per executions
    elif flag == '-i':
        maxi = int(flags.pop(0))
    # set maximum number of algorithm executions
    elif flag == '-l':
        maxl = int(flags.pop(0))
    # set parallel computations on/off
    elif flag == '-p':
        cpu = 1
    # set path for figure
    elif flag == '-f':
        figPath = flags.pop(0)+'/'
    # enable beeps (good for long jobs)
    elif flag == '-a':
        beepFlag = True

# print starting details
printv('------------------------------------------')
printv('Start:                        ' + startTime)
printv('End:                          ' + endTime)
printv('Parallel computations:        ' + str((cpu == -1)))
printv('Output table/figure:          ' + tableName + '\n')
printv('Centroid amount (k):          ' + str(k))
printv('Max iterations per execution: ' + str(maxi))
printv('Full execution loops:         ' + str(maxl))
printv('------------------------------------------')

# connect to database and create table
printv('Accessing database...')
dbConnection = sqlite3.connect(dbPath, 60)
db = dbConnection.cursor()
db.execute('DROP TABLE IF EXISTS ' + tableName + ';')
db.execute('CREATE TABLE ' + tableName + '(time_stamp INTEGER, usage NUMERIC);')
dbConnection.commit()

# convert yyyy-mm-dd to unix timstamps
startTime = int(time.mktime(time.strptime(startTime, '%Y-%m-%d')))
endTime = int(time.mktime(time.strptime(endTime, '%Y-%m-%d')))-1

# get data in range
printv('Fetching data...')
sql = "SELECT time_stamp,usage FROM usages WHERE time_stamp BETWEEN " + str(startTime) + " AND " + str(endTime) + " ORDER BY time_stamp;"
rows = db.execute(sql);

# format data into usable array
dataset = []
for row in rows:
    dataset.append( (int(row[0]), float(row[1])) )
dataset = np.asarray(dataset)
printv('Done! ' + str(len(dataset)) + ' data points found')

# caluclate centroids
printv('Computing k-mean centroids...')
runTime = time.time();
kmeans = KMeans(n_clusters=k, n_init=maxl, max_iter=maxi, verbose=xtrv, n_jobs=cpu, tol=0.0001).fit(dataset)
printv('Av. Inertia:   ' + str(kmeans.inertia_))
runTime = time.time() - runTime
printv('Done!')
printv('Computation time: %.4f sec' % runTime)

# save to db
printv('Saving to database...')
for centroid in kmeans.cluster_centers_:
    db.execute('INSERT INTO ' + tableName + ' VALUES(' + str(int(centroid[0])) + ',' + str(centroid[1]) + ');')
dbConnection.commit()
printv('Done!')

# plot data
printv('Generating Plot...')
fig = plotter.figure(figsize=(16,9))
p1 = fig.add_subplot(111)
p1.scatter(*zip(*dataset), s=3.3**2, marker="o", label='Original Data')
p1.scatter(*zip(*kmeans.cluster_centers_), s=3.3**2, marker="^", label='k-Mean Centroids')

# configure plot
p1.legend()
p1.set_title('K-Mean Centroids with k=' + str(k))
p1.set_xlabel('Time')
p1.set_ylabel('Usage (kWh)')
print(figPath+'figure_'+tableName+'.png')
plotter.savefig(figPath+'figure_'+tableName+'.png', format='png', bbox_inches='tight')
printv('Done!')

# notify and show figure
if(beepFlag):
    beepbeep(550)
if verbose:
    plotter.show()
