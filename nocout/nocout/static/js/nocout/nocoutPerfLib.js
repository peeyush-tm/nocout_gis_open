/**
 * This library is used to show live performance of particular device & its functionality
 * @class nocout.perf.lib
 * @uses FLOT CHARTS
 * Coded By :- Yogender Purohit
 */

/*Global Variables*/
var perf_that = "",
	allDevices = "",
	device_status = "",
	device_services = "",
	single_service_data = "",
	getServiceDataUrl = "",
	x=0;

 function nocoutPerfLib() {

 	/*Save reference of current pointer to the global variable*/
 	perf_that = this;

 	/**
 	 * This function call the server to get all the devices data & then populate it to the dropdown
 	 * @class nocout.perf.lib
 	 * @method getAllDevices
 	 * @param get_device_url "String", It contains the url to fetch the devices list.
 	 * @param device_id "INT", It contains the ID of current device.
 	 */
 	this.getAllDevices = function(get_device_url,device_id) {

		/*Ajax call to Get Devices API*/
		// $.ajax({
		// 	crossDomain: true,
		// 	url : get_device_url,
		// 	type : "GET",
		// 	dataType : "json",
		// 	success : function(result) {
				if(device_data.success == 1) {
					allDevices = device_data.data.objects;
					var devices_options = '<option value="">Select Device</option>';
					$.each(allDevices,function(key,value) {
						if(value.id == device_id) {
							devices_options += '<option value="'+value.id+'" selected>'+value.alias+'</option>';
						} else {
							devices_options += '<option value="'+value.id+'">'+value.alias+'</option>';
						}
					});
					$("#device_name").html(devices_options);
				} else {
					console.log(device_data.message);
				}
		// 	},
		// 	error : function(err) {
		// 		console.log(err);
		// 	}
		// });
 	};

 	/**
 	 * This function fetch the status of current device
 	 * @class nocout.perf.lib
 	 * @method getStatus
 	 * @param get_status_url "String", It contains the url to fetch the status of current device.
 	 * @param device_id "INT", It contains the ID of current device.
 	 */
 	this.getStatus = function(get_status_url,device_id) {

 		/*Ajax call to Get Devices API*/
		// $.ajax({
		// 	crossDomain: true,
		// 	url : get_status_url,
		// 	type : "GET",
		// 	dataType : "json",
		// 	success : function(result) {
				if(status_data.success == 1) {
					
					device_status = status_data.data.objects;
					/*Loop for table headers*/
					var headers = "<tr>";
					$.each(device_status.header,function(key,value) {
						headers += '<th>'+value+'</th>';
					});

					headers += "</tr>";
					/*Populate table headers*/
					$("#status_table thead").html(headers);

					/*Loop for status table data*/
					var status_val = "<tr>";
					$.each(device_status.values,function(key,value) {
						status_val += '<td>'+value+'</td>';
					});

					status_val += "</tr>";
					/*Populate table data*/
					$("#status_table tbody").html(status_val);
				} else {
					console.log(device_status.message);
				}
		// 	},
		// 	error : function(err) {
		// 		console.log(err);
		// 	}
		// });
 	};

 	/**
 	 * This function fetch the list of services
 	 * @class nocout.perf.lib
 	 * @method getServices
 	 * @param get_service_url "String", It contains the url to fetch the services.
 	 * @param device_id "INT", It contains the ID of current device.
 	 */
 	this.getServices = function(get_service_url,device_id) {

 		/*Ajax call to Get Devices API*/
		// $.ajax({
		// 	crossDomain: true,
		// 	url : get_service_url,
		// 	type : "GET",
		// 	dataType : "json",
		// 	success : function(result) {
				if(service_data.success == 1) {
					var active_tab_id = "",
						active_tab_url = "";
					device_services = service_data.data.objects;
					/*Loop to get services from object*/
					var service_tabs = '<ul class="nav nav-tabs">';
					var service_tabs_data = '<div class="tab-content">';

					$.each(device_services,function(key,value) {
						if(value.active == 1) {
							
							active_tab_id = value.name;
							active_tab_url = value.url;

							service_tabs += '<li class="active"><a href="#'+value.name+'_block" url="'+value.url+'" id="'+value.name+'_tab" data-toggle="tab">'+value.title+'</a></li>';
							service_tabs_data += '<div class="tab-pane fade active in" id="'+value.name+'_block"><div class="divide-10"></div><div class="chart_container"><div id="'+value.name+'_chart" style="height:350px;width:100%;"></div></div></div>';
						} else {
							service_tabs += '<li class=""><a href="#'+value.name+'_block" url="'+value.url+'" id="'+value.name+'_tab" data-toggle="tab">'+value.title+'</a></li>';
							service_tabs_data += '<div class="tab-pane fade" id="'+value.name+'_block"><div class="divide-10"></div><div class="chart_container"><div id="'+value.name+'_chart" style="height:350px;width:100%;"></div></div></div>';
						}
					});

					service_tabs += "</ul>";
					service_tabs_data += "</div>";

					var tabs_with_data = service_tabs +" "+service_tabs_data;

					$("#services_tab_container").html(tabs_with_data);

					/*Call getServiceData function to fetch the data for currently active service*/
					perf_that.getServiceData(active_tab_url,active_tab_id,device_id);

				} else {
					console.log(device_services.message);
				}
		// 	},
		// 	error : function(err) {
		// 		console.log(err);
		// 	}
		// });
 	};

 	/**
 	 * This function fetches data regarding particular service
 	 * @class nocout.perf.lib
 	 * @method getServiceData
 	 * @param get_service_data_url "String", It contains the url to fetch the status of current device.
 	 * @param service_id "String", It contains unique name for service.
 	 * @param device_id "INT", It contains the ID of current device.
 	 */
 	this.getServiceData = function(get_service_data_url,service_id,device_id) {
 		
 		/*Temporary Code*/
 		if(x >= 3) {
 			x = 1;
 		} else {
 			x++;
 		}
 		
 		/*Ajax call to Get Devices API*/
		// $.ajax({
		// 	crossDomain: true,
		// 	url : get_service_data_url,
		// 	type : "GET",
		// 	dataType : "json",
		// 	success : function(result) {
				if(singleServiceData1.success == 1) {
					
					/*Temporary code*/
					if(x == 1) {
						single_service_data = singleServiceData1.data.objects;
					} else if(x == 2) {
						single_service_data = singleServiceData2.data.objects;
					} else {
						single_service_data = singleServiceData3.data.objects;
					}

					$.plot($("#"+service_id+"_chart"), single_service_data.chart_data, {
                        series: {
                            stack: true,
                            lines: {
                                show: single_service_data.show_line,
                                steps: single_service_data.steps
                            },
                            bars: {
                                show: single_service_data.show_bar,
                                barWidth: 1000*60*60*1,//1000*60*60*24*350,/*Bar width in Hrs*/
                                horizontal : single_service_data.horizontal
                            }
                        },
                        crosshair: {
                            mode: "x"
                        },
                        yaxis: {},
				        xaxis: {
			        		mode: "time"
    						// timeformat: "%d/%m/%Y"
						},
						grid:{
								borderWidth: 0
						}
                    });
					
				} else {
					console.log(singleServiceData1.message);
				}
		// 	},
		// 	error : function(err) {
		// 		console.log(err);
		// 	}
		// });
 	};
 }