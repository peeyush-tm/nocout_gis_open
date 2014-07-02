/*Global Variables*/
var earth_that = "",
	mapsLibInstance = "",
	ge = "",
	devices_earth = [],
	main_devices_data_earth = [],
	appliedFilterObj_earth = {},
	devicesObject_earth = {},
	hitCounter = 1,
	showLimit = 0,
	devicesCount = 0,
	counter = -999;

/**
 * This class is used to plot the BS & SS on the google earth & performs their functionality.
 * @class earth_devicePlottingLib
 * @method googleEarthClass
 * @uses jQuery
 * @uses Google Earth
 * @uses jQuery UI
 * Coded By :- Yogender Purohit
 */
function googleEarthClass() {

	/*Store the reference of current pointer in a global variable*/
	earth_that = this;

	/**
	 * This function creates google earth on the given domElement
	 * @class earth_devicePlottingLib
	 * @method createGoogleEarth
	 * @param domElement "String", It is the dom element on which google earth is to be created.
	 */
	this.createGoogleEarth = function(domElement) {

		google.earth.createInstance(domElement, earth_that.earthInitCallback, earth_that.earthFailureCallback);
	};

	/**
	 * This function handles the initialization callback of google earth creation function
	 * @class earth_devicePlottingLib
	 * @method earthInitCallback
	 * @param pluginInstance {JSON Object}, It is the JSON object returned from google earth create instance function on successful creation of google earth.
	 */
	this.earthInitCallback = function(pluginInstance) {
				

		ge = pluginInstance;
		ge.getWindow().setVisibility(true);

		/*Set current position of google earth to india*/
		var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);
		lookAt.setLatitude(21.0000);
		lookAt.setLongitude(78.0000);

		// Update the view in Google Earth 
		ge.getView().setAbstractView(lookAt); 
		// add a navigation control
		ge.getNavigationControl().setVisibility(ge.VISIBILITY_AUTO);

		// add some layers
		ge.getLayerRoot().enableLayerById(ge.LAYER_BORDERS, true);
		ge.getLayerRoot().enableLayerById(ge.LAYER_ROADS, true);

		/*Call get devices function*/
		earth_that.getDevicesData_earth();
	};

	/**
	 * This function handles the failure callback of google earth creation function
	 * @class earth_devicePlottingLib
	 * @method earthFailureCallback
	 * @param errorCode {JSON Object}, It is the JSON object returned from google earth create instance function when google earth creation was not successful or failed.
	 */
	this.earthFailureCallback = function(errorCode) {
		console.log(errorCode);
	};

	/**
	 * This function fetch the BS & SS from python API.
	 * @class earth_devicePlottingLib
	 * @function getDevicesData_earth
	 */
	this.getDevicesData_earth = function() {

		if(counter > 0 || counter == -999) {

			/*Show The loading Icon*/
			$("#loadingIcon").show();

			/*Disable the refresh button*/
			$("#resetFilters").button("loading");

			/*Ajax call to the API*/
			$.ajax({
				crossDomain: true,
				url : "../../device/stats/",
				// url : "../../static/new_format.json",
				type : "GET",
				dataType : "json",
				/*If data fetched successful*/
				success : function(result) {
					
					if(result.data.objects != null) {

						hitCounter = hitCounter + 1;
						/*First call case*/
						if(devicesObject_earth.data == undefined) {

							/*Save the result json to the global variable for global access*/
							devicesObject_earth = result;
							/*This will update if any filer is applied*/
							devices_earth = devicesObject_earth.data.objects.children;
							/*This will changes only when data re-fetched*/
							main_devices_data_earth = devicesObject_earth.data.objects.children;
						} else {

							devices_earth = devices_earth.concat(result.data.objects.children);
						}

						/*Update the device count with the received data*/
						devicesCount = devicesObject_earth.data.meta.total_count;

						/*Update the device count with the received data*/
						showLimit = devicesObject_earth.data.meta.limit;

						if(counter == -999) {
							counter = Math.round(devicesCount/showLimit);
						}
						
						if(devicesObject_earth.success == 1) {

							/*Check that any filter is applied or not*/
							var appliedFilterLength_earth = Object.keys(appliedFilterObj_earth).length;

							if(appliedFilterLength_earth > 0) {
								/*If any filter is applied then plot the fetch data as per the filters*/
								earth_that.applyFilter(appliedFilterObj_earth);
							} else {
								/*Call the plotDevices_earth to show the markers on the map*/
								earth_that.plotDevices_earth(devices_earth);
							}

							/*Call the function after 3 sec.*/
							setTimeout(function() {
									
								earth_that.getDevicesData_earth();
							},3000);

						} else {

							// earth_that.recallServer_earth();
							/*Hide The loading Icon*/
							$("#loadingIcon").hide();

							/*Enable the refresh button*/
							$("#resetFilters").button("complete");
						}
						/*Decrement the counter*/
						counter = counter - 1;

					} else {

						// earth_that.recallServer_earth();
						/*Hide The loading Icon*/
						$("#loadingIcon").hide();

						/*Enable the refresh button*/
						$("#resetFilters").button("complete");
					}

				},
				error : function(err) {
					console.log(err);
				}
			});
		} else {
			/*Hide The loading Icon*/
			$("#loadingIcon").hide();

			/*Enable the refresh button*/
			$("#resetFilters").button("complete");
		}
	};

	/**
     * This function is used to populate the markers on the google earth
     * @class earth_devicePlottingLib
     * @method plotDevices_earth
     * @param resultantMarkers [JSON Objet Array] It is the devies object array
	 */
	this.plotDevices_earth = function(resultantMarkers) {

		/*Assign the potting devices to the 'devices' global variables*/
		devices_earth = resultantMarkers;
		for(var i=0;i<resultantMarkers.length;i++) {

			/*Create BS info window HTML string*/
			var bs_infoTable = "<table class='table table-bordered'><tbody>";
			/*Fetch BS information*/
			for(var x=0;x<resultantMarkers[i].data.param.base_station.length;x++) {

				if(resultantMarkers[i].data.param.base_station[x].show == 1) {
					bs_infoTable += "<tr><td>"+resultantMarkers[i].data.param.base_station[x].title+"</td><td>"+resultantMarkers[i].data.param.base_station[x].value+"</td></tr>";
				}
			}
			/*Set lat-lon*/
			bs_infoTable += "<tr><td>Lat, Long</td><td>"+resultantMarkers[i].data.lat+", "+resultantMarkers[i].data.lon+"</td></tr>";
			bs_infoTable += "</tbody></table>";
			/*Perf value of BS*/
			var perfContent = "<h1><i class='fa fa-signal'></i>  "+resultantMarkers[i].data.perf+"</h1>";
			/*Final infowindow content string*/
			var bs_windowContent = "<div class='windowContainer'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>  BS</h4></div><div class='box-body'><div class='windowInfo' align='center'>"+bs_infoTable+"</div><div class='perf'>"+perfContent+"</div><div class='clearfix'></div></div></div></div>";

			// Create BS placemark.
			var bs_placemark = ge.createPlacemark('');
			// Define a custom icon.
			var bs_icon = ge.createIcon('');
			bs_icon.setHref(window.location.origin+"/"+resultantMarkers[i].data.markerUrl);
			var style = ge.createStyle(''); //create a new style
			style.getIconStyle().setIcon(bs_icon); //apply the icon to the style
			bs_placemark.setStyleSelector(style); //apply the style to the placemark
			bs_placemark.setDescription(bs_windowContent);
			// Set the placemark's location.
			var point = ge.createPoint('');
			point.setLatitude(resultantMarkers[i].data.lat);
			point.setLongitude(resultantMarkers[i].data.lon);
			bs_placemark.setGeometry(point);
			// Add the placemark to Earth.
			ge.getFeatures().appendChild(bs_placemark);


		    var SSCount = resultantMarkers[i].children.length;  
		    /*Loop for the number of SS & their links with the master*/
		    for(var j=0;j<SSCount;j++) {
		    	/*Create SS info window HTML string*/
		    	var ss_infoTable = "<table class='table table-bordered'><tbody>";
		    	/*Fetch SS information*/
				for(var y=0;y<resultantMarkers[i].children[j].data.param.sub_station.length;y++) {
					if(resultantMarkers[i].children[j].data.param.sub_station[y].show == 1) {
							ss_infoTable += "<tr><td>"+resultantMarkers[i].children[j].data.param.sub_station[y].title+"</td><td>"+resultantMarkers[i].children[j].data.param.sub_station[y].value+"</td></tr>";
					}
				}
				/*Set lat-lon*/
				ss_infoTable += "<tr><td>Lat, Long</td><td>"+resultantMarkers[i].children[j].data.lat+", "+resultantMarkers[i].children[j].data.lon+"</td></tr>";
				ss_infoTable += "</tbody></table>";
				/*Perf value of SS*/
				var ss_perfContent = "<h1><i class='fa fa-signal'></i>  "+resultantMarkers[i].children[j].data.perf+"</h1>";
				/*Final infowindow content string*/
				var ss_windowContent = "<div class='windowContainer'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>  SS</h4></div><div class='box-body'><div class='windowInfo' align='center'>"+ss_infoTable+"</div><div class='perf'>"+ss_perfContent+"</div><div class='clearfix'></div></div></div></div>";

		    	// Create SS placemark.
				var ss_placemark = ge.createPlacemark('');
				// Define a custom icon.
				var ss_icon = ge.createIcon('');
				ss_icon.setHref(window.location.origin+"/"+resultantMarkers[i].children[j].data.markerUrl);
				var style = ge.createStyle(''); //create a new style
				style.getIconStyle().setIcon(ss_icon); //apply the icon to the style
				ss_placemark.setStyleSelector(style); //apply the style to the placemark
				ss_placemark.setDescription(ss_windowContent);
				// Set the ss_placemark's location.  
				var point = ge.createPoint('');
				point.setLatitude(resultantMarkers[i].children[j].data.lat);
				point.setLongitude(resultantMarkers[i].children[j].data.lon);
				ss_placemark.setGeometry(point);
				// Add the ss_placemark to Earth.
				ge.getFeatures().appendChild(ss_placemark);

				var startLat = "",
					startLon = "",
					endLat = "",
					endLon = "";
				/*If device are of P2P type*/
				if(resultantMarkers[i].type == "P2P") {
					/*Create object for Link Line Between Master & Slave*/
					startLat = resultantMarkers[i].data.lat;
					startLon = resultantMarkers[i].data.lon;
					endLat = resultantMarkers[i].children[j].data.lat;
					endLon = resultantMarkers[i].children[j].data.lon;

				} else {
					var lat = resultantMarkers[i].data.lat;
					var lon = resultantMarkers[i].data.lon;
					var rad = resultantMarkers[i].children[j].data.radius;
					var azimuth = resultantMarkers[i].children[j].data.azimuth_angle;
					var beam_width = resultantMarkers[i].children[j].data.beam_width;
					var sector_color = resultantMarkers[i].children[j].data.sector_color;
					var sectorInfo = resultantMarkers[i].children[j].data.param.sector_info;
					var orientation = $.trim(resultantMarkers[i].children[j].data.sector_orientation);
					
					/*Call createSectorData function to get the points array to plot the sector on google earth.*/
					mapsLibInstance.createSectorData(lat,lon,rad,azimuth,beam_width,orientation,function(pointsArray) {
						
						/*Plot sector on google earth with the retrived points*/
						earth_that.plotSector_earth(lat,lon,pointsArray,sectorInfo,sector_color);

						var halfPt = Math.floor(pointsArray.length / (+2));
						// Create object for Link Line Between BS & SS
						startLat = pointsArray[halfPt].lat;
						startLon = pointsArray[halfPt].lon;
						endLat = resultantMarkers[i].children[j].data.lat;
						endLon = resultantMarkers[i].children[j].data.lon;

					});
				}

				if(resultantMarkers[i].children[j].data.show_link == 1) {

					/*Create info window HTML string for link(line).*/
					var line_infoTable = "",
						bs_info = {};
					if($.trim(resultantMarkers[i].type) == "P2P") {
						bs_info = resultantMarkers[i].data.param.base_station;
					} else {
						bs_info = resultantMarkers[i].children[j].data.param.sector_info;
					}
					/*Line Information HTML String*/
					line_infoTable += "<table class='table table-bordered'><thead><th>BS-Sector Info</th><th>BS-Sector Perf</th><th>SS Info</th><th>SS Perf</th></thead><tbody>";
					line_infoTable += "<tr>";
					/*BS or Sector Info Start*/
					line_infoTable += "<td>";	
					line_infoTable += "<table class='table table-hover innerTable'><tbody>";
					/*Loop for ss info object array*/
					for(var p=0;p<resultantMarkers[i].children[j].data.param.sub_station.length;p++) {

						if(resultantMarkers[i].children[j].data.param.sub_station[p].show == 1) {
							line_infoTable += "<tr><td>"+resultantMarkers[i].children[j].data.param.sub_station[p].title+"</td><td>"+resultantMarkers[i].children[j].data.param.sub_station[p].value+"</td></tr>";
						}
					}
					line_infoTable += "<tr><td>Lat, Long</td><td>"+resultantMarkers[i].children[j].data.lat+", "+resultantMarkers[i].children[j].data.lon+"</td></tr>";
					line_infoTable += "</tbody></table>";			
					line_infoTable += "</td>";
					/*BS-Sector Info End*/
					/*BS-Sector Performance Start*/
					line_infoTable += "<td style='vertical-align:middle;text-align: center;'><h1><i class='fa fa-signal'></i>  "+resultantMarkers[i].children[j].data.perf+"</h1></td>";
					/*BS-Sector Performance End*/
					/*SS Info Start*/
					line_infoTable += "<td>";			
					line_infoTable += "<table class='table table-hover innerTable'><tbody>";
					/*Loop for BS or Sector info object array*/
					for(var q=0;q<bs_info.length;q++) {

						if(bs_info[q].show == 1) {
							line_infoTable += "<tr><td>"+bs_info[q].title+"</td><td>"+bs_info[q].value+"</td></tr>";
						}
					}
					line_infoTable += "<tr><td>Lat, Long</td><td>"+resultantMarkers[i].data.lat+", "+resultantMarkers[i].data.lon+"</td></tr>";
					line_infoTable += "</tbody></table>";		
					line_infoTable += "</td>";
					/*SS Info End*/
					/*SS Performance Start*/
					line_infoTable += "<td style='vertical-align:middle;text-align: center;'><h1><i class='fa fa-signal'></i>  "+resultantMarkers[i].data.perf+"</h1></td>";
					/*SS Performance End*/
					line_infoTable += "</tr>";
					line_infoTable += "</tbody></table>";
					
					/*Concat infowindow content*/
					var line_windowContent = "<div class='windowContainer'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i> BS-SS</h4></div><div class='box-body'>"+line_infoTable+"<div class='clearfix'></div></div></div></div>";

					// Create link(line) placemark
					var lineStringPlacemark = ge.createPlacemark('');
					// Create the LineString
					var lineString = ge.createLineString('');
					lineStringPlacemark.setGeometry(lineString);
					// Add LineString points
					lineString.getCoordinates().pushLatLngAlt(startLat, startLon, 0);
					lineString.getCoordinates().pushLatLngAlt(endLat, endLon, 0);
					lineStringPlacemark.setDescription(line_windowContent);
					// Create a style and set width and color of line
					lineStringPlacemark.setStyleSelector(ge.createStyle(''));
					var lineStyle = lineStringPlacemark.getStyleSelector().getLineStyle();
					lineStyle.setWidth(2);
					var link_color_obj = resultantMarkers[i].children[j].data.link_color;
					lineStyle.getColor().setA(200);
					lineStyle.getColor().setB(link_color_obj.b);
					lineStyle.getColor().setG(link_color_obj.g);
					lineStyle.getColor().setR(link_color_obj.r);
					// Add the feature to Earth
					ge.getFeatures().appendChild(lineStringPlacemark);				
				}/*SHOW_LINK condition ends*/
			}
		}
	};

	/**
	 * This function plot the sector for given lat-lon points
	 * @class earth_devicePlottingLib
	 * @method plotSector_earth.
	 * @param Lat "Number", It contains lattitude of any point.
	 * @param Lng "Number", It contains longitude of any point.
	 * @param pointsArray [Array], It contains the points lat-lon object array.
	 * @param sectorInfo {JSON Object Array}, It contains the information about the sector which are shown in info window.
	 * @param bgColor {JSON Object}, It contains the RGBA format color code JSON object.
	 */
	this.plotSector_earth = function(lat,lng,pointsArray,sectorInfo,bgColor) {

		/*Create Sector info window HTML string*/
    	var sector_infoTable = "<table class='table table-bordered'><tbody>";
    	/*Fetch SS information*/
		for(var y=0;y<sectorInfo.length;y++) {
			if(sectorInfo[y].show == 1) {
					sector_infoTable += "<tr><td>"+sectorInfo[y].title+"</td><td>"+sectorInfo[y].value+"</td></tr>";
			}
		}
		/*Set lat-lon*/
		sector_infoTable += "<tr><td>Lat, Long</td><td>"+lat+", "+lng+"</td></tr>";
		sector_infoTable += "</tbody></table>";
		/*Final infowindow content string*/
		var sector_windowContent = "<div class='windowContainer'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>  Sector</h4></div><div class='box-body'><div class='windowInfo' align='center'>"+sector_infoTable+"</div><div class='clearfix'></div></div></div></div>";

		// Create the placemark.
		var sectorPolygonObj = ge.createPlacemark('');

		// Create sector polygon.
		var sector_polygon = ge.createPolygon('');
		sector_polygon.setAltitudeMode(ge.ALTITUDE_RELATIVE_TO_GROUND);
		sectorPolygonObj.setGeometry(sector_polygon);

		// Add points for poly coordinates.
		var polyPoints = ge.createLinearRing('');
		polyPoints.setAltitudeMode(ge.ALTITUDE_RELATIVE_TO_GROUND);
		
		/*Loop to get the polygon point n plot the coordinates*/
		for(var i=0;i<pointsArray.length;i++) {
			polyPoints.getCoordinates().pushLatLngAlt(pointsArray[i].lat, pointsArray[i].lon, 700);
		}

		sector_polygon.setOuterBoundary(polyPoints);
		//Create a style and set width and color of line
		sectorPolygonObj.setStyleSelector(ge.createStyle(''));
		/*Set info window content for sector*/
		sectorPolygonObj.setDescription(sector_windowContent);
		var lineStyle = sectorPolygonObj.getStyleSelector().getLineStyle();
		lineStyle.setWidth(1);
		lineStyle.getColor().setA(200);
		lineStyle.getColor().setB(102);
		lineStyle.getColor().setG(101);
		lineStyle.getColor().setR(99);

		// Color can also be specified by individual color components.
		var polyColor = sectorPolygonObj.getStyleSelector().getPolyStyle().getColor();
		polyColor.setA(200);
		polyColor.setB(bgColor.b);
		polyColor.setG(bgColor.g);
		polyColor.setR(bgColor.r);
		// Add the placemark to Earth.
		ge.getFeatures().appendChild(sectorPolygonObj);
	};

	/**
	 * This function filters the BS data from devices object as per the applied rule
	 * @class earth_devicePlottingLib
	 * @method applyFilter_earth
	 * @param filtersArray [JSON Array] It is an object array of filters with keys
	 */
	this.applyFilter_earth = function(filtersArray) {

		appliedFilterObj_earth = filtersArray;

		var filterKey = [],
			filteredData = [],
			masterIds = [];

		/*Fetch the keys from the filter array*/
		$.each(filtersArray, function(key, value) {

		    filterKey.push(key);
		});

	 	if(main_devices_data_earth.length > 0) {

	 		for(var i=0;i<main_devices_data_earth.length;i++) {

 				var master = main_devices_data_earth[i];

	 			/*Conditions as per the number of filters*/
	 			if(filterKey.length == 1) {

 					if(master.data[filterKey[0]].toLowerCase() == filtersArray[filterKey[0]].toLowerCase()) {

	 					/*Check For The Duplicacy*/
	 					if(masterIds.indexOf(master.id) == -1) {

	 						/*Save the BS id's to array to remove duplicacy*/
	 						masterIds.push(master.id);

	 						filteredData.push(main_devices_data_earth[i]);
	 					}
	 				}

	 			} else if(filterKey.length == 2) {

 					if((master.data[filterKey[0]].toLowerCase() == filtersArray[filterKey[0]].toLowerCase()) && (master.data[filterKey[1]].toLowerCase() == filtersArray[filterKey[1]].toLowerCase())) {

	 					/*Check For The Duplicacy*/
	 					if(masterIds.indexOf(master.id) == -1) {

	 						/*Save the BS id's to array to remove duplicacy*/
	 						masterIds.push(master.id);

	 						filteredData.push(main_devices_data_earth[i]);
	 					}
	 				}
	 			} else if(filterKey.length == 3) {

	 				if((master.data[filterKey[0]].toLowerCase() == filtersArray[filterKey[0]].toLowerCase()) && (master.data[filterKey[1]].toLowerCase() == filtersArray[filterKey[1]].toLowerCase()) && (master.data[filterKey[2]].toLowerCase() == filtersArray[filterKey[2]].toLowerCase())) {

	 					/*Check For The Duplicacy*/
	 					if(masterIds.indexOf(master.id) == -1) {

	 						/*Save the BS id's to array to remove duplicacy*/
	 						masterIds.push(master.id);

	 						filteredData.push(main_devices_data_earth[i]);
	 					}
	 				}
	 			} else if(filterKey.length == 4) {

	 				if((master.data[filterKey[0]].toLowerCase() == filtersArray[filterKey[0]].toLowerCase()) && (master.data[filterKey[1]].toLowerCase() == filtersArray[filterKey[1]].toLowerCase()) && (master.data[filterKey[2]].toLowerCase() == filtersArray[filterKey[2]].toLowerCase()) && (master.data[filterKey[3]].toLowerCase() == filtersArray[filterKey[3]].toLowerCase())) {

	 					/*Check For The Duplicacy*/
	 					if(masterIds.indexOf(master.id) == -1) {

	 						/*Save the BS id's to array to remove duplicacy*/
	 						masterIds.push(master.id);

	 						filteredData.push(main_devices_data_earth[i]);
	 					}
	 				}
	 			}
	 		}
	 		/*Check that after applying filters any data exist or not*/
	 		if(filteredData.length === 0) {

	 			bootbox.alert("User Don't Have Any Devies For Selected Filters");
	 			$("#resetFilters").click();

	 		} else {

				/*Reset the markers, polyline & filters*/
	 			earth_that.clearEarthElements();

				masterMarkersObj = [];
				slaveMarkersObj = [];

				/*Populate the map with the filtered markers*/
	 			earth_that.plotDevices_earth(filteredData);
	 		}	 		
	 	}	
	};

	/**
     * This function resets the global variables & again call the api calling function after given timeout i.e. 5 minutes
     * @class earth_devicePlottingLib
     * @method recallServer_earth
     */
    this.recallServer_earth = function() {

    	/*Hide The loading Icon*/
		$("#loadingIcon").hide();

		/*Enable the refresh button*/
		$("#resetFilters").button("complete");
		

    	setTimeout(function() {
			
			/*Hide The loading Icon*/
			$("#loadingIcon").show();

			/*Enable the refresh button*/
			$("#resetFilters").button("loading");

			/*Clear all the elements from google earth*/
			earth_that.clearEarthElements();

			/*Reset Global Variables*/
			earth_that.resetVariables_earth();
			
			/*Recall the API*/
			earth_that.getDevicesData_earth();

		},300000);
    };

    /**
     * This function will clear all the elements from google earth
     * @class earth_devicePlottingLib
     * @method clearEarthElements
     */
    this.clearEarthElements = function() {

    	var features = ge.getFeatures(); 
        while (features.getFirstChild()) { 
           features.removeChild(features.getFirstChild()); 
        }
    };


    /**
     * This function will clear all the elements from google earth
     * @class earth_devicePlottingLib
     * @method resetVariables_earth
     */
    this.resetVariables_earth = function() {

 		devices_earth = [];
 		appliedFilterObj_earth = {};
		devicesObject_earth = {};
		hitCounter = 1;
		showLimit = 0;
		devicesCount = 0;
		counter = -999;
    };
}