# General
Various tools and programs used for data analysis of power usage statistics. The overall suite of tools is very much underdeveloped at the moment of writing. All tools/programs make use of a common database format and schema.

It should be noted, unless explicitly stated otherwise, all reference to Python are specifically for python3, and SQLite/database to sqlite3.




# Database Schema
The database all programs/tools use is assumed to contain the **source** data in a table named **usage**. The table stores the usage values using UNIX timestamps as opposed to human-readable timestamps in order to simplify the data processing. The usage table is assumed to be adhear to the following structure:
```sql
CREATE TABLE usages (
  time_stamp INTEGER,
  house_id INTEGER,
  usage NUMERIC
);
```

In order to initialize an empty usage table (or clear an existing one) the `init.sql` file located in the `sql` directory can be used. Use of `init.sql` can be done trivially as:
```
sudo sqlite3 database.db < init.sql
```




# Manual
## Building an SQL File
The `.sql` file used to populate the original usages database is generated from raw data stored as a `.csv`. The program reads the data in the CSV, from start until end (or a specified end-date), and creates the needed `INSERT` statements required for table population. The CSV is assumed to be of format:
```
Time,Apartment1,Apartment2,Apartment3,Apartment4,Apartment5
```

The program is called as:
```
python3 build-sql.py [CSV] [SQL]
```

In which `CSV` is the relative path/name of the raw CSV file, and `SQL` is the relative path/name of the generated SQL file (program output).

| CLI Parameters | Default | Description |
|----------------|---------|-------------|
| `[CSV]` | n/a | Relative path/name of the input CSV |
| `[SQL]` | n/a | Relative path/name of the output SQL file |
| `-d` | To the end of file | **Exclusive** end date for the data to be read from the CSV |

## Linear Regression Model
This program reads a set of usage values and attempts to find the "line of best fit" for it. It outputs a graphical result of the line-of-best-fit superimposed on the dataset as well as the calculated:
* Slope
* Y-Intercept
* Coefficient of correlation (r)
* Coefficient of determination (r^2)
* Two-tailed p value for null hypothesis m=0
* Error estimator
* Linear equation `y = mx + b`

The program is called as:
```
sudo python3 [S] [E] [DB]
```

In which `[S]` is the start date of the data and `[E]` is the end date of the data. Both dates are required to be formated as `YYYY-MM-DD`. The start date is **inclusive**, while the end date is **exclusive**. For example, a range of 2015-01-01 to 2015-01-04 would read data with timestamps on a date {2015-01-01, 2015-01-02, 2015-01-03}.

The `[DB]` flag is the relative path to the SQLite3 database, in which the data to be processed is stored.

An example of the program being run over selective data from the first week of February, 2015 is given as follows:
```
sudo python3 2015-02-01 2015-02-08 dat/sample-data.db
```

| CLI Parameters | Default | Description |
|----------------|---------|-------------|
| `[S]` | n/a | **Inclusive** start date of the data to be processed |
| `[E]` | n/a | **Exclusive** end date of the data to be processed |
| `[DB]` | n/a | Full relative path/name to the SQLite3 database file containing the data. Also the database where the processed data will be stored |
| `-v` | Off | Toggles verbose on |
| `-a` | Off | Enable audible beeping upon program completion |
| `-f [F]` | Current Directory | Set the **path** *(not name)* for figure dump |

## K-Mean Clusters Pre-Processing

This program reads a set of *N* values, and outputs a set of *K* values, in which *K < N*. The program then graphs and stores the result. This script is computationally expensive, and for most configurations, will take a long duration of time to run. The program is called as:
```
sudo python3 [S] [E] [DB] [T]
```

In which `[S]` is the start date of the data and `[E]` is the end date of the data. Both dates are required to be formated as `YYYY-MM-DD`. The start date is **inclusive**, while the end date is **exclusive**. For example, a range of 2015-01-01 to 2015-01-04 would read data with timestamps on a date {2015-01-01, 2015-01-02, 2015-01-03}.

The `[DB]` flag is the relative path to the SQLite3 database, in which the data to be processed is stored.

The `[T]` flag is the name of the table the resulting data set will stored in, using the aforementioned schema. It should be noted that if a table of name `[T]` already exists, it will be dropped without warning. `[T]` also denotes the filename the resulting figure will be saved as.

| CLI Parameters | Default | Description |
|----------------|---------|-------------|
| `[S]` | n/a | **Inclusive** start date of the data to be processed |
| `[E]` | n/a | **Exclusive** end date of the data to be processed |
| `[DB]` | n/a | Full relative path/name to the SQLite3 database file containing the data. Also the database where the processed data will be stored |
| `[T]` | n/a | Name of the table to store processed data in. Also the filename of the resulting figure |
| `-v` | Off | Toggles verbose on |
| `-vv` | Off | Toggles maximum verbosity |
| `-p` | On | Disable using multiple cores for computation |
| `-a` | Off | Enable audible beeping upon program completion |
| `-k [K]` | 10 | Set k value |
| `-l [L]` | 1 | Number times the algorithm is fully run. Higher values tend to lead to better results |
| `-i [I]` | 500 | Max number of iterations per algorithm executions. Higher values tend to lead to better results |
| `-f [F]` | Current Directory | Set the **path** *(not name)* for figure dump |
