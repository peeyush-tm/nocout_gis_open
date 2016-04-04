from mysql.connector import connect
from start_pub import app 
from db_ops import *
from formatting import inventory 
#from celery import Task
# Get topology data in hierarchy for which backhaul exists.
query1 = """
SELECT
	backhaul.id as BackhaulID,	
	IF(isnull(backhaul.pe_ip), 'NA', backhaul.pe_ip) as PE_IP,
	IF(isnull(aggregator_device.ip_address), 'NA', aggregator_device.ip_address) as AggregationSwitchIP,
	IF(isnull(popconverter_device.ip_address), 'NA', popconverter_device.ip_address) as POPconverterIP,
	IF(isnull(pop_device_tech.name), 'NA', pop_device_tech.name) as POPconverterTech,
	IF(isnull(pop_parent.ip_address), 'NA', pop_parent.ip_address) as POPconverterParentIP, 
	IF(isnull(popconverter_device.parent_port), 'NA',popconverter_device.parent_port) as POPconverterParentPort, 
	IF(isnull(popparent_devicetype.name), 'NA', popparent_devicetype.name) as POPconverterParentType,
	IF(isnull(bsconverter_device.ip_address), 'NA', bsconverter_device.ip_address) as BTSconverterIP,
	IF(isnull(bsconverter_device_tech.name), 'NA', bsconverter_device_tech.name) as BTSconverterTech,
	IF(isnull(bsconverter_parent.ip_address), 'NA', bsconverter_parent.ip_address) as BTSconverterParentIP,
	IF(isnull(bsconverter_device.parent_port), 'NA', bsconverter_device.parent_port) as BTSconverterParentPort,
	IF(isnull(bsconverterparent_devicetype.name), 'NA', bsconverterparent_devicetype.name) as BTSconverterParentType,
	IF(isnull(bh_device.ip_address), 'NA', bh_device.ip_address) as backhaul_configured_on_ip,
	IF(isnull(bsswitch_device.ip_address), 'NA', bsswitch_device.ip_address) as BSswitchIP,
	IF(isnull(bsswitch_device_tech.name), 'NA', bsswitch_device_tech.name) as BSswitchTech,
	IF(isnull(bsswitch_parent.ip_address), 'NA', bsswitch_parent.ip_address) as BSswitchParentIP,
	IF(isnull(bsswitchparent_devicetype.name), 'NA', bsswitchparent_devicetype.name) as BSswitchParentType,
	IF(isnull(bsswitch_device.parent_port), 'NA', bsswitch_device.parent_port) as BSswitchParentPort,
	GROUP_CONCAT(CONCAT(
		IF(isnull(bs.id), 'NA', bs.id), '|',
		IF(isnull(bs.name), 'NA', bs.name), '|',
		IF(isnull(bsswitch_device.ip_address), 'NA', bsswitch_device.ip_address), '|',
		IF(isnull(city.city_name), 'NA', city.city_name), '|',
		IF(isnull(state.state_name), 'NA', state.state_name), '|',
		IF(isnull(region.country_name), 'NA', region.country_name),'|',
		IF(isnull(bsswitch_parent.ip_address), 'NA', bsswitch_parent.ip_address),'|',
		IF(isnull(bsswitchparent_devicetype.name), 'NA', bsswitchparent_devicetype.name)
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
        	IF(isnull(device.parent_port), 'NA', device.parent_port)

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
        	IF(isnull(device.ip_address), 'NA', device.ip_address)
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
	device_device as pop_parent
ON
	popconverter_device.parent_id = pop_parent.id
LEFT JOIN 
	device_devicetype as popparent_devicetype
ON
	pop_parent.device_type = popparent_devicetype.id
LEFT JOIN
	device_device as bsconverter_device
on
	bsconverter_device.id = backhaul.bh_switch_id
LEFT JOIN
	device_devicetechnology AS bsconverter_device_tech
ON
	bsconverter_device.device_technology = bsconverter_device_tech.id
LEFT JOIN
	device_device as bsconverter_parent
ON
	bsconverter_device.parent_id = bsconverter_parent.id
LEFT JOIN
	device_devicetype as bsconverterparent_devicetype
ON
	bsconverter_parent.device_type = bsconverterparent_devicetype.id
LEFT JOIN
	device_device as bsswitch_device
on
	bs.bs_switch_id = bsswitch_device.id
LEFT JOIN
	device_devicetechnology AS bsswitch_device_tech
ON
	bsswitch_device.device_technology = bsswitch_device_tech.id
LEFT JOIN
	device_device as bsswitch_parent
ON
	bsswitch_device.parent_id = bsswitch_parent.id
LEFT JOIN
	device_devicetype as bsswitchparent_devicetype
ON
	bsswitch_parent.device_type = bsswitchparent_devicetype.id
LEFT JOIN
	inventory_sector AS sect
ON
	bs.id = sect.base_station_id
LEFT JOIN
	device_device AS device
ON
	sect.sector_configured_on_id = device.id
	AND
	device.is_added_to_nms > 0
LEFT JOIN
	device_device AS device_parent
ON
	device.parent_id = device_parent.id
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
	AND
	ss_device.is_added_to_nms > 0
LEFT JOIN
	device_devicetechnology AS ss_device_tech
ON
	ss_device.device_technology = ss_device_tech.id
LEFT JOIN
	device_devicetype AS ss_device_type
ON
	ss_device.device_type = ss_device_type.id
WHERE
	not isnull(backhaul.bh_configured_on_id)
	AND
	bh_device.is_added_to_nms > 0
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
	IF(isnull(alarm_category), 'NA',alarm_category ) as alarm_category,
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
@app.task(base=DatabaseTask, name='mysql_to_inventory_data')
def mysql_to_inventory_data():
    inv = inventory()
    ptp_farend = list()
    conn = mysql_to_inventory_data.mysql_cnx('historical')
    cur = conn.cursor()
    cur.execute(query2)
    desc = cur.description
    farend_list = cur.fetchall()
    for ip_tuple in farend_list:
	ptp_farend.append(ip_tuple[0])

    cur.execute(query1)
    desc =  cur.description
    my_list = [dict(zip([col[0] for col in desc ],row)) for row in cur.fetchall()]
    with open('/omd/sites/ospf1_slave_1/test.bs','w') as f:
    	f.write(str(my_list))
    #logger.error('{0}'.format(my_list))
    inv.create_inventory_data(my_list,ptp_farend)
    conn = mysql_to_inventory_data.mysql_cnx('snmptt')
    cur = conn.cursor()
    cur.execute(query3)
    desc = cur.description
    mat_list = [dict(zip([col[0] for col in desc ],row)) for row in cur.fetchall()]
    #with open('/omd/sites/ospf1_slave_1/test.bs','w') as f:
    #	f.write(str(mat_list))
    #logger.error('{0}'.format(mat_list))
    inv.insert_mat_data_in_redis(mat_list)

if __name__ == '__main__':
    mysql_to_inventory_data.apply_async()
