import re
import datetime

# fread = open("complete_db_structure.sql", 'r')
# filedata = fread.readlines()

count = 0
count_year = int(raw_input("how many years:>"))  # license validity
now = datetime.datetime.now()

cur_yer = now.year
cur_mon = now.month

partitionTableList = [
    "performance_eventinventory",
    "performance_eventmachine",
    "performance_eventnetwork",
    "performance_eventservice",
    "performance_eventstatus",
    "performance_inventorystatus",
    "performance_machinestatus",
    "performance_networkstatus",
    "performance_performanceinventory",
    "performance_performancemachine",
    "performance_performancemetric",
    "performance_performancenetwork",
    "performance_performanceservice",
    "performance_performancestatus",
    "performance_servicestatus",
    "performance_status"
]

if cur_mon != 1:
    count_year += 1

table_column = "sys_timestamp"

for ptable in partitionTableList:
    count += 1
    fwrite = open("resetPartition.sql", 'a')

    # ##
    # ALTER TABLE  `nocout_dev`.`performance_performancenetwork` DROP PRIMARY KEY ,
    # ADD PRIMARY KEY (  `id` ,  `sys_timestamp` )
    # ##

    fwrite.write('ALTER TABLE `'+ptable+'` DROP PRIMARY KEY , \n')
    fwrite.write('ADD PRIMARY KEY (  `id` ,  `sys_timestamp` ) ; \n')

    fwrite.write("ALTER TABLE " + ptable + "\n")
    fwrite.write(
        "PARTITION BY RANGE(sys_timestamp)" + "\n")
    fwrite.write("(" + "\n")
    j = 0
    i = cur_yer
    while j < count_year:
        if j == 0 and cur_mon != 1:
            x = cur_mon - 1
            y = 12
        elif j == count_year - 1 and cur_mon != 1:
            x = 0
            y = cur_mon + 1
        else:
            x = 0
            y = 12
        while x < y:
            x += 1
            writeThis = "PARTITION p" + str(x * i + x - 1) + \
                " VALUES LESS THAN (UNIX_TIMESTAMP(" + "'" + str(i) + "-"\
                + str(x) + "-" + "01" + " 00:00:00'" + "))"
            fwrite.write(writeThis)
            if j == count_year - 1 and x == y:
                fwrite.write("\n")
            else:
                fwrite.write(", \n")
        i += 1
        j += 1
    fwrite.write("); \n")
    fwrite.write("\n")
    fwrite.write("\n")

fwrite.close
# fread.close()
# print count
