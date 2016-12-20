from mysql.connector import connect
from start.start import app 
from handlers.db_ops import *
from formatting import inventory
from collections import defaultdict 
#from celery import Task
# Get topology data in hierarchy for which backhaul exists.
query1 = """
SELECT
	backhaul.id as BackhaulID,	
	IF(isnull(backhaul.bh_circuit_id), 'NA', backhaul.bh_circuit_id ) as ior,
	IF(isnull(backhaul.ttsl_circuit_id), 'NA', backhaul.ttsl_circuit_id) as bso_ckt,
	IF(isnull(bsswitch_device.parent_port), 'NA', bsswitch_device.parent_port) as BSswitchParentPort,
	IF(isnull(pe_device.ip_address), 'NA', pe_device.ip_address) as PE_IP,
	IF(isnull(aggregator_device.ip_address), 'NA', aggregator_device.ip_address) as AggregationSwitchIP,
	IF(isnull(popconverter_device.ip_address), 'NA', popconverter_device.ip_address) as POPconverterIP,
	IF(isnull(pop_device_tech.name), 'NA', pop_device_tech.name) as POPconverterTech,
	IF(isnull(pop_device_type.name), 'NA', pop_device_type.name) as POPconverterType,
	IF(isnull(pop_device_vendor.name), 'NA', pop_device_vendor.name) as POPconverterDeviceVendor,
	IF(isnull(pop_parent.ip_address), 'NA', pop_parent.ip_address) as POPconverterParentIP, 
	IF(isnull(popconverter_device.parent_port), 'NA',popconverter_device.parent_port) as POPconverterParentPort, 
	IF(isnull(popparent_devicetype.name), 'NA', popparent_devicetype.name) as POPconverterParentType,
	IF(isnull(bsconverter_device.ip_address), 'NA', bsconverter_device.ip_address) as BTSconverterIP,
	IF(isnull(bsconverter_device_tech.name), 'NA', bsconverter_device_tech.name) as BTSconverterTech,
	IF(isnull(bsconverter_device_type.name), 'NA', bsconverter_device_type.name) as BTSconverterType,
	IF(isnull(bsconverter_device_vendor.name), 'NA', bsconverter_device_vendor.name) as BTSconverterDeviceVendor,
	IF(isnull(bsconverter_parent.ip_address), 'NA', bsconverter_parent.ip_address) as BTSconverterParentIP,
	IF(isnull(bsconverter_device.parent_port), 'NA', bsconverter_device.parent_port) as BTSconverterParentPort,
	IF(isnull(bsconverterparent_devicetype.name), 'NA', bsconverterparent_devicetype.name) as BTSconverterParentType,
	IF(isnull(bh_device.ip_address), 'NA', bh_device.ip_address) as backhaul_configured_on_ip,
	IF(isnull(bsswitch_device.ip_address), 'NA', bsswitch_device.ip_address) as BSswitchIP,
	IF(isnull(bsswitch_device_tech.name), 'NA', bsswitch_device_tech.name) as BSswitchTech,
	IF(isnull(bsswitch_device_type.name), 'NA', bsswitch_device_type.name) as BSswitchType,
	IF(isnull(bsswitch_device_vendor.name), 'NA', bsswitch_device_vendor.name) as BSswitchDeviceVendor,
	IF(isnull(bsswitch_parent.ip_address), 'NA', bsswitch_parent.ip_address) as BSswitchParentIP,
	IF(isnull(bsswitchparent_devicetype.name), 'NA', bsswitchparent_devicetype.name) as BSswitchParentType,
	IF(isnull(bsswitch_device.parent_port), 'NA', bsswitch_device.parent_port) as BSswitchParentPort,
	IF(isnull(pop_org.alias), 'NA', pop_org.alias) as POPconverterorg,
	IF(isnull(bsconverter_org.alias), 'NA', bsconverter_org.alias) as BTSconverterorg,
	IF(isnull(bsswitch_org.alias), 'NA', bsswitch_org.alias) as BSswitchorg,
	
	GROUP_CONCAT(CONCAT(
		IF(isnull(bs.id), 'NA', bs.id), '|',
		IF(isnull(bs.alias), 'NA', bs.alias), '|',
		IF(isnull(bsswitch_device.ip_address), 'NA', bsswitch_device.ip_address), '|',
		IF(isnull(city.city_name), 'NA', city.city_name), '|',
		IF(isnull(state.state_name), 'NA', state.state_name), '|',
		IF(isnull(region.country_name), 'NA', region.country_name),'|',
		IF(isnull(bsswitch_parent.ip_address), 'NA', bsswitch_parent.ip_address),'|',
		IF(isnull(bsswitchparent_devicetype.name), 'NA', bsswitchparent_devicetype.name),'|',
		IF(isnull(organization.alias), 'NA', organization.alias)
	) SEPARATOR '-|-|-') AS BASESTATION,
	GROUP_CONCAT(CONCAT(
		IF(isnull(sect.id), 'NA', sect.id),'|',
	        IF(isnull(sect.sector_id), 'NA', sect.sector_id), '|',
		IF(isnull(bs_device_tech.name), 'NA', bs_device_tech.name), '|',
		IF(isnull(bs_device_vendor.name), 'NA', bs_device_vendor.name), '|',
		IF(isnull(bs_device_type.name), 'NA', bs_device_type.name), '|',
		IF(isnull(device.ip_address), 'NA', device.ip_address), '|',
		IF(isnull(device.device_name), 'NA', device.device_name),'|',
		IF(isnull(device.id), 'NA', device.id),'|',
		IF(isnull(device_parent.ip_address), 'NA', device_parent.ip_address),'|',
		IF(isnull(deviceparent_devicetype.name), 'NA', deviceparent_devicetype.name),'|',
        	IF(isnull(ckt.circuit_id), 'NA', ckt.circuit_id), '|',
        	IF(isnull(customer.alias), 'NA', customer.alias), '|',
        	IF(isnull(device.parent_type), 'NA', device.parent_type),'|',
        	IF(isnull(device.parent_port), 'NA', device.parent_port),'|',
		IF(isnull(sect.sector_configured_on_port_id), 'NA', sect.sector_configured_on_port_id),'|',
		IF(isnull(device_org.alias), 'NA', device_org.alias)
	) SEPARATOR '-|-|-') AS SECT_STR,
	GROUP_CONCAT(CONCAT(
		IF(isnull(sect.id), 'NA', sect.id),'|',
		IF(isnull(ss.id), 'NA', ss.id),'|',
		IF(isnull(ss_device.id), 'NA', device_ss.id),'|',
		IF(isnull(ss_device.device_name), 'NA', device_ss.device_name),'|',
		IF(isnull(ss_device.ip_address), 'NA', device_ss.ip_address), '|',
		IF(isnull(ss_device_type.name), 'NA', ss_device_type.name), '|',
        	IF(isnull(ckt.circuit_id), 'NA', ckt.circuit_id), '|',
        	IF(isnull(customer.alias), 'NA', customer.alias), '|',
		IF(isnull(ss_device_tech.name), 'NA', ss_device_tech.name), '|',
        	IF(isnull(ss.name), 'NA', ss.name), '|',
        	IF(isnull(device.ip_address), 'NA', device.ip_address),'|',
		IF(isnull(bs_device_type.name), 'NA', bs_device_type.name), '|',
		IF(isnull(ss_device_vendor.name), 'NA', ss_device_vendor.name)
	) separator '-|-|-') AS SubStation
	FROM
		inventory_backhaul AS backhaul
	LEFT JOIN
		device_device AS bh_device
	ON
		backhaul.bh_configured_on_id = bh_device.id
	INNER JOIN
		inventory_basestation AS bs
	ON
		bs.backhaul_id = backhaul.id
	LEFT JOIN
		device_device as aggregator_device
	on
		backhaul.aggregator_id = aggregator_device.id
	LEFT JOIN
		device_device as popconverter_device
	on
		popconverter_device.id = backhaul.pop_id
	LEFT JOIN
		device_devicetechnology AS pop_device_tech
	ON
		popconverter_device.device_technology = pop_device_tech.id
	LEFT JOIN
		device_devicetype AS pop_device_type
	ON
		popconverter_device.device_type = pop_device_type.id
	LEFT JOIN
		device_devicevendor as pop_device_vendor
	on
		popconverter_device.device_vendor = pop_device_vendor.id
	LEFT JOIN
		device_device as pop_parent
	ON
		popconverter_device.parent_id = pop_parent.id
	LEFT JOIN 
		device_devicetype as popparent_devicetype
	ON
		pop_parent.device_type = popparent_devicetype.id
	LEFT JOIN
		organization_organization as pop_org
	ON     
		pop_parent.organization_id = pop_org.id 
	LEFT JOIN
		device_device as bsconverter_device
	on
		bsconverter_device.id = backhaul.bh_switch_id
	LEFT JOIN
		device_device as pe_device
	on
		backhaul.pe_ip_id = pe_device.id
	LEFT JOIN
		device_devicetechnology AS bsconverter_device_tech
	ON
		bsconverter_device.device_technology = bsconverter_device_tech.id
	LEFT JOIN
		device_devicetype AS bsconverter_device_type
	ON
		bsconverter_device.device_type = bsconverter_device_type.id
	LEFT JOIN
		device_devicevendor as bsconverter_device_vendor
	on
		bsconverter_device.device_vendor = bsconverter_device_vendor.id
	LEFT JOIN
		device_device as bsconverter_parent
	ON
		bsconverter_device.parent_id = bsconverter_parent.id
	LEFT JOIN
		device_devicetype as bsconverterparent_devicetype
	ON
		bsconverter_parent.device_type = bsconverterparent_devicetype.id
	LEFT JOIN
		organization_organization as bsconverter_org
	ON     
		bsconverter_parent.organization_id = bsconverter_org.id 
	LEFT JOIN
		device_device as bsswitch_device
	on
		bs.bs_switch_id = bsswitch_device.id
	LEFT JOIN
		device_devicetechnology AS bsswitch_device_tech
	ON
		bsswitch_device.device_technology = bsswitch_device_tech.id
	LEFT JOIN
		device_devicetype AS bsswitch_device_type
	ON
		bsswitch_device.device_type = bsswitch_device_type.id
	LEFT JOIN
		device_devicevendor as bsswitch_device_vendor
	on
		bsswitch_device.device_vendor = bsswitch_device_vendor.id
	LEFT JOIN
		device_device as bsswitch_parent
	ON
		bsswitch_device.parent_id = bsswitch_parent.id
	LEFT JOIN
		device_devicetype as bsswitchparent_devicetype
	ON
		bsswitch_parent.device_type = bsswitchparent_devicetype.id
	LEFT JOIN
		organization_organization as bsswitch_org
	ON     
		bsswitch_parent.organization_id = bsswitch_org.id 
	LEFT JOIN
		inventory_sector AS sect
	ON
		bs.id = sect.base_station_id
	LEFT JOIN
		device_device AS device
	ON
		sect.sector_configured_on_id = device.id
	LEFT JOIN
		device_device AS device_parent
	ON
		device.parent_id = device_parent.id
	LEFT JOIN 
		organization_organization as device_org
	ON
	        device.organization_id = device_org.id
	LEFT JOIN
		device_devicetype as deviceparent_devicetype
	ON
		device.device_type = deviceparent_devicetype.id
	LEFT JOIN
		device_devicetechnology AS bs_device_tech
	ON
		device.device_technology = bs_device_tech.id
	LEFT JOIN 
		device_devicetype as bs_device_type
	ON
		device.device_type = bs_device_type.id
	LEFT JOIN
		device_devicevendor as bs_device_vendor
	on
		device.device_vendor = bs_device_vendor.id
	LEFT JOIN
		device_city as city
	on
		bs.city_id = city.id
	LEFT JOIN
		device_state as state
	on
		bs.state_id = state.id
	LEFT JOIN
		device_country as region
	on
		bs.country_id = region.id
	LEFT JOIN
                organization_organization as organization
        on
                bs.organization_id = organization.id
	LEFT JOIN
		inventory_circuit AS ckt
	ON
		sect.id = ckt.sector_id
	LEFT JOIN
		inventory_substation AS ss
	ON
		ss.id = ckt.sub_station_id
	LEFT JOIN
		device_device as device_ss
	on
		ss.device_id = device_ss.id
	LEFT JOIN
		inventory_customer AS customer
	ON
		customer.id = ckt.customer_id
	LEFT JOIN
		device_device AS ss_device
	ON
		ss_device.id = ss.device_id
	LEFT JOIN
		device_devicetechnology AS ss_device_tech
	ON
		ss_device.device_technology = ss_device_tech.id
	LEFT JOIN
		device_devicetype AS ss_device_type
	ON
		ss_device.device_type = ss_device_type.id
	LEFT JOIN
		device_devicevendor as ss_device_vendor
	on
		ss_device.device_vendor = ss_device_vendor.id
	WHERE
		not isnull(backhaul.bh_configured_on_id)
	GROUP BY
		backhaul.bh_configured_on_id;
	"""

