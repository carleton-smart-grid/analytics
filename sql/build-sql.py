##############################################################################
#
# Program:           build-sql.py
# Author:            Jason Van Kerkhoven
# Date of Update:    28/11/2017
# Version:           1.0.1
#
# Purpose:           Generate SQL files from CSV rawdata.
#
# Arugments:         ~PATH/usagedat.csv ~PATH/output.sql
#
# Flags:             -d yyyy-mm-dd      ==> stop sql at date (exclusive)
#
##############################################################################


# import libraries
import csv
import sys
import time


# Program constants
YEAR_CONSTANT = '20'

# call pathing arguments ~PATH/usagedat.csv
# get program arguments
csvPath = sys.argv[1]
fileName = sys.argv[2]

# check for flags
endDate = None
flags = sys.argv
for i in range(0, 3):
    del flags[0]
while (len(flags) > 0):
    flag = flags.pop(0)
    if (flag == '-d'):
        endDate = str(flags.pop(0))


# open the csv file and skip headers, get file newline size
csvFile = open(csvPath, 'r')
reader = csv.reader(csvFile)
current = next(reader, None)

# create/open/setup file for writing
sqlFile = open(fileName, 'w')
sqlFile.write('DROP TABLE IF EXISTS usages;\n')
sqlFile.write('CREATE TABLE usages (time_stamp INTEGER, house_id INTEGER, usage NUMERIC);\n');
#sqlFile.write('CREATE TABLE usages (date DATE, time TIME, house_id INTEGER, usage NUMERIC);\n');

# read-write loop
print('Building SQL...')
current = next(reader, None)
while(current != None):
    # get current csv data
    timeRaw = current[0]
    usages = [current[1], current[2], current[3], current[4], current[5]]

    # parse date-time into correct format
    dateTime = timeRaw.split(' ')
    dmy = dateTime[0].split('-')
    dateFormated = YEAR_CONSTANT + dmy[2] + '-' + dmy[1] + '-' + dmy[0]

    # check terminating
    if (dateFormated == endDate):
        break;

    # insert each houseIDs usages (1, 2, 3, 4, 5)
    for id in range(1, 6):
        timestamp = int(time.mktime(time.strptime(dateFormated+' '+dateTime[1], '%Y-%m-%d %H:%M')))
        sql = "INSERT INTO usages VALUES(" + str(timestamp) + "," + str(id) + "," + str(usages[id-1]) + "); -- " + dateFormated + " " + dateTime[1] +"\n"
        #sql = "INSERT INTO usages values(DATE('" + dateFormated + "'),TIME('" + dateTime[1] + "')," + str(id) + "," + str(usages[id-1]) + ");\n" #SQL FOR INSERT AS DATE AND TIME INTO DATE AND TIME COLUMNS
        sqlFile.write(sql);

    # get next values
    current = next(reader, None)

# Print completion
print('Complete!')
