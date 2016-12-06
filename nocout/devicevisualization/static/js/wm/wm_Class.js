var ccpl_map, 
	base_url, 
	global_this = "",
	main_devices_data_wmap= [],
	wm_obj = {'features': {}, 'data': {}, 'devices': {}, 'lines': {}, 'sectors': {}},
	data_for_filter_wmap= [],
	filtered_devices_array= [];

var state_city_obj= {}, 
	all_cities_array= [],
	all_region_array = [],
	tech_vendor_obj= {}, 
	all_vendor_array= [], 
	sectorMarkerConfiguredOn= [], 
	sectorMarkersMasterObj = {},
	lat_lon_search_icon = "/static/img/icons/search_icon.png";

var bs_loki_db = [],
    ss_loki_db = [],
    sector_loki_db = [],
    polygon_loki_db = [],
    line_loki_db = [],
    all_devices_loki_db= [],
    green_status_array = ['ok','success','up'],
    red_status_array = ['critical','down'],
    orange_status_array = ['warning'],
    ptp_tech_list = ['ptp','p2p','ptp bh'],
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
	markersMasterObj= {'BS': {}, 'Lines': {}, 'SS': {}, 'BSNamae': {}, 'SSNamae': {}, 'LinesName': {}, 'Poly': {}, 'backhaul' : {}},
	masterMarkersObj= [],
	ssLatArray = {},
	ssLonArray = {},
	overlapping_ss = {},
	ssLinkArray_filtered = [],
	isFirstTime= 1,
	isExportDataActive= 0,
	pollCallingTimeout = "",
	remainingPollCalls = 0,
	pollingInterval = 10,
	pollingMaxInterval = 1,
	isPollingPaused = 0,
	isPerfCallStopped = 1,
	isPerfCallStarted = 0,
	tooltipInfoLabel = {},
	last_perf_called_items = [];

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
	polled_device_count = {},
	pollableDevices = [],
	polled_devices_names= [];

var bs_ss_markers = [],
	bs_obj= {},
	isCallCompleted,
	gisPerformanceClass = "",
	spiderified_ss = [],
	na_items_list = ['n/a', 'na'];

