var ccpl_map, base_url;
var hasAdvFilter = 0;
/*Set the base url of application for ajax calls*/
if(window.location.origin) {
	base_url = window.location.origin;
} else {
	base_url = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
}
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

		var main_devices_data_feature_obj_wmaps = {'features': {}, 'data': {}, 'devices': {}};
		//Variable to Store JSON data of Markers
		var main_devices_data_wmaps = [], data_for_filter = [];
		//Variable to Store All Markers
		var main_stations_features_wmaps= [], filtered_features = [];
		var main_devices_marker_features_wmaps = [], filtered_lines_main_devices_marker_features_wmaps= [];
		var main_lines_sectors_features_wmaps= {'lines': [], 'sectors': []}, filtered_lines_sectors_features = [], main_line_sectors_features_obj_wmaps = {'lines': {}, 'sectors': {}};

		var state_city_obj= {}, all_cities_array= [], tech_vendor_obj= {}, all_vendor_array= [], sectorMarkerConfiguredOn= [], sectorMarkersMasterObj = {};

		var pollableDevices = [];
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
				global_this.markerDevicesLayer.removeAllFeatures();
				markerSpiderfied= "";				
			}
		}

		this.spiderfyBsMarker= function(markername) {
			this.unSpiderifyBsMarker();
			var bs_marker= main_devices_data_feature_obj_wmaps.features[markername];
			var bs_devices = deviceMarkerObj[markername];
			var map_Zoom_Level = ccpl_map.getZoom();
			devices_Marker_On_Map= [];
			if(bs_devices) {
				//Loop through the devices
				for (var i = 0; i < bs_devices.length; i++) {
					// console.log(bs_devices[i]);
					bs_devices[i].style.externalGraphic = bs_devices[i].attributes.defaultIcon;

					bs_devices[i].move(new OpenLayers.LonLat(bs_devices[i].attributes.ptLon, bs_devices[i].attributes.ptLat));
					devices_Marker_On_Map.push(bs_devices[i]);
					if(i=== bs_devices.length-1) {
						global_this.markerDevicesLayer.removeAllFeatures();
						global_this.markerDevicesLayer.addFeatures(devices_Marker_On_Map);
						global_this.markerDevicesLayer.redraw();
					}
				}
				bs_marker.isSpiderfied = false;
				markerSpiderfied= bs_marker;
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

		this.mapZoomChangeEvent = function() {
			if(ccpl_map.getZoom() > whiteMapSettings.zoomLevelAfterLineAppears) {
				var selectedValue = $("#showConnLines").prop('checked', true);
			} else {
				var selectedValue = $("#showConnLines").prop('checked', false);
			}
			this.toggleLineLayer();
		}

		/*
		This event is Triggered when Click on Map is done.
		@param e {Event Object} Mouse event
		Here, we closeInfoWindow. If infoWindow was present, just close window. Else, if no window was there, unSpiderify Markers too.
		 */
		this.mapClickEvent = function(e) {
			console.log('Click on Map');
			//Close Window
			var closeInfoWindow= this.closeInfoWindow();
			//If no window was there
			if(closeInfoWindow=== 'no window') {
				//Unspiderify Bs Markers
				this.unSpiderifyBsMarker();
			}
		}

		var oldFeature = "";
		this.onFeatureUnselect = function() {
			if(oldFeature) {
				ccpl_map.removePopup(oldFeature.popup);
				oldFeature.popup.destroy();
				oldFeature.popup = null;
			}
		}

		this.onFeatureSelect = function(e) {
			this.onFeatureUnselect();
			var infoWindowContent;
			if(e.feature.attributes && e.feature.attributes.pointType === "sector_Marker") {
				infoWindowContent = gmap_self.makeWindowContent(e.feature.attributes);
			} else {
				infoWindowContent = gmap_self.makeWindowContent(e.feature);
			}

			var feature = e.feature;
			oldFeature= feature;
			var popup = new OpenLayers.Popup.FramedCloud("popup", feature.geometry.getBounds().getCenterLonLat(), null, infoWindowContent, null, true);
			popup.autoSize= true;
			popup.maxSize= new OpenLayers.Size(500, 350);
			feature.popup = popup;
			ccpl_map.addPopup(popup);
			/*Update window content to show less items*/
			gmap_self.show_hide_info();
		}

		this.markerClick= function(event) {

			if(event.feature.cluster.length) {
				if(event.feature.cluster.length === 1 && event.feature.cluster[0].attributes.pointType=== "base_station" && !markerSpiderfied) {
					this.unSpiderifyBsMarker();
					this.spiderfyBsMarker( event.feature.cluster[0].attributes.name);
					markerSpiderfied = event.feature.cluster[0];
					event.feature.cluster[0].attributes.isSpiderfied = false;
				} else {
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
						this.onFeatureUnselect();
						var infoWindowContent = gmap_self.makeWindowContent(event.feature.cluster[0].attributes);

						var feature = event.feature;
						oldFeature= feature;
						var popup = new OpenLayers.Popup.FramedCloud("popup",
							feature.geometry.getBounds().getCenterLonLat(),
							null,
							infoWindowContent,
							null,
							true
							);
					popup.autoSize= true;
					popup.maxSize= new OpenLayers.Size(300, 350);
					feature.popup = popup;
					ccpl_map.addPopup(popup);
					/*Update window content to show less items*/
					gmap_self.show_hide_info();
					// popup.setSize(new OpenLayers.Size(500, 400));
						//Click on Marker
						// global_this.bsMarkerClick(event, f);
					}
				}
				
			} else {
				console.log('what happened');
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
				global_this.openInfoWindow(e, marker, main_devices_data_feature_obj_wmaps.data[marker.name]);
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

			$.ajax({
				url : base_url+"/"+"device/filter/",
				success : function(result) {
					var techData = JSON.parse(result).data.objects.technology.data;
					/*Populate technology dropdown*/
					var techOptions = "<option value=''>Select Technology</option>";
					$.grep(techData,function(tech) {
						if(technology.indexOf(tech.value) >= 0) {
							techOptions += "<option value='"+tech.id+"'>"+tech.value.toUpperCase()+"</option>";
						}
					});
					$("#polling_tech").html(techOptions);
				},
				error : function(err) {
					// console.log(err.statusText);
				}
			});
		}

		this.fetchPollingTempate = function() {
			var selected_technology = $("#polling_tech").val();
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

	    					ccpl_map.addLayer(global_this.livePollFeatureLayer);

	    					global_this.drawLivePollPolygon();
	    				}
	    			}
	    		});
	    	} else {
	    		alert("Please select technology.");
	    	}
		}
		
		this.stopPolling= function() {
			// if(this.livePollingPolygonControl) {
			this.livePollingPolygonControl.deactivate();
			this.livePollFeatureLayer.destroyFeatures();
			ccpl_map.removeLayer(this.livePollFeatureLayer);
			// }

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
		}
		this.startPolling= function() {
			ccpl_map.addLayer(this.livePollFeatureLayer);
		}
		var polygon = "";
		this.livePollingPolygonAdded = function(e) {
			polygon = e.feature;
			this.livePollingPolygonControl.deactivate();
			global_this.getMarkerInPolygon();
		}
		this.getMarkerInPolygon = function() {

			var allSS = ssAndDeviceArray;
			var allSSIds = [];
			var polygonSelectedDevices = [];
			var selected_polling_technology = $("#polling_tech option:selected").text();
console.log(selected_polling_technology);
			for(var k=0;k<allSS.length;k++) {
				if(polygon) {
					// console.log(allSS[k].attributes.ptLon, allSS[k].attributes.ptLat);
					if(displayBounds(polygon, allSS[k].attributes.ptLon, allSS[k].attributes.ptLat) === 'in') {
						if($.trim(allSS[k].attributes.technology.toLowerCase()) == $.trim(selected_polling_technology.toLowerCase())) {
// console.log($.trim(allSS[k].attributes.technology.toLowerCase()));
							if($.trim(allSS[k].attributes.technology.toLowerCase()) == "ptp" || $.trim(allSS[k].attributes.technology.toLowerCase()) == "p2p") {
								// console.log(allSS[k]);
								if(allSS[k].attributes.name && (allSSIds.indexOf(allSS[k].attributes.name) == -1)) {
									allSSIds.push(allSS[k].attributes.device_name);
									polygonSelectedDevices.push(allSS[k]);
								}
							} else {
								if(allSS[k].pointType == 'sub_station') {
									// console.log(allSS[k]);
									if(allSS[k].attributes.name && (allSSIds.indexOf(allSS[k].attributes.name) == -1)) {
										allSSIds.push(allSS[k].attributes.device_name);
										polygonSelectedDevices.push(allSS[k]);
									}
								}
							}
						}
					}
				}
			}
console.log(allSSIds);
console.log(polygonSelectedDevices);
			// for(var i=0; i< ssAndDeviceArray.length; i++) {
			// 	console.log(ssAndDeviceArray[i]);
			// 	if(polygon){
			// 		if(displayBounds(polygon, ssAndDeviceArray[i].attributes.lon, ssAndDeviceArray[i].attributes.lat) === 'in') {
			// 			var deviceTechnology = ssAndDeviceArray[i].attributes.technology;
			// 			var selected_technology = $("#polling_tech").val();
			// 			if($.trim(deviceTechnology.toLowerCase()) === $.trim(selected_technology.toLowerCase())) {
			// 				var deviceName = ssAndDeviceArray[i].attributes.name;
			// 				var ssMarkers = main_devices_data_feature_obj_wmaps.features[deviceName];
			// 				for(var j=0; j< )
			// 				// main_devices_data_feature_obj_wmaps.features
			// 				console.log(ssAndDeviceArray[i]);
			// 			}
			// 		}
			// 	} else {
			// 		alert("no Polygon created.");
			// 	}
			// }

			// for(var i=0; i< ss_features_master_array.length; i++) {
			// 	if(polygon){
			// 		if(displayBounds(polygon, ss_features_master_array[i].attributes.lon, ss_features_master_array[i].attributes.lat) === 'in') {
			// 			var deviceTechnology = ss_features_master_array[i].attributes.technology;
			// 			var selected_technology = $("#polling_tech").val();
			// 			if($.trim(deviceTechnology.toLowerCase()) === $.trim(selected_technology.toLowerCase())) {
			// 				console.log(ss_features_master_array[i]);
			// 			}
			// 		}
			// 	} else {
			// 		alert("no Polygon created.");
			// 	}
			// }
		}
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
							console.log(x[i].filteredLine);
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
			//Selected value of the icon size in the dropdown
			var iconSizeSelected = $("#icon_size_select").val();

			var size = new OpenLayers.Size(20, 28);
			var newSize= "";

			if(iconSizeSelected=== "large") {
				newSize = new OpenLayers.Size(size.w + 8, size.h + 8);
			} else if (iconSizeSelected === "small") {
				newSize = new OpenLayers.Size(size.w - 8, size.h - 8);
			} else {
				newSize = size;
			}
			//Loop through all markers
			for (var i = 0; i < main_stations_features_wmaps.length; i++) {
				//Set icon marker size with newSize
				main_stations_features_wmaps[i].icon.setSize(newSize);
			}
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
	 * Advance Search and Filter
	 */	
		this.updateStationMarker = function(base_station, newBaseStationObject, callback) {
			callback();
		}
		/*
		This function show Bs Marker
		 */
		this.showStationMarker = function(base_station) {
			var bs_name = base_station.name;
			var bs_marker = main_devices_data_feature_obj_wmaps.features[bs_name];
			bs_marker.style.display= '';
			var devicesMarkers = deviceMarkerObj[bs_name];
			if (devicesMarkers) {
				for (var i = 0; i < devicesMarkers.length; i++) {
					var deviceMarker = devicesMarkers[i];
					var deviceName = deviceMarker.name;
					var sub_stations = main_devices_data_feature_obj_wmaps.features[deviceName];
					if (sub_stations) {
						for (var j = 0; j < sub_stations.length; j++) {
							var sub_station = sub_stations[j];
							sub_station.style.display= '';
							// sub_station.display(true);
						}
					}

					var lines = cktLinesObj[deviceName];
					if (lines) {
						for (var j = 0; j < lines.length; j++) {
							var line = lines[j];
							line.style.display = 'block'
						}
						global_this.linesLayer.redraw();
					}

					var sectors = sectorsObj[deviceName];
					if (sectors) {
						for (var j = 0; j < sectors.length; j++) {
							var sector = sectors[j];
							sector.style.display = 'block';
						}
						global_this.sectorsLayer.redraw();
					}
				}
			}
			global_this.markersVectorLayer.redraw();
		}
		/*
		This function hides BS marker
		 */
		var markersToHide= [];
		this.hideStationMarkers = function(base_station) {
			var bs_name = base_station.name;
			var bs_marker = main_devices_data_feature_obj_wmaps.features[bs_name];
			global_this.markersVectorLayer.destroyFeatures([bs_marker]);
			bs_marker.style.display = 'none';
			// bs_marker.style = { visibility: 'hidden' };
			// // bs_marker.display(false);
			// var devicesMarkers = deviceMarkerObj[bs_name];
			// if (devicesMarkers) {
			// 	for (var i = 0; i < devicesMarkers.length; i++) {
			// 		var deviceMarker = devicesMarkers[i];
			// 		// deviceMarker.display(false);
			// 		var deviceName = deviceMarker.name;
			// 		var sub_stations = main_devices_data_feature_obj_wmaps.features[deviceName];
			// 		if (sub_stations) {
			// 			for (var j = 0; j < sub_stations.length; j++) {
			// 				var sub_station = sub_stations[j];
			// 				sub_station.style = { visibility: 'hidden' };
			// 			}
			// 		}

			// 		var lines = cktLinesObj[deviceName];
			// 		if (lines) {
			// 			for (var j = 0; j < lines.length; j++) {
			// 				var line = lines[j];
			// 				line.style.display = 'none'
			// 			}
			// 			global_this.linesLayer.redraw();
			// 		}

			// 		var sectors = sectorsObj[deviceName];
			// 		if (sectors) {
			// 			for (var j = 0; j < sectors.length; j++) {
			// 				var sector = sectors[j];
			// 				sector.style.display = 'none';
			// 			}
			// 			global_this.sectorsLayer.redraw();
			// 		}
			// 	}
			// }
			// global_this.markersVectorLayer.redraw();
		}
		/*
		This function is triggered when Reset Filter is done.
		Select empty value in the Select2 boxes, update filter_data variable and reset basic filters too.
		 */
		this.resetAdvanceFilter = function() {
			// this.resetBasicFilter();

			wmAdvanceFilterClass.resetAdvanceFilter();
			hasAdvFilter = 0;
		}

		this.hideAdvanceFilter= function() {
			wmAdvanceFilterClass.destroyAdvFilterHtml();
		}
		/*
		This function is triggered when Apply Advance Filter is triggered.
		Here, we check for the values selected in the Multibox and filter result according to it.
		 */
		var filteredFeatures = {markers: [], lines: [], sectors: []};
		this.applyAdvanceFilter = function() {
			this.resetBasicFilter();
			data_for_filter= [];
			var appliedFilter = wmAdvanceFilterClass.applyAdvFilter();
			data_for_filter = appliedFilter.data_for_filter;

			this.markersVectorLayer.removeAllFeatures();
			this.markersVectorLayer.addFeatures(appliedFilter.filtered_Features);
			filteredFeatures.markers = appliedFilter.filtered_Features;

			this.linesLayer.removeAllFeatures();
			this.linesLayer.addFeatures(appliedFilter.line_Features);
			filteredFeatures.lines = appliedFilter.line_Features;

			this.sectorsLayer.removeAllFeatures();
			this.sectorsLayer.addFeatures(appliedFilter.sector_Features);
			filteredFeatures.sectors = appliedFilter.sector_Features;

			
			wmAdvanceSearchClass.setMasterData(data_for_filter);
			
			global_this.markersLayerStrategy.recluster();

			hasAdvFilter= 1;
			get_page_status();
		}

		/*
		This function populates AdvanceFilter Multiselect dataItems
		 */
		this.showAdvanceFilter = function() {
			var advFilterData= [];
			var technologyData = { 'element_type':'multiselect', 'field_type':'string', 'key':'technology', 'title':'Technology', 'values':[] };
			//Loop through the technology for the devices
			if (technology.length) {
				for (var i = 0; i < technology.length; i++) {
					//technology[i] is a valid value
					if (technology[i]) {
						technologyData.values.push(technology[i]);
					}
				}
			}
			advFilterData.push(technologyData);

			var vendorData = { 'element_type':'multiselect', 'field_type':'string', 'key':'vendor', 'title':'Vendor', 'values':[] };
			//Loop through the vendor for the devices
			if (vendor.length) {
				for (var i = 0; i < vendor.length; i++) {
					//vendor[i] is a valid value
					if (vendor[i]) {
						vendorData.values.push(vendor[i]);
					}
				}
			}
			advFilterData.push(vendorData);

			var cityData = { 'element_type':'multiselect', 'field_type':'string', 'key':'city', 'title':'City', 'values':[] };
			//Loop through the city for the devices
			if (city.length) {
				for (var i = 0; i < city.length; i++) {
					//city[i] is a valid value
					if (city[i]) {
						cityData.values.push(city[i]);
					}
				}
			}
			advFilterData.push(cityData);

			var stateData = { 'element_type':'multiselect', 'field_type':'string', 'key':'state', 'title':'State', 'values':[] }
			//Loop through the state for the devices
			if (state.length) {
				for (var i = 0; i < state.length; i++) {
					//state[i] is a valid value
					if (state[i]) {
						stateData.values.push(state[i]);
					}
				}
			}
			advFilterData.push(stateData);
			wmAdvanceFilterClass.prepareAdvFilterHtml(advFilterData);
		}
		/*
		This function reset Advance Search
		 */
		var search_Markers = [];
		this.resetAdvanceSearch = function() {
			wmAdvanceSearchClass.resetAdvanceSearch();	
			if($("#gis_search_status_txt").length) {
				$("#gis_search_status_txt").remove();
			}		
			//hide search markers here			
		}
		/*
		This function applies Advance Search
		 */
		this.applyAdvanceSearch = function() {
			wmAdvanceSearchClass.applyAdvanceSearch();
			hideSpinner();
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
			wmAdvanceSearchClass.prepareAdvSearchHtml(advSearchData);
		}

		this.hideAdvanceSearch = function() {
			wmAdvanceSearchClass.destroyAdvSearchHtml();
		}
		/*
		This function applies Basic Filter
		 */
		this.applyBasicFilter = function() {
			var technologyValue = $("#technology").val();
			var vendorValue = $("#vendor").val();
			var stateValue = $("#state").val();
			var cityValue = $("#city").val();
			
			var filtered_lines_features= [], filtered_stations_features = [], filtered_sector_features = [];

			stationsLoop: for (var i = 0; i < data_for_filter.length; i++) {
				var markerData = data_for_filter[i];
				if (technologyValue === "" && vendorValue === "" && stateValue === "" && cityValue === "") {
					filtered_stations_features = main_stations_features_wmaps;
					filtered_lines_features = main_lines_sectors_features_wmaps.lines;
					filtered_sector_features = main_lines_sectors_features_wmaps.sectors;
					
					// global_this.applyAdvanceFilter();
					break stationsLoop;
				} else {
					if(technologyValue !== "") {
						var baseStationTechnology = markerData.sector_ss_technology;
						if(baseStationTechnology) {
							baseStationTechnology= $.trim(baseStationTechnology.toLowerCase());
							technologyValue = $.trim(technologyValue.toLowerCase());
							if(baseStationTechnology.indexOf(technologyValue) === -1) {
								continue stationsLoop;
							}
						} else {
							continue stationsLoop;
						}
					}

					if (vendorValue !== "") {
						var baseStationVendor = markerData.sector_ss_vendor;
						if(baseStationVendor) {
							baseStationVendor= $.trim(baseStationVendor.toLowerCase());
							vendorValue = $.trim(vendorValue.toLowerCase());
							if (baseStationVendor.indexOf(vendorValue) === -1) {
								continue stationsLoop;
							}
						} else {
							continue stationsLoop;
						}
					}

					if (stateValue !== "") {
						var baseStationState = markerData.data.state;
						if(baseStationState) {
							baseStationState= $.trim(baseStationState.toLowerCase());
							stateValue = $.trim(stateValue.toLowerCase());
							if (baseStationState !== stateValue) {
								continue stationsLoop;
							}
						} else {
							continue stationsLoop;
						}
					}

					if (cityValue !== "") {
						var baseStationCity = markerData.data.city;
						if(baseStationCity) {
							// console.log(baseStationCity, cityValue);
							baseStationCity= $.trim(baseStationCity.toLowerCase());
							cityValue = $.trim(cityValue.toLowerCase());
							if (baseStationCity !== cityValue) {
								continue stationsLoop;
							}
						} else {
							continue stationsLoop;
						}
					}

					filtered_stations_features.push(main_devices_data_feature_obj_wmaps.features[markerData.name]);
					for(var x=0; x< markerData.data.param.sector.length; x++) {
						var sec = markerData.data.param.sector[x];
						if($.trim(sec.technology.toLowerCase()) === $.trim(technologyValue.toLowerCase())) {
							if(main_line_sectors_features_obj_wmaps.sectors[sec.sector_configured_on_device]) {
								filtered_sector_features.push(main_line_sectors_features_obj_wmaps.sectors[sec.sector_configured_on_device]);
							}
							if(main_line_sectors_features_obj_wmaps.lines[sec.sector_configured_on_device]) {
								filtered_lines_features.push(main_line_sectors_features_obj_wmaps.lines[sec.sector_configured_on_device]);
							}

							for(var y=0; y< sec.sub_station.length; y++) {
								var sub_stat = sec.sub_station[y];
								console.log(sub_stat.name);
								console.log(Object.keys(main_devices_data_feature_obj_wmaps.features));
								filtered_stations_features.push(main_devices_data_feature_obj_wmaps.features[sub_stat.name])
							}
						}
					}
				}
			}
			console.log(filtered_stations_features.length);
			global_this.markersLayer.removeAllFeatures();
			global_this.markersLayer.addFeatures(filtered_stations_features);
			global_this.markersLayerStrategy.recluster();
			global_this.linesLayer.removeAllFeatures();
			global_this.linesLayer.addFeatures(filtered_lines_features);
			global_this.sectorsLayer.removeAllFeatures();
			global_this.sectorsLayer.addFeatures(filtered_sector_features);
			global_this.toggleLineLayer();
		}

		this.populateBasicFilterDropdowns = function() {
			/*Populate City & State*/
			var state_array = Object.keys(state_city_obj);

			var state_option = "";
			state_option = "<option value=''>Select State</option>";

			for(var i=0;i<state_array.length;i++) {
				state_option += "<option value='"+i+1+"'>"+state_array[i]+"</option>";
			}

			$("#state").html(state_option);

			var city_option = "";
			city_option = "<option value=''>Select City</option>";

			for(var i=0;i<all_cities_array.length;i++) {
				city_option += "<option value='"+i+1+"'>"+all_cities_array[i]+"</option>";
			}

			$("#city").html(city_option);

			/*Populate Technology & Vendor*/
			var technology_array = Object.keys(tech_vendor_obj);

			var tech_option = "";
			tech_option = "<option value=''>Select Technology</option>";

			for(var i=0;i<technology_array.length;i++) {
				tech_option += "<option value='"+technology_array[i]+"'>"+technology_array[i]+"</option>";
			}

			$("#technology").html(tech_option);
			// $("#polling_tech").html(tech_option);

			var vendor_option = "";
			vendor_option = "<option value=''>Select Vendor</option>";

			for(var i=0;i<all_vendor_array.length;i++) {
				vendor_option += "<option value='"+i+1+"'>"+all_vendor_array[i]+"</option>";
			}

			$("#vendor").html(vendor_option);

			/*Ajax call for Live polling technology data*/
			$.ajax({
				url : base_url+"/"+"device/filter/",
				// url : "../../static/filter_data.json",
				success : function(result) {
					var techData = JSON.parse(result).data.objects.technology.data;

					/*Populate technology dropdown*/
					var techOptions = "<option value=''>Select Technology</option>";
					$.grep(techData,function(tech) {
						if(technology_array.indexOf(tech.value) >= 0) {
							techOptions += "<option value='"+tech.id+"'>"+tech.value.toUpperCase()+"</option>";
						}
					});
					$("#polling_tech").html(techOptions);
				},
				error : function(err) {
					// console.log(err.statusText);
				}
			});
		}
		this.resetBasicFilter = function() {
			$("#technology").val('');
			$("#vendor").val('');
			$("#state").val('');
			$("#city").val('');

			this.applyBasicFilter();
		}
	/**
	 * End of Advance Search and Filter
	 */

	

	/**
	 *
	 * Private Functions
	 */
	
		
	 	/**
    * This function creates data to plot sectors on google maps.
    * * @method createSectorData.
    * * @param Lat {Number}, It contains lattitude of any point.
    * * @param Lng {Number}, It contains longitude of any point.
    * * @param radius {Number}, It contains radius for sector.
    * * @param azimuth {Number}, It contains azimuth angle for sector.
    * * @param beamwidth {Number}, It contains width for the sector.
    * * @param sectorData {Object}, It contains sector info json object.
    * * @param orientation {String}, It contains the orientation type of antena i.e. vertical or horizontal
    * * @return {Object Array} sectorDataArray, It is the polygon points lat-lon object array
    * */
    function createSectorData(lat, lng, radius, azimuth, beamWidth, orientation, callback) {
        var triangle = [],
             sectorDataArray = [];
        // Degrees to radians
        var d2r = Math.PI / 180;
        //  Radians to degrees
        var r2d = 180 / Math.PI;

        var PRlat = (radius / 6371) * r2d; // using 3959 miles or 6371 KM as earth's radius
        var PRlng = PRlat / Math.cos(lat * d2r);

        var PGpoints = [],
             pointObj = {};

        with(Math) {
            lat1 = (+lat) + (PRlat * cos(d2r * (azimuth - beamWidth / 2)));
            lon1 = (+lng) + (PRlng * sin(d2r * (azimuth - beamWidth / 2)));

            /*Create lat-lon point object*/
            /*Reset Pt Object*/
            pointObj = {};
            pointObj["lat"] = lat1;
            pointObj["lon"] = lon1;
            /*Add point object to array*/
            PGpoints.push(pointObj);

            lat2 = (+lat) + (PRlat * cos(d2r * (azimuth + beamWidth / 2)));
            lon2 = (+lng) + (PRlng * sin(d2r * (azimuth + beamWidth / 2)));

            var theta = 0;
            var gamma = d2r * (azimuth + beamWidth / 2);

            for (var a = 1; theta < gamma; a++) {
                theta = d2r * (azimuth - beamWidth / 2 + a);
                PGlon = (+lng) + (PRlng * sin(theta));
                PGlat = (+lat) + (PRlat * cos(theta));
                /*Reset Pt Object*/
                pointObj = {};
                pointObj["lat"] = PGlat;
                pointObj["lon"] = PGlon;
                /*Add point object to array*/
                PGpoints.push(pointObj);
            }
            /*Reset Pt Object*/
            pointObj = {};
            pointObj["lat"] = lat2;
            pointObj["lon"] = lon2;
            /*Add point object to array*/
            PGpoints.push(pointObj);

            var centerPtObj = {};
            centerPtObj["lat"] = lat;
            centerPtObj["lon"] = lng;
            /*Add center point object to array*/
            PGpoints.push(centerPtObj);
        }

        /*Condition for the orientation of sector antina*/
        if (orientation == "horizontal") {
            var len = Math.floor(PGpoints.length / 3);
            triangle.push(PGpoints[0]);
            triangle.push(PGpoints[(len * 2) - 1]);
            triangle.push(PGpoints[(len * 3) - 1]);
            /*Assign the triangle object array to sectorDataArray for plotting the polygon*/
            sectorDataArray = triangle;
        } else {
            /*Assign the PGpoints object array to sectorDataArray for plotting the polygon*/
            sectorDataArray = PGpoints;
        }
        /*Callback with lat-lon object array.*/
        callback(sectorDataArray);
    };

		/*
		This function takes a array of Markers and loop through each list and call prototype method createOpenLayerMarker() to create Marker for it.
		@param markersData {Array for BsData} Array containing Bs to be plotted.
		@param callback {Function} Callback to return when Finished.
		Also we add Marker Data in our variables for future use.
		 */
	   this.plotMarkers = function(markersData, callback) {
			//Loop through the markersData
			$.each(markersData, function(i, markerData) {
				
				if(markerData.data.state) {
					if(!state_city_obj[markerData.data.state]) {
						state_city_obj[markerData.data.state] = [];
					}
					if(state_city_obj[markerData.data.state].indexOf(markerData.data.city) == -1) {
						state_city_obj[markerData.data.state].push(markerData.data.city);
					}
				}

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
				main_devices_data_feature_obj_wmaps.data[name] = markerData;
				
				var bsMarkerCustomInfo = { 
					id: id, 
					name: name, 
					type: type, 
					isSpiderfied: true, 
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
				main_devices_data_feature_obj_wmaps.features[name] = marker;

				main_stations_features_wmaps.push(marker);
				
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

					var startEndObj = {};

					createSectorData(lat, lon, 4, device.azimuth_angle, device.beam_width, device.orientation, function(sectorPoints) {

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
								radius: 4,
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
							main_lines_sectors_features_wmaps.sectors.push(plottedSector);
							main_line_sectors_features_obj_wmaps.sectors[device.sector_configured_on_device] = plottedSector;
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

					if(device.technology.toLowerCase() == "p2p" || device.technology.toLowerCase() == "ptp") {
						
						if(deviceIDArray.indexOf(device['device_info'][1]['value']) === -1) {

							var perf_obj = { "performance_paramter" : "N/A", "performance_value" : "N/A", "frequency" : "N/A", "pl" : "N/A" };

							var deviceAdditionalInfo = {
								ptLat: lat,
								ptLon: lon,
								originalIcon:  base_url+"/"+device.markerUrl,
								defaultIcon: base_url+'/static/img/icons/1x1.png',
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

							//Create deviceMarker
							var deviceMarker = global_this.createOpenLayerVectorMarker(size, base_url+'/static/img/icons/1x1.png', lon, lat, deviceAdditionalInfo);

							if(sectorMarkerConfiguredOn.indexOf(device.sector_configured_on) == -1) {
								main_devices_marker_features_wmaps.push(deviceMarker);

								/*Push Sector marker to pollableDevices array*/
								pollableDevices.push(deviceMarker);

								main_devices_data_feature_obj_wmaps['devices']['sector_'+device.sector_configured_on] = deviceMarker;

								sectorMarkerConfiguredOn.push(device.sector_configured_on);

								if(main_devices_data_feature_obj_wmaps['devices'][name]) {
									main_devices_data_feature_obj_wmaps['devices'][name].push(deviceMarker)
								} else {
									main_devices_data_feature_obj_wmaps['devices'][name]= [];
									main_devices_data_feature_obj_wmaps['devices'][name].push(deviceMarker)
								}	
							}

							/*End of Create Sector Marker*/
							deviceIDArray.push(device['device_info'][1]['value']);
						}

					}
					//substation loop
					for (var k = 0; k < device.sub_station.length; k++) {

						var sub_station = device.sub_station[k];
						main_devices_data_feature_obj_wmaps.data[sub_station.name] = sub_station;

						var perf_obj = { "performance_paramter" : "N/A", "performance_value" : "N/A", "frequency" : "N/A", "pl" : "N/A" };

						var subStationAdditionalInfo = {
							ptLat: sub_station.data.lat, ptLon: sub_station.data.lon, 
							technology: device.technology,
							pointType: "sub_station",
							type: "sub_station",
							dataset: sub_station.data.param.sub_station,
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
						sub_station_marker = global_this.createOpenLayerVectorMarker(size, sub_station_icon, sub_station_lon, sub_station_lat, subStationAdditionalInfo);
						main_devices_data_feature_obj_wmaps.features[sub_station.name] = sub_station_marker;
						main_stations_features_wmaps.push(sub_station_marker);

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

							global_this.linesLayer.addFeatures([line]);
							main_lines_sectors_features_wmaps.lines.push(line);
							main_line_sectors_features_obj_wmaps.lines[device.sector_configured_on_device] = line;
						}
					}
				}
			});
			callback();
		}
		/*
		This function start Ajax Request to get the Data.
		@param i {Number} Current Counter of Ajax Request
		In Success, we get how many times we need to call Ajax Request and according to that, we recurvsily call this function.
		Also call Functions to create Marker with the data.
		 */		
		function startAjaxRequest(i) {
			//Ajax Request
			$.ajax({
				url : base_url+"/"+"device/stats/?total_count="+total_count+"&page_number="+i,
				type: 'GET',
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

							main_devices_data_wmaps = main_devices_data_wmaps.concat(response.data.objects.children);
							
							//Plot markers, on callback
							global_this.plotMarkers(response.data.objects.children, function() {
								
								//if all calls are completed
								if (i === loop_count) {

									//hide Loading
									global_this.hideLoading();

									data_for_filter = main_devices_data_wmaps;

									filtered_Features = main_stations_features_wmaps;

									//add markers to the vector Layer
									global_this.markersLayer.addFeatures(filtered_Features);

									//activate cluster strategy
									global_this.markersLayerStrategy.activate();

									//initiate advance filter class
									wmAdvanceFilterClass = new WmAdvanceFilter(main_devices_data_wmaps, main_devices_data_feature_obj_wmaps.features, main_devices_data_feature_obj_wmaps.features, main_stations_features_wmaps, cktLinesBsObj, sectorsBsObj);
									
									//initiate advance search class
									wmAdvanceSearchClass = new WmAdvanceSearch(data_for_filter);

									//populate basic filter dropdown
									global_this.populateBasicFilterDropdowns();

									global_this.linesLayer.redraw();

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
				}
			});
		}
	/**
	 *
	 * End of Private Functions
	 */


	/*
	 *
	 * Utils Section
	 */
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