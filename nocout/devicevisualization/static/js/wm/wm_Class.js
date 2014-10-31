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
	 * Private Variables
	*/	
		var global_this = "";

		this.markerLayerStrategy = "";

		var total_count = "", device_count= "", limit= "", loop_count = 0;	
		//Variable to Store JSON data of Markers
		var markersDataArray = [], markersDataObj = {};
		//Variable to Store All Markers
		var markerArray = [], markerObj = {};
		//Variable to hold Markers
		var bsMarkerObj = {}, deviceMarkerObj = {}, subStationMarkerObj = {}, cktLinesObj = {}, sectorsObj = {}, ssMarkerObj= {}, masterStationsArray= [], cktLinesBsObj = {}, sectorsBsObj= {}, ssAndDeviceArray= [];
		//Variable to hold device markers currently displayed on map
		var devices_Marker_On_Map = [], devices_Lines_On_Map = [];
		//Variable to hold Searched Markers List
		var searched_markers = [];
		//Variable to hold data after Advance Filter
		var filtered_data = [];
		/*
		Variables to hold Data which Technologies, State, Cities
		*/
		var technology = [], vendor = [], state = [], city = [], bs_name = [], ip = [], cktId = [];

		var wmAdvanceFilterClass = "";
		var wmAdvanceSearchClass = "";

		//Layer for Markers
		this.markersLayer = "";
		//Layer for Lines
		this.linesLayer = "";
		//Layer for Sector
		this.sectorsLayer = "";
		this.featuresLayer= "";
		this.markersVectorLayer = "";
		this.devicesVectorLayer= "";
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
				//This function hides Device Marker shown on the map
				function hideDevices() {
					for (var i = 0; i < devices_Marker_On_Map.length; i++) {
						devices_Marker_On_Map[i].style.externalGraphic = base_url + "static/img/icons/1x1.png";
						if(i=== devices_Marker_On_Map.length-1) {
							global_this.devicesVectorLayer.redraw();	
						}
					}
				}
				hideDevices();
				markerSpiderfied.isSpiderfied = true;
				markerSpiderfied= "";
			}
		}
		this.spiderfyBsMarker= function(marker) {
			this.unSpiderifyBsMarker();
			var bs_marker= bsMarkerObj[marker.name];
			var bs_devices = deviceMarkerObj[marker.name];
			var map_Zoom_Level = ccpl_map.getZoom();
			if(bs_devices) {
				//Loop through the devices
				for (var i = 0; i < bs_devices.length; i++) {
					bs_devices[i].style.externalGraphic = bs_devices[i].attributes.defaultIcon;
					devices_Marker_On_Map.push(bs_devices[i]);
					if(i=== bs_devices.length-1) {
						global_this.devicesVectorLayer.redraw();
					}
				}
				marker.isSpiderfied = false;
				markerSpiderfied= marker;
			}
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
			// console.log("Feature clicked: ", e);
			var infoWindowContent = gmap_self.makeWindowContent(e.feature);
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

		this.markerLayerFeatureClick= function(event) {
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
				console.log("Click on Marker");
				this.onFeatureUnselect();
				console.log(event.feature);
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
		/*
		This function is triggered on click of Bs Marker
		 */
		this.bsMarkerClick = function(e, featureMarker) {
			var marker = featureMarker.cluster[0].attributes;
			if(marker.isSpiderfied) {
				global_this.spiderfyBsMarker(marker);
			} else {
				global_this.openInfoWindow(e, marker, markersDataObj[marker.name]);
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
		var workingControl = "";
		this.toggleControl= function(element) {
			var controls = this.controls;
			for(key in controls) {
				var control = controls[key];
				if(element == key) {
					workingControl = control;
					control.activate();
				} else {
					control.deactivate();
				}
			}
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

	    					ccpl_map.addLayer(global_this.featuresLayer);

	    					global_this.toggleControl('polygon');
	    				}
	    			}
	    		});
	    	} else {
	    		alert("Please select technology.");
	    	}
		}
		
		this.stopPolling= function() {
			workingControl.deactivate();
			this.featuresLayer.destroyFeatures();
			ccpl_map.removeLayer(this.featuresLayer);
		}
		this.startPolling= function() {
			ccpl_map.addLayer(this.featuresLayer);
		}
		var polygon = "";
		this.livePollingPolygonAdded = function(e) {
			polygon = e.feature;
			workingControl.deactivate();
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
			// 				var ssMarkers = subStationMarkerObj[deviceName];
			// 				for(var j=0; j< )
			// 				// subStationMarkerObj
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
			for (var i = 0; i < markerArray.length; i++) {
				//Set icon marker size with newSize
				markerArray[i].icon.setSize(newSize);
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
			var bs_marker = bsMarkerObj[bs_name];
			bs_marker.style.display= '';
			var devicesMarkers = deviceMarkerObj[bs_name];
			if (devicesMarkers) {
				for (var i = 0; i < devicesMarkers.length; i++) {
					var deviceMarker = devicesMarkers[i];
					var deviceName = deviceMarker.name;
					var sub_stations = subStationMarkerObj[deviceName];
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
			var bs_marker = bsMarkerObj[bs_name];
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
			// 		var sub_stations = subStationMarkerObj[deviceName];
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
			filtered_data= [];
			var appliedFilter = wmAdvanceFilterClass.applyAdvFilter();
			filtered_data = appliedFilter.filtered_data;

			this.markersVectorLayer.removeAllFeatures();
			this.markersVectorLayer.addFeatures(appliedFilter.filtered_Features);
			filteredFeatures.markers = appliedFilter.filtered_Features;

			this.linesLayer.removeAllFeatures();
			this.linesLayer.addFeatures(appliedFilter.line_Features);
			filteredFeatures.lines = appliedFilter.line_Features;

			this.sectorsLayer.removeAllFeatures();
			this.sectorsLayer.addFeatures(appliedFilter.sector_Features);
			filteredFeatures.sectors = appliedFilter.sector_Features;

			
			wmAdvanceSearchClass.setMasterData(filtered_data);
			
			global_this.markerLayerStrategy.recluster();

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
			// global_this.markersVectorLayer.strategies[0].deactivate();
			var vendorValue = $("#vendor").val();
			var stateValue = $("#state").val();
			var cityValue = $("#city").val();
			var markerDataShowing = [];
			var markersToShow= [], linesToShow= [], sectorsToShow= [];

			stationsLoop: for (var i = 0; i < filtered_data.length; i++) {
				var markerData = filtered_data[i];
				var bsMarker = bsMarkerObj[markerData.name];
				if (true) {
					if (technologyValue === "" && vendorValue === "" && stateValue === "" && cityValue === "") {
						console.log('lol');
						markerDataShowing = filtered_data;
						markersToShow = filteredFeatures.markers;
						linesToShow = filteredFeatures.lines;
						sectorsToShow = filteredFeatures.sectors;
						break stationsLoop;
					} else {
						if (technologyValue !== "") {
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
								if (vendorValue !== baseStationVendor) {
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
								console.log(baseStationCity, cityValue);
								baseStationCity= $.trim(baseStationCity.toLowerCase());
								cityValue = $.trim(cityValue.toLowerCase());
								if (baseStationCity !== cityValue) {
									continue stationsLoop;
								}
							} else {
								continue stationsLoop;
							}
						}

						markerDataShowing.push(markerData);

						markersToShow.push(bsMarkerObj[markerData.name]);
						var bsSubStationsMarkers = ssMarkerObj[markerData.name];
						if(bsSubStationsMarkers && bsSubStationsMarkers.length) {
							for(var j=0; j< bsSubStationsMarkers.length; j++) {
								markersToShow.push(bsSubStationsMarkers[j]);
							}
						}

						var lines = cktLinesBsObj[markerData.name];

						if(lines && lines.length) {
							for(var j=0; j< lines.length; j++) {
								linesToShow.push(lines[j]);
							}
						}
						
						var sectors = cktLinesBsObj[markerData.name];
						if(sectors && sectors.length) {
							for(var j=0; j< sectors.length; j++) {
								sectorsToShow.push(sectors[j]);
							}
							
						}
					}
				}
			}

			global_this.markersVectorLayer.removeAllFeatures();
			global_this.markersVectorLayer.addFeatures(markersToShow);

			// global_this.linesLayer.removeAllFeatures();
			// global_this.linesLayer.addFeatures(linesToShow);
			global_this.toggleLines();

			global_this.sectorsLayer.removeAllFeatures();
			global_this.sectorsLayer.addFeatures(sectorsToShow);

			wmAdvanceSearchClass.setMasterData(markerDataShowing);

			global_this.markerLayerStrategy.recluster();
		}

		this.populateBasicFilterDropdowns = function() {
			if (technology.length) {
				for (var i = 0; i < technology.length; i++) {
					if (technology[i]) {
						$("#technology").append('<option value="' + technology[i] + '">' + technology[i] + '</option>');
					}
				}
			}

			if (vendor.length) {
				for (var i = 0; i < vendor.length; i++) {
					if (vendor[i]) {
						$("#vendor").append('<option value="' + vendor[i] + '">' + vendor[i] + '</option>');
					}
				}
			}

			if (city.length) {
				for (var i = 0; i < city.length; i++) {
					if (city[i]) {
						$("#city").append('<option value="' + city[i] + '">' + city[i] + '</option>');
					}
				}
			}

			if (state.length) {
				for (var i = 0; i < state.length; i++) {
					if (state[i]) {
						$("#state").append('<option value="' + state[i] + '">' + state[i] + '</option>');
					}
				}
			}
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
	* This function creates data to plot sectors on google maps.
	* * @method getSectorPointsArray.
	* * @param Lat {Number}, It contains lattitude of any point.
	* * @param Lng {Number}, It contains longitude of any point.
	* * @param radius {Number}, It contains radius for sector.
	* * @param azimuth {Number}, It contains azimuth angle for sector.
	* * @param beamwidth {Number}, It contains width for the sector.
	* * @param sectorData {Object}, It contains sector info json object.
	* * @param orientation {String}, It contains the orientation type of antena i.e. vertical or horizontal
	* * @return {Object Array} sectorDataArray, It is the polygon points lat-lon object array
	* */
	function getSectorPointsArray(lat, lng, radius, azimuth, beamWidth, orientation, callback) {
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

	/**
	 *
	 * Private Functions
	 */
	
		var master_data_array = [], master_data_obj = {}
		var bs_features_master_array = [], bs_features_master_obj = {};
		var device_features_master_array = [], device_features_master_obj = {};
		var ss_features_master_array = [], ss_features_master_obj = {};
		var line_features_master_array = [], line_features_master_obj = {};
		var sector_features_master_array = [], sector_features_master_obj = {};
		/*
		This function takes a array of Markers and loop through each list and call prototype method createOpenLayerMarker() to create Marker for it.
		@param markersData {Array for BsData} Array containing Bs to be plotted.
		@param callback {Function} Callback to return when Finished.
		Also we add Marker Data in our variables for future use.
		 */
		// var stationsMarkerFeaturesArray = [];
	   function addMarkers(markersData, callback) {
			//Loop through the markersData
			$.each(markersData, function(i, markerData) {
				//Store data in a Object with BS Name as key
				markersDataObj[markerData.name] = markerData;
				//Push data in the Global Variable
				markersDataArray.push(markerData);

				master_data_array.push(markerData);
				master_data_obj[markerData.name] = markerData;

				//Push data for Search and Basic Filter dataset.
				filtered_data.push(markerData);

				//Add Bs Name to bs_name Array
				bs_name.push(markerData.name);

				//Add States to State Array
				if (state.indexOf(markerData.data.state) === -1) {
					state.push(markerData.data.state);
				}

				//Add Cities to City Array
				if (city.indexOf(markerData.data.city) === -1) {
					city.push(markerData.data.city);
				}

				//base station 
				var id = markerData.id, name = markerData.name, lon = markerData.data.lon, lat = markerData.data.lat, icon = base_url+"/static/img/icons/bs.png", size = new OpenLayers.Size(whiteMapSettings.size.medium.width, whiteMapSettings.size.medium.height), type = "base_station";
				var additionalInfoObject = { id: id, name: name, type: type, visible: 'true', isSpiderfied: true, dataset: markerData.data.param.base_station, bhInfo: markerData.data.param.backhual, ptLat: lat, ptLon: lon, pointType: type }

				var marker = global_this.createOpenLayerVectorMarker(size, icon, lon, lat, additionalInfoObject);

				//Store marker in bs marker object
				bsMarkerObj[name] = marker;
				//push marker in markerArray
				markerArray.push(marker);

				bs_features_master_array.push(marker);
				bs_features_master_obj[name] = marker;

				masterStationsArray.push(marker);

				filteredFeatures.markers.push(marker);
				
				//base station devices loop
				var total_angle = 360, devices_length = markerData.data.param.sector.length, angleOnWhichDeviceIconToPlace = Math.floor(total_angle / devices_length), current_angle = 0;
				//Loop through the bs devices
				for (var i = 0; i < markerData.data.param.sector.length; i++) {
					if(!(lon && lat)) {
						return ;
					}

					var device = markerData.data.param.sector[i];

					if (vendor.indexOf(device.vendor) === -1) {
						vendor.push(device.vendor);
					}

					if (technology.indexOf(device.technology) === -1) {
						technology.push(device.technology);
					}

					if(device.technology.toLowerCase() == "p2p" || device.technology.toLowerCase() == "ptp") {
						//get angle at which device marker is to be shown
						current_angle += angleOnWhichDeviceIconToPlace;
						//Get Lat Lng at a specific angle and distance.
						var deviceLatLngObject = getAtXYDirection(current_angle, 1, lon, lat);
						//Get device Icon
						var deviceIcon = base_url+'/static/img/icons/1x1.png';
						var deviceType = "base_station_device";
						var deviceAdditionalInfo = {
							id: device.device_info[1].value,
							name: device.device_info[0].value,
							type: deviceType,
							visible: false,
							defaultIcon:  base_url+"/"+device.markerUrl,
							clusterIcon: base_url+'/static/img/icons/1x1.png',
							lat: deviceLatLngObject.lat,
							lon: deviceLatLngObject.lon,
							technology: device.technology,
							ptLat: deviceLatLngObject.lat,
							ptLon: deviceLatLngObject.lon,
							device_name : device.sector_configured_on_device,
							sectorName  		: device.sector_configured_on
						}
						//Create deviceMarker
						var deviceMarker = global_this.createOpenLayerVectorMarker(size, deviceIcon, deviceLatLngObject.lon, deviceLatLngObject.lat, deviceAdditionalInfo);

						ssAndDeviceArray.push(deviceMarker);
						device_features_master_array.push(deviceMarker);
						device_features_master_obj[name] = deviceMarker;

						global_this.devicesVectorLayer.addFeatures(deviceMarker);
						//Add marker to markerArray
						markerArray.push(deviceMarker);

						//Store deviceMarker in a obj for later use.
						if (!deviceMarkerObj[name]) {
							deviceMarkerObj[name] = [];
						}					
						deviceMarkerObj[name].push(deviceMarker);
					}
					var sectorPintsArray =[];
					if (device.technology.toLowerCase() !== "p2p" && device.technology.toLowerCase() != "ptp") {
						getSectorPointsArray(lat, lon, device.radius, device.azimuth_angle, device.beam_width, device.orientation, function(sectorsPointArray) {
							var sectorAdditionalInfo = {
								bsname: name,
								ssname: sub_station_name,
								ckt: device.circuit_id,
								devicename: device.device_info[0].value,
								type: "sector",
								pointType: "sector",
								startLat: lat,
								startLon: lon,
								bhInfo: [],
								dataset: device.info,
								"bs_name" : markerData.alias,
								"sector_name" : device.sector_configured_on,
								ptLat: lat,
								ptLon: lon,
								technology: device.technology
							}
							global_this.drawSector(sectorsPointArray, device.color, device.technology, sectorAdditionalInfo, function(sector) {
								sectorPintsArray= sectorsPointArray;
								global_this.sectorsLayer.addFeatures([sector]);
								//Store CktID in an Object for later use.
								if (!sectorsObj[device.device_info[0].value]) {
									sectorsObj[device.device_info[0].value] = [];
								}
								sectorsObj[device.device_info[0].value].push(sector);
								if (!sectorsBsObj[name]) {
									sectorsBsObj[name] = [];
								}
								sectorsBsObj[name].push(sector);
								filteredFeatures.sectors.push(sector);

								sector_features_master_array.push(sector);

								if (!sector_features_master_obj[name]) {
									sector_features_master_obj[name] = [];
								}
								sector_features_master_obj[name].push(sector);
								
							});
						});
					}

					//substation loop
					for (var j = 0; j < device.sub_station.length; j++) {
						var sub_station = device.sub_station[j];
						ip.push(sub_station.data.substation_device_ip_address);
						cktId.push(sub_station.data.param.sub_station[3].value);
						var sub_station_id = sub_station.id;
						var sub_station_name = sub_station.name;
						var sub_station_type = "sub_station";
						var sub_station_lon = sub_station.data.lon;
						var sub_station_lat = sub_station.data.lat;
						var sub_station_icon = base_url+"/"+sub_station.data.markerUrl;
						var subStationAdditionalInfo = {
							id: sub_station_id,
							name: sub_station_name,
							type: sub_station_type,
							visible: true,
							dataset: sub_station.data.param.sub_station,
							bhInfo: [],
							poll_info: [],
							ptLat: sub_station_lat, ptLon: sub_station_lon, 
							pointType: sub_station_type,
							technology: device.technology,
							device_name 	 : 	sub_station.device_name,
							bs_sector_device :  device.sector_configured_on_device,
							ss_ip 	 		 : 	sub_station.data.substation_device_ip_address,
							sector_ip 		 :  device.sector_configured_on,
						}
						//Create marker
						// var sub_station_marker = global_this.createOpenLayerMarker(size, sub_station_icon, sub_station_lon, sub_station_lat, subStationAdditionalInfo);
						var sub_station_marker = global_this.createOpenLayerVectorMarker(size, sub_station_icon, sub_station_lon, sub_station_lat, subStationAdditionalInfo);
						//Add marker to markerArray
						markerArray.push(sub_station_marker);
						// stationsMarkerFeaturesArray.push(sub_station_marker);
						ssAndDeviceArray.push(sub_station_marker);
						masterStationsArray.push(sub_station_marker);

						filteredFeatures.markers.push(sub_station_marker);
						//Add marker to MarkerLayer
						// global_this.markersLayer.addMarker(sub_station_marker);
						// 
						ss_features_master_array.push(sub_station_marker);

						if (!ss_features_master_obj[name]) {
							ss_features_master_obj[name] = [];
						}
						ss_features_master_obj[name].push(sub_station_marker);

						//Store SubStations for later use.
						if (!subStationMarkerObj[device.device_info[0].value]) {
							subStationMarkerObj[device.device_info[0].value] = [];
						}
						subStationMarkerObj[device.device_info[0].value].push(sub_station_marker);

						if (!ssMarkerObj[name]) {
							ssMarkerObj[name] = [];
						}
						ssMarkerObj[name].push(sub_station_marker);

						if (device.technology.toLowerCase() !== "p2p" && device.technology.toLowerCase() != "ptp") {
							var lineAdditionalInfo = {
								bsname: name,
								ssname: sub_station_name,
								ckt: device.circuit_id,
								devicename: device.device_info[0].value,
								type: "line"
							}

							var halfPt = Math.floor(sectorPintsArray.length / (+2));

							var line = global_this.drawLine(sectorPintsArray[halfPt].lon, sectorPintsArray[halfPt].lat, sub_station_lon, sub_station_lat, device.color, lineAdditionalInfo);
							line.style.display= 'none';
							global_this.linesLayer.addFeatures([line]);

							//Store CktID in an Object for later use.
							if (!cktLinesObj[device.device_info[0].value]) {
								cktLinesObj[device.device_info[0].value] = [];
							}
							cktLinesObj[device.device_info[0].value].push(line);

							if (!cktLinesBsObj[name]) {
								cktLinesBsObj[name] = [];
							}
							cktLinesBsObj[name].push(line);

							line_features_master_array.push(line);

							if (!line_features_master_obj[name]) {
								line_features_master_obj[name] = [];
							}
							line_features_master_obj[name].push(line);

						} else {
							var lineAdditionalInfo = {
								"bsname": name,
								"ssname": sub_station_name,
								"ckt": device.circuit_id,
								devicename: device.device_info[0].value,
								type: "line",
								pointType: "path",
								bs_info: markerData.data.param.base_station,
								ss_info: sub_station.data.param.sub_station,
								nearLat: lat,
								nearLon: lon,
								ss_lat: sub_station_lat,
								ss_lon: sub_station_lon
							}
							//Draw line between BS and SS
							var line = global_this.drawLine(lon, lat, sub_station_lon, sub_station_lat, device.color, lineAdditionalInfo);
							line.style.display= 'none';
							//Add line to the LinesLayer
							global_this.linesLayer.addFeatures([line]);
							filteredFeatures.lines.push(line);


							//Store CktID in an Object for later use.
							if (!cktLinesObj[device.device_info[0].value]) {
								cktLinesObj[device.device_info[0].value] = [];
							}
							cktLinesObj[device.device_info[0].value].push(line);

							if (!cktLinesBsObj[name]) {
								cktLinesBsObj[name] = [];
							}
							cktLinesBsObj[name].push(line);

							line_features_master_array.push(line);

							if (!line_features_master_obj[name]) {
								line_features_master_obj[name] = [];
							}
							line_features_master_obj[name].push(line);
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
		var devicesCount=0;
		function startAjaxRequest(i) {
			//Ajax Request
			$.ajax({
				url : base_url+"/"+"device/stats/?total_count="+devicesCount+"&page_number="+i,
				type: 'GET',
				dataType: 'json',
				//Success callback
				success: function(response) {
					if(response.success == 1) {
						//First Time, find how many times Ajax Request is to be sent.
						if (i === 1) {
							total_count = response.data.meta.total_count;
							devicesCount = total_count;
							device_count = response.data.meta.device_count;
							limit = response.data.meta.limit;

							loop_count = Math.ceil(total_count / limit);
						}
						//Condition to check if we need to call Ajax Request again
						if (i <= loop_count && response.success && response.data.objects.children.length) {
							//IIFE to add Markers
							(function(i) {
								addMarkers(response.data.objects.children, function() {
									//if all markers are plotted, dropdwon basicfilter, advance search and advance filter dropdowns with the markers data.
									if (i === loop_count) {
										disableAdvanceButton('no');
										$("#loadingIcon").hide();
										$("#resetFilters").button("complete");

										global_this.markersVectorLayer.addFeatures(masterStationsArray);
										global_this.markerLayerStrategy.activate();

										wmAdvanceFilterClass = new WmAdvanceFilter(markersDataArray, bsMarkerObj, ssMarkerObj, masterStationsArray, cktLinesBsObj, sectorsBsObj);
										wmAdvanceSearchClass = new WmAdvanceSearch(markersDataArray);

										global_this.populateBasicFilterDropdowns();
										return;
									}

									//send next request after 40 ms.
									setTimeout(function() {
										i++;
										startAjaxRequest(i);
									}, 40);
								});
							}(i));
							return ;
						}
					}
				},
				error: function(response) {
					showErrorMessage('ajax call error', response);
				}
			});
		}
	/**
	 *
	 * End of Private Functions
	 */


	/*
	* Constructor for White Map Class.
	* * Starts building of White Maps
	* */
	this.init = function() {
		//save this as global variable within this class
		global_this = this;
		disableAdvanceButton();
		$("#loadingIcon").show();
		$("#resetFilters").button("loading");
		//Call prototype method createOpenLayerMap() to create White Map and in the callback, Bind Click control to map. Start Ajax Request to get Data.
		this.createOpenLayerMap(function() {			
			//start ajax request
			startAjaxRequest(1);
		});
	}
}