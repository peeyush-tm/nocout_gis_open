# -*- encoding: utf-8; py-indent-offset: 4 -*-

# misc utility functions
def prepare_query(table_name=None, devices=None, data_sources=["pl", "rta"], columns=None, condition=None):
    """
    The raw query preparation.

    :param table_name:
    :param devices:
    :param data_sources:
    :param columns:
    :return query:
    """
    in_string = lambda x: "'" + str(x) + "'"
    col_string = lambda x: "`" + str(x) + "`"
    query = None
    if columns:
        columns = (",".join(map(col_string, columns)))
    else:
        columns = "*"

    extra_where_clause = condition if condition else ""

    if table_name and devices:
        query = " SELECT {0} FROM ( " \
                " SELECT {0} FROM `{1}` " \
                " WHERE `{1}`.`device_name` in ( {2} ) " \
                " AND `{1}`.`data_source` in ( {3} ) {4} " \
                " ORDER BY `{1}`.sys_timestamp DESC) as `derived_table` " \
                " GROUP BY `derived_table`.`device_name`, `derived_table`.`data_source` " \
            .format(columns,
                    table_name,
                    (",".join(map(in_string, devices))),
                    (',').join(map(in_string, data_sources)),
                    extra_where_clause.format(table_name)
        )

    return query


def prepare_row_query(table_name=None, devices=None, data_sources=["pl", "rta"], columns=None, condition=None):
    """

    :return:
    """
    in_string = lambda x: "'" + str(x) + "'"
    query = """
        select table_1.id as id,
            table_1.service_name as service_name,
            table_1.device_name as device_name,
            table_1.current_value as pl,
            table_2.current_value as rta,
            table_1.sys_timestamp as sys_timestamp,
            table_1.age as age
        from (
        select `id`,`service_name`,`device_name`,`data_source`,`current_value`,`sys_timestamp`, `age`
        from
            (
                select `id`,
                `service_name`,
                `device_name`,
                `data_source`,
                `current_value`,
                `sys_timestamp`,
                `age`
                from `performance_networkstatus`
                where
                    `performance_networkstatus`.`device_name` in ({0})
                    and `performance_networkstatus`.`data_source` in ( 'pl' )
            ) as `derived_table`
        ) as table_1
        join (
            select `id`,`service_name`,`device_name`,`data_source`,`current_value`,`sys_timestamp`
            from
                (
                    select `id`,
                    `service_name`,
                    `device_name`,
                    `data_source`,
                    `current_value`,
                    `sys_timestamp`
                    from `performance_networkstatus`
                    where
                        `performance_networkstatus`.`device_name` in ({0})
                        and `performance_networkstatus`.`data_source` in ( 'rta' )
              ) as `derived_table`
        ) as table_2
        on (table_1.device_name = table_2.device_name
            and table_1.data_source != table_2.data_source
            and table_1.sys_timestamp = table_2.sys_timestamp
            )
        group by (table_1.device_name);
    """.format(",".join(map(in_string, devices)))

    return query