# Query result for PTP-BH far end ip list.
query2 = """
select 
	device.ip_address as ip_address
from
	inventory_circuit as circuit
left join
	inventory_substation as substation
on
	circuit.sub_station_id = substation.id
left join
	device_device as device
on
	device.id = substation.device_id
where
	lower(circuit.circuit_type) = 'backhaul';
"""
# Query result for Master alarm table in snmptt database.
query3 = """
select
	alarm_name as alarm_name,
	IF(isnull(oid),'NA',oid) as oid,
	IF(isnull(severity), 'NA', severity) as severity,
	IF(isnull(device_type), 'NA', device_type) as device_type,
	IF(isnull(alarm_mode), 'NA',alarm_mode ) as alarm_mode,
	IF(isnull(alarm_category), 'set([])',alarm_category ) as alarm_category,
	IF(isnull(alarm_group), 'NA',alarm_group ) as alarm_group,
	IF(isnull(alarm_type), 'NA', alarm_type) as alarm_type,
	IF(isnull(sia), 'NA', sia) as sia, 
	IF(isnull(auto_tt), 'NA', auto_tt) as auto_tt,
	IF(isnull(correlation), 'NA', correlation) as correlation,
	IF(isnull(to_monolith), 'NA', to_monolith) as to_monolith,
	IF(isnull(mail), 'NA', mail) as mail,
	IF(isnull(sms), 'NA', sms) as sms,
	IF(isnull(coverage), 'NA', coverage) as coverage,
	IF(isnull(resource_name), 'NA', resource_name) as resource_name,
	IF(isnull(resource_type), 'NA', resource_type) as resource_type,
	IF(isnull(support_organization), 'NA', support_organization) as support_organization,
	IF(isnull(bearer_organization), 'NA', bearer_organization) as bearer_organization,
	IF(isnull(priority), 'NA', priority) as priority,
	IF(isnull(category_id), 'NA', category_id) as category_id,
	IF(isnull(refer), 'NA', refer) as refer
from
	master_alarm_table;
"""

query_4 = """
SELECT master1.alarm_name, master1.severity, master2.alarm_name,master2.severity
FROM
	alarm_masking_table mask
INNER JOIN
	master_alarm_table master1
ON
	mask.alarm_id = master1.id
INNER JOIN
	master_alarm_table master2
ON
	mask.alarm_mask_id = master2.id
"""

query_5 = """
SELECT master.alarm_name,master.severity,master.priority from master_alarm_table as master
"""

query6 = """
        SELECT
                `ic`.`circuit_id`,
                `pt`.`ip_address`,
                `is`.`sector_configured_on_port_id`,
                `is`.`sector_id`
        FROM
                `performance_topology` `pt`
        LEFT JOIN
                `inventory_sector` `is`
        ON
                `is`.`sector_id` = `pt`.`sector_id`
        LEFT JOIN
                `inventory_circuit` `ic`
        ON
                `ic`.`sector_id` = `is`.`id`

      	UNION

	SELECT 
		`ic`.`circuit_id`,
                `dd`.`ip_address`,
		`is`.`sector_configured_on_port_id`,
		`is`.`sector_id`

	FROM
		`inventory_sector` `is`
	LEFT JOIN
		`device_device` `dd`
	ON 
		`is`.`sector_configured_on_id` = `dd`.`id`
	LEFT JOIN
		`inventory_circuit` `ic`
	ON
		`ic`.`sector_id` = `is`.`id`;
	"""

@app.task(base=DatabaseTask, name='mysql_to_inventory_data')
def mysql_to_inventory_data():
    try: 
	alarm_mapping_dict = defaultdict(list)
	alarm_priority_dict = {} 
	inv = inventory()
	ptp_farend = list()
	conn_historical = mysql_to_inventory_data.mysql_cnx('historical')
	fetch_circuit_dict_from_mysql(conn_historical)
	cur = conn_historical.cursor()
	cur.execute(query2)
	desc = cur.description
	farend_list = cur.fetchall()
	for ip_tuple in farend_list:
	    ptp_farend.append(ip_tuple[0])
	cur.execute(query1)
	desc =  cur.description
	my_list = [dict(zip([col[0] for col in desc ],row)) for row in cur.fetchall()]
        inv.create_inventory_data(my_list,ptp_farend)
	cur.close()
	conn_historical.close()
    except Exception,e:
	logger.error('Error in Mysql data extraction %s' %(e))
    #print mylist
    try:
	conn_snmptt = mysql_to_inventory_data.mysql_cnx('snmptt')
	cur = conn_snmptt.cursor()
	cur.execute(query3)
	desc = cur.description
	mat_list = [dict(zip([col[0] for col in desc ],row)) for row in cur.fetchall()]
	inv.insert_mat_data_in_redis(mat_list)

	# Current Clear alarm mapping
	cur.execute(query_4)
	current_clear_mapping = cur.fetchall()
	for (name,severity,mask_name,mask_severity) in current_clear_mapping:
		alarm_mapping_dict[(name,severity)].append((mask_name,mask_severity))
	alarm_mapping = {'alarm_mapping_dict':alarm_mapping_dict}
	inv.insert_data_in_redis(alarm_mapping)

	# Alarm - Priority mapping
	cur.execute("SELECT master.alarm_name,master.severity,master.priority from master_alarm_table as master")
	alarm_priority = cur.fetchall()
	for (name,severity,priority) in alarm_priority:
	    alarm_priority_dict[(name,severity)] = priority
	redis_alarm_priority = {'alarm_priority_dict':alarm_priority_dict}
        inv.insert_data_in_redis(redis_alarm_priority)
	cur.close()
	conn_snmptt.close()
    except Exception,e:
	logger.error('Error in MAt data extraction %s' %(e))
   

def fetch_circuit_dict_from_mysql(conn_historical):
    cur = conn_historical.cursor()
    cur.execute(query6)
    data_performance_topology = cur.fetchall()

    #logger.error('Circuit_dict data %s'%(data))
    circuit_dict = make_circuit_dict_from_data(data_performance_topology)
    #circuit_dict_new = make_circuit_dict_from_data_copy(data_performance_topology)
    rds_cli = RedisInterface(custom_conf={'db': 5})
    redis_conn =  rds_cli.redis_cnx
    redis_conn.set('circuit_dict',circuit_dict)
    #redis_conn.set('circuit_dict_new',circuit_dict_new)
    logger.error('Circuit dict has been updated')

def make_circuit_dict_from_data(data_performance_topology):
    my_dict = {}
    for each_tuple in data_performance_topology:
        circuit_id = each_tuple [0]
        ip_address = each_tuple[1]
        sector_type = each_tuple[2]
        #if ip_address is not None and sector_id is not None and circuit_id is not None:
	if ip_address is not None and circuit_id is not None:

	    if sector_type == 43:
		sector_type = "odu1"
	    elif sector_type == 44:
		sector_type = "odu2"
	    else:
		sector_type = "odu"

            if ip_address in my_dict:
                if sector_type in my_dict[ip_address]:
                    if circuit_id in my_dict[ip_address][sector_type]:
                        pass
                    else:
                        my_dict[ip_address][sector_type].append(circuit_id)
                else:
                    my_dict[ip_address][sector_type] = []
                    my_dict[ip_address][sector_type].append(circuit_id)
            else:
                my_dict[ip_address] = {}
                my_dict[ip_address][sector_type] = []
                my_dict[ip_address][sector_type].append(circuit_id)
    return my_dict

def make_circuit_dict_from_data_copy(data_performance_topology):
    #my_dict = {}
    my_dict = defaultdict(lambda: defaultdict(list))
    for each_tuple in data_performance_topology:
        circuit_id = each_tuple [0]
        ip_address = each_tuple[1]
        sector_type = each_tuple[2]
        #if ip_address is not None and sector_id is not None and circuit_id is not None:
        if ip_address is not None and circuit_id is not None:

            if sector_type == 43:
                sector_type = "odu1"
            elif sector_type == 44:
                sector_type = "odu2"
            else:
                sector_type = "odu"

            my_dict[ip_address][sector_type].append(circuit_id)

    my_dict = dict(my_dict)
	    
    return my_dict

if __name__ == '__main__':
    mysql_to_inventory_data.apply_async()
