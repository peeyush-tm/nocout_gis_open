var ccpl_map, base_url;
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
		var total_count = "", device_count= "", limit= "", loop_count = 0;	
		//Variable to Store JSON data of Markers
		var markersDataArray = [], markersDataObj = {};
		//Variable to Store All Markers
		var markerArray = [], markerObj = {};
		//Variable to hold Markers
		var bsMarkerObj = {}, deviceMarkerObj = {}, subStationMarkerObj = {}, cktLinesObj = {}, sectorsObj = {};
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
			if (f.cluster.length > 2){
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
				if(element.value == key && element.checked) {
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
		}
		this.getMarkerInPolygon = function() {
			for(var i=0; i< markersDataArray.length; i++) {
				if(polygon){
					if(displayBounds(polygon, markersDataArray[i].data.lon, markersDataArray[i].data.lat) === 'in') {
						console.log("Inside Substation: "+ JSON.stringify(markersDataArray[i]));
					}
				}
			}
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
		this.toggleLines = function() {
			//Checked if Show/Hide option is checked or unchecked.
			var selectedValue = $("#tools_show_lines").attr('checked')
			//Loop through all cktLinesObj
			for (var keys in cktLinesObj) {
				if (cktLinesObj.hasOwnProperty(keys)) {
					//Ckt Line
					var cktLines = cktLinesObj[keys];
					//Loop through all CktLine for a Device 
					for (var i = 0; i < cktLines.length; i++) {
						var cktLine = cktLines[i];
						//Set display to block if show is checked
						if (selectedValue) {
							cktLine.style.display = 'block';
						//Else set display to none if hide is checked.
						} else {
							cktLine.style.display = 'none';
						}
					}
				}
			}
			//Redraw Lines Layer to update the layer.
			global_this.linesLayer.redraw();
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
		this.zoomToLonLat = function() {
			//Longitude, Latitude entered in the textbox
			var lonlat = $("#latLongSearch_lonlat").val();

			//If textbox is non-empty
			if (lonlat.length > 0) {
				//Split the value entered in the lat long. If , is not specified, show alert
				if (lonlat.split(",").length != 2) {
					//Alert
					alert("Please Enter Proper Lattitude,Longitude.");
					//Reset value
					$("#latLongSearch_lonlat").val("");
				} else {
					//Get lat entered.
					var lat = +(lonlat.split(",")[0]),
					//Get long entered
					lng = +(lonlat.split(",")[1]),
					//Check lat for -90 > lat > 90 condition
					lat_check = (lat >= -90 && lat < 90),
					lon_check = (lat >= -180 && lat < 180),
					dms_pattern = /^(-?\d+(?:\.\d+)?)[°:d]?\s?(?:(\d+(?:\.\d+)?)['′:]?\s?(?:(\d+(?:\.\d+)?)["″]?)?)?\s?([NSEW])?/i;
					dms_regex = new RegExp(dms_pattern);

					if ((lat_check && lon_check) || (dms_regex.exec(lonlat.split(",")[0]) && dms_regex.exec(lonlat.split(",")[1]))) {
						if ((lat_check && lon_check)) {
							var bounds = new OpenLayers.Bounds;
							var lonLat = new OpenLayers.LonLat(lng, lat);
							bounds.extend(lonLat);
							ccpl_map.zoomToExtent(bounds);
						} else {
							var converted_lat = dmsToDegree(dms_regex.exec(lonlat.split(",")[0]));
							var converted_lng = dmsToDegree(dms_regex.exec(lonlat.split(",")[1]));
							var bounds = new OpenLayers.Bounds;
							var lonLat = new OpenLayers.LonLat(converted_lng, converted_lat);
							bounds.extend(lonLat);
							ccpl_map.zoomToExtent(bounds);
						}
					} else {
						alert("Please Enter Proper Lattitude,Longitude.");
						$("#latLongSearch_lonlat").val("");
					}
				}
			} else {
				alert("Please Enter Lattitude,Longitude.");
			}
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
			//Select Empty value is select boxes
			$("#advance_filter_technology").select2('val', '');
			$("#advance_filter_vendor").select2('val', '');
			$("#advance_filter_state").select2('val', '');
			$("#advance_filter_city").select2('val', '');

			//Trigger applyAdvanceFilter()
			this.applyAdvanceFilter();

			//Update filtered_data variable
			filtered_data = markersDataArray;

			//Trigger resetBasicFilter()
			this.resetBasicFilter();
		}	
		/*
		This function is triggered when Apply Advance Filter is triggered.
		Here, we check for the values selected in the Multibox and filter result according to it.
		 */
		this.applyAdvanceFilter = function() {
			filtered_data = [];
			//Values
			var technologyValue = $("#advance_filter_technology").val(), vendorValue = $("#advance_filter_vendor").val(), stateValue = $("#advance_filter_state").val(), cityValue = $("#advance_filter_city").val();

			//If no value is selected, show All Markers
			if ((technologyValue === "" || technologyValue === null) && (vendorValue === "" || vendorValue === null) && (stateValue === "" || stateValue === null) && (cityValue === "" || cityValue === null)) {
				filtered_data = markersDataArray;
				markersDataArray.map(function(marker) {
					//show marker
					global_this.showStationMarker(marker);
				});
			} else {
				//Loop through bs station
				stationsLoop: for (var i = 0; i < markersDataArray.length; i++) {
					var markerData = markersDataArray[i];
					//If technology value is present
					if (technologyValue !== "" && technologyValue !== null && technologyValue.length) {
						var goodThing = false;
						var baseStationTechnology = markerData.sector_ss_technology;
						//check if marker satisfies the technology condition
						for (var j = 0; j < technologyValue.length; j++) {
							if (technologyValue[j] && (baseStationTechnology.indexOf(technologyValue[j])) !== -1) {
								goodThing = true;
							}
						}
						//if does not
						if (goodThing === false) {
							//hide station marker
							global_this.hideStationMarkers(markerData);
							//continue loop
							continue stationsLoop;
						} else {
							//else show station marker
							global_this.showStationMarker(markerData);
						}
					}

					//If vendor value is present
					if (vendorValue !== "" && vendorValue !== null && vendorValue.length) {
						var baseStationVendor = markerData.sector_ss_vendor;
						var goodThing = false;
						//check if marker satisfies the vendor condition
						for (var j = 0; j < vendorValue.length; j++) {
							if (vendorValue[j] && baseStationVendor.indexOf(vendorValue[j]) !== -1) {
								goodThing = true;
							}
						}
						//if does not
						if (goodThing === false) {
							//hide station marker
							global_this.hideStationMarkers(markerData);
							//continue loop
							continue stationsLoop;
						} else {
							//else show station marker
							global_this.showStationMarker(markerData);
						}
					}

					//If state value is present
					if (stateValue !== "" && stateValue !== null && stateValue.length) {
						var baseStationState = markerData.data.state;
						var goodThing = false;
						//check if marker satisfies the state condition
						for (var j = 0; j < stateValue.length; j++) {
							if (stateValue[j] && baseStationState === stateValue[j]) {
								goodThing = true;
							}
						}
						//if does not
						if (goodThing === false) {
							//hide station marker
							global_this.hideStationMarkers(markerData);
							//continue loop
							continue stationsLoop;
						} else {
							//else show station marker
							global_this.showStationMarker(markerData);
						}
					}

					//If state value is present
					if (cityValue !== "" && cityValue !== null && cityValue.length) {
						var baseStationCity = markerData.data.city;
						var goodThing = false;
						//check if marker satisfies the state condition
						for (var j = 0; j < cityValue.length; j++) {
							if (cityValue[j] && baseStationCity === cityValue[j]) {
								goodThing = true;
							}
						}
						//if does not
						if (goodThing === false) {
							//hide station marker
							global_this.hideStationMarkers(markerData);
							//continue loop
							continue stationsLoop;
						} else {
							//else show station marker
							global_this.showStationMarker(markerData);
						}
					}
					//push data in filtered_data
					filtered_data.push(markerData);
				}
			}
			//reset search and basic filter.
			global_this.resetAdvanceSearch();
			global_this.resetBasicFilter();
		}
		/*
		This function populates AdvanceFilter Multiselect dataItems
		 */
		this.populateAdvanceFilterDropdown = function() {
			var options = { width: 'resolve' };
			//Loop through the technology for the devices
			if (technology.length) {
				for (var i = 0; i < technology.length; i++) {
					//technology[i] is a valid value
					if (technology[i]) {
						//Append the option in dropdown
						$("#advance_filter_technology").append('<option value="' + technology[i] + '">' + technology[i] + '</option>');
					}
				}
			}

			//Call select2 method to create multiselect
			$("#advance_filter_technology").select2(options);

			//Loop through the vendor for the devices
			if (vendor.length) {
				for (var i = 0; i < vendor.length; i++) {
					//vendor[i] is a valid value
					if (vendor[i]) {
						//Append the option in dropdown
						$("#advance_filter_vendor").append('<option value="' + vendor[i] + '">' + vendor[i] + '</option>');
					}
				}
			}

			//Call select2 method to create multiselect
			$("#advance_filter_vendor").select2(options);

			//Loop through the city for the devices
			if (city.length) {
				for (var i = 0; i < city.length; i++) {
					//city[i] is a valid value
					if (city[i]) {
						//Append the option in dropdown
						$("#advance_filter_city").append('<option value="' + city[i] + '">' + city[i] + '</option>');
					}
				}
			}

			//Call select2 method to create multiselect
			$("#advance_filter_city").select2(options);

			//Loop through the state for the devices
			if (state.length) {
				for (var i = 0; i < state.length; i++) {
					//state[i] is a valid value
					if (state[i]) {
						//Append the option in dropdown
						$("#advance_filter_state").append('<option value="' + state[i] + '">' + state[i] + '</option>');
					}
				}
			}

			//Call select2 method to create multiselect
			$("#advance_filter_state").select2(options);
		}
		/*
		This function reset Advance Search
		 */
		var search_Markers = [];
		this.resetAdvanceSearch = function() {
			$("#advance_search_bs_name").select2('val', '');
			$("#advance_search_ip").select2('val', '');
			$("#advance_search_cktid").select2('val', '');
			$("#advance_search_city").select2('val', '');
			//hide search markers here
			for(var i=0; i< search_Markers.length; i++) {
				this.markersLayer.removeMarker(search_Markers[i]);
				search_Markers[i].destroy();
			}
		}
		/*
		This function applies Advance Search
		 */
		this.applyAdvanceSearch = function() {
			var bs_name = "", ip = "", city = "", searchCktId = "";
			var base_stations = [];

			bs_name = $("#advance_search_bs_name").val();
			ip = $("#advance_search_ip").val();
			city = $("#advance_search_city").val();
			searchCktId = $("#advance_search_cktid").val();

			//If no value for advance search
			if ((bs_name === "" || bs_name === null) && (ip === "" || ip === null) && (city === "" || city === null) && (searchCktId === "" || searchCktId === null)) {
				//do nothing
			} else {
				stationsLoop: for (var i = 0; i < filtered_data.length; i++) {
					var markerData = filtered_data[i];
					var isValid = false;
					var ipCondition;
					var namePresent, cktIdPresent, cityPresent;
					//If bs_name is present
					if (bs_name !== "" && bs_name !== null && bs_name.length) {

						//Check for Undefined value because of select2
						if (bs_name.length === 1 && !bs_name[0]) {} else {
							namePresent= true;
							var goodThing = false;
							var baseStationName = markerData.name;
							//Check for bs_name
							for (var j = 0; j < bs_name.length; j++) {
								if (bs_name[j] && baseStationName === bs_name[j]) {
									goodThing = true;
								}
							}
							//If bs_name fails, continue stationsLoop
							if (goodThing === false) {
								continue stationsLoop;
							}
						}
					}

					//If ip is present
					if (ip !== "" && ip !== null && ip.length) {
						//Check for Undefined value because of select2
						if (ip.length === 1 && !ip[0]) {} else {
							var goodThing = false;
							var baseStationIps = markerData.sector_configured_on_devices;
							//Check for ip name
							for (var j = 0; j < ip.length; j++) {
								if (ip[j] && baseStationIps.indexOf(ip[j]) !== -1) {
									ipCondition= true;
									goodThing = true;
								}
								for(var z=0; z< markerData.data.param.sector.length; z++) {
									var sector= markerData.data.param.sector[z];
									for(var y=0; y< sector.sub_station.length; y++) {
										var sub_station = sector.sub_station[y];
										if(sub_station.data.param.sub_station[0].value == ip[j]) {
											base_stations.push(sub_station);
											if(ipCondition === undefined) {
												ipCondition = false;
												goodThing= true;
											}
										}
									}
								}
							}
							//If ip fails, continue stationsLoop
							if (goodThing === false) {
								continue stationsLoop;
							}
						}
					}

					//If searchCktId is present
					if (searchCktId !== "" && searchCktId !== null && searchCktId.length) {
						//Check for Undefined value because of select2
						if (searchCktId.length === 1 && !searchCktId[0]) {} else {
							cktIdPresent= true;
							var goodThing = false;
							var baseStationCktId = markerData.circuit_ids;
							//Check for searchCktId name
							for (var j = 0; j < searchCktId.length; j++) {
								if (searchCktId[j] && baseStationCktId.indexOf(searchCktId[j]) !== -1) {
									for(var z=0; z< markerData.data.param.sector.length; z++) {
										var sector= markerData.data.param.sector[z];
										for(var y=0; y< sector.sub_station.length; y++) {
											var sub_station = sector.sub_station[y];
											if(sub_station.data.param.sub_station[3].value === searchCktId[j]) {
												base_stations.push(sub_station);
											}
										}
									}
									goodThing = true;
								}
							}
							//If searchCktId fails, continue stationsLoop
							if (goodThing === false) {
								continue stationsLoop;
							}
						}
					}

					//If city is present
					if (city !== "" && city !== null && city.length) {
						//Check for Undefined value because of select2
						if (city.length === 1 && !city[0]) {} else {
							cityPresent = true;
							var goodThing = false;
							var baseStationCity = markerData.data.city;
							//Check for city value
							for (var j = 0; j < city.length; j++) {
								if (city[j] && baseStationCity === city[j]) {
									goodThing = true;
								}
							}
							//If city failes, continue stationsLoop
							if (goodThing === false) {
								continue stationsLoop;
							}
						}
					}
					if((ipCondition=== undefined && ipCondition !== false) || (cityPresent || cktIdPresent || namePresent)) {
						base_stations.push(markerData);
					}
				}

				if (base_stations.length) {
					var bounds = new OpenLayers.Bounds();
					for (var i = 0; i < base_stations.length; i++) {

						var marker = global_this.createOpenLayerMarker(new OpenLayers.Size(21, 25), 'http://mapicons.nicolasmollet.com/wp-content/uploads/mapicons/shape-default/color-c03638/shapecolor-color/shadow-1/border-dark/symbolstyle-white/symbolshadowstyle-dark/gradient-no/pirates.png', base_stations[i].data.lon, base_stations[i].data.lat, {});
						// this.markersLayer.addMarker(marker);
						search_Markers.push(marker);
						bounds.extend(new OpenLayers.LonLat(base_stations[i].data.lon, base_stations[i].data.lat));
					}
					ccpl_map.zoomToExtent(bounds);
				} else {
					alert("NO RESULT FOUND");
				}
			}
		}
		/*
		This function populate Advance Search Dropdowns
		 */
		this.populateAdvanceSearchDropdowns = function() {
			var options = { width: 'resolve' };

			//Loop through the technology for the devices
			if (bs_name.length) {
				for (var i = 0; i < bs_name.length; i++) {
					if (bs_name[i]) {
						$("#advance_search_bs_name").append('<option value="' + bs_name[i] + '">' + bs_name[i] + '</option>');
					}
				}
			}

			$("#advance_search_bs_name").select2(options);

			if (ip.length) {
				for (var i = 0; i < ip.length; i++) {
					if (ip[i]) {
						$("#advance_search_ip").append('<option value="' + ip[i] + '">' + ip[i] + '</option>');
					}
				}
			}

			$("#advance_search_ip").select2(options);

			if (cktId.length) {
				for (var i = 0; i < cktId.length; i++) {
					if (cktId[i]) {
						$("#advance_search_cktid").append('<option value="' + cktId[i] + '">' + cktId[i] + '</option>');
					}
				}
			}

			$("#advance_search_cktid").select2(options);

			if (city.length) {
				for (var i = 0; i < city.length; i++) {
					if (city[i]) {
						$("#advance_search_city").append('<option value="' + city[i] + '">' + city[i] + '</option>');
					}
				}
			}

			$("#advance_search_city").select2(options);
		}
		/*
		This function applies Basic Filter
		 */
		var markersToShow= [];
		this.applyBasicFilter = function() {
			var technologyValue = $("#technology").val();
			// global_this.markersVectorLayer.strategies[0].deactivate();
			var vendorValue = $("#vendor").val();
			var stateValue = $("#state").val();
			var cityValue = $("#city").val();
			markersToHide= [];
			markersToShow= [];
			stationsLoop: for (var i = 0; i < filtered_data.length; i++) {
				var markerData = filtered_data[i];
				var bsMarker = bsMarkerObj[markerData.name];
				if (true) {
					if (technologyValue === "" && vendorValue === "" && stateValue === "" && cityValue === "") {
						markersToShow.push(bsMarkerObj[markerData.name]);
					} else {
						if (technologyValue !== "") {
							var baseStationTechnology = markerData.sector_ss_technology;
							baseStationTechnology= $.trim(baseStationTechnology.toLowerCase());
							technologyValue = $.trim(technologyValue.toLowerCase());
							if(baseStationTechnology.indexOf(technologyValue) !== -1) {
								global_this.showStationMarker(markerData);
							} else {
								markersToHide.push(markerData);
								// global_this.hideStationMarkers(markerData);
								continue stationsLoop;
							}
						}

						if (vendorValue !== "") {
							var baseStationVendor = markerData.sector_ss_vendor;
							baseStationVendor= $.trim(baseStationVendor.toLowerCase());
							vendorValue = $.trim(vendorValue.toLowerCase());
							if (vendorValue === baseStationVendor) {
								global_this.showStationMarker(markerData);
							} else {
								markersToHide.push(markerData);
								// global_this.hideStationMarkers(markerData);
								continue stationsLoop;
							}
						}

						if (stateValue !== "") {
							var baseStationState = markerData.data.state;
							baseStationState= $.trim(baseStationState.toLowerCase());
							stateValue = $.trim(stateValue.toLowerCase());
							if (baseStationState === stateValue) {
								global_this.showStationMarker(markerData);
							} else {
								markersToHide.push(markerData);
								// global_this.hideStationMarkers(markerData);
								continue stationsLoop;
							}
						}

						if (cityValue !== "") {
							var baseStationCity = markerData.data.city;
							baseStationCity= $.trim(baseStationCity.toLowerCase());
							cityValue = $.trim(cityValue.toLowerCase());
							if (baseStationCity === cityValue) {
								global_this.showStationMarker(markerData);
							} else {
								markersToHide.push(markerData);
								// global_this.hideStationMarkers(markerData);
							}
						}
						markersToShow.push(bsMarkerObj[markerData.name]);
					}
				}
			}
			global_this.markersVectorLayer.removeAllFeatures();
			global_this.markersVectorLayer.addFeatures(markersToShow);
			strategy.recluster();
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
			$("#basic_filter_technology").val('');
			$("#basic_filter_vendor").val('');
			$("#basic_filter_state").val('');
			$("#basic_filter_city").val('');
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
		/*
		This function takes a array of Markers and loop through each list and call prototype method createOpenLayerMarker() to create Marker for it.
		@param markersData {Array for BsData} Array containing Bs to be plotted.
		@param callback {Function} Callback to return when Finished.
		Also we add Marker Data in our variables for future use.
		 */
		var markerVectors = [];
	   function addMarkers(markersData, callback) {

			//Loop through the markersData
			$.each(markersData, function(i, markerData) {

				//Store data in a Object with BS Name as key
				markersDataObj[markerData.name] = markerData;
				//Push data in the Global Variable
				markersDataArray.push(markerData);

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
				var id = markerData.id;
				var name = markerData.name;
				var lon = markerData.data.lon;
				var lat = markerData.data.lat;
				var icon = base_url+"/static/img/icons/bs.png";
				var size = new OpenLayers.Size(whiteMapSettings.size.medium.width, whiteMapSettings.size.medium.height);
				var type = "base_station";
				var additionalInfoObject = { id: id, name: name, type: type, visible: 'true', isSpiderfied: true, dataset: markerData.data.param.base_station, bhInfo: markerData.data.param.backhual, ptLat: lat, ptLon: lon, pointType: type }

				var marker = global_this.createOpenLayerVectorMarker(size, icon, lon, lat, additionalInfoObject);
				markerVectors.push(marker);

				//Store marker in bs marker object
				bsMarkerObj[name] = marker;
				//push marker in markerArray
				markerArray.push(marker);
				
				//base station devices loop
				var total_angle = 360;
				var devices_length = markerData.data.param.sector.length;
				var angleOnWhichDeviceIconToPlace = Math.floor(total_angle / devices_length);
				var current_angle = 0;
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
							defaultIcon:  base_url+"/"+device.markerUrl
						}
						//Create deviceMarker
						var deviceMarker = global_this.createOpenLayerVectorMarker(size, deviceIcon, deviceLatLngObject.lon, deviceLatLngObject.lat, deviceAdditionalInfo);

						global_this.devicesVectorLayer.addFeatures(deviceMarker);
						//Add marker to markerArray
						markerArray.push(deviceMarker);
						//Hide the marker by default

						//Store deviceMarker in a obj for later use.
						if (!deviceMarkerObj[name]) {
							deviceMarkerObj[name] = [];
						}					
						deviceMarkerObj[name].push(deviceMarker);
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
							pointType: sub_station_type
						}
						//Create marker
						// var sub_station_marker = global_this.createOpenLayerMarker(size, sub_station_icon, sub_station_lon, sub_station_lat, subStationAdditionalInfo);
						var sub_station_marker = global_this.createOpenLayerVectorMarker(size, sub_station_icon, sub_station_lon, sub_station_lat, subStationAdditionalInfo);
						//Add marker to markerArray
						markerArray.push(sub_station_marker);

						markerVectors.push(sub_station_marker);
						//Add marker to MarkerLayer
						// global_this.markersLayer.addMarker(sub_station_marker);

						//Store SubStations for later use.
						if (!subStationMarkerObj[device.device_info[0].value]) {
							subStationMarkerObj[device.device_info[0].value] = [];
						}
						subStationMarkerObj[device.device_info[0].value].push(sub_station_marker);

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
									ptLon: lon
								}
								global_this.drawSector(sectorsPointArray, device.color, device.technology, sectorAdditionalInfo, function(sector) {
									global_this.sectorsLayer.addFeatures([sector]);

									//Store CktID in an Object for later use.
									if (!sectorsObj[device.device_info[0].value]) {
										sectorsObj[device.device_info[0].value] = [];
									}
									sectorsObj[device.device_info[0].value].push(sector);
								});

								var lineAdditionalInfo = {
									bsname: name,
									ssname: sub_station_name,
									ckt: device.circuit_id,
									devicename: device.device_info[0].value,
									type: "line"
								}

								var halfPt = Math.floor(sectorsPointArray.length / (+2));

								var line = global_this.drawLine(sectorsPointArray[halfPt].lon, sectorsPointArray[halfPt].lat, sub_station_lon, sub_station_lat, device.color, lineAdditionalInfo);

								global_this.linesLayer.addFeatures([line]);

								//Store CktID in an Object for later use.
								if (!cktLinesObj[device.device_info[0].value]) {
									cktLinesObj[device.device_info[0].value] = [];
								}
								cktLinesObj[device.device_info[0].value].push(line);
							});
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
							//Add line to the LinesLayer
							global_this.linesLayer.addFeatures([line]);

							//Store CktID in an Object for later use.
							if (!cktLinesObj[device.device_info[0].value]) {
								cktLinesObj[device.device_info[0].value] = [];
							}
							cktLinesObj[device.device_info[0].value].push(line);
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
				// url: 'Scripts/data_json/page_' + i + '.json',
				type: 'get',
				dataType: 'json',
				//Success callback
				success: function(response) {

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
									// $("#current_status").html('Loaded');

									global_this.markersVectorLayer.addFeatures(markerVectors);
									strategy.activate();

									global_this.populateBasicFilterDropdowns();
									global_this.populateAdvanceSearchDropdowns();
									global_this.populateAdvanceFilterDropdown();
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

		//Call prototype method createOpenLayerMap() to create White Map and in the callback, Bind Click control to map. Start Ajax Request to get Data.
		this.createOpenLayerMap(function() {			
			//start ajax request
			startAjaxRequest(1);
		});
	}
}