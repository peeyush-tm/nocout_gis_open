/*Global Variables*/
var mapInstance = "",
	gmap_self = "",
	currentDomElement = "",
	main_devices_data_gmaps = [],
	oms = "",
    oms_ss = "",
    oms_sect = ""
	pathConnector = "",
	infowindow = "",	
	devicesObject = {},
	plottedSS = [],
	metaData = {},
	isCallCompleted = 0,
	bsLatArray = [],
	bsLonArray = [],
	ssLatArray = [],
	ssLonArray = [],
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
	allSSIds = [],
	pathArray = [],
	polygon = "",
	pointsArray = [],
	currentPolygon = {},
	drawingManager = "",
	dataArray = [],
	leftMargin = 0,
	calling_count = 0,
	sectorArray = [],
	circleArray = [],
	servicesData = {},
	/*Variables used in fresnel zone calculation*/
	isDialogOpen = true,
	bts1_name = "",
	bts2_name = "",
	fresnelLat1 = "",
	fresnelLon1 = "",
	fresnelLat2 = "",
	fresnelLon2 = "",
	arrayCounter = 0,
	latLongArray = [],
	latLongArrayCopy = [],
	depthStep = 6,
	freq_mhz = 900, //MHZ
	total_bs = [],
	HEIGHT_CHANGED = false,
	clear_factor = 100,
	/*Default antina heights*/
	antenaHight1 = Math.floor(Math.random() * (70 - 40 + 1)) + 40,
	antenaHight2 = Math.floor(Math.random() * (70 - 40 + 1)) + 40,
	/*Colors for fresnel zone graph*/
	pinPointsColor = 'rgb(170,102,102)',
	altitudeColor = '#EDC240',
	losColor = 'rgb(203,75,75)',
	fresnel1Color = 'rgba(82, 172, 82, 0.99)',
	fresnel2Color = 'rgb(148,64,237)',
	/*Google Map Tools Variables*/
	ruler_array = [],
	tools_line_array = [],
	isCreated = 0,
	ruler_pt_count = 0,
	distance_label = {},
	isFreeze = 0;
    map_points_array = [];
    map_point_count = 0, zoomAfterRightClickComes= 10, fresnelData= {}, markersMasterObj= {'BS': {}, 'Lines': {}, 'SS': {}, 'BSNamae': {}, 'SSNamae': {}};

var sector_MarkersArray= [], zoomAtWhichSectorMarkerAppears= 9, sectorMarkersMasterObj= {}, isSectorMarkerLoaded=0, tempFilterSectordata= [];
var defaultIconSize= 'medium';

function addSubSectorMarkersToOms(arr) {
	if(arr) {
		for(var i=0; i< arr.length; i++) {
			var sectorMarkersAtThePoint= sectorMarkersMasterObj[arr[i].name];
			if(sectorMarkersAtThePoint && sectorMarkersAtThePoint.length) {
				for(var j=0; j< sectorMarkersAtThePoint.length; j++) {
					sectorMarkersAtThePoint[i].setMap(mapInstance);
					// oms.addMarker(sectorMarkersAtThePoint[j]);
				}	
			}
		}
		return ;
	}
	for(var i=0; i< sector_MarkersArray.length; i++) {
		sector_MarkersArray[i].setMap(mapInstance);
		// oms.addMarker(sector_MarkersArray[i]);
	}
}

var place_markers = [];

function displayCoordinates(pnt) {
      var coordsLabel = $("#cursor_lat_long");
      var lat = pnt.lat();
      lat = lat.toFixed(4);
      var lng = pnt.lng();
      lng = lng.toFixed(4);
      coordsLabel.html("Latitude: " + lat + "  Longitude: " + lng);
}

var markerContextInfoWindow;
function openBSRightClickMenu(event, marker) {
	if(mapInstance.getZoom() > zoomAfterRightClickComes) {
		
		var latlng= marker.getPosition();
		var contentString= '<div class="box border" style="width:90%;float:left;"><div class="box-title">Base Station Maintenance Settings</div><div class="box-body"><form action="#" class="form-horizontal "><div class="form-group"><label class="col-md-4 control-label">Maintainance:</label><div class="col-md-8"><input type="checkbox" name="maintenance-checkbox"></div></div></form></div></div>';

		if(markerContextInfoWindow) {
			markerContextInfoWindow.close();
		}
		markerContextInfoWindow= new InfoBox({
			content: contentString,
			boxStyle: {
				background: "white",
				color: "black",
				width: '300px'
			},
			disableAutoPan: true,
			pixelOffset: new google.maps.Size(-25, 0),
			position: latlng,
			closeBoxURL: "",
			isHidden: false,
			enableEventPropagation: false,
			zIndex_: 10000,
			closeBoxURL: "http://www.google.com/intl/en_us/mapfiles/close.gif"
		});

		markerContextInfoWindow.open(mapInstance);
		setTimeout(function() {
			$("[name='maintenance-checkbox']").bootstrapSwitch({
				size: 'small',
				offColor: 'danger'
			});
			var image = '/static/img/icons/caution.png';

			var maintenanceMarker= new google.maps.Marker({position: marker.getPosition(), icon: image, oldIcon: image});
			oms.addMarker(maintenanceMarker);
			$('input[name="maintenance-checkbox"]').on('switchChange.bootstrapSwitch', function(event, state) {
				if(state) {
					maintenanceMarker.setMap(mapInstance);
				} else {
					maintenanceMarker.setMap(null);
				}
			});
		},100);
	}
}

