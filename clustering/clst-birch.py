##############################################################################
#
# Class:             clst-birch.py
# Author:            Jason Van Kerkhoven
# Date of Update:    14/10/2017
# Version:           1.0.0
#
# Purpose:           TODO
#
# Arguments:         SAMPLE_START SAMPLE_END ~PATH/database.db TABLE_NAME
#
#                    SAMPLE_START, SAMPLE_END must be form yyyy-mm-dd
#                    **start in INCLUSIVE, end is EXCLUSIVE
#
#                    TABLE_NAME is where the resulting dataset is stored, and is
#                    used for labeling the resulting figure image file
#
# Flags:             -v         ==> toggles verbose on
#                    -k int     ==> set number of clusters, default 10
#                    -b int     ==> set max. number CF subclusters per node, default 50
#                    -f str     ==> set path for figure dump, default use current directory
#
##############################################################################


# import libraries
import numpy as np
from sklearn.cluster import Birch
import sys
import sqlite3
import time
import matplotlib.pyplot as plotter
import matplotlib.dates as dates



###############################################################################
# DECLARING FUNCTIONS
###############################################################################

# verbose print
def printv(string):
    if verbose:
        print(string)





###############################################################################
# PROGRAM START
###############################################################################

# initialize parameters
verbose = False
k = 10
branching = 50
figPath = ''

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
    # set k
    elif flag == '-k':
        k = int(flags.pop(0))
    # set branching factor
    elif flag == '-b':
        braching = int(flags.pop(0))
    # set path for figure
    elif flag == '-f':
        figPath = flags.pop(0)+'/'

# print starting details
printv('------------------------------------------')
printv('Start:                        ' + startTime)
printv('End:                          ' + endTime)
printv('Output table/figure:          ' + tableName + '\n')
printv('BIRCH Clusters:               ' + str(k))
printv('Branching factor:             ' + str(branching))
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

# compute BIRCH clusters
printv('Computing BIRCH clusters...')
runTime = time.clock();
birch = Birch(branching_factor=branching, n_clusters=k).fit(dataset)#TODO research threshold factor param
runTime = time.clock() - runTime
printv('Done!')
printv('Time to completion: ' + str(runTime) + 's')

# plot data
printv('Generating Plot...')
fig = plotter.figure(figsize=(16,9))
p1 = fig.add_subplot(111)
p1.scatter(*zip(*dataset), s=3.3**2, marker="o", label='Original Data')
p1.scatter(birch), s=3.3**2, marker="^", label='BIRCH Subcluster Centroids')

# configure plot
p1.legend()
p1.set_title('BIRCH Subcluster Centroids with k=' + str(k))
p1.set_xlabel('Time')
p1.set_ylabel('Usage (kWh)')
print(figPath+'figure_'+tableName+'.png')
plotter.savefig(figPath+'figure_'+tableName+'.png', format='png', bbox_inches='tight')
printv('Done!')
if verbose:
    plotter.show()
