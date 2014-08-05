/*Global Variables*/
var mapInstance = "",
	gmap_self = "",
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
	ssLinkArray = [],
	pathArray = [],
	polygon = "",
	pointsArray = [],
	currentPolygon = {},
	drawingManager = "",
	dataArray = [],
	leftMargin = 0,
	sectorArray = [],
	circleArray = [],
	servicesData = {},
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
 * @class gmap_devicePlottingLib
 * @uses jQuery
 * @uses Google Maps
 * @uses jQuery Flot
 * @uses jQuery UI
 * Coded By :- Yogender Purohit
 */
function devicePlottingClass_gmap() {

	/*Store the reference of current pointer in a global variable*/
	gmap_self = this;

	/**
	 * This function creates the base google map with the lat long of India
	 * @method createMap
	 * @param domElement {String} It the the dom element on which the map is to be create
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
		oms = new OverlappingMarkerSpiderfier(mapInstance,{markersWontMove: true, markersWontHide: true, keepSpiderfied: true});

		/*Create a instance of google map info window*/
		infowindow = new google.maps.InfoWindow();		

		oms.addListener('click', function(marker,e) {

			var isChecked = $("#showAllSS:checked").length;
			
			if($.trim(marker.pointType) == 'base_station') {

				if(isChecked != 1) {

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

					gmap_self.plotSubStation_gmap(marker);
				}
			}

			var windowPosition = new google.maps.LatLng(marker.ptLat,marker.ptLon);
			/*Call the function to create info window content*/
			var content = gmap_self.makeWindowContent(marker);
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
	 * @method getDevicesData_gmap
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
				url : window.location.origin+"/"+"device/stats/",
				// url : window.location.origin+"/"+"static/new_format.json",
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
									clusterIcon = window.location.origin+"/"+devicesObject.data.objects.data.unspiderfy_icon;
								}

								/*Check that any filter is applied or not*/
								var appliedFilterLength_gmaps = Object.keys(appliedFilterObj_gmaps).length;

								if(appliedFilterLength_gmaps > 0) {
									/*If any filter is applied then plot the fetch data as per the filters*/
									gmap_self.applyFilter_gmaps(appliedFilterObj_gmaps);
								} else {
									/*Call the plotDevices_gmap to show the markers on the map*/
									gmap_self.plotDevices_gmap(devices_gmaps,"base_station");
								}

								/*Call the function after 3 sec.*/
								setTimeout(function() {
										
									gmap_self.getDevicesData_gmap();
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
								gmap_self.recallServer_gmap();
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
							gmap_self.recallServer_gmap();
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

						gmap_self.recallServer_gmap();
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
					gmap_self.recallServer_gmap();
				}
			});
		} else {

			/*Recall the server after the defined time*/
			gmap_self.recallServer_gmap();
		}
	};

	/**
     * This function is used to plot BS or SS devices & their respective elements on the google maps
     * @method plotDevices_gmap
     * @param stationObject {Object} In case of BS, it is the devies object array & for SS it contains BS marker object with SS & sector info
     * @param stationType {String}, It contains that the points are for BS or SS.
	 */
	this.plotDevices_gmap = function(stationObject,stationType) {

		var bsLatArray = [],
			bsLonArray = [],
			bs_ss_devices = [];

		if($.trim(stationType) == "base_station") {
			bs_ss_devices = stationObject;
		} else {
			bs_ss_devices = stationObject.child_ss;
		}

		for(var i=0;i<bs_ss_devices.length;i++) {

			var deviceData = [],
				pt_technology = "",
				bhInfo = [],
				bsInfo = [];

			if($.trim(stationType) == "base_station") {
				deviceData = bs_ss_devices[i].data.param.base_station;
				bsInfo = bs_ss_devices[i].data.param.base_station;
				pt_technology = bs_ss_devices[i].data.technology;
				bhInfo = bs_ss_devices[i].data.param.backhual;
			} else {
				bsInfo = bs_ss_devices[i].data.param.sub_station;
				deviceData = bs_ss_devices[i].data.param.sub_station;
			}

			/*If base station then create all the sectors within it.*/
			if($.trim(stationType) == "base_station") {

		    	/*In case of PMP or WIMAX*/
				if($.trim(bs_ss_devices[i].data.technology) != "PTP" && $.trim(bs_ss_devices[i].data.technology) != "P2P") {
					
					var sector_array = bs_ss_devices[i].data.param.sector;

					$.grep(sector_array,function(sector) {

		    			var lat = bs_ss_devices[i].data.lat;
						var lon = bs_ss_devices[i].data.lon;
						var azimuth = sector.azimuth_angle;
						var beam_width = sector.beam_width;
						var sector_color = sector.color;
						var sectorInfo = sector.info;
						var orientation = $.trim(sector.orientation);
						var sector_child = sector.sub_station;
						
						var rad = 4;
						var sectorRadius = (+sector.radius);

						/*If radius is greater than 4 Kms then set it to 4.*/
						if((sectorRadius <= 4) && (sectorRadius != null) && (sectorRadius > 0)) {
							rad = sectorRadius;
						}

						/*Call createSectorData function to get the points array to plot the sector on google maps.*/
						gmap_self.createSectorData(lat,lon,rad,azimuth,beam_width,orientation,function(pointsArray) {

							/*Plot sector on map with the retrived points*/
							gmap_self.plotSector_gmap(lat,lon,pointsArray,sectorInfo,sector_color,sector_child);

						});
		    		});		    		
		    		/*In case of PTP*/
				} else {

					var has_ss = bs_ss_devices[i].data.param.sector[0].sub_station.length;					
					if(has_ss > 0) {

						var ss_marker_obj = bs_ss_devices[i].data.param.sector[0].sub_station[0];						

						/*Create SS Marker Object*/
						var ss_marker_object = {
					    	position  	     : new google.maps.LatLng(ss_marker_obj.data.lat,ss_marker_obj.data.lon),
					    	ptLat 		     : ss_marker_obj.data.lat,
					    	ptLon 		     : ss_marker_obj.data.lon,
					    	technology 	     : pt_technology,
					    	map       	     : mapInstance,
					    	icon 	  	     : window.location.origin+"/"+ss_marker_obj.data.markerUrl,
					    	oldIcon 	     : window.location.origin+"/"+ss_marker_obj.data.markerUrl,
					    	pointType	     : "sub_station",
							dataset 	     : ss_marker_obj.data.param.sub_station,
							bhInfo 			 : [],
							antena_height    : ss_marker_obj.data.antena_height,
							name 		 	 : ss_marker_obj.name,
							device_name 	 : ss_marker_obj.device_name,
							zIndex 			 : 200
						};

						/*Create SS Marker*/
					    var ss_marker = new google.maps.Marker(ss_marker_object);

					    bsLatArray.push(ss_marker_obj.data.lat);
						bsLonArray.push(ss_marker_obj.data.lon);
					    
					    var startEndObj = {},
					    	ss_info = {},
					    	base_info = {};

					    startEndObj["startLat"] = bs_ss_devices[i].data.lat;
			    		startEndObj["startLon"] = bs_ss_devices[i].data.lon;
					    
					    startEndObj["endLat"] = ss_marker_obj.data.lat;
			    		startEndObj["endLon"] = ss_marker_obj.data.lon;

			    		/*Sub station info Object*/
			    		ss_info["info"] = ss_marker_obj.data.param.sub_station;
			    		ss_info["antena_height"] = ss_marker_obj.data.antena_height;

			    		
			    		/*Link color object*/
			    		linkColor = ss_marker_obj.data.link_color;
			    			
		    			base_info["info"] = bs_ss_devices[i].data.param.base_station;
		    			base_info["antena_height"] = bs_ss_devices[i].data.antena_height;
		    			
		    			if(ss_marker_obj.data.show_link == 1) {
		    				/*Create the link between BS & SS or Sector & SS*/
					    	var ss_link_line = gmap_self.createLink_gmaps(startEndObj,linkColor,base_info,ss_info);

					    	ssLinkArray.push(ss_link_line);
		    			}
					    /*Add SS markers to the OverlappingMarkerSpiderfier*/
		    			oms.addMarker(ss_marker);
					}
				}
		    }

		    /*Create BS or SS Marker Object*/
			var station_marker_object = {
		    	position  	     : new google.maps.LatLng(bs_ss_devices[i].data.lat,bs_ss_devices[i].data.lon),
		    	ptLat 		     : bs_ss_devices[i].data.lat,
		    	ptLon 		     : bs_ss_devices[i].data.lon,
		    	technology 	     : pt_technology,
		    	map       	     : mapInstance,
		    	icon 	  	     : window.location.origin+"/"+bs_ss_devices[i].data.markerUrl,
		    	oldIcon 	     : window.location.origin+"/"+bs_ss_devices[i].data.markerUrl,
		    	pointType	     : stationType,
				child_ss   	     : bs_ss_devices[i].data.param.sector,
				original_sectors : bs_ss_devices[i].data.param.sector,
				dataset 	     : deviceData,
				bsInfo 			 : bsInfo,
				bhInfo 			 : bhInfo,
				bs_name 		 : bs_ss_devices[i].name,
				name 		 	 : bs_ss_devices[i].name,
				antena_height    : bs_ss_devices[i].data.antena_height,
				zIndex 			 : 200
			};

			/*Create BS or SS Marker*/
		    var station_marker = new google.maps.Marker(station_marker_object);

			/*Get All BS Lat & Lon*/
			bsLatArray.push(bs_ss_devices[i].data.lat);
			bsLonArray.push(bs_ss_devices[i].data.lon);


		    if($.trim(stationType) != "base_station") {

		    	var startEndObj = {},
	    			linkColor = {},
	    			bs_info = {},
	    			ss_info = {};

		    	if($.trim(stationObject.technology) == "P2P" || $.trim(stationObject.technology) == "PTP") {
		    		/*Start & end point object*/
		    		startEndObj["startLat"] = stationObject.ptLat;
		    		startEndObj["startLon"] = stationObject.ptLon;
		    	} else {
		    			
					startEndObj["startLat"] = stationObject.startLat;
	    			startEndObj["startLon"] = stationObject.startLon;
		    	}

		    	/*Base station info Object*/
	    		bs_info["info"] = stationObject.dataset;
	    		bs_info["antena_height"] = stationObject.antena_height;
		    	

		    	startEndObj["endLat"] = bs_ss_devices[i].data.lat;
	    		startEndObj["endLon"] = bs_ss_devices[i].data.lon;

	    		/*Sub station info Object*/
	    		ss_info["info"] = bs_ss_devices[i].data.param.sub_station;
	    		ss_info["antena_height"] = bs_ss_devices[i].data.antena_height;

	    		/*Link color object*/
	    		linkColor = bs_ss_devices[i].data.link_color;
	    		
		    	/*Create the link between BS & SS or Sector & SS*/
		    	var polyLineObj = gmap_self.createLink_gmaps(startEndObj,linkColor,bs_info,ss_info);		    	

		    	/*Push the created line in global line array*/
		    	pathLineArray.push(polyLineObj);
		    	/*Push the plotted SS to an array for further use*/
		    	plottedSS.push(station_marker);
		    }

		    if($.trim(stationType) == "base_station") {
		    	
		    	/*Add the master marker to the global master markers array*/
		    	masterMarkersObj.push(station_marker);
		    	masterMarkersObj.push(ss_marker);
		    }

		    /*Add parent markers to the OverlappingMarkerSpiderfier*/
		    oms.addMarker(station_marker);
		}

		/*Loop to change the icon for same location markers(to cluster icon)*/
		for(var k=0;k<masterMarkersObj.length;k++) {
			
			if(masterMarkersObj[k] != undefined) {

				/*if two BS on same position*/
				var bsLatOccurence = $.grep(bsLatArray, function (elem) {return elem === masterMarkersObj[k].ptLat;}).length;
				var bsLonOccurence = $.grep(bsLonArray, function (elem) {return elem === masterMarkersObj[k].ptLon;}).length;

				if(bsLatOccurence > 1 && bsLonOccurence > 1) {
					masterMarkersObj[k].setOptions({"icon" : clusterIcon});
				}
			} else {
				masterMarkersObj.splice(k, 1);
			}
		}

		/*Cluster options object*/
		var clusterOptions = {gridSize: 70, maxZoom: 8};
		/*Add the master markers to the cluster MarkerCluster object*/
		masterClusterInstance = new MarkerClusterer(mapInstance, masterMarkersObj, clusterOptions);
	};

	/**
	 * This function plots all the sub-station in given sectors object array.
	 * @method plotSubStation_gmap.
	 * @param stationSectorObject {Object} It contains sector object in which SS are present.
	 */
	this.plotSubStation_gmap = function(stationSectorObject) {

		var sectorObj = stationSectorObject.original_sectors;

		if($.trim(stationSectorObject.technology) != "PTP" && $.trim(stationSectorObject.technology) != "P2P") {
			
			for(var i=0;i<sectorObj.length;i++) {

				var rad = 4;

				var sectorRadius = (+sectorObj[i].radius);

				/*If radius is greater than 4 Kms then set it to 4.*/
				if((sectorRadius <= 4) && (sectorRadius != null) && (sectorRadius > 0)) {
					rad = sectorRadius;
				}

				gmap_self.createSectorData(stationSectorObject.ptLat,stationSectorObject.ptLon,rad,sectorObj[i].azimuth_angle,sectorObj[i].beam_width,sectorObj[i].orientation,function(pointArray) {

					var halfPt = Math.floor(pointArray.length / (+2));

					stationSectorObject["startLat"] = pointArray[halfPt].lat;
					stationSectorObject["startLon"] = pointArray[halfPt].lon;
				});

				stationSectorObject["child_ss"] = sectorObj[i].sub_station;
				stationSectorObject["dataset"] = sectorObj[i].info;				

				gmap_self.plotDevices_gmap(stationSectorObject,"sub_station");
			}
		}
	};


	/**
	 * This function plot all the BS & SS on google maps & bind events accordingly
	 * @method plotAllDevice_gmap. 
	 */
	this.plotAllDevice_gmap = function() {
		
		var isChecked = $("#showAllSS:checked").length;

		if(isChecked == 1) {

			/*Check "Show Connection Line" checkbox*/
			$("#showConnLines").prop('checked', true);

			$.grep(masterMarkersObj, function(plotedDevices) {
				
				if($.trim(plotedDevices.pointType) == 'base_station') {

					gmap_self.plotSubStation_gmap(plotedDevices);
				}
			});
		} else {

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

			/*Uncheck "Show Connection Line" checkbox*/
			$("#showConnLines").prop('checked', false);
		}
	};


	/**
	 * This function creates a link between Bs & SS
	 * @method createLink_gmaps. 
	 * @param startEndObj {Object}, It contains the start & end points json object.
	 * @param linkColor {String}, It contains the color for link line.
	 * @param bs_info {Object}, It contains the start point information json object.
	 * @param ss_info {Object}, It contains the end point information json object.
	 * @return {Object} pathConnector, It contains gmaps polyline object.
	 */
	this.createLink_gmaps = function(startEndObj,linkColor,bs_info,ss_info) {

		var pathDataObject = [
			new google.maps.LatLng(startEndObj.startLat,startEndObj.startLon),
			new google.maps.LatLng(startEndObj.endLat,startEndObj.endLon)
		],
		linkObject = {},
		link_path_color = linkColor;

		linkObject = {
			path 			: pathDataObject,
			strokeColor		: link_path_color,
			strokeOpacity	: 1.0,
			strokeWeight	: 3,
			pointType 		: "path",
			geodesic		: true,
			ss_info			: ss_info.info,
			ss_lat 			: startEndObj.endLat,
			ss_lon 			: startEndObj.endLon,
			ss_perf 		: ss_info.perf,
			ss_height 		: ss_info.antena_height,
			bs_lat 			: startEndObj.startLat,
			bs_info 		: bs_info.info,
			bs_lon 			: startEndObj.startLon,
			bs_perf 		: bs_info.perf,
			bs_height 		: bs_info.antena_height,
			zIndex 			: 9999
		};

		pathConnector = new google.maps.Polyline(linkObject);
		/*Plot the link line between master & slave*/
		pathConnector.setMap(mapInstance);

		/*Bind Click Event on Link Path Between Master & Slave*/
		google.maps.event.addListener(pathConnector, 'click', function(e) {

			/*Call the function to create info window content*/
			var content = gmap_self.makeWindowContent(this);
			/*Set the content for infowindow*/
			infowindow.setContent(content);
			/*Set The Position for InfoWindow*/
			infowindow.setPosition(e.latLng);
			/*Open the info window*/
			infowindow.open(mapInstance);
		});

		/*returns gmap polyline object */
		return pathConnector;
	};

	/**
	 * This function show/hide the connection line between BS & SS.
	 * @method showConnectionLines_gmap
	 */
	this.showConnectionLines_gmap = function() {

		var isLineChecked = $("#showConnLines:checked").length;

		var isSSChecked = $("#showAllSS:checked").length;

		var existing_lines = pathLineArray;

		/*Unchecked case*/
		if(isLineChecked == 0) {

			for (var i = 0; i < pathLineArray.length; i++) {
				pathLineArray[i].setMap(null);
			}

		} else {

			if(isSSChecked == 1) {
				for (var i = 0; i < existing_lines.length; i++) {
					existing_lines[i].setMap(mapInstance);
				}
			} else {

				bootbox.alert('Please select "Show Connected SS" first.');
				$("#showConnLines").prop('checked', false);

			}
		}
	};


	/**
	 * This function creates data to plot sectors on google maps.
	 * @method createSectorData.
	 * @param Lat {Number}, It contains lattitude of any point.
	 * @param Lng {Number}, It contains longitude of any point.
	 * @param radius {Number}, It contains radius for sector.
	 * @param azimuth {Number}, It contains azimuth angle for sector.
	 * @param beamwidth {Number}, It contains width for the sector.
	 * @param sectorData {Object}, It contains sector info json object.
	 * @param orientation {String}, It contains the orientation type of antena i.e. vertical or horizontal
	 * @return {Object Array} sectorDataArray, It is the polygon points lat-lon object array
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
	 * @method plotSector_gmap.
	 * @param Lat {Number}, It contains lattitude of the point on which sector is creater i.e. BS lat-lon.
	 * @param Lng {Number}, It contains longitude of the point on which sector is creater i.e. BS lat-lon.
	 * @param pointsArray [Array], It contains the points lat-lon object array.
	 * @param sectorInfo {JSON Object Array}, It contains the information about the sector which are shown in info window.
	 * @param bgColor {String}, It contains the RGBA format color code for sector.
	 * @param sector_child [JSON object Array], It contains the connected SS data.
	 */
	this.plotSector_gmap = function(lat,lon,pointsArray,sectorInfo,bgColor,sector_child) {

		var polyPathArray = [];
		
		var halfPt = Math.floor(pointsArray.length / (+2));
		
		var startLat = pointsArray[halfPt].lat;
		var startLon = pointsArray[halfPt].lon;

		for(var i=0;i<pointsArray.length;i++) {
			var pt = new google.maps.LatLng(pointsArray[i].lat,pointsArray[i].lon);
			polyPathArray.push(pt);
		}

		var poly = new google.maps.Polygon({
			map 		     : mapInstance,
			path 		     : polyPathArray,
			ptLat 		     : lat,
			ptLon 		     : lon,
			strokeColor      : bgColor,
			fillColor 	     : bgColor,
			pointType	     : "sector",
			strokeOpacity    : 1.0,
			fillOpacity 	 : 0.6,
			strokeWeight     : 1,
			dataset 	     : sectorInfo,
			startLat 	     : startLat,
			startLon 	     : startLon,
			bhInfo 			 : [],
			child_ss 	     : sector_child,
			original_sectors : sector_child,
			zIndex 			 : 180,
			geodesic		 : true
        });

        /*Push polygon to an array*/
		sectorArray.push(poly);

        poly.setMap(mapInstance);

        /*listener for click event of sector*/
		google.maps.event.addListener(poly,'click',function(e) {

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

			gmap_self.plotDevices_gmap(this,"sub_station");

			var windowPosition = new google.maps.LatLng(e.latLng.k,e.latLng.B);
			/*Call the function to create info window content*/
			var content = gmap_self.makeWindowContent(poly);
			/*Set the content for infowindow*/
			infowindow.setContent(content);
			/*Set The Position for InfoWindow*/
			infowindow.setPosition(windowPosition);
			/*Open the info window*/
			infowindow.open(mapInstance);
		});
	};

	/**
	 * This function creates the info window content for BS,SS & link path 
	 * @method makeWindowContent
	 * @param contentObject {Object} It contains current pointer(this) information
	 * @return {String} windowContent, It contains content to be shown on info window
	 */
	this.makeWindowContent = function(contentObject) {

		var windowContent = "",
			infoTable =  "",
			perfContent = "",
			clickedType = $.trim(contentObject.pointType);

		/*True,if clicked on the link line*/
		if(clickedType == "path") {

			infoTable += "<table class='table table-bordered'><thead><th>BS-Sector Info</th><th>SS Info</th></thead><tbody>";
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

			infoTable += "</tr>";
			infoTable += "</tbody></table>";
			
			/*Concat infowindow content*/
			windowContent += "<div class='windowContainer'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i> BS-SS</h4></div><div class='box-body'>"+infoTable+"<div class='clearfix'></div><ul class='list-unstyled list-inline'><li><button class='btn btn-sm btn-info' onClick='gmap_self.claculateFresnelZone("+contentObject.bs_lat+","+contentObject.bs_lon+","+contentObject.ss_lat+","+contentObject.ss_lon+","+contentObject.bs_height+","+contentObject.ss_height+");'>Fresnel Zone</button></li></ul></div></div></div>";

		} else {

			infoTable += "<table class='table table-bordered'><tbody>";
			var startPtInfo = [];

			if(contentObject.bsInfo != undefined) {
				startPtInfo = contentObject.bsInfo;
			} else {
				startPtInfo = contentObject.dataset;	
			}
			for(var i=0;i<startPtInfo.length;i++) {

				if(startPtInfo[i].show == 1) {
					infoTable += "<tr><td>"+startPtInfo[i].title+"</td><td>"+startPtInfo[i].value+"</td></tr>";
				}
			}
			
			/*Set the lat lon of the point*/
			infoTable += "<tr><td>Lat, Long</td><td>"+contentObject.ptLat+", "+contentObject.ptLon+"</td></tr>";

			if(clickedType == "base_station") {

				infoTable += "<tr><td colspan='2'><b>Backhaul Info</b></td></tr>";
				for(var i=0;i<contentObject.bhInfo.length;i++) {

					if(contentObject.bhInfo[i].show == 1) {
						infoTable += "<tr><td>"+contentObject.bhInfo[i].title+"</td><td>"+contentObject.bhInfo[i].value+"</td></tr>";
					}
				}
			}

			infoTable += "</tbody></table>";

			/*Final infowindow content string*/
			windowContent += "<div class='windowContainer'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>  "+contentObject.pointType.toUpperCase()+"</h4></div><div class='box-body'><div class='' align='center'>"+infoTable+"</div><div class='clearfix'></div></div></div></div>";
		}
		/*Return the info window content*/
		return windowContent;
	};

	/**
	 * This function calculates the fresnel zone for the given lat-lon's
	 * @method claculateFresnelZone
	 * @param lat1 {Number}, It contains lattitude of first point
	 * @param lon1 {Number}, It contains longitude of first point
	 * @param lat2 {Number}, It contains lattitude of second point
	 * @param lon2 {Number}, It contains longitude of second point
	 * @param height1 {Number}, It contains antina height of first point
	 * @param height2 {Number}, It contains antina height of second point
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
	    gmap_self.getFresnelPath(lat1.toRad(), lon1.toRad(), lat2.toRad(), lon2.toRad(), depthStep);

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
	            gmap_self.getFresnelChartData(elevationArray, distance_between_sites);
	        }
	    });
	};

	/**
	 * This function generate fresnel point data.
	 * @method getFresnelPath
	 * @param lat1 {Number}, It contains lattitude of first point
	 * @param lon1 {Number}, It contains longitude of first point
	 * @param lat2 {Number}, It contains lattitude of second point
	 * @param lon2 {Number}, It contains longitude of second point
	 * @param depth {Number}, It contains accuracy or depth value for which lat-lons path has to be calculated
	 */
	this.getFresnelPath = function(lat1, lon1, lat2, lon2, depth) {

	    var mlat = gmap_self.getMidPT_Lat(lat1, lon1, lat2, lon2);
	    var mlon = gmap_self.getMidPT_Lon(lat1, lon1, lat2, lon2);
	    
	    if (depth > 0) {
	        gmap_self.getFresnelPath(lat1, lon1, mlat, mlon, depth - 1);
	        latLongArray[arrayCounter] = new Array();
	        latLongArray[arrayCounter][0] = mlat.toDeg();
	        latLongArray[arrayCounter++][1] = mlon.toDeg();

	        gmap_self.getFresnelPath(mlat, mlon, lat2, lon2, depth - 1);
	    }
	    else {
	        latLongArray[arrayCounter] = new Array();
	        latLongArray[arrayCounter][0] = mlat.toDeg();
	        latLongArray[arrayCounter++][1] = mlon.toDeg();
	    }
	};

	/**
	 * This function calculates mid lattitude point for given lat-lons
	 * @method getMidPT_Lat
	 * @param lat1 {Number}, It contains lattitude of first point
	 * @param lon1 {Number}, It contains longitude of first point
	 * @param lat2 {Number}, It contains lattitude of second point
	 * @param lon2 {Number}, It contains longitude of second point
	 * @return {Number}  lat3, It contains mid pt lat value
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
	 * @method getMidPT_Lon
	 * @param lat1 {Number}, It contains lattitude of first point
	 * @param lon1 {Number}, It contains longitude of first point
	 * @param lat2 {Number}, It contains lattitude of second point
	 * @param lon2 {Number}, It contains longitude of second point
	 * @return {Number} lon3, It contains mid pt lon value
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
	 * @method getFresnelChartData
	 * @param elevationArray [Int Array], It contains elevation values array
	 * @param pt_distance {Number}, It contains distance between two points
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
	    gmap_self.drawFresnelChart();
	};

	/**
	 * This function creates the fresnal zone chart with elevation points using jquery.flot.js
	 * @method drawFresnelChart
	 * @uses jquery.flot.js
	 * @uses bootbox.js
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
	    		gmap_self.heightChanged();
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
	    		gmap_self.heightChanged();
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
	    		gmap_self.heightChanged();
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
				gmap_self.showScanPointerDetails(pos);
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
				gmap_self.addPinPoint(gmap_self.getNearestPointX(pos.x.toFixed(2)), pos);
			});
			$("#chart_div").addClass('readytoclick');
		}

		/*Graph Click Event End*/
	};

	/**
	 * This function show hovering position detail in right side.
	 * @method showScanPointerDetails
	 * @param pos {Object}, It contains the position object.
	 */
	this.showScanPointerDetails = function(pos) {
		
		var ptLat = parseFloat(latLongArray[gmap_self.getNearestPointX(pos.x.toFixed(2))][0]);
		var ptLon = parseFloat(latLongArray[gmap_self.getNearestPointX(pos.x.toFixed(2))][1]);

		// finding parameters on scan line 
		$('#latitude').text(ptLat.toFixed(10));
		$('#longitude').text(ptLon.toFixed(10));
		$('#distance').text(parseFloat(latLongArray[gmap_self.getNearestPointX(pos.x.toFixed(2))][3]).toFixed(2)+' Km');
		$('#altitude').text(parseFloat(latLongArray[gmap_self.getNearestPointX(pos.x.toFixed(2))][2]).toFixed(2)+' m');
		$('#obstacle').text(parseFloat((latLongArray[gmap_self.getNearestPointX(pos.x.toFixed(2))][9]) - parseFloat(latLongArray[gmap_self.getNearestPointX(pos.x.toFixed(2))][2])).toFixed(2)+' m');
		$('#los').text(parseFloat(latLongArray[gmap_self.getNearestPointX(pos.x.toFixed(2))][4]).toFixed(2)+' m' );
		$('#fresnel1').text(parseFloat(latLongArray[gmap_self.getNearestPointX(pos.x.toFixed(2))][5]).toFixed(2)+' m' );
		$('#fresnel2').text(parseFloat(latLongArray[gmap_self.getNearestPointX(pos.x.toFixed(2))][7]).toFixed(2)+' m' );
		$('#fresnel-altitude').text((parseFloat(latLongArray[gmap_self.getNearestPointX(pos.x.toFixed(2))][7] ) - parseFloat(latLongArray[gmap_self.getNearestPointX(pos.x.toFixed(2))][9])).toFixed(2)+' m' );
	};

	/**
	 * This function returns the nearest point on X-axis
	 * @method getNearestPointX
	 * @param posx {Number}, It contains the current point X-position value
	 * @return {Number} result, It contains the next or nearest point on X-axis
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
	 * @method addPinPoint
	 * @param index {Number}, It contains counter value of no. of pin points
	 * @param pos {Object}, It contains the position object.
	 */
	this.addPinPoint = function(index, pos) {
		if($('#pin-point-'+index+'').length == 0) {
			$('#pin-points-container').append('<div id="pin-point-'+index+'" class="pin-point col-md-5" pointid="'+ index +'"><span class="pin-point-name">Point '+ index +' - <input name="pinpoint'+ index +'" class="userpinpoint" type="text" size="2" value="0" /> m at <span class="point-distance'+ index +'">'+ parseFloat(latLongArray[index][3]).toFixed(2) +'</span> Km</span>  <span id="pin-point-remove'+index+'" class="pin-point-remove">X</span></div>');
			
			$('input[name="pinpoint'+ index +'"]').change(function() {
				var height =  parseFloat($(this).val());
				latLongArray[index][9] = height + parseFloat(latLongArray[index][2]);
				isDialogOpen = false;
				gmap_self.drawFresnelChart();
			});
			/*Click event on pinpoint content*/
			$('#pin-point-remove'+index+'').click(function() {
				$('#pin-point-'+index+'').remove();
				latLongArray[index][9] = latLongArray[index][2];
				isDialogOpen = false;
				gmap_self.drawFresnelChart();
			});
			/*Hover event on pinpoint content*/
			$('#pin-point-'+index+'').hover(function() {
				isDialogOpen = false;
				$('#chart-details').show();
				gmap_self.showScanPointerDetails(pos)
			},function(){
				$('#chart-details').hide();
			});

		} else {
			$('#pin-point-'+index+'').effect('highlight',{},500);
		}
	}

	/**
	 * This function trigger when any antina height slider is changed
	 * @method heightChanged
	 */
	this.heightChanged = function() {
		HEIGHT_CHANGED = true;
		isDialogOpen = false;
		latLongArrayCopy = latLongArray;
		antenaHight1 = $("#antinaVal1").val();
		antenaHight2 = $("#antinaVal2").val();
		clear_factor = $("#clear-factor_val").val();

		gmap_self.claculateFresnelZone(fresnelLat1,fresnelLon1,fresnelLat2,fresnelLon2,antenaHight1,antenaHight2);
	};

	/**
	 * This function fetch the basic filters from appropriate API & this populate the data to respective dropdowns
	 * @method getBasicFilters
	 */
	this.getBasicFilters = function() {

		var filtersData = {};

		/*Ajax call for filters data*/
		$.ajax({
			url : window.location.origin+"/"+"device/filter/",
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
	 * This function filters bs-ss object as per the applied filters
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

				// master.data[filterKey[0]].toLowerCase().split(",").indexOf(filtersArray[filterKey[0]].toLowerCase())
	 			/*Conditions as per the number of filters*/
	 			if(filterKey.length == 1) {

	 				var dataVal1 = master.data[filterKey[0]].toLowerCase().split(",");
	 				var selectedVal1 = filtersArray[filterKey[0]].toLowerCase();

 					if(dataVal1.indexOf(selectedVal1) > -1) {

	 					/*Check For The Duplicacy*/
	 					if(masterIds.indexOf(master.id) == -1) {

	 						/*Save the BS id's to array to remove duplicacy*/
	 						masterIds.push(master.id);

	 						filteredData.push(main_devices_data_gmaps[i]);
	 					}
	 				}

	 			} else if(filterKey.length == 2) {

	 				var dataVal1 = master.data[filterKey[0]].toLowerCase().split(",");
	 				var selectedVal1 = filtersArray[filterKey[0]].toLowerCase();

	 				var dataVal2 = master.data[filterKey[1]].toLowerCase().split(",");
	 				var selectedVal2 = filtersArray[filterKey[1]].toLowerCase();

 					if((dataVal1.indexOf(selectedVal1) > -1) && (dataVal2.indexOf(selectedVal2) > -1)) {

	 					/*Check For The Duplicacy*/
	 					if(masterIds.indexOf(master.id) == -1) {

	 						/*Save the BS id's to array to remove duplicacy*/
	 						masterIds.push(master.id);

	 						filteredData.push(main_devices_data_gmaps[i]);
	 					}
	 				}
	 			} else if(filterKey.length == 3) {

	 				var dataVal1 = master.data[filterKey[0]].toLowerCase().split(",");
	 				var selectedVal1 = filtersArray[filterKey[0]].toLowerCase();

	 				var dataVal2 = master.data[filterKey[1]].toLowerCase().split(",");
	 				var selectedVal2 = filtersArray[filterKey[1]].toLowerCase();

	 				var dataVal3 = master.data[filterKey[2]].toLowerCase().split(",");
	 				var selectedVal3 = filtersArray[filterKey[2]].toLowerCase();
	 				
	 				if((dataVal1.indexOf(selectedVal1) > -1) && (dataVal2.indexOf(selectedVal2) > -1) && (dataVal3.indexOf(selectedVal3) > -1)) {

	 					/*Check For The Duplicacy*/
	 					if(masterIds.indexOf(master.id) == -1) {

	 						/*Save the BS id's to array to remove duplicacy*/
	 						masterIds.push(master.id);

	 						filteredData.push(main_devices_data_gmaps[i]);
	 					}
	 				}
	 			} else if(filterKey.length == 4) {

	 				var dataVal1 = master.data[filterKey[0]].toLowerCase().split(",");
	 				var selectedVal1 = filtersArray[filterKey[0]].toLowerCase();

	 				var dataVal2 = master.data[filterKey[1]].toLowerCase().split(",");
	 				var selectedVal2 = filtersArray[filterKey[1]].toLowerCase();

	 				var dataVal3 = master.data[filterKey[2]].toLowerCase().split(",");
	 				var selectedVal3 = filtersArray[filterKey[2]].toLowerCase();

	 				var dataVal4 = master.data[filterKey[3]].toLowerCase().split(",");
	 				var selectedVal4 = filtersArray[filterKey[3]].toLowerCase();

	 				if((dataVal1.indexOf(selectedVal1) > -1) && (dataVal2.indexOf(selectedVal2) > -1) && (dataVal3.indexOf(selectedVal3) > -1) && (dataVal4.indexOf(selectedVal4) > -1)) {

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
	 			gmap_self.clearGmapElements();

				masterMarkersObj = [];
				slaveMarkersObj = [];

				 /*Reset The basic filters dropdown*/
			    $("#technology").val($("#technology option:first").val());
			    $("#vendor").val($("#vendor option:first").val());
			    $("#state").val($("#state option:first").val());
			    $("#city").val($("#city option:first").val());

				/*Populate the map with the all data*/
	 			gmap_self.plotDevices_gmap(main_devices_data_gmaps,"base_station");	 			

	 		} else {

				/*Reset the markers, polyline & filters*/
	 			gmap_self.clearGmapElements();

				masterMarkersObj = [];
				slaveMarkersObj = [];

				/*Populate the map with the filtered markers*/
	 			gmap_self.plotDevices_gmap(filteredData,"base_station");
	 		}	 		
	 	}	
	};

	/**
	 * This function calls the plotDevices_gmap function to load the fetched devices in case of no filters
	 * @method loadExistingDevices
	 */
	this.loadExistingDevices = function() {

		gmap_self.plotDevices_gmap(main_devices_data_gmaps,"base_station");
	};

	/**
     * This function makes an array from the selected filters
     * @method makeFiltersArray
     * @param mapPageType {String}, It contains the string value by which we can get the page information
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

        	/*Zoom to the selected state area*/
        	$.getJSON("https://maps.googleapis.com/maps/api/geocode/json?address="+$("#state option:selected").text(),function(result) {
        	
	        	var bounds = new google.maps.LatLngBounds();
	    		/*point bounds to the place location*/
	    		var ptLatLon = new google.maps.LatLng(result.results[0].geometry.location.lat, result.results[0].geometry.location.lng);
	    		bounds.extend(ptLatLon);
	    		/*call fitbounts for the mapInstance with the place location bounds object*/
	    		mapInstance.fitBounds(bounds)

	    		var listener = google.maps.event.addListener(mapInstance, "idle", function() { 
	    			/*check for current zoom level*/
					if (mapInstance.getZoom() > 8) {
						mapInstance.setZoom(8);
					}
					google.maps.event.removeListener(listener);
				});
	        });
        }

        if($("#city").val().length > 0) {
        	// selectedCity = $("#city option:selected").text();
        	appliedFilterObj_gmaps["city"] = $("#city option:selected").text();

        	/*Zoom to the selected city area*/
        	$.getJSON("https://maps.googleapis.com/maps/api/geocode/json?address="+$("#city option:selected").text(),function(result) {
        	
	        	var bounds = new google.maps.LatLngBounds();
	    		/*point bounds to the place location*/
	    		var ptLatLon = new google.maps.LatLng(result.results[0].geometry.location.lat, result.results[0].geometry.location.lng);
	    		bounds.extend(ptLatLon);
	    		/*call fitbounts for the mapInstance with the place location bounds object*/
	    		mapInstance.fitBounds(bounds)

	    		var listener = google.maps.event.addListener(mapInstance, "idle", function() { 
	    			/*check for current zoom level*/
					if (mapInstance.getZoom() > 12) {
						mapInstance.setZoom(12);
					}
					google.maps.event.removeListener(listener);
				});
	        });
        }

        /*Get The Length Of Filter Array*/
        var filtersLength = Object.keys(appliedFilterObj_gmaps).length;

        /*If any filter is applied then filter the data*/
        if(filtersLength > 0) {

        	if($.trim(mapPageType) == "gmap") {
        		gmap_self.applyFilter_gmaps(appliedFilterObj_gmaps);
        	} else {
        		earth_instance.applyFilter_earth(appliedFilterObj_gmaps);
        	}
        }
        /*If no filter is applied the load all the devices*/
        else {

        	/*Reset markers & polyline*/
			gmap_self.clearGmapElements();

			/*Reset Global Variables & Filters*/
			gmap_self.resetVariables_gmap();

            gmap_self.plotDevices_gmap(main_devices_data_gmaps,"base_station");
        }
    };

	/**
	 * This function enable the polygon drawing tool & draw the polygon
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

				/*Remove drawing mode*/
				drawingManager.setDrawingMode(null);

				pathArray = e.overlay.getPath().getArray();
				polygon = new google.maps.Polygon({"path" : pathArray});
				bs_ss_array = masterMarkersObj;

				currentPolygon = e.overlay;
				currentPolygon.type = e.type;
				var allSS = [],
					allSSIds = [];


				$.grep(main_devices_data_gmaps, function(bs) {
					
					$.grep(bs.data.param.sector, function(sector) {

						$.grep(sector.sub_station, function(ss) {
							allSS.push(ss);							
						});
					});
				});

				for(var k=0;k<allSS.length;k++) {
						
					var point = new google.maps.LatLng(allSS[k].data.lat,allSS[k].data.lon);

					if (google.maps.geometry.poly.containsLocation(point, polygon)) {

						allSSIds.push(allSS[k].device_name);
						polygonSelectedDevices.push(allSS[k]);
					}
				}

				selectedCount = polygonSelectedDevices.length;

				if(selectedCount == 0) {
					
					bootbox.alert("No 'Sub-Station' under the selected area.Please re-select");
					/*Remove current polygon from map*/
					gmap_self.clearPolygon();

				} else if(selectedCount > 200) {
					
					bootbox.alert("Max. limit for selecting sub-stations is 200.Please re-select");
					/*Remove current polygon from map*/
					gmap_self.clearPolygon();

				} else {
					
					var devicesTemplate = "<div class='deviceWellContainer'>";
					for(var i=0;i<selectedCount;i++) {
						
						var new_device_name = "";

						if(polygonSelectedDevices[i].device_name.indexOf(".") != -1) {
							new_device_name = polygonSelectedDevices[i].device_name.split(".");
							new_device_name = new_device_name.join("-");
						} else {
							new_device_name = polygonSelectedDevices[i].device_name;
						}

						devicesTemplate += '<div class="well well-sm" id="div_'+new_device_name+'"><h5>'+(i+1)+'.) '+polygonSelectedDevices[i].name+'</h5>';
						devicesTemplate += '<div style="min-height:60px;margin:15px 0px;" id="livePolling_'+new_device_name+'"></div></div>';
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

					/*Make ajax call to get the services & datasources.*/
					$.ajax({
						url : window.location.origin+"/device/lp_services/"+" ?devices="+JSON.stringify(allSSIds),
						//url : window.location.origin+"/"+"static/services.json",
						type : "GET",
						dataType : "json",
						/*If data fetched successful*/
						success : function(result) {

							if(result.success == 1) {

								servicesData = {};
								servicesData = result.data;
								var devicesName = Object.keys(servicesData);
								var servicesOption = "";
								var replace_device_name = "";

								for(var i=0;i<devicesName.length;i++) {
									if(devicesName[i].indexOf(".") != -1) {

										replace_device_name = devicesName[i].split('.');
										replace_device_name = replace_device_name.join('-');
									} else {
										replace_device_name = devicesName[i];
									}

									var allServices = result.data[devicesName[i]].services;
									var deviceNameParam = '"'+replace_device_name+'"';
									servicesOption = "<ul class='list-unstyled'><li class='servicesContainer'><select class='form-control' onchange='gmap_self.serviceSeleted_gmap("+deviceNameParam+")' id='service_"+replace_device_name+"'><option value=''>Select Service</option>";
									/*Loop For Number of services*/
									for(var j=0;j<allServices.length;j++) {

										servicesOption += "<option value='"+allServices[j].value+"'>"+allServices[j].name+"</option>";
									}
									servicesOption += "</select></li><li class='divide-10'></li><li><select class='form-control' id='datasource_"+replace_device_name+"'><option value=''>Select Service Datasource</option></select></li><li class='divide-10'></li><li><button class='btn btn-primary' data-complete-text='Fetch' data-loading-text='Please Wait...' id='fetchBtn_"+replace_device_name+"' onClick='gmap_self.pollDevice_gmap("+deviceNameParam+")'>Fetch</button> <i class='fa fa-spinner fa fa-spin hide' id='fetch_spinner'>&nbsp;</i> </li></ul><div class='clearfix'><ul class='list-unstyled list-inline' id='pollVal_"+replace_device_name+"'></ul></div>";

									$("#livePolling_"+replace_device_name).append(servicesOption);
								}								

							} else {

								$.gritter.add({
						            // (string | mandatory) the heading of the notification
						            title: 'Live Polling - Error',
						            // (string | mandatory) the text inside the notification
						            text: result.message,
						            // (bool | optional) if you want it to fade out on its own or just sit there
						            sticky: true
						        });
							}
						},
						error : function(err) {

							$.gritter.add({
					            // (string | mandatory) the heading of the notification
					            title: 'Live Polling - Server Error',
					            // (string | mandatory) the text inside the notification
					            text: err.statusText,
					            // (bool | optional) if you want it to fade out on its own or just sit there
					            sticky: true
					        });
						}
					});					
					
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
	 * This function load the service datasource as per the selected service.
	 * @method serviceSeleted_gmap
	 * @param deviceName {String}, It contains the name of the device whose service is selected
	 */
	this.serviceSeleted_gmap = function(deviceName) {

		var serviceVal = $.trim($("#service_"+deviceName).val());
		var serviceName = $.trim($("#service_"+deviceName+" option:selected").text());
		var dataSourceOption = "<option value=''>Select Service Datasource</option>";

		/*If any service is selected*/
		if(serviceVal != "") {

			var updated_device_name = "";

			var count = deviceName.match(/-/g); 

			if(deviceName.indexOf("-") != -1 && count.length == 3) {
				
				updated_device_name = deviceName.split("-");
				updated_device_name = updated_device_name.join(".");
			} else {
				updated_device_name = deviceName;
			}
			
			// if(deviceName.indexOf("-"))

			var activeServices = servicesData[updated_device_name].services;

			for(var i=0;i<activeServices.length;i++) {

				if($.trim(activeServices[i].name) == serviceName && $.trim(activeServices[i].value) == serviceVal) {

					var serviceDataSource = activeServices[i].datasource;

					for(var j=0;j<serviceDataSource.length;j++) {

						dataSourceOption += "<option value='"+serviceDataSource[j].value+"'>"+serviceDataSource[j].name+"</option>";
					}
				}
			}			
		}

		/*Append the datasource to select box as per the selected service*/
		$("#datasource_"+deviceName).html(dataSourceOption);
	};

	/**
	 * This function fetch the live polling value for particular device.
	 * @method pollDevice_gmap
	 * @param deviceName {String}, It contains the name of the device for which the polling value is to be fetched.
	 */
	this.pollDevice_gmap = function(deviceName) {

		$("#fetchBtn_"+deviceName).button("loading");

		var selectedServiceTxt = $.trim($("#service_"+deviceName+" option:selected").text());
		var selectedServiceVal = $.trim($("#service_"+deviceName).val());
		
		var selectedDatasourceTxt = $.trim($("#datasource_"+deviceName+" option:selected").text());
		var selectedDatasourceVal = $.trim($("#datasource_"+deviceName).val());

		var actual_device_name = "",
			count = deviceName.match(/-/g);
		if(deviceName.indexOf("-") != -1 && count.length == 3) {
				
			actual_device_name = deviceName.split("-");
			actual_device_name = actual_device_name.join(".");
		} else {
			actual_device_name = deviceName;
		}

		if(selectedServiceVal != "" && selectedDatasourceVal != "") {

			if($("#fetch_spinner").hasClass("hide")) {
				$("#fetch_spinner").removeClass("hide");
			}


			/*Make ajax call to get the live polling data.*/
			$.ajax({
				url : window.location.origin+"/device/lp_service_data/"+"?device=['"+actual_device_name+"']&service=['"+selectedServiceTxt+"']&datasource=['"+selectedDatasourceTxt+"']",
				// url : window.location.origin+"/"+"static/livePolling.json",
				type : "GET",
				dataType : "json",
				/*If data fetched successful*/
				success : function(result) {

					$("#fetchBtn_"+deviceName).button("complete");

					if(!($("#fetch_spinner").hasClass("hide"))) {
						$("#fetch_spinner").addClass("hide");
					}

					if(result.success == 1) {

						/*Check that polling value exist or not*/
						if(result.data.value.length > 0) {

							$("#pollVal_"+deviceName+" ").append("<li>"+result.data.value[0]+"</li>");
						}

						/*Check that markerurl exist or not*/
						if(result.data.icon.length > 0) {

							var isPlotted = 0;
							var newIcon = window.location.origin+"/"+result.data.icon[0];

							$.grep(masterMarkersObj,function(markers) {

								var plottedMarkerName = $.trim(markers.device_name);

								if(plottedMarkerName == actual_device_name) {

									isPlotted = 1;
									markers.icon = newIcon;
									markers.oldIcon = newIcon;
									markers.setOptions({icon : newIcon, oldIcon : newIcon});
								}
							});

							if(isPlotted == 0) {

								$.grep(plottedSS,function(markers) {

									var plottedSSName = $.trim(markers.name);

									if(plottedSSName == actual_device_name) {

										markers.icon = newIcon;
										markers.oldIcon = newIcon;
										markers.setOptions({icon : newIcon, oldIcon : newIcon});
									}
								});							
								// end if statement
							}

							$.grep(main_devices_data_gmaps,function(devices) {
								var sectors = devices.data.param.sector;

								$.grep(sectors, function(sector) {

									var sub_station = sector.sub_station;
									
									$.grep(sub_station,function(ss) {

										if($.trim(ss.name) == $.trim(deviceName)) {

											ss.data.markerUrl = result.data.icon[0];
										}
									});
								});
							});
						}

					} else {

						$.gritter.add({
				            // (string | mandatory) the heading of the notification
				            title: 'Live Polling - Error',
				            // (string | mandatory) the text inside the notification
				            text: result.message,
				            // (bool | optional) if you want it to fade out on its own or just sit there
				            sticky: true
				        });
					}
				},
				error : function(err) {

					$("#fetchBtn_"+deviceName).button("complete");

					if(!($("#fetch_spinner").hasClass("hide"))) {
						$("#fetch_spinner").addClass("hide");
					}

					$.gritter.add({
			            // (string | mandatory) the heading of the notification
			            title: 'Live Polling - Server Error',
			            // (string | mandatory) the text inside the notification
			            text: err.statusText,
			            // (bool | optional) if you want it to fade out on its own or just sit there
			            sticky: true
			        });
				}
			});
 		// End if Statement
		} else {

			$.gritter.add({
	            // (string | mandatory) the heading of the notification
	            title: 'Live Polling - Error',
	            // (string | mandatory) the text inside the notification
	            text: "Service & Service Datasource selection is mandatory.",
	            // (bool | optional) if you want it to fade out on its own or just sit there
	            sticky: true
	        });
		} // End else Statement
	};


	/**
	 * This function clear the polygon selection from the map
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

		$("#showAllSS").prop('checked', false);
	};

	/**
	 * This function creates the line chart for the monitoring of selected devices
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
				gmap_self.makeMonitoringChart(id);
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

        gmap_self.makeMonitoringChart(id);
	};

	this.pauseMonitoring = function(id) {
		
		$("#pause_"+id).addClass("active");
        if($("#play_"+id).hasClass("active")) {
            $("#play_"+id).removeClass("active");
        }
        if($("#stop_"+id).hasClass("active")) {
            $("#stop_"+id).removeClass("active");
        }
        gmap_self.makeMonitoringChart(id);
	};

	this.stopMonitoring = function(id) {
		
		$("#stop_"+id).addClass("active");
        if($("#play_"+id).hasClass("active")) {
            $("#play_"+id).removeClass("active");
        }
        if($("#pause_"+id).hasClass("active")) {
            $("#pause_"+id).removeClass("active");
        }
        gmap_self.makeMonitoringChart(id);
	};
	
    /**
     * This function resets the global variables & again call the api calling function after given timeout i.e. 5 minutes
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
			gmap_self.clearGmapElements();

			/*Reset Global Variables & Filters*/
			gmap_self.resetVariables_gmap();
			
			/*Recall the API*/
			gmap_self.getDevicesData_gmap();

		},300000);
    };

    /**
	 * This function removes all the elements from the map
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

		/*Clear the existing SS for same point*/
		for(var i=0;i<plottedSS.length;i++) {
			plottedSS[i].setMap(null);
		}

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

		/*Clear PTP SS*/
		for(var j=0;j<ssLinkArray.length;j++) {

			ssLinkArray[j].setMap(null);
		}
	};

	/**
	 * This function reset all global variable used in the process
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
		plottedSS = [];
		ssLinkArray = [];
	};
}