function WhiteMapClass() {

	/*
	 *
	 * Public Variables
	*/
		this.livePollingPolygonControl = "";
		this.exportDataPolygonControl = "";
	/*
	 *
	 * Private Variables
	*/	
		var total_count = 0,
			device_count = 0,
			limit = 0,
			loop_count = 0;

		/**
		 * Marker Spidifier For BS
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
				if(markerSpiderfied == feature) {
					return true;
				}
				global_this.unSpiderifyBsMarker();

			}

			var bsData = wm_obj.data[feature.bs_name],
				bsSectors = bsDevicesObj[bsData.name];

			// var bsSectorLength = bsData.sectors.length;
			if(bsSectors && bsSectors.length) {
				var currentAngle = 0;
				for(var i=0; i<= bsSectors.length; i++) {
					if(i == bsSectors.length) {
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
						var current_sector = bsData.sectors[i];
						// If sector exists
						if(current_sector) {
							var sectorMarker = current_sector.ip_address ? allMarkersObject_wmap['sector_device']['sector_'+current_sector.ip_address] : "",
								xyDirection = "";
							// If sector marker then proceed
							if(sectorMarker) {
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
								var finalLatLong = new OpenLayers.LonLat(xyDirection.lon, xyDirection.lat),
									start_point = new OpenLayers.Geometry.Point(feature.ptLon,feature.ptLat),
									end_point = new OpenLayers.Geometry.Point(xyDirection.lon,xyDirection.lat);

								ccpl_map.getLayersByName("Devices")[0].addFeatures(
									[new OpenLayers.Feature.Vector(new OpenLayers.Geometry.LineString([start_point, end_point]))]
								);
								ccpl_map.getLayersByName("Devices")[0].addFeatures([sectorMarker]);
								sectorMarker["new_lat"] = xyDirection.lat;
								sectorMarker["new_lon"] = xyDirection.lon;
								sectorMarker.move(finalLatLong);
								sectorMarker.style.externalGraphic = sectorMarker.pollingIcon ? sectorMarker.pollingIcon : sectorMarker.oldIcon;
							}
						}
					}
					currentAngle = currentAngle+(360/(bsSectors.length+1));
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
	 * This function unspiderify features present in global array
	 * @method unSpiderifyWmapMarker
	 */
	this.unSpiderifyWmapMarker = function() {
		if(spiderified_ss.length) {
			for(var x=0;x<spiderified_ss.length;x++) {
				var feature = spiderified_ss[x],
					feature_position_obj = new OpenLayers.LonLat(feature.ptLon, feature.ptLat);

				feature['isMarkerSpiderfied'] = false;

				feature.move(feature_position_obj);
			}

			ccpl_map.getLayersByName("Spider_SS_Lines")[0].removeAllFeatures();

			spiderified_ss = [];
		}		
	};

	/**
	 * This function spiderify features as per given features id list
	 * @method spiderifyWmapMarker
	 * @param features_id_list {Array}, It contains the id's of features which are to be spiderify
	 */
	this.spiderifyWmapMarker = function(features_id_list) {

		if(spiderified_ss.length) {
			global_this.unSpiderifyWmapMarker();
		}

		var isSpiderfied = false,
			currentAngle = 0,
			distance = 1;

		// Set distance between the markers as per zoom levels
		if(ccpl_map.getZoom() > 12) {
			if(ccpl_map.getZoom() > 13) {
				distance = 0.08;
			} else {
				distance = 0.3;
			}
		}

		for(var i=0;i<features_id_list.length;i++) {
			var current_features = allMarkersObject_wmap['sub_station'][features_id_list[i]];
			if(current_features && current_features['isMarkerSpiderfied']) {
				break;
			} else {
				isSpiderfied = true;

				current_features['isMarkerSpiderfied'] = true;

				var new_lat_lon = "";

				var start_point = new OpenLayers.Geometry.Point(current_features.ptLon,current_features.ptLat),
					end_point = "";

				if(current_features['new_lat'] && current_features['new_lon']) {
					new_lat_lon = new OpenLayers.LonLat(current_features['new_lon'], current_features['new_lat']);
					end_point = new OpenLayers.Geometry.Point(current_features['new_lon'],current_features['new_lat'])
				} else {
					// Get new position lat lon dict
					var xyDirection = getAtXYDirection(currentAngle, distance, current_features.ptLon, current_features.ptLat);

					new_lat_lon = new OpenLayers.LonLat(xyDirection.lon, xyDirection.lat);
					end_point = new OpenLayers.Geometry.Point(xyDirection.lon,xyDirection.lat)

					// Update the new location lat,lon to feature object
					current_features['new_lat'] = xyDirection.lat;
					current_features['new_lon'] = xyDirection.lon;

					// Update the angle between the markers as per total markers count
					currentAngle = currentAngle+(360/(features_id_list.length+1));
				}

				if(new_lat_lon) {
					// Move feature to new location
					current_features.move(new_lat_lon);

					spiderified_ss.push(current_features);

					// Create Line between the new location n original location of feature
					ccpl_map.getLayersByName("Spider_SS_Lines")[0].addFeatures(
						[new OpenLayers.Feature.Vector(new OpenLayers.Geometry.LineString([start_point, end_point]))]
					);
				}

			}
		}
		return isSpiderfied;
	};

	/**
	 * 
	 * Polling Section
	 */
	
		this.initLivePolling = function() {
			if(isDebug) {
				console.log("White Map - initLivePolling");
				var start_date_initLivePolling = new Date();
			}
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
			if(isDebug) {
            	var time_diff = (new Date().getTime() - start_date_initLivePolling.getTime())/1000;
				// console.log("Google Map Idle Event End Time :- "+ new Date().toLocaleString());
				console.log("White Map - initLivePolling End Time :- "+ time_diff + "Seconds");
				console.log("*************************************");
				start_date_initLivePolling = "";
			}
		}

		 /**
	     * This function initialize live polling
	     * @method fetchPollingTemplate_gmap
	     */
		this.fetchPollingTemplate_wmap = function() {

			var selected_technology = $.trim($("#polling_tech").val()),
    			selected_type = $.trim($("#polling_type").val()),
				pathArray = [],
				polygon = "",
				service_type = $("#isPing")[0].checked ? "ping" : "other";


			/*Re-Initialize the polling*/
			whiteMapClass.initLivePolling();
			
			/*Reset the variables*/
			polygonSelectedDevices = [];
			pointsArray = [];

			if(selected_technology && selected_type) {			
				$("#tech_send").button("loading");
				/*ajax call for services & datasource*/
				$.ajax({
					url : base_url+"/"+"device/ts_templates/?technology="+selected_technology+"&device_type="+selected_type+"&service_type="+service_type,
					success: function (response) {

		                var result = "";
		                // Type check of response
		                if(typeof response == 'string') {
		                    result = JSON.parse(response);
		                } else {
		                    result = response;
		                }

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
				alert("Please select technology & type.");
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

			if(isPerfCallStopped == 0 && isPerfCallStarted == 0) {
				/*Restart performance calling*/
		    	gisPerformanceClass.restart();
	    	}
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

			var selected_polling_technology = $("#polling_tech option:selected").text(),
				polling_technology_condition = $.trim(selected_polling_technology.toLowerCase()),
				selected_polling_type = $("#polling_type option:selected").text(),
				polling_type_condition = $.trim(selected_polling_type.toLowerCase());

			for(var k=0;k<allSS.length;k++) {
				
				if(allSS[k].ptLon && allSS[k].ptLat && polygon) {
					if (displayBounds(polygon, allSS[k].ptLon, allSS[k].ptLat) == 'in') {
						var point_tech = allSS[k].technology ? $.trim(allSS[k].technology.toLowerCase()) : "";
						var point_type = allSS[k].device_type ? $.trim(allSS[k].device_type.toLowerCase()) : "";

						// if point technology is PTP BH then use it as PTP
						if(ptp_tech_list.indexOf(point_tech) > -1) {
							point_tech = 'ptp';
						}

						// PTP, P2P & PTP BH are same
						if(ptp_tech_list.indexOf(polling_technology_condition) > -1) {
							polling_technology_condition = 'ptp';
						}

						if(point_tech) {
							if(point_tech == polling_technology_condition && point_type == polling_type_condition) {
								if(ptp_tech_list.indexOf(point_tech)  > -1) {
									if(allSSIds.indexOf(allSS[k].device_name) < 0) {
										if(allSS[k].pointType == 'sub_station') {
											if(allSSIds.indexOf(allSS[k].bs_sector_device) < 0) {
												allSSIds.push(allSS[k].bs_sector_device);
												polygonSelectedDevices.push(allMarkersObject_wmap['sector_device']['sector_'+allSS[k].sector_ip]);
											}
										}
										allSSIds.push(allSS[k].device_name);
										polygonSelectedDevices.push(allSS[k]);
									}
								} else {
									if(allSS[k].pointType == 'sub_station') {
										if(allSSIds.indexOf(allSS[k].device_name) < 0) {
											allSSIds.push(allSS[k].device_name);
											polygonSelectedDevices.push(allSS[k]);
										}
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

				/*Reset polling technology and polling Type select box*/
				$("#polling_tech").val($("#polling_tech option:first").val());
				$("#polling_type").val($("#polling_type option:first").val());

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
				$("#polling_type").val($("#polling_type option:first").val());

				bootbox.alert("Max. limit for selecting devices is 200.");

			} else {
								
				var devicesTemplate = gmap_self.createLivePollingHtml(polygonSelectedDevices);
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
					var timeout_val = Number(pollingInterval) * 1000;
					// Call function to fetch polled data for selected devices
					gmap_self.getPollingData_gmap(function(response) {
						pollCallingTimeout = setTimeout(function() {
							remainingPollCalls--;
							whiteMapClass.startDevicePolling_wmap();
						},timeout_val);
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
				var ip_str = complete_polled_devices_data[i].ip ? complete_polled_devices_data[i].ip : "",
					name = complete_polled_devices_data[i].device_name ? complete_polled_devices_data[i].device_name : "N/A",
					display_name = ip_str ? ip_str : name;

				table_html += '<tr>';
				table_html += '<td>'+display_name+'</td>';
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
					if(polygonSelectedDevices[x].device_name == polled_devices_names[i]) {
						marker_name = polygonSelectedDevices[x].name;
						if(polygonSelectedDevices[x].pointType == 'sub_station') {
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
					if(polygonSelectedDevices[x].device_name == polled_devices_names[i]) {
						marker_name = polygonSelectedDevices[x].name;
						if(polygonSelectedDevices[x].pointType == 'sub_station') {
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
	 * This function export selected BS inventory by calling respective API
	 * @method exportData_wmap
	 */
	this.exportData_wmap = function() {
		exportDataPolygon = {};

		ccpl_map.getLayersByName('export_Polling')[0].setVisibility(true);
		global_this.exportDataPolygonControl.activate();

	};

	/**
	 * This function trigger when export data polygon created.
	 * @method exportDataPolygonAdded
	 */
	this.exportDataPolygonAdded = function(e) {
		global_this.exportDataPolygonControl.deactivate();
		polygon = e.feature;
		global_this.getStatesInPolygon();
		currentPolygon = e.feature;
	};

	this.getStatesInPolygon = function() {
		
		var bs_id_array = [],
			bs_obj_array = [],
			states_array = [];

		// If state clusers showing
		if(ccpl_map.getZoom() < 4) {

			var technology_filter = $("#filter_technology").select2('val').length > 0 ? $("#filter_technology").select2('val').join(',').toLowerCase().split(',') : [],
				vendor_filter = $("#filter_vendor").select2('val').length > 0 ? $("#filter_vendor").select2('val').join(',').toLowerCase().split(',') : [],
				city_filter = $("#filter_city").select2('val').length > 0 ? $("#filter_city").select2('val').join(',').toLowerCase().split(',') : [],
				state_filter = $("#filter_state").select2('val').length > 0 ? $("#filter_state").select2('val').join(',').toLowerCase().split(',') : [],
				frequency_filter = $("#filter_frequency").select2('val').length > 0 ? $("#filter_frequency").select2('val').join(',').toLowerCase().split(',') : [],
				polarization_filter = $("#filter_polarization").select2('val').length > 0 ? $("#filter_polarization").select2('val').join(',').toLowerCase().split(',') : [],
				filterObj = {
					"technology" : $.trim($("#technology option:selected").text()),
					"vendor" : $.trim($("#vendor option:selected").text()),
					"state" : $.trim($("#state option:selected").text()),
					"city" : $.trim($("#city option:selected").text())
				},
				isAdvanceFilterApplied = technology_filter.length > 0 || vendor_filter.length > 0 || state_filter.length > 0 || city_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0,
				isBasicFilterApplied = filterObj['technology'] != 'Select Technology' || filterObj['vendor'] != 'Select Vendor' || filterObj['state'] != 'Select State' || filterObj['city'] != 'Select City';

			var states_within_polygon = state_lat_lon_db.where(function(obj) {
				return displayBounds(polygon, obj.lon, obj.lat) == 'in';
				// return google.maps.geometry.poly.containsLocation(new google.maps.LatLng(obj.lat,obj.lon),polygon);
			});

			for(var i=0;i<states_within_polygon.length;i++) {
				if(state_wise_device_labels[states_within_polygon[i].name]) {
					states_array.push(states_within_polygon[i].name);
				}
			}


			if(states_within_polygon.length > 0) {
				
				var current_bound_devices = all_devices_loki_db.where(function( obj ) {
	    			if(!isAdvanceFilterApplied && !isBasicFilterApplied) {
	    				if(states_array.indexOf(obj.state) > -1) {
	        				bs_id_array.push(obj.bs_id);
	        				return true;
	    				} else {
	    					return false;
	    				}
	    			} else if(isAdvanceFilterApplied) {
	    				var technology_count = technology_filter.length >  0 ? $.grep(obj.sector_ss_technology.split("|"), function (elem) {
					        	return technology_filter.indexOf(elem) > -1;
					        }).length : 1,
			            	filter_condition1 = technology_count > 0 ? true : false,
			            	vendor_count = vendor_filter.length >  0 ? $.grep(obj.sector_ss_vendor.split("|"), function (elem) {
					        	return vendor_filter.indexOf(elem) > -1;
					        }).length : 1,
			                filter_condition2 = vendor_count > 0 ? true : false,
			                filter_condition3 = state_filter.length > 0 ? state_filter.indexOf(obj.state) > -1 : true,
			                filter_condition4 = city_filter.length > 0 ? city_filter.indexOf(obj.city) > -1 : true;
				            
				            // Condition to check for applied advance filters
				            if(filter_condition1 && filter_condition2 && filter_condition3 && filter_condition4) {
				            	if(states_array.indexOf(obj.state) > -1) {
		            				bs_id_array.push(obj.bs_id);
		            				return true;
	            				} else {
	            					return false;
	            				}
				            } else {
				                return false;
				            }
	    			} else if(isBasicFilterApplied) {

	    				var sectors = obj.sectors,
							basic_filter_condition1 = filterObj['state'] != 'Select State' ? obj.state == filterObj['state'] : true,
							basic_filter_condition2 = filterObj['city'] != 'Select City' ? obj.city == filterObj['city'] : true;;
						for(var i=sectors.length;i--;) {
							var basic_filter_condition3 = filterObj['technology'] != 'Select Technology' ? $.trim(sectors[i]['technology'].toLowerCase()) == $.trim(filterObj['technology'].toLowerCase()) : true,
								basic_filter_condition4 = filterObj['vendor'] != 'Select Vendor' ? $.trim(sectors[i]['vendor'].toLowerCase()) == $.trim(filterObj['vendor'].toLowerCase()) : true

							if(basic_filter_condition1 && basic_filter_condition2 && basic_filter_condition3 && basic_filter_condition4) {
								if(states_array.indexOf(obj.state) > -1) {
		            				bs_id_array.push(obj.id);
		            				return true;
	            				} else {
	            					return false;
	            				}
							} else {
								return false;
							}
						}
					}
	    		});
				
				// Remove unmatched sectors
				for(var x=0;x<current_bound_devices.length;x++) {
					var sectors = current_bound_devices[x].sectors,
						delete_index = [];
					for(var y=0;y<sectors.length;y++) {
						var sector_technology = $.trim(sectors[y].technology.toLowerCase()),
							sector_vendor = $.trim(sectors[y].vendor.toLowerCase());
						if(technology_filter.length > 0 || vendor_filter.length > 0) {
							var advance_filter_condition1 = technology_filter.length ? technology_filter.indexOf(sector_technology) > -1 : true,
								advance_filter_condition1 = vendor_filter.length ? vendor_filter.indexOf(sector_vendor) > -1 : true;
								
							if(!advance_filter_condition1 || !advance_filter_condition2) {
								delete_index.push(y);
							}

						} else {

							if(filterObj['technology'] != 'Select Technology' || filterObj['vendor'] != 'Select Vendor') {
								var basic_filter_technology = filterObj['technology'] != 'Select Technology' ? filterObj['technology'] : false,
									basic_filter_vendor = filterObj['vendor'] != 'Select Vendor' ? filterObj['vendor'] : false,
									basic_filter_condition1 = basic_filter_technology ? basic_filter_technology == sector_technology : true,
									basic_filter_condition2 = basic_filter_vendor ? basic_filter_vendor == sector_vendor : true;
									
								if(!basic_filter_condition1 || !basic_filter_condition2) {
									delete_index.push(y);
								}
							}
						}
					}
					// Delete Unmatched Values
					for(var z=0;z<delete_index.length;z++) {
						current_bound_devices[x].sectors.splice(delete_index[z],1);
					}
				}

				// If any bs exists
				if(bs_id_array.length > 0) {

					inventory_bs_ids = bs_id_array;

					var devicesTemplate = "";
					for(var i=0;i<current_bound_devices.length;i++) {
						var current_bs = current_bound_devices[i];
						devicesTemplate += '<div class="well well-sm" id="bs_'+current_bs.bs_id+'"><h5>'+(i+1)+'.) '+current_bs.alias+'</h5></div>';
					}

					$("#exportData_sideInfo > .panel-body > .bs_list").html(devicesTemplate);

					if($("#exportDeviceContainerBlock").hasClass('hide')) {
						$("#exportDeviceContainerBlock").removeClass('hide');
					}

				} else {
					networkMapInstance.removeInventorySelection();

					bootbox.alert("No BS found in the selected area.");	
				}

			} else {
				networkMapInstance.removeInventorySelection();

				bootbox.alert("No BS found in the selected area.");	
			}
		} else {
			// If marker showing
			var bs_obj = allMarkersObject_wmap['base_station'],
				selected_bs_ids = [],
				selected_bs_markers = [];
			for(key in bs_obj) {
            	if(displayBounds(polygon, bs_obj[key].ptLon, bs_obj[key].ptLat) == 'in') {
            		if(selected_bs_ids.indexOf(bs_obj[key].filter_data.bs_id) == -1) {
            			selected_bs_ids.push(bs_obj[key].filter_data.bs_id);
            			selected_bs_markers.push(bs_obj[key]);
            		} 
            			
            	}
			}
			// If any bs exists
			if(selected_bs_ids.length > 0) {

				inventory_bs_ids = selected_bs_ids;

				var devicesTemplate = "";
				for(var i=0;i<selected_bs_markers.length;i++) {
					var current_bs = selected_bs_markers[i];
					devicesTemplate += '<div class="well well-sm" id="bs_'+current_bs.filter_data.bs_id+'"><h5>'+(i+1)+'.) '+current_bs.bs_alias+'</h5></div>';
				}

				$("#exportData_sideInfo > .panel-body > .bs_list").html(devicesTemplate);

				if($("#exportDeviceContainerBlock").hasClass('hide')) {
					$("#exportDeviceContainerBlock").removeClass('hide');
				}

			} else {

				gmap_self.removeInventorySelection();

				bootbox.alert("No BS found in the selected area.");
			}
		}
	};


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
		};

		/**
		 * This function returns marker width & height object as per given type.
		 * @method getMarkerSize_wmap
		 * @param isBaseStation {boolean}, It states that the marker size is for BS or for any other markers(True in case of BS else False).
		 */
		this.getMarkerSize_wmap = function(isBaseStation) {

			var largeur = 32/1.4,
				hauteur = 37/1.4,
				divideBy = 0.8,
				anchorX = -0.2,
				markerSizeObj = {
					"width"   : 0,
					"height"  : 0,
					"xOffset" : 0,
					"yOffset" : 0
				};

			if(isBaseStation) {
				largeur = 20/1.4;
				hauteur = 40/1.4;
			}

			if(current_icon_size == 'small') {
				divideBy = 1.4;
				anchorX = 0.4;
			} else if(current_icon_size == 'medium') {
				divideBy = 1;
				anchorX = 0;
			} else {
				divideBy = 0.8;
				anchorX = -0.2;
			}

			markerSizeObj["width"] = Math.ceil(largeur/divideBy);
			markerSizeObj["height"] = Math.ceil(hauteur/divideBy);
			markerSizeObj["xOffset"] = Math.ceil(16-(16*anchorX));
			markerSizeObj["yOffset"] = Math.ceil(hauteur/divideBy);

			return markerSizeObj;
		};

		/*
		 * This function toggles all Station Markers size based on the Value selected in the dropdown.
		 * @method updateMarkersSize
		 */
		this.updateMarkersSize = function(iconSize) {
			global_this.unSpiderifyBsMarker();
			var largeur = 32/1.4,
				hauteur = 37/1.4,
				largeur_bs = 20/1.4,
				hauteur_bs = 40/1.4,
				divideBy;

			var anchorX, i, markerImage, markerImage2, icon;

			if(iconSize == 'small') {
				divideBy = 1.4;
				anchorX = 0.4;
			} else if(iconSize== 'medium') {
				divideBy = 1;
				anchorX = 0;
			} else {
				divideBy = 0.8;
				anchorX = -0.2;
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
					ccpl_map.getLayersByName("Devices")[0].drawFeature(marker);
				})(sector_MarkersArray[i]);
			}
			//End of Loop through the sector markers

			ccpl_map.getLayersByName("Devices")[0].redraw();
			ccpl_map.getLayersByName("Devices")[0].removeAllFeatures();


			// Loop through the Master Markers
			for(var i=0; i< bs_ss_markers.length; i++ ) {
				(function updateMasterMarker(marker) {
					var newGraphicHeight = 0, newGraphicWidth = 0, newGraphicXOffset = 0, newGraphicYOffset = 0;
					if(marker.pointType == "base_station") {
						newGraphicHeight = Math.ceil(hauteur_bs/divideBy);
						newGraphicWidth = Math.ceil(largeur_bs/divideBy);
						newGraphicXOffset = Math.ceil(16-(16*anchorX));
						newGraphicYOffset = Math.ceil(hauteur_bs/divideBy);

						marker.style.graphicWidth = newGraphicWidth;
						marker.style.graphicHeight = newGraphicHeight;
						ccpl_map.getLayersByName('Markers')[0].drawFeature(marker);

					} else if (marker.pointType == "sub_station") {
						newGraphicWidth = Math.ceil(largeur/divideBy);
						newGraphicHeight = Math.ceil(hauteur/divideBy);
						newGraphicXOffset = Math.ceil(16-(16*anchorX));
						newGraphicYOffset = Math.ceil(hauteur/divideBy);

						marker.style.graphicWidth = newGraphicWidth;
						marker.style.graphicHeight = newGraphicHeight;
						ccpl_map.getLayersByName('Markers')[0].drawFeature(marker);
					}
				})(bs_ss_markers[i]);
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

			try {
				if(ccpl_map.getLayersByName('SearchMarkers')) {
					ccpl_map.getLayersByName('SearchMarkers')[0].destroy();
					ccpl_map.getLayersByName('SearchMarkers')[0].clearMarkers();
				}
			} catch(e) {
				// pass
			}

			// Update "searchResultData" with map data as per applied filters for plotting.
			searchResultData = JSON.parse(JSON.stringify(networkMapInstance.updateStateCounter_gmaps(true)));

			var lat = +lat_long_string.split(",")[0],
				lng = +lat_long_string.split(",")[1],
				bounds = new OpenLayers.Bounds,
				lonLat = new OpenLayers.LonLat(lng, lat);

			// search_icon.png
			bounds.extend(lonLat);
			ccpl_map.zoomToExtent(bounds);

			if(ccpl_map.getZoom() > 12) {
                ccpl_map.zoomTo(12);
            }

			var markers = new OpenLayers.Layer.Markers("SearchMarkers"),
				search_icon = base_url+""+lat_lon_search_icon,
				size = new OpenLayers.Size(20,40),
				offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
				
			ccpl_map.addLayer(markers);

			var icon = new OpenLayers.Icon(search_icon, size, offset);
			markers.addMarker(new OpenLayers.Marker(lonLat,icon));

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
			var isLineShown = false;
			/*Loop for polylines*/
			for(var key in allMarkersObject_wmap['path']) {
				if(allMarkersObject_wmap['path'].hasOwnProperty(key)) {
			    	var current_line = allMarkersObject_wmap['path'][key];
			    	if(current_line) {
					    var connected_bs = allMarkersObject_wmap['base_station']['bs_'+current_line.filter_data.bs_name],
					      	connected_ss = allMarkersObject_wmap['sub_station']['ss_'+current_line.filter_data.ss_name],
					    	nearEndVisible = global_this.checkIfPointLiesInside({lat: connected_bs["ptLat"], lon: connected_bs["ptLon"]}),
					      	farEndVisible = global_this.checkIfPointLiesInside({lat: connected_ss["ptLat"], lon: connected_ss["ptLon"]});
					    if((nearEndVisible || farEndVisible) && ((connected_bs && connected_ss) && (connected_bs.isActive != 0 && connected_ss.isActive != 0))) {
					    	if(!isLineShown) {
					    		isLineShown = true;
					    	}
					    	// If polyline not shown then show the polyline
				    		showOpenLayerFeature(current_line);
					    }
			    	}
			    }
			}
			if(isLineShown) {
				ccpl_map.getLayersByName('Lines')[0].redraw();
			}
		}

		if(isDebug) {
			console.log("Show in bound lines End Time :- "+ new Date().toLocaleString());
			console.log("**********************************");
		}
	};
	
	/**
	 * This function show base-stations backhaul devices within the bounds
	 * @method showBackhaulDevicesInBounds
	 */
	this.showBackhaulDevicesInBounds = function() {
		if(isDebug) {
			console.log("Show in bound Backhaul Devices");
			console.log("Show in bound Backhaul Devices Start Time :- "+ new Date().toLocaleString());
		}
		/*Loop for polylines*/
		for(var key in allMarkersObject_wmap['backhaul']) {
			if(allMarkersObject_wmap['backhaul'].hasOwnProperty(key)) {
		    	var bh_marker = allMarkersObject_wmap['backhaul'][key],
		      		isMarkerExist = global_this.checkIfPointLiesInside({lat: bh_marker.ptLat, lon: bh_marker.ptLon});
	      		if(isMarkerExist) {
			    	if(bh_marker.isActive && +(bh_marker.isActive) == 1) {
			    		// If Backhaul Marker not shown then show the Backhaul Marker
		    			showOpenLayerFeature(allMarkersObject_wmap['backhaul'][key]);
			    	} else {
			    		// If Backhaul Marker shown then hide the Backhaul Marker
		    			hideOpenLayerFeature(allMarkersObject_wmap['backhaul'][key]);
			        }
	      		}
		  }
		}
		if(isDebug) {
			console.log("Show in bound Backhaul Devices End Time :- "+ new Date().toLocaleString());
			console.log("******************************************");
		}
	};

	/**
	 * This function show sub-stations within the bounds
	 * @method showSubStaionsInBounds
	 */
	this.showSubStaionsInBounds = function() {
		if(isDebug) {
			console.log("Show in bound SS Function");
			var start_date_ss_bounds = new Date();
		}
 		var isSSChecked = $("#showAllSS:checked").length;
		/*Checked case*/
		if(isSSChecked > 0) {
			var ss_keys_array = Object.keys(allMarkersObject_wmap['sub_station']);
			/*Loop for polylines*/
			for(var i=0;i<ss_keys_array.length;i++) {
		    	var key = ss_keys_array[i],
		    		ss_marker = allMarkersObject_wmap['sub_station'][key],
		    		isMarkerExist = global_this.checkIfPointLiesInside({lat: ss_marker.ptLat, lon: ss_marker.ptLon});
	    		if(isMarkerExist) {
	    			if(tooltipInfoLabel[key]) {
	      				tooltipInfoLabel[key].show();
	      			}
		    		if(!ss_marker.getVisibility()) {
		    			showOpenLayerFeature(allMarkersObject_wmap['sub_station'][key]);
		    		}
	    		}
			}
		}

		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_ss_bounds.getTime())/1000;
            console.log("Show in bound SS End Time :- "+ time_diff + "Seconds");
			console.log("***********************************");
			start_date_ss_bounds = "";
		}
	};

	/**
	 * This function show base-stations within the bounds
	 * @method showBaseStaionsInBounds
	 */
	this.showBaseStaionsInBounds = function() {
		if(isDebug) {
			console.log("White Map - Show in bound BS");
			var start_date_bs_bounds = new Date();
		}

		/*Loop for polylines*/
		for(var key in allMarkersObject_wmap['base_station']) {
			if(allMarkersObject_wmap['base_station'].hasOwnProperty(key)) {
		    	var bs_marker = allMarkersObject_wmap['base_station'][key],
		      		isMarkerExist = "";
		      	isMarkerExist = global_this.checkIfPointLiesInside({lat: bs_marker.ptLat, lon: bs_marker.ptLon});
	      		if(isMarkerExist) {
	      			if(tooltipInfoLabel[key]) {
	      				tooltipInfoLabel[key].show();
	      			}
			    	if(!bs_marker.getVisibility()) {
			    		// If BS Marker not shown then show the BS Marker
		      			showOpenLayerFeature(allMarkersObject_wmap['base_station'][key]);
			        }
	      		}
		    }
		}

		// var sector_to_plot = all_devices_loki_db.where(function(obj){return plotted_bs_ids.indexOf(obj.bs_id) > -1;});
		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_bs_bounds.getTime())/1000;
			console.log("White Map - Show in bound BS End Time :- "+ time_diff + "Seconds");
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
		var areMarkerShown = false;
		/*Loop for polylines*/
		for(var key in allMarkersObject_wmap['sector_device']) {
			if(allMarkersObject_wmap['sector_device'].hasOwnProperty(key)) {
		    	var sector_marker = allMarkersObject_wmap['sector_device'][key],
		      		isMarkerExist = "";
		      	isMarkerExist = global_this.checkIfPointLiesInside({lat: sector_marker.ptLat, lon: sector_marker.ptLon});
	      		if(isMarkerExist) {
	      			var sector_layer = sector_marker.layer ? sector_marker.layer : sector_marker.layerReference;
			    	if(!sector_marker.getVisibility()) {
			    		if(!areMarkerShown) {
			    			areMarkerShown = true;
			    		}
			    		// If Sector Marker not shown then show the Sector Marker
		      			showOpenLayerFeature(allMarkersObject_wmap['sector_device'][key]);
			    	}
	      		}
	      	}
		}

		if(areMarkerShown) {
			ccpl_map.getLayersByName("Devices")[0].redraw();
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
		var areMarkerShown = false;
		/*Loop for polylines*/
		for(var key in allMarkersObject_wmap['sector_polygon']) {
			if(allMarkersObject_wmap['sector_polygon'].hasOwnProperty(key)) {
		    	var sector_polygon = allMarkersObject_wmap['sector_polygon'][key],
		    		isMarkerExist = "";
		    	isMarkerExist = global_this.checkIfPointLiesInside({lat: sector_polygon.ptLat, lon: sector_polygon.ptLon});
	    		if(isMarkerExist) {
	    			var sector_polygon_layer = sector_polygon.layer ? sector_polygon.layer : sector_polygon.layerReference;
			    	if(!sector_polygon.getVisibility()) {
			    		if(!areMarkerShown) {
			    			areMarkerShown = true;
			    		}
			    		// If Polygon not shown then show the polygon
		      			showOpenLayerFeature(allMarkersObject_wmap['sector_polygon'][key]);
			    	}
	    		}
		    }
		}

		if(areMarkerShown) {
			ccpl_map.getLayersByName("Sectors")[0].redraw();
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
				hideOpenLayerFeature(allMarkersObject_wmap['path'][key]);
				// Hide the red cross if exists
				if(cross_label_array[key] && cross_label_array[key].getVisibility()) {
					hideOpenLayerFeature(cross_label_array[key]);
				}
			}

		} else {
			for(key in allMarkersObject_wmap['path']) {
				showOpenLayerFeature(allMarkersObject_wmap['path'][key]);
				// Show the red cross if exists
				if(cross_label_array[key] && !cross_label_array[key].getVisibility()) {
					showOpenLayerFeature(cross_label_array[key]);
				}
			}
		}

		// Redraw Lines layer to apply updates(Hide Lines)
		ccpl_map.getLayersByName('Lines')[0].redraw();

		// Redraw Red Cross layer to apply updates(Hide Lines)
		ccpl_map.getLayersByName("RedCross")[0].redraw();

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

		var isSSChecked = $("#showAllSS:checked").length,
			layer_name = '';
		/*Unchecked case*/
		if(isSSChecked == 0) {
			for(key in allMarkersObject_wmap['sub_station']) {
				var current_ss = allMarkersObject_wmap['sub_station'][key];
				hideOpenLayerFeature(current_ss);
				if(!layer_name) {
					layer_name = current_ss.layerReference ? current_ss.layerReference : current_ss.layer;
				}
			}

		} else {
			for(key in allMarkersObject_wmap['sub_station']) {
				var current_ss = allMarkersObject_wmap['sub_station'][key];
				showOpenLayerFeature(current_ss);
				if(!layer_name) {
					layer_name = current_ss.layerReference ? current_ss.layerReference : current_ss.layer;
				}
			}
		}
		
		// Redraw The layer
		if(layer_name) {
			layer_name.redraw()
		} else {
			// Redraw Lines layer to apply updates(Hide Lines)
			ccpl_map.getLayersByName('Markers')[0].redraw();
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
				var current_bs = dataset[i],
					state = current_bs['state'] && na_items_list.indexOf(current_bs['state'].toLowerCase()) == -1 ? $.trim(current_bs['state']) : '',
					city = current_bs['city'] && na_items_list.indexOf(current_bs['city'].toLowerCase()) == -1  ? $.trim(current_bs['city']) : '';
					region = current_bs['region'] && na_items_list.indexOf(current_bs['region'].toLowerCase()) == -1  ? $.trim(current_bs['region']) : '';
				/*Create BS state,city object*/
				if(state) {

					state_city_obj[state] = state_city_obj[state] ? state_city_obj[state] : [];
					if(state_city_obj[state].indexOf(city) == -1) {
						state_city_obj[state].push(city);
					}
				}

				if(city) {
					if(all_cities_array.indexOf(city) == -1) {
						all_cities_array.push(city); 
					}
				}

				if(region) {
	                if(all_region_array.indexOf(region) == -1){
	                    all_region_array.push(region)
	                }
	            }
				
				var sectors_data = current_bs.sectors ? current_bs.sectors : [],
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
					var lat = current_bs.lat,
						lon = current_bs.lon,
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
								dataset[i]['state'] = current_state_name;
								state = current_state_name;
	                            state_lat_lon_obj = state_lat_lon_db.find({"name" : state}).length > 0 ? state_lat_lon_db.find({"name" : state})[0] : false;
	                            state_param = state_lat_lon_obj ? JSON.stringify(state_lat_lon_obj) : false;
	                            state_click_event = "onClick='gmap_self.state_label_clicked("+state_param+")'";

								var new_lat_lon_obj = state_lat_lon_db.where(function(obj) {
									return obj.name == current_state_name;
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
				if(isApiResponse == 1) {
					all_devices_loki_db.insert(dataset[i]);
				}

				//Loop For Sector Devices
				for(var j=sectors_data.length;j--;) {

					var sector_tech = sectors_data[j]['technology'],
						sector_vendor = sectors_data[j]['vendor'];
					if (sector_tech != 'NA') {
						tech_vendor_obj[sector_tech] = tech_vendor_obj[sector_tech] ? tech_vendor_obj[sector_tech] : [];
						if(sector_vendor != 'NA' && tech_vendor_obj[sector_tech].indexOf(sector_vendor) == -1) {
							tech_vendor_obj[sector_tech].push(sector_vendor);
						}

						if(sector_vendor != 'NA' && all_vendor_array.indexOf(sector_vendor) == -1) {
							all_vendor_array.push(sector_vendor); 
						}
					}

					var total_ss = sectors_data[j].sub_stations ? sectors_data[j].sub_stations.length : 0;
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
		 * @method plotDevices_wmaps
		 * @param bs_ss_devices {Object} In case of BS, it is the devies object array & for SS it contains BS marker object with SS & sector info
		 * @param stationType {String}, It contains that the points are for BS or SS.
		 */
		
	    this.plotDevices_wmaps = function(bs_ss_devices, stationType) {

			if(isDebug) {
				console.log("White Map - Plot Devices Function");
				start_date_white_plot = new Date();
			}
			var zoom_level = ccpl_map.getZoom(),
				hide_flag = !$("#show_hide_label")[0].checked,
				icon = base_url+"/static/img/icons/bs.png",
				bs_size_obj = global_this.getMarkerSize_wmap(true),
				bs_width = bs_size_obj.width ? bs_size_obj.width : whiteMapSettings.size.medium.width,
				bs_height = bs_size_obj.height ? bs_size_obj.height : whiteMapSettings.size.medium.height,
				bs_size = new OpenLayers.Size(bs_width, bs_height),
				other_size_obj = global_this.getMarkerSize_wmap(false),
				other_width = other_size_obj.width ? other_size_obj.width : whiteMapSettings.devices_size.medium.width,
				other_height = other_size_obj.height ? other_size_obj.height : whiteMapSettings.devices_size.medium.height,
				devices_size = new OpenLayers.Size(other_width, other_height);

			//Loop through the bs_ss_devices
			for(var i=0; i< bs_ss_devices.length; i++) {
				wm_obj.data[bs_ss_devices[i].name] = bs_ss_devices[i];
				
				var lon = bs_ss_devices[i].lon, 
					lat = bs_ss_devices[i].lat,
					sector_info_list = bs_ss_devices[i].sectorss_info_list,
					sector_infoWindow_content = sector_info_list ? sector_info_list : [],
					filter_info = {
		            	"bs_name" : bs_ss_devices[i].name,
		                "bs_id" : bs_ss_devices[i].bs_id
		            };

				// BS marker url
				var bs_marker_url = bs_ss_devices[i].markerUrl ? base_url+"/"+bs_ss_devices[i].markerUrl : base_url+"/static/img/icons/bs.png",
					bs_maintenance_status = bs_ss_devices[i].maintenance_status ? $.trim(bs_ss_devices[i].maintenance_status) : "No";

				/*Create BS Marker Info Object*/
				var bs_marker_object = getMarkerInfoJson(bs_ss_devices[i], 'base_station', filter_info);

				// Update map specific info
				bs_marker_object['position'] = {lat: bs_ss_devices[i].lat, lon: bs_ss_devices[i].lon};
				bs_marker_object['icon'] = bs_marker_url;
				bs_marker_object['oldIcon'] = bs_marker_url;
				bs_marker_object['clusterIcon'] = bs_marker_url;
				bs_marker_object['zIndex'] = 250;
				bs_marker_object['optimized'] = false;
				bs_marker_object['markerType'] = 'BS';
				bs_marker_object['isMarkerSpiderfied'] =	false;
				bs_marker_object['isActive'] =	1;
				bs_marker_object['layerReference'] = ccpl_map.getLayersByName("Markers")[0];
				bs_marker_object['layer'] =	ccpl_map.getLayersByName("Markers")[0];

				var bs_marker = global_this.createOpenLayerVectorMarker(bs_size, bs_marker_url, lon, lat, bs_marker_object);
				bs_ss_markers.push(bs_marker);

				// ccpl_map.getLayersByName("Markers")[0].addFeatures([bs_marker]);

				/*Sectors Array*/
				var sector_array = bs_ss_devices[i].sectors ? bs_ss_devices[i].sectors : [],
					backhaul_array = bs_ss_devices[i].backhual ? bs_ss_devices[i].backhual : [],
					deviceIDArray= [];

				
				/*Plot Sector*/
				for (var j = 0; j < sector_array.length; j++) {

					var fetched_azimuth = sector_array[j].azimuth_angle,
						fetched_beamWidth = sector_array[j].beam_width,
						fetched_color = sector_array[j].color && sector_array[j].color != 'NA' ? sector_array[j].color : 'rgba(74,72,94,0.58)',
						ss_infoWindow_content = sector_array[j].ss_info_list ? sector_array[j].ss_info_list : [],
						azimuth = fetched_azimuth && fetched_azimuth != 'NA' ? fetched_azimuth : 10,
						beam_width = fetched_beamWidth && fetched_beamWidth != 'NA' ? fetched_beamWidth : 10,
						sector_color = fetched_color,
						sector_perf_url = sector_array[j].perf_page_url ? sector_array[j].perf_page_url : "",
						sector_inventory_url = sector_array[j].inventory_url ? sector_array[j].inventory_url : "",
						sector_item_index = sector_array[j].item_index > -1 ? sector_array[j].item_index : 0,
						sector_tech = sector_array[j].technology ? $.trim(sector_array[j].technology.toLowerCase()) : "",
						orientation = $.trim(sector_array[j].polarization),
						sector_child = sector_array[j].sub_stations,
						rad = sector_array[j].radius && Number(sector_array[j].radius) > 0 ? sector_array[j].radius : 0.5,
						parent_info = {
							'filter_info' : {
								'bs_name' 		   : bs_ss_devices[i].name,
								'sector_name' 	   : sector_array[j].ip_address,
								'bs_id' 		   : bs_ss_devices[i].bs_id,
								'sector_id' 	   : sector_array[j].sector_id,
								'sector_device_id' : sector_array[j].device_id,
								'id' 			   : sector_array[j].id
							},
							'bs_lat'	  : lat,
							'bs_lon'	  : lon
						},
						startLon = "",
						startLat = "",
						sect_height = sector_array[j].antenna_height;

					var startEndObj = {};

					if(ptp_tech_list.indexOf(sector_tech)  == -1) {
						/*Call createSectorData function to get the points array to plot the sector on google maps.*/
						gmap_self.createSectorData(lat,lon,rad,azimuth,beam_width,orientation,function(pointsArray) {
						
							var halfPt = Math.floor(pointsArray.length / (+2)),
								polyStartLat = "",
								polyStartLon = "";

							if(halfPt == 1) {
								var latLonArray = [
									pointsArray[0],
									pointsArray[1]
								];
								var centerPosition = gmap_self.getMiddlePoint(latLonArray);

								polyStartLat = centerPosition.lat * 180 / Math.PI;
								polyStartLon = centerPosition.lon * 180 / Math.PI;
							} else {
								polyStartLat = pointsArray[halfPt].lat;
								polyStartLon = pointsArray[halfPt].lon;
							}

							var sectorInfo = getMarkerInfoJson(sector_array[j], 'sector_polygon', parent_info);

							/*Plot sector on map with the retrived points*/
							whiteMapClass.plotSector_wmap(pointsArray, sectorInfo);

							startEndObj["startLat"] = polyStartLat;
							startEndObj["startLon"] = polyStartLon;
							startEndObj["sectorLat"] = polyStartLat;
							startEndObj["sectorLon"] = polyStartLon;
						});
					} else {

						startEndObj["startLat"] = bs_ss_devices[i].lat;
		    			startEndObj["startLon"] = bs_ss_devices[i].lon;
		    			
		    			startEndObj["sectorLat"] = bs_ss_devices[i].lat;
						startEndObj["sectorLon"] = bs_ss_devices[i].lon;
					}

					if(ptp_tech_list.indexOf(sector_tech)  > -1) {

						if(deviceIDArray.indexOf(sector_array[j].device_id) == -1) {

							parent_info['startLat'] = startEndObj["startLat"];
							parent_info['startLon'] = startEndObj["startLon"];

							var sectors_Markers_Obj = getMarkerInfoJson(sector_array[j], 'sector', parent_info);

							// Update map specific info
							sectors_Markers_Obj['position'] = {lat: lat, lon: lon};
							sectors_Markers_Obj['icon'] = base_url+'/static/img/icons/1x1.png';
							sectors_Markers_Obj['oldIcon'] = base_url+"/"+sector_array[j].markerUrl;
							sectors_Markers_Obj['clusterIcon'] = base_url+'/static/img/icons/1x1.png';
							sectors_Markers_Obj['zIndex'] = 200;
							sectors_Markers_Obj['optimized'] = false;
							sectors_Markers_Obj['isActive'] = 1;
							sectors_Markers_Obj['map'] = 'current';
							sectors_Markers_Obj['layerReference'] = ccpl_map.getLayersByName("Devices")[0];
		                }

		                var sect_height = gisPerformanceClass.getKeyValue(
		                	sector_infoWindow_content,
		                	"antenna_height",
		                	true,
		                	sector_item_index
	                	);

						/*Create Sector Marker*/
						var sector_Marker = global_this.createOpenLayerVectorMarker(
							devices_size,
							sectors_Markers_Obj.icon,
							lon,
							lat,
							sectors_Markers_Obj
						);

						if(!bsDevicesObj[bs_ss_devices[i].name]) {
							bsDevicesObj[bs_ss_devices[i].name]= [];
						}

						bsDevicesObj[bs_ss_devices[i].name].push(sector_Marker);

						ccpl_map.getLayersByName("Devices")[0].addFeatures([sector_Marker]);

						if(sectorMarkerConfiguredOn.indexOf(sector_array[j].ip_address) == -1) {
							sector_MarkersArray.push(sector_Marker);
							// allMarkersArray_wmap.push(sector_Marker);

							/*Push Sector marker to pollableDevices array*/
							pollableDevices.push(sector_Marker);
							
							allMarkersObject_wmap['sector_device']['sector_'+sector_array[j].ip_address] = sector_Marker;

							sectorMarkerConfiguredOn.push(sector_array[j].ip_address);
							if(sectorMarkersMasterObj[bs_ss_devices[i].name]) {
								sectorMarkersMasterObj[bs_ss_devices[i].name].push(sector_Marker)
							} else {
								sectorMarkersMasterObj[bs_ss_devices[i].name]= [];
								sectorMarkersMasterObj[bs_ss_devices[i].name].push(sector_Marker)
							}	
						}

						/*End of Create Sector Marker*/
						deviceIDArray.push(sector_array[j].device_id);
					}

					/*Plot Sub-Station*/
					for(var k=sector_child.length;k--;) {
					
						var ss_marker_obj = sector_child[k],
							ckt_id_val = ss_marker_obj.circuit_id ? ss_marker_obj.circuit_id : "",
							parent_info = {
								'filter_info' : {
									'bs_name' 		   : bs_ss_devices[i].name,
									'sector_name' 	   : sector_array[j].ip_address,
						    		"ss_name" 		   : ss_marker_obj.name,
									'bs_id' 		   : bs_ss_devices[i].bs_id,
									'sector_id' 	   : sector_array[j].sector_id,
									'sector_device_id' : sector_array[j].device_id,
									"id" 			   : ss_marker_obj.id
								},
								'technology' : sector_array[j].technology,
								'sector_device_name' : sector_array[j].device_name
							};

						// Set the ckt id to sector marker object (only in case of PTP)
						if(ptp_tech_list.indexOf(sector_tech) > -1) {
							allMarkersObject_wmap['sector_device']['sector_'+sector_array[j].ip_address]["cktId"] = ckt_id_val;
						}

						var ss_marker_object = getMarkerInfoJson(ss_marker_obj, 'sub_station', parent_info);

						// Update map specific info
						ss_marker_object['position'] = {lat: ss_marker_obj.lat, lon: ss_marker_obj.lon};
						ss_marker_object['icon'] = base_url+"/"+ss_marker_obj.markerUrl;
						ss_marker_object['oldIcon'] = base_url+"/"+ss_marker_obj.markerUrl;
						ss_marker_object['clusterIcon'] = base_url+"/"+ss_marker_obj.markerUrl;
						ss_marker_object['zIndex'] = 200;
						ss_marker_object['optimized'] = false;
						ss_marker_object['zIndex'] = 200;
						ss_marker_object['map'] = 'current';
				    	ss_marker_object['isActive'] =  1;
				    	ss_marker_object['isMarkerSpiderfied'] =  false;
				    	ss_marker_object['layerReference'] =  ccpl_map.getLayersByName("Markers")[0];
				    	ss_marker_object['layer'] =  ccpl_map.getLayersByName("Markers")[0];

					    /*Create SS Marker*/
					    var ss_marker = global_this.createOpenLayerVectorMarker(
					    	devices_size,
					    	ss_marker_object.icon,
					    	ss_marker_object.ptLon,
					    	ss_marker_object.ptLat,
					    	ss_marker_object
				    	);

					    bs_ss_markers.push(ss_marker);

					    // ccpl_map.getLayersByName("Markers")[0].addFeatures([ss_marker]);
					    var show_ss_len = $("#showAllSS:checked").length;

				    	// Hide Feature if Show SS checkbox unchecked
					    if(show_ss_len <= 0) {
					    	hideOpenLayerFeature(ss_marker);
				    	}

				    	if(last_selected_label && not_ss_param_labels.indexOf(last_selected_label) == -1) {
					    	var labelInfoObject = gisPerformanceClass.getKeyValue(
					    			ss_marker.dataset,
					    			last_selected_label,
					    			false,
					    			ss_marker.item_index
				    			),
					    		labelHtml = "";

					    	if(labelInfoObject) {
	                    		var shownVal = labelInfoObject['value'] ? $.trim(labelInfoObject['value']) : "NA";
	                            labelHtml += shownVal;
	                        }

					    	// If any html created then show label on ss
					    	if(labelHtml) {
								
							   var toolTip_infobox = new OpenLayers.Popup('ss_'+ss_marker_obj.name,
			            	    	new OpenLayers.LonLat(ss_marker.ptLon,ss_marker.ptLat),
			            	    	new OpenLayers.Size(110,18),
			            	    	labelHtml,
			            	    	false
			        	    	);
								ccpl_map.addPopup(toolTip_infobox);
			        	    	
			        	    	// Remove height prop from div's
			        	    	$('.olPopupContent').css('height','');
			        	    	$('.olPopup').css('height','');

		                        tooltipInfoLabel['ss_'+ss_marker_obj.name] = toolTip_infobox;

					    	}
					    }

						markersMasterObj['SS'][String(ss_marker_obj.lat)+ ss_marker_obj.lon]= ss_marker;
				    	markersMasterObj['SSNamae'][String(ss_marker_obj.device_name)]= ss_marker;

				    	allMarkersObject_wmap['sub_station']['ss_'+ss_marker_obj.name] = ss_marker;

					    /*Push SS marker to pollableDevices array*/
						pollableDevices.push(ss_marker)

					    /*Push All SS Lat & Lon*/
					    if(!ssLatArray[String(ss_marker_obj.lat)+"_"+String(ss_marker_obj.lon)]) {
					    	ssLatArray[String(ss_marker_obj.lat)+"_"+String(ss_marker_obj.lon)] = 0;
					    }

					    ssLatArray[String(ss_marker_obj.lat)+"_"+String(ss_marker_obj.lon)] += 1;

					    // if(!ssLonArray[String(ss_marker_obj.lon)]) {
					    // 	ssLonArray[String(ss_marker_obj.lon)] = 0;
					    // }

					    // ssLonArray[String(ss_marker_obj.lon)] += 1;

						var ss_info = {
								"info" : ss_infoWindow_content,
								"antenna_height" : ss_marker_obj.antenna_height,
								"ss_id": ss_marker_obj.id
							},
							base_info = {
								"info" : bs_ss_devices[i].base_station,
								"antenna_height" : bs_ss_devices[i].antenna_height
							};

						startEndObj["nearEndLat"] = bs_ss_devices[i].lat;
						startEndObj["nearEndLon"] = bs_ss_devices[i].lon;

					    startEndObj["endLat"] = ss_marker_obj.lat;
			    		startEndObj["endLon"] = ss_marker_obj.lon;

			    		/*Link color object*/
			    		var lineColor = ss_marker_obj.link_color;
			    		
			    		linkColor = lineColor && lineColor != 'NA' ? lineColor : 'rgba(74,72,94,0.58)';

		    			if(ss_marker_obj.show_link == 1) {
		    				/*Create the link between BS & SS or Sector & SS*/
					    	var ss_link_line = global_this.plotLines_wmap(
					    		startEndObj,
					    		linkColor,
					    		base_info,
					    		ss_info,
					    		sect_height,
					    		sector_array[j].ip_address,
					    		ss_marker_obj.name,
					    		bs_ss_devices[i].name,
					    		bs_ss_devices[i].id,
					    		sector_array[j].sector_id
				    		);

					    	ccpl_map.getLayersByName("Lines")[0].addFeatures([ss_link_line]);

					    	var isLineChecked = $("#showConnLines:checked").length;

					    	if(isLineChecked <= 0) {
								hideOpenLayerFeature(ss_link_line);
					    	}

					    	ssLinkArray.push(ss_link_line);
					    	ssLinkArray_filtered = ssLinkArray;

					    	allMarkersObject_wmap['path']['line_'+ss_marker_obj.name] = ss_link_line;

					    	markersMasterObj['Lines'][String(startEndObj.startLat)+ startEndObj.startLon+ startEndObj.endLat+ startEndObj.endLon]= ss_link_line;
							markersMasterObj['LinesName'][String(bs_ss_devices[i].name)+ ss_marker_obj.name]= ss_link_line;

					    	// allMarkersArray_wmap.push(ss_link_line);
		    			}
					}
				}

				/*Add the master marker to the global master markers array*/
		    	masterMarkersObj.push(bs_marker);

		    	allMarkersObject_wmap['base_station']['bs_'+bs_ss_devices[i].name] = bs_marker;

		    	if(last_selected_label && not_ss_param_labels.indexOf(last_selected_label) > -1) {

                    var labelHtml = bs_ss_devices[i].alias;

			    	// If any html created then show label on ss
			    	if(labelHtml) {
						
					   var toolTip_infobox = new OpenLayers.Popup('bs_'+bs_ss_devices[i].name,
	            	    	new OpenLayers.LonLat(bs_marker.ptLon,bs_marker.ptLat),
	            	    	new OpenLayers.Size(110,18),
	            	    	labelHtml,
	            	    	false
	        	    	);
						ccpl_map.addPopup(toolTip_infobox);
	        	    	
	        	    	// Remove height prop from div's
	        	    	$('.olPopupContent').css('height','');
	        	    	$('.olPopup').css('height','');

                        tooltipInfoLabel['bs_'+bs_ss_devices[i].name] = toolTip_infobox;

			    	}
			    }

		    	//Add markers to markersMasterObj with LatLong at key so it can be fetched later.
				markersMasterObj['BS'][String(bs_ss_devices[i].lat)+bs_ss_devices[i].lon]= bs_marker;
				markersMasterObj['BSNamae'][String(bs_ss_devices[i].name)]= bs_marker;
			}

			if(isCallCompleted == 1) {

				/*Hide The loading Icon*/
				$("#loadingIcon").hide();

				/*Enable the refresh button*/
				// $("#resetFilters").button("complete");

				var ss_markers_object = allMarkersObject_wmap['sub_station'],
					ss_markers_obj_keys = Object.keys(allMarkersObject_wmap['sub_station']);

				overlapping_ss = {};

				for(var k = ss_markers_obj_keys.length;k--;) {
					var key = ss_markers_obj_keys[k],
						lat = ss_markers_object[key].ptLat,
						lon = ss_markers_object[key].ptLon;

					if(key && ss_markers_object[key]) {

						var lat_lon_key = String(lat)+"_"+String(lon),
							ssLatLonOccurence = ssLatArray[lat_lon_key] ? ssLatArray[lat_lon_key] : 0;

						if(ssLatLonOccurence > 1) {
							
							if(!overlapping_ss[lat_lon_key]) {
								overlapping_ss[lat_lon_key] = [];
							}

							if(overlapping_ss[lat_lon_key].indexOf(key) == -1) {
								overlapping_ss[lat_lon_key].push(key);
							}
						}
					}
				}


				
				if(isFirstTime == 1) {
					/*Load data for basic filters*/
					gmap_self.getBasicFilters();
				}
			}

			if(bs_ss_markers.length> 0) {
				ccpl_map.getLayersByName("Markers")[0].addFeatures(bs_ss_markers);
			}

			if(isDebug) {
				var time_diff = (new Date().getTime() - start_date_white_plot.getTime())/1000;
				// console.log("Google Map Idle Event End Time :- "+ new Date().toLocaleString());
				console.log("White Map - Plot Devices End Time :- "+ time_diff + "Seconds");
				console.log("*************************************");
				start_date_white_plot = "";
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

	                var result = "";
	                // Type check of response
	                if(typeof response == 'string') {
	                    result = JSON.parse(response);
	                } else {
	                    result = response;
	                }

					if(result.success == 1) {
						
						//First Time, find how many times Ajax Request is to be sent.
						if (i == 1) {
							total_count = result.data.meta.total_count;
							device_count = result.data.meta.device_count;
							limit = result.data.meta.limit;

							loop_count = Math.ceil(total_count / limit);
						}

						if(result.data.objects) {
							main_devices_data_wmap = main_devices_data_wmap.concat(result.data.objects.children);

							data_for_filter_wmap = main_devices_data_wmap;

							global_this.showStateWiseData_wmap(result.data.objects.children);
						}

						//Condition to check if we need to call Ajax Request again
						if (i <= loop_count && result.success) {

							//if all calls are completed
							if (i == loop_count) {

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

				// Hide loading spinner
        		hideSpinner();

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

		gisPerformanceClass= new GisPerformance();

		/*Initialize Loki db for bs,ss,sector,line,polygon*/
		// Create the database:
		var db = new loki('loki.json');
		// Create new collection for All Map data
		all_devices_loki_db = db.addCollection('allDevices');
		//Call prototype method createOpenLayerMap() to create White Map and in the callback. Start Ajax Request to get Data.
		this.createOpenLayerMap(function() {
			//start ajax request
			startAjaxRequest(1);
		});
	}
}