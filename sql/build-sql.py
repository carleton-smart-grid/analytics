##############################################################################
#
# Class:             build-sql.py
# Author:            Jason Van Kerkhoven
# Date of Update:    22/11/2017
# Version:           1.0.0
#
# Purpose:           Generate SQL files from CSV rawdata
#
# Arugments:         ~PATH/usagedat.csv
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

# open the csv file and skip headers, get file newline size
csvFile = open(csvPath, 'r')
reader = csv.reader(csvFile)
current = next(reader, None)

# create/open/setup file for writing
sqlFile = open('populate-12m.sql', 'w')
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
