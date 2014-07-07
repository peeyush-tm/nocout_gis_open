/*Global Variables*/
var mapInstance = "",
	that = "",
	currentDomElement = "",
	main_devices_data_gmaps = [],
	oms = "",
	pathConnector = "",
	infowindow = "",
	devicesObject = {},
	plottedSS = [],
	metaData = {},
	hitCounter = 1,
	showLimit = 0,
	devicesCount = 0,
	remainingDevices = 0,
	cityArray = [],
	stateArray = [],
	vendorArray = [],
	techArray = [],
	devices_gmaps = [],
	masterMarkersObj = [],
	slaveMarkersObj = [],
	pathLineArray = [],
	counter = -999,
	totalCalls = 1,
	clusterIcon = "",
	appliedFilterObj_gmaps = {},
	masterClusterInstance = "",
	slaveClusterInstance = "",
	polygonSelectedDevices = [],
	pathArray = [],
	polygon = "",
	pointsArray = [],
	currentPolygon = {},
	drawingManager = "",
	dataArray = [],
	leftMargin = 0,
	sectorArray = [],
	circleArray = [],
	/*Variables used in fresnel zone calculation*/
	isDialogOpen = true,
	fresnelLat1 = "",
	fresnelLon1 = "",
	fresnelLat2 = "",
	fresnelLon2 = "",
	arrayCounter = 0,
	latLongArray = [],
	latLongArrayCopy = [],
	depthStep = 6,
	freq_mhz = 900, //MHZ
	HEIGHT_CHANGED = false,
	clear_factor = 100,
	/*Default antina heights*/
	antenaHight1 = 40.0,
	antenaHight2 = 45.0,
	/*Colors for fresnel zone graph*/
	pinPointsColor = 'rgb(170,102,102)',
	altitudeColor = '#EDC240',
	losColor = 'rgb(203,75,75)',
	fresnel1Color = 'rgba(82, 172, 82, 0.99)',
	fresnel2Color = 'rgb(148,64,237)';

/**
 * This class is used to plot the BS & SS on the google maps & performs their functionality.
 * @class devicePlottingLib
 * @method devicePlottingClass_gmap
 * @uses jQuery
 * @uses Google Maps
 * @uses jQuery Flot
 * @uses jQuery UI
 * Coded By :- Yogender Purohit
 */
