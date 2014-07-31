import re
import datetime
import calendar

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

    i = cur_yer

    # while j < count_year:
    #     c = calendar.Calendar()
    #     c.setfirstweekday(calendar.SUNDAY)
    #     weeks = c.yeardatescalendar(i)
    #     count = 0
    #     temp = {}
    #     writeThis = []
    #     for week in weeks:
    #         for w in week:
    #             for ws in w:
    #                 if str(ws[-1]) not in temp:
    #                     count += 1
    #                     temp[str(ws[-1])] = ""
    #                     temp[str(ws[-1])] = str(ws[-1]) + " " + "00:00:00"
    #                     writeThis.append("PARTITION p" + str(count * (i + count - 1)) +
    #                                      " VALUES LESS THAN (UNIX_TIMESTAMP('"+temp[str(ws[-1])]+"'))" + "\n")
    #     fwrite.write(",".join(writeThis))
    #     i += 1
    #     j += 1

    temp_partition = {}
    for yearstocome in range(count_year):
        if i not in temp_partition:
            if i == cur_yer:
                temp_partition[i] = range(cur_mon, 13)
            elif i == cur_yer + count_year - 1:
                temp_partition[i] = range(1, cur_mon+1)
            else:
                temp_partition[i] = range(1, 13)
        else:
            pass

        i += 1

    i = cur_yer

    c = calendar.Calendar()
    c.setfirstweekday(calendar.SUNDAY)
    writeThis = []
    temp = {}
    for year in temp_partition:
        for month in temp_partition[year]:
            weeks = c.monthdatescalendar(i, month)
            count = 0
            for week in weeks:
                if str(week[-1]) not in temp:
                    count += 1
                    temp[str(week[-1])] = ""
                    temp[str(week[-1])] = str(week[-1]) + " " + "00:00:00"
                    writeThis.append("PARTITION p" + str(i) + str(month) + str(count) +
                                     " VALUES LESS THAN (UNIX_TIMESTAMP('"+temp[str(week[-1])]+"'))" + "\n")
        i += 1
    fwrite.write(",".join(writeThis))

    fwrite.write("); \n")
    fwrite.write("\n")
    fwrite.write("\n")

fwrite.close
# fread.close()
# print count
