var ccpl_map, base_url, main_devices_data_wmap= [], wm_obj = {'features': {}, 'data': {}, 'devices': {}, 'lines': {}, 'sectors': {}};
var data_for_filter_wmap = []
var state_city_obj= {}, all_cities_array= [], tech_vendor_obj= {}, all_vendor_array= [], sectorMarkerConfiguredOn= [], sectorMarkersMasterObj = {};
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
function WhiteMapClass() {

	/*
	 *
	 * Public Variables
	*/
		//vector Layer for Sector
		this.sectorsLayer = "";

		//vector Layer for Lines
		this.linesLayer = "";
		
		//vector Layer for Markers
		this.markersLayer = "";

		//CLuster Strategy for Markers Layer
		this.markersLayerStrategy = "";

		//vector Layer for Marker Devices
		this.markerDevicesLayer = "";

		//vector Layer for Live Poll Features
		this.livePollFeatureLayer = "";

		//vector Layer for Search Markers
		this.searchMarkerLayer = "";

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

		var bsDevicesObj = {};

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

	/**
	 *
	 * Map Events Section
	 */

		var markerSpiderfied= "";
		this.unSpiderifyBsMarker= function() {
			if(markerSpiderfied) {
				markerSpiderfied.attributes.isMarkerSpiderfied = false;
				markerSpiderfied= "";
				global_this.markerDevicesLayer.removeAllFeatures();
			}
		}

		// this.spiderfyBsMarker= function(markername) {
		// 	this.unSpiderifyBsMarker();
		// 	var bs_marker= wm_obj.features[markername];
		// 	var bs_devices = deviceMarkerObj[markername];
		// 	var map_Zoom_Level = ccpl_map.getZoom();
		// 	devices_Marker_On_Map= [];
		// 	if(bs_devices) {
		// 		//Loop through the devices
		// 		for (var i = 0; i < bs_devices.length; i++) {
		// 			// console.log(bs_devices[i]);
		// 			bs_devices[i].style.externalGraphic = bs_devices[i].attributes.defaultIcon;

		// 			bs_devices[i].move(new OpenLayers.LonLat(bs_devices[i].attributes.ptLon, bs_devices[i].attributes.ptLat));
		// 			devices_Marker_On_Map.push(bs_devices[i]);
		// 			if(i=== bs_devices.length-1) {
		// 				global_this.markerDevicesLayer.removeAllFeatures();
		// 				global_this.markerDevicesLayer.addFeatures(devices_Marker_On_Map);
		// 				global_this.markerDevicesLayer.redraw();
		// 			}
		// 		}
		// 		bs_marker.isSpiderfied = false;
		// 		markerSpiderfied= bs_marker;
		// 	}
		// }

		function spiderifyMarker(feature, otherfeatures) {
			global_this.unSpiderifyBsMarker();
			if(feature && otherfeatures && otherfeatures.length) {
				var totalLen = otherfeatures.length;
				var totalAngle = 360;
				var angleToIncrase = totalAngle/totalLen;
				var currentAngle = 0;
				var zoomLevel = ccpl_map.getZoom();	
				for(var i=0; i< otherfeatures.length; i++) {		
					otherfeatures[i].style.externalGraphic = otherfeatures[i].attributes.originalIcon;
					var xy = getAtXYDirection(currentAngle, 1, otherfeatures[i].attributes.ptLon, otherfeatures[i].attributes.ptLat);
					var diffLon = ((xy.lon)*1000000000000) - ((otherfeatures[i].attributes.ptLon)*1000000000000);
					var diffLat = ((xy.lat)*1000000000000) - ((otherfeatures[i].attributes.ptLat)*1000000000000);
					var deviceLng = (((diffLon * zoomLevel)/9)/1000000000000);
					var deviceLat = (((diffLat * zoomLevel)/9)/1000000000000);
					console.log(deviceLng, deviceLat);
					var newLatLong = new OpenLayers.LonLat(deviceLng, deviceLat);
					// if(zoomLevel> 8) {
					// 	if(zoomLevel> 11) {
					// 		var xy = getAtXYDirection(currentAngle, 1, otherfeatures[i].attributes.ptLon, otherfeatures[i].attributes.ptLat);
					// 		var newLatLong = new OpenLayers.LonLat(xy.lon, xy.lat);
							
					// 	} else {
					// 		var xy = getAtXYDirection(currentAngle, 1, otherfeatures[i].attributes.ptLon, otherfeatures[i].attributes.ptLat);
					// 		var newLatLong = new OpenLayers.LonLat(xy.lon, xy.lat);
					// 	}
						
					// } else {
					// 	var xy = getAtXYDirection(currentAngle, 3, otherfeatures[i].attributes.ptLon, otherfeatures[i].attributes.ptLat);
					// 	var newLatLong = new OpenLayers.LonLat(xy.lon, xy.lat);
					// }
					var start_point = new OpenLayers.Geometry.Point(feature.attributes.ptLon,feature.attributes.ptLat);
					var end_point = new OpenLayers.Geometry.Point(deviceLng, deviceLat);

					global_this.markerDevicesLayer.addFeatures([new OpenLayers.Feature.Vector(new OpenLayers.Geometry.LineString([start_point, end_point]))]);
					global_this.markerDevicesLayer.addFeatures(otherfeatures[i]);
					otherfeatures[i].move(newLatLong);
					currentAngle+= angleToIncrase;
				}

				markerSpiderfied = feature;
				feature.attributes.isMarkerSpiderfied = true;
			}
		}

		this.toggleLineLayer = function() {
			var selectedValue = $("#showConnLines").prop('checked');
			if(selectedValue) {
				this.linesLayer.display(true);
			} else {
				this.linesLayer.display(false);
			}
		}

		var lastZoomLevel = 1;
		var lastIconCondition = "medium";
		this.mapZoomChangeEvent = function() {

			if(ccpl_map.getZoom() > whiteMapSettings.zoomLevelAfterLineAppears) {
				var selectedValue = $("#showConnLines").prop('checked', true);
				this.markersLayerStrategy.distance = 40;
				this.markersLayerStrategy.threshold = 10;
				this.markersLayerStrategy.recluster();
			} else {
				var selectedValue = $("#showConnLines").prop('checked', false);
				this.markersLayerStrategy.distance = 70;
				this.markersLayerStrategy.threshold = "";
				this.markersLayerStrategy.recluster();
			}
			this.toggleLineLayer();
			// this.unSpiderifyBsMarker();
		}

		/*
		This event is Triggered when Click on Map is done.
		@param e {Event Object} Mouse event
		Here, we closeInfoWindow. If infoWindow was present, just close window. Else, if no window was there, unSpiderify Markers too.
		 */
		this.mapClickEvent = function(e) {
			// console.log(e);
			// this.unSpiderifyBsMarker();
		}

		var oldFeature = "";
		this.removePopupWindow = function() {
			if(oldFeature) {
				ccpl_map.removePopup(oldFeature.popup);
				oldFeature.popup.destroy();
				oldFeature.popup = null;
			}
		}

		this.onFeatureSelect = function(e) {
			var infoWindowContent;
			// console.log(e.feature.attributes);
			if(e.feature.attributes && e.feature.attributes.pointType === "sector_Marker") {
				infoWindowContent = gmap_self.makeWindowContent(e.feature.attributes);
			} else {
				infoWindowContent = gmap_self.makeWindowContent(e.feature);
			}

			$("#infoWindowContainer").html(infoWindowContent);
			$("#infoWindowContainer").find('ul.list-unstyled.list-inline').remove();
			$("#infoWindowContainer").removeClass('hide');
			// var feature = e.feature;
			// oldFeature= feature;
			// var popup = new OpenLayers.Popup.FramedCloud("popup", feature.geometry.getBounds().getCenterLonLat(), null, infoWindowContent, null, true);
			// popup.autoSize= true;
			// popup.maxSize= new OpenLayers.Size(500, 350);
			// feature.popup = popup;
			// ccpl_map.addPopup(popup);
			// /*Update window content to show less items*/
			// gmap_self.show_hide_info();
		}
		this.markerClick= function(event) {
			var feature = event.feature;
			if(feature.cluster && feature.cluster.length) {
				var f = event.feature;
				if (f.cluster.length >= 2){
					//Click on Cluster
					clusterpoints = [];
					for(var i = 0; i<f.cluster.length; i++){
						clusterpoints.push(f.cluster[i].geometry);
					}
					var linestring = new OpenLayers.Geometry.LineString(clusterpoints);
					ccpl_map.zoomToExtent(linestring.getBounds());
				} else {
					var infoWindowContent = gmap_self.makeWindowContent(event.feature.cluster[0].attributes);
					$("#infoWindowContainer").html(infoWindowContent);
					$("#infoWindowContainer").find('ul.list-unstyled.list-inline').remove();
					$("#infoWindowContainer").removeClass('hide');
				}
			} else {
				var f = event.feature;
				if(f.attributes.type=== "base_station" && f.attributes.isMarkerSpiderfied === false) {
					spiderifyMarker(f, bsDevicesObj[f.attributes.name]);
				} else {

					var infoWindowContent = gmap_self.makeWindowContent(f.attributes);
					$("#infoWindowContainer").html(infoWindowContent);
					$("#infoWindowContainer").find('ul.list-unstyled.list-inline').remove();
					$("#infoWindowContainer").removeClass('hide');				
				}
			}
		}
		/*
		This function is triggered on click of Bs Marker
		 */
		this.bsMarkerClick = function(e, featureMarker) {
			var marker = featureMarker.cluster[0].attributes;
			if(marker.isSpiderfied) {
				global_this.spiderfyBsMarker(marker);
			} else {
				global_this.openInfoWindow(e, marker, wm_obj.data[marker.name]);
			}
		}
	/**
	 *
	 * End of Map Events Section
	 */
	
	/**
	 *
	 * Draw Feature Section
	 */	
		this.drawLivePollPolygon= function(element) {
			this.livePollingPolygonControl.activate();
		}
	/**
	 *
	 * End of Draw Feature Section
	 */

	/**
	 *
	 * Gis Performance Section
	 */
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
					sector_marker = wm_obj['devices']['sector_'+polygonSelectedDevices[i].attributes.sectorName]
				}

				if(ss_marker) {
					ss_marker.style.externalGraphic = ss_marker.attributes.originalIcon;
					
				} else if(sector_marker) {
					sector_marker.style.externalGraphic = sector_marker.attributes.originalIcon
					
				}
			}
			global_this.markersLayer.redraw();
			global_this.markerDevicesLayer.redraw();

			global_this.livePollFeatureLayer.removeAllFeatures();

			global_this.livePollingPolygonControl.activate();

			ccpl_map.addLayer(global_this.livePollFeatureLayer);

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

							global_this.drawLivePollPolygon();
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

			/*Reset marker icon*/
			for(var i=0;i<polygonSelectedDevices.length;i++) {

				var ss_marker = wm_obj['features'][polygonSelectedDevices[i].attributes.name],
					pointType = ss_marker.attributes.pointType,
					sector_marker = "";

				if(pointType === 'sub_station') {
					sector_marker = wm_obj['features'][polygonSelectedDevices[i].attributes.sector_ip];
				} else {
					sector_marker = wm_obj['devices']['sector_'+polygonSelectedDevices[i].attributes.sectorName]
				}

				if(ss_marker) {
					ss_marker.style.externalGraphic = ss_marker.attributes.originalIcon;
					
				} else if(sector_marker) {
					sector_marker.style.externalGraphic = sector_marker.attributes.originalIcon
					
				}
			}
			global_this.markersLayer.redraw();
			global_this.markerDevicesLayer.redraw();

			if(global_this.livePollingPolygonControl) {
				global_this.livePollingPolygonControl.deactivate();
				global_this.livePollFeatureLayer.destroyFeatures();
				ccpl_map.removeLayer(global_this.livePollFeatureLayer);
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

			/*Enable other buttons*/
			disableAdvanceButton("no");

			/*Enable 'Reset' button*/
			$("#resetFilters").button("complete");

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


		this.startPolling= function() {
			ccpl_map.addLayer(this.livePollFeatureLayer);
		}

		var polygon = "";
		this.livePollingPolygonAdded = function(e) {
			if(global_this.livePollingPolygonControl) {
				global_this.livePollingPolygonControl.deactivate();
			}
			polygon = e.feature;
			global_this.getMarkerInPolygon();
		}

		this.getMarkerInPolygon = function() {
			var allSS = pollableDevices;
			allSSIds = [];
			

			var selected_polling_technology = $("#polling_tech option:selected").text();

			for(var k=0;k<allSS.length;k++) {
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

			if(polygonSelectedDevices.length == 0) {
				
				if(global_this.livePollingPolygonControl) {
					global_this.livePollingPolygonControl.deactivate();
				}
				
				if(polygon) {
					/*Remove the current polygon from the map*/
					global_this.livePollFeatureLayer.removeAllFeatures();
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
					global_this.livePollFeatureLayer.removeAllFeatures();
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
					// url : base_url+"/"+"device/lp_bulk_data/?ts_template="+selected_lp_template+"&devices="+JSON.stringify(allSSIds),
					url : base_url+"/"+"static/services.json",
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
console.log(ss_marker);
										ss_marker.style.externalGraphic = newIcon;
										global_this.markersLayer.drawFeature(ss_marker);
									} else if(sector_marker) {
										sector_marker.style.externalGraphic = newIcon;
										global_this.markerDevicesLayer.drawFeature(sector_marker);
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
	 * @method show_previous_polled_icon
	 */
	this.show_previous_polled_icon_wmaps = function() {
		if(nav_click_counter > 0) {
			nav_click_counter--;
		}
		/*Remove 'text-info' class from all li's*/
		$(".deviceWellContainer div div ul li").removeClass("text-info");

		for(var i=0;i<polled_devices_names.length;i++) {

			var ss_marker = wm_obj['features'][polled_devices_names[i]],
				sector_marker = wm_obj['devices']['sector_'+polled_devices_names[i]],
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
				sector_Marker.style.externalGraphic = newIcon;
			}
			$("#pollVal_"+new_device_name+" li.fetchVal_"+new_device_name)[nav_click_counter-1].className = $("#pollVal_"+new_device_name+" li.fetchVal_"+new_device_name)[nav_click_counter-1].className+' text-info';
		}
		global_this.markersLayer.redraw();
		global_this.markerDevicesLayer.redraw();

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

			var ss_marker = wm_obj['features'][polled_devices_names[i]],
				sector_marker = wm_obj['devices']['sector_'+polled_devices_names[i]],
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
				sector_Marker.style.externalGraphic = newIcon;
			}
			$("#pollVal_"+new_device_name+" li.fetchVal_"+new_device_name)[nav_click_counter-1].className = $("#pollVal_"+new_device_name+" li.fetchVal_"+new_device_name)[nav_click_counter-1].className+' text-info';
		}

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
							// console.log(x[i].filteredLine);
							if(x[i].filteredLine) {
								x[i].style.display = 'block';
								linesFeaturesList.push(x[i]);
							}
						}
					}
				}
				global_this.linesLayer.removeAllFeatures();
				if(selectedValue) {
					global_this.linesLayer.addFeatures(linesFeaturesList);
				}
				global_this.linesLayer.redraw();
				previousValue= selectedValue;
			}
		}
		/*
		This function toggles all Station Markers size based on the Value selected in the dropdown.
		 */
		this.toggleIconSize = function() {

			global_this.markersLayerStrategy.recluster();
			// //Selected value of the icon size in the dropdown
			// var iconSizeSelected = $("#icon_Size_Select_In_Tools").val();

			// var size = new OpenLayers.Size(whiteMapSettings.size.medium.width, whiteMapSettings.size.medium.height);
			// var newSize= "";

			// if(iconSizeSelected=== "large") {
			// 	newSize = new OpenLayers.Size(size.w + 6, size.h + 9);
			// } else if (iconSizeSelected === "small") {
			// 	newSize = new OpenLayers.Size(size.w - 6, size.h - 9);
			// } else {
			// 	newSize = size;
			// }

			// global_this.markersLayerStrategy.deactivate();
			// for (var i=0; i<global_this.markersLayer.features.length; i++) {
			// 	var clusteredFeatures = global_this.markersLayer.features[i];
			// 	if(clusteredFeatures && clusteredFeatures.cluster) {
			// 		for(var j=0; j< clusteredFeatures.cluster.length; j++) {
			// 			global_this.markersLayer.features[i].cluster[j].style.graphicWidth = newSize.w;
			// 			global_this.markersLayer.features[i].cluster[j].style.graphicHeight = newSize.h;
			// 			global_this.markersLayer.features[i].cluster[j].style.graphicYOffset = -newSize.h;
			// 			global_this.markersLayer.features[i].cluster[j].style.graphicXOffset = -newSize.w;						
			// 			// global_this.markersLayer.drawFeature(global_this.markersLayer.features[i].cluster[j]);
			// 		}
			// 	}

			// 	if(i === global_this.markersLayer.features.length-1) {
			// 		global_this.markersLayer.redraw();
			// 		global_this.markersLayerStrategy.activate();
			// 		global_this.markersLayerStrategy.recluster();
			// 	}
			// }
			//Loop through all markers
			// for (var i = 0; i < bs_ss_features_list.length; i++) {
			// 	resizeFeatures(newScale, bs_ss_features_list[i]);
			// 	console.log(bs_ss_features_list[i]);
			// 	if(i === bs_ss_features_list.length -1) {
			// 		global_this.markersLayer.redraw();					
			// 	}
			// }
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
	 * Search and Filter Function
	 */	

		/*
		This function is triggered when Reset Filter is done.
		Select empty value in the Select2 boxes, update filter_data variable and reset basic filters too.
		 */
		this.resetAdvanceFilter = function() {

			//reset filters
			wmAdvanceFilterClass.resetFilter();

			//set adAdvFilter = 0
			hasAdvFilter = 0;

			//update page status
			get_page_status();
		}

		/*
		 * This function is triggered when Cancel Filter is done.
		 */
		this.hideAdvanceFilter= function() {

			//remove advance filter content
			wmAdvanceFilterClass.destroyAdvanceFilter();
		}

		/*
		 * This function is triggered when Apply Advance Filter is triggered.
		 * Here, we check for the values selected in the Multibox and filter result according to it.
		 */
		
		this.applyAdvanceFilter = function(appliedFilterData) {

			data_for_filter_wmap= [];

			//set data for filter
			data_for_filter_wmap = appliedFilterData.data_for_filters;

			//remove features from markersLayer and add filteredFeatures
			this.markersLayer.removeAllFeatures();
			this.markersLayer.addFeatures(appliedFilterData.filtered_Features);
			filtered_Features.markers = appliedFilterData.filtered_Features;

			// console.log(filtered_Features.markers);
			
			//remove lines from linesLayer and add filteredLine
			this.linesLayer.removeAllFeatures();
			this.linesLayer.addFeatures(appliedFilterData.line_Features);
			filtered_Features.lines = appliedFilterData.line_Features;

			//remove sectors from sectorsLayer and add filtered sectors
			this.sectorsLayer.removeAllFeatures();
			this.sectorsLayer.addFeatures(appliedFilterData.sector_Features);
			filtered_Features.sectors = appliedFilterData.sector_Features;
			
			//set master data for search to data_to_filter
			wmAdvanceSearchClass.setMasterData(data_for_filter_wmap);
			
			//rescluster the strategy
			global_this.markersLayerStrategy.recluster();

			//update page status
			get_page_status();

			this.toggleLineLayer();

			/*Enable Reset Button*/
			$("#resetFilters").button("complete");
		}

		/*
		This function reset Advance Search
		 */
		this.resetAdvanceSearch = function() {

			//reset adv class
			// wmAdvanceSearchClass.resetAdvanceSearch();

			//set hasAdvSearch = 0
			// hasAdvSearch = 0;

			//remove search markers
			this.searchMarkerLayer.removeAllFeatures();

			//update get status
			// get_page_status();
		}

		/*
		This function applies Advance Search
		 */
		this.applyAdvanceSearch = function() {
			//apply adv Search
			wmAdvanceSearchClass.applyAdvanceSearch(function() {
				hideSpinner();
			});
		}

		/*
		This function populate Advance Search Dropdowns
		 */
		this.showAdvanceSearch = function() {
			var advSearchData= [];
			var bsNameData = { 'element_type':'multiselect', 'field_type':'string', 'key':'name', 'title':'Bs Name', 'values':[] };
			//Loop through the technology for the devices
			if (bs_name.length) {
				for (var i = 0; i < bs_name.length; i++) {
					//bs_name[i] is a valid value
					if (bs_name[i]) {
						bsNameData.values.push(bs_name[i]);
					}
				}
			}
			advSearchData.push(bsNameData);

			var ipData = { 'element_type':'multiselect', 'field_type':'string', 'key':'ip', 'title':'IP', 'values':[] };
			//Loop through the vendor for the devices
			if (ip.length) {
				for (var i = 0; i < ip.length; i++) {
					//ip[i] is a valid value
					if (ip[i]) {
						ipData.values.push(ip[i]);
					}
				}
			}
			advSearchData.push(ipData);

			var cktIdData = { 'element_type':'multiselect', 'field_type':'string', 'key':'cktId', 'title':'Circuit ID', 'values':[] };
			//Loop through the cktId for the devices
			if (cktId.length) {
				for (var i = 0; i < cktId.length; i++) {
					//cktId[i] is a valid value
					if (cktId[i]) {
						cktIdData.values.push(cktId[i]);
					}
				}
			}
			advSearchData.push(cktIdData);

			var cityData = { 'element_type':'multiselect', 'field_type':'string', 'key':'city', 'title':'City', 'values':[] }
			//Loop through the city for the devices
			if (city.length) {
				for (var i = 0; i < city.length; i++) {
					//city[i] is a valid value
					if (city[i]) {
						cityData.values.push(city[i]);
					}
				}
			}
			advSearchData.push(cityData);
			wmAdvanceSearchClass.createAdvanceSearchMarkup(advSearchData);
		}

		this.hideAdvanceSearch = function() {
			
			wmAdvanceSearchClass.destroyAdvanceSearch();
		}
		/*
		This function applies Basic Filter
		 */
		this.applyBasicFilter = function() {

			var filterArray = gmap_self.makeFiltersArray('white_background');

			var technologyValue = $("#technology").val(), vendorValue = $("#vendor").val(), stateValue = $("#state").val(), cityValue = $("#city").val();
			
			global_this.markersLayer.removeAllFeatures();
			global_this.linesLayer.removeAllFeatures();
			global_this.sectorsLayer.removeAllFeatures();

			if(technologyValue == "" && vendorValue == "" && stateValue == "" && cityValue == "") {

				global_this.markersLayer.addFeatures(filtered_Features.markers);
				global_this.linesLayer.addFeatures(filtered_Features.lines);
				global_this.sectorsLayer.addFeatures(filtered_Features.sectors);
				global_this.markersLayerStrategy.recluster();

				return;
			} else {
				var basic_filtered_features = {markers: [], lines: [], sectors: []}, i= 0;
				
				bsLoop: for(i=0; i< data_for_filter_wmap.length; i++) {
					var bs = data_for_filter_wmap[i], j=0, k=0;
					if(technologyValue != "") {
						var bsTechnologies = bs.sector_ss_technology;
						if(bsTechnologies) {
							bsTechnologies = $.trim(bsTechnologies.toLowerCase());
							technologyValue = $.trim(technologyValue.toLowerCase());
							if(bsTechnologies.indexOf(technologyValue) == -1) {
								continue bsLoop;
							}
						}
					} else {
						continue bsLoop;
					}

					if(vendorValue != "") {
						var bsVendors = bs.sector_ss_vendor;
						if(bsVendors) {
							bsVendors = $.trim(bsVendors.toLowerCase());
							vendorValue = $.trim(vendorValue.toLowerCase());
							if(bsVendors.indexOf(vendorValue) == -1) {
								continue bsLoop;
							}
						}
					} else {
						continue bsLoop;
					}

					if(stateValue != "") {
						var bsState = bs.data.state;
						if(bsState) {
							bsState = $.trim(bsState.toLowerCase());
							stateValue = $.trim(stateValue.toLowerCase());
							if(bsState.indexOf(stateValue) == -1) {
								continue bsLoop;
							}
						}
					} else {
						continue bsLoop;
					}

					if(cityValue != "") {
						var bsCity = bs.data.city;
						if(bsCity) {
							bsCity = $.trim(bsCity.toLowerCase());
							cityValue = $.trim(cityValue.toLowerCase());
							if(bsCity.indexOf(cityValue) == -1) {
								continue bsLoop;
							}
						}
					} else {
						continue bsLoop;
					}

					basic_filtered_features.markers.push(wm_obj.features[bs.name]);

					for(j=0; j< bs.data.param.sector.length; j++) {
						var bsSector = bs.data.param.sector[j];
						if($.trim(bsSector.technology.toLowerCase()) == $.trim(technologyValue.toLowerCase())) {
							if(wm_obj.sectors[bsSector.sector_configured_on_device]) {
								basic_filtered_features.sectors.push(wm_obj.sectors[bsSector.sector_configured_on_device]);
							}
							if(wm_obj.lines[bsSector.sector_configured_on_device]) {
								basic_filtered_features.lines.push(wm_obj.lines[bsSector.sector_configured_on_device]);
							}

							for(k=0; k< bsSector.sub_station.length; k++) {
								var sub_Station = bsSector.sub_station[k];
								basic_filtered_features.markers.push(wm_obj.features[sub_Station.name]);
							}
						}
					}
				}

				global_this.markersLayer.addFeatures(basic_filtered_features.markers);	
				global_this.linesLayer.addFeatures(basic_filtered_features.lines);
				global_this.sectorsLayer.addFeatures(basic_filtered_features.sectors);
				global_this.markersLayerStrategy.recluster();
			}
		}

		/*
		This function populates basic filter dropdowns
		 */
		this.populateBasicFilterDropdowns = function() {
			gmap_self.getBasicFilters();
		}

		/*
		Reset Filters
		 */
		this.resetBasicFilter = function() {
			$("#technology").val('');
			$("#vendor").val('');
			$("#state").val('');
			$("#city").val('');

			this.applyBasicFilter();
		}
	/**
	 * End of Search and Filter Functions
	 */	

	/**
	 *
	 * Plotting Functions
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
					originalIcon: base_url+"/static/img/icons/bs.png", 
					child_ss: markerData.data.param.sector,
					original_sectors: markerData.data.param.sector,
					dataset: markerData.data.param.base_station, 
					bhInfo: markerData.data.param.backhual, 
					bs_name: name,
					filter_data: {"bs_name": markerData.name},
					antenna_height: markerData.data.antenna_height,
					ptLat: lat, 
					ptLon: lon, 
					pointType: type,
					markerType: 'BS',
					isMarkerSpiderfied: false
				}



				var marker = global_this.createOpenLayerVectorMarker(size, icon, lon, lat, bsMarkerCustomInfo);
				wm_obj.features[name] = marker;

				bs_ss_features_list.push(marker);
				
				var deviceIDArray= [];
				//base station devices loop
				var total_angle = 360, devices_length = markerData.data.param.sector.length, angleOnWhichDeviceIconToPlace = Math.floor(total_angle / devices_length), current_angle = 0;
				//Loop through the bs devices
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
					var sectorRadius = device.radius,
						rad = 4;
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
							// wm_obj.sectors[device.sector_configured_on_device] = plottedSector;
							wm_obj.sectors["poly_"+device.sector_configured_on+"_"+rad+"_"+device.azimuth_angle+"_"+device.beam_width] = plottedSector;
							global_this.sectorsLayer.addFeatures([plottedSector]);

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

							var perf_obj = { "performance_paramter" : "N/A", "performance_value" : "N/A", "frequency" : "N/A", "pl" : "N/A" };
							
							var deviceAdditionalInfo = {
								ptLat: lat,
								ptLon: lon,
								originalIcon:  base_url+"/"+device.markerUrl,
								icon: base_url+'/static/img/i/1x1.png',
								pointType 		 	: 'sector_Marker',
								technology: device.technology,
								vendor 				: device.vendor,
								deviceExtraInfo 	: device.info,
								deviceInfo 			: device.device_info,
								poll_info 			: [],
								sectorName: device.sector_configured_on,
								device_name : device.sector_configured_on_device,
								name: name,
								filter_data 	    : {"bs_name" : name, "sector_name" : device.sector_configured_on},
								sector_lat  		: startEndObj["startLat"],
								sector_lon  		: startEndObj["startLon"],
								type: "base_station_device",
								perf_data_obj  		: perf_obj,
								antenna_height 		: device.antenna_height
							}

							if(!bsDevicesObj[name]) {
								bsDevicesObj[name]= [];
							}

							//Create deviceMarker
							var deviceMarker = global_this.createOpenLayerVectorMarker(device_marker_size, deviceAdditionalInfo.icon, lon, lat, deviceAdditionalInfo);
							// global_this.markerDevicesLayer.addFeatures(deviceMarker);
							bsDevicesObj[name].push(deviceMarker);


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

						var perf_obj = { "performance_paramter" : "N/A", "performance_value" : "N/A", "frequency" : "N/A", "pl" : "N/A" };

						var subStationAdditionalInfo = {
							ptLat: sub_station.data.lat, ptLon: sub_station.data.lon, 
							technology: device.technology,
							pointType: "sub_station",
							type: "sub_station",
							dataset: sub_station.data.param.sub_station,
							originalIcon: base_url+"/"+sub_station.data.markerUrl,
							icon: base_url+"/"+sub_station.data.markerUrl,
							bhInfo: [],
							poll_info: [],
							antenna_height: sub_station.data.antenna_height,
							name: sub_station.name,
							bs_name: name,
							bs_sector_device :  device.sector_configured_on_device,
							filter_data 	 :  {"bs_name" : name, "sector_name" : device.sector_configured_on, "ss_name" : sub_station.name},
							device_name 	 : 	sub_station.device_name,
							bs_sector_device :  device.sector_configured_on_device,
							ss_ip 	 		 : 	sub_station.data.substation_device_ip_address,
							sector_ip 		 :  device.sector_configured_on,
							perf_data_obj: perf_obj
						}

						var sub_station_lon = sub_station.data.lon;
						var sub_station_lat = sub_station.data.lat;
						var sub_station_icon = base_url+"/"+sub_station.data.markerUrl;
						var sub_station_name = sub_station.name

						//Create marker
						sub_station_marker = global_this.createOpenLayerVectorMarker(device_marker_size, sub_station_icon, sub_station_lon, sub_station_lat, subStationAdditionalInfo);
						wm_obj.features[sub_station.name] = sub_station_marker;
						
						bs_ss_features_list.push(sub_station_marker);

						 /*Push SS marker to pollableDevices array*/
						pollableDevices.push(sub_station_marker);

						var ss_info = {},
							base_info = {};
						startEndObj["nearEndLat"] = markerData.data.lat;
						startEndObj["nearEndLon"] = markerData.data.lon;

						startEndObj["endLat"] = sub_station.data.lat;
						startEndObj["endLon"] = sub_station.data.lon;
						// console.log(startEndObj);
						/*Sub station info Object*/
						ss_info["info"] = sub_station.data.param.sub_station;

						ss_info["antenna_height"] = sub_station.data.antenna_height;
						/*Link color object*/
						var linkColor = sub_station.data.link_color;

						base_info["info"] = markerData.data.param.base_station;
						base_info["antenna_height"] = markerData.data.antenna_height;

						if(sub_station.data.show_link == 1) {

							var ss_info_obj = "",
							ss_height = 40;

							if(sub_station.data.param.sub_station != undefined || sub_station.data.param.sub_station == "") {
								ss_info_obj = sub_station.data.param.sub_station.info;
								ss_height = sub_station.data.param.sub_station.antenna_height;
							} else {
								ss_info_obj = "";
								ss_height = 40;
							}

							var bs_info_obj = "",
							bs_height = 40;
							if(markerData.data.param.base_station != undefined || markerData.data.param.base_station == "") {
								bs_info_obj = markerData.data.param.base_station.info;
								bs_height = markerData.data.param.base_station.antenna_height;
							} else {
								bs_info_obj = "";
								bs_height = 40;
							}

							var sect_height="";
							if (sect_height == undefined || sect_height == ""){
								sect_height = 47;
							}
							var lineAdditionalInfo = {
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
								ss_lat: sub_station_lat,
								bs_lat 			: startEndObj.startLat,
								bs_lon 			: startEndObj.startLon,
								ss_lon: sub_station_lon,
								filter_data 	: {"bs_name" : name, "sector_name" : device.sector_configured_on, "ss_name" : sub_station_name},
								filteredLine: true
							}

							// console.log(startEndObj);
							var line = global_this.plotLines_wmap(startEndObj.startLon,startEndObj.startLat, startEndObj.endLon,startEndObj.endLat, linkColor, lineAdditionalInfo);

							filtered_Features.lines.push(line);
							global_this.linesLayer.addFeatures([line]);
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
									global_this.markersLayer.addFeatures(filtered_Features.markers);

									//activate cluster strategy
									global_this.markersLayerStrategy.activate();

									//initiate advance filter class
									wmAdvanceFilterClass = new WmAdvanceFilter(bs_data_list, wm_obj.features, wm_obj.features, bs_ss_features_list, cktLinesBsObj, sectorsBsObj);
									
									//initiate advance search class
									wmAdvanceSearchClass = new WmAdvanceSearch(data_for_filter_wmap);

									//populate basic filter dropdown
									global_this.populateBasicFilterDropdowns();
									// global_this.linesLayer.redraw();

									//hide linesLayer by default.
									global_this.linesLayer.display(false);

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
	 * End of Plotting Functions
	 */


	/*
	 *
	 * Utils Section
	 */
		
		/*
		This function removes all Features from marker, line and sector layers.
		 */
		this.hideAllFeatures = function() {
			global_this.markersLayer.removeAllFeatures();
			global_this.linesLayer.removeAllFeatures();
			global_this.sectorsLayer.removeAllFeatures();
		}

		/*
		This function shows all Filtered Features for marker, line and sector layers.
		 */
		this.showAllFeatures = function() {

			global_this.markersLayer.addFeatures(bs_ss_features_list);
			global_this.linesLayer.addFeatures(main_lines_sectors_features_wmaps.lines);
			global_this.sectorsLayer.addFeatures(main_lines_sectors_features_wmaps.sectors);
			global_this.markersLayerStrategy.recluster();
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


	/*
	* Constructor for White Map Class.
	* * Starts building of White Maps
	* */
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