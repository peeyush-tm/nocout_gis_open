SELECT table_1.id as id,
            table_1.service_name as service_name,
            table_1.device_name as device_name,
            table_1.current_value as pl,
            table_2.current_value as rta,
            table_1.sys_timestamp
        from (
        SELECT `id`,`service_name`,`device_name`,`data_source`,`current_value`,`sys_timestamp`
        FROM
            (
                SELECT `id`,
                `service_name`,
                `device_name`,
                `data_source`,
                `current_value`,
                `sys_timestamp`
                FROM `performance_networkstatus`
                WHERE
                    `performance_networkstatus`.`device_name` in ( select device_name from device_device )
                    AND `performance_networkstatus`.`data_source` in ( 'pl','rta' )
            ORDER BY `performance_networkstatus`.sys_timestamp DESC) as `derived_table`
        GROUP BY `derived_table`.`device_name`, `derived_table`.`data_source`
        ) as table_1
        join (
            SELECT `id`,`service_name`,`device_name`,`data_source`,`current_value`,`sys_timestamp`
            FROM
                (
                    SELECT `id`,
                    `service_name`,
                    `device_name`,
                    `data_source`,
                    `current_value`,
                    `sys_timestamp` FROM
                    `performance_networkstatus`
                    WHERE
                    `performance_networkstatus`.`device_name` in ( select device_name from device_device )
                    AND `performance_networkstatus`.`data_source` in ( 'pl','rta' )
                ORDER BY `performance_networkstatus`.sys_timestamp DESC) as `derived_table`
            GROUP BY `derived_table`.`device_name`, `derived_table`.`data_source`
        ) as table_2
        on (table_1.device_name = table_2.device_name and table_1.data_source != table_2.data_source)
        group by (table_1.device_name)
LIMIT 100000