var ccpl_map, 
	base_url, 
	main_devices_data_wmap= [],
	wm_obj = {'features': {}, 'data': {}, 'devices': {}, 'lines': {}, 'sectors': {}},
	data_for_filter_wmap= [],
	filtered_devices_array= [];

var state_city_obj= {}, 
	all_cities_array= [], 
	tech_vendor_obj= {}, 
	all_vendor_array= [], 
	sectorMarkerConfiguredOn= [], 
	sectorMarkersMasterObj = {};

var bs_loki_db = [],
    ss_loki_db = [],
    sector_loki_db = [],
    polygon_loki_db = [],
    line_loki_db = [],
    all_devices_loki_db= [],
	state_lat_lon_db= [],
	searchResultData= [],
	state_wise_device_labels= {},
	allMarkersObject_wmap= {
		'base_station': {},
		'path': {},
		'sub_station': {},
		'sector_device': {},
		'sector_polygon': {}
	},
	allMarkersArray_wmap= [],
	currentlyPlottedDevices = [],
	plottedBsIds = [],
	sector_MarkersArray= [],
	markersMasterObj= {'BS': {}, 'Lines': {}, 'SS': {}, 'BSNamae': {}, 'SSNamae': {}, 'LinesName': {}, 'Poly': {}},
	masterMarkersObj= [],
	bsLatArray = [],
	bsLonArray = [],
	ssLatArray = [],
	ssLonArray = [],
	ssLinkArray_filtered = [],
	isFirstTime= 1,
	isExportDataActive= 0,
	pollCallingTimeout = "",
	remainingPollCalls = 0,
	pollingInterval = 10,
	pollingMaxInterval = 1,
	isPollingPaused = 0;

var bsDevicesObj = {};
var tempbsDeviceObj = {};
/*Set the base url of application for ajax calls*/
if(window.location.origin) {
	base_url = window.location.origin;
} else {
	base_url = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
}

var allSSIds = [],
	polygonSelectedDevices = [],
	currentPolygon = {},
	polled_devices_names = [],
	complete_polled_devices_data = [],
	complete_polled_devices_icon = {},
	total_polled_occurence = 0,
	nav_click_counter = 0,
	polled_device_count = {};
var pollableDevices = [];
var polled_devices_names= [];

var bs_ss_markers = [];
var bs_obj= {};
var isCallCompleted;
// var gisPerformanceClass = "";

