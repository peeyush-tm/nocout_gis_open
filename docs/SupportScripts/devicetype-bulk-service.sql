select  
device_devicetype.name as DEVICETYPE,
service_service.name as SERVICE,
service_servicedatasource.name as DATASOURCE,
service_servicedatasource.warning as WARN,
service_servicedatasource.critical as CRIT
from device_devicetype 

inner join (
	service_serviceparameters, 
	service_protocol,
	service_servicedatasource,
	service_service_service_data_sources,
	service_service,
	device_devicetype_service
)
on (
	service_serviceparameters.id = service_service.parameters_id and
	service_protocol.id = service_serviceparameters.protocol_id and
	service_service_service_data_sources.service_id = service_service.id and
	service_service_service_data_sources.servicedatasource_id = service_servicedatasource.id and
	device_devicetype_service.service_id = service_service.id and
	device_devicetype_service.devicetype_id = device_devicetype.id
) 
group by device_devicetype.name, service_service.name