/**
 * This library is used to show live performance of particular device & its functionality
 * @class nocout.perf.lib
 * @uses Highcharts
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

$.urlParam = function(name){
                    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
                    if (results==null){
                       return null;
                    }
                    else{
                       return results[1] || 0;
                    }};


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
        var get_url = get_device_url;
		$.ajax({
			crossDomain: true,
			url : get_url,
			type : "GET",
			dataType : "json",
			success : function(result) {

				if(result.success == 1) {
					allDevices = result.data.objects;
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
					console.log(result.message);
				}
			},
			error : function(err) {
				console.log(err);
			}
		});
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
        var get_url = get_status_url;
		$.ajax({
			crossDomain: true,
			url : get_url,
			type : "GET",
			dataType : "json",
			success : function(result) {
				if(result.success == 1) {
					
					device_status = result.data.objects;
					/*Loop for table headers*/
					var headers = "<tr>";
					$.each(device_status.headers,function(key, value) {
						headers += '<th>'+value+'</th>';
					});

					headers += "</tr>";
					/*Populate table headers*/
					$("#status_table thead").html(headers);

					/*Loop for status table data*/
					var status_val = "<tr>";
					$.each(device_status.values,function(key, value) {
						status_val += '<td>'+value+'</td>';
					});

					status_val += "</tr>";
					/*Populate table data*/
					$("#status_table tbody").html(status_val);
				} else {
					console.log(result.message);
				}
			},
			error : function(err) {

				$("#status_table tbody").html(err.statusText);

			}
		});
 	};

 	/**
 	 * This function fetch the list of services
 	 * @class nocout.perf.lib
 	 * @method getServices
 	 * @param get_service_url "String", It contains the url to fetch the services.
 	 * @param device_id "INT", It contains the ID of current device.
 	 */
 	this.getServices = function(get_service_url, device_id) {

        /*Show the spinner*/
        showSpinner();

 		/*Ajax call to Get Devices API*/
        var get_url = get_service_url;
		$.ajax({
			crossDomain: true,
			url : get_url,
			type : "GET",
			dataType : "json",
			success : function(result) {

				if(result.success == 1) {
					var active_tab_id = "",
						active_tab_url = "";
					device_services_tab = Object.keys(result.data.objects);


					/*Loop to get services from object*/
                    var li_style = "background: #f5f5f5; width:100%; border:1px solid #dddddd;"
                    var li_a_style = "background: none; border:none;";
                    
                    var count = 0;

                    for(var i= 0; i<device_services_tab.length; i++) {                        
                        
                        device_services = result.data.objects[device_services_tab[i]];
                        var tabs_with_data = "";
                        var service_tabs = '<div class="col-md-3"><ul class="nav nav-tabs">';

                        var service_tabs_data = '<div class="col-md-9">'
                        service_tabs_data += '<div class="tab-content">';
                        $.each(device_services, function(key, value) {
                            if(count == 0) {
                                count += 1;
                                active_tab_id = value.name;
                                active_tab_url = "/"+value.url;

                                service_tabs += '<li class="active" style="'+li_style+'"><a href="#'+value.name+'_block" url="'+value.url+'" id="'+value.name+'_tab" data-toggle="tab" style="'+li_a_style+'">'+value.title+'</a></li>';
                                service_tabs_data += '<div class="tab-pane active" id="'+value.name+'_block"><div class="chart_container"><div id="'+value.name+'_chart" style="height:350px;width:100%;"></div></div></div>';
                            } else {
                                service_tabs += '<li class="" style="'+li_style+'"><a href="#'+value.name+'_block" url="'+value.url+'" id="'+value.name+'_tab" data-toggle="tab" style="'+li_a_style+'">'+value.title+'</a></li>';
                                service_tabs_data += '<div class="tab-pane" id="'+value.name+'_block"><div class="chart_container" style="width:100%;"><div id="'+value.name+'_chart" style="height:350px;width:100%;"></div></div></div>';
                            }
                        });
                        service_tabs += '</ul></div>';
                        service_tabs_data += '</div>';
                        tabs_with_data = service_tabs +" "+service_tabs_data;

                            $("#"+device_services_tab[i]+" .inner_tab_container .panel-body .tabs-left").html(tabs_with_data);
                            /*Call getServiceData function to fetch the data for currently active service*/                            
                        }

                    /*Load data of first tab*/
                    perf_that.getServiceData(active_tab_url, active_tab_id, device_id);

                    /*Bind click event on tabs*/
                    $('.inner_tab_container .nav-tabs li a').click(function(e) {
                        var serviceId = e.currentTarget.id.slice(0, -4);
                        //@TODO: all the ursl must end with a / - django style
                        var serviceDataUrl = "/" + $.trim(e.currentTarget.attributes.url.value);
                        perfInstance.getServiceData(serviceDataUrl, serviceId, current_device);

                    });

				} else {
					$(".inner_tab_container").html("<p>"+result.message+"</p>");
					console.log(result.message);
				}

                /*Hide the spinner*/
                hideSpinner();
			},
			error : function(err) {

				$(".inner_tab_container").html(err.statusText);

                /*Hide the spinner*/
                hideSpinner();
			}
		});
 	};

 	/**
 	 * This function fetches data regarding particular service
 	 * @class nocout.perf.lib
 	 * @method getServiceData
 	 * @param get_service_data_url "String", It contains the url to fetch the status of current device.
 	 * @param service_id "String", It contains unique name for service.
 	 * @param device_id "INT", It contains the ID of current device.
 	 */
 	this.getServiceData = function(get_service_data_url, service_id, device_id) {
    
        /*Show the spinner*/
        showSpinner();
        /* Appending the Hash Tag of service_name with service_data_source */
        window.location.href = '#'+ get_service_data_url.split('/')[3] + "#"+ get_service_data_url.split('/')[5];
 		/*Ajax call to Get Devices API*/
        var start_date=$.urlParam('start_date');
        var end_date=$.urlParam('end_date');
        var get_url = get_service_data_url;
		$.ajax({
			crossDomain: true,
			url : get_url,
            data : {'start_date':start_date, 'end_date':end_date },
			type : "GET",
			dataType : "json",
			success : function(result) {

				if(result.success == 1) {
					/*Service Data Object*/
					single_service_data = result.data.objects;

                    if (result.data.objects.table_data != undefined) {
                        if(result.data.objects.table_data.length > 0) {

                            var table_string = "";
                            var grid_headers = result.data.objects.table_data_header;
                            table_string += '<table class="table table-bordered"><thead>';
                            /*Table header creation start*/
                            for(var i=0;i<grid_headers.length;i++) {
                                table_string += '<td>'+grid_headers[i]+'</td>';
                            }
                            table_string += '</thead><tbody>';
                            /*Table header creation end*/

                            /*Table data creation start*/

                            for(var i=0;i<result.data.objects.table_data.length;i++) {
                                table_string += '<tr>';
                                table_string += '<td>'+result.data.objects.table_data[i].date+'</td>';
                                table_string += '<td>'+result.data.objects.table_data[i].time+'</td>';
                                table_string += '<td>'+result.data.objects.table_data[i].value+'</td>';
                                table_string += '</tr>';
                            }
                            /*Table data creation end*/
                            table_string += '</tbody></table>';
                            $('#'+service_id+'_chart').html(table_string);
                        } else {
                            $('#'+service_id+'_chart').html(result.message);
                        }

                    }
                    else{
                        $('#'+service_id+'_chart').highcharts({
                            chart: {
                                zoomType: 'x',
                                type: single_service_data.type
    //                            events:{
    //                                load: Highcharts.drawTable //@TODO: here in we need to draw canvas table with data table data
    //                            }
                            },
                            title: {
                                text: single_service_data.name
                            },
                            legend: {
                                align: 'right',
                                verticalAlign: 'top',
                                x: 0,
                                y: 0,
                                floating: true,
                                borderWidth: 1,
                                backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
                            },
                            tooltip: {
                                pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b><br/>',
                                shared: true,
                                crosshairs: true,
                                valueSuffix: single_service_data.valuesuffix
                            },
                            xAxis: {
                                title: {
                                    text: "time"
                                },
                                type: 'datetime',
                                minRange: 3600000,
                                dateTimeLabelFormats: {
                                    millisecond: '%H:%M:%S.%L',
                                    second: '%H:%M:%S',
                                    minute: '%H:%M',
                                    hour: '%H:%M',
                                    day: '%e. %b',
                                    week: '%e. %b',
                                    month: '%b \'%y',
                                    year: '%Y'
                                }
                            },
                            yAxis: {
                              title: {
                                    text: single_service_data.valuetext
                                }
                            },
                            series: single_service_data.chart_data
                        });

                        /*Hide Highcharts.com Name*/
                        var highcharts_link = $("#services_tab_container svg text:last-child");
                        $.grep(highcharts_link,function(val) {
                            if($.trim(val.innerHTML) == 'Highcharts.com') {
                                val.innerHTML = "";
                            }
                        });
                    }
				} else {
					$('#'+service_id+'_chart').html(result.message);
					// console.log(result.message);
				}

                /*Hide the spinner*/
                hideSpinner();
			},
			error : function(err) {
				
				$('#'+service_id+'_chart').html(err.statusText);
				// console.log(err);

                /*Hide the spinner*/
                hideSpinner();
			}
		});
 	};
 }