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

var bs_obj= {};
var isCallCompleted;
var gisPerformanceClass = "";

function WhiteMapClass() {

	/*
	 *
	 * Public Variables
	*/		

		//Live Poll Polygon on off control
		this.livePollingPolygonControl = "";
	/*
	 *
	 * Private Variables
	*/	
		var global_this = "";

		var total_count = 0, device_count= 0, limit= 0, loop_count = 0;

		var wmAdvanceFilterClass = "", wmAdvanceSearchClass = "";

		
		//Variable to Store JSON data of Markers
		var bs_data_list = [];
		//Variable to Store All Markers
		var bs_ss_features_list= [];
		var filtered_Features = {markers: [], lines: [], sectors: []};
		var main_devices_marker_features_wmaps = [], filtered_lines_main_devices_marker_features_wmaps= [];
		var main_lines_sectors_features_wmaps= {'lines': [], 'sectors': []}, filtered_lines_sectors_features = [];
		var devicesMarkersArray= [];
		

		var pollableDevices = [];
		var polled_devices_names= [];

		var hasAdvFilter= 0, hasAdvSearch = 0;
		//Variable to hold Markers
		var deviceMarkerObj = {}, cktLinesObj = {}, sectorsObj = {}, cktLinesBsObj = {}, sectorsBsObj= {}, ssAndDeviceArray= [];
		//Variable to hold device markers currently displayed on map
		var devices_Marker_On_Map = [], devices_Lines_On_Map = [];
		//Variable to hold Searched Markers List
		var searched_markers = [];
		/*
		Variables to hold Data which Technologies, State, Cities
		*/
		var technology = [], vendor = [], state = [], city = [], bs_name = [], ip = [], cktId = [];

		
		//Variable flag to start Performance
		this.startPerformance = false;
		//Variable flag to stop Performance
		this.toStartPerformance = false;
		this.controls = "";


		/*
		Marker Spidifier For BS
		 */

		var markerSpiderfied= "";
		this.unSpiderifyBsMarker= function() {
			if(markerSpiderfied) {
				ccpl_map.getLayersByName("Devices")[0].removeAllFeatures();
				var finalLatLong = new OpenLayers.LonLat(markerSpiderfied.attributes.ptLon, markerSpiderfied.attributes.ptLat);
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
			var bsData = wm_obj.data[feature.attributes.bs_name];
			var bsSectors = bsDevicesObj[bsData.name];
			// var bsSectorLength = bsData.data.param.sector.length;
			if(bsSectors && bsSectors.length) {
				var currentAngle = 0;
				for(var i=0; i<= bsSectors.length; i++) {
					if(i=== bsSectors.length) {
						var bsMarker = wm_obj['features'][bsData.name];						
						var xyDirection= "";
						if(ccpl_map.getZoom() < 9) {
							xyDirection = getAtXYDirection(currentAngle, 7, feature.attributes.ptLon, feature.attributes.ptLat);
						} else {
							if(ccpl_map.getZoom() >= 12) {
								if(ccpl_map.getZoom() >= 14) {
									xyDirection = getAtXYDirection(currentAngle, 0.3, feature.attributes.ptLon, feature.attributes.ptLat);		
								} else {
									xyDirection = getAtXYDirection(currentAngle, 1, feature.attributes.ptLon, feature.attributes.ptLat);		
								}
							} else {
								xyDirection = getAtXYDirection(currentAngle, 3, feature.attributes.ptLon, feature.attributes.ptLat);	
							}
							
						}					

						var finalLatLong = new OpenLayers.LonLat(xyDirection.lon, xyDirection.lat);
											
						var start_point = new OpenLayers.Geometry.Point(feature.attributes.ptLon,feature.attributes.ptLat);
						var end_point = new OpenLayers.Geometry.Point(xyDirection.lon,xyDirection.lat);

						ccpl_map.getLayersByName("Devices")[0].addFeatures([new OpenLayers.Feature.Vector(new OpenLayers.Geometry.LineString([start_point, end_point]))]);

						bsMarker.move(finalLatLong);
						markerSpiderfied = feature;
					} else {
						var sector = bsData.data.param.sector[i];
						var sectorMarker = wm_obj['devices']['sector_'+sector.sector_configured_on];
						var xyDirection= "";
						if(ccpl_map.getZoom() < 9) {
							xyDirection = getAtXYDirection(currentAngle, 7, feature.attributes.ptLon, feature.attributes.ptLat);
						} else {
							if(ccpl_map.getZoom() >= 12) {
								if(ccpl_map.getZoom() >= 14) {
									xyDirection = getAtXYDirection(currentAngle, 0.3, feature.attributes.ptLon, feature.attributes.ptLat);		
								} else {
									xyDirection = getAtXYDirection(currentAngle, 1, feature.attributes.ptLon, feature.attributes.ptLat);		
								}
							} else {
								xyDirection = getAtXYDirection(currentAngle, 3, feature.attributes.ptLon, feature.attributes.ptLat);	
							}
							
						}					

						var finalLatLong = new OpenLayers.LonLat(xyDirection.lon, xyDirection.lat);
											
						var start_point = new OpenLayers.Geometry.Point(feature.attributes.ptLon,feature.attributes.ptLat);
						var end_point = new OpenLayers.Geometry.Point(xyDirection.lon,xyDirection.lat);

						ccpl_map.getLayersByName("Devices")[0].addFeatures([new OpenLayers.Feature.Vector(new OpenLayers.Geometry.LineString([start_point, end_point]))]);
						ccpl_map.getLayersByName("Devices")[0].addFeatures([sectorMarker]);
						sectorMarker.move(finalLatLong);
						sectorMarker.style.externalGraphic = sectorMarker.attributes.pollingIcon ? sectorMarker.attributes.pollingIcon : sectorMarker.attributes.clusterIcon;
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
	 * Gis Performance Section
	 */
		
		function getMarkerInCurrentBound() {
			var bsMarkersInBound = [];
			for(var key in bs_obj) {
				if(bs_obj.hasOwnProperty(key)) {
					if (bs_obj[key].geometry.getBounds().intersectsBounds(ccpl_map.getExtent())) { 
						if(bs_obj[key].attributes.isActive  && bs_obj[key].attributes.isActive != 0) {
							bsMarkersInBound.push(bs_obj[key]['name']);
						}
					}
				}
			}
			return bsMarkersInBound;
		}


		/**
		 * This function show Features[Markers, Lines, Sector, Devices] in currentBounds
		 */
		this.showFeatuesInCurrentBounds = function() {
			
		}

		function updateBsMarker() {}
		function createRequestJson() {}
		function sendAjaxRequest() {}
		function gisPerformanceStop() {}
		function gisPerformanceStart() {}
	/**
	 *
	 * End of Gis Performance Section
	 */

	/**
	 * 
	 * Polling Section
	 */
	
		this.initLivePolling = function() {

			/*Reset marker icon*/
			for(var i=0;i<polygonSelectedDevices.length;i++) {

				var ss_marker = wm_obj['features'][polygonSelectedDevices[i].attributes.name],
					pointType = ss_marker.attributes.pointType,
					sector_marker = "";

				if(pointType === 'sub_station') {
					sector_marker = wm_obj['features'][polygonSelectedDevices[i].attributes.sector_ip];
				} else {
					sector_marker = wm_obj['devices']['sector_'+polygonSelectedDevices[i].attributes.sectorName];
				}

				if(ss_marker) {
					ss_marker.style.externalGraphic = ss_marker.attributes.oldIcon;
					
				} else if(sector_marker) {
					sector_marker.style.externalGraphic = sector_marker.attributes.oldIcon
					
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
		}

		this.fetchPollingTemplate_wmap = function() {

			var selected_technology = $("#polling_tech").val(),
			pathArray = [],
			polygon = "";


			/*Re-Initialize the polling*/
			whiteMapClass.initLivePolling();
			
			/*Reset the variables*/
			polygonSelectedDevices = [];
			pointsArray = [];
			if(selected_technology != "") {
				$("#tech_send").button("loading");
				/*ajax call for services & datasource*/
				$.ajax({
					url : base_url+"/"+"device/ts_templates/?technology="+$.trim(selected_technology),
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

							$("#tech_send").button("complete");

							// ccpl_map.addLayer(ccpl_map.getLayersByName('Polling')[0]);
							ccpl_map.getLayersByName('Polling')[0].setVisibility(true);

							global_this.livePollingPolygonControl.activate();
						}
					},
					error : function(err) {
						
						$("#tech_send").button("complete");
						$("#sideInfo .panel-body .col-md-12 .template_container").html("");

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

				var ss_marker = wm_obj['features'][polygonSelectedDevices[i].attributes.name],
            		sector_ip = "";
            
		        if(polygonSelectedDevices[i].attributes.pointType && ($.trim(polygonSelectedDevices[i].attributes.pointType) == 'sub_station')) {
		        	sector_ip = polygonSelectedDevices[i].attributes.sector_ip;
		        } else {
		        	sector_ip = polygonSelectedDevices[i].attributes.sectorName;
		        }

		        var sector_marker = wm_obj['devices']['sector_'+sector_ip];

				if(ss_marker) {
					ss_marker.style.externalGraphic = ss_marker.attributes.icon;
				} else if(sector_marker) {
					sector_marker.attributes.pollingIcon = "";
					sector_marker.style.externalGraphic = sector_marker.attributes.icon;
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
		}

		this.getMarkerInPolygon = function() {
			var allSS = pollableDevices;
			allSSIds = [];
			

			var selected_polling_technology = $("#polling_tech option:selected").text();

			for(var k=0;k<allSS.length;k++) {
				if(filtered_devices_array.indexOf(allSS[k]) > -1 || filtered_Features.markers.indexOf(allSS[k]) > -1) {
					if(polygon && allSS[k].attributes.ptLon && allSS[k].attributes.ptLat) {
						if(displayBounds(polygon, allSS[k].attributes.ptLon, allSS[k].attributes.ptLat) === 'in') {
							if($.trim(allSS[k].attributes.technology.toLowerCase()) == $.trim(selected_polling_technology.toLowerCase())) {
								
								if($.trim(allSS[k].attributes.technology.toLowerCase()) == "ptp" || $.trim(allSS[k].attributes.technology.toLowerCase()) == "p2p") {
									if(allSS[k].attributes.device_name && (allSSIds.indexOf(allSS[k].attributes.device_name) == -1)) {
										allSSIds.push(allSS[k].attributes.device_name);
										polygonSelectedDevices.push(allSS[k]);
									}
								} else {
									if(allSS[k].attributes.pointType == 'sub_station') {
										if(allSS[k].attributes.device_name && (allSSIds.indexOf(allSS[k].attributes.device_name) == -1)) {
											allSSIds.push(allSS[k].attributes.device_name);
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

				for(var i=0;i<polygonSelectedDevices.length;i++) {
					
					var new_device_name = "";
					var current_technology = $.trim(polygonSelectedDevices[i].attributes.technology.toLowerCase());
					
					if(polygonSelectedDevices[i].attributes.device_name.indexOf(".") != -1) {
						new_device_name = polygonSelectedDevices[i].attributes.device_name.split(".");
						new_device_name = new_device_name.join("-");
					} else {
						new_device_name = polygonSelectedDevices[i].attributes.device_name;
					}

					var devices_counter = "";
					
					if(polygonSelectedDevices[i].attributes.pointType == 'sub_station') {
						devices_counter = polygonSelectedDevices[i].attributes.bs_sector_device;
					} else {
						devices_counter = polygonSelectedDevices[i].attributes.device_name;
					}

						if(!polled_device_count[devices_counter]) {
						polled_device_count[devices_counter]  = 1;
					} else {
						polled_device_count[devices_counter] = polled_device_count[devices_counter] +1;
					}


					if((current_technology == 'ptp' || current_technology == 'p2p') && polygonSelectedDevices[i].attributes.pointType == 'sub_station') {

						if(polygonSelectedDevices[i].attributes.bs_sector_device.indexOf(".") != -1) {
							var new_device_name2 = polygonSelectedDevices[i].attributes.bs_sector_device.split(".");
							new_device_name2 = new_device_name2.join("-");
						} else {
							var new_device_name2 = polygonSelectedDevices[i].attributes.bs_sector_device;
						}

						if(polled_device_count[devices_counter] <= 1) {
							devicesTemplate += '<div class="well well-sm" id="div_'+new_device_name2+'"><h5>Near-End '+(i+1)+'.) '+polygonSelectedDevices[i].attributes.sector_ip+'</h5>';
							devicesTemplate += '<div style="min-height:60px;margin-top:15px;margin-bottom: 5px;" id="livePolling_'+new_device_name2+'">';
							devicesTemplate += '<ul id="pollVal_'+new_device_name2+'" class="list-unstyled list-inline"></ul>';
							devicesTemplate += '<span class="sparkline" id="sparkline_'+new_device_name2+'"></span></div></div>';
						}

						devicesTemplate += '<div class="well well-sm" id="div_'+new_device_name+'"><h5>Far-End '+(i+1)+'.) '+polygonSelectedDevices[i].attributes.ss_ip+'</h5>';
						devicesTemplate += '<div style="min-height:60px;margin-top:15px;margin-bottom: 5px;" id="livePolling_'+new_device_name+'">';
						devicesTemplate += '<ul id="pollVal_'+new_device_name+'" class="list-unstyled list-inline"></ul>';
						devicesTemplate += '<span class="sparkline" id="sparkline_'+new_device_name+'"></span></div></div>';

					} else {
						if(polled_device_count[devices_counter] ) //<= 1) //why do we have this condition ???
						{
							var device_end_txt = "",
								point_name = "";
							if(polygonSelectedDevices[i].attributes.pointType == 'sub_station') {
								device_end_txt = "Far End";
								point_name = polygonSelectedDevices[i].attributes.ss_ip
							} else {
								device_end_txt = "Near End";
								point_name = polygonSelectedDevices[i].attributes.sectorName
							}

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
		 * This function fetch the polling value for selected devices
		 * @method getDevicesPollingData
		 */
		this.getDevicesPollingData_wmaps = function() {

			if(polygonSelectedDevices.length > 0 && $("#lp_template_select").val() != "") {

				$("#getDevicesPollingData").button("loading");

				/*Disable service templates dropdown*/
				$("#lp_template_select").attr("disabled","disabled");

				var selected_lp_template = $("#lp_template_select").val();

				// start spinner
				if($("#fetch_spinner").hasClass("hide")) {
					$("#fetch_spinner").removeClass("hide");
				}

				$.ajax({
					url : base_url+"/"+"device/lp_bulk_data/?ts_template="+selected_lp_template+"&devices="+JSON.stringify(allSSIds),
					// url : base_url+"/"+"static/services.json",
					success : function(results) {
						var result = "";

						if(typeof results === 'string') {
							result = JSON.parse(results);
						} else {
							result = results;
						}
						
						if(result.success == 1) {
							
							$("#getDevicesPollingData").button("complete");


							/*Remove 'text-info' class from all li's*/
							if($(".deviceWellContainer div div ul li")) {
								$(".deviceWellContainer div div ul li").removeClass("text-info");
							}

							// stop spinner
							if(!($("#fetch_spinner").hasClass("hide"))) {
								$("#fetch_spinner").addClass("hide");
							}

							if($(".devices_container").hasClass("hide")) {
								$(".devices_container").removeClass("hide");
							}


							var hasPolledInfo = true;
							for(var i=0;i<allSSIds.length;i++) {
								var new_device_name = "";
								if(allSSIds[i] && allSSIds[i].indexOf(".") != -1) {
									new_device_name = allSSIds[i].split('.');
									new_device_name = new_device_name.join('-');
								} else {
									new_device_name = allSSIds[i];
								}
								if(result.data.devices[allSSIds[i]] != undefined) {

									if(hasPolledInfo) {
										if($("#polling_tabular_view").hasClass("hide")) {
											$("#polling_tabular_view").removeClass("hide");
										}

										/*Remove hide class to navigation container on polling widget*/
										if($("#navigation_container").hasClass("hide")) {
											$("#navigation_container").removeClass("hide");
										}
										hasPolledInfo = false;
									}

									var dateObj = new Date(),
										current_time = dateObj.getHours()+":"+dateObj.getMinutes()+":"+dateObj.getSeconds(),
										final_chart_data = [];
									
									if($("#pollVal_"+new_device_name+" li").length == 0) {

										var fetchValString = "";
										fetchValString += "<li class='fetchVal_"+new_device_name+" text-info' style='padding:0px;'> (<i class='fa fa-clock-o'></i> "+current_time+", <i class='fa fa-arrow-circle-o-right'></i> "+result.data.devices[allSSIds[i]].value+")  <input type='hidden' name='chartVal_"+new_device_name+"' id='chartVal_"+new_device_name+"' value='"+result.data.devices[allSSIds[i]].value+"'/></li>";

										$("#pollVal_"+new_device_name).append(fetchValString);
										/*Sparkline Chart Data*/
										final_chart_data.push((+result.data.devices[allSSIds[i]].value));
									
									} else {

										var	string_val = [];

										$("#chartVal_"+new_device_name).val($("#chartVal_"+new_device_name).val()+","+result.data.devices[allSSIds[i]].value);

										string_val = $("#chartVal_"+new_device_name).val().split(",");

										/*Create integer array from fetched values for sparkline chart*/
										var chart_data = string_val.map(function(item) {
											return parseInt(item, 10);
										});

										$("#pollVal_"+new_device_name).append("<li class='fetchVal_"+new_device_name+" text-info' style='padding:0px;'> , (<i class='fa fa-clock-o'></i> "+current_time+", <i class='fa fa-arrow-circle-o-right'></i> "+result.data.devices[allSSIds[i]].value+")</li>");
										/*Sparkline Chart Data*/
										final_chart_data = chart_data;
									}


									/*Plot sparkline chart with the fetched polling value*/
									$("#sparkline_"+new_device_name).sparkline(final_chart_data, {
										type: "line",
										lineColor: "blue",
										spotColor : "orange",
										defaultPixelsPerValue : 10
									});
									var ss_name = "",
										sector_ip = "";
									for(var x=0;x<polygonSelectedDevices.length;x++) {
										if(allSSIds[i] === polygonSelectedDevices[x].attributes.device_name) {
											if(polygonSelectedDevices[x].attributes.pointType === 'sub_station') {
												ss_name = polygonSelectedDevices[x].attributes.name;
												sector_ip = polygonSelectedDevices[x].attributes.sector_ip;
											} else {
													ss_name = "";
													sector_ip = polygonSelectedDevices[x].attributes.sectorName;  
											}
										}
									}

									var newIcon = base_url+"/"+result.data.devices[allSSIds[i]].icon,
										ss_marker = wm_obj['features'][ss_name],
										sector_marker = wm_obj['devices']['sector_'+sector_ip],
										marker_polling_obj = {
											"device_name" : allSSIds[i],
											"polling_icon" : newIcon,
											"polling_time" : current_time,
											"polling_value" : result.data.devices[allSSIds[i]].value
										};

									if(polled_devices_names.indexOf(allSSIds[i]) == -1) {
										polled_devices_names.push(allSSIds[i]);
									}
									
									if(!complete_polled_devices_icon[allSSIds[i]]) {
										complete_polled_devices_icon[allSSIds[i]] = [];
									}
									complete_polled_devices_icon[allSSIds[i]].push(newIcon);
									complete_polled_devices_data.push(marker_polling_obj);
									
									/*Update the marker icons*/
									if(ss_marker) {
										ss_marker.style.externalGraphic = newIcon;
										ccpl_map.getLayersByName('Markers')[0].drawFeature(ss_marker);
										ccpl_map.getLayersByName('Markers')[0].strategies[0].recluster();
									} else if(sector_marker) {
										sector_marker.attributes.pollingIcon = newIcon;
										sector_marker.style.externalGraphic = newIcon;
										ccpl_map.getLayersByName("Devices")[0].redraw();
									}

									/*total Polled Occurence*/
									total_polled_occurence = complete_polled_devices_icon[allSSIds[i]].length;

									if(complete_polled_devices_icon[allSSIds[i]] && complete_polled_devices_icon[allSSIds[i]].length <= 1) {
										$("#navigation_container button").addClass('disabled');
									} else if(complete_polled_devices_icon[allSSIds[i]] && complete_polled_devices_icon[allSSIds[i]].length > 1) {
										$("#navigation_container button#previous_polling_btn").removeClass('disabled');
										$("#navigation_container button#next_polling_btn").addClass('disabled');
										/*Update previous counter with number of polled occurences*/
										nav_click_counter = total_polled_occurence;
									}

								} // End of for loop
							}
						} else {

							$("#getDevicesPollingData").button("complete");

							// stop spinner
							if(!($("#fetch_spinner").hasClass("hide"))) {
								$("#fetch_spinner").addClass("hide");
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

						$("#getDevicesPollingData").button("complete");

						// stop spinner
						if(!($("#fetch_spinner").hasClass("hide"))) {
							$("#fetch_spinner").addClass("hide");
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
				bootbox.alert("Please select devices & polling template first.");
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
					if(polygonSelectedDevices[x].attributes.device_name === polled_devices_names[i]) {
						marker_name = polygonSelectedDevices[x].attributes.name;
						if(polygonSelectedDevices[x].attributes.pointType === 'sub_station') {
							sector_ip = polygonSelectedDevices[x].attributes.sector_ip ? polygonSelectedDevices[x].attributes.sector_ip : "";
						} else {
							sector_ip = polygonSelectedDevices[x].attributes.sectorName ? polygonSelectedDevices[x].attributes.sectorName : "";
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
					if(polygonSelectedDevices[x].attributes.device_name === polled_devices_names[i]) {
						marker_name = polygonSelectedDevices[x].attributes.name;
						if(polygonSelectedDevices[x].attributes.pointType === 'sub_station') {
							sector_ip = polygonSelectedDevices[x].attributes.sector_ip ? polygonSelectedDevices[x].attributes.sector_ip : "";
						} else {
							sector_ip = polygonSelectedDevices[x].attributes.sectorName ? polygonSelectedDevices[x].attributes.sectorName : "";
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
		This function toggles all Station Markers size based on the Value selected in the dropdown.
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
			for(i=0; i< devicesMarkersArray.length; i++) {
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
				})(devicesMarkersArray[i]);
			}
			//End of Loop through the sector markers

			ccpl_map.getLayersByName("Devices")[0].redraw();
			ccpl_map.getLayersByName("Devices")[0].removeAllFeatures();


			// Loop through the Master Markers
			for(var i=0; i< bs_ss_features_list.length; i++ ) {
				(function updateMasterMarker(marker) {

					var newGraphicHeight = 0, newGraphicWidth = 0, newGraphicXOffset = 0, newGraphicYOffset = 0;
					if(marker.attributes.pointType=== "base_station") {
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
					} else if (marker.attributes.pointType === "sub_station") {
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
				})(bs_ss_features_list[i]);
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
	 *
	 * Plotting Section
	 */
	
		/*
		 * This function takes a array of Markers and loop through each list and call prototype method createOpenLayerMarker() to create Marker for it.
		 * @param markersData {Array for BsData} Array containing Bs to be plotted.
		 * @param callback {Function} Callback to return when Finished.
		 * Also we add Marker Data in our variables for future use.
		 */
	    this.plotMarkers = function(markersData, callback) {
			
			//Loop through the markersData
			$.each(markersData, function(i, markerData) {
				
				//store state in array
				if(markerData.data.state) {
					if(!state_city_obj[markerData.data.state]) {
						state_city_obj[markerData.data.state] = [];
					}
					//store city in array
					if(state_city_obj[markerData.data.state].indexOf(markerData.data.city) == -1) {
						state_city_obj[markerData.data.state].push(markerData.data.city);
					}
				}

				//store city in array
				if(markerData.data.city) {
					if(all_cities_array.indexOf(markerData.data.city) == -1) {
						all_cities_array.push(markerData.data.city);
					}
				}

				//base station 
				var id = markerData.id, 
					name = markerData.name, 
					lon = markerData.data.lon, 
					lat = markerData.data.lat, 
					icon = base_url+"/static/img/icons/bs.png", 
					size = new OpenLayers.Size(whiteMapSettings.size.medium.width, whiteMapSettings.size.medium.height), 
					type = "base_station";

				//add data to main device obj
				wm_obj.data[name] = markerData;
				
				var bsMarkerCustomInfo = { 
					id: id, 
					name: name, 
					type: type, 
					isSpiderfied: true, 
					icon: icon, 
					oldIcon:icon,
					clusterIcon:icon,
					child_ss: markerData.data.param.sector,
					original_sectors: markerData.data.param.sector,
					dataset: markerData.data.param.base_station, 
					bsInfo:markerData.data.param.base_station,
					bhInfo: markerData.data.param.backhual, 
					bs_name: name,
					filter_data: {"bs_name": markerData.name},
					antenna_height: markerData.data.antenna_height,
					ptLat: lat, 
					ptLon: lon, 
					pointType: type,
					device_name : markerData.data.device_name,
					markerType: 'BS',
					isMarkerSpiderfied: false,
					isActive: 1
				}

				var marker = global_this.createOpenLayerVectorMarker(size, icon, lon, lat, bsMarkerCustomInfo);
				wm_obj.features[name] = marker;
				bs_obj[name] = marker;

				bs_ss_features_list.push(marker);
				
				var deviceIDArray= [];
				
				//base station devices loop
				for (var j = 0; j < markerData.data.param.sector.length; j++) {
					
					var device = markerData.data.param.sector[j];

					if(!tech_vendor_obj[device.technology]) {
						tech_vendor_obj[device.technology] = [];
					}

					if(tech_vendor_obj[device.technology].indexOf(device.vendor) == -1) {
						tech_vendor_obj[device.technology].push(device.vendor);
					}

					if(all_vendor_array.indexOf(device.vendor) == -1) {
						all_vendor_array.push(device.vendor); 
					}

					var sectorRadius = device.radius, rad = 4;
					/*If radius is greater than 4 Kms then set it to 4.*/
					if((sectorRadius != null) && (sectorRadius > 0)) {
						rad = sectorRadius;
					}

					var startEndObj = {};

					createSectorData(lat, lon, rad, device.azimuth_angle, device.beam_width, device.orientation, function(sectorPoints) {

						var halfPt = Math.floor(sectorPoints.length / (+2));

						var startLat = sectorPoints[halfPt].lat;
						var startLon = sectorPoints[halfPt].lon;

						if($.trim(device.technology) != "PTP" && $.trim(device.technology) != "P2P") {
							var sColor = "#000000",
								sWidth = 1;

							if(device.technology.toLowerCase() == 'pmp') {
								sColor = '#FFFFFF';
								sWidth = 2;
							}

							var sectorCustomInfo = {
								ptLat: lat,
								ptLon: lon,
								pointType: "sector",
								strokeColor      : sColor,
								fillColor 	     : device.color,
								technology: device.technology,
								strokeOpacity    : 1,
								fillOpacity 	 : 0.5,
								strokeWeight     : sWidth,
								lat: lat,
								lon: lon,
								azimuth: device.azimuth_angle,
								beam_width: device.beam_width,
								technology: device.technology,
								vendor 				: device.vendor,
								deviceExtraInfo 	: device.info,
								deviceInfo 			: device.device_info,
								poll_info 			: [],
								radius: rad,
								dataset: device.info,
								startLat: startLat,
								startLon: startLon,
								filter_data 	 : {"bs_name" : name, "sector_name" : device.sector_configured_on},
								bhInfo: [],
								child_ss: device.sub_station,
								polarisation: device.polarisation,
								original_sectors : device.sub_station
							};

							var plottedSector = global_this.plotSector_wmap(sectorPoints, sectorCustomInfo);

							filtered_Features.sectors.push(plottedSector);

							main_lines_sectors_features_wmaps.sectors.push(plottedSector);

							wm_obj.sectors["poly_"+device.sector_configured_on+"_"+rad+"_"+device.azimuth_angle+"_"+device.beam_width] = plottedSector;

							ccpl_map.getLayersByName("Sectors")[0].addFeatures([plottedSector]);

							startEndObj["startLat"] = sectorPoints[halfPt].lat;
							startEndObj["startLon"] = sectorPoints[halfPt].lon;


							startEndObj["sectorLat"] = sectorPoints[halfPt].lat;
							startEndObj["sectorLon"] = sectorPoints[halfPt].lon;
						} else {
							startEndObj["startLat"] = markerData.data.lat;
							startEndObj["startLon"] = markerData.data.lon;

							startEndObj["sectorLat"] = markerData.data.lat;
							startEndObj["sectorLon"] = markerData.data.lon;
						}

					});
					
					var device_marker_size = new OpenLayers.Size(whiteMapSettings.devices_size.medium.width, whiteMapSettings.devices_size.medium.height);
					
					if($.trim(device.technology.toLowerCase()) == "p2p" || $.trim(device.technology.toLowerCase()) == "ptp") {
						
						if(deviceIDArray.indexOf(device['device_info'][1]['value']) === -1) {

							// var perf_obj = { "performance_paramter" : "N/A", "performance_value" : "N/A", "frequency" : "N/A", "pl" : "N/A" };
							
							var deviceAdditionalInfo = {
								ptLat: lat,
								ptLon: lon,
								icon: base_url+'/static/img/icons/1x1.png',
								oldIcon: base_url+'/static/img/icons/1x1.png',
								clusterIcon: base_url+"/"+device.markerUrl,
								pollingIcon: '',
								pointType 		 	: 'sector_Marker',
								technology: device.technology,
								vendor 				: device.vendor,
								deviceExtraInfo 	: device.info,
								deviceInfo 			: device.device_info,
								poll_info 			: [],
								sectorName: device.sector_configured_on,
								device_name : device.sector_configured_on_device,
								name: device.sector_configured_on_device,
								filter_data 	    : {"bs_name" : name, "sector_name" : device.sector_configured_on},
								sector_lat  		: startEndObj["startLat"],
								sector_lon  		: startEndObj["startLon"],
								type: "base_station_device",
								hasPerf: 0,
								isActive: 1
								// perf_data_obj  		: perf_obj,
								// antenna_height 		: device.antenna_height
							}


							//Create deviceMarker
							var deviceMarker = global_this.createOpenLayerVectorMarker(device_marker_size, deviceAdditionalInfo.icon, lon, lat, deviceAdditionalInfo);
							
							if(!bsDevicesObj[name]) {
								bsDevicesObj[name]= [];
							}

							if(!tempbsDeviceObj[name]) {
								tempbsDeviceObj[name]= [];
							}
							
							tempbsDeviceObj[name].push(deviceMarker);
							bsDevicesObj[name].push(deviceMarker);

							devicesMarkersArray.push(deviceMarker);

							filtered_devices_array.push(deviceMarker);


							if(sectorMarkerConfiguredOn.indexOf(device.sector_configured_on) == -1) {
								main_devices_marker_features_wmaps.push(deviceMarker);

								/*Push Sector marker to pollableDevices array*/
								pollableDevices.push(deviceMarker);

								wm_obj['devices']['sector_'+device.sector_configured_on] = deviceMarker;

								sectorMarkerConfiguredOn.push(device.sector_configured_on);

								if(wm_obj['devices'][name]) {
									wm_obj['devices'][name].push(deviceMarker)
								} else {
									wm_obj['devices'][name]= [];
									wm_obj['devices'][name].push(deviceMarker)
								}	
							}

							/*End of Create Sector Marker*/
							deviceIDArray.push(device['device_info'][1]['value']);
						}

					}
					//substation loop
					for (var k = 0; k < device.sub_station.length; k++) {

						var sub_station = device.sub_station[k];
						wm_obj.data[sub_station.name] = sub_station;

						// var perf_obj = { "performance_paramter" : "N/A", "performance_value" : "N/A", "frequency" : "N/A", "pl" : "N/A" };
						var sub_station_lon = sub_station.data.lon;
						var sub_station_lat = sub_station.data.lat;
						var sub_station_icon = base_url+"/"+sub_station.data.markerUrl;
						var sub_station_name = sub_station.name

						var subStationAdditionalInfo = {
							ptLon: sub_station_lon, 
							ptLat: sub_station_lat, 
							technology: sub_station.data.technology,
							pointType: "sub_station",
							type: "sub_station",
							dataset: sub_station.data.param.sub_station,
							icon: sub_station_icon,
							oldIcon: sub_station_icon,
							clusterIcon: sub_station_icon,
							bhInfo: [],
							poll_info: [],
							antenna_height: sub_station.data.antenna_height,
							name: sub_station_name,
							bs_name: name,
							bs_sector_device :  device.sector_configured_on_device,
							filter_data 	 :  {"bs_name" : name, "sector_name" : device.sector_configured_on, "ss_name" : sub_station_name},
							device_name 	 : 	sub_station.device_name,
							bs_sector_device :  device.sector_configured_on_device,
							ss_ip 	 		 : 	sub_station.data.substation_device_ip_address,
							sector_ip 		 :  device.sector_configured_on,
							hasPerf: 0,
							isActive: 1
							// perf_data_obj: perf_obj
						}


						//Create marker
						sub_station_marker = global_this.createOpenLayerVectorMarker(device_marker_size, sub_station_icon, sub_station_lon, sub_station_lat, subStationAdditionalInfo);

						wm_obj.features[sub_station.name] = sub_station_marker;
						
						bs_ss_features_list.push(sub_station_marker);

						 /*Push SS marker to pollableDevices array*/
						pollableDevices.push(sub_station_marker);

						var ss_info = {
							"info" : sub_station.data.param.sub_station,
							"antenna_height" : sub_station.data.antenna_height
						},
						base_info = {
							"info" : markerData.data.param.base_station,
							"antenna_height" : markerData.data.antenna_height
						};

						startEndObj["nearEndLat"] = markerData.data.lat;
						startEndObj["nearEndLon"] = markerData.data.lon;

						startEndObj["endLat"] = sub_station.data.lat;
						startEndObj["endLon"] = sub_station.data.lon;

						// /*Sub station info Object*/
						// ss_info["info"] = sub_station.data.param.sub_station;

						// ss_info["antenna_height"] = sub_station.data.antenna_height;
						/*Link color object*/
						var linkColor = sub_station.data.link_color;

						// base_info["info"] = markerData.data.param.base_station;
						// base_info["antenna_height"] = markerData.data.antenna_height;

						if(sub_station.data.show_link == 1) {

							var ss_info_obj = "", ss_height = 40;

							if(sub_station.data.param.sub_station != undefined || sub_station.data.param.sub_station == "") {
								ss_info_obj = sub_station.data.param.sub_station.info;
								ss_height = sub_station.data.param.sub_station.antenna_height;
							} else {
								ss_info_obj = "";
								ss_height = 40;
							}

							var bs_info_obj = "", bs_height = 40;

							if(markerData.data.param.base_station != undefined || markerData.data.param.base_station == "") {
								bs_info_obj = markerData.data.param.base_station.info;
								bs_height = markerData.data.param.base_station.antenna_height;
							} else {
								bs_info_obj = "";
								bs_height = 40;
							}

							var sect_height="";
							if (device.antenna_height == undefined || device.antenna_height == ""){
								sect_height = 47;
							} else {
								sect_height = device.antenna_height;
							}

							var lineAdditionalInfo = {
								strokeColor: linkColor,
								strokeColor: 1.0,
								strokeWeight: 3,
								bsname: name,
								ssname: sub_station_name,
								sectorName 	    : device.sector_configured_on,
								ckt: device.circuit_id,
								devicename: device.device_info[0].value,
								type: "line",
								pointType: "path",
								bs_info: markerData.data.param.base_station,
								ss_info: sub_station.data.param.sub_station,
								nearLat: lat,
								nearLon: lon,
								sector_lat 		: startEndObj.sectorLat,
								sector_lon 		: startEndObj.sectorLon,
								ss_height 		: sect_height,
								bs_height 		: ss_height,
								ss_lat: sub_station_lat,
								ss_lon: sub_station_lon,
								bs_lat 			: startEndObj.startLat,
								bs_lon 			: startEndObj.startLon,
								filter_data 	: {"bs_name" : name, "sector_name" : device.sector_configured_on, "ss_name" : sub_station_name},
								filteredLine: true
							}

							
							var line = global_this.plotLines_wmap(startEndObj.startLon,startEndObj.startLat, startEndObj.endLon,startEndObj.endLat, linkColor, lineAdditionalInfo);

							filtered_Features.lines.push(line);

							ccpl_map.getLayersByName("Lines")[0].addFeatures([line]);

							main_lines_sectors_features_wmaps.lines.push(line);

							wm_obj.lines['line_'+sub_station.name] = line;
						}
					}
				}
			});
			callback();
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

						//First Time, find how many times Ajax Request is to be sent.
						if (i === 1) {
							total_count = response.data.meta.total_count;
							device_count = response.data.meta.device_count;
							limit = response.data.meta.limit;

							loop_count = Math.ceil(total_count / limit);
						}

						//Condition to check if we need to call Ajax Request again
						if (i <= loop_count && response.success && response.data.objects.children.length) {

							bs_data_list = bs_data_list.concat(response.data.objects.children);
							
							//Plot markers, on callback
							global_this.plotMarkers(response.data.objects.children, function() {
								
								//if all calls are completed
								if (i === loop_count) {

									//hide Loading
									global_this.hideLoading();

									data_for_filter_wmap = bs_data_list;
									main_devices_data_wmap = bs_data_list;

									filtered_Features.markers = bs_ss_features_list;									

									//add markers to the vector Layer
									ccpl_map.getLayersByName('Markers')[0].addFeatures(filtered_Features.markers);

									//activate cluster strategy
									ccpl_map.getLayersByName('Markers')[0].strategies[0].activate();

									//populate basic filter dropdown
									gmap_self.getBasicFilters();

									return;
								}

								//send next request after 40 ms.
								setTimeout(function() {
									i++;
									//send next request
									startAjaxRequest(i);
								}, 40);
							});

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

					//hide Loading
					global_this.hideLoading();
				}
			});
		}

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

		//Call prototype method createOpenLayerMap() to create White Map and in the callback. Start Ajax Request to get Data.
		this.createOpenLayerMap(function() {			
			//start ajax request
			startAjaxRequest(1);
		});
	}
}