function WhiteMapClass() {

	/*
	 *
	 * Public Variables
	*/
		this.livePollingPolygonControl = "";
	/*
	 *
	 * Private Variables
	*/	
		var global_this = "",
			total_count = 0, device_count= 0, limit= 0, loop_count = 0;

		/*
		Marker Spidifier For BS
		 */

		var markerSpiderfied= "";
		this.unSpiderifyBsMarker= function() {
			if(markerSpiderfied) {
				ccpl_map.getLayersByName("Devices")[0].removeAllFeatures();
				var finalLatLong = new OpenLayers.LonLat(markerSpiderfied.ptLon, markerSpiderfied.ptLat);
				markerSpiderfied.move(finalLatLong);
				markerSpiderfied= "";
			}
			return true;
		}

		this.spiderifyMarker = function(feature) {
			if(markerSpiderfied) {
				if(markerSpiderfied === feature) {
					return true;
				}
				global_this.unSpiderifyBsMarker();

			}
			var bsData = wm_obj.data[feature.bs_name];
			var bsSectors = bsDevicesObj[bsData.name];
			// var bsSectorLength = bsData.data.param.sector.length;
			if(bsSectors && bsSectors.length) {
				var currentAngle = 0;
				for(var i=0; i<= bsSectors.length; i++) {
					if(i=== bsSectors.length) {
						var bsMarker = allMarkersObject_wmap['base_station']['bs_'+bsData.name];						
						var xyDirection= "";
						if(ccpl_map.getZoom() < 9) {
							xyDirection = getAtXYDirection(currentAngle, 7, feature.ptLon, feature.ptLat);
						} else {
							if(ccpl_map.getZoom() >= 12) {
								if(ccpl_map.getZoom() >= 14) {
									xyDirection = getAtXYDirection(currentAngle, 0.3, feature.ptLon, feature.ptLat);		
								} else {
									xyDirection = getAtXYDirection(currentAngle, 1, feature.ptLon, feature.ptLat);		
								}
							} else {
								xyDirection = getAtXYDirection(currentAngle, 3, feature.ptLon, feature.ptLat);	
							}
							
						}					

						var finalLatLong = new OpenLayers.LonLat(xyDirection.lon, xyDirection.lat);
											
						var start_point = new OpenLayers.Geometry.Point(feature.ptLon,feature.ptLat);
						var end_point = new OpenLayers.Geometry.Point(xyDirection.lon,xyDirection.lat);

						ccpl_map.getLayersByName("Devices")[0].addFeatures([new OpenLayers.Feature.Vector(new OpenLayers.Geometry.LineString([start_point, end_point]))]);

						bsMarker.move(finalLatLong);
						markerSpiderfied = feature;
					} else {
						var sector = bsData.data.param.sector[i];
						var sectorMarker = allMarkersObject_wmap['sector_device']['sector_'+sector.sector_configured_on];
						var xyDirection= "";
						if(ccpl_map.getZoom() < 9) {
							xyDirection = getAtXYDirection(currentAngle, 7, feature.ptLon, feature.ptLat);
						} else {
							if(ccpl_map.getZoom() >= 12) {
								if(ccpl_map.getZoom() >= 14) {
									xyDirection = getAtXYDirection(currentAngle, 0.3, feature.ptLon, feature.ptLat);		
								} else {
									xyDirection = getAtXYDirection(currentAngle, 1, feature.ptLon, feature.ptLat);		
								}
							} else {
								xyDirection = getAtXYDirection(currentAngle, 3, feature.ptLon, feature.ptLat);	
							}
							
						}					

						var finalLatLong = new OpenLayers.LonLat(xyDirection.lon, xyDirection.lat);
											
						var start_point = new OpenLayers.Geometry.Point(feature.ptLon,feature.ptLat);
						var end_point = new OpenLayers.Geometry.Point(xyDirection.lon,xyDirection.lat);

						ccpl_map.getLayersByName("Devices")[0].addFeatures([new OpenLayers.Feature.Vector(new OpenLayers.Geometry.LineString([start_point, end_point]))]);
						ccpl_map.getLayersByName("Devices")[0].addFeatures([sectorMarker]);
						sectorMarker.move(finalLatLong);
						sectorMarker.style.externalGraphic = sectorMarker.pollingIcon ? sectorMarker.pollingIcon : sectorMarker.oldIcon;
					}
					currentAngle= currentAngle+(360/(bsSectors.length+1));
				}
				ccpl_map.getLayersByName("Devices")[0].redraw();
			} else {
				return true;
			}
			return false;
		}

		this.refreshLineLayers = function() {
			var selectedValue = $("#showConnLines").prop('checked'), lineLayers=  ccpl_map.getLayersByName("Lines")[0];
			if(selectedValue) {
				lineLayers.display(true);
			} else {
				lineLayers.display(false);
			}
		}


	/**
	 * 
	 * Polling Section
	 */
	
		this.initLivePolling = function() {

			if(ccpl_map.getZoom() > whiteMapSettings.zoomLevelAtWhichStateClusterExpands) {
				/*Reset marker icon*/
				for(var i=0;i<polygonSelectedDevices.length;i++) {

					var ss_marker = allMarkersObject_wmap['sub_station']['ss_'+polygonSelectedDevices[i].name],
		            	sector_ip = "";

		            if(polygonSelectedDevices[i].pointType && ($.trim(polygonSelectedDevices[i].pointType) == 'sub_station')) {
		            	sector_ip = polygonSelectedDevices[i].sector_ip;
		            } else {
		            	sector_ip = polygonSelectedDevices[i].sectorName;
		            }

		            var sector_marker = allMarkersObject_wmap['sector_device']['sector_'+sector_ip];

		            if(ss_marker) {
		            	ss_marker.style.externalGraphic = ss_marker.oldIcon;
					} else if(sector_marker) {
		            	sector_marker.style.externalGraphic = sector_marker.oldIcon;
					}
				}

				ccpl_map.getLayersByName('Markers')[0].redraw();
				ccpl_map.getLayersByName("Devices")[0].redraw();

				ccpl_map.getLayersByName('Polling')[0].removeAllFeatures();

				if(global_this.livePollingPolygonControl) {
					global_this.livePollingPolygonControl.deactivate();
				}

				// ccpl_map.addLayer(ccpl_map.getLayersByName('Polling')[0]);
				ccpl_map.getLayersByName('Polling')[0].setVisibility(true);

				isPollingActive = 1;

				/*Reset global variables*/
				allSSIds = [];
				polygonSelectedDevices = [];
				currentPolygon = {};
				polled_devices_names = [];
				complete_polled_devices_data = [];
				complete_polled_devices_icon = {};
				total_polled_occurence = 0;
				nav_click_counter = 0;
				polled_device_count = {};

				$("#sideInfo > .panel-body > .col-md-12 > .devices_container").html("");

		    	$("#tech_send").button("complete");
				$("#sideInfo .panel-body .col-md-12 .template_container").html("");

				if(!($("#timeInterval_container").hasClass("hide"))) {
					$("#timeInterval_container").addClass("hide");
				}

				if(!($(".play_pause_btns").hasClass("hide"))) {
					$(".play_pause_btns").addClass("hide");
				}

				if(($(".play_pause_btns").hasClass("disabled"))) {
					$(".play_pause_btns").removeClass("disabled");
				}

				if(!($("#fetch_polling").hasClass("hide"))) {
					$("#fetch_polling").addClass("hide");
				}

				if(!($("#polling_tabular_view").hasClass("hide"))) {
					$("#polling_tabular_view").addClass("hide");
				}

				/*Add hide class to navigation container on polling widget*/
				if(!$("#navigation_container").hasClass("hide")) {
					$("#navigation_container").addClass("hide");
				}

		    	if($("#sideInfoContainer").hasClass("hide")) {
					$("#sideInfoContainer").removeClass("hide");
				}

				if(!$("#createPolygonBtn").hasClass("hide")) {
					$("#createPolygonBtn").addClass("hide");
				}

				if($("#clearPolygonBtn").hasClass("hide")) {
					$("#clearPolygonBtn").removeClass("hide");
				}

				/*Disable poll interval & max interval dropdown*/
	            $("#poll_interval").removeAttr("disabled");
	            $("#poll_maxInterval").removeAttr("disabled");

	            /*Select default value*/
	            $("#poll_interval").val($("#poll_interval option:first").val());
	            $("#poll_maxInterval").val($("#poll_maxInterval option:first").val());
			} else {
				bootbox.alert("<p style='position:relative;z-index:9999;'>Please zoom in for live poll devices.There are too many devices.</p>");
				$("#clearPolygonBtn").trigger('click');
			}
		}

		 /**
	     * This function initialize live polling
	     * @method fetchPollingTemplate_gmap
	     */
		this.fetchPollingTemplate_wmap = function() {

			var selected_technology = $("#polling_tech").val(),
				pathArray = [],
				polygon = "",
				service_type = $("#isPing")[0].checked ? "ping" : "other";


			/*Re-Initialize the polling*/
			whiteMapClass.initLivePolling();
			
			/*Reset the variables*/
			polygonSelectedDevices = [];
			pointsArray = [];

			if(selected_technology != "") {
				$("#tech_send").button("loading");
				/*ajax call for services & datasource*/
				$.ajax({
					url : base_url+"/"+"device/ts_templates/?technology="+$.trim(selected_technology)+"&service_type="+service_type,
					success : function(results) {

						result = JSON.parse(results);
						if(result.success == 1) {
							/*Make live polling template select box*/
							var polling_templates = result.data.thematic_settings;
							var polling_select = "<select class='form-control' name='lp_template_select' id='lp_template_select'><option value=''>Select Template</option>";

							for(var i=0;i<polling_templates.length;i++) {
								polling_select += '<option value="'+polling_templates[i].id+'">'+polling_templates[i].value+'</option>'
							}
							polling_select += "</select>";

							$("#sideInfo .panel-body .col-md-12 .template_container").html(polling_select);

	    					if($("#fetch_polling").hasClass("hide")) {
	    						$("#fetch_polling").removeClass("hide");
	    					}

	    					if(($("#timeInterval_container").hasClass("hide"))) {
								$("#timeInterval_container").removeClass("hide");
							}

							if(($(".play_pause_btns").hasClass("hide"))) {
								$(".play_pause_btns").removeClass("hide");
							}

							if(($(".play_pause_btns").hasClass("disabled"))) {
								$(".play_pause_btns").removeClass("disabled");
							}

	    					$("#tech_send").button("complete");

							// ccpl_map.addLayer(ccpl_map.getLayersByName('Polling')[0]);
							ccpl_map.getLayersByName('Polling')[0].setVisibility(true);

							global_this.livePollingPolygonControl.activate();
						} else {
    					
	    					$("#tech_send").button("complete");
	    					$("#sideInfo .panel-body .col-md-12 .template_container").html("");

	    					if(!($("#timeInterval_container").hasClass("hide"))) {
								$("#timeInterval_container").addClass("hide");
							}

							if(!($(".play_pause_btns").hasClass("hide"))) {
								$(".play_pause_btns").addClass("hide");
							}

							if(($(".play_pause_btns").hasClass("disabled"))) {
								$(".play_pause_btns").removeClass("disabled");
							}

	    					if(!($("#fetch_polling").hasClass("hide"))) {
	    						$("#fetch_polling").addClass("hide");
	    					}

	    					$.gritter.add({
					            // (string | mandatory) the heading of the notification
					            title: 'Live Polling - Error',
					            // (string | mandatory) the text inside the notification
					            text: result.message,
					            // (bool | optional) if you want it to fade out on its own or just sit there
					            sticky: false
					        });
	    				}
					},
					error : function(err) {
						
						$("#tech_send").button("complete");
	    				$("#sideInfo .panel-body .col-md-12 .template_container").html("");

	    				if(!($("#timeInterval_container").hasClass("hide"))) {
							$("#timeInterval_container").addClass("hide");
						}

						if(!($(".play_pause_btns").hasClass("hide"))) {
							$(".play_pause_btns").addClass("hide");
						}

						if(($(".play_pause_btns").hasClass("disabled"))) {
							$(".play_pause_btns").removeClass("disabled");
						}

	    				if(!($("#fetch_polling").hasClass("hide"))) {
							$("#fetch_polling").addClass("hide");
						}
	    				
	    				$.gritter.add({
				            // (string | mandatory) the heading of the notification
				            title: 'Live Polling - Error',
				            // (string | mandatory) the text inside the notification
				            text: err.statusText,
				            // (bool | optional) if you want it to fade out on its own or just sit there
				            sticky: false
				        });
					}
				});
			} else {
				alert("Please select technology.");
			}
		}

		this.stopPolling= function() {
			global_this.unSpiderifyBsMarker();
			isPollingActive = 0;
			/*Reset marker icon*/
			for(var i=0;i<polygonSelectedDevices.length;i++) {

				var ss_marker = allMarkersObject_wmap['sub_station']['ss_'+polygonSelectedDevices[i].name],
            		sector_ip = "";
            
		        if(polygonSelectedDevices[i].pointType && ($.trim(polygonSelectedDevices[i].pointType) == 'sub_station')) {
		        	sector_ip = polygonSelectedDevices[i].sector_ip;
		        } else {
		        	sector_ip = polygonSelectedDevices[i].sectorName;
		        }

		        var sector_marker = allMarkersObject_wmap['sector_device']['sector_'+sector_ip];

				if(ss_marker) {
					ss_marker.pollingIcon = "";
					ss_marker.style.externalGraphic = ss_marker.icon;
				} else if(sector_marker) {
					sector_marker.pollingIcon = "";
					sector_marker.style.externalGraphic = sector_marker.icon;
				}
			}
			ccpl_map.getLayersByName('Markers')[0].redraw();
			ccpl_map.getLayersByName("Devices")[0].redraw();

			if(global_this.livePollingPolygonControl) {
				global_this.livePollingPolygonControl.deactivate();
				ccpl_map.getLayersByName('Polling')[0].removeAllFeatures();
				ccpl_map.getLayersByName('Polling')[0].setVisibility(false);
			}

			if(!$("#sideInfoContainer").hasClass("hide")) {
				$("#sideInfoContainer").addClass("hide");
			}

			/*Show Select Devices button*/
			if($("#createPolygonBtn").hasClass("hide")) {
				$("#createPolygonBtn").removeClass("hide");
				$("#createPolygonBtn").button("complete");
			}

			/*Hide the clear selection button*/
			if(!$("#clearPolygonBtn").hasClass("hide")) {
				$("#clearPolygonBtn").addClass("hide");
			}

			/*Add hide class to tabular button on polling widget*/
			if(!$("#polling_tabular_view").hasClass("hide")) {
				$("#polling_tabular_view").addClass("hide");
			}

			/*Add hide class to navigation container on polling widget*/
			if(!$("#navigation_container").hasClass("hide")) {
				$("#navigation_container").addClass("hide");
			}

			this.hideLoading();

			/*Reset global variables*/
			allSSIds = [];
			polygonSelectedDevices = [];
			currentPolygon = {};
			polled_devices_names = [];
			complete_polled_devices_data = [];
			complete_polled_devices_icon = {};
			total_polled_occurence = 0;
			nav_click_counter = 0;
			polled_device_count = {};
		}

		var polygon = "";

		this.livePollingPolygonAdded = function(e) {
			global_this.livePollingPolygonControl.deactivate();
			polygon = e.feature;
			global_this.getMarkerInPolygon();
			currentPolygon = e.feature;
		}

		this.getMarkerInPolygon = function() {
			var allSS = pollableDevices;
			allSSIds = [];

			var selected_polling_technology = $("#polling_tech option:selected").text();

			for(var k=0;k<allSS.length;k++) {
				
				if(allSS[k].ptLon && allSS[k].ptLat && polygon) {
					if (displayBounds(polygon, allSS[k].ptLon, allSS[k].ptLat) === 'in') {
						if($.trim(allSS[k].technology.toLowerCase()) == $.trim(selected_polling_technology.toLowerCase())) {
							if($.trim(allSS[k].technology.toLowerCase()) == "ptp" || $.trim(allSS[k].technology.toLowerCase()) == "p2p") {
								if(allSS[k].device_name && (allSSIds.indexOf(allSS[k].device_name) == -1)) {
									allSSIds.push(allSS[k].device_name);
									polygonSelectedDevices.push(allSS[k]);
								}
							} else {
								if(allSS[k].pointType == 'sub_station') {
									if(allSS[k].device_name && (allSSIds.indexOf(allSS[k].device_name) == -1)) {
										allSSIds.push(allSS[k].device_name);
										polygonSelectedDevices.push(allSS[k]);
									}
								}
							}
						}
					}
				}
			}

			if(polygonSelectedDevices.length == 0) {
				
				if(global_this.livePollingPolygonControl) {
					global_this.livePollingPolygonControl.deactivate();
				}
				
				if(polygon) {
					/*Remove the current polygon from the map*/
					ccpl_map.getLayersByName('Polling')[0].removeAllFeatures();
				}

				/*Remove current polygon from map*/
				global_this.initLivePolling();

				/*Reset polling technology select box*/
				$("#polling_tech").val($("#polling_tech option:first").val());

				bootbox.alert("No SS found under the selected area.");

			} else if(polygonSelectedDevices.length > 200) {

				if(global_this.livePollingPolygonControl) {
					global_this.livePollingPolygonControl.deactivate();
				}
				
				if(polygon) {
					/*Remove the current polygon from the map*/
					ccpl_map.getLayersByName('Polling')[0].removeAllFeatures();
				}

				/*Remove current polygon from map*/
				global_this.initLivePolling();

				/*Reset polling technology select box*/
				$("#polling_tech").val($("#polling_tech option:first").val());

				bootbox.alert("Max. limit for selecting devices is 200.");

			} else {

				var devicesTemplate = "<div class='deviceWellContainer'>";
				var num_counter = 0;
				for(var i=0;i<polygonSelectedDevices.length;i++) {
					
					var new_device_name = "";
					var current_technology = $.trim(polygonSelectedDevices[i].technology.toLowerCase());
					
					if(polygonSelectedDevices[i].device_name.indexOf(".") != -1) {
						new_device_name = polygonSelectedDevices[i].device_name.split(".");
						new_device_name = new_device_name.join("-");
					} else {
						new_device_name = polygonSelectedDevices[i].device_name;
					}

					var devices_counter = "";
					if(current_technology == "ptp" || current_technology == "p2p") {					
						if(polygonSelectedDevices[i].pointType == 'sub_station') {
							devices_counter = polygonSelectedDevices[i].bs_sector_device;
						} else {
							devices_counter = polygonSelectedDevices[i].device_name;
						}

						if(!polled_device_count[devices_counter]) {
							polled_device_count[devices_counter]  = 1;
						} else {
							polled_device_count[devices_counter] = polled_device_count[devices_counter] +1;
						}
					}


					if((current_technology == 'ptp' || current_technology == 'p2p') && polygonSelectedDevices[i].pointType == 'sub_station') {

						if(polygonSelectedDevices[i].bs_sector_device.indexOf(".") != -1) {
							var new_device_name2 = polygonSelectedDevices[i].bs_sector_device.split(".");
							new_device_name2 = new_device_name2.join("-");
						} else {
							var new_device_name2 = polygonSelectedDevices[i].bs_sector_device;
						}

						if(polled_device_count[devices_counter] <= 1) {
							num_counter++;
							devicesTemplate += '<div class="well well-sm" id="div_'+new_device_name2+'"><h5>Near-End '+(i+1)+'.) '+polygonSelectedDevices[i].sector_ip+'</h5>';
							devicesTemplate += '<div style="min-height:60px;margin-top:15px;margin-bottom: 5px;" id="livePolling_'+new_device_name2+'">';
							devicesTemplate += '<ul id="pollVal_'+new_device_name2+'" class="list-unstyled list-inline"></ul>';
							devicesTemplate += '<span class="sparkline" id="sparkline_'+new_device_name2+'"></span></div></div>';
						}

						num_counter++;

						devicesTemplate += '<div class="well well-sm" id="div_'+new_device_name+'"><h5>Far-End '+(i+1)+'.) '+polygonSelectedDevices[i].ss_ip+'</h5>';
						devicesTemplate += '<div style="min-height:60px;margin-top:15px;margin-bottom: 5px;" id="livePolling_'+new_device_name+'">';
						devicesTemplate += '<ul id="pollVal_'+new_device_name+'" class="list-unstyled list-inline"></ul>';
						devicesTemplate += '<span class="sparkline" id="sparkline_'+new_device_name+'"></span></div></div>';

					} else {
						var device_end_txt = "",
							point_name = "";

						if(current_technology == "ptp" || current_technology == "p2p") {
							if(polled_device_count[devices_counter] <= 1) {
								if(polygonSelectedDevices[i].pointType == 'sub_station') {
									device_end_txt = "Far End";
									point_name = polygonSelectedDevices[i].ss_ip
								} else {
									device_end_txt = "Near End";
									point_name = polygonSelectedDevices[i].sectorName
								}

								num_counter++;
								devicesTemplate += '<div class="well well-sm" id="div_'+new_device_name+'"><h5>'+device_end_txt+''+(i+1)+'.) '+point_name+'</h5>';
								devicesTemplate += '<div style="min-height:60px;margin-top:15px;margin-bottom: 5px;" id="livePolling_'+new_device_name+'">';
								devicesTemplate += '<ul id="pollVal_'+new_device_name+'" class="list-unstyled list-inline"></ul>';
								devicesTemplate += '<span class="sparkline" id="sparkline_'+new_device_name+'"></span></div></div>';
							}
						} else {
							device_end_txt = "Far End";
							point_name = polygonSelectedDevices[i].ss_ip

							num_counter++;
							devicesTemplate += '<div class="well well-sm" id="div_'+new_device_name+'"><h5>'+device_end_txt+''+(i+1)+'.) '+point_name+'</h5>';
							devicesTemplate += '<div style="min-height:60px;margin-top:15px;margin-bottom: 5px;" id="livePolling_'+new_device_name+'">';
							devicesTemplate += '<ul id="pollVal_'+new_device_name+'" class="list-unstyled list-inline"></ul>';
							devicesTemplate += '<span class="sparkline" id="sparkline_'+new_device_name+'"></span></div></div>';
						}
					}
				}

				devicesTemplate += "</div>";

				$("#sideInfo > .panel-body > .col-md-12 > .devices_container").html(devicesTemplate);
			}
		}

		/**
		 * This function fetch the polling value for selected devices periodically as per the selected intervals.
		 * @method startDevicePolling_gmap
		 */
	    this.startDevicePolling_wmap = function() {
	    	if(remainingPollCalls > 0) {
				if(isPollingPaused == 0) {
					// Call function to fetch polled data for selected devices
					gmap_self.getPollingData_gmap(function(response) {
						pollCallingTimeout = setTimeout(function() {
							remainingPollCalls--;
							whiteMapClass.startDevicePolling_wmap();
						},pollingInterval);
					});
				} else {
					if($("#play_btn").hasClass("disabled")) {
		                $("#play_btn").removeClass("disabled");
		            }
		    		clearTimeout(pollCallingTimeout);
				}
	    	} else {
	    		if($("#play_btn").hasClass("disabled")) {
	                $("#play_btn").removeClass("disabled");
	            }
	    		clearTimeout(pollCallingTimeout);
	    	}
	    };


		/**
		 * This function show the polled devices data in tabular format & also give option to download that data
		 * @method show_polling_datatable
		 */
		this.show_polling_datatable_wmaps = function() {

			var table_html = "";

			table_html += "<div class='polling_table_container'><table style='z-index:9999;' id='polling_data_table' class='datatable table table-striped table-bordered table-hover'><thead><tr><th>Device Name</th><th>Time</th><th>Value</th></tr><thead><tbody>";

			for(var i=0;i<complete_polled_devices_data.length;i++) {
				table_html += '<tr>';
				table_html += '<td>'+complete_polled_devices_data[i].device_name+'</td>';
				table_html += '<td>'+complete_polled_devices_data[i].polling_time+'</td>';
				table_html += '<td>'+complete_polled_devices_data[i].polling_value+'</td>';
				table_html += '</tr>';
			}

			table_html += "</tbody></table></div><div class='clearfix'></div>";

			/*Call the bootbox to show the popup with Fresnel Zone Graph*/
			bootbox.dialog({
				message: table_html,
				title: '<i class="fa fa-dot-circle-o">&nbsp;</i> Polling Data - Tabular Format'
			});

			if($("#polling_data_table").length > 0) {
				/*Initialize Data Table*/
				$("#polling_data_table").DataTable({
					sDom: 'T<"clear">lfrtip',
					oTableTools: {
						sSwfPath : base_url+"/static/js/datatables/extras/TableTools/media/swf/copy_csv_xls.swf",
						aButtons : [
							{
								sExtends : "xls",
								sButtonText : "Download Excel",
								sFileName : "*.xls"
							}
						]
					},
					bProcessing : true,
					bPaginate : true,
					bAutoWidth : true,
					sPaginationType : "full_numbers"
				});
			}

		};

		/**
		* This function shows the previous polled icon(if available) on google maps for selected devices
		* * @method show_previous_polled_icon
		* */
		this.show_previous_polled_icon_wmaps = function() {
			if(nav_click_counter > 0) {
				nav_click_counter--;
			}
			/*Remove 'text-info' class from all li's*/
			$(".deviceWellContainer div div ul li").removeClass("text-info");

			for(var i=0;i<polled_devices_names.length;i++) {

				var marker_name = "",
					sector_ip = "";

				for(var x=0;x<polygonSelectedDevices.length;x++) {
					if(polygonSelectedDevices[x].device_name === polled_devices_names[i]) {
						marker_name = polygonSelectedDevices[x].name;
						if(polygonSelectedDevices[x].pointType === 'sub_station') {
							sector_ip = polygonSelectedDevices[x].sector_ip ? polygonSelectedDevices[x].sector_ip : "";
						} else {
							sector_ip = polygonSelectedDevices[x].sectorName ? polygonSelectedDevices[x].sectorName : "";
						}
					}
				}

				var ss_marker = wm_obj['features'][marker_name],
					sector_marker = wm_obj['devices']['sector_'+sector_ip],
					new_device_name = "";

				if(polled_devices_names[i] && polled_devices_names[i].indexOf(".") != -1) {
					new_device_name = polled_devices_names[i].split('.');
					new_device_name = new_device_name.join('-');
				} else {
					new_device_name = polled_devices_names[i];
				}

				if(nav_click_counter > 0) {
					newIcon = complete_polled_devices_icon[polled_devices_names[i]][nav_click_counter-1];
				} else {
					newIcon = complete_polled_devices_icon[polled_devices_names[i]][nav_click_counter];
				}

				if(ss_marker) {
					ss_marker.style.externalGraphic = newIcon;
				} else if(sector_marker) {
					sector_marker.style.externalGraphic = newIcon;
				}

				$("#pollVal_"+new_device_name+" li.fetchVal_"+new_device_name)[nav_click_counter-1].className = $("#pollVal_"+new_device_name+" li.fetchVal_"+new_device_name)[nav_click_counter-1].className+' text-info';
			}
			ccpl_map.getLayersByName('Markers')[0].redraw();
			ccpl_map.getLayersByName("Devices")[0].redraw();

			if((nav_click_counter-1) <= 0) {
				/*Disable next button*/
				$("#navigation_container button#previous_polling_btn").addClass('disabled');
			}
			/*Enable next button*/
			$("#navigation_container button#next_polling_btn").removeClass('disabled');
		};

		/**
	 	* This function shows the next polled icon(if available) on google maps for selected devices
	 	* @method show_next_polled_icon
	 	*/
		this.show_next_polled_icon_wmaps = function() {
			if(nav_click_counter <= total_polled_occurence) {
				nav_click_counter++;
			}

			$(".deviceWellContainer div div ul li").removeClass("text-info");

			for(var i=0;i<polled_devices_names.length;i++) {

				var marker_name = "",
					sector_ip = "";

				for(var x=0;x<polygonSelectedDevices.length;x++) {
					if(polygonSelectedDevices[x].device_name === polled_devices_names[i]) {
						marker_name = polygonSelectedDevices[x].name;
						if(polygonSelectedDevices[x].pointType === 'sub_station') {
							sector_ip = polygonSelectedDevices[x].sector_ip ? polygonSelectedDevices[x].sector_ip : "";
						} else {
							sector_ip = polygonSelectedDevices[x].sectorName ? polygonSelectedDevices[x].sectorName : "";
						}
					}
				}

				var ss_marker = wm_obj['features'][marker_name],
					sector_marker = wm_obj['devices']['sector_'+sector_ip],
					new_device_name = "";

				if(polled_devices_names[i] && polled_devices_names[i].indexOf(".") != -1) {
					new_device_name = polled_devices_names[i].split('.');
					new_device_name = new_device_name.join('-');
				} else {
					new_device_name = polled_devices_names[i];
				}

				if(nav_click_counter > 0) {
					newIcon = complete_polled_devices_icon[polled_devices_names[i]][nav_click_counter-1];
				} else {
					newIcon = complete_polled_devices_icon[polled_devices_names[i]][nav_click_counter];
				}

				if(ss_marker) {
					ss_marker.style.externalGraphic = newIcon;
					
				} else if(sector_marker) {
					sector_marker.style.externalGraphic = newIcon;
				}
				$("#pollVal_"+new_device_name+" li.fetchVal_"+new_device_name)[nav_click_counter-1].className = $("#pollVal_"+new_device_name+" li.fetchVal_"+new_device_name)[nav_click_counter-1].className+' text-info';
			}
			ccpl_map.getLayersByName('Markers')[0].redraw();
			ccpl_map.getLayersByName("Devices")[0].redraw();

			if((nav_click_counter+1) > total_polled_occurence) {
				/*Disable next button*/
				$("#navigation_container button#next_polling_btn").addClass('disabled');
			}

			/*Enable previous button*/
			$("#navigation_container button#previous_polling_btn").removeClass('disabled');
		};
	/**
	 * 
	 * End of Polling Section
	 */

	 /**
	 * 
	 * Tools Section
	 */
		/*
		This function is activated when Show/Hide Line option is changed.
		Display or hide CktID Lines based on its value
		 */
		var previousValue= "";
		this.toggleLines = function() {
			//Checked if Show/Hide option is checked or unchecked.
			var selectedValue = $("#showConnLines").prop('checked');
			if(previousValue !== selectedValue) {
				var linesFeaturesList = [];
				for(var key in cktLinesBsObj) {
					var x= cktLinesBsObj[key];
					if(x && x.length) {
						for(var i=0; i< x.length; i++) {
							
							if(x[i].filteredLine) {
								x[i].style.display = 'block';
								linesFeaturesList.push(x[i]);
							}
						}
					}
				}
				// ccpl_map.getLayersByName("Lines")[0].removeAllFeatures();
				if(selectedValue) {
					// ccpl_map.getLayersByName("Lines")[0].addFeatures(linesFeaturesList);
				}
				// ccpl_map.getLayersByName("Lines")[0].redraw();
				previousValue= selectedValue;
			}
		}
		/*
		This function toggles all Station Marker
		s size based on the Value selected in the dropdown.
		 */
		this.updateMarkersSize = function(iconSize) {
			global_this.unSpiderifyBsMarker();
			var largeur= 32, hauteur= 37,largeur_bs = 32, hauteur_bs= 37, divideBy;
			var anchorX, i, markerImage, markerImage2, icon;
			if(iconSize=== 'small') {
				divideBy= 1.4;
				anchorX= 0.4;
			} else if(iconSize=== 'medium') {
				divideBy= 1;
				anchorX= 0;
			} else {
				divideBy= 0.8;
				anchorX= -0.2;
			}

			//Loop through the sector markers
			for(i=0; i< sector_MarkersArray.length; i++) {
				(function updateSectMarker(marker) {
					var newGraphicHeight = 0, newGraphicWidth = 0, newGraphicXOffset = 0, newGraphicYOffset = 0;
					newGraphicWidth = Math.ceil(largeur/divideBy);
					newGraphicHeight = Math.ceil(hauteur/divideBy);
					newGraphicXOffset = Math.ceil(16-(16*anchorX));
					newGraphicYOffset = Math.ceil(hauteur/divideBy);

					marker.style.graphicWidth = newGraphicWidth;
					marker.style.graphicHeight = newGraphicHeight;
					// marker.style.graphicXOffset = newGraphicXOffset;
					// marker.style.graphicYOffset = newGraphicYOffset;
					
					// 
					ccpl_map.getLayersByName("Devices")[0].drawFeature(marker);
				})(sector_MarkersArray[i]);
			}
			//End of Loop through the sector markers

			ccpl_map.getLayersByName("Devices")[0].redraw();
			ccpl_map.getLayersByName("Devices")[0].removeAllFeatures();


			// Loop through the Master Markers
			for(var i=0; i< masterMarkersObj.length; i++ ) {
				(function updateMasterMarker(marker) {

					var newGraphicHeight = 0, newGraphicWidth = 0, newGraphicXOffset = 0, newGraphicYOffset = 0;
					if(marker.pointType=== "base_station") {
						newGraphicHeight= Math.ceil(hauteur_bs/divideBy)+5;
						newGraphicWidth = Math.ceil(largeur_bs/divideBy)-5;
						newGraphicXOffset = Math.ceil(16-(16*anchorX));
						newGraphicYOffset = Math.ceil(hauteur_bs/divideBy);

						marker.style.graphicWidth = newGraphicWidth;
						marker.style.graphicHeight = newGraphicHeight;
						// marker.style.graphicXOffset = newGraphicXOffset;
						// marker.style.graphicYOffset = newGraphicYOffset;
						
						// 
						ccpl_map.getLayersByName('Markers')[0].drawFeature(marker);
					} else if (marker.pointType === "sub_station") {
						newGraphicWidth = Math.ceil(largeur/divideBy);
						newGraphicHeight = Math.ceil(hauteur/divideBy);
						newGraphicXOffset = Math.ceil(16-(16*anchorX));
						newGraphicYOffset = Math.ceil(hauteur/divideBy);

						marker.style.graphicWidth = newGraphicWidth;
						marker.style.graphicHeight = newGraphicHeight;
						// marker.style.graphicXOffset = newGraphicXOffset;
						// marker.style.graphicYOffset = newGraphicYOffset;
						
						// 
						ccpl_map.getLayersByName('Markers')[0].drawFeature(marker);
					}
				})(masterMarkersObj[i]);
			}
			//End of Loop through the Master Markers
			//
			ccpl_map.getLayersByName('Markers')[0].redraw();

			ccpl_map.getLayersByName('Markers')[0].strategies[0].recluster();
		}
		/*
		This function is triggered when Lat Lng Search is done.Validate the point, if LatLng is valid, zoom to the given lat lng.
		 */
		this.zoomToLonLat = function(lat_long_string) {
			var lat = +lat_long_string.split(",")[0], lng = +lat_long_string.split(",")[1];
			var bounds = new OpenLayers.Bounds;
			var lonLat = new OpenLayers.LonLat(lng, lat);
			bounds.extend(lonLat);
			ccpl_map.zoomToExtent(bounds);
		}
		this.goFullScreen= function() {
			$("#content_div").hide();
			$("#map").width("100%");
		}
	/**
	 * 
	 * End of Tools Section
	 */

	/**
	* Search and Filter Section
	* */

		/*
		This function updates the openLayer map with the filteredData
		 */
		this.applyAdvanceFilter = function(appliedFilterData) {
			this.unSpiderifyBsMarker();

			data_for_filter_wmap= [];

			//set data for filter
			data_for_filter_wmap = appliedFilterData.data_for_filters;

			//remove features from markersLayer and add filteredFeatures
			ccpl_map.getLayersByName('Markers')[0].removeAllFeatures();
			ccpl_map.getLayersByName('Markers')[0].addFeatures(appliedFilterData.filtered_Features);
			filtered_Features.markers = appliedFilterData.filtered_Features;

			bsDevicesObj = appliedFilterData.filtered_Devices;
			

			//remove lines from linesLayer and add filteredLine
			ccpl_map.getLayersByName("Lines")[0].removeAllFeatures();
			ccpl_map.getLayersByName("Lines")[0].addFeatures(appliedFilterData.line_Features);
			filtered_Features.lines = appliedFilterData.line_Features;

			//remove sectors from sectorsLayer and add filtered sectors
			ccpl_map.getLayersByName("Sectors")[0].removeAllFeatures();
			ccpl_map.getLayersByName("Sectors")[0].addFeatures(appliedFilterData.sector_Features);
			filtered_Features.sectors = appliedFilterData.sector_Features;
						
			//rescluster the strategy
			ccpl_map.getLayersByName('Markers')[0].strategies[0].recluster();

			//update page status
			get_page_status();

			this.refreshLineLayers();

			/*Enable Reset Button*/
			global_this.hideLoading();
		}

	/**
	 * End of Search and Filter Functions
	 */	
	
	/**
	 * This function show connection lines within the bounds
	 * @method showLinesInBounds
	 */
	this.showLinesInBounds = function() {

		if(isDebug) {
			console.log("Show in bound lines Function");
			console.log("Show in bound lines Start Time :- "+ new Date().toLocaleString());
		}

		var isLineChecked = $("#showConnLines:checked").length;
		/*checked case*/
		if(isLineChecked > 0) {
			/*Loop for polylines*/
			for(var key in allMarkersObject_wmap['path']) {
				if(allMarkersObject_wmap['path'].hasOwnProperty(key)) {
			    	var current_line = allMarkersObject_wmap['path'][key];
			    	if(current_line) {
					    var nearEndVisible = global_this.checkIfPointLiesInside({lat: current_line.nearLat, lon: current_line.nearLon}),
					      	farEndVisible = global_this.checkIfPointLiesInside({lat: current_line.ss_lat, lon: current_line.ss_lon}),
					      	connected_bs = allMarkersObject_wmap['base_station']['bs_'+current_line.filter_data.bs_name],
					      	connected_ss = allMarkersObject_wmap['sub_station']['ss_'+current_line.filter_data.ss_name];

					    if((nearEndVisible || farEndVisible) && ((connected_bs && connected_ss) && (connected_bs.isActive != 0 && connected_ss.isActive != 0))) {
					    	// If polyline not shown then show the polyline
					    	if(!current_line.map) {
					    		showOpenLayerFeature(current_line);
					    	}
					    } else {
					    	// If polyline shown then hide the polyline
					    	if(current_line.map) {
					    		hideOpenLayerFeature(current_line);
				    		}
					    }
			    	}
			    }
			}
		}

		if(isDebug) {
			console.log("Show in bound lines End Time :- "+ new Date().toLocaleString());
			console.log("**********************************");
		}
	};
	

	/**
	 * This function show sub-stations within the bounds
	 * @method showSubStaionsInBounds
	 */
	this.showSubStaionsInBounds = function() {
		if(isDebug) {
			console.log("Show in bound SS Function");
			console.log("Show in bound SS Start Time :- "+ new Date().toLocaleString());
		}
 		var isSSChecked = $("#showAllSS:checked").length;

		/*Checked case*/
		if(isSSChecked > 0) {
			/*Loop for polylines*/
			for(var key in allMarkersObject_wmap['sub_station']) {
				if(allMarkersObject_wmap['sub_station'].hasOwnProperty(key)) {
			    	var ss_marker = allMarkersObject_wmap['sub_station'][key],
			    		isMarkerExist = "";
			    	isMarkerExist= global_this.checkIfPointLiesInside({lat: ss_marker.ptLat, lon: ss_marker.ptLon});
			    		// mapInstance.getBounds().contains(ss_marker.getPosition());
		    		if(isMarkerExist) {
				    	if(ss_marker.isActive && +(ss_marker.isActive) === 1) {
				    		// If SS Marker not shown then show the SS Marker
				    		if(!allMarkersObject_wmap['sub_station'][key].map) {
				    			showOpenLayerFeature(allMarkersObject_wmap['sub_station'][key]);
				    		}
				    	} else {
				    		// If SS Marker shown then hide the SS Marker
				    		if(allMarkersObject_wmap['sub_station'][key].map) {
				    			hideOpenLayerFeature(allMarkersObject_wmap['sub_station'][key]);
			    			}
				    	}
		    		}
			    }
			}
		}

		if(isDebug) {
			console.log("Show in bound SS End Time :- "+ new Date().toLocaleString());
			console.log("***********************************");
		}
	};

	/**
	 * This function show base-stations within the bounds
	 * @method showBaseStaionsInBounds
	 */
	this.showBaseStaionsInBounds = function() {
		if(isDebug) {
			console.log("Show in bound BS");
			console.log("Show in bound BS Start Time :- "+ new Date().toLocaleString());
		}
		// var plotted_bs_ids = [];
		/*Loop for polylines*/
		for(var key in allMarkersObject_wmap['base_station']) {
			if(allMarkersObject_wmap['base_station'].hasOwnProperty(key)) {
		    	var bs_marker = allMarkersObject_wmap['base_station'][key],
		      		isMarkerExist = "";
		      	isMarkerExist = global_this.checkIfPointLiesInside({lat: bs_marker.ptLat, lon: bs_marker.ptLon});
	      		if(isMarkerExist) {
			    	if(bs_marker.isActive && +(bs_marker.isActive) === 1) {
			    		// If BS Marker not shown then show the BS Marker
			    		if(!allMarkersObject_wmap['base_station'][key].map) {
			      			showOpenLayerFeature(allMarkersObject_wmap['base_station'][key]);
			    		}
			    		// plotted_bs_ids.push(allMarkersObject_wmap['base_station'][key].filter_data.bs_id);
			        } else {
			        	// If BS Marker shown then hide the BS Marker
			        	if(allMarkersObject_wmap['base_station'][key].map) {
			      			hideOpenLayerFeature(allMarkersObject_wmap['base_station'][key]);
		        		}
			        }
	      		}
		    }
		}

		// var sector_to_plot = all_devices_loki_db.where(function(obj){return plotted_bs_ids.indexOf(obj.originalId) > -1;});
		if(isDebug) {
			console.log("Show in bound BS End Time :- "+ new Date().toLocaleString());
			console.log("**********************************");
		}
	};

	/**
	 * This function show base-stations devices(sector devices) within the bounds
	 * @method showSectorDevicesInBounds
	 */
	this.showSectorDevicesInBounds = function() {
		if(isDebug) {
			console.log("Show in bound Sector Devices");
			console.log("Show in bound Sector Devices Start Time :- "+ new Date().toLocaleString());
		}
		/*Loop for polylines*/
		for(var key in allMarkersObject_wmap['sector_device']) {
			if(allMarkersObject_wmap['sector_device'].hasOwnProperty(key)) {
		    	var sector_marker = allMarkersObject_wmap['sector_device'][key],
		      		isMarkerExist = "";
		      	isMarkerExist = global_this.checkIfPointLiesInside({lat: sector_marker.ptLat, lon: sector_marker.ptLon});
	      		if(isMarkerExist) {
			    	if(sector_marker.isActive && +(sector_marker.isActive) === 1) {
			    		// If Sector Marker not shown then show the Sector Marker
			    		if(!allMarkersObject_wmap['sector_device'][key].map) {
			      			showOpenLayerFeature(allMarkersObject_wmap['sector_device'][key]);
			    		}
			    	} else {
			    		// If Sector Marker shown then hide the Sector Marker
			    		if(allMarkersObject_wmap['sector_device'][key].map) {
			    			hideOpenLayerFeature(allMarkersObject_wmap['sector_device'][key]);
		    			}
			        }
	      		}
		  }
		}
		if(isDebug) {
			console.log("Show in bound Sector Devices End Time :- "+ new Date().toLocaleString());
			console.log("******************************************");
		}
	};

	/**
	 * This function show polygon(sector) within the bounds
	 * @method showSectorPolygonInBounds
	 */
	this.showSectorPolygonInBounds = function() {
		if(isDebug) {
			console.log("Show in bound Sector Polygons");
			console.log("Show in bound Sector Polygons Start Time :- "+ new Date().toLocaleString());
		}
		/*Loop for polylines*/
		for(var key in allMarkersObject_wmap['sector_polygon']) {
			if(allMarkersObject_wmap['sector_polygon'].hasOwnProperty(key)) {
		    	var sector_polygon = allMarkersObject_wmap['sector_polygon'][key],
		    		isMarkerExist = "";
		    	isMarkerExist = global_this.checkIfPointLiesInside({lat: sector_polygon.ptLat, lon: sector_polygon.ptLon});
	    		if(isMarkerExist) {
			    	if(sector_polygon.isActive && +(sector_polygon.isActive) === 1) {
			    		// If Polygon not shown then show the polygon
			    		if(!allMarkersObject_wmap['sector_polygon'][key].map) {
			      			showOpenLayerFeature(allMarkersObject_wmap['sector_polygon'][key]);
			    		}
			    	} else {
			    		// If Polygon shown then hide the polygon
			    		if(allMarkersObject_wmap['sector_polygon'][key].map) {
			      			hideOpenLayerFeature(allMarkersObject_wmap['sector_polygon'][key]);
		    			}
			        }
	    		}
		    }
		}
		if(isDebug) {
			console.log("Show in bound Sector Polygons End Time :- "+ new Date().toLocaleString());
			console.log("***********************************");
		}
	};

	/**
	 * This function show/hide the connection line between BS & SS.
	 * @method showConnectionLines_gmap
	 */
	this.showConnectionLines_wmap = function() {
		if(isDebug) {
			console.log("Show/Hide Connection Lines");
			console.log("Show/Hide Connection Lines Start Time :- "+ new Date().toLocaleString());
		}

		var isLineChecked = $("#showConnLines:checked").length;

		var current_lines = ssLinkArray_filtered;

		/*Unchecked case*/
		if(isLineChecked == 0) {
			for(key in allMarkersObject_wmap['path']) {
				if(allMarkersObject_wmap['path'][key].map) {
					hideOpenLayerFeature(allMarkersObject_wmap['path'][key]);
				}
			}

		} else {
			for(key in allMarkersObject_wmap['path']) {
				if(!allMarkersObject_wmap['path'][key].map) {
					showOpenLayerFeature(allMarkersObject_wmap['path'][key]);
				}
			}
		}

		if(isDebug) {
			console.log("Show/Hide Connection Lines End Time :- "+ new Date().toLocaleString());
			console.log("********************************");
		}
	};

	/**
	 * This function show/hide the sub-stations.
	 * @method showSubStations_wmap
	 */
	this.showSubStations_wmap = function() {

		if(isDebug) {
			console.log("Show/Hide SS");
			console.log("Show/Hide SS Start Time :- "+ new Date().toLocaleString());
		}

		var isSSChecked = $("#showAllSS:checked").length;

		/*Unchecked case*/
		if(isSSChecked == 0) {
			for(key in allMarkersObject_wmap['sub_station']) {
				if(allMarkersObject_wmap['sub_station'][key].map) {
					hideOpenLayerFeature(allMarkersObject_wmap['sub_station'][key]);
				}
			}

		} else {
			for(key in allMarkersObject_wmap['sub_station']) {
				if(!allMarkersObject_wmap['sub_station'][key].map) {
					showOpenLayerFeature(allMarkersObject_wmap['sub_station'][key]);
				}
			}
		}

		if(isDebug) {
			console.log("Show/Hide SS End Time :- "+ new Date().toLocaleString());
			console.log("*********************************");
		}
	};

	/**
	 *
	 * Plotting Section
	 */
	
		this.clearStateCounters_wmaps = function() {
			for(key in state_wise_device_counters) {
				state_wise_device_counters[key] = 0;
				if(state_wise_device_labels[key]) {
					state_wise_device_labels[key].destroy();
				}
			}
			ccpl_map.getLayersByName('States')[0].redraw();
		}
	 	
	 	/**
	 	* This function show counter of state wise data on gmap
	 	* @method showStateWiseData_wmap
	     * @param dataset {Object} In case of BS, it is the devies object array & for SS it contains BS marker object with SS & sector info
		 */
		this.showStateWiseData_wmap = function(dataset) {
			if(isDebug) {
				console.log("State Wise Clusters Function")
				console.log("State Cluster Plotting Start Time :- "+ new Date().toLocaleString());
			}
			//Loop For Base Station
			for(var i=dataset.length;i--;) {

				/*Create BS state,city object*/
				if(dataset[i].data.state) {

					state_city_obj[dataset[i].data.state] = state_city_obj[dataset[i].data.state] ? state_city_obj[dataset[i].data.state] : [];
					if(state_city_obj[dataset[i].data.state].indexOf(dataset[i].data.city) == -1) {
						state_city_obj[dataset[i].data.state].push(dataset[i].data.city);
					}
				}

				if(dataset[i].data.city) {
					if(all_cities_array.indexOf(dataset[i].data.city) == -1) {
						all_cities_array.push(dataset[i].data.city); 
					}
				}

				var current_bs = dataset[i],
					state = current_bs.data.state,
					sectors_data = current_bs.data.param.sector ? current_bs.data.param.sector : [],
					update_state_str = state ? state : "",
					state_lat_lon_obj = state_lat_lon_db.find({"name" : update_state_str}).length > 0 ? state_lat_lon_db.find({"name" : update_state_str})[0] : false,
					state_param = state_lat_lon_obj ? JSON.stringify(state_lat_lon_obj) : false,
					state_click_event = "onClick='gmap_self.state_label_clicked("+state_param+")'";

				// If state is not null
				if(state) {
					if(state_wise_device_counters[state]) {
						state_wise_device_counters[state] += 1;
						if(state_lat_lon_obj) {
							// Update the content of state counter label as per devices count
							state_wise_device_labels[state].attributes.label = state_wise_device_counters[state];
							state_wise_device_labels[state].attributes.display = '';
						}
					} else {
						state_wise_device_counters[state] = 1;
						if(state_lat_lon_obj) {
					        // create a point feature
				            var point = new OpenLayers.Geometry.Point(state_lat_lon_obj.lon, state_lat_lon_obj.lat);
				            var device_counter_label = new OpenLayers.Feature.Vector(point);
				            device_counter_label.attributes = {
				                label: state_wise_device_counters[state],
				                state: state,
				                state_param: state_lat_lon_obj,
				                cursor: "pointer",
				                title: "Load "+ state+ " Data",
				                display: ''
				            };
				            device_counter_label.map = 'current';
				            
				            ccpl_map.getLayersByName('States')[0].addFeatures([device_counter_label]);
						}
				        state_wise_device_labels[state] = device_counter_label;
					}
				} else {
					var lat = current_bs.data.lat,
						lon = current_bs.data.lon,
						allStateBoundries = state_boundries_db.data;
						// bs_point = new google.maps.LatLng(lat,lon);

					// Loop to find that the lat lon of BS lies in which state.
					for(var y=allStateBoundries.length;y--;) {
						var current_state_boundries = allStateBoundries[y].boundries,
							current_state_name = allStateBoundries[y].name,
							latLonArray = [];

						if(current_state_boundries.length > 0) {
							for(var z=current_state_boundries.length;z--;) {
								latLonArray.push({lat: current_state_boundries[z].lat, lon: current_state_boundries[z].lon});
							}

							if(isPointInPoly(latLonArray, {lat: lat, lon: lon})) {
								//Update json with state name
								dataset[i]['data']['state'] = current_state_name;
								state = current_state_name;
	                            state_lat_lon_obj = state_lat_lon_db.find({"name" : state}).length > 0 ? state_lat_lon_db.find({"name" : state})[0] : false;
	                            state_param = state_lat_lon_obj ? JSON.stringify(state_lat_lon_obj) : false;
	                            state_click_event = "onClick='gmap_self.state_label_clicked("+state_param+")'";

								var new_lat_lon_obj = state_lat_lon_db.where(function(obj) {
									return obj.name === current_state_name;
								});
								if(state_wise_device_counters[current_state_name]) {
									state_wise_device_counters[current_state_name] += 1;
									state_wise_device_labels[current_state_name].attributes.label = state_wise_device_counters[current_state_name];
									state_wise_device_labels[current_state_name].attributes.display = '';
								} else {
									state_wise_device_counters[current_state_name] = 1;
									
						        	// create a point feature
						            var point = new OpenLayers.Geometry.Point(new_lat_lon_obj[0].lon, new_lat_lon_obj[0].lat);
						            var device_counter_label = new OpenLayers.Feature.Vector(point);
						            device_counter_label.attributes = {
						                label: state_wise_device_counters[current_state_name],
						                state: current_state_name,
				                		state_param: state_lat_lon_obj,
				                		title: "Load "+ current_state_name+ " Data",
				                		cursor: "pointer",
				                		display: ''
						            };
						            device_counter_label.map = 'current';

						            ccpl_map.getLayersByName('States')[0].addFeatures([device_counter_label]);
							        state_wise_device_labels[current_state_name] = device_counter_label;
								}

								// Break for loop if state found
								break;
							}
						}
					}
				}
				/*Insert devices object to loki db variables*/
				if(isApiResponse === 1) {
					all_devices_loki_db.insert(dataset[i]);
				}

				//Loop For Sector Devices
				for(var j=sectors_data.length;j--;) {

					tech_vendor_obj[sectors_data[j].technology] = tech_vendor_obj[sectors_data[j].technology] ? tech_vendor_obj[sectors_data[j].technology] : [];
					if(tech_vendor_obj[sectors_data[j].technology].indexOf(sectors_data[j].vendor) == -1) {
						tech_vendor_obj[sectors_data[j].technology].push(sectors_data[j].vendor);
					}

					if(all_vendor_array.indexOf(sectors_data[j].vendor) == -1) {
						all_vendor_array.push(sectors_data[j].vendor); 
					}

					var total_ss = sectors_data[j].sub_station ? sectors_data[j].sub_station.length : 0;
					// state_wise_device_counters[state] += 1;
					state_wise_device_counters[state] += total_ss;
					if(state_lat_lon_obj) {
						state_wise_device_labels[state].attributes.label = state_wise_device_counters[state];
					}
				}
			}

			if(isCallCompleted == 1) {
				/*Hide The loading Icon*/
				$("#loadingIcon").hide();

				/*Enable the refresh button*/
				$("#resetFilters").button("complete");
				
				if(isFirstTime == 1) {
					/*Load data for basic filters*/
					gmap_self.getBasicFilters();
				}
			}

			ccpl_map.getLayersByName('States')[0].refresh();
			ccpl_map.getLayersByName('States')[0].redraw();

			if(isDebug) {
				console.log("State Cluster Plotting End Time :- "+ new Date().toLocaleString());
				console.log("*******************************************");
			}
		};

		/*
		 * This function is used to plot BS or SS devices & their respective elements on the White Background
		 * @method plotDevices_gmap
		 * @param bs_ss_devices {Object} In case of BS, it is the devies object array & for SS it contains BS marker object with SS & sector info
		 * @param stationType {String}, It contains that the points are for BS or SS.
		 */
		
	    this.plotDevices_wmaps = function(bs_ss_devices, stationType) {
			if(isDebug) {
				console.log("Plot Devices Function");
				console.log("Plot Devices Start Time :- "+ new Date().toLocaleString());
			}
			var zoom_level = ccpl_map.getZoom();

			//Loop through the bs_ss_devices
			for(var i=0; i< bs_ss_devices.length; i++) {
				wm_obj.data[bs_ss_devices[i].name] = bs_ss_devices[i];
				
				var lon = bs_ss_devices[i].data.lon, 
					lat = bs_ss_devices[i].data.lat, 
					icon = base_url+"/static/img/icons/bs.png", 
					size = new OpenLayers.Size(whiteMapSettings.size.medium.width, whiteMapSettings.size.medium.height);
				/*Create BS Marker Object*/
				var bs_marker_object = {
					position  	       : 	{lat: bs_ss_devices[i].data.lat, lon: bs_ss_devices[i].data.lon},
					ptLat 		       : 	bs_ss_devices[i].data.lat,
					ptLon 		       : 	bs_ss_devices[i].data.lon,
					map       	       : 	'current',
					icon 	  	       : 	base_url+"/static/img/icons/bs.png",
					oldIcon 	       : 	base_url+"/static/img/icons/bs.png",
					clusterIcon 	   : 	base_url+"/static/img/icons/bs.png",
					pointType	       : 	stationType,
					child_ss   	       : 	bs_ss_devices[i].data.param.sector,
					dataset 	       : 	bs_ss_devices[i].data.param.base_station,
					device_name 	   : 	bs_ss_devices[i].data.device_name,
					bsInfo 			   : 	bs_ss_devices[i].data.param.base_station,
					bhInfo 			   : 	bs_ss_devices[i].data.param.backhual,
					bs_name 		   : 	bs_ss_devices[i].name,
					bs_alias 		   :    bs_ss_devices[i].alias,
					name 		 	   : 	bs_ss_devices[i].name,
					filter_data 	   : 	{"bs_name" : bs_ss_devices[i].name, "bs_id" : bs_ss_devices[i].originalId},
					antenna_height     : 	bs_ss_devices[i].data.antenna_height,
					zIndex 			   : 	250,
					optimized 		   : 	false,
					markerType 		   : 	'BS',
					isMarkerSpiderfied : 	false,
					isActive 		   : 	1,
					layerReference: ccpl_map.getLayersByName("Markers")[0]
				};

				var bs_marker = global_this.createOpenLayerVectorMarker(size, icon, lon, lat, bs_marker_object);
				bs_ss_markers.push(bs_marker);

				// ccpl_map.getLayersByName("Markers")[0].addFeatures([bs_marker]);

				/*Sectors Array*/
				var sector_array = bs_ss_devices[i].data.param.sector;
				var deviceIDArray= [];
				
				/*Plot Sector*/
				for (var j = 0; j < sector_array.length; j++) {

					var lat = bs_ss_devices[i].data.lat,
						lon = bs_ss_devices[i].data.lon,
						azimuth = sector_array[j].azimuth_angle,
						beam_width = sector_array[j].beam_width,
						sector_color = sector_array[j].color,
						sectorInfo = {
							"info" : sector_array[j].info,
							"bs_name" : bs_ss_devices[i].name,
							"sector_name" : sector_array[j].sector_configured_on,
							"sector_id" : sector_array[j].sector_id,
							"device_info" : sector_array[j].device_info,
							"technology" : sector_array[j].technology,
							"vendor" : sector_array[j].vendor
						},
						orientation = $.trim(sector_array[j].orientation),
						sector_child = sector_array[j].sub_station,
						rad = 4,
						sectorRadius = (+sector_array[j].radius),
						startLon = "",
						startLat = "";

					/*If radius is greater than 4 Kms then set it to 4.*/
					if(sectorRadius && (sectorRadius > 0)) {
						rad = sectorRadius;
					}

					var startEndObj = {};

					if($.trim(sector_array[j].technology) != "PTP" && $.trim(sector_array[j].technology) != "P2P") {
						// if(zoom_level > 9) {
							/*Call createSectorData function to get the points array to plot the sector on google maps.*/
							gmap_self.createSectorData(lat,lon,rad,azimuth,beam_width,orientation,function(pointsArray) {
							
								var halfPt = Math.floor(pointsArray.length / (+2));

								/*Plot sector on map with the retrived points*/
								whiteMapClass.plotSector_wmap(lat,lon,pointsArray,sectorInfo,sector_color,sector_child,$.trim(sector_array[j].technology),orientation,rad,azimuth,beam_width);

								startEndObj["startLat"] = pointsArray[halfPt].lat;
								startEndObj["startLon"] = pointsArray[halfPt].lon;
								startEndObj["sectorLat"] = pointsArray[halfPt].lat;
								startEndObj["sectorLon"] = pointsArray[halfPt].lon;
							});
						// }

					} else {

						startEndObj["startLat"] = bs_ss_devices[i].data.lat;
		    			startEndObj["startLon"] = bs_ss_devices[i].data.lon;
		    			
		    			startEndObj["sectorLat"] = bs_ss_devices[i].data.lat;
						startEndObj["sectorLon"] = bs_ss_devices[i].data.lon;
					}

					if($.trim(sector_array[j].technology.toLowerCase()) == "ptp" || $.trim(sector_array[j].technology.toLowerCase()) == "p2p") {

						if(deviceIDArray.indexOf(sector_array[j]['device_info'][1]['value']) === -1) {

							var sectors_Markers_Obj = {
								position 		 	: {lat: lat, lon: lon},
								map 				: 'current',
								ptLat 			 	: lat,
								ptLon 			 	: lon,
								icon 			 	: base_url+'/static/img/icons/1x1.png',
								oldIcon 		 	: base_url+"/"+sector_array[j].markerUrl,
								clusterIcon 	 	: base_url+'/static/img/icons/1x1.png',
								pointType 		 	: 'sector_Marker',
								technology 		 	: sector_array[j].technology,
								vendor 				: sector_array[j].vendor,
								deviceExtraInfo 	: sector_array[j].info,
								deviceInfo 			: sector_array[j].device_info,
								poll_info 			: [],
								pl 					: "",
								rta					: "",
								sectorName  		: sector_array[j].sector_configured_on,
								device_name  		: sector_array[j].sector_configured_on_device,
								name  				: sector_array[j].sector_configured_on_device,
								filter_data 	    : {"bs_name" : bs_ss_devices[i].name, "sector_name" : sector_array[j].sector_configured_on, "bs_id" : bs_ss_devices[i].originalId, "sector_id" : sector_array[j].sector_id},
								sector_lat  		: startEndObj["startLat"],
								sector_lon  		: startEndObj["startLon"],
								zIndex 				: 200,
								optimized 			: false,
								hasPerf  			: 0,
		                        antenna_height 		: sector_array[j].antenna_height,
		                        isActive 			: 1,
		                        layerReference: ccpl_map.getLayersByName("Devices")[0]
		                    }
		                }

		                var sect_height = sector_array[j].antenna_height;

						/*Create Sector Marker*/
						var sector_Marker = global_this.createOpenLayerVectorMarker(size, sectors_Markers_Obj.icon, lon, lat, sectors_Markers_Obj);

						bsDevicesObj

						if(!bsDevicesObj[bs_ss_devices[i].name]) {
							bsDevicesObj[bs_ss_devices[i].name]= [];
						}
						bsDevicesObj[bs_ss_devices[i].name].push(sector_Marker);

						ccpl_map.getLayersByName("Devices")[0].addFeatures([sector_Marker]);

						if(sectorMarkerConfiguredOn.indexOf(sector_array[j].sector_configured_on) == -1) {
							sector_MarkersArray.push(sector_Marker);
							allMarkersArray_wmap.push(sector_Marker);

							/*Push Sector marker to pollableDevices array*/
							pollableDevices.push(sector_Marker);
							
							allMarkersObject_wmap['sector_device']['sector_'+sector_array[j].sector_configured_on] = sector_Marker;

							sectorMarkerConfiguredOn.push(sector_array[j].sector_configured_on);
							if(sectorMarkersMasterObj[bs_ss_devices[i].name]) {
								sectorMarkersMasterObj[bs_ss_devices[i].name].push(sector_Marker)
							} else {
								sectorMarkersMasterObj[bs_ss_devices[i].name]= [];
								sectorMarkersMasterObj[bs_ss_devices[i].name].push(sector_Marker)
							}	
						}

						/*End of Create Sector Marker*/
						deviceIDArray.push(sector_array[j]['device_info'][1]['value']);
					}

					/*Plot Sub-Station*/
					for(var k=sector_child.length;k--;) {

					
						var ss_marker_obj = sector_child[k];

						/*Create SS Marker Object*/
						var ss_marker_object = {
							position 		 : 	{lat: ss_marker_obj.data.lat, lon: ss_marker_obj.data.lon},
					    	ptLat 			 : 	ss_marker_obj.data.lat,
					    	ptLon 			 : 	ss_marker_obj.data.lon,
					    	technology 		 : 	ss_marker_obj.data.technology,
					    	map 			 : 	'current',
					    	icon 			 : 	base_url+"/"+ss_marker_obj.data.markerUrl,
					    	oldIcon 		 : 	base_url+"/"+ss_marker_obj.data.markerUrl,
					    	clusterIcon 	 : 	base_url+"/"+ss_marker_obj.data.markerUrl,
					    	pointType	     : 	"sub_station",
					    	dataset 	     : 	ss_marker_obj.data.param.sub_station,
					    	bhInfo 			 : 	[],
					    	poll_info 		 :  [],
					    	pl 				 :  "",
							rta				 :  "",
					    	antenna_height   : 	ss_marker_obj.data.antenna_height,
					    	name 		 	 : 	ss_marker_obj.name,
					    	bs_name 		 :  bs_ss_devices[i].name,
					    	bs_sector_device :  sector_array[j].sector_configured_on_device,
					    	filter_data 	 :  {"bs_name" : bs_ss_devices[i].name, "sector_name" : sector_array[j].sector_configured_on, "ss_name" : ss_marker_obj.name, "bs_id" : bs_ss_devices[i].originalId, "sector_id" : sector_array[j].sector_id},
					    	device_name 	 : 	ss_marker_obj.device_name,
					    	ss_ip 	 		 : 	ss_marker_obj.data.substation_device_ip_address,
					    	sector_ip 		 :  sector_array[j].sector_configured_on,
					    	zIndex 			 : 	200,
					    	hasPerf 		 :  0,
					    	optimized 		 : 	false,
					    	isActive 		 : 1,
					    	layerReference: ccpl_map.getLayersByName("Markers")[0]
					    };

					    /*Create SS Marker*/
					    var ss_marker = global_this.createOpenLayerVectorMarker(size, ss_marker_object.icon, ss_marker_object.ptLon, ss_marker_object.ptLat, ss_marker_object);
					    bs_ss_markers.push(ss_marker);
					    // ccpl_map.getLayersByName("Markers")[0].addFeatures([ss_marker]);

						markersMasterObj['SS'][String(ss_marker_obj.data.lat)+ ss_marker_obj.data.lon]= ss_marker;
				    	markersMasterObj['SSNamae'][String(ss_marker_obj.device_name)]= ss_marker;

				    	allMarkersObject_wmap['sub_station']['ss_'+ss_marker_obj.name] = ss_marker;

				    	allMarkersArray_wmap.push(ss_marker);

					    /*Push SS marker to pollableDevices array*/
						pollableDevices.push(ss_marker)

					    /*Push All SS Lat & Lon*/
			    	    ssLatArray.push(ss_marker_obj.data.lat);
						ssLonArray.push(ss_marker_obj.data.lon);

						var ss_info = {
								"info" : ss_marker_obj.data.param.sub_station,
								"antenna_height" : ss_marker_obj.data.antenna_height
							},
							base_info = {
								"info" : bs_ss_devices[i].data.param.base_station,
								"antenna_height" : bs_ss_devices[i].data.antenna_height
							};

						startEndObj["nearEndLat"] = bs_ss_devices[i].data.lat;
						startEndObj["nearEndLon"] = bs_ss_devices[i].data.lon;

					    startEndObj["endLat"] = ss_marker_obj.data.lat;
			    		startEndObj["endLon"] = ss_marker_obj.data.lon;

			    		/*Sub station info Object*/
			    		// ss_info["info"] = ss_marker_obj.data.param.sub_station;
			    		// ss_info["antenna_height"] = ss_marker_obj.data.antenna_height;

			    		/*Link color object*/
			    		linkColor = ss_marker_obj.data.link_color;
			    			
		    			// base_info["info"] = bs_ss_devices[i].data.param.base_station;
		    			// base_info["antenna_height"] = bs_ss_devices[i].data.antenna_height;
		    			// if(zoom_level > 9) {
			    			if(ss_marker_obj.data.show_link == 1) {
			    				/*Create the link between BS & SS or Sector & SS*/
						    	var ss_link_line = global_this.plotLines_wmap(startEndObj,linkColor,base_info,ss_info,sect_height,sector_array[j].sector_configured_on,ss_marker_obj.name,bs_ss_devices[i].name,bs_ss_devices[i].id,sector_array[j].sector_id);

						    	ccpl_map.getLayersByName("Lines")[0].addFeatures([ss_link_line]);

						    	ssLinkArray.push(ss_link_line);
						    	ssLinkArray_filtered = ssLinkArray;

						    	allMarkersObject_wmap['path']['line_'+ss_marker_obj.name] = ss_link_line;

						    	markersMasterObj['Lines'][String(startEndObj.startLat)+ startEndObj.startLon+ startEndObj.endLat+ startEndObj.endLon]= ss_link_line;
								markersMasterObj['LinesName'][String(bs_ss_devices[i].name)+ ss_marker_obj.name]= ss_link_line;

						    	allMarkersArray_wmap.push(ss_link_line);
			    			}
		    			// }
					}
				}

				/*Add the master marker to the global master markers array*/
		    	masterMarkersObj.push(bs_marker);

		    	allMarkersObject_wmap['base_station']['bs_'+bs_ss_devices[i].name] = bs_marker;

		    	allMarkersArray_wmap.push(bs_marker);

		    	//Add markers to markersMasterObj with LatLong at key so it can be fetched later.
				markersMasterObj['BS'][String(bs_ss_devices[i].data.lat)+bs_ss_devices[i].data.lon]= bs_marker;
				markersMasterObj['BSNamae'][String(bs_ss_devices[i].name)]= bs_marker;

			    /*Push All BS Lat & Lon*/
				bsLatArray.push(bs_ss_devices[i].data.lat);
				bsLonArray.push(bs_ss_devices[i].data.lon);
			}

			if(isCallCompleted == 1) {

				/*Hide The loading Icon*/
				$("#loadingIcon").hide();

				/*Enable the refresh button*/
				$("#resetFilters").button("complete");
				
				if(isFirstTime == 1) {
					/*Load data for basic filters*/
					gmap_self.getBasicFilters();
				}

				global_this.updateMarkersSize('medium');
			}

			if(bs_ss_markers.length> 0) {
				ccpl_map.getLayersByName("Markers")[0].addFeatures(bs_ss_markers);
			}

			if(isDebug) {
				console.log("Plot Devices End Time :- "+ new Date().toLocaleString());
				console.log("**********************************");
			}
		}

		/*
		 * This function start Ajax Request to get the Data.
		 * @param i {Number} Current Counter of Ajax Request
		 * In Success, we get how many times we need to call Ajax Request and according to that, we recurvsily call this function.
		 * Also call Functions to create Marker with the data.
		 */		
		function startAjaxRequest(i) {
			//Ajax Request
			$.ajax({
				//Url for the request
				url : base_url+'/'+'device/stats/?total_count='+total_count+'&page_number='+i,
				//request type
				type: 'GET',
				//json 
				dataType: 'json',
				//Success callback
				success: function(response) {

					if(response.success == 1) {

						var result = response;
						//First Time, find how many times Ajax Request is to be sent.
						if (i === 1) {
							total_count = response.data.meta.total_count;
							device_count = response.data.meta.device_count;
							limit = response.data.meta.limit;

							loop_count = Math.ceil(total_count / limit);
						}

						if(result.data.objects) {
							main_devices_data_wmap = main_devices_data_wmap.concat(result.data.objects.children);

							data_for_filter_wmap = main_devices_data_wmap;

							global_this.showStateWiseData_wmap(result.data.objects.children);
						}

						//Condition to check if we need to call Ajax Request again
						if (i <= loop_count && response.success) {

							//if all calls are completed
							if (i === loop_count) {

								isCallCompleted = 1;
								//hide Loading
								global_this.hideLoading();

								gmap_self.getBasicFilters();

								return;
							}
								

							//send next request after 40 ms.
							setTimeout(function() {
								i++;
								//send next request
								startAjaxRequest(i);
							}, 40);

							return ;
						}
					}
				},
				//on error, show error message
				error: function(response) {
					$.gritter.add({
						// (string | mandatory) the heading of the notification
						title: 'GIS - Server Error',
						// (string | mandatory) the text inside the notification
						text: response.statusText,
						// (bool | optional) if you want it to fade out on its own or just sit there
						sticky: false
					});

					isCallCompleted = 1;
					//hide Loading
					global_this.hideLoading();
				},
				always : function() {
					global_this.hideLoading();

					/*Load tools(point,line) data*/
					// gmap_self.get_tools_data_gmap();

					setTimeout(function() {
						var current_zoom_level = ccpl_map.getZoom();
    					if(current_zoom_level > 7) {
							var bs_list = getMarkerInCurrentBound();
			            	if(bs_list.length > 0 && isCallCompleted == 1) {            		
			            		if(recallPerf != "") {
			            			clearTimeout(recallPerf);
			            			recallPerf = "";
			            		}
			            		// gisPerformanceClass.start(bs_list);
			            	}
		            	}
						gisPerformanceClass.start(getMarkerInCurrentBound());
					}, 30000);

					/*Recall the server after particular timeout if system is not freezed*/
					setTimeout(function(e){
						// gmap_self.recallServer_wmap();
					},21600000);
				}
			});
		}

		 /**
     * This function resets the global variables & again call the api calling function after given timeout i.e. 5 minutes
     * @method recallServer_wmap
     */
    this.recallServer_wmap = function() {

    	if(isFreeze == 0) {

			/*Hide The loading Icon*/
			$("#loadingIcon").show();

			/*Enable the refresh button*/
			$("#resetFilters").button("loading");

			/*Reset markers & polyline*/
			gmap_self.clearGmapElements();

			/*Reset Global Variables & Filters*/
			gmap_self.resetVariables_gmap();
			
			/*Recall the API*/
			gmap_self.getDevicesData_gmap();

		}
    };

	/**
	 *
	 * End of Plotting Section
	 */


	/*
	 *
	 * Utils Section
	 */
		
		/*
		This function removes all Features from marker, line and sector layers.
		 */
		this.hideAllFeatures = function() {
			ccpl_map.getLayersByName('Markers')[0].removeAllFeatures();
			ccpl_map.getLayersByName("Lines")[0].removeAllFeatures();
			ccpl_map.getLayersByName("Sectors")[0].removeAllFeatures();
		}

		/*
		This function shows all Filtered Features for marker, line and sector layers.
		 */
		this.showAllFeatures = function() {
			bsDevicesObj = tempbsDeviceObj;
			ccpl_map.getLayersByName('Markers')[0].addFeatures(bs_ss_features_list);
			ccpl_map.getLayersByName("Lines")[0].addFeatures(main_lines_sectors_features_wmaps.lines);
			ccpl_map.getLayersByName("Sectors")[0].addFeatures(main_lines_sectors_features_wmaps.sectors);
			ccpl_map.getLayersByName('Markers')[0].strategies[0].recluster();
		}

		/*
		 * Update page status in the div
		 */
		function get_page_status() {
			var status_txt = "";

			if(hasAdvSearch == 0) {
				//remove html element from page status
				if($("#gis_search_status_txt").length) {
					$("#gis_search_status_txt").remove();
				}
			}

			//if filter is applied
			if(hasAdvFilter == 1) {
				status_txt+= '<li>Advance Filters Applied</li>';
			}

			//if nothing is applied
			if(status_txt == "") {
				status_txt += "<li>Default</li>";    
			}

			//update html
			$("#gis_status_txt").html(status_txt);
		}
		/*
		 * This function show Loading on the White Map Gui
		*/
		this.showLoading= function() {

				//Disable Advance buttons Loading
				disableAdvanceButton();

				//Show loading
				$("#loadingIcon").show();

				//Set reset Filter button text
				$("#resetFilters").button("loading");
		}

		/*
		 * This function hides Loading on the White Map Gui
		*/
		this.hideLoading= function() {

				//Enable Advance buttons Loading
				disableAdvanceButton('no');

				//hide loading
				$("#loadingIcon").hide();

				//Set reset Filter button text
				$("#resetFilters").button("complete");
		}
	/*
	 *
	 * End of Utils Section
	 */
	
	/**
	 * Constructor for White Map Class.
	 * Starts building of White Maps
	 * @return {undefined} 
	 */
	this.init = function() {
		
		//Set this
		global_this = this;

		//Show loading on the map
		global_this.showLoading();		

		/*style for state wise counter label*/
		counter_div_style = "margin-left:-30px;margin-top:-30px;cursor:pointer;background:url("+base_url+"/static/js/OpenLayers/img/state_cluster.png) top center no-repeat;text-align:center;width:65px;height:65px;";

		/*Initialize Loki db for bs,ss,sector,line,polygon*/
		// Create the database:
		var db = new loki('loki.json');

		// Create a collection:
		bs_loki_db = db.addCollection('base_station')
		ss_loki_db = db.addCollection('sub_station')
		sector_loki_db = db.addCollection('sector_device')
		polygon_loki_db = db.addCollection('sector_polygon')
		line_loki_db = db.addCollection('path')
		all_devices_loki_db = db.addCollection('allDevices');

		state_lat_lon_db = db.addCollection('state_lat_lon');

		state_lat_lon_db.insert({"name" : "Andhra Pradesh","lat" : 16.50,"lon" : 80.64});
		state_lat_lon_db.insert({"name" : "Arunachal Pradesh","lat" : 27.06,"lon" : 93.37});
		state_lat_lon_db.insert({"name" : "Assam","lat" : 26.14,"lon" : 91.77});
		state_lat_lon_db.insert({"name" : "Bihar","lat" : 25.37,"lon" : 85.13});
		state_lat_lon_db.insert({"name" : "Chhattisgarh","lat" : 21.27,"lon" : 81.60});
		state_lat_lon_db.insert({"name" : "Delhi","lat" : 28.61,"lon" : 77.23});
		state_lat_lon_db.insert({"name" : "Goa","lat" : 15.4989,"lon" : 73.8278});
		state_lat_lon_db.insert({"name" : "Gujrat","lat" : 23.2167,"lon" : 72.6833});
		state_lat_lon_db.insert({"name" : "Haryana","lat" : 30.73,"lon" : 76.78});
		state_lat_lon_db.insert({"name" : "Himachal Pradesh","lat" : 31.1033,"lon" : 77.1722});
		state_lat_lon_db.insert({"name" : "Jammu and Kashmir","lat" : 33.45,"lon" : 76.24});
		state_lat_lon_db.insert({"name" : "Jharkhand","lat" : 23.3500,"lon" : 85.3300});
		state_lat_lon_db.insert({"name" : "Karnataka","lat" : 12.9702,"lon" : 77.5603});
		state_lat_lon_db.insert({"name" : "Kerala","lat" : 8.5074,"lon" : 76.9730});
		state_lat_lon_db.insert({"name" : "Madhya Pradesh","lat" : 23.2500,"lon" : 77.4170});
		state_lat_lon_db.insert({"name" : "Maharashtra","lat" : 18.9600,"lon" : 72.8200});
		state_lat_lon_db.insert({"name" : "Manipur","lat" : 24.8170,"lon" : 93.9500});
		state_lat_lon_db.insert({"name" : "Meghalaya","lat" : 25.5700,"lon" : 91.8800});
		state_lat_lon_db.insert({"name" : "Mizoram","lat" : 23.3600,"lon" : 92.0000});
		state_lat_lon_db.insert({"name" : "Nagaland","lat" : 25.6700,"lon" : 94.1200});
		state_lat_lon_db.insert({"name" : "Orissa","lat" : 20.1500,"lon" : 85.5000});
		state_lat_lon_db.insert({"name" : "Punjab","lat" : 30.7900,"lon" : 76.7800});
		state_lat_lon_db.insert({"name" : "Rajasthan","lat" : 26.5727,"lon" : 73.8390});
		state_lat_lon_db.insert({"name" : "Sikkim","lat" : 27.3300,"lon" : 88.6200});
		state_lat_lon_db.insert({"name" : "Tamil Nadu","lat" : 13.0900,"lon" : 80.2700});
		state_lat_lon_db.insert({"name" : "Tripura","lat" : 23.8400,"lon" : 91.2800});
		state_lat_lon_db.insert({"name" : "Uttarakhand","lat" : 30.3300,"lon" : 78.0600});
		state_lat_lon_db.insert({"name" : "Uttar Pradesh","lat" : 26.8500,"lon" : 80.9100});
		state_lat_lon_db.insert({"name" : "West Bengal","lat" : 22.5667,"lon" : 88.3667});
		state_lat_lon_db.insert({"name" : "Andaman and Nicobar Islands","lat" : 11.6800,"lon" : 92.7700});
		state_lat_lon_db.insert({"name" : "Lakshadweep","lat" : 10.5700,"lon" : 72.6300});
		state_lat_lon_db.insert({"name" : "Pondicherry","lat" : 11.9300,"lon" : 79.8300});
		state_lat_lon_db.insert({"name" : "Dadra And Nagar Haveli","lat" : 20.2700,"lon" : 73.0200});
		//Call prototype method createOpenLayerMap() to create White Map and in the callback. Start Ajax Request to get Data.
		this.createOpenLayerMap(function() {			
			//start ajax request
			startAjaxRequest(1);
		});
	}
}