function devicePlottingClass_gmap() {

	/*Store the reference of current pointer in a global variable*/
	that = this;

	/**
	 * This function creates the base google map with the lat long of India
	 * @function createMap
	 * @class devicePlottingLib
	 * @param domElement "String" It the the dom element on which the map is to be create
	 */
	this.createMap = function(domElement) {

		/*Save the dom element in the global variable*/
		currentDomElement = domElement;

		var mapObject = {
			center    : new google.maps.LatLng(21.1500,79.0900),
			zoom      : 4
		};    
		/*Create Map Type Object*/
		mapInstance = new google.maps.Map(document.getElementById(domElement),mapObject);
		/*Search text box object*/
		var searchTxt = document.getElementById('searchTxt');

		/*google search object for search text box*/
		var searchBox = new google.maps.places.SearchBox(searchTxt);

		/*Event listener for search text box*/
		google.maps.event.addListener(new google.maps.places.SearchBox(searchTxt), 'places_changed', function() {			
			/*place object returned from map API*/
    		var places = searchBox.getPlaces();
    		/*initialize bounds object*/
    		var bounds = new google.maps.LatLngBounds();
    		/*point bounds to the place location*/
    		bounds.extend(places[0].geometry.location);
    		/*call fitbounts for the mapInstance with the place location bounds object*/
    		mapInstance.fitBounds(bounds)
    		/*Listener to reset zoom level if it exceeds to particular value*/
    		var listener = google.maps.event.addListener(mapInstance, "idle", function() { 
    			/*check for current zoom level*/
				if (mapInstance.getZoom() > 8) {
					mapInstance.setZoom(8);
				}
				google.maps.event.removeListener(listener);
			});
		});

		/*Create a instance of OverlappingMarkerSpiderfier*/
		oms = new OverlappingMarkerSpiderfier(mapInstance,{markersWontMove: true, markersWontHide: true});		

		/*Create a instance of google map info window*/
		infowindow = new google.maps.InfoWindow();		

		oms.addListener('click', function(marker,e) {
			
			if($.trim(marker.pointType) == 'base_station') {

				/*Clear all the Sectors on BS*/
				for(var k=0;k<sectorArray.length;k++) {
					sectorArray[k].setMap(null);	
				}
				/*Reset the SS points array*/				
				sectorArray = [];

				/*True in case of PMP & WIMAX*/
				if($.trim(marker.technology) != "PTP" && $.trim(marker.technology) != "P2P") {
					
					$.grep(marker.sectors,function(sector) {
		    			var lat = marker.ptLat;
						var lon = marker.ptLon;
						var rad = 4;//sector.radius;
						var azimuth = sector.azimuth_angle;
						var beam_width = sector.beam_width;
						var sector_color = "";
					    sector_color = "rgba(";
					    sector_color += JSON.parse(sector.color).r+",";
					    sector_color += JSON.parse(sector.color).g+",";
					    sector_color += JSON.parse(sector.color).b+",";
					    sector_color += JSON.parse(sector.color).a;
					    sector_color += ")";

						var sectorInfo = sector.info;
						var orientation = $.trim(sector.orientation);
						/*Call createSectorData function to get the points array to plot the sector on google maps.*/
						that.createSectorData(lat,lon,rad,azimuth,beam_width,orientation,function(pointsArray) {

							/*Plot sector on map with the retrived points*/
							that.plotSector_gmap(lat,lon,pointsArray,sectorInfo,sector_color);

						});
		    		});

				}

				/*Clear the existing SS for same point*/
				for(var i=0;i<plottedSS.length;i++) {
					plottedSS[i].setMap(null);
				}

				/*Clear all the link between BS & SS  or Sector & SS*/
				for(var j=0;j<pathLineArray.length;j++) {
					pathLineArray[j].setMap(null);	
				}
				/*Reset global variables*/
				plottedSS = [];
				pathLineArray = [];

				that.plotDevices_gmap(marker,"sub_station");
			}

			var windowPosition = new google.maps.LatLng(marker.ptLat,marker.ptLon);
			/*Call the function to create info window content*/
			var content = that.makeWindowContent(marker);
			/*Set the content for infowindow*/
			infowindow.setContent(content);
			/*Set The Position for InfoWindow*/
			infowindow.setPosition(windowPosition);
			/*Open the info window*/
			infowindow.open(mapInstance);
		});
		/*Event when the markers cluster expands or spiderify*/
		oms.addListener('spiderfy', function(e,markers) {
			/*Change the markers icon from cluster icon to thrie own icon*/
			for(var i=0;i<e.length;i++) {
				e[i].setOptions({"icon":e[i].oldIcon});
			}

			infowindow.close();
		});
		/*Event when markers cluster is collapsed or unspiderify*/
		oms.addListener('unspiderfy', function(e,markers) {

			var latArray = [],
				lonArray = [];

			$.grep(e, function (elem) {
				latArray.push(elem.ptLat);
				lonArray.push(elem.ptLon);
			});

			/*Reset the marker icon to cluster icon*/
			for(var i=0;i<e.length;i++) {

				var latCount = $.grep(latArray, function (elem) {return elem === e[i].ptLat;}).length;
				var lonCount = $.grep(lonArray, function (elem) {return elem === e[i].ptLon;}).length;

				if(lonCount > 1 && latCount > 1) {
					e[i].setOptions({"icon":clusterIcon});
				}				
			}
		});
	};

	/**
	 * This function plots the BS & SS network on the created google map
	 * @function getDevicesData_gmap
	 * @class devicePlottingLib
	 */
	this.getDevicesData_gmap = function() {

		if(counter > 0 || counter == -999) {
			/*Show The loading Icon*/
			$("#loadingIcon").show();

			/*Disable the refresh button*/
			$("#resetFilters").button("loading");

			/*To Enable The Cross Domain Request*/
			$.support.cors = true;
			
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
						if(devicesObject.data == undefined) {

							/*Save the result json to the global variable for global access*/
							devicesObject = result;
							/*This will update if any filer is applied*/
							devices_gmaps = devicesObject.data.objects.children;
							/*This will changes only when data re-fetched*/
							main_devices_data_gmaps = devicesObject.data.objects.children;

						} else {

							devices_gmaps = devices_gmaps.concat(result.data.objects.children);
						}

						if(devicesObject.success == 1) {

							if(devicesObject.data.objects.children.length > 0) {

								/*Update the device count with the received data*/
								if(devicesObject.data.meta.total_count != undefined) {
									devicesCount = devicesObject.data.meta.total_count;
								} else {
									devicesCount = 1;
								}

								/*Update the device count with the received data*/
								if(devicesObject.data.meta.limit != undefined) {
									showLimit = devicesObject.data.meta.limit;
								} else {
									showLimit = 1;
								}

								if(counter == -999) {
									counter = Math.floor(devicesCount / showLimit);
								}

								/*If cluster icon exist then save it to global variable else make the global variable blank*/
								if(devicesObject.data.objects.data.unspiderfy_icon == undefined) {
									clusterIcon = "";
								} else {
									clusterIcon = "../../"+devicesObject.data.objects.data.unspiderfy_icon;
								}

								/*Check that any filter is applied or not*/
								var appliedFilterLength_gmaps = Object.keys(appliedFilterObj_gmaps).length;

								if(appliedFilterLength_gmaps > 0) {
									/*If any filter is applied then plot the fetch data as per the filters*/
									that.applyFilter_gmaps(appliedFilterObj_gmaps);
								} else {
									/*Call the plotDevices_gmap to show the markers on the map*/
									that.plotDevices_gmap(devices_gmaps,"base_station");
								}

								/*Call the function after 3 sec.*/
								setTimeout(function() {
										
									that.getDevicesData_gmap();
								},3000);
								
							} else {
								$.gritter.add({
						            // (string | mandatory) the heading of the notification
						            title: 'GIS - No Data',
						            // (string | mandatory) the text inside the notification
						            text: 'No Devices Found',
						            // (bool | optional) if you want it to fade out on its own or just sit there
						            sticky: true
						        });

						        /*Recall the server after particular timeout*/
								that.recallServer_gmap();
							}

						} else {
							$.gritter.add({
					            // (string | mandatory) the heading of the notification
					            title: 'GIS - Server Error',
					            // (string | mandatory) the text inside the notification
					            text: devicesObject.message,
					            // (bool | optional) if you want it to fade out on its own or just sit there
					            sticky: true
					        });

					        /*Recall the server after particular timeout*/
							that.recallServer_gmap();
						}
						/*Decrement the counter*/
						counter = counter - 1;

					} else {

						$.gritter.add({
				            // (string | mandatory) the heading of the notification
				            title: 'GIS - Server Error',
				            // (string | mandatory) the text inside the notification
				            text: 'No Devices Found',
				            // (bool | optional) if you want it to fade out on its own or just sit there
				            sticky: true
				        });

						that.recallServer_gmap();
					}
				},
				/*If data not fetched*/
				error : function(err) {

					// console.log(err.responseText);
					$.gritter.add({
			            // (string | mandatory) the heading of the notification
			            title: 'GIS - Server Error',
			            // (string | mandatory) the text inside the notification
			            text: err.statusText,
			            // (bool | optional) if you want it to fade out on its own or just sit there
			            sticky: true
			        });
					that.recallServer_gmap();
				}
			});
		} else {

			/*Recall the server after the defined time*/
			that.recallServer_gmap();
		}
	};

	/**
     * This function is used to populate the markers on the google maps
     * @class devicePlottingLib
     * @method plotDevices_gmap
     * @param stationObject {JSON Objet} In case of BS, it is the devies object array & for SS it contains BS marker object with SS & sector info
     * @param stationType "String", It contains that the points are for BS or SS.
	 */
	this.plotDevices_gmap = function(stationObject,stationType) {

		var bsLatArray = [],
			bsLonArray = [],
			bs_ss_devices = [];

		if($.trim(stationType) == "base_station") {
			bs_ss_devices = stationObject;
		} else {
			bs_ss_devices = stationObject.ssList;
		}

		for(var i=0;i<bs_ss_devices.length;i++) {

			var available_sectors = [],
				deviceData = [],
				pt_technology = "";

			if(bs_ss_devices[i].data.param.sector != undefined) {
				available_sectors = bs_ss_devices[i].data.param.sector;
			}

			if($.trim(stationType) == "base_station") {
				deviceData = bs_ss_devices[i].data.param.base_station;
				pt_technology = bs_ss_devices[i].data.technology;
			} else {				
				deviceData = bs_ss_devices[i].data.param.sub_station;
			}


			/*Get All BS Lat & Lon*/
			bsLatArray.push(bs_ss_devices[i].data.lat);
			bsLonArray.push(bs_ss_devices[i].data.lon);

			/*Create BS or SS Marker Object*/
			var station_marker_object = {
		    	position  	  : new google.maps.LatLng(bs_ss_devices[i].data.lat,bs_ss_devices[i].data.lon),
		    	ptLat 		  : bs_ss_devices[i].data.lat,
		    	technology 	  : pt_technology,
		    	ptLon 		  : bs_ss_devices[i].data.lon,
		    	map       	  : mapInstance,
		    	icon 	  	  : "../../"+bs_ss_devices[i].data.markerUrl,//"https://chart.googleapis.com/chart?chst=d_map_pin_letter&chld=|fcfcfc|",
		    	oldIcon 	  : "../../"+bs_ss_devices[i].data.markerUrl,
		    	pointType	  : stationType,
				perf 		  : bs_ss_devices[i].data.perf,
				ssList   	  : bs_ss_devices[i].children,
				sectors 	  : available_sectors,
				dataset 	  : deviceData,
				antena_height : bs_ss_devices[i].data.antena_height
			};

			/*Create BS or SS Marker*/
		    var station_marker = new google.maps.Marker(station_marker_object);


		    if($.trim(stationType) != "base_station") {

		    	var startEndObj = {},
	    			linkColor = {},
	    			bs_info = {},
	    			ss_info = {};

		    	if($.trim(stationObject.technology) == "P2P" || $.trim(stationObject.technology) == "PTP") {
		    		/*Start & end point object*/
		    		startEndObj["startLat"] = stationObject.ptLat;
		    		startEndObj["startLon"] = stationObject.ptLon;

		    		/*Base station info Object*/
		    		bs_info["info"] = stationObject.dataset;
		    		bs_info["antena_height"] = stationObject.antena_height;
		    		bs_info["perf"] = stationObject.perf;

		    	} else {
		    		var lat = "",
		    			lon = "",
		    			rad = 4,
		    			azimuth = "",
		    			beam_width = "",
		    			orientation = "";

		    		lat = stationObject.ptLat;
					lon = stationObject.ptLon;

					if(bs_ss_devices[i].data.radius != null && resultantMarkers[i].children[j].data.radius > 0) {
						rad = resultantMarkers[i].children[j].data.radius;
					}

					azimuth = bs_ss_devices[i].data.azimuth_angle;
					beam_width = bs_ss_devices[i].data.beam_width;
					orientation = $.trim(bs_ss_devices[i].data.sector_orientation);

					
					/*Call createSectorData function to get the points array to plot the sector on google maps.*/
					that.createSectorData(lat,lon,rad,azimuth,beam_width,orientation,function(pointsArray) {

						var halfPt = Math.floor(pointsArray.length / (+2));
						
						startEndObj["startLat"] = pointsArray[halfPt].lat;
		    			startEndObj["startLon"] = pointsArray[halfPt].lon;
					});

					/*Base station info Object*/
		    		bs_info["info"] = bs_ss_devices[i].data.param.sector_info;
		    	}

		    	bs_info["antena_height"] = stationObject.antena_height;
	    		bs_info["perf"] = stationObject.perf;

		    	startEndObj["endLat"] = bs_ss_devices[i].data.lat;
	    		startEndObj["endLon"] = bs_ss_devices[i].data.lon;

	    		/*Sub station info Object*/
	    		ss_info["info"] = bs_ss_devices[i].data.param.sub_station;
	    		ss_info["antena_height"] = bs_ss_devices[i].data.antena_height;
	    		ss_info["perf"] = bs_ss_devices[i].data.perf;

	    		/*Link color object*/
	    		linkColor = JSON.parse(bs_ss_devices[i].data.link_color);
	    		
		    	/*Create the link between BS & SS or Sector & SS*/
		    	that.createLink_gmaps(startEndObj,linkColor,bs_info,ss_info);

		    	/*Push the plotted SS to an array for further use*/
		    	plottedSS[i]  = station_marker;
		    }

		    if($.trim(stationType) == "base_station") {
		    	
		    	/*Add the master marker to the global master markers array*/
		    	masterMarkersObj.push(station_marker);
		    }
		    /*Add parent markers to the OverlappingMarkerSpiderfier*/
		    oms.addMarker(station_marker);
		}

		/*Loop to change the icon for same location markers(to cluster icon)*/
		for(var k=0;k<masterMarkersObj.length;k++) {
			
			/*if two BS on same position*/
			var bsLatOccurence = $.grep(bsLatArray, function (elem) {return elem === masterMarkersObj[k].ptLat;}).length;
			var bsLonOccurence = $.grep(bsLonArray, function (elem) {return elem === masterMarkersObj[k].ptLon;}).length;
			if(bsLatOccurence > 1 && bsLonOccurence > 1) {
				masterMarkersObj[k].setOptions({"icon" : clusterIcon});
			}
		}

		/*Cluster options object*/
		var clusterOptions = {gridSize: 70, maxZoom: 8};
		/*Add the master markers to the cluster MarkerCluster object*/
		masterClusterInstance = new MarkerClusterer(mapInstance, masterMarkersObj, clusterOptions);
	};

	/**
	 * This function creates a link between Bs & SS
	 * @class devicePlottingLib
	 * @method createLink_gmaps. 
	 * 
	 *
	 */
	this.createLink_gmaps = function(startEndObj,linkColor,bs_info,ss_info) {

		pathDataObject = [
			new google.maps.LatLng(startEndObj.startLat,startEndObj.startLon),
			new google.maps.LatLng(startEndObj.endLat,startEndObj.endLon)
		];

		var linkObject = {},
			link_path_color = "";

		link_path_color = "rgba(";
	    link_path_color += linkColor.r+",";
	    link_path_color += linkColor.g+",";
	    link_path_color += linkColor.b+",";
	    
	    if(linkColor.a != undefined) {
	    	link_path_color += linkColor.a;
	    } else {
	    	link_path_color += "1.0";	
	    }

	    link_path_color += ")";

		linkObject = {
			path 				: pathDataObject,
			strokeColor			: link_path_color,
			strokeOpacity		: 1.0,
			strokeWeight		: 2,
			pointType 			: "path",
			geodesic			: true,
			ss_info				: ss_info.info,
			ss_lat 				: startEndObj.endLat,
			ss_lon 				: startEndObj.endLon,
			ss_perf 			: ss_info.perf,
			ss_height 			: ss_info.antena_height,
			bs_lat 				: startEndObj.startLat,
			bs_info 			: bs_info.info,
			bs_lon 				: startEndObj.startLon,
			bs_perf 			: bs_info.perf,
			bs_height 			: bs_info.antena_height
		};

		// if($.trim(resultantMarkers[i].type) == "P2P" || $.trim(resultantMarkers[i].type) == "PTP") {
		// 	linkObject["bs_info"] = resultantMarkers[i].data.param.base_station;
		// } else {
		// 	linkObject[""] = resultantMarkers[i].children[j].data.param.sector_info;
		// }

		pathConnector = new google.maps.Polyline(linkObject);
		/*Plot the link line between master & slave*/
		pathConnector.setMap(mapInstance);

		pathLineArray.push(pathConnector);

		/*Bind Click Event on Link Path Between Master & Slave*/
		google.maps.event.addListener(pathConnector, 'click', function(e) {

			/*Call the function to create info window content*/
			var content = that.makeWindowContent(this);
			/*Set the content for infowindow*/
			infowindow.setContent(content);
			/*Set The Position for InfoWindow*/
			infowindow.setPosition(e.latLng);
			/*Open the info window*/
			infowindow.open(mapInstance);
		});
	};


	/**
	 * This function creates data to plot sectors on google maps.
	 * @class devicePlottingLib
	 * @method createSectorData.
	 * @param Lat "Number", It contains lattitude of any point.
	 * @param Lng "Number", It contains longitude of any point.
	 * @param radius "Number", It contains radius for sector.
	 * @param azimuth "Number", It contains azimuth angle for sector.
	 * @param beamwidth "Number", It contains width for the sector.
	 * @param sectorData {JSON Object}, It contains sector info json object.
	 * @param orientation "String", It contains the orientation type of antena i.e. vertical or horizontal
	 * @return sectorDataArray {JSON Object Array}, It is the polygon points lat-lon object array
	 */
	this.createSectorData = function(lat,lng,radius,azimuth,beamWidth,orientation,callback) {

		var triangle = [],
			sectorDataArray = [];
		// Degrees to radians
        var d2r = Math.PI / 180;
        //  Radians to degrees
        var r2d = 180 / Math.PI;

        var PRlat = (radius/6371) * r2d; // using 3959 miles or 6371 KM as earth's radius
        var PRlng = PRlat/Math.cos(lat*d2r);

        var PGpoints = [],
        	pointObj = {};

        with(Math) {

			lat1 = (+lat) + (PRlat * cos( d2r * (azimuth - beamWidth/2 )));
			lon1 = (+lng) + (PRlng * sin( d2r * (azimuth - beamWidth/2 )));
			/*Create lat-lon point object*/
			/*Reset Pt Object*/
			pointObj = {};
			pointObj["lat"] = lat1;
			pointObj["lon"] = lon1;
			/*Add point object to array*/
			PGpoints.push(pointObj);

			lat2 = (+lat) + (PRlat * cos( d2r * (azimuth + beamWidth/2 )));
			lon2 = (+lng) + (PRlng * sin( d2r * (azimuth + beamWidth/2 )));
			
			var theta = 0;
			var gamma = d2r * (azimuth + beamWidth/2 );

			for (var a = 1; theta < gamma ; a++ ) {
				theta = d2r * (azimuth - beamWidth/2 +a);
				PGlon = (+lng) + (PRlng * sin( theta ));
				PGlat = (+lat) + (PRlat * cos( theta ));
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
		if(orientation == "horizontal") {

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
	 * This function plot the sector for given lat-lon points
	 * @class devicePlottingLib
	 * @method plotSector_gmap.
	 * @param Lat "Number", It contains lattitude of the point on which sector is creater i.e. BS lat-lon.
	 * @param Lng "Number", It contains longitude of the point on which sector is creater i.e. BS lat-lon.
	 * @param pointsArray [Array], It contains the points lat-lon object array.
	 * @param sectorInfo {JSON Object Array}, It contains the information about the sector which are shown in info window.
	 * @param bgColor "String", It contains the RGBA format color code for sector.
	 */
	this.plotSector_gmap = function(lat,lon,pointsArray,sectorInfo,bgColor) {

		var polyPathArray = [];

		for(var i=0;i<pointsArray.length;i++) {
			var pt = new google.maps.LatLng(pointsArray[i].lat,pointsArray[i].lon);
			polyPathArray.push(pt);
		}

		var poly = new google.maps.Polygon({
			map 		  : mapInstance,
			path 		  : polyPathArray,
			ptLat 		  : lat,
			ptLon 		  : lon,
			strokeColor   : "rgba(90, 101, 102, 1.0)",
			fillColor 	  : bgColor,
			pointType	  : "sector",
			strokeOpacity : 1.0,
			strokeWeight  : 1,
			dataset 	  : sectorInfo
        });

        /*Push polygon to an array*/
		sectorArray.push(poly);

        poly.setMap(mapInstance);

        /*listener for click event of sector*/
		google.maps.event.addListener(poly,'click',function(e) {

			var windowPosition = new google.maps.LatLng(e.latLng.k,e.latLng.B);
			/*Call the function to create info window content*/
			var content = that.makeWindowContent(poly);
			/*Set the content for infowindow*/
			infowindow.setContent(content);
			/*Set The Position for InfoWindow*/
			infowindow.setPosition(windowPosition);
			/*Open the info window*/
			infowindow.open(mapInstance);
		});
	};

	/**
	 * This function creates circle on the given lat lon of given radius
	 * @class devicePlottingLib
	 * @method createCircle.
	 * @param Lat "Number", It contains lattitude of any point.
	 * @param Lng "Number", It contains longitude of any point.
	 * @param radius "Number", It contains radius for sector.
	 * @param bgColor "String", It contains bg color for circle.
	 * @param pType "String", It contains info about circle is plot for BH or frequency.
	 * @param dType "String", It contains info about circle is plot for SS or BS.
	 * @param bhData {JSON Object}, It contains JSON object of BH info data.
	 */
	this.createCircle = function(lat,lng,radius,bgColor,pType,dType,bhData) {

		var rad = 0,
			fOpacity = 0,
			sColor = "";
		if($.trim(pType) == "frequency") {
			rad = radius * 2;
			fOpacity = 0.5;
			sColor = bgColor;
		} else if($.trim(dType) == "ss") {
			rad = radius;
			fOpacity = 0.95;
			sColor = '000000';
		} else {
			rad = radius;
			fOpacity = 0.8;
			sColor = bgColor;
		}
		/*Make circle data object for devices*/
		var devicesCircleOptions = {
			strokeColor		: "#"+sColor,
			strokeOpacity	: 1.0,
			ptLat 			: lat,
			ptLon 			: lng,
			clickable		: true,
			strokeWeight	: 1,
			fillColor		: "#"+bgColor,
			fillOpacity		: fOpacity,
			pointType		: pType,
			map 			: mapInstance,
			center 			: new google.maps.LatLng(lat,lng),
			radius 			: rad,
			dataset 		: bhData
		};

		/*Make the circle on the device marker*/
		var deviceCircle = new google.maps.Circle(devicesCircleOptions);

		/*Add circle object to an array*/
		circleArray.push(deviceCircle);
		rad = 0;
		fOpacity = 0;
		sColor = "";
		if($.trim(pType) == "backhual") {
			/*listener for click event of circle*/
			google.maps.event.addListener(deviceCircle,'click',function(e) {
				
				var windowPosition = new google.maps.LatLng(lat,lng);
				/*Call the function to create info window content*/
				var content = that.makeWindowContent(deviceCircle);
				/*Set the content for infowindow*/
				infowindow.setContent(content);
				/*Set The Position for InfoWindow*/
				infowindow.setPosition(windowPosition);
				/*Open the info window*/
				infowindow.open(mapInstance);
			});
		}
	};

	/**
	 * This function creates the info window content for BS,SS & link path 
	 * @class devicePlottingLib
	 * @method makeWindowContent
	 * @param contentObject {JSON Object} It contains current pointer(this) information
	 * @return windowContent "String" It contains content to be shown on info window
	 */
	this.makeWindowContent = function(contentObject) {

		var windowContent = "",
			infoTable =  "",
			perfContent = "",
			clickedType = $.trim(contentObject.pointType);

		/*True,if clicked on the link line*/
		if(clickedType == "path") {

			infoTable += "<table class='table table-bordered'><thead><th>BS-Sector Info</th><th>BS-Sector Perf</th><th>SS Info</th><th>SS Perf</th></thead><tbody>";
			infoTable += "<tr>";
			/*BS-Sector Info Start*/
			infoTable += "<td>";	
			infoTable += "<table class='table table-hover innerTable'><tbody>";
			
			/*Loop for BS or Sector info object array*/
			for(var i=0;i<contentObject.bs_info.length;i++) {

				if(contentObject.bs_info[i].show == 1) {
					infoTable += "<tr><td>"+contentObject.bs_info[i].title+"</td><td>"+contentObject.bs_info[i].value+"</td></tr>";
				}
			}

			infoTable += "<tr><td>Lat, Long</td><td>"+contentObject.bs_lat+", "+contentObject.bs_lon+"</td></tr>";
			infoTable += "</tbody></table>";			
			infoTable += "</td>";
			/*BS-Sector Info End*/
			/*BS-Sector Performance Start*/
			infoTable += "<td style='vertical-align:middle;text-align: center;'><h1><i class='fa fa-signal'></i>  "+contentObject.bs_perf+"</h1></td>";
			/*BS-Sector Performance End*/
			/*SS Info Start*/
			infoTable += "<td>";			
			infoTable += "<table class='table table-hover innerTable'><tbody>";
			
			/*Loop for ss info object array*/
			for(var i=0;i<contentObject.ss_info.length;i++) {

				if(contentObject.ss_info[i].show == 1) {
					infoTable += "<tr><td>"+contentObject.ss_info[i].title+"</td><td>"+contentObject.ss_info[i].value+"</td></tr>";
				}
			}

			infoTable += "<tr><td>Lat, Long</td><td>"+contentObject.ss_lat+", "+contentObject.ss_lon+"</td></tr>";
			infoTable += "</tbody></table>";		
			infoTable += "</td>";
			/*SS Info End*/
			/*SS Performance Start*/
			infoTable += "<td style='vertical-align:middle;text-align: center;'><h1><i class='fa fa-signal'></i>  "+contentObject.ss_perf+"</h1></td>";
			/*SS Performance End*/
			infoTable += "</tr>";
			infoTable += "</tbody></table>";
			
			/*Concat infowindow content*/
			windowContent += "<div class='windowContainer'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i> BS-SS</h4></div><div class='box-body'>"+infoTable+"<div class='clearfix'></div><ul class='list-unstyled list-inline'><li><button class='btn btn-sm btn-info' onClick='that.claculateFresnelZone("+contentObject.bs_lat+","+contentObject.bs_lon+","+contentObject.ss_lat+","+contentObject.ss_lon+","+contentObject.bs_height+","+contentObject.ss_height+");'>Fresnel Zone</button></li></ul></div></div></div>";

		} else {

			infoTable += "<table class='table table-bordered'><tbody>";

			for(var i=0;i<contentObject.dataset.length;i++) {

				if(contentObject.dataset[i].show == 1) {
					infoTable += "<tr><td>"+contentObject.dataset[i].title+"</td><td>"+contentObject.dataset[i].value+"</td></tr>";
				}
			}
			/*Set the lat lon of the point*/
			infoTable += "<tr><td>Lat, Long</td><td>"+contentObject.ptLat+", "+contentObject.ptLon+"</td></tr>";

			infoTable += "</tbody></table>";

			if(contentObject.perf != undefined) {
				perfContent += "<h1><i class='fa fa-signal'></i>  "+contentObject.perf+"</h1>";
			}			
			/*Final infowindow content string*/
			windowContent += "<div class='windowContainer'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>  "+contentObject.pointType.toUpperCase()+"</h4></div><div class='box-body'><div class='windowInfo' align='center'>"+infoTable+"</div><div class='perf'>"+perfContent+"</div><div class='clearfix'></div></div></div></div>";
		}
		/*Return the info window content*/
		return windowContent;
	};

	/**
	 * This function calculates the fresnel zone
	 * @class devicePlottingLib
	 * @method claculateFresnelZone
	 * @param lat1 "Int", It contains lattitude of first point
	 * @param lon1 "Int", It contains longitude of first point
	 * @param lat2 "Int", It contains lattitude of second point
	 * @param lon2 "Int", It contains longitude of second point
	 * @param height1 "Int", It contains antina height of first point
	 * @param height2 "Int", It contains antina height of second point
	 */
	this.claculateFresnelZone = function(lat1,lon1,lat2,lon2,height1,height2) {

		/** Converts numeric degrees to radians */
		Number.prototype.toRad = function() {
		   return this * Math.PI / 180;
		}
		/** Converts numeric radians to degrees */
		Number.prototype.toDeg = function() {
		   return this * 180 / Math.PI;
		}
		/*Assign lat lons to global variables*/
		fresnelLat1 = lat1;
		fresnelLon1 = lon1;
		fresnelLat2 = lat2;
		fresnelLon2 = lon2;
		/*Set the antina height to the available heights*/
		if(height1 == 0 || height1 == undefined) {
			antenaHight1 = antenaHight1;			
		} else {
			antenaHight1 = height1;
		}

		if(height2 == 0 || height2 == undefined) {
			antenaHight2 = antenaHight2;			
		} else {
			antenaHight2 = height2;
		}

		/*Reset global variables*/
		latLongArray = [];
		arrayCounter = 0;

		/*Set clear_factor for first time dialog open*/
		if(isDialogOpen) {
			clear_factor = 100;
		}

		/*Google maps elevation object*/
		var elevator = new google.maps.ElevationService();

	    /*Two points distance calculation*/
	    /*earth's mean radius in km*/
	    var earthRadius = 6371;
	    var radian_lat1 = lat1.toRad();
	    var radian_lat2 = lat2.toRad();
	    var decimal_Lat = (lat2 - lat1).toRad();
	    var decimal_Lon = (lon2 - lon1).toRad();
	    /*Distance params calculation*/
	    var distance_param1 = Math.sin(decimal_Lat / 2) * Math.sin(decimal_Lat / 2) + Math.cos(radian_lat1) * Math.cos(radian_lat2) * Math.sin(decimal_Lon / 2) * Math.sin(decimal_Lon / 2);
	    var distance_param2 = 2 * Math.atan2(Math.sqrt(distance_param1), Math.sqrt(1 - distance_param1));
	    /*Distance between two points*/
	    var distance_between_sites = earthRadius * distance_param2;
	    
	    /*Stores one end or BS lat lon info to latLongArray*/
	    latLongArray[arrayCounter] = new Array();
	    latLongArray[arrayCounter][0] = lat1;
	    latLongArray[arrayCounter++][1] = lon1;
	    /*Call the getFresnelPath function to generate the data for */
	    that.getFresnelPath(lat1.toRad(), lon1.toRad(), lat2.toRad(), lon2.toRad(), depthStep);

	    /* ----  It stores the destination BTS cordinaties ------*/
	    latLongArray[arrayCounter] = new Array();
	    latLongArray[arrayCounter][0] = lat2;
	    latLongArray[arrayCounter++][1] = lon2;

	    var locations = [];
	    for (var abc = 0; abc < arrayCounter; abc++) {
	        locations.push(new google.maps.LatLng(latLongArray[abc][0], latLongArray[abc][1]));
	    }
	    var positionalRequest = { 'locations': locations };
	    var elevationArray = [];

	    elevator.getElevationForLocations(positionalRequest, function (results, status) {
	        if (status == google.maps.ElevationStatus.OK) {
	            for (var x = 0; x < results.length; x++) {
	                elevationArray.push(results[x].elevation);
	            }
	            that.getFresnelChartData(elevationArray, distance_between_sites);
	        }
	    });
	};

	/**
	 * This function generate fresnel point data.
	 * @class devicePlottingLib
	 * @method getFresnelPath
	 * @param lat1 "Int", It contains lattitude of first point
	 * @param lon1 "Int", It contains longitude of first point
	 * @param lat2 "Int", It contains lattitude of second point
	 * @param lon2 "Int", It contains longitude of second point
	 * @param depth "Int", It contains accuracy or depth value for which lat-lons path has to be calculated
	 */
	this.getFresnelPath = function(lat1, lon1, lat2, lon2, depth) {

	    var mlat = that.getMidPT_Lat(lat1, lon1, lat2, lon2);
	    var mlon = that.getMidPT_Lon(lat1, lon1, lat2, lon2);
	    
	    if (depth > 0) {
	        that.getFresnelPath(lat1, lon1, mlat, mlon, depth - 1);
	        latLongArray[arrayCounter] = new Array();
	        latLongArray[arrayCounter][0] = mlat.toDeg();
	        latLongArray[arrayCounter++][1] = mlon.toDeg();

	        that.getFresnelPath(mlat, mlon, lat2, lon2, depth - 1);
	    }
	    else {
	        latLongArray[arrayCounter] = new Array();
	        latLongArray[arrayCounter][0] = mlat.toDeg();
	        latLongArray[arrayCounter++][1] = mlon.toDeg();
	    }
	};

	/**
	 * This function calculates mid lattitude point for given lat-lons
	 * @class devicePlottingLib
	 * @method getMidPT_Lat
	 * @param lat1 "Int", It contains lattitude of first point
	 * @param lon1 "Int", It contains longitude of first point
	 * @param lat2 "Int", It contains lattitude of second point
	 * @param lon2 "Int", It contains longitude of second point
	 * @return lat3 "Int", It contains mid pt lat value
	 */
	this.getMidPT_Lat = function(lat1, lon1, lat2, lon2) {
	    var decimal_Lon = (lon2.toDeg() - lon1.toDeg()).toRad();
	    var Bx = Math.cos(lat2) * Math.cos(decimal_Lon);
	    var By = Math.cos(lat2) * Math.sin(decimal_Lon);
	    var lat3 = Math.atan2(Math.sin(lat1) + Math.sin(lat2), Math.sqrt((Math.cos(lat1) + Bx) * (Math.cos(lat1) + Bx) + By * By));

	    return lat3;
	};

	/**
	 * This function calculates mid longitude point for given lat-lons
	 * @class devicePlottingLib
	 * @method getMidPT_Lon
	 * @param lat1 "Int", It contains lattitude of first point
	 * @param lon1 "Int", It contains longitude of first point
	 * @param lat2 "Int", It contains lattitude of second point
	 * @param lon2 "Int", It contains longitude of second point
	 * @return lon3 "Int", It contains mid pt lon value
	 */
	this.getMidPT_Lon = function(lat1, lon1, lat2, lon2) {
	    var decimal_Lon = (lon2.toDeg() - lon1.toDeg()).toRad();
	    var Bx = Math.cos(lat2) * Math.cos(decimal_Lon);
	    var By = Math.cos(lat2) * Math.sin(decimal_Lon);

	    var lon3 = lon1 + Math.atan2(By, Math.cos(lat1) + Bx);

	    return lon3;
	};

	/**
	 * This function generates the data for fresnel zone
	 * @class devicePlottingLib
	 * @method getFresnelChartData
	 * @param elevationArray [Int Array], It contains elevation values array
	 * @param pt_distance "Int", It contains distance between two points
	 */
	this.getFresnelChartData = function(elevationArray, pt_distance) {

	    var segSize = pt_distance / (arrayCounter - 1);

	    for (var i = 0; i < arrayCounter; i++) {
	        latLongArray[i][2] = parseFloat(elevationArray[i]);
	        latLongArray[i][3] = i * segSize;
	    }
		
		minYChart=latLongArray[0][2];
		maxYChart=latLongArray[0][2];

		for(var j=1;j<arrayCounter;j++){
			if(minYChart>latLongArray[j][2]){
				minYChart=latLongArray[j][2];
			}
			if(maxYChart<latLongArray[j][2]){
				maxYChart=latLongArray[j][2];
			}
			
		}
			
		minYChart=Math.round(minYChart);
		minYChart=(minYChart>20)? (minYChart-20):minYChart;
		mod=minYChart%10;
		minYChart=minYChart-mod;

	    latLongArray[0][2] += parseFloat(antenaHight1);
	    latLongArray[arrayCounter - 1][2] += parseFloat(antenaHight2);
		
		var startHeight = parseFloat(latLongArray[0][2]);
	    var endHeight = parseFloat(latLongArray[arrayCounter - 1][2]);
	    var theta = Math.atan((endHeight - startHeight) / pt_distance);
		var slant_d = pt_distance / Math.cos(theta);
		var freq_ghz = freq_mhz / 1000;
		var clr_coff = clear_factor / 100;

	    for (var k = 0; k < arrayCounter; k++) {
	        latLongArray[k][4] = startHeight + (((endHeight - startHeight) / pt_distance) * latLongArray[k][3]);

	        var vS0 = parseFloat(latLongArray[k][3]);
			var slant_vS0 = vS0 / Math.cos(theta);
			var vS1 = parseFloat(latLongArray[k][4]);
			var v1 = 17.314 * Math.sqrt((slant_vS0 * (slant_d - slant_vS0)) / (slant_d * freq_ghz));
			var v2 = v1 * Math.cos(theta) * clr_coff;
			
	        latLongArray[k][5] = (vS1) + v2;
	        latLongArray[k][7] = (vS1) - v2;
			
			/*If tower height changed*/
			if(!HEIGHT_CHANGED) {
				latLongArray[k][9] = latLongArray[k][2]; // pin points
			} else {
				latLongArray[k][9] = latLongArrayCopy[k][9];
				if(k == (arrayCounter-1)) {
					HEIGHT_CHANGED = false;
				}
			}
	    }

		for(var l=0;l<arrayCounter;l++){
				
			if(maxYChart<latLongArray[l][5]){
				maxYChart=latLongArray[l][5];
			}
		}

		maxYChart=Math.round(maxYChart);
		maxYChart=maxYChart+30;
		mod=maxYChart%10;
		maxYChart=maxYChart-mod;

		/*Call 'drawFresnelChart' function to plot Fresnel Chart*/
	    that.drawFresnelChart();
	};

	/**
	 * This function creates the fresnal zone chart with elevation points using jquery.flot.js
	 * @class devicePlottingLib
	 * @method drawFresnelChart
	 * @user jquery.flot.js
	 * @user bootbox.js
	 */
	this.drawFresnelChart = function() {

		/* init points arrays for the chart */
		var dataPinpoints = [],
			dataAltitude = [],
			dataLOS = [],
			dataFresnel1 = [],
			dataFresnel2 = [];

		/* filling points arrays for the chart */
		for(i = 0; i < arrayCounter; i++) {
			dataAltitude.push([parseFloat(latLongArray[i][3]), parseFloat(latLongArray[i][2])]);
			dataLOS.push([parseFloat(latLongArray[i][3]), parseFloat(latLongArray[i][4])]);
			dataFresnel1.push([parseFloat(latLongArray[i][3]), parseFloat(latLongArray[i][5])]);
			dataFresnel2.push([parseFloat(latLongArray[i][3]), parseFloat(latLongArray[i][7])]);
			dataPinpoints.push([parseFloat(latLongArray[i][3]), parseFloat(latLongArray[i][9])]);
		}

		if(isDialogOpen) {
			/*Fresnel template String*/
			var leftSlider = '<div class="col-md-2" align="center"><div class="col-md-8 col-md-offset-2"><input type="text" id="antinaVal1" class="form-control" value="'+antenaHight1+'"></div><div class="clearfix"></div><div id="antina_height1" style="height:300px;" class="slider slider-blue"></div><div class="col-md-12">BTS-1 Height</div></div>';
			var chart_detail = '<div id="chart-details"><div><span id="longitude-lbl" class="chart-detail-lbl">Longitude </span> <span id="longitude"></span></div><div><span id="latitude-lbl" class="chart-detail-lbl">Latitude </span> <span id="latitude"></span></div><div><span id="distance-lbl" class="chart-detail-lbl">Distance </span> <span id="distance"></span></div><div><span id="altitude-lbl" class="chart-detail-lbl">Altitude </span> <span id="altitude"></span></div><div><span id="obstacle-lbl" class="chart-detail-lbl">Obstacle </span> <span id="obstacle"></span></div><div><span id="los-lbl" class="chart-detail-lbl">LOS </span> <span id="los"></span></div><div><span id="fresnel1-lbl" class="chart-detail-lbl">Fresnel-1 </span> <span id="fresnel1"></span></div><div><span id="fresnel2-lbl" class="chart-detail-lbl">Fresnel-2 </span> <span id="fresnel2"></span></div><div><span id="fresnel2-altitude-lbl" class="chart-detail-lbl">Clearance </span> <span id="fresnel-altitude"></span></div></div>';
			var middleBlock = '<div class="col-md-8 mid_fresnel_container"><div align="center"><div class="col-md-12">Clearance Factor</div><div class="col-md-4 col-md-offset-3"><div id="clear-factor" class="slider slider-red"></div></div><div class="col-md-2"><input type="text" id="clear-factor_val" class="form-control" value="'+clear_factor+'"></div><div class="clearfix"></div></div><div id="chart_div" style="width:600px;max-width:100%;height:300px;"></div><div class="clearfix divide-10"></div><div id="pin-points-container" class="col-md-12" align="center"></div></div>';
			var rightSlider = '<div class="col-md-2" align="center"><div class="col-md-8 col-md-offset-2"><input type="text" id="antinaVal2" class="form-control" value="'+antenaHight2+'"></div><div class="clearfix"></div><div id="antina_height2" class="slider slider-blue" style="height:300px;"></div><div class="col-md-12">BTS-2 Height</div></div>';

			var fresnelTemplate = '<div class="fresnelContainer row" style="height:400px;overflow-y:auto;">'+leftSlider+' '+middleBlock+' '+rightSlider+'</div>'+chart_detail;

			/*Call the bootbox to show the popup with Fresnel Zone Graph*/
			bootbox.dialog({
				message: fresnelTemplate,
				title: '<i class="fa fa-dot-circle-o">&nbsp;</i> Fresnel Zone'
			});

		} else {

			isDialogOpen = true;
		}

		/*Initialize antina1 height slider*/
		$("#antina_height1").slider({
	    	range 		: "min",
	    	value 		: antenaHight1,
	    	min 		: 1,
	    	max 		: 100,
	    	animate 	: true,
	    	orientation : "vertical",
	    	slide : function(a,b){
    			$("#antinaVal1").val(b.value);
	    	},
	    	stop : function(a,b){
	    		that.heightChanged();
	    	}
	    });

		/*Initialize antina2 height slider*/
	    $("#antina_height2").slider({
	    	range 		: "min",
	    	value 		: antenaHight2,
	    	min 		: 1,
	    	max 		: 100,
	    	animate 	: true,
	    	orientation : "vertical",
	    	slide : function(a,b) {
    			$("#antinaVal2").val(b.value);
	    	},
	    	stop : function(a,b) {
	    		that.heightChanged();
	    	}
	    });

	    /*Initialize clear factor slider*/
		$("#clear-factor").slider({
	    	range 		: "min",
	    	value 		: clear_factor,
	    	min 		: 1,
	    	max 		: 100,
	    	animate 	: true,
	    	orientation : "horizontal",
	    	slide : function(a,b){
    			$("#clear-factor_val").val(b.value);
	    	},
	    	stop : function(a,b){
	    		that.heightChanged();
	    	}
	    });

		$(".modal-dialog").css("width","70%");

		/*Plotting chart with points array using jquery.flot.js*/
		var fresnelChart = $.plot(
			$("#chart_div"),
			[ 
				{ data: dataPinpoints, label: "Pin Points", lines: { show: false}, points: { show: true ,fill: true, radius: 1}, bars: {show:true, lineWidth:1, fill:false, barWidth:0}},
				{ data: dataAltitude, label: "Altitude",lines: { show: true ,fill: 0.8, fillColor: altitudeColor}},
				{ data: dataLOS, label: "LOS", lines: { show: true}},
				{ data: dataFresnel1, label: "Fresnel-1"},
				{ data: dataFresnel2, label: "Fresnel-2"}
			],
			{
				series: {
					lines: { show: true},
					points: { show: false },
					colors: [{ opacity: 0.8 }, { brightness: 0.6, opacity: 0.8 } ]
				},
				grid: { hoverable: true, clickable: true, autoHighlight: true, backgroundColor: { colors: ["#ccc", "#fff"] }},
				yaxis: { min:minYChart, max:  maxYChart },
				xaxis: { min: 0, max:  latLongArray[arrayCounter - 1][3]},
				colors: [pinPointsColor,altitudeColor,losColor,fresnel1Color,fresnel2Color]
			}
		);

		/*Bind 'hover' events on fresnel graph*/
		var previousPoint = null;
		if(!$("#chart_div").hasClass('readytoscan')) {
			$("#chart_div").bind("plothover", function (event, pos, item) {
				/*Show point detail block*/
				$('#chart-details').show();
				that.showScanPointerDetails(pos);
				// just in case if tooltip functionality need to be disabled we can use this condition
				if (true) {
					if (item) {
						if (previousPoint != item.datapoint) {
							previousPoint = item.datapoint;
							var x = item.datapoint[0].toFixed(2),
							y = item.datapoint[1].toFixed(2);
						}
					}
					else {
						$("#tooltip").remove();
						previousPoint = null;            
					}
				}
				$("#chart_div").addClass('readytoscan');
				
				$("#chart_div").mouseout(function() {
					/*Hide point detail block*/
					$('#chart-details').hide();
				});
			});
		} //endif
		// end plothover binding

		/*Bind 'click' events on fresnel graph*/
		if(!$("#chart_div").hasClass('readytoclick')) {
			$("#chart_div").bind("plotclick", function (event, pos, item) {
				if(item) {
					fresnelChart.highlight(item.series, item.datapoint);
				} else {
					fresnelChart.unhighlight();
				}
				that.addPinPoint(that.getNearestPointX(pos.x.toFixed(2)), pos);
			});
			$("#chart_div").addClass('readytoclick');
		}

		/*Graph Click Event End*/
	};

	/**
	 * This function show hovering position detail in right side.
	 * @class devicePlottingLib
	 * @method showScanPointerDetails
	 * @param pos {JSON Object}, It contains the position object.
	 */
	this.showScanPointerDetails = function(pos) {
		
		var ptLat = parseFloat(latLongArray[that.getNearestPointX(pos.x.toFixed(2))][0]);
		var ptLon = parseFloat(latLongArray[that.getNearestPointX(pos.x.toFixed(2))][1]);

		// finding parameters on scan line 
		$('#latitude').text(ptLat.toFixed(10));
		$('#longitude').text(ptLon.toFixed(10));
		$('#distance').text(parseFloat(latLongArray[that.getNearestPointX(pos.x.toFixed(2))][3]).toFixed(2)+' Km');
		$('#altitude').text(parseFloat(latLongArray[that.getNearestPointX(pos.x.toFixed(2))][2]).toFixed(2)+' m');
		$('#obstacle').text(parseFloat((latLongArray[that.getNearestPointX(pos.x.toFixed(2))][9]) - parseFloat(latLongArray[that.getNearestPointX(pos.x.toFixed(2))][2])).toFixed(2)+' m');
		$('#los').text(parseFloat(latLongArray[that.getNearestPointX(pos.x.toFixed(2))][4]).toFixed(2)+' m' );
		$('#fresnel1').text(parseFloat(latLongArray[that.getNearestPointX(pos.x.toFixed(2))][5]).toFixed(2)+' m' );
		$('#fresnel2').text(parseFloat(latLongArray[that.getNearestPointX(pos.x.toFixed(2))][7]).toFixed(2)+' m' );
		$('#fresnel-altitude').text((parseFloat(latLongArray[that.getNearestPointX(pos.x.toFixed(2))][7] ) - parseFloat(latLongArray[that.getNearestPointX(pos.x.toFixed(2))][9])).toFixed(2)+' m' );
	};

	/**
	 * This function returns the nearest point on X-axis
	 * @class devicePlottingLib
	 * @method getNearestPointX
	 * @param posx "Int", It contains the current point X-position value
	 * @return result "Int", It contains the next or nearest point on X-axis
	 */
	this.getNearestPointX = function(posx) {
		var tmp = (parseFloat(latLongArray[0][3]) - posx)*(parseFloat(latLongArray[0][3]) - posx);
		var result = 0;
		for (i = 1; i < arrayCounter; i++) {
			if(((parseFloat(latLongArray[i][3]) - posx)*(parseFloat(latLongArray[i][3]) - posx)) < tmp){
				tmp = (parseFloat(latLongArray[i][3]) - posx)*(parseFloat(latLongArray[i][3]) - posx);
				result = i;
			}
		}
		return result;
	};

	/**
	 * This function adds pin point info at the bottom of the fresnel graph & bind hover and click event on them.
	 * @class devicePlottingLib
	 * @method addPinPoint
	 * @param index "Int", It contains counter value of no. of pin points
	 * @param pos {JSON Object}, It contains the position object.
	 */
	this.addPinPoint = function(index, pos) {
		if($('#pin-point-'+index+'').length == 0) {
			$('#pin-points-container').append('<div id="pin-point-'+index+'" class="pin-point col-md-5" pointid="'+ index +'"><span class="pin-point-name">Point '+ index +' - <input name="pinpoint'+ index +'" class="userpinpoint" type="text" size="2" value="0" /> m at <span class="point-distance'+ index +'">'+ parseFloat(latLongArray[index][3]).toFixed(2) +'</span> Km</span>  <span id="pin-point-remove'+index+'" class="pin-point-remove">X</span></div>');
			
			$('input[name="pinpoint'+ index +'"]').change(function() {
				var height =  parseFloat($(this).val());
				latLongArray[index][9] = height + parseFloat(latLongArray[index][2]);
				isDialogOpen = false;
				that.drawFresnelChart();
			});
			/*Click event on pinpoint content*/
			$('#pin-point-remove'+index+'').click(function() {
				$('#pin-point-'+index+'').remove();
				latLongArray[index][9] = latLongArray[index][2];
				isDialogOpen = false;
				that.drawFresnelChart();
			});
			/*Hover event on pinpoint content*/
			$('#pin-point-'+index+'').hover(function() {
				isDialogOpen = false;
				$('#chart-details').show();
				that.showScanPointerDetails(pos)
			},function(){
				$('#chart-details').hide();
			});

		} else {
			$('#pin-point-'+index+'').effect('highlight',{},500);
		}
	}

	/**
	 * This function trigger when any antina height slider is changed
	 * @class devicePlottingLib
	 * @method heightChanged
	 */
	this.heightChanged = function() {
		HEIGHT_CHANGED = true;
		isDialogOpen = false;
		latLongArrayCopy = latLongArray;
		antenaHight1 = $("#antinaVal1").val();
		antenaHight2 = $("#antinaVal2").val();
		clear_factor = $("#clear-factor_val").val();

		that.claculateFresnelZone(fresnelLat1,fresnelLon1,fresnelLat2,fresnelLon2,antenaHight1,antenaHight2);
	};

	/**
	 * This function fetch the basic filters from appropriate API & this populate the data to respective dropdowns
	 * @class devicePlottingLib
	 * @method getBasicFilters
	 */
	this.getBasicFilters = function() {

		var filtersData = {};

		/*Ajax call for filters data*/
		$.ajax({
			url : "../../device/filter/",
			// url : "../../static/filter_data.json",
			success : function(result) {				
				filtersData = JSON.parse(result);

				var techData = filtersData.data.objects.technology.data;
				var vendorData = filtersData.data.objects.vendor.data;
				var cityData = filtersData.data.objects.city.data;
				var stateData = filtersData.data.objects.state.data;

				/*Populate technology dropdown*/
				var techOptions = "<option value=''>Select Technology</option>";
				$.grep(techData,function(tech) {
					techOptions += "<option value='"+tech.id+"'>"+tech.value.toUpperCase()+"</option>";
				});
				$("#technology").html(techOptions);

				/*Populate Vendor dropdown*/
				var vendorOptions = "<option value=''>Select Vendor</option>";
				$.grep(vendorData,function(vendor) {
					vendorOptions += "<option value='"+vendor.id+"'>"+vendor.value.toUpperCase()+"</option>";
				});
				$("#vendor").html(vendorOptions);

				/*Populate City dropdown*/
				var cityOptions = "<option value=''>Select City</option>";
				$.grep(cityData,function(city) {
					cityOptions += "<option value='"+city.id+"'>"+city.value.toUpperCase()+"</option>";
				});
				$("#city").html(cityOptions);

				/*Populate State dropdown*/
				var stateOptions = "<option value=''>Select State</option>";
				$.grep(stateData,function(state) {
					stateOptions += "<option value='"+state.id+"'>"+state.value.toUpperCase()+"</option>";
				});
				$("#state").html(stateOptions);
			},
			error : function(err) {
				$.gritter.add({
		            // (string | mandatory) the heading of the notification
		            title: 'Basic Filters - Server Error',
		            // (string | mandatory) the text inside the notification
		            text: err.statusText,
		            // (bool | optional) if you want it to fade out on its own or just sit there
		            sticky: true
		        });
				// console.log(err);
			}
		});
	};

	/**
	 * This function filters the markers for the given filters
	 * @class devicePlottingLib
	 * @method applyFilter_gmaps
	 * @param filtersArray [JSON Array] It is an object array of filters with keys
	 */
	this.applyFilter_gmaps = function(filtersArray) {

		var filterKey = [],
			filteredData = [],
			masterIds = [];

		/*Fetch the keys from the filter array*/
		$.each(filtersArray, function(key, value) {

		    filterKey.push(key);
		});

	 	if(main_devices_data_gmaps.length > 0) {

	 		for(var i=0;i<main_devices_data_gmaps.length;i++) {

 				var master = main_devices_data_gmaps[i];

	 			/*Conditions as per the number of filters*/
	 			if(filterKey.length == 1) {
	 				
 					if(master.data[filterKey[0]].toLowerCase() == filtersArray[filterKey[0]].toLowerCase()) {

	 					/*Check For The Duplicacy*/
	 					if(masterIds.indexOf(master.id) == -1) {

	 						/*Save the BS id's to array to remove duplicacy*/
	 						masterIds.push(master.id);

	 						filteredData.push(main_devices_data_gmaps[i]);
	 					}
	 				}

	 			} else if(filterKey.length == 2) {

 					if((master.data[filterKey[0]].toLowerCase() == filtersArray[filterKey[0]].toLowerCase()) && (master.data[filterKey[1]].toLowerCase() == filtersArray[filterKey[1]].toLowerCase())) {

	 					/*Check For The Duplicacy*/
	 					if(masterIds.indexOf(master.id) == -1) {

	 						/*Save the BS id's to array to remove duplicacy*/
	 						masterIds.push(master.id);

	 						filteredData.push(main_devices_data_gmaps[i]);
	 					}
	 				}
	 			} else if(filterKey.length == 3) {

	 				if((master.data[filterKey[0]].toLowerCase() == filtersArray[filterKey[0]].toLowerCase()) && (master.data[filterKey[1]].toLowerCase() == filtersArray[filterKey[1]].toLowerCase()) && (master.data[filterKey[2]].toLowerCase() == filtersArray[filterKey[2]].toLowerCase())) {

	 					/*Check For The Duplicacy*/
	 					if(masterIds.indexOf(master.id) == -1) {

	 						/*Save the BS id's to array to remove duplicacy*/
	 						masterIds.push(master.id);

	 						filteredData.push(main_devices_data_gmaps[i]);
	 					}
	 				}
	 			} else if(filterKey.length == 4) {

	 				if((master.data[filterKey[0]].toLowerCase() == filtersArray[filterKey[0]].toLowerCase()) && (master.data[filterKey[1]].toLowerCase() == filtersArray[filterKey[1]].toLowerCase()) && (master.data[filterKey[2]].toLowerCase() == filtersArray[filterKey[2]].toLowerCase()) && (master.data[filterKey[3]].toLowerCase() == filtersArray[filterKey[3]].toLowerCase())) {

	 					/*Check For The Duplicacy*/
	 					if(masterIds.indexOf(master.id) == -1) {

	 						/*Save the BS id's to array to remove duplicacy*/
	 						masterIds.push(master.id);

	 						filteredData.push(main_devices_data_gmaps[i]);
	 					}
	 				}
	 			}
	 		}

	 		/*Check that after applying filters any data exist or not*/
	 		if(filteredData.length === 0) {

	 			$.gritter.add({
		            // (string | mandatory) the heading of the notification
		            title: 'GIS - No Devices',
		            // (string | mandatory) the text inside the notification
		            text: "User Don't Have Any Devies For Selected Filters",
		            // (bool | optional) if you want it to fade out on its own or just sit there
		            sticky: true
		        });

	 			/*Reset the markers, polyline & filters*/
	 			that.clearGmapElements();

				masterMarkersObj = [];
				slaveMarkersObj = [];

				 /*Reset The basic filters dropdown*/
			    $("#technology").val($("#technology option:first").val());
			    $("#vendor").val($("#vendor option:first").val());
			    $("#state").val($("#state option:first").val());
			    $("#city").val($("#city option:first").val());

				/*Populate the map with the all data*/
	 			that.plotDevices_gmap(main_devices_data_gmaps,"base_station");	 			

	 		} else {

				/*Reset the markers, polyline & filters*/
	 			that.clearGmapElements();

				masterMarkersObj = [];
				slaveMarkersObj = [];

				/*Populate the map with the filtered markers*/
	 			that.plotDevices_gmap(filteredData,"base_station");
	 		}	 		
	 	}	
	};

	/**
	 * This function calls the plotDevices_gmap function to load the fetched devices in case of no filters
	 * @class devicePlottingLib
	 * @method loadExistingDevices
	 */
	this.loadExistingDevices = function() {

		that.plotDevices_gmap(main_devices_data_gmaps,"base_station");
	};

	/**
     * This function makes an array from the selected filters
     * @class devicePlottingLib
     * @function makeFiltersArray
     * @param mapPageType "String", It contains the string value by which we can get the page information
     */
    this.makeFiltersArray = function(mapPageType) {

        var selectedTechnology = "",
            selectedvendor = "",
            selectedState = "",
            selectedCity = "",
        	appliedFilterObj_gmaps = {};

        if($("#technology").val().length > 0) {
        	// selectedTechnology = $("#technology option:selected").text();
        	appliedFilterObj_gmaps["technology"] = $("#technology option:selected").text();
        }

        if($("#vendor").val().length > 0) {
        	// selectedvendor = $("#vendor option:selected").text();
        	appliedFilterObj_gmaps["vendor"] = $("#vendor option:selected").text();
        }

        if($("#state").val().length > 0) {
        	// selectedState = $("#state option:selected").text();
        	appliedFilterObj_gmaps["state"] = $("#state option:selected").text();
        }

        if($("#city").val().length > 0) {
        	// selectedCity = $("#city option:selected").text();
        	appliedFilterObj_gmaps["city"] = $("#city option:selected").text();
        }


        /*Get The Length Of Filter Array*/
        var filtersLength = Object.keys(appliedFilterObj_gmaps).length;

        /*If any filter is applied then filter the data*/
        if(filtersLength > 0) {

        	if($.trim(mapPageType) == "gmap") {
        		that.applyFilter_gmaps(appliedFilterObj_gmaps);
        	} else {
        		earth_instance.applyFilter_earth(appliedFilterObj_gmaps);
        	}
        }
        /*If no filter is applied the load all the devices*/
        else {

        	/*Reset markers & polyline*/
			that.clearGmapElements();

			/*Reset Global Variables & Filters*/
			that.resetVariables_gmap();

            that.plotDevices_gmap(main_devices_data_gmaps,"base_station");
        }
    };

	/**
	 * This function creates enable the polygon drawing tool & draw the polygon
	 * @class devicePlottingLib
	 * @method createPolygon
	 */
	this.createPolygon = function() {
    	
    	selectedCount = polygonSelectedDevices.length;

    	if(selectedCount == 0) {

    		drawingManager = new google.maps.drawing.DrawingManager({
				drawingMode: google.maps.drawing.OverlayType.POLYGON,
				drawingControl: false,
				drawingControlOptions: {
					position: google.maps.ControlPosition.TOP_CENTER,
					drawingModes: [
						google.maps.drawing.OverlayType.POLYGON,
					]
				},
				map : mapInstance
			});
			
			drawingManager.setMap(mapInstance);

			google.maps.event.addListener(drawingManager, 'overlaycomplete', function(e) {

				pathArray = e.overlay.getPath().getArray();
				polygon = new google.maps.Polygon({"path" : pathArray});
				bs_ss_array = masterMarkersObj.concat(slaveMarkersObj);
				currentPolygon = e.overlay;
				currentPolygon.type = e.type;
				
				for(var k=0;k<bs_ss_array.length;k++) {
					
					var point = bs_ss_array[k].position;

					if (google.maps.geometry.poly.containsLocation(point, polygon)) {
						polygonSelectedDevices.push(bs_ss_array[k]);
					}
				}
				selectedCount = polygonSelectedDevices.length;
				if(selectedCount == 0) {
					
					bootbox.alert("No devices are under the selected area.Please re-select");
					/*Remove current polygon from map*/
					that.clearPolygon();

				} else if(selectedCount > 200) {
					
					bootbox.alert("Max. limit for selecting devices is 200.Please re-select");
					/*Remove current polygon from map*/
					that.clearPolygon();

				} else {
					// var datasetArray = [];
					// $.each(polygonSelectedDevices,function(key,val) {
					// 	datasetArray.push(val.dataset);
					// });
					// $.each(datasetArray,function(key2,dataval) {
					// 	if(dataval.name == "title" || dataval.name == "ip") {
							
					// 	}
					// });
					
					var devicesTemplate = "<div class='deviceWellContainer'>";
					for(var i=0;i<selectedCount;i++) {
						devicesTemplate += '<div class="well well-sm"><h5>'+polygonSelectedDevices[i].title+'('+polygonSelectedDevices[i].pointIp+')</h5><ul class="list-unstyled list-inline">';
						devicesTemplate += '<li><button id="play_'+i+'" onClick="that.startMonitoring('+i+')" class="btn btn-default btn-xs"><i class="fa fa-play"></i></button></li>';
						devicesTemplate += '<li><button id="pause_'+i+'" onClick="that.pauseMonitoring('+i+')" class="btn btn-default btn-xs"><i class="fa fa-pause"></i></button></li>';
						devicesTemplate += '<li><button id="stop_'+i+'" onClick="that.stopMonitoring('+i+')" class="btn btn-default btn-xs"><i class="fa fa-stop"></i></button></li>';
						devicesTemplate += '</ul><div class="sparklineContainer"><span class="sparkline" id="sparkline_'+i+'">Loading...</span></div></div>';
					}
					devicesTemplate += "</div>";
					

					$("#sideInfo > .panel-body").html(devicesTemplate);					

					if($("#sideInfoContainer").hasClass("hide")) {
						$("#sideInfoContainer").removeClass("hide");
					}
					if(!$("#createPolygonBtn").hasClass("hide")) {
						$("#createPolygonBtn").addClass("hide");
					}

					if($("#clearPolygonBtn").hasClass("hide")) {
						$("#clearPolygonBtn").removeClass("hide");
					}

					drawingManager.setDrawingMode(null);
				}

				$("#createPolygonBtn").button("complete");
				$("#advFilterBtn").button("complete");
				$("#resetFilters").button("complete");
			});
    	} else {

    		bootbox.alert("Please clear the current selection.");
    		$("#clearPolygonBtn").removeClass("hide");
    		$("#createPolygonBtn").button("complete");
			$("#advFilterBtn").button("complete");
			$("#resetFilters").button("complete");
    	}
	};

	/**
	 * This function clear the polygon selection from the map
	 * @class devicePlottingLib
	 * @method clearPolygon
	 */
	this.clearPolygon = function() {

		/*Update the html of accordian body*/
		$("#sideInfo > .panel-body").html("No device selected.");
		/*Collapse the selected devices accordian*/
		if(!$("#sideInfoContainer").hasClass("hide")) {
			$("#sideInfoContainer").addClass("hide");
		}		
		/*Show Select Devices button*/
		if($("#createPolygonBtn").hasClass("hide")) {
			$("#createPolygonBtn").removeClass("hide");
		}
		/*Hide the clear selection button*/
		if(!$("#clearPolygonBtn").hasClass("hide")) {
			$("#clearPolygonBtn").addClass("hide");
		}
		/*Remove the current polygon from the map*/
		currentPolygon.setMap(null);
		/*Reset the variables*/
		polygonSelectedDevices = [];		
		pathArray = [];
		polygon = "";
		pointsArray = [];
		// currentPolygon = {};
	};

	/**
	 * This function creates the line chart for the monitoring of selected devices
	 * @class devicePlottingLib
	 * @method makeMonitoringChart
	 * @param id 'Integer'
	 */
	this.makeMonitoringChart = function(id) {

		var startClassNames = $("#play_"+id)[0].className;
		var stopClassNames = $("#stop_"+id)[0].className;

		if(startClassNames.indexOf("active") != -1) {
			
			var num = Math.floor((Math.random() * 20) + 1)
			var oldLength = dataArray.length;
			for(var i=0;i<num;i++) {

				dataArray.push(Math.floor(Math.random() * 80));
			}

			var margin = oldLength * 5;
			
			$("#sparkline_"+id).sparkline(dataArray, {
		        type: "line",
		        lineColor: "blue",
		        spotColor : "orange",
		        defaultPixelsPerValue : 5
		    });

		    setTimeout(function() {
				$("#sparkline_"+id).css("margin-left","-"+leftMargin+"px");
				/*Decrement the margin-left value*/
				leftMargin = margin;
				/*Recursive calling*/
				that.makeMonitoringChart(id);
			},1500);

		} else if(stopClassNames.indexOf("active") != -1) {

				$("#sparkline_"+id).sparkline("", {
			        type: "line",
			        lineColor: "blue",
			        spotColor : "orange",
			        zeroAxis: false
			    });
		}
	};

	this.startMonitoring = function(id) {

		$("#play_"+id).addClass("active");
        if($("#pause_"+id).hasClass("active")) {
            $("#pause_"+id).removeClass("active");
        }
        if($("#stop_"+id).hasClass("active")) {
            $("#stop_"+id).removeClass("active");
        }

        that.makeMonitoringChart(id);
	};

	this.pauseMonitoring = function(id) {
		
		$("#pause_"+id).addClass("active");
        if($("#play_"+id).hasClass("active")) {
            $("#play_"+id).removeClass("active");
        }
        if($("#stop_"+id).hasClass("active")) {
            $("#stop_"+id).removeClass("active");
        }
        that.makeMonitoringChart(id);
	};

	this.stopMonitoring = function(id) {
		
		$("#stop_"+id).addClass("active");
        if($("#play_"+id).hasClass("active")) {
            $("#play_"+id).removeClass("active");
        }
        if($("#pause_"+id).hasClass("active")) {
            $("#pause_"+id).removeClass("active");
        }
        that.makeMonitoringChart(id);
	};
	
    /**
     * This function resets the global variables & again call the api calling function after given timeout i.e. 5 minutes
     * @class devicePlottingLib
     * @method recallServer_gmap
     */
    this.recallServer_gmap = function() {

    	/*Hide The loading Icon*/
		$("#loadingIcon").hide();

		/*Enable the refresh button*/
		$("#resetFilters").button("complete");
		

    	setTimeout(function() {
			
			/*Hide The loading Icon*/
			$("#loadingIcon").show();

			/*Enable the refresh button*/
			$("#resetFilters").button("loading");

			/*Reset markers & polyline*/
			that.clearGmapElements();

			/*Reset Global Variables & Filters*/
			that.resetVariables_gmap();
			
			/*Recall the API*/
			that.getDevicesData_gmap();

		},300000);
    };

    /**
	 * This function removes all the elements from the map
	 * @class devicePlottingLib
	 * @method clearGmapElements
	 */
	this.clearGmapElements = function() {

		/*Clear the marker array of OverlappingMarkerSpiderfier*/
		oms.clearMarkers();

		/*Clear master marker cluster objects*/
		if(masterClusterInstance != "") {
			masterClusterInstance.clearMarkers();
		}


		/*Hide The loading Icon*/
		$("#loadingIcon").hide();

		/*Enable the refresh button*/
		$("#resetFilters").button("complete");		

		/*Remove All Master Markers*/
		for(var i=0;i<masterMarkersObj.length;i++) {

			masterMarkersObj[i].setMap(null);
		}

		/*Clear the existing SS for same point*/
		for(var i=0;i<plottedSS.length;i++) {
			plottedSS[i].setMap(null);
		}

		/*Remove all link line between devices*/
		for(var j=0;j<pathLineArray.length;j++) {

			pathLineArray[j].setMap(null);
		}

		/*Clear the sectors from map*/
		for(var j=0;j<sectorArray.length;j++) {

			sectorArray[j].setMap(null);
		}
	};

	/**
	 * This function reset all global variable used in the process
	 * @class devicePlottingLib
	 * @method resetVariables_gmap
	 */
	this.resetVariables_gmap = function() {

		/*Reset All The Variables*/
		hitCounter = 1;
		showLimit = 0;
		remainingDevices = 0;
		counter = -999;
		totalCalls = 1;
		devicesObject = {};
		devices_gmaps = [];
		masterMarkersObj = [];
		plottedSS = [];
		slaveMarkersObj = [];
		clusterIcon = "";
		sectorArray = [];
		circleArray = [];
	};
}