function prepare_oms_object(oms_instance) {
	oms_instance.addListener('click', function(marker,e) {
		var windowPosition = new google.maps.LatLng(marker.ptLat,marker.ptLon);
		/*Call the function to create info window content*/
		var content = gmap_self.makeWindowContent(marker);
		/*Set the content for infowindow*/
		infowindow.setContent(content);
		/*Set The Position for InfoWindow*/
		infowindow.setPosition(windowPosition);
		/*Open the info window*/
		infowindow.open(mapInstance);

		/*Show only 5 rows, hide others*/
		gmap_self.show_hide_info();
	});

	/*Event when the markers cluster expands or spiderify*/
	oms_instance.addListener('spiderfy', function(e,markers) {
		/*Change the markers icon from cluster icon to thrie own icon*/
		for(var i=0;i<e.length;i++) {
			/*Change the icon of marker*/
			e[i].setOptions({"icon":e[i].oldIcon});
			for(var j=0;j<ssLinkArray.length;j++) {
				var pt_type = $.trim(e[i].pointType);

				if(pt_type == "sub_station") {
					if($.trim(ssLinkArray[j].ssName) == $.trim(e[i].name)) {
						var pathArray = [];
						pathArray.push(new google.maps.LatLng(e[i].position.k,e[i].position.B));
						pathArray.push(new google.maps.LatLng(ssLinkArray[j].bs_lat,ssLinkArray[j].bs_lon));
						ssLinkArray[j].setPath(pathArray);
					}
				} else if(pt_type == "base_station") {
					if($.trim(ssLinkArray[j].bsName) == $.trim(e[i].name)) {
						var pathArray = [];
						pathArray.push(new google.maps.LatLng(e[i].position.k,e[i].position.B));
						pathArray.push(new google.maps.LatLng(ssLinkArray[j].ss_lat,ssLinkArray[j].ss_lon));
						ssLinkArray[j].setPath(pathArray);
					}
				}
			}
		}
        //freeze the map when spiderified
        isFreeze = 1;
        infowindow.close();
    });

    /*Event when markers cluster is collapsed or unspiderify*/
    oms_instance.addListener('unspiderfy', function(e,markers) {
        //un freeze the map when in normal state
        isFreeze = 0;
        var latArray = [],
            lonArray = [];
            
        $.grep(e, function (elem) {
            latArray.push(elem.ptLat);
            lonArray.push(elem.ptLon);
        });

        /*Reset the marker icon to cluster icon*/
        for(var i=0; i< e.length; i++) {
        	var latCount= $.grep(latArray, function(elem) {return elem=== e[i].ptLat;}).length;
        	var lonCount = $.grep(lonArray, function (elem) {return elem === e[i].ptLon;}).length;
        	if(lonCount> 1 && latCount> 1) {
        		//change all to cluster icon
        		e[i].setOptions({"icon": e[i].clusterIcon});
        	}
        }
//         for(var i=0;i<e.length;i++) {
// <<<<<<< HEAD
//         	var latCount = $.grep(latArray, function (elem) {return elem === e[i].ptLat;}).length;
//         	var lonCount = $.grep(lonArray, function (elem) {return elem === e[i].ptLon;}).length;
//         	if(lonCount > 1 && latCount > 1) {
//         		if(e[i].pointType=== "sector_Marker") {
//         			e[i].setOptions({"icon":new google.maps.MarkerImage('http://upload.wikimedia.org/wikipedia/commons/c/ca/1x1.png',null,null,null)});
//         		} 
//         		else if(e[i].pointType=== "base_station"){
//         			e[i].setOptions({"icon": e[i].oldIcon});
//         		}else {
// =======

//             var latCount = $.grep(latArray, function (elem) {return elem === e[i].ptLat;}).length;
//             var lonCount = $.grep(lonArray, function (elem) {return elem === e[i].ptLon;}).length;

//             if(lonCount > 1 && latCount > 1) {
//                 if(e[i].pointType === "sector_Marker") {
//                     e[i].setOptions({"icon":new google.maps.MarkerImage(
//                                     'http://upload.wikimedia.org/wikipedia/commons/c/ca/1x1.png',
//                                     null,
//                                     null,
//                                     null
//                                    )});
//                 } else if(e[i].pointType === "base_station") {
//                     e[i].setOptions({"icon":clusterIcon});
//                 } else {
// >>>>>>> 600754fd233290a1846083d672cbdda943be05bf
//                 	e[i].setOptions({"icon":''});
//                 }
//             }

            for(var j=0;j<ssLinkArray.length;j++) {
                var pt_type = $.trim(e[i].pointType);

                if(pt_type == "sub_station") {
                    if($.trim(ssLinkArray[j].ssName) == $.trim(e[i].name)) {
                        var pathArray = [];
                        pathArray.push(new google.maps.LatLng(e[i].ptLat,e[i].ptLon));
                        pathArray.push(new google.maps.LatLng(ssLinkArray[j].bs_lat,ssLinkArray[j].bs_lon));
                        ssLinkArray[j].setPath(pathArray);
                    }
                } else if(pt_type == "base_station") {
                    if($.trim(ssLinkArray[j].bsName) == $.trim(e[i].name)) {
                        var pathArray = [];
                        pathArray.push(new google.maps.LatLng(e[i].ptLat,e[i].ptLon));
                        pathArray.push(new google.maps.LatLng(ssLinkArray[j].ss_lat,ssLinkArray[j].ss_lon));
                        ssLinkArray[j].setPath(pathArray);
                    }
                }
            }
        }
    });
}

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

		/*If no internet access*/
		if(typeof google != "undefined") {
			/*Save the dom element in the global variable*/
			currentDomElement = domElement;
			var mapObject = {};
			if(window.location.pathname.indexOf("google_earth") > -1) {
				mapObject = {
					center    : new google.maps.LatLng(21.1500,79.0900),
					zoom      : 5,
					mapTypeId : google.maps.MapTypeId.SATELLITE,
					mapTypeControl : false
				};
			} else {
				mapObject = {
					center    : new google.maps.LatLng(21.1500,79.0900),
					zoom      : 5,
					mapTypeId : google.maps.MapTypeId.ROADMAP,
					mapTypeControl : true,
					mapTypeControlOptions: {
						style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
					}
				};
			}

			/*Create Map Type Object*/
			mapInstance = new google.maps.Map(document.getElementById(domElement),mapObject);		
			/*Search text box object*/
			var searchTxt = document.getElementById('searchTxt');

			/*google search object for search text box*/
			var searchBox = new google.maps.places.SearchBox(searchTxt);

            /*show co ordinates on mouse move*/
            google.maps.event.addListener(mapInstance, 'mousemove', function (event) {
                displayCoordinates(event.latLng);
            });

            //On Zoom_Change, IF zoomLevel is greater than zoomAtWhichSectorMarkerAppears, show Sector Markers, else Hide them.
            google.maps.event.addListener(mapInstance, 'zoom_changed', function() {
            	var zoom = mapInstance.getZoom();
            	if( zoom > zoomAtWhichSectorMarkerAppears) {
            		if(!isSectorMarkerLoaded) {
		        		for(var i=0; i< sector_MarkersArray.length; i++) {
		        			sector_MarkersArray[i].setMap(mapInstance);
		        		}
            		}
            		isSectorMarkerLoaded=1;
            	} else {
            		if(isSectorMarkerLoaded) {
            			for (var i = 0; i < sector_MarkersArray.length; i++) {
            				sector_MarkersArray[i].setMap(null);
            			}
            		}
            		isSectorMarkerLoaded= 0;
            	}
            });

			/*Event listener for search text box*/
			google.maps.event.addListener(new google.maps.places.SearchBox(searchTxt), 'places_changed', function() {

                for (var i = 0, marker; marker = place_markers[i]; i++) {
                    marker.setMap(null);
                }

				/*place object returned from map API*/
	    		var places = searchBox.getPlaces();

                if (places.length == 0) {
                    return;
                }


                // For each place, get the icon, place name, and location.
                place_markers = [];
                var bounds = new google.maps.LatLngBounds();
                for (var i = 0, place; place = places[i]; i++) {
                  var image = {
                    url: place.icon,
                    size: new google.maps.Size(71, 71),
                    origin: new google.maps.Point(0, 0),
                    anchor: new google.maps.Point(17, 34),
                    scaledSize: new google.maps.Size(25, 25)
                  };

                  // Create a marker for each place.
                  var marker = new google.maps.Marker({
                    map: mapInstance,
                    icon: image,
                    title: place.name,
                    position: place.geometry.location
                  });

                  place_markers.push(marker);

                  bounds.extend(place.geometry.location);
                }

                mapInstance.fitBounds(bounds);

	    		/*Listener to reset zoom level if it exceeds to particular value*/
                var listener = google.maps.event.addListener(mapInstance, "idle", function() {
                    /*check for current zoom level*/
                    if (mapInstance.getZoom() >= 15) {
                        mapInstance.setZoom(15);
                    }
                    google.maps.event.removeListener(listener);
                });
			});

			/*Add Full Screen Control*/
			mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].push(new FullScreenControl(mapInstance));

			/*Create a instance of OverlappingMarkerSpiderfier*/
			oms = new OverlappingMarkerSpiderfier(mapInstance,{markersWontMove: true, markersWontHide: true, keepSpiderfied: true});
            oms_ss = new OverlappingMarkerSpiderfier(mapInstance,{markersWontMove: true, markersWontHide: true, keepSpiderfied: true});

            prepare_oms_object(oms);
            prepare_oms_object(oms_ss);

			/*Create a instance of google map info window*/
			infowindow = new google.maps.InfoWindow();
		} else {
			$.gritter.add({
	            // (string | mandatory) the heading of the notification
	            title: 'Google Maps',
	            // (string | mandatory) the text inside the notification
	            text: 'No Internet Access',
	            // (bool | optional) if you want it to fade out on its own or just sit there
	            sticky: false
	        });
		}
	};

	/**
	 * This function plots the BS & SS network on the created google map
	 * @method getDevicesData_gmap
	 */
	this.getDevicesData_gmap = function() {

		var get_param_filter = "";
		/*If any advance filters are applied then pass the advance filer with API call else pass blank array*/
		if(appliedAdvFilter.length > 0) {
			get_param_filter = JSON.stringify(appliedAdvFilter);
		} else {
			get_param_filter = "";
		}

		//display advance search, filter etc button when call is going on.
		disableAdvanceButton();

		if(counter > 0 || counter == -999) {

			/*Ajax call not completed yet*/
			isCallCompleted = 0;

			/*Show The loading Icon*/
			$("#loadingIcon").show();

			/*Disable the refresh button*/
			$("#resetFilters").button("loading");

			/*To Enable The Cross Domain Request*/
			$.support.cors = true;

			/*Ajax call to the API*/
			$.ajax({
				crossDomain: true,
				url : window.location.origin+"/"+"device/stats/?filters="+get_param_filter+"&page_number="+hitCounter,
				// url : window.location.origin+"/"+"static/new_format.json",
				type : "GET",
				dataType : "json",
				/*If data fetched successful*/
				success : function(result) {

					if(result.success == 1) {

						if(result.data.objects != null) {

							hitCounter = hitCounter + 1;							
							/*First call case*/
							if(devicesObject.data == undefined) {

								/*Save the result json to the global variable for global access*/
								devicesObject = result;
								/*This will update if any filer is applied*/
								devices_gmaps = devicesObject.data.objects.children;

							} else {

								devices_gmaps = devices_gmaps.concat(result.data.objects.children);
							}

							main_devices_data_gmaps = devices_gmaps;

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

								if(result.data.objects.data.unspiderfy_icon != "" && result.data.objects.data.unspiderfy_icon != undefined) {
									clusterIcon = window.location.origin+"/static/img/icons/bs.png";
								} else {
									clusterIcon = window.location.origin+"/static/img/icons/bs.png";
								}

								/*Check that any advance filter is applied or not*/
								if(appliedAdvFilter.length <= 0) {

									/*applied basic filters count*/
									var appliedFilterLength_gmaps = Object.keys(appliedFilterObj_gmaps).length;

									/*Check that any basic filter is applied or not*/
									if(appliedFilterLength_gmaps > 0) {
										/*If any filter is applied then plot the fetch data as per the filters*/
										gmap_self.applyFilter_gmaps(appliedFilterObj_gmaps);
									} else {
									
										/*Call the plotDevices_gmap to show the markers on the map*/
										gmap_self.plotDevices_gmap(result.data.objects.children,"base_station");
										
									}

								} else {
                                    /*Call the plotDevices_gmap to show the markers on the map*/
									gmap_self.plotDevices_gmap(result.data.objects.children,"base_station");
                                }

                                /*Decrement the counter*/
								counter = counter - 1;

								/*Call the function after 3 sec. for lazyloading*/
								setTimeout(function() {
									gmap_self.getDevicesData_gmap();
								},10);
								
							} else {
								isCallCompleted = 1;
								gmap_self.plotDevices_gmap([],"base_station");

								disableAdvanceButton('no');

								/*Recall the server after particular timeout if system is not freezed*/
						        /*Hide The loading Icon*/
								$("#loadingIcon").hide();

								/*Enable the refresh button*/
								$("#resetFilters").button("complete");

								setTimeout(function(e){
									gmap_self.recallServer_gmap();
								},21600000);
							}							

						} else {
							
							isCallCompleted = 1;
							gmap_self.plotDevices_gmap([],"base_station");

							/*Hide The loading Icon*/
							$("#loadingIcon").hide();

							/*Enable the refresh button*/
							$("#resetFilters").button("complete");

							setTimeout(function(e){
								gmap_self.recallServer_gmap();
							},21600000);
						}

					} else {

						isCallCompleted = 1;
						gmap_self.plotDevices_gmap([],"base_station");

						disableAdvanceButton('no, enable it.');

						/*Recall the server after particular timeout if system is not freezed*/
						setTimeout(function(e) {
							gmap_self.recallServer_gmap();
						},21600000);

					}

				},
				/*If data not fetched*/
				error : function(err) {					

					$.gritter.add({
			            // (string | mandatory) the heading of the notification
			            title: 'GIS - Server Error',
			            // (string | mandatory) the text inside the notification
			            text: err.statusText,
			            // (bool | optional) if you want it to fade out on its own or just sit there
			            sticky: false
			        });
					/*Recall the server after particular timeout if system is not freezed*/
					/*Hide The loading Icon*/
					$("#loadingIcon").hide();

					/*Enable the refresh button*/
					$("#resetFilters").button("complete");

					setTimeout(function(e){
						gmap_self.recallServer_gmap();
					},21600000);
				}
			});
		} else {

			/*Ajax call not completed yet*/
			isCallCompleted = 1;
			gmap_self.plotDevices_gmap([],"base_station");

			disableAdvanceButton('no, enable it.');
			
			/*Recall the server after particular timeout if system is not freezed*/
			setTimeout(function(e){
				gmap_self.recallServer_gmap();
			},21600000);
		}
	};

	/**
     * This function is used to plot BS or SS devices & their respective elements on the google maps
     * @method plotDevices_gmap
     * @param bs_ss_devices {Object} In case of BS, it is the devies object array & for SS it contains BS marker object with SS & sector info
     * @param stationType {String}, It contains that the points are for BS or SS.
	 */
	this.plotDevices_gmap = function(bs_ss_devices,stationType) {

		for(var i=0;i<bs_ss_devices.length;i++) {

			/*Create BS Marker Object*/
			var bs_marker_object = {
				position  	     : new google.maps.LatLng(bs_ss_devices[i].data.lat,bs_ss_devices[i].data.lon),
				ptLat 		     : bs_ss_devices[i].data.lat,
				ptLon 		     : bs_ss_devices[i].data.lon,
				map       	     : mapInstance,
				icon 	  	     : '/static/img/icons/bs.png',
				oldIcon 	     : '/static/img/icons/bs.png',
				pointType	     : stationType,
				child_ss   	     : bs_ss_devices[i].data.param.sector,
				original_sectors : bs_ss_devices[i].data.param.sector,
				dataset 	     : bs_ss_devices[i].data.param.base_station,
				device_name 	 : bs_ss_devices[i].data.device_name,
				bsInfo 			 : bs_ss_devices[i].data.param.base_station,
				bhInfo 			 : bs_ss_devices[i].data.param.backhual,
				bs_name 		 : bs_ss_devices[i].name,
				name 		 	 : bs_ss_devices[i].name,
				antenna_height    : bs_ss_devices[i].data.antenna_height,
				zIndex 			 : 200,
				optimized 		 : false,
				markerType: 'BS'
			};

			/*Create BS Marker*/
			var bs_marker = new google.maps.Marker(bs_marker_object);

			//Add markers to markersMasterObj with LatLong at key so it can be fetched later.
			markersMasterObj['BS'][String(bs_ss_devices[i].data.lat)+bs_ss_devices[i].data.lon]= bs_marker;
			markersMasterObj['BSNamae'][String(bs_ss_devices[i].name)]= bs_marker;

			/*
			Add Context menu event to the marker
			*/
			(function bindRightMenuToMarker(marker) {
				var markerRightClick= google.maps.event.addListener(marker, 'rightclick', function(event) {
					openBSRightClickMenu(event, marker);
				});

				return markerRightClick;
			})(bs_marker);

			/*Sectors Array*/
			var sector_array = bs_ss_devices[i].data.param.sector;
			var deviceIDArray= [];
			/*Plot Sector*/
			for(var j=0;j<sector_array.length;j++) {

				var lat = bs_ss_devices[i].data.lat,
					lon = bs_ss_devices[i].data.lon,
					azimuth = sector_array[j].azimuth_angle,
					beam_width = sector_array[j].beam_width,
					sector_color = sector_array[j].color,
					sectorInfo = sector_array[j].info,
					orientation = $.trim(sector_array[j].orientation),
					sector_child = sector_array[j].sub_station,
					rad = 4,
					sectorRadius = (+sector_array[j].radius),
					startLon = "",
					startLat = "";

				/*If radius is greater than 4 Kms then set it to 4.*/
				if((sectorRadius <= 4) && (sectorRadius != null) && (sectorRadius > 0)) {
					rad = sectorRadius;
				}

				var startEndObj = {};

				/*Call createSectorData function to get the points array to plot the sector on google maps.*/
				gmap_self.createSectorData(lat,lon,rad,azimuth,beam_width,orientation,function(pointsArray) {

					var halfPt = Math.floor(pointsArray.length / (+2));

					if($.trim(sector_array[j].technology) != "PTP" && $.trim(sector_array[j].technology) != "P2P") {
						/*Plot sector on map with the retrived points*/
						gmap_self.plotSector_gmap(lat,lon,pointsArray,sectorInfo,sector_color,sector_child);
						startEndObj["startLat"] = pointsArray[halfPt].lat;
						startEndObj["startLon"] = pointsArray[halfPt].lon;
					} else {
						startEndObj["startLat"] = bs_ss_devices[i].data.lat;
		    			startEndObj["startLon"] = bs_ss_devices[i].data.lon;
					}
				});

				if(deviceIDArray.indexOf(sector_array[j]['device_info'][1]['value']) === -1) {

					var sectors_Markers_Obj= {
						position: new google.maps.LatLng(lat, lon),
						ptLat: bs_ss_devices[i].data.lat,
						ptLon: bs_ss_devices[i].data.lon,
						icon: 'http://upload.wikimedia.org/wikipedia/commons/c/ca/1x1.png',
						oldIcon: window.location.origin+"/"+sector_array[j].markerUrl,
						pointType: 'sector_Marker',
						technology: sector_array[j].technology,
						vendor: sector_array[j].vendor,
						deviceExtraInfo: sector_array[j].info,
						deviceInfo: sector_array[j].device_info,
						zIndex: 200,
						optimized: false,
				    	title: "Sector Marker",
                        antenna_height: sector_array[j].antenna_height
                    }

                    var sect_height = sector_array[j].antenna_height;

/*Create Sector Marker*/
					var sector_Marker = new google.maps.Marker(sectors_Markers_Obj);

					sector_MarkersArray.push(sector_Marker);

					if(sectorMarkersMasterObj[bs_ss_devices[i].name]) {
						sectorMarkersMasterObj[bs_ss_devices[i].name].push(sector_Marker)
					} else {
						sectorMarkersMasterObj[bs_ss_devices[i].name]= [];
						sectorMarkersMasterObj[bs_ss_devices[i].name].push(sector_Marker)
					}

					oms.addMarker(sector_Marker);
/*End of Create Sector Marker*/

					deviceIDArray.push(sector_array[j]['device_info'][1]['value']);
				}

				/*Plot Sub-Station*/
				for(var k=0;k<sector_child.length;k++) {

					var ss_marker_obj = sector_child[k];

					/*Create SS Marker Object*/
					var ss_marker_object = {
						position: new google.maps.LatLng(ss_marker_obj.data.lat,ss_marker_obj.data.lon),
				    	ptLat: ss_marker_obj.data.lat,
				    	ptLon: ss_marker_obj.data.lon,
				    	technology: ss_marker_obj.data.technology,
				    	map: mapInstance,
				    	icon: new google.maps.MarkerImage(window.location.origin+"/"+ss_marker_obj.data.markerUrl,null,null,null,new google.maps.Size(32,37)),
				    	oldIcon: new google.maps.MarkerImage(window.location.origin+"/"+ss_marker_obj.data.markerUrl,null,null,null,new google.maps.Size(32,37)),
				    	pointType	     : "sub_station",
				    	dataset 	     : ss_marker_obj.data.param.sub_station,
				    	bhInfo 			 : [],
				    	antenna_height    : ss_marker_obj.data.antenna_height,
				    	name 		 	 : ss_marker_obj.name,
				    	device_name 	 : ss_marker_obj.device_name,
				    	zIndex 			 : 200,
				    	optimized 		 : false
				    };

				    /*Create SS Marker*/
				    var ss_marker = new google.maps.Marker(ss_marker_object);

				    markersMasterObj['SS'][String(ss_marker_obj.data.lat)+ ss_marker_obj.data.lon]= ss_marker;
				    markersMasterObj['SSNamae'][String(ss_marker_obj.device_name)]= ss_marker;

				    total_bs.push(ss_marker);

				    /*Add the master marker to the global master markers array*/
			    	masterMarkersObj.push(ss_marker);

			    	/*Add parent markers to the OverlappingMarkerSpiderfier*/
				    oms_ss.addMarker(ss_marker);

				    /*Push All SS Lat & Lon*/
		    	    ssLatArray.push(ss_marker_obj.data.lat);
					ssLonArray.push(ss_marker_obj.data.lon);

					var ss_info = {}, base_info = {};

				    startEndObj["endLat"] = ss_marker_obj.data.lat;
		    		startEndObj["endLon"] = ss_marker_obj.data.lon;

		    		/*Sub station info Object*/
		    		ss_info["info"] = ss_marker_obj.data.param.sub_station;
		    		ss_info["antenna_height"] = ss_marker_obj.data.antenna_height;

		    		
		    		/*Link color object*/
		    		linkColor = ss_marker_obj.data.link_color;
		    			
	    			base_info["info"] = bs_ss_devices[i].data.param.base_station;
	    			base_info["antenna_height"] = bs_ss_devices[i].data.antenna_height;
	    			
	    			if(ss_marker_obj.data.show_link == 1) {
	    				/*Create the link between BS & SS or Sector & SS*/
				    	var ss_link_line = gmap_self.createLink_gmaps(startEndObj,linkColor,base_info,ss_info,sect_height,sector_array[j].sector_configured_on,ss_marker_obj.name,bs_ss_devices[i].name);

				    	ssLinkArray.push(ss_link_line);
	    			}

				}
    		}



    		/*Add the master marker to the global master markers array*/
	    	masterMarkersObj.push(bs_marker);

	    	/*Add parent markers to the OverlappingMarkerSpiderfier*/
		    oms.addMarker(bs_marker);

		    /*Push All BS Lat & Lon*/
			bsLatArray.push(bs_ss_devices[i].data.lat);
			bsLonArray.push(bs_ss_devices[i].data.lon);			
		}

		if(isCallCompleted == 1) {

			/*Hide The loading Icon*/
			$("#loadingIcon").hide();

			/*Enable the refresh button*/
			$("#resetFilters").button("complete");


			var oms_bs_markers = oms.getMarkers(), oms_ss_markers = oms_ss.getMarkers();			

			/*Loop to change the icon for same location BS markers(to cluster icon)*/
			for(var k=0;k<oms_bs_markers.length;k++) {
				
				if(oms_bs_markers[k] != undefined) {
	
					/*if two BS or SS on same position*/
					var bsLatOccurence = $.grep(bsLatArray, function (elem) {return elem === oms_bs_markers[k].ptLat;}).length;
					var bsLonOccurence = $.grep(bsLonArray, function (elem) {return elem === oms_bs_markers[k].ptLon;}).length;

					if(bsLatOccurence > 1 && bsLonOccurence > 1) {
						oms_bs_markers[k].setOptions({"icon" : clusterIcon});
					}
				}
			}

			/*Loop to change the icon for same location SS markers(to cluster icon)*/
			for(var k=0;k<oms_ss_markers.length;k++) {
				
				if(oms_ss_markers[k] != undefined) {
	
					/*if two BS or SS on same position*/
					var bsLatOccurence = $.grep(ssLatArray, function (elem) {return elem === oms_ss_markers[k].ptLat;}).length;
					var bsLonOccurence = $.grep(ssLonArray, function (elem) {return elem === oms_ss_markers[k].ptLon;}).length;

					if(bsLatOccurence > 1 && bsLonOccurence > 1) {
						oms_ss_markers[k].setOptions({"icon" : ''});
					}
				}
			}

			gmap_self.updateAllMarkersWithNewIcon(defaultIconSize);

			/*Cluster options object*/
            var clusterOptions = {gridSize: 70, maxZoom: 8};
            /*Add the master markers to the cluster MarkerCluster object*/
            masterClusterInstance = new MarkerClusterer(mapInstance, masterMarkersObj, clusterOptions);
		}
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
	 * @param sector_name {String}, It contains the name of sector configured device.
	 * @param ss_name {String}, It contains the name of sub-station.
	 * @param bs_name {String}, It contains the name of base-station.
	 * @return {Object} pathConnector, It contains gmaps polyline object.
	 */
	this.createLink_gmaps = function(startEndObj,linkColor,bs_info,ss_info,sect_height,sector_name,ss_name,bs_name) {


		var pathDataObject = [
			new google.maps.LatLng(startEndObj.startLat,startEndObj.startLon),
			new google.maps.LatLng(startEndObj.endLat,startEndObj.endLon)
		],
		linkObject = {},
		link_path_color = linkColor;

		var ss_info_obj = "",
			ss_height = 40;

		if(ss_info != undefined || ss_info == "") {
			ss_info_obj = ss_info.info;
			ss_height = ss_info.antenna_height;
		} else {
			ss_info_obj = "";
			ss_height = 40;
		}

		var bs_info_obj = "",
			bs_height = 40;
		if(bs_info != undefined || bs_info == "") {
			bs_info_obj = bs_info.info;
			bs_height = bs_info.antenna_height;
		} else {
			bs_info_obj = "";
			bs_height = 40;
		}

        if (sect_height == undefined || sect_height == ""){
            sect_height = 47;
        }

		linkObject = {
			path 			: pathDataObject,
			strokeColor		: link_path_color,
			strokeOpacity	: 1.0,
			strokeWeight	: 3,
			pointType 		: "path",
			geodesic		: true,
			ss_info			: ss_info_obj,
			ss_lat 			: startEndObj.endLat,
			ss_lon 			: startEndObj.endLon,
			bs_height 		: ss_height,
			bs_lat 			: startEndObj.startLat,
			bs_info 		: bs_info_obj,
			bs_lon 			: startEndObj.startLon,
			ss_height 		: sect_height,
			sectorName 	    : sector_name,
			ssName 		    : ss_name,
			bsName 			: bs_name,
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

			/*Show only 5 rows, hide others*/
			gmap_self.show_hide_info();
		});

		markersMasterObj['Lines'][String(startEndObj.startLat)+ startEndObj.startLon+ startEndObj.endLat+ startEndObj.endLon]= pathConnector;

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
			strokeColor      : "#111111",
			fillColor 	     : bgColor,
			pointType	     : "sector",
			strokeOpacity    : 0.8,
			fillOpacity 	 : 0.4,
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
			/*Show only 5 rows, hide others*/
			gmap_self.show_hide_info();
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

			var sector_ss_name_obj = {
				sector_Alias: contentObject.bs_info[0].value,
				sector_name : contentObject.sectorName,
				ss_name : contentObject.ssName,
				ss_customerName: contentObject.ss_info[17].value,
				ss_circuitId: contentObject.ss_info[3].value
			};

			var sector_ss_name = JSON.stringify(sector_ss_name_obj);

			/*Concat infowindow content*/
			windowContent += "<div class='windowContainer'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i> BS-SS</h4></div><div class='box-body'>"+infoTable+"<div class='clearfix'></div><div class='pull-right'><button class='btn btn-info' id='more_less_btn' onClick='gmap_self.show_hide_info();'>More</button></div><div class='clearfix'></div><ul class='list-unstyled list-inline'><li><button class='btn btn-sm btn-info' onClick='gmap_self.claculateFresnelZone("+contentObject.bs_lat+","+contentObject.bs_lon+","+contentObject.ss_lat+","+contentObject.ss_lon+","+contentObject.bs_height+","+contentObject.ss_height+","+sector_ss_name+");'>Fresnel Zone</button></li></ul></div></div></div>";

		} else if (clickedType == 'sector_Marker') {
/*
						technology: sector_array[j].technology,
						vendor: sector_array[j].vendor,
						deviceExtraInfo: sector_array[j].info,
						deviceInfo: sector_array[j].device_info,
 */
			infoTable += "<table class='table table-bordered'><tbody>";
			for(var i=0; i< contentObject['deviceInfo'].length; i++) {
				if(contentObject['deviceInfo'][i].show) {
					infoTable += "<tr><td>"+contentObject['deviceInfo'][i]['title']+"</td><td>"+contentObject['deviceInfo'][i]['value']+"</td></tr>";		
				}
			}
			infoTable += "<tr><td>Technology</td><td>"+contentObject.technology+"</td></tr>";
			infoTable += "<tr><td>Vendor</td><td>"+contentObject.vendor+"</td></tr>";
			for(var i=0; i< contentObject['deviceExtraInfo'].length; i++) {
				if(contentObject['deviceExtraInfo'][i].show) {
					infoTable += "<tr><td>"+contentObject['deviceExtraInfo'][i]['title']+"</td><td>"+contentObject['deviceExtraInfo'][i]['value']+"</td></tr>";		
				}
			}

			infoTable += "</tbody></table>";

			/*Final infowindow content string*/
			windowContent += "<div class='windowContainer'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>Base Station Device</h4></div><div class='box-body'><div class='' align='center'>"+infoTable+"</div><div class='clearfix'></div><div class='pull-right'><button class='btn btn-info' id='more_less_btn' onClick='gmap_self.show_hide_info();'>More</button></div><div class='clearfix'></div></div></div></div>";
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
			windowContent += "<div class='windowContainer'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>  "+contentObject.pointType.toUpperCase()+"</h4></div><div class='box-body'><div class='' align='center'>"+infoTable+"</div><div class='clearfix'></div><div class='pull-right'><button class='btn btn-info' id='more_less_btn' onClick='gmap_self.show_hide_info();'>More</button></div><div class='clearfix'></div></div></div></div>";
		}
		/*Return the info window content*/
		return windowContent;
	};

	/**
	 * This function show or hide extra info on info window
	 * @method show_hide_info
	 */
	this.show_hide_info = function() {
		
		var tables = $(".windowContainer table");

		if(tables.length == 1) {
			/*Show only 5 rows, hide others*/
			for(var i=7;i<$(".windowContainer table tbody tr").length;i++) {
				if($(".windowContainer table tbody tr")[i].className.indexOf("hide") == -1) {
					$("#more_less_btn").html("More");
					$(".windowContainer table tbody tr")[i].className = "hide";
				} else {
					$("#more_less_btn").html("Less");
					$(".windowContainer table tbody tr")[i].className = "";
				}
			}
		} else {			
			for(var i=1;i<tables.length;i++) {
				for(var j=5;j<tables[i].children[0].children.length;j++) {
					if(tables[i].children[0].children[j].className.indexOf("hide") == -1) {
						$("#more_less_btn").html("More");
						tables[i].children[0].children[j].className = "hide";
					} else {
						$("#more_less_btn").html("Less");
						tables[i].children[0].children[j].className = "";
					}
				}
					
			}
		}
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
	 * @param sector_name {String}, It contains the name of sector configured device
	 * @param ss_name {String}, It contains the sub-station name
	 */
	this.claculateFresnelZone = function(lat1,lon1,lat2,lon2,height1,height2,sector_ss_obj) {
		/*Save sector & ss name in global variables*/
		bts1_name = sector_ss_obj.sector_name;
		bts2_name = sector_ss_obj.ss_name;

		fresnelData.bts1_alias= sector_ss_obj.sector_Alias;
		fresnelData.bts2_customerName= sector_ss_obj.ss_customerName;
		fresnelData.bts2_circuitId= sector_ss_obj.ss_circuitId;

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




		// fresnelData.bts1_alias= sector_ss_obj.sector_Alias;
		// fresnelData.bts2_customerName= sector_ss_obj.ss_customerName;
		// fresnelData.bts2_circuitId= sector_ss_obj.ss_circuitId;

		if(isDialogOpen) {
			/*Fresnel template String*/
			var leftSlider = '<div class="col-md-2" align="center"><div class="col-md-8 col-md-offset-2"><input type="text" id="antinaVal1" class="form-control" value="'+antenaHight1+'"></div><div class="clearfix"></div><div id="antina_height1" style="height:300px;" class="slider slider-blue"></div><div class="col-md-12">'+fresnelData.bts1_alias+"<br />"+bts1_name+'<br /> (Height)</div></div>';
			var chart_detail = '<div id="chart-details"><div><span id="longitude-lbl" class="chart-detail-lbl">Longitude </span> <span id="longitude"></span></div><div><span id="latitude-lbl" class="chart-detail-lbl">Latitude </span> <span id="latitude"></span></div><div><span id="distance-lbl" class="chart-detail-lbl">Distance </span> <span id="distance"></span></div><div><span id="altitude-lbl" class="chart-detail-lbl">Altitude </span> <span id="altitude"></span></div><div><span id="obstacle-lbl" class="chart-detail-lbl">Obstacle </span> <span id="obstacle"></span></div><div><span id="los-lbl" class="chart-detail-lbl">LOS </span> <span id="los"></span></div><div><span id="fresnel1-lbl" class="chart-detail-lbl">Fresnel-1 </span> <span id="fresnel1"></span></div><div><span id="fresnel2-lbl" class="chart-detail-lbl">Fresnel-2 </span> <span id="fresnel2"></span></div><div><span id="fresnel2-altitude-lbl" class="chart-detail-lbl">Clearance </span> <span id="fresnel-altitude"></span></div></div>';
			var middleBlock = '<div class="col-md-8 mid_fresnel_container"><div align="center"><div class="col-md-12">Clearance Factor</div><div class="col-md-4 col-md-offset-3"><div id="clear-factor" class="slider slider-red"></div></div><div class="col-md-2"><input type="text" id="clear-factor_val" class="form-control" value="'+clear_factor+'"></div><div class="clearfix"></div></div><div id="chart_div" style="width:600px;max-width:100%;height:300px;"></div><div class="clearfix divide-10"></div><div id="pin-points-container" class="col-md-12" align="center"></div></div>';
			var rightSlider = '<div class="col-md-2" align="center"><div class="col-md-8 col-md-offset-2"><input type="text" id="antinaVal2" class="form-control" value="'+antenaHight2+'"></div><div class="clearfix"></div><div id="antina_height2" class="slider slider-blue" style="height:300px;"></div><div class="col-md-12">'+fresnelData.bts2_customerName+"<br />"+fresnelData.bts2_circuitId+ "<br />"+ bts2_name+' (Height)</div></div>';

			var fresnelTemplate = "<div class='fresnelContainer row' style='height:400px;overflow-y:auto;'>"+leftSlider+" "+middleBlock+" "+rightSlider+"</div>"+chart_detail;

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

		var sector_ss_obj = {
			"sector_name" : bts1_name,
			"ss_name" : bts2_name,
			"sector_Alias" : fresnelData.bts1_alias,
			"ss_customerName" : fresnelData.bts2_customerName,
			"ss_circuitId" : fresnelData.bts2_circuitId
		};

		gmap_self.claculateFresnelZone(fresnelLat1,fresnelLon1,fresnelLat2,fresnelLon2,antenaHight1,antenaHight2,sector_ss_obj);
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
				$("#polling_tech").html(techOptions);

				/*Populate Vendor dropdown*/
				var vendorOptions = "<option value=''>Select Vendor</option>";
				$.grep(vendorData,function(vendor) {
					vendorOptions += "<option value='"+vendor.id+"' tech_id='"+vendor.tech_id+"' tech_name='"+vendor.tech_name+"'>"+vendor.value.toUpperCase()+"</option>";
				});
				$("#vendor").html(vendorOptions);

				/*Populate City dropdown*/
				var cityOptions = "<option value=''>Select City</option>";
				$.grep(cityData,function(city) {
					cityOptions += "<option state_id='"+city.state_id+"' state_name='"+city.state_name+"' value='"+city.id+"'>"+city.value.toUpperCase()+"</option>";
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
		            sticky: false
		        });
			}
		});
	};

	/**
	 * This function filters bs-ss object as per the applied filters
	 * @method applyFilter_gmaps
	 * @param filtersArray [JSON Array] It is an object array of filters with keys
	 */
	this.applyFilter_gmaps = function(filtersArray) {

		var	filteredData = [];


	 		/*Check that after applying filters any data exist or not*/
	 	// 	if(filteredData.length === 0) {

	 	// 		Reset the markers, polyline & filters
	 	// 		gmap_self.clearGmapElements();
	 	// }
        for(var i=0;i<main_devices_data_gmaps.length;i++)
        {

            /*Deep Copy of the main_devices_data_gmaps*/
            var bs_data= $.extend( true, {}, main_devices_data_gmaps[i]);
            bs_data.data.param.sector=[];
            /*Sectors Array*/
            for(var j=0;j< main_devices_data_gmaps[i].data.param.sector.length;j++) {
                var sector=main_devices_data_gmaps[i].data.param.sector[j];

                if ((filtersArray['technology'] ? filtersArray['technology'].toLowerCase() == sector.technology.toLowerCase(): true) &&
                    (filtersArray['vendor'] ? filtersArray['vendor'].toLowerCase() == sector.vendor.toLowerCase(): true) &&
                    (filtersArray['city'] ? filtersArray['city'].toLowerCase() == main_devices_data_gmaps[i].data.city.toLowerCase(): true) &&
                    (filtersArray['state'] ? filtersArray['state'].toLowerCase() == main_devices_data_gmaps[i].data.state.toLowerCase(): true))
                {
                	bs_data.data.param.sector.push(sector);
                }
            }
            if ( bs_data.data.param.sector.length >0){
                filteredData.push(bs_data)
            }

        }
        /*Check that after applying filters any data exist or not*/
        if(filteredData.length === 0) {
        	/*Reset the markers, polyline & filters*/
            gmap_self.clearGmapElements();

            masterMarkersObj = [];
            slaveMarkersObj = [];

            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: 'GIS : Filters',
                // (string | mandatory) the text inside the notification
                text: 'No data available for applied filters.',
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false
            });


            /*Populate the map with the All markers*/
            // gmap_self.plotDevices_gmap(main_devices_data_gmaps,"base_station");

        } else {

            /*Reset the markers, polyline & filters*/
            gmap_self.clearGmapElements();

            masterMarkersObj = [];
            slaveMarkersObj = [];

            // showRequiredSectorMarker(filteredData);

<<<<<<< HEAD
=======
            tempFilteredData= filteredData;
            isCallCompleted = 1;
>>>>>>> 600754fd233290a1846083d672cbdda943be05bf
            /*Populate the map with the filtered markers*/
            gmap_self.plotDevices_gmap(filteredData,"base_station");
            addSubSectorMarkersToOms(filteredData);
            /*Resetting filter data to Empty.*/
            filteredData=[]
        }

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
        	appliedFilterObj_gmaps["state"] = $("#state option:selected").text();
        }


        try {
            if($("#city").val().length > 0) {
            	appliedFilterObj_gmaps["city"] = $("#city option:selected").text();
            }
        }
        catch(err) {
            //PASS
            //PASS
        }

        /*Get The Length Of Filter Array*/
        var filtersLength = Object.keys(appliedFilterObj_gmaps).length;

        /*If any filter is applied then filter the data*/
        if(filtersLength > 0) {

        	if($.trim(mapPageType) == "gmap") {
        		gmap_self.applyFilter_gmaps(appliedFilterObj_gmaps);
        	} else {
        		// earth_instance.applyFilter_earth(appliedFilterObj_gmaps);
        		gmap_self.applyFilter_gmaps(appliedFilterObj_gmaps);
        	}
        }
        /*If no filter is applied the load all the devices*/
        else {

        	if($.trim(mapPageType) == "gmap") {
    			
    			/*Reset markers & polyline*/
				gmap_self.clearGmapElements();

				/*Reset Global Variables & Filters*/
				gmap_self.resetVariables_gmap();

				/*create the BS-SS network on the google map*/
	            gmap_self.plotDevices_gmap(main_devices_data_gmaps,"base_station");

	            addSubSectorMarkersToOms(main_devices_data_gmaps);

        	} else {

        		/*Clear all the elements from google earth*/
		        earth_instance.clearEarthElements();

		        /*Reset Global Variables & Filters*/
		        earth_instance.resetVariables_earth();

		        /*create the BS-SS network on the google earth*/
		        earth_instance.plotDevices_earth(main_devices_data_earth,"base_station");

		        addSubSectorMarkersToOms();
        	}
        }
    };

    /**
     * This function initialize live polling
     * @method initLivePolling
     */
    this.initLivePolling = function() {

    	$("#sideInfo > .panel-body > .col-md-12 > .devices_container").html("");

    	$("#tech_send").button("complete");
		$("#sideInfo .panel-body .col-md-12 .template_container").html("");

		if(!($("#fetch_polling").hasClass("hide"))) {
			$("#fetch_polling").addClass("hide");
		}
		$("#polling_tech").val($("#polling_tech option:first").val());

    	if($("#sideInfoContainer").hasClass("hide")) {
			$("#sideInfoContainer").removeClass("hide");
		}

		if(!$("#createPolygonBtn").hasClass("hide")) {
			$("#createPolygonBtn").addClass("hide");
		}

		if($("#clearPolygonBtn").hasClass("hide")) {
			$("#clearPolygonBtn").removeClass("hide");
		}
    };

    /**
     * This function initialize live polling
     * @method fetchPollingTemplate_gmap
     */
    this.fetchPollingTemplate_gmap = function() {
    	
    	var selected_technology = $("#polling_tech").val();

    	if(selected_technology != "") {
    		
    		$("#tech_send").button("loading");

    		/*ajax call for services & datasource*/
    		$.ajax({
    			url : window.location.origin+"/"+"device/lp_settings/?technology="+selected_technology,
    			// url : window.location.origin+"/"+"static/livePolling.json",
    			success : function(results) {
					
					result = JSON.parse(results);
    				
    				if(result.success == 1) {

    					/*Make live polling template select box*/
    					var polling_templates = result.data.lp_templates;
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

    					/*Initialize create Polygon functionality*/
    					drawingManager = new google.maps.drawing.DrawingManager({
							drawingMode: google.maps.drawing.OverlayType.POLYGON,
							drawingControl: false,
							drawingControlOptions: {
								position: google.maps.ControlPosition.TOP_CENTER,
								drawingModes: [
									google.maps.drawing.OverlayType.POLYGON,
								]
							},
                            polygonOptions: {
                              fillColor: '#ffffff',
                              fillOpacity: 0,
                              strokeWeight: 2,
                              clickable: false,
                              editable: true,
                              zIndex: 1
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
							var allSS = [];
							
							allSSIds = [];

							$.grep(main_devices_data_gmaps, function(bs) {
								
								$.grep(bs.data.param.sector, function(sector) {

									$.grep(sector.sub_station, function(ss) {
										allSS.push(ss);
									});
								});
							});

							var selected_polling_technology = $("#polling_tech option:selected").text();

							for(var k=0;k<allSS.length;k++) {
									
								var point = new google.maps.LatLng(allSS[k].data.lat,allSS[k].data.lon);

								if (google.maps.geometry.poly.containsLocation(point, polygon)) {

									if($.trim(allSS[k].data.technology) == $.trim(selected_polling_technology)) {

										allSSIds.push(allSS[k].device_name);
										polygonSelectedDevices.push(allSS[k]);
									}
								}
							}

							if(polygonSelectedDevices.length == 0) {

								bootbox.alert("No devices are under the selected area.Please re-select");
								/*Remove current polygon from map*/
								gmap_self.clearPolygon();

							} else if(polygonSelectedDevices.length > 200) {

								bootbox.alert("Max. limit for selecting devices is 200.Please re-select");
								/*Remove current polygon from map*/
								gmap_self.clearPolygon();
							} else {

								var devicesTemplate = "<div class='deviceWellContainer'>";
									
								for(var i=0;i<polygonSelectedDevices.length;i++) {
									
									var new_device_name = "";

									if(polygonSelectedDevices[i].device_name.indexOf(".") != -1) {
										new_device_name = polygonSelectedDevices[i].device_name.split(".");
										new_device_name = new_device_name.join("-");
									} else {
										new_device_name = polygonSelectedDevices[i].device_name;
									}

									devicesTemplate += '<div class="well well-sm" id="div_'+new_device_name+'"><h5>'+(i+1)+'.) '+polygonSelectedDevices[i].name+'</h5>';
									devicesTemplate += '<div style="min-height:60px;margin-top:15px;margin-bottom: 5px;" id="livePolling_'+new_device_name+'">';
									devicesTemplate += '<ul id="pollVal_'+new_device_name+'" class="list-unstyled"></ul>';
									devicesTemplate += '<span class="sparkline" id="sparkline_'+new_device_name+'"></span></div></div>';
								}

								devicesTemplate += "</div>";

								$("#sideInfo > .panel-body > .col-md-12 > .devices_container").html(devicesTemplate);
							}
						});


    				} else {
    					
    					$("#tech_send").button("complete");
    					$("#sideInfo .panel-body .col-md-12 .template_container").html("");

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
    };

    /**
	 * This function fetch the polling value for selected devices
	 * @method getDevicesPollingData
	 */
    this.getDevicesPollingData = function() {

    	if(polygonSelectedDevices.length > 0 && $("#lp_template_select").val() != "") {

			var selected_lp_template = $("#lp_template_select").val();

            // start spinner
            if($("#fetch_spinner").hasClass("hide")) {
				$("#fetch_spinner").removeClass("hide");
			}

	    	$.ajax({
				url : window.location.origin+"/"+"device/lp_bulk_data/?lp_template="+selected_lp_template+"&devices="+JSON.stringify(allSSIds),
				// url : window.location.origin+"/"+"static/services.json",
				success : function(results) {

					var result = JSON.parse(results);

					if(result.success == 1) {
                        
                        // stop spinner
                        if(!($("#fetch_spinner").hasClass("hide"))) {
                            $("#fetch_spinner").addClass("hide");
                        }

						if($(".devices_container").hasClass("hide")) {
							$(".devices_container").removeClass("hide");
						}

						for(var i=0;i<allSSIds.length;i++) {

							var new_device_name = "";
							if(allSSIds[i].indexOf(".") != -1) {
								new_device_name = allSSIds[i].split('.');
								new_device_name = new_device_name.join('-');
							} else {
								new_device_name = allSSIds[i];
							}

							if(result.data.devices[allSSIds[i]] != undefined) {

								var dateObj = new Date(),
									current_time = dateObj.getHours()+":"+dateObj.getMinutes()+":"+dateObj.getSeconds(),
									final_chart_data = [];

								// $("#fetchVal_"+new_device_name).append("(<i class='fa fa-clock-o'></i> "+current_time+", <i class='fa fa-arrow-circle-o-right'></i> "+result.data.devices[allSSIds[i]].value+") , ");
								
								if($("#fetchVal_"+new_device_name).length == 0) {

									var fetchValString = "";
									fetchValString += "<li id='fetchVal_"+new_device_name+"' style='margin-top:8px;margin-bottom:8px;'> (<i class='fa fa-clock-o'></i> "+current_time+", <i class='fa fa-arrow-circle-o-right'></i> "+result.data.devices[allSSIds[i]].value+") <input type='hidden' name='chartVal_"+new_device_name+"' id='chartVal_"+new_device_name+"' value='"+result.data.devices[allSSIds[i]].value+"'/></li>";

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

									$("#fetchVal_"+new_device_name).append(", (<i class='fa fa-clock-o'></i> "+current_time+", <i class='fa fa-arrow-circle-o-right'></i> "+result.data.devices[allSSIds[i]].value+")");
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

								var isPlotted = 0;
								var newIcon = window.location.origin+"/"+result.data.devices[allSSIds[i]].icon;

								$.grep(masterMarkersObj,function(markers) {
									var plottedMarkerName = $.trim(markers.device_name);
									if(plottedMarkerName == allSSIds[i]) {

										isPlotted = 1;
										markers.icon = newIcon;
										markers.oldIcon = newIcon;
										markers.setOptions({icon : newIcon, oldIcon : newIcon});
									}
								});

								if(isPlotted == 0) {

									$.grep(plottedSS,function(markers) {

										var plottedSSName = $.trim(markers.name);

										if(plottedSSName == polygonSelectedDevices[calling_count].name) {

											markers.icon = newIcon;
											markers.oldIcon = newIcon;
											markers.setOptions({
												icon : newIcon,
												oldIcon : newIcon
											});
										}
									});							
									// end if statement
								}

								/*
								// On reset marker icon will reset to new icon
								$.grep(main_devices_data_gmaps,function(devices) {
									var sectors = devices.data.param.sector;
									$.grep(sectors, function(sector) {
										var sub_station = sector.sub_station;
										$.grep(sub_station,function(ss) {
											if($.trim(ss.name) == $.trim(polygonSelectedDevices[calling_count].device_name)) {
												ss.data.markerUrl = result.data.icon;
											}
										});
									});
								});
								*/

							}
						}

					} else {

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
					
					hasSelectDevice = 0;
					/*Call get_page_status function to show the current status*/
    				get_page_status();

					bootbox.alert("No 'Sub-Station' under the selected area.Please re-select");
					/*Remove current polygon from map*/
					gmap_self.clearPolygon();

					if(!($("#selectDeviceContainerBlock").hasClass("hide"))) {
						$("#selectDeviceContainerBlock").addClass("hide");
					}

				} else if(selectedCount > 200) {
					
					hasSelectDevice = 0;
					/*Call get_page_status function to show the current status*/
    				get_page_status();

					bootbox.alert("Max. limit for selecting sub-stations is 200.Please re-select");
					/*Remove current polygon from map*/
					gmap_self.clearPolygon();

					if(!($("#selectDeviceContainerBlock").hasClass("hide"))) {
						$("#selectDeviceContainerBlock").addClass("hide");
					}

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
						devicesTemplate += '<div style="min-height:60px;margin-top:15px;margin-bottom: 5px;" id="livePolling_'+new_device_name+'"></div></div>';
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
									servicesOption += "</select></li><li class='divide-10'></li><li><select class='form-control' id='datasource_"+replace_device_name+"'><option value=''>Select Service Datasource</option></select></li><li class='divide-10'></li><li><button class='btn btn-primary' data-complete-text='Fetch' data-loading-text='Please Wait...' id='fetchBtn_"+replace_device_name+"' onClick='gmap_self.pollDevice_gmap("+deviceNameParam+")'>Fetch</button> <i class='fa fa-spinner fa fa-spin hide' id='fetch_spinner'>&nbsp;</i> </li></ul><div class='clearfix'><ul class='list-unstyled' id='pollVal_"+replace_device_name+"'></ul></div>";

									$("#livePolling_"+replace_device_name).append(servicesOption);
								}

								/*Hide the spinner*/
								$("#sideInfoContainer .panel-title i").addClass("hide");

							} else {

								$.gritter.add({
						            // (string | mandatory) the heading of the notification
						            title: 'Live Polling - Error',
						            // (string | mandatory) the text inside the notification
						            text: result.message,
						            // (bool | optional) if you want it to fade out on its own or just sit there
						            sticky: false
						        });
						        /*Hide the spinner*/
								$("#sideInfoContainer .panel-title i").addClass("hide");
							}
						},
						error : function(err) {

							$.gritter.add({
					            // (string | mandatory) the heading of the notification
					            title: 'Live Polling - Server Error',
					            // (string | mandatory) the text inside the notification
					            text: err.statusText,
					            // (bool | optional) if you want it to fade out on its own or just sit there
					            sticky: false
					        });
					        /*Hide the spinner*/
							$("#sideInfoContainer .panel-title i").addClass("hide");
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

			$("#fetchBtn_"+deviceName).button("loading");

			if($("#fetch_spinner").hasClass("hide")) {
				$("#fetch_spinner").removeClass("hide");
			}

			if($("#fetchVal_"+deviceName+"_"+selectedDatasourceVal).length > 0) {
				
				var data_with_bracket = $("#fetchVal_"+deviceName+"_"+selectedDatasourceVal).html().split(":-")[1].replace(/ +/g, "").split(","),
					string_val = [];

				/*Remove ')' from data_with_bracket array and make new array*/
				for(var i=1;i<data_with_bracket.length;i += 2) {
					string_val.push(data_with_bracket[i].replace(')', ''));
				}

				/*Create integer array from fetched values for sparkline chart*/
				var chart_data = string_val.map(function(item) {
				    return parseInt(item, 10);
				});				
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

							var dateObj = new Date(),
								current_time = dateObj.getHours()+":"+dateObj.getMinutes()+":"+dateObj.getSeconds(),
								final_chart_data = [];

							if($("#fetchVal_"+deviceName+"_"+selectedDatasourceVal).length == 0) {

								var fetchValString = "";
								fetchValString += "<li id='fetchVal_"+deviceName+"_"+selectedDatasourceVal+"' style='margin-top:8px;margin-bottom:8px;'><b>"+selectedDatasourceTxt.toUpperCase()+"</b> :- (<i class='fa fa-clock-o'></i> "+current_time+", <i class='fa fa-arrow-circle-o-right'></i> "+result.data.value[0]+")</li>";
								fetchValString += "<li><span class='sparkline' id='sparkline_"+deviceName+"_"+selectedDatasourceVal+"'></span></li>";

								$("#pollVal_"+deviceName+" ").append(fetchValString);
								/*Sparkline Chart Data*/
								final_chart_data.push((+result.data.value[0]));
							
							} else {
								$("#fetchVal_"+deviceName+"_"+selectedDatasourceVal).append(", (<i class='fa fa-clock-o'></i> "+current_time+", <i class='fa fa-arrow-circle-o-right'></i> "+result.data.value[0]+")");
								/*Sparkline Chart Data*/
								final_chart_data = chart_data;
							}

							/*Plot sparkline chart with the fetched polling value*/
							$("#sparkline_"+deviceName+"_"+selectedDatasourceVal).sparkline(final_chart_data, {

						        type: "line",
						        lineColor: "blue",
						        spotColor : "orange",
						        defaultPixelsPerValue : 10
						    });
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
				            sticky: false
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
			            sticky: false
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
	            sticky: false
	        });
		} // End else Statement
	};

	/**
	 * This function enables ruler tool & perform corresponding functionality.
	 * @method addRulerTool_gmap
	 */
	this.addRulerTool_gmap = function() {
        //first clear the click listners. point tool might be in use
        google.maps.event.clearListeners(mapInstance,'click');

		google.maps.event.addListener(mapInstance,'click',function(e) {

			if(isCreated == 0) {

				if(ruler_pt_count < 2) {

					/*Create Point*/
					ruler_point = new google.maps.Marker({position: e.latLng, map: mapInstance});
					ruler_array.push(ruler_point);

					/*If second point is plot*/
					if(ruler_pt_count == 1) {

						/*Lat lon object for poly line*/
						var latLonObj = {
							"startLat" : ruler_array[0].getPosition().lat(),
							"startLon" : ruler_array[0].getPosition().lng(),
							"endLat" : ruler_array[1].getPosition().lat(),
							"endLon" : ruler_array[1].getPosition().lng()
						};

						var ruler_line = gmap_self.createLink_gmaps(latLonObj);
						tools_line_array.push(ruler_line);

						var latLon1 = new google.maps.LatLng(ruler_array[0].getPosition().lat(), ruler_array[0].getPosition().lng()),
							latLon2 = new google.maps.LatLng(ruler_array[1].getPosition().lat(), ruler_array[1].getPosition().lng());

						/*Distance in Km's */
						var distance = (google.maps.geometry.spherical.computeDistanceBetween(latLon1, latLon2) / 1000).toFixed(2);

					    //convert degree to radians
					    var lat1 = ruler_array[0].getPosition().lat() * Math.PI / 180;
					    var lat2 = ruler_array[1].getPosition().lat() * Math.PI / 180;
					    var lon1 = ruler_array[0].getPosition().lng() * Math.PI / 180;

					    var dLon = (ruler_array[1].getPosition().lng() - ruler_array[0].getPosition().lng()) * Math.PI / 180;

					    var Bx = Math.cos(lat2) * Math.cos(dLon);
					    var By = Math.cos(lat2) * Math.sin(dLon);
					    var lat3 = Math.atan2(Math.sin(lat1) + Math.sin(lat2), Math.sqrt((Math.cos(lat1) + Bx) * (Math.cos(lat1) + Bx) + By * By));
					    var lon3 = lon1 + Math.atan2(By, Math.cos(lat1) + Bx);

					    /*Create distance infobox(label)*/
						distance_label = new InfoBox({
							content: distance+" Km",
							boxStyle: {
								border: "2px solid black",
								background: "white",
							    textAlign: "center",
							    fontSize: "10pt",
							    color: "black",
							    width: '80px'
							},
							disableAutoPan: true,
							pixelOffset: new google.maps.Size(-25, 0),
							position: new google.maps.LatLng(lat3 * 180 / Math.PI,lon3 * 180 / Math.PI),
							closeBoxURL: "",
							isHidden: false,
							enableEventPropagation: true,
							zIndex_: 9999
						});

						/*Show distance infobox*/
						distance_label.open(mapInstance);

				        /*True the flag value*/
						isCreated = 1;
					}

				} else {

					for(var i=0;i<ruler_array.length;i++) {
						ruler_array[i].setMap(null);
					}
					ruler_array = [];

					/*Remove line between two points*/
					for(var j=0;j<tools_line_array.length;j++) {
						tools_line_array[j].setMap(null);
					}
					tools_line_array = [];

					/*Remove Distance Label*/
					if(distance_label.map != undefined) {
						distance_label.setMap(null);
					}

					isCreated = 0;
				}

				/*Increment points count*/
				ruler_pt_count++;

			} else {

				for(var i=0;i<ruler_array.length;i++) {
					ruler_array[i].setMap(null);
				}
				ruler_array = [];

				/*Remove line between two points*/
				for(var j=0;j<tools_line_array.length;j++) {
					tools_line_array[j].setMap(null);
				}
				tools_line_array = [];

				/*Remove Distance Label*/
				if(distance_label.map != undefined) {
					distance_label.setMap(null);
				}

				isCreated = 0;
				ruler_pt_count = 0;
			}
		});
	};

	/**
	 * This function disable ruler tool.
	 * @method clearToolsParams_gmap
	 */
	this.clearToolsParams_gmap = function() {

		/*Reset global variables*/
		isCreated = 0;
		ruler_pt_count = 0;

		/*If any info window is open then close it*/
		infowindow.close();

		for(var i=0;i<ruler_array.length;i++) {
			ruler_array[i].setMap(null);
		}
		ruler_array = [];

		/*Remove line between two points*/
		for(var j=0;j<tools_line_array.length;j++) {
			tools_line_array[j].setMap(null);
		}
		tools_line_array = [];

		/*Remove Distance Label*/
		if(distance_label.map != undefined) {
			distance_label.setMap(null);
		}

		/*If system freezed then unfreeze the system & recall the server*/
		if(isFreeze == 1) {

			isFreeze = 0;
			gmap_self.recallServer_gmap();
		}

        if (map_point_count == 0){
            /*Remove click listener from google maps*/
		    google.maps.event.clearListeners(mapInstance,'click');
        }
	};

    /**
	 * This function enables point tool & perform corresponding functionality.
	 * @method addPointTool_gmap
	 */
	this.addPointTool_gmap = function() {

        //first clear the listners. as ruler tool might be in place
        google.maps.event.clearListeners(mapInstance,'click');

        var image = '/static/img/icons/caution.png';
		google.maps.event.addListener(mapInstance,'click',function(e) {

            map_point = new google.maps.Marker({position: e.latLng, map: mapInstance, icon: image});

            map_points_array.push(map_point);

            map_point_count ++;

		});
	};

    /**
	 * This function enables point tool & perform corresponding functionality.
	 * @method clearPointTool_gmap
	 */
	this.clearPointTool_gmap = function() {

		for(var j=0;j<map_points_array.length;j++) {
			map_points_array[j].setMap(null);
		}
        map_points_array = [];
        map_point_count = 0;
        /*Remove click listener from google maps*/
        if (ruler_pt_count == 0){
            google.maps.event.clearListeners(mapInstance,'click');
        }
	};

	/**
	 * This function freeze the server call for BS-SS data
	 * @method freezeDevices_gmap
	 */
	 this.freezeDevices_gmap = function() {

	 	/*Enable freeze flag*/
	 	isFreeze = 1;
	 };

	 /**
	 * This function unfreeze the system & recall the server
	 * @method unfreezeDevices_gmap
	 */
	 this.unfreezeDevices_gmap = function() {

	 	/*Enable freeze flag*/
	 	isFreeze = 0;

	 	/*Recall the server*/
	 	gmap_self.recallServer_gmap();
	 };

	/**
	 * This function clear the polygon selection from the map
	 * @method clearPolygon
	 */
	this.clearPolygon = function() {

		// oms.unspiderfy();

		/*Update the html of accordian body*/
		// $("#sideInfo > .panel-body").html("No device selected.");

		/*Collapse the selected devices accordian*/
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

		/*Enable other buttons*/
    	disableAdvanceButton("no");
    	$("#resetFilters").button("complete");

		if(Object.keys(currentPolygon).length > 0) {
			/*Remove the current polygon from the map*/
			currentPolygon.setMap(null);
		}
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
     * This function resets the global variables & again call the api calling function after given timeout i.e. 5 minutes
     * @method recallServer_gmap
     */
    this.recallServer_gmap = function() {

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
	 * This function removes all the elements from the map
	 * @method clearGmapElements
	 */
	this.clearGmapElements = function() {

		/*close infowindow*/
		infowindow.close();

		/*Hide The loading Icon*/
		$("#loadingIcon").hide();

		/*Enable the refresh button*/
		$("#resetFilters").button("complete");

		/*Remove All Master Markers*/
		for(var i=0;i<masterMarkersObj.length;i++) {

			masterMarkersObj[i].setMap(null);
		}

		for(var i=0;i<sector_MarkersArray.length; i++) {
			sector_MarkersArray[i].setMap(null)
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

		/*Clear the marker array of OverlappingMarkerSpiderfier*/
		oms.clearMarkers();
        oms_ss.clearMarkers();

		/*Clear master marker cluster objects*/
		if(masterClusterInstance != "") {
			masterClusterInstance.clearMarkers();
		}		
	};

	//This function updates the Marker Icon with the new Size.
	this.updateAllMarkersWithNewIcon= function(iconSize) {

		var largeur= 32, hauteur= 37, divideBy;
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
		for(i=0; i< sector_MarkersArray.length; i++) {
			(function updateSectMarker(markerIcon) {
				icon= markerIcon;
				var iconUrl;
				if(typeof(icon.oldIcon)=== "string") {
					iconUrl= icon.oldIcon;
				} else {
					iconUrl= icon.oldIcon.url;
				}
				//Create a new marker Image according to the value selected
				markerImage= new google.maps.MarkerImage(
					iconUrl,
					new google.maps.Size(Math.ceil(largeur/divideBy), Math.ceil(hauteur/divideBy)),
					new google.maps.Point(0, 0), 
					new google.maps.Point(Math.ceil(16-(16*anchorX)), Math.ceil(hauteur/divideBy)),
					new google.maps.Size(Math.ceil(largeur/divideBy), Math.ceil(hauteur/divideBy)));
				//Set oldIcon for Sector Marker to the new image.
				markerIcon.oldIcon= markerImage;
			})(sector_MarkersArray[i]);
		}
	//End of Loop through the sector markers


	//Loop through the Master Markers
		for(var i=0; i< masterMarkersObj.length; i++ ) {
			(function updateMasterMarker(markerIcon) {
				icon = markerIcon.getIcon();
				//If icon is "" it mean it is a BS marker
				if(markerIcon.pointType=== "base_station") {
					var iconUrl;
					if(typeof(markerIcon.oldIcon)=== "string") {
						iconUrl= markerIcon.oldIcon;
					} else {
						iconUrl= markerIcon.oldIcon.url;
					}
					//Create a new marker Image for BS Marker according to the value selected.
					markerImage= new google.maps.MarkerImage(
						iconUrl,
						new google.maps.Size(Math.ceil(largeur/divideBy)-5, Math.ceil(hauteur/divideBy)+5),
						new google.maps.Point(0, 0), 
						new google.maps.Point(Math.ceil(16-(16*anchorX)), Math.ceil(hauteur/divideBy)),
						new google.maps.Size(Math.ceil(largeur/divideBy)-5, Math.ceil(hauteur/divideBy)+5));
					//Set oldIcon for BS Marker to the new image
					markerIcon.oldIcon= markerImage;
					//Else icon is for SSpointType	     : "sub_station",
				} else if (markerIcon.pointType === "sub_station") {

					//Create a new marker Imge for SS marker according to the value selected for OLD ICON.
					markerImage2= new google.maps.MarkerImage(
						markerIcon.oldIcon.url,
						new google.maps.Size(Math.ceil(largeur/divideBy), Math.ceil(hauteur/divideBy)),
						new google.maps.Point(0, 0), 
						new google.maps.Point(Math.ceil(16-(16*anchorX)), Math.ceil(hauteur/divideBy)),
						new google.maps.Size(Math.ceil(largeur/divideBy), Math.ceil(hauteur/divideBy)));
					//Set icon to Marker Image
					markerIcon.setIcon(markerImage2);
					// //Set oldIcon to Marker Image
					markerIcon.oldIcon= markerImage2;
				}
			})(masterMarkersObj[i]);
		}
	//End of Loop through the Master Markers
	}

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
		sectorMarkersMasterObj= {};
	};
}


function prepare_data_for_filter(){

//    filter_data_bs_name_collection=[],
//        filter_data_bs_lat_collection =[],
//        filter_data_bs_lon_collection=[],
    var filter_data_bs_city_collection=[];
        filter_data_bs_state_collection=[];
        filter_data_sector_ss_technology_collection=[];
        filter_data_sector_ss_vendor_collection=[];
//        filter_data_sector_configured_on_collection=[];
//        filter_data_sector_circuit_ids_collection=[];

    if ( main_devices_data_gmaps.length >0 )
        {
            for (i=0; i< main_devices_data_gmaps.length; i++)
            {            	
//                filter_data_bs_name_collection.push({ 'id':[main_devices_data_gmaps[i].id],
//                                                      'value':main_devices_data_gmaps[i].name });
//
//                filter_data_bs_lat_collection.push({ 'id':[main_devices_data_gmaps[i].id] ,
//                                                     'value':main_devices_data_gmaps[i].data.lat });
//
//                filter_data_bs_lon_collection.push({ 'id':[main_devices_data_gmaps[i].id],
//                                                     'value':main_devices_data_gmaps[i].data.lon });

//                filter_data_sector_configured_on_value= main_devices_data_gmaps[i].sector_configured_on_devices.split(' ').filter(function (n) { return n != ""})
//                for (var k=0;k<filter_data_sector_configured_on_value.length;k++){
//                    filter_data_sector_configured_on_collection.push({ 'id':[main_devices_data_gmaps[i].id],
//                                                     'value':filter_data_sector_configured_on_value[k] });
//                }

//                filter_data_sector_circuit_ids_values= main_devices_data_gmaps[i].circuit_ids.split(' ').filter(function (n) { return n != ""})

//                for (var k=0;k<filter_data_sector_circuit_ids_values.length;k++){
//                    filter_data_sector_circuit_ids_collection.push({ 'id':[main_devices_data_gmaps[i].id],
//                                                     'value':filter_data_sector_circuit_ids_values[k] });
//                }

                filter_data_sector_ss_technology_value= main_devices_data_gmaps[i].sector_ss_technology.split(' ').filter(function (n) { return n != ""})
                filter_data_sector_ss_technology_collection.push({ 'id': main_devices_data_gmaps[i].id ,
                        'value':filter_data_sector_ss_technology_value });


                filter_data_sector_ss_vendor_value= main_devices_data_gmaps[i].sector_ss_vendor.split(' ').filter(function (n) { return n != ""})
                filter_data_sector_ss_vendor_collection.push({ 'id':main_devices_data_gmaps[i].id,
                                                      'value':filter_data_sector_ss_vendor_value });


                /*removing the devices which do not have the states and city entered.*/
                if (main_devices_data_gmaps[i].data.state != 'N/A'){
                    filter_data_bs_state_collection.push({ 'id': main_devices_data_gmaps[i].id,
                            'value': main_devices_data_gmaps[i].data.state });
                }

                if (main_devices_data_gmaps[i].data.city != 'N/A'){
                    filter_data_bs_city_collection.push({ 'id': main_devices_data_gmaps[i].id,
                            'value': main_devices_data_gmaps[i].data.city });
                }
            }

            filter_data_bs_state_collection= unique_values_field_and_with_base_station_ids(filter_data_bs_state_collection);
            filter_data_bs_city_collection= unique_values_field_and_with_base_station_ids(filter_data_bs_city_collection);
            filter_data_sector_ss_technology_collection= unique_values_field_and_with_base_station_ids(filter_data_sector_ss_technology_collection,'technology');
            filter_data_sector_ss_vendor_collection= unique_values_field_and_with_base_station_ids(filter_data_sector_ss_vendor_collection,'vendor');

            var filter_data=[
//                {
//                'element_type':'multiselect',
//                'field_type':'string',
//                'key':'name',
//                'title':'BS Name',
//                'values':filter_data_bs_name_collection
//                },
                {
                'element_type':'multiselect',
                'field_type':'string',
                'key':'technology',
                'title':'Technology',
                'values':filter_data_sector_ss_technology_collection
                },
                {
                'element_type':'multiselect',
                'field_type':'string',
                'key':'vendor',
                'title':'Vendor',
                'values':filter_data_sector_ss_vendor_collection
                },
                {
                'element_type':'multiselect',
                'field_type':'string',
                'key':'state',
                'title':'BS State',
                'values':filter_data_bs_state_collection
                },
                {
                'element_type':'multiselect',
                'field_type':'string',
                'key':'city',
                'title':'BS City',
                'values':filter_data_bs_city_collection
                }
//                {
//                'element_type':'multiselect',
//                'field_type':'string',
//                'key':'latitude',
//                'title':'BS Latitude',
//                'values':filter_data_bs_lat_collection
//                },
//                {
//                'element_type':'multiselect',
//                'field_type':'string',
//                'key':'longitude',
//                'title':'BS Longitude',
//                'values':filter_data_bs_lon_collection
//                },
//                {
//                'element_type':'multiselect',
//                'field_type':'string',
//                'key':'sector_configured_on',
//                'title':'Sector Configured On',
//                'values':filter_data_sector_configured_on_collection
//                },
//                {
//                'element_type':'multiselect',
//                'field_type':'string',
//                'key':'circuit_ids',
//                'title':'Circuit Id',
//                'values':filter_data_sector_circuit_ids_collection
//                }
            ];
    }//if condition closed
    return filter_data

}//function closed


function getDataForAdvanceSearch() {
	//extra form elements that will be showing in Advance Search. We will get other Elements like City, Vendor, Technology from prepare_data_for_filter();
	var filter_data_bs_name_collection=[],
	filter_data_bs_lat_collection =[],
	filter_data_bs_lon_collection=[],
	filter_data_sector_configured_on_collection=[];
	filter_data_sector_circuit_ids_collection=[];

    if(main_devices_data_gmaps.length >0) {
    	for (i=0; i< main_devices_data_gmaps.length; i++) {

    		filter_data_bs_name_collection.push({ 'id':[main_devices_data_gmaps[i].id], 'value':main_devices_data_gmaps[i].name });

    		filter_data_bs_lat_collection.push({ 'id':[main_devices_data_gmaps[i].id] , 'value':main_devices_data_gmaps[i].data.lat });

    		filter_data_bs_lon_collection.push({ 'id':[main_devices_data_gmaps[i].id], 'value':main_devices_data_gmaps[i].data.lon });

    		filter_data_sector_configured_on_value= main_devices_data_gmaps[i].sector_configured_on_devices.split(' ').filter(function (n) { return n != ""});

    		for (var k=0;k<filter_data_sector_configured_on_value.length;k++) {
    			filter_data_sector_configured_on_collection.push({ 'id':[main_devices_data_gmaps[i].id], 'value':filter_data_sector_configured_on_value[k] });
    		}

    		filter_data_sector_circuit_ids_values= main_devices_data_gmaps[i].circuit_ids.split(' ').filter(function (n) { return n != ""});

    		for (var k=0;k<filter_data_sector_circuit_ids_values.length;k++){
    			filter_data_sector_circuit_ids_collection.push({ 'id':[main_devices_data_gmaps[i].id], 'value':filter_data_sector_circuit_ids_values[k] });
    		}
    	}

    	var advanceSearchFilterData= prepare_data_for_filter();

    	advanceSearchFilterData.push({
    			'element_type':'multiselect',
    			'field_type':'string',
    			'key':'name',
    			'title':'BS Name',
    			'values':filter_data_bs_name_collection
    		});

    	advanceSearchFilterData.push({
    			'element_type':'multiselect',
    			'field_type':'string',
    			'key':'latitude',
    			'title':'BS Latitude',
    			'values':filter_data_bs_lat_collection
    		});

    	advanceSearchFilterData.push({
    			'element_type':'multiselect',
    			'field_type':'string',
    			'key':'longitude',
    			'title':'BS Longitude',
    			'values':filter_data_bs_lon_collection
    		});

    	advanceSearchFilterData.push({
    			'element_type':'multiselect',
    			'field_type':'string',
    			'key':'sector_configured_on',
    			'title':'IP',
    			'values':filter_data_sector_configured_on_collection
    		});

    	advanceSearchFilterData.push({
    			'element_type':'multiselect',
    			'field_type':'string',
    			'key':'circuit_ids',
    			'title':'Circuit Id',
    			'values':filter_data_sector_circuit_ids_collection
    		});
    	
    }//if condition closed
    return advanceSearchFilterData;
}



function unique_values_field_and_with_base_station_ids(filter_data_collection, type){
    /*Unique mappper names.*/

    /*Incase of technology and vendor the two values can appear for the sector_configured_on device as well as in  Substation.*/
    var unique_names={};
    if (type=='technology' || type=='vendor'){

        for (var i=0;i< filter_data_collection.length; i++)
        {
            if (filter_data_collection[i].value.length>1)
            {
                for(var j=0;j< filter_data_collection[i].value.length; j++)
                {
                    unique_names[filter_data_collection[i].value[j]]=true
                }
            }
            else {

                unique_names[filter_data_collection[i].value]=true
            }
        }

    } else {
        for (var i=0;i< filter_data_collection.length; i++)
        {
            unique_names[filter_data_collection[i].value]=true
        }

    }
    unique_names= Object.keys(unique_names);

    /*All the devices_ids w.r.t to the mappers*/
    var result_bs_collection=[];
    for (var i=0;i< unique_names.length; i++)
        {
            var unique_device_ids=[];

            for(var j=0;j< filter_data_collection.length; j++)
            {

                if (type=='technology' || type=='vendor'){

                    if (filter_data_collection[j].value.length>1)
                    {
                       for(var k=0;k< filter_data_collection[j].value.length; k++)
                       {
                          if(unique_names[i]== filter_data_collection[j].value[k])
                          {
                            unique_device_ids.push(filter_data_collection[j].id)
                          }
                       }
                    }
                    else{
                        if(unique_names[i]== filter_data_collection[j].value[0])
                        {
                            unique_device_ids.push(filter_data_collection[j].id)
                        }
                    }
                } else {
                        if (unique_names[i]== filter_data_collection[j].value)
                        {
                            unique_device_ids.push(filter_data_collection[j].id)
                        }
                }
            }
        result_bs_collection.push({'id':unique_device_ids, 'value': unique_names[i] });
        }
    return result_bs_collection
}

function include_performancedata()
{
    var sco_devices=[];
    var circuit_ids=[];
    for (var i=0; i<main_devices_data_gmaps.length; i++)
    {
        sco_devices.push(main_devices_data_gmaps[i].sector_configured_on_devices.split(' '))
        circuit_ids.push(main_devices_data_gmaps[i].circuit_ids.split(' '))
    }

    $.ajax({
        url : window.location.origin+"/performance/gismap_data/",
	    type : "POST",
        data:{'sco_devices':sco_devices,'circuit_ids':circuit_ids },
	    dataType : "json",
	    /*If data fetched successful*/
	    success : function(result){
            console.log(result)
        }
    })
}

