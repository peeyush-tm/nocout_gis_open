/*Global Variables*/
var earth_self = "",
	mapsLibInstance = "",
	ge = "",
	plotted_ss_earth = [],
	plotterLinks_earth = [],
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
 * @uses jQuery
 * @uses Google Earth
 * @uses jQuery UI
 * Coded By :- Yogender Purohit
 */
function googleEarthClass() {

	/*Store the reference of current pointer in a global variable*/
	earth_self = this;

	/**
	 * This function creates google earth on the given domElement
	 * @method createGoogleEarth
	 * @param domElement {String}, It is the dom element on which google earth is to be created.
	 */
	this.createGoogleEarth = function(domElement) {

		google.earth.createInstance(domElement, earth_self.earthInitCallback, earth_self.earthFailureCallback);
	};

	/**
	 * This function handles the initialization callback of google earth creation function
	 * @method earthInitCallback
	 * @param pluginInstance {Object}, It is the JSON object returned from google earth create instance function on successful creation of google earth.
	 */
	this.earthInitCallback = function(pluginInstance) {
		console.log(pluginInstance);
		// var mapTypeId = myMap.getMapTypeId();
		// myMapObject.setMapTypeId(google.maps.MapTypeId.SATELLITE);

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
		earth_self.getDevicesData_earth();
	};

	/**
	 * This function handles the failure callback of google earth creation function
	 * @method earthFailureCallback
	 * @param errorCode {Object}, It is the JSON object returned from google earth create instance function when google earth creation was not successful or failed.
	 */
	this.earthFailureCallback = function(errorCode) {
		// console.log(errorCode);
		$.gritter.add({
            // (string | mandatory) the heading of the notification
            title: 'Google Earth',
            // (string | mandatory) the text inside the notification
            text: errorCode,
            // (bool | optional) if you want it to fade out on its own or just sit there
            sticky: true
        });
	};

	/**
	 * This function fetch the BS & SS from python API.
	 * @method getDevicesData_earth
	 */
	this.getDevicesData_earth = function() {

		var get_param_filter = [];
		/*If any advance filters are applied then pass the advance filer with API call else pass blank array*/
		if(appliedAdvFilter.length > 0) {
			get_param_filter = appliedAdvFilter;
		} else {
			get_param_filter = [];
		}

		if(counter > 0 || counter == -999) {

			/*Show The loading Icon*/
			$("#loadingIcon").show();

			/*Disable the refresh button*/
			$("#resetFilters").button("loading");

			/*Ajax call to the API*/
			$.ajax({
				crossDomain: true,
				url : window.location.origin+"/"+"device/stats/?filters="+JSON.stringify(get_param_filter),
				// url : window.location.origin+"/"+"static/new_format.json",
				type : "GET",
				dataType : "json",
				/*If data fetched successful*/
				success : function(result) {
					
					if(result.success == 1) {

						if(result.data.objects != null) {

							hitCounter = hitCounter + 1;

							if(result.data.objects.children.length > 0) {

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

								/*Check that any advance filter is applied or not*/
								if(appliedAdvFilter.length <= 0) {

									/*applied basic filters count*/
									var appliedFilterLength_earth = Object.keys(appliedFilterObj_earth).length;

									/*Check that any basic filter is applied or not*/
									if(appliedFilterLength_earth > 0) {
										/*If any filter is applied then plot the fetch data as per the filters*/
										earth_self.applyFilter_earth(appliedFilterObj_earth);
									} else {
										/*Call the plotDevices_earth to show the markers on the map*/
										earth_self.plotDevices_earth(devices_earth,"base_station");
									}
								}

								/*Hide The loading Icon*/
								$("#loadingIcon").hide();

								/*Enable the refresh button*/
								$("#resetFilters").button("complete");

								/*Call the function after 3 sec.*/
								setTimeout(function() {
										
									earth_self.getDevicesData_earth();
								},3000);

							} else {
								$.gritter.add({
						            // (string | mandatory) the heading of the notification
						            title: 'Googole Earth - No Data',
						            // (string | mandatory) the text inside the notification
						            text: 'No Devices Found',
						            // (bool | optional) if you want it to fade out on its own or just sit there
						            sticky: true
						        });
							}

							/*Decrement the counter*/
							counter = counter - 1;

						} else {

							setTimeout(function(e) {
								earth_self.recallServer_earth();
							},20000);
							/*Hide The loading Icon*/
							$("#loadingIcon").hide();

							/*Enable the refresh button*/
							$("#resetFilters").button("complete");
						}

					} else {

						$.gritter.add({
				            // (string | mandatory) the heading of the notification
				            title: 'Google Earth - Server Error',
				            // (string | mandatory) the text inside the notification
				            text: devicesObject_earth.message,
				            // (bool | optional) if you want it to fade out on its own or just sit there
				            sticky: true
				        });

						/*Hide The loading Icon*/
						$("#loadingIcon").hide();

						/*Enable the refresh button*/
						$("#resetFilters").button("complete");

						setTimeout(function(e) {
							earth_self.recallServer_earth();
						},20000);

					}

				},
				error : function(err) {
					// console.log(err);
					$.gritter.add({
			            // (string | mandatory) the heading of the notification
			            title: 'Google Earth - Server Error',
			            // (string | mandatory) the text inside the notification
			            text: err.statusText,
			            // (bool | optional) if you want it to fade out on its own or just sit there
			            sticky: true
			        });
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
     * This function is used to populate the BS & SS on the google earth
     * @method plotDevices_earth
     * @param devicesList {Object Array}, It is the devices object array
     * @uses gmap_devicePlottingLib
	 */
	this.plotDevices_earth = function(devicesList,station_type) {

		var resultantMarkers = [];

		if($.trim(station_type) == "base_station") {
			resultantMarkers = devicesList;			
		} else {			
			resultantMarkers = devicesList.ssList;
		}

		for(var i=0;i<resultantMarkers.length;i++) {

			var window_name = "",
				dev_technology = "",
				sectorsDetail = [];

			/*Create BS info window HTML string*/
			var bs_infoTable = "<table class='table table-bordered'><tbody>";

			/*True when we are plotting base station devices & their elements*/
			if($.trim(station_type) == "base_station") {

				/*Fetch BS information*/
				for(var x=0;x<resultantMarkers[i].data.param.base_station.length;x++) {

					if(resultantMarkers[i].data.param.base_station[x].show == 1) {
						bs_infoTable += "<tr><td>"+resultantMarkers[i].data.param.base_station[x].title+"</td><td>"+resultantMarkers[i].data.param.base_station[x].value+"</td></tr>";
					}
				}
				/*Set lat-lon*/
				bs_infoTable += "<tr><td>Lat, Long</td><td>"+resultantMarkers[i].data.lat+", "+resultantMarkers[i].data.lon+"</td></tr>";
				
				window_name = "Base Station Info";
				/*Fetch Backhaul information*/
				bs_infoTable += "<tr><td colspan='2'><b>Backhaul Info</b></td></tr>";
				for(var y=0;y<resultantMarkers[i].data.param.backhual.length;y++) {

					if(resultantMarkers[i].data.param.backhual[y].show == 1) {
						bs_infoTable += "<tr><td>"+resultantMarkers[i].data.param.backhual[y].title+"</td><td>"+resultantMarkers[i].data.param.backhual[y].value+"</td></tr>";
					}
				}
				/*Device Technology*/
				dev_technology = resultantMarkers[i].data.technology;

				/*Sectors*/
				sectorsDetail = resultantMarkers[i].data.param.sector;

			/*In case of sub station devices*/
			} else {

				window_name = "Sub Station Info";
				dev_technology = devicesList.technology;

				/*Fetch SS information*/
				for(var x=0;x<resultantMarkers[i].data.param.sub_station.length;x++) {

					if(resultantMarkers[i].data.param.sub_station[x].show == 1) {
						bs_infoTable += "<tr><td>"+resultantMarkers[i].data.param.sub_station[x].title+"</td><td>"+resultantMarkers[i].data.param.sub_station[x].value+"</td></tr>";
					}
				}
				/*Set lat-lon*/
				bs_infoTable += "<tr><td>Lat, Long</td><td>"+resultantMarkers[i].data.lat+", "+resultantMarkers[i].data.lon+"</td></tr>";
			}

			bs_infoTable += "</tbody></table>";

			/*Final infowindow content string*/
			var bs_windowContent = "<div class='windowContainer'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>  "+window_name+"</h4></div><div class='box-body'><div class='' align='center'>"+bs_infoTable+"</div><div class='clearfix'></div></div></div></div>";

			// Create BS placemark.
			var bs_placemark = ge.createPlacemark('');
			// Define a custom icon.
			var bs_icon = ge.createIcon('');
			bs_icon.setHref(window.location.origin+"/"+resultantMarkers[i].data.markerUrl);
			var style = ge.createStyle(''); //create a new style
			style.getIconStyle().setIcon(bs_icon); //apply the icon to the style
			bs_placemark.setStyleSelector(style); //apply the style to the placemark			
			
			var infoObject = {};
			infoObject["technology"] = dev_technology;
			infoObject["device_type"] = station_type;
			infoObject["startLat"] = resultantMarkers[i].data.lat;
			infoObject["startLon"] = resultantMarkers[i].data.lon;
			infoObject["bs_info"] = resultantMarkers[i].data.param.base_station;			
			bs_placemark.setDescription(bs_windowContent+"<input type='hidden' value=' &-&-& "+JSON.stringify(infoObject)+" &-&-& '/><input type='hidden' name='sectorData' value=' -|-|-|- "+JSON.stringify(sectorsDetail)+" -|-|-|- '/>");
			// Set the placemark's location.
			var point = ge.createPoint('');
			point.setLatitude(resultantMarkers[i].data.lat);
			point.setLongitude(resultantMarkers[i].data.lon);
			bs_placemark.setGeometry(point);
			// Add the placemark to Earth.
			ge.getFeatures().appendChild(bs_placemark);

			google.earth.addEventListener(bs_placemark, 'click', function(event) {

				var description = this.getDescription(),
					infoObj = {};

				var infoObj = JSON.parse(description.split("&-&-&")[1]);
				infoObj["sectorsDataset"] = JSON.parse(description.split("-|-|-|-")[1]);

				if($.trim(infoObj.device_type) == "base_station") {

					/*Remove All SS from Google Earth*/
					$.grep(plotted_ss_earth,function(ss) {
						ge.getFeatures().removeChild(ss);
					});

					/*Remove All Links from google earth*/
					$.grep(plotterLinks_earth,function(links) {
						ge.getFeatures().removeChild(links);
					});

					/*Reset SS & links array*/
					plotted_ss_earth = [];
					plotterLinks_earth = [];

					earth_self.plotSubStation_earth(infoObj);
				}
			});

			/*True for base-stations*/
			if(station_type == "base_station") {

				/*In case of PMP & WIMAX*/
				if($.trim(dev_technology) != "P2P" && $.trim(dev_technology) != "PTP") {
		    		
					var sectorsArray = resultantMarkers[i].data.param.sector;

		    		$.grep(sectorsArray,function(sector) { 

		    			var lat = resultantMarkers[i].data.lat;
						var lon = resultantMarkers[i].data.lon;
						var rad = 1;

						/*If radius is greater than 4 Kms then set it to 4.*/
						if(sector.radius > 4 || sector.radius == 0 || sector.radius == null) {
							rad = 4;
						} else {
							rad = sector.radius;
						}

						var azimuth = sector.azimuth_angle;
						var beam_width = sector.beam_width;
						var sector_color = earth_self.makeRgbaObject(sector.color);
						var sectorInfo = sector.info;
						var childSS = JSON.stringify(sector.sub_station);
						var device_technology = $.trim(resultantMarkers[i].data.technology);
						var orientation = $.trim(sector.orientation);
						
						/*Call createSectorData function to get the points array to plot the sector on google earth.*/
						mapsLibInstance.createSectorData(lat,lon,rad,azimuth,beam_width,orientation,function(pointsArray) {
							/*Plot sector on google earth with the retrived points*/
							earth_self.plotSector_earth(lat,lon,pointsArray,sectorInfo,sector_color,childSS,device_technology);
						});
		    		});

				/*In case of PTP*/
				} else {

					var has_ss = resultantMarkers[i].data.param.sector[0].sub_station.length;

					if(has_ss > 0) {

						var ssDataObj = resultantMarkers[i].data.param.sector[0].sub_station[0];
						var ss_infoTable = "<table class='table table-bordered'><tbody>";
						window_name = "Sub Station Info";
						dev_technology = devicesList.technology;

						/*Fetch SS information*/
						for(var x=0;x<ssDataObj.data.param.sub_station.length;x++) {

							if(ssDataObj.data.param.sub_station[x].show == 1) {
								ss_infoTable += "<tr><td>"+ssDataObj.data.param.sub_station[x].title+"</td><td>"+ssDataObj.data.param.sub_station[x].value+"</td></tr>";
							}
						}
						/*Set lat-lon*/
						ss_infoTable += "<tr><td>Lat, Long</td><td>"+ssDataObj.data.lat+", "+ssDataObj.data.lon+"</td></tr>";
						ss_infoTable += "</tbody></table>";

						var ss_windowContent = "<div class='windowContainer'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>  "+window_name+"</h4></div><div class='box-body'><div class='' align='center'>"+ss_infoTable+"</div><div class='clearfix'></div></div></div></div>";

						// Create BS placemark.
						var ss_placemark = ge.createPlacemark('');
						// Define a custom icon.
						var bs_icon = ge.createIcon('');
						bs_icon.setHref(window.location.origin+"/"+ssDataObj.data.markerUrl);
						var style = ge.createStyle(''); //create a new style
						style.getIconStyle().setIcon(bs_icon); //apply the icon to the style
						ss_placemark.setStyleSelector(style); //apply the style to the placemark			
						
						var infoObject = {};
						infoObject["technology"] = dev_technology;
						infoObject["device_type"] = "Sub Station";
						infoObject["startLat"] = ssDataObj.data.lat;
						infoObject["startLon"] = ssDataObj.data.lon;
						infoObject["bs_info"] = ssDataObj.data.param.base_station;			
						ss_placemark.setDescription(ss_windowContent);
						// Set the placemark's location.
						var point = ge.createPoint('');
						point.setLatitude(ssDataObj.data.lat);
						point.setLongitude(ssDataObj.data.lon);
						ss_placemark.setGeometry(point);
						// Add the placemark to Earth.
						ge.getFeatures().appendChild(ss_placemark);

						/*Create link between bs & ss or sector & ss*/
						if(ssDataObj.data.show_link == 1) {
							var startEndObj = {};
						
							startEndObj["startLat"] = resultantMarkers[i].data.lat;
							startEndObj["startLon"] = resultantMarkers[i].data.lon;

							startEndObj["endLat"] = ssDataObj.data.lat;
							startEndObj["endLon"] = ssDataObj.data.lon;

							var linkColor = ssDataObj.data.link_color;
							var bs_info = resultantMarkers[i].data.param.base_station;
							var ss_info = ssDataObj.data.param.sub_station;

							var linkLinePlacemark = earth_self.createLink_earth(startEndObj,linkColor,bs_info,ss_info);
						}
					}/*Has sub-station condition ends*/
				}
				/*end if for base_station case*/
			} else {
				/*Add plotted sub-stations to an array*/
				plotted_ss_earth.push(bs_placemark);

				/*Create link between bs & ss or sector & ss*/
				if(resultantMarkers[i].data.show_link == 1) {

					var startEndObj = {};
					
					startEndObj["startLat"] = devicesList.startLat;
					startEndObj["startLon"] = devicesList.startLon;

					startEndObj["endLat"] = resultantMarkers[i].data.lat;
					startEndObj["endLon"] = resultantMarkers[i].data.lon;

					var linkColor = resultantMarkers[i].data.link_color;
					var bs_info = devicesList.info;
					var ss_info = resultantMarkers[i].data.param.sub_station;

					var linkLinePlacemark = earth_self.createLink_earth(startEndObj,linkColor,bs_info,ss_info);

					/*Push the plotted line to link line array*/
					plotterLinks_earth.push(linkLinePlacemark);
				
				}/*SHOW_LINK condition ends*/

			}/*End of station_type condition else.*/

		}/*End of devices list for loop.*/

		/*Hide The loading Icon*/
		$("#loadingIcon").hide();

		/*Enable the refresh button*/
		$("#resetFilters").button("complete");
	};

	/**
	 * This function plots all the sub-station in given sectors object array.
	 * @method plotSubStation_earth.
	 * @param stationSectorObject {Object} It contains sector object in which SS are present.
	 */
	this.plotSubStation_earth = function(stationSectorObject) {

		if($.trim(stationSectorObject.technology) != "PTP" && $.trim(stationSectorObject.technology) != "P2P") {

			var sector = stationSectorObject.sectorsDataset;

			for(var i=0;i<sector.length;i++) {

				var rad = 1;

				/*If radius is greater than 4 Kms then set it to 4.*/
				if(sector[i].radius > 4 || sector[i].radius == 0 || sector[i].radius == null) {
					rad = 4;
				} else {
					rad = sector[i].radius;
				}

				var azimuth = sector[i].azimuth_angle;
				var beam_width = sector[i].beam_width;
				var sector_color = earth_self.makeRgbaObject(sector[i].color);
				var sectorInfo = sector[i].info;
				var ssList = sector[i].sub_station;
				var orientation = $.trim(sector[i].orientation);				
				
				/*Call createSectorData function to get the points array to plot the sector on google earth.*/
				mapsLibInstance.createSectorData(stationSectorObject.startLat,stationSectorObject.startLon,rad,azimuth,beam_width,orientation,function(pointsArray) {
					
					var infoData = {};
					infoData["technology"] = stationSectorObject.technology;
					
					var halfPt = Math.floor(pointsArray.length / (+2));
					// Create object for Link Line Between Sector & SS
					infoData["startLat"] = pointsArray[halfPt].lat;
					infoData["startLon"] = pointsArray[halfPt].lon;
					infoData["info"] = sectorInfo;
					if(ssList.length > 0) {

						infoData["ssList"] = ssList;
						earth_self.plotDevices_earth(infoData,"sub_station");
					}
				});
			}
		}
	};

	/**
	 * This function create a line between two points
	 * @method createLink_earth.
	 * @param startEndObj {Object}, It contains the start & end points json object.
	 * @param linkColor {String}, It contains the color for link line.
	 * @param bs_info {Object}, It contains the start point information json object.
	 * @param ss_info {Object}, It contains the end point information json object.
	 * @return {Object} lineStringPlacemark, It contains the google earth line Placemark object
	 */
	this.createLink_earth = function(startEndObj,linkColor,bs_info,ss_info) {

		/*Create info window HTML string for link(line).*/
		var line_infoTable = "";		

		/*Line Information HTML String*/
		line_infoTable += "<table class='table table-bordered'><thead><th>BS/Sector Info</th><th>SS Info</th></thead><tbody>";
		line_infoTable += "<tr>";
		/*BS or Sector Info Start*/
		line_infoTable += "<td>";	
		line_infoTable += "<table class='table table-hover innerTable'><tbody>";
		/*Loop for BS or Sector info object array*/
		for(var q=0;q<bs_info.length;q++) {

			if(bs_info[q].show == 1) {
				line_infoTable += "<tr><td>"+bs_info[q].title+"</td><td>"+bs_info[q].value+"</td></tr>";
			}
		}
		line_infoTable += "<tr><td>Lat, Long</td><td>"+startEndObj.startLat+", "+startEndObj.startLon+"</td></tr>";
		line_infoTable += "</tbody></table>";			
		line_infoTable += "</td>";
		/*BS-Sector Info End*/

		/*SS Info Start*/
		line_infoTable += "<td>";			
		line_infoTable += "<table class='table table-hover innerTable'><tbody>";

		/*Loop for SS info object array*/
		for(var p=0;p<ss_info.length;p++) {

			if(ss_info[p].show == 1) {
				line_infoTable += "<tr><td>"+ss_info[p].title+"</td><td>"+ss_info[p].value+"</td></tr>";
			}
		}
		line_infoTable += "<tr><td>Lat, Long</td><td>"+startEndObj.endLat+", "+startEndObj.endLon+"</td></tr>";
		line_infoTable += "</tbody></table>";		
		line_infoTable += "</td>";
		/*SS Info End*/

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
		lineString.getCoordinates().pushLatLngAlt((+startEndObj.startLat), (+startEndObj.startLon), 0);
		lineString.getCoordinates().pushLatLngAlt((+startEndObj.endLat), (+startEndObj.endLon), 0);					
		lineStringPlacemark.setDescription(line_windowContent);					
		// Create a style and set width and color of line
		lineStringPlacemark.setStyleSelector(ge.createStyle(''));
		var lineStyle = lineStringPlacemark.getStyleSelector().getLineStyle();					
		lineStyle.setWidth(2);

		/*Color for the link line*/
		var link_color_obj = earth_self.makeRgbaObject(linkColor);

		lineStyle.getColor().setA(200);
		lineStyle.getColor().setB((+link_color_obj.b));
		lineStyle.getColor().setG((+link_color_obj.g));
		lineStyle.getColor().setR((+link_color_obj.r));
		// Add the feature to Earth
		ge.getFeatures().appendChild(lineStringPlacemark);

		return lineStringPlacemark;
	};


	/**
	 * This function plot the sector for given lat-lon points
	 * @method plotSector_earth.
	 * @param Lat {Number}, It contains lattitude of any point.
	 * @param Lng {Number}, It contains longitude of any point.
	 * @param pointsArray {Array}, It contains the points lat-lon object array.
	 * @param sectorInfo {Object Array}, It contains the information about the sector which are shown in info window.
	 * @param bgColor {Object}, It contains the RGBA format color code JSON object.
	 * @param childSS {Object Array}, It contains all the sub-station info for the given sector
	 * @param device_technology {String}, It contains the base station device technology
	 */
	this.plotSector_earth = function(lat,lng,pointsArray,sectorInfo,bgColor,childSS,device_technology) {

		var infoData = {};
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

		infoData["technology"] = device_technology;
		var halfPt = Math.floor(pointsArray.length / (+2));
		// Create object for Link Line Between Sector & SS
		infoData["startLat"] = pointsArray[halfPt].lat;
		infoData["startLon"] = pointsArray[halfPt].lon;
		infoData["info"] = sectorInfo;

		sector_polygon.setOuterBoundary(polyPoints);
		//Create a style and set width and color of line
		sectorPolygonObj.setStyleSelector(ge.createStyle(''));
		/*Set info window content for sector*/
		sectorPolygonObj.setDescription(sector_windowContent+"<input type='hidden' name='technology' value=' &-&-& "+JSON.stringify(infoData)+" &-&-& '/><input type='hidden' name='sub_station_data' value=' -|-|-|- "+childSS+" -|-|-|- '/>");

		var lineStyle = sectorPolygonObj.getStyleSelector().getLineStyle();
		lineStyle.setWidth(1);
		lineStyle.getColor().setA(200);
		lineStyle.getColor().setB(102);
		lineStyle.getColor().setG(101);
		lineStyle.getColor().setR(99);

		// Color can also be specified by individual color components.
		var polyColor = sectorPolygonObj.getStyleSelector().getPolyStyle().getColor();
		polyColor.setR((+bgColor.r));
		polyColor.setG((+bgColor.g));
		polyColor.setB((+bgColor.b));

		polyColor.setA(200);
		// Add the placemark to Earth.
		ge.getFeatures().appendChild(sectorPolygonObj);

		google.earth.addEventListener(sectorPolygonObj, 'click', function(event) {
			
			var infoObject = {};

			var description = this.getDescription();
			var ssList = JSON.parse(description.split("-|-|-|-")[1]);

			infoObject = JSON.parse(description.split('&-&-&')[1]);
			infoObject["ssList"] = ssList;

			if(ssList.length > 0) {
				/*Remove All SS from Google Earth*/
				$.grep(plotted_ss_earth,function(ss) {
					ge.getFeatures().removeChild(ss);
				});

				/*Remove All Links from google earth*/
				$.grep(plotterLinks_earth,function(links) {
					ge.getFeatures().removeChild(links);
				});

				/*Reset SS & links array*/
				plotted_ss_earth = [];
				plotterLinks_earth = [];
				earth_self.plotDevices_earth(infoObject,"sub_station");
			}
		});
	};

	/**
	 * This function make "r,g,b,a" color object from rgba color string
	 * @method makeRgbaObject
	 * @param color {String}, It contains color in rgba format(string).
	 */
	this.makeRgbaObject = function(color) {
		var colorObject = {};
		var colorArray = color.substring(color.lastIndexOf("(")+1,color.lastIndexOf(")")).split(",");
		colorObject["r"] = colorArray[0];
		colorObject["g"] = colorArray[1];
		colorObject["b"] = colorArray[2];
		colorObject["a"] = colorArray[3];

		return colorObject;
	};

	/**
	 * This function filters the BS data from devices object as per the applied rule
	 * @method applyFilter_earth
	 * @param filtersArray {Object Array} It is an object array of filters with keys
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
	 			// $("#resetFilters").click();
	 			$("#resetFilters").button("loading");
		        /*Reset The basic filters dropdown*/
		        $("#technology").val($("#technology option:first").val());
		        $("#vendor").val($("#vendor option:first").val());
		        $("#state").val($("#state option:first").val());
		        $("#city").val($("#city option:first").val());
		        
	 			/*create the BS-SS network on the google earth*/
		        earth_self.plotDevices_earth(main_devices_data_earth,"base_station");

	 		} else {

				/*Reset the markers, polyline & filters*/
	 			earth_self.clearEarthElements();

				masterMarkersObj = [];
				slaveMarkersObj = [];

				/*Populate the map with the filtered markers*/
	 			earth_self.plotDevices_earth(filteredData,"base_station");
	 			// addSubSectorMarkersToOms(filteredData);
	 		}	 		
	 	}	
	};

	/**
     * This function resets the global variables & again call the api calling function after given timeout i.e. 5 minutes
     * @method recallServer_earth
     */
    this.recallServer_earth = function() {

    	/*Hide The loading Icon*/
		$("#loadingIcon").show();

		/*Enable the refresh button*/
		$("#resetFilters").button("loading");

		/*Clear all the elements from google earth*/
		earth_self.clearEarthElements();

		/*Reset Global Variables*/
		earth_self.resetVariables_earth();
		
		/*Recall the API*/
		earth_self.getDevicesData_earth();
    };

    /**
     * This function will clear all the elements from google earth
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