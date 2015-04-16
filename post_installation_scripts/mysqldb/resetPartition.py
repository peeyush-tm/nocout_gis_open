import re
import datetime
import calendar

count_year = int(raw_input("how many years:>"))  # license validity

partitionTableList = [
    "performance_eventinventory",
    "performance_eventmachine",
    "performance_eventnetwork",
    "performance_eventnetworkdaily",
    "performance_eventnetworkmonthly",
    "performance_eventnetworkweekly",
    "performance_eventnetworkyearly",
    "performance_eventservice",
    "performance_eventservicedaily",
    "performance_eventserviceweekly",
    "performance_eventserviceyearly",
    "performance_networkavailabilitydaily",
    "performance_networkavailabilitymonthly",
    "performance_networkavailabilityweekly",
    "performance_networkavailabilityyearly",
    "performance_performanceinventory",
    "performance_performanceinventorydaily",
    "performance_performanceinventorymonthly",
    "performance_performanceinventoryweekly",
    "performance_performanceinventoryyearly",
    "performance_performancemachine",
    "performance_performancemetric",
    "performance_performancenetwork",
    "performance_performancenetworkbihourly",
    "performance_performancenetworkdaily",
    "performance_performancenetworkhourly",
    "performance_performancenetworkmonthly",
    "performance_performancenetworkweekly",
    "performance_performancenetworkyearly",
    "performance_performanceservice",
    "performance_performanceservicebihourly",
    "performance_performanceservicedaily",
    "performance_performanceservicehourly",
    "performance_performanceservicemonthly",
    "performance_performanceserviceweekly",
    "performance_performanceserviceyearly",
    "performance_performancestatus",
    "performance_performancestatusdaily",
    "performance_performancestatusmonthly",
    "performance_performancestatusweekly",
    "performance_performancestatusyearly",
    "performance_utilization",
    "performance_utilizationdaily",
    "performance_utilizationmonthly",
    "performance_utilizationweekly",
    "performance_utilizationyearly",
]

skip_partitioning = [
    "performance_eventstatus",
    "performance_inventorystatus",
    "performance_machinestatus",
    "performance_networkstatus",
    "performance_servicestatus",
    "performance_status",
    "performance_utilizationstatus",
    "performance_topology",
    "performance_wimaxtopology",
]


now = datetime.datetime.now()
cur_yer = now.year
cur_mon = now.month

if cur_mon > 1:
    count_year += 1

years_list = range(cur_yer, cur_yer + count_year + 1)

table_column = "sys_timestamp"

for ptable in partitionTableList:


    if "daily" in ptable:
        pass
    if "weekly" in ptable:
        pass
    if "monthly" in ptable:
        continue
    if "yearly" in ptable:
        continue
    if ptable in skip_partitioning:
        continue

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

    temp_partition = {}

    for year in years_list:
        if year not in temp_partition:
            if year == cur_yer:
                temp_partition[year] = range(cur_mon, 13)
            elif year == (cur_yer + count_year):
                temp_partition[year] = range(1, cur_mon+1)
            else:
                temp_partition[year] = range(1, 13)

    # print temp_partition

    c = calendar.Calendar()
    c.setfirstweekday(calendar.MONDAY)
    writeThis = []
    temp = {}
    for year in years_list:
        for month in temp_partition[year]:
            count = 0
            weeks = c.monthdatescalendar(year, month)
            for week in weeks:
                if str(week[-1]) not in temp:
                    count += 1
                    temp[str(week[-1])] = ""
                    temp[str(week[-1])] = str(week[-1]) + " " + "00:00:00"
                    writeThis.append("PARTITION p" + str(year) + str(month) + str(count) +
                                     " VALUES LESS THAN (UNIX_TIMESTAMP('"+temp[str(week[-1])]+"'))" + "\n")

    fwrite.write(",".join(writeThis))

    fwrite.write("); \n")
    fwrite.write("\n")
    fwrite.write("\n")

fwrite.close
# fread.close()
# print count
