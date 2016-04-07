/**
 * This library is used to plot google map & also handle the corresponding functionality
 * @for devicePlotingLib
 * @uses jQuery
 * @uses Google Maps
 * @uses jQuery Flot
 * @uses jQuery UI
 * @uses Highcharts
 * @uses Loki DB
 * @uses OverlappingMarkerSpiderfier
 * @uses markerCluster
 * @uses jquery.cookie
 * @uses infobox
 * @uses sparkline charts
 * @uses fullScreenControl(for google map fullscreen)
 * Coded By :- Yogender Purohit
 */

/*global instance & other variables*/
var mapInstance = "",
	gmap_self = "",
	admin_val_list = ['admin'],
	gisPerformanceClass = {},
	infowindow = "",
	drawingManager = "",
	drawingManager_livePoll = "",
	masterClusterInstance = "",
	base_url = "",
	defaultIconSize = 'medium',
	counter_div_style = "",
	green_status_array = ['ok','success','up'],
    red_status_array = ['critical','down'],
    orange_status_array = ['warning'],
    ptp_tech_list = ['ptp','p2p','ptp bh','ptp-bh'],
    search_element_bs_id = [],
    meter_unit_fields = [
    	'radwin_link_distance_invent_link_distance'
	],
    mbps_unit_fields = [
    	'radwin_ul_utilization_Management_Port_on_Odu',
    	'radwin_dl_utilization_Management_Port_on_Odu',
    	'cambium_ul_utilization_ul_utilization',
    	'cambium_dl_utilization_dl_utilization',
    	'wimax_ss_ul_utilization_ul_utilization',
    	'wimax_ss_dl_utilization_dl_utilization',
    	'wimax_pmp1_utilization_pmp1_utilization',
    	'wimax_pmp2_utilization_pmp2_utilization'
	],
    india_center_lon = 79.0900,
    india_center_lat = 21.1500,
    posLink1 = "https://121.244.244.23/ISCWebServiceUI/JSP/types/ISCType.faces?serviceId",
	posLink2 = "https://liferay/ExternalLinksWSUI/JSP/ProvisioningDetails.faces?serviceId",
	svp_link = "http://172.31.6.73/ipservices/wirelessintegrate/integratesv.php?viznet_id",
	ptp_not_show_items = ['pe_ip'],
	tech_list = ['PMP', 'PTP', 'P2P', 'WiMAX'];

/*Lazy loading API calling variables*/
var hitCounter = 1,
	showLimit = 0,
	counter = -999,
	devicesObject = {},
	devicesCount = 0;

/*Flag variables*/
var isFreeze = 0,
	isFirstTime = 1,
	isCallCompleted = 0,
	isPollingActive = 0,
	isExportDataActive = 0,
	isApiResponse = 1,
	isAdvanceFilter = 0,
	isAdvanceSearch = 0,
	isDebug = false;

/*Global data objects & arrays of map data & filters*/
var main_devices_data_gmaps = [],
	currentlyPlottedDevices = [],
	plottedBsIds = [],
	lastZoomLevel = 5,
	current_zoom = 5,
	bs_marker_icon_obj = "",
	hiddenIconImageObj = "",
	all_devices_loki_db = [],
	state_wise_device_counters = {},
	state_wise_device_labels = {},
	null_state_device_counters = {},
	searchResultData = [],
	clusterOptions = {gridSize: 60, maxZoom: 8},
	markersMasterObj= {'BS': {}, 'Lines': {}, 'SS': {}, 'BSNamae': {}, 'SSNamae': {}, 'LinesName': {}, 'Poly': {}},
    allMarkersObject_gmap= {'base_station': {}, 'path': {}, 'sub_station': {}, 'sector_device': {}, 'sector_polygon': {}, 'backhaul' : {}},
    allMarkersArray_gmap = [],
    bs_loki_db = [],
    ss_loki_db = [],
    sector_loki_db = [],
    polygon_loki_db = [],
    line_loki_db = [],
	oms = "",
    oms_ss = "",
    oms_sect = "",
    tech_vendor_obj = {},
	all_vendor_array = [],
	state_city_obj = {},
	all_cities_array = [],
	bsLatArray = [],
	bsLonArray = [],
	masterMarkersObj = [],
	labelsArray = [],
	labelsArray_filtered = [],
	appliedFilterObj_gmaps = {},
	ssLinkArray = [],
	ssLinkArray_filtered = [],
	lastSearchedPt = {},
    data_for_filters = [],
    sector_MarkersArray= [],
    sectorMarkersMasterObj= {},
    sectorMarkerConfiguredOn= [],
    place_markers = [],
	currentDevicesObject_gmap= {'base_station': {}, 'path': {}, 'sub_station': {}, 'sector_device': {}},
	exportDataPolygon = {},
	inventory_bs_ids = [],
	cross_label_array = {},
	ssParamLabelStyle = {
        border 		  : "1px solid #B0AEAE",
        background 	  : "white",
        textAlign 	  : "center",
        fontSize 	  : "10px",
        color 		  : "black",
        padding 	  : '2px',
        borderRadius  : "5px",
        width  		  : '110px',
        maxWidth  	  : '110px'
    },
    country_label = {
    	"india" : ""
    },
    direct_val_keys = ['pos_link1','pos_link2'];

/* Live Polling Variables */
var allSSIds = [],
	polygonSelectedDevices = [],
	currentPolygon = {},
	polled_devices_names = [],
	complete_polled_devices_data = [],
	complete_polled_devices_icon = {},
	total_polled_occurence = 0,
	nav_click_counter = 0,
	polled_device_count = {},
	pollableDevices = [],
	pollCallingTimeout = "",
	remainingPollCalls = 0,
	pollingInterval = 10,
	pollingMaxInterval = 1,
	isPollingPaused = 0,
	isPerfCallStopped = 1,
	isPerfCallStarted = 0;

/*Tools Global Variables*/
var is_line_active = 0,
	is_bs_clicked = 0,
	is_ruler_active= -1,
	line_pt_array =[],
	ruler_array = [],
	ruler_line_color = 'rgba(255,192,0,0.97)',
	tools_rule_array = [],
	isCreated = 0,
	ruler_pt_count = 0,
	temp_line = "",
	distance_label = {},
    map_points_array = [],
    map_points_lat_lng_array= [],
    map_point_count = 0,
    pointAdded= -1,
    tools_line_array =[],
	tools_line_marker_array= [],
	distance_line_label= "",
	point_icon_url = "/static/img/icons/tools/point/caution.png",
	point_data_obj = {},
	line_data_obj = {},
	connected_end_obj = {},
	current_point_for_line = "",
	last_selected_label = "",
	tooltipInfoLabel = {},
	last_perf_called_items = [],
	letter_a_img_url = 'static/img/icons/letter_a.png',
	letter_b_img_url = 'static/img/icons/letter_b.png';

/*Variables used in fresnel zone feature*/
var isDialogOpen = true,
	bts1_name = "",
	bts2_name = "",
	fresnelLat1 = "",
	fresnelLon1 = "",
	fresnelLat2 = "",
	fresnelLon2 = "",
	fresnelData = {},
	arrayCounter = 0,
	latLongArray = [],
	latLongArrayCopy = [],
	depthStep = 6,
	freq_mhz = 900, //MHZ
	total_bs = [],
	fresnel_isBSLeft = 1,
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
	sectorMarkersInMap = [],
	sectorOmsMarkers = [],
	na_items_list = ['n/a', 'na'];

/**
 * This class is used to plot the BS & SS on the google maps & performs their functionality.
 * @class gmap_devicePlottingLib
 */
function devicePlottingClass_gmap() {

	/*Store the reference of current pointer in a global variable*/
	gmap_self = this;

	/**
	 * This function creates google map & defines the corresponding events
	 * @method createMap
	 * @param domElement {String}, It the the dom element on which the map is to be create
	 */
	this.createMap = function(domElement) {

		//display advance search, filter etc button when call is going on.
		disableAdvanceButton();

		/*If no internet access*/
		if(typeof google != "undefined") {
			var mapObject = {};
			if(window.location.pathname.indexOf("setellite") > -1) {
				mapObject = {
					center    : new google.maps.LatLng(india_center_lat,india_center_lon),
					zoom      : 5,
					mapTypeId : google.maps.MapTypeId.HYBRID/*google.maps.MapTypeId.SATELLITE*/,
					mapTypeControl : true,
					styles 	  : typeof gmap_styles_array != 'undefined' ? gmap_styles_array[1] : {},
					mapTypeControlOptions: {
						mapTypeIds: [google.maps.MapTypeId.SATELLITE, google.maps.MapTypeId.HYBRID],
						style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
					}
				};
			} else {
				mapObject = {
					center    : new google.maps.LatLng(india_center_lat,india_center_lon),
					zoom      : 5,
					mapTypeId : google.maps.MapTypeId.ROADMAP,
					mapTypeControl : true,
					styles 	  : typeof gmap_styles_array != 'undefined' ? gmap_styles_array[1] : {},
					mapTypeControlOptions: {
						mapTypeIds: [
							google.maps.MapTypeId.ROADMAP,
							google.maps.MapTypeId.TERRAIN,
							google.maps.MapTypeId.SATELLITE,
							google.maps.MapTypeId.HYBRID
						],
						style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
					},
					draggableCursor : ''
				};
			}

			/*Create Map Type Object*/
			mapInstance = new google.maps.Map(document.getElementById(domElement),mapObject);

			/*Initialize markercluster*/
         	masterClusterInstance = new MarkerClusterer(mapInstance, [], clusterOptions);

			/*style for state wise counter label*/
			counter_div_style = "";
			counter_div_style += "margin-left:-30px;margin-top:-30px;cursor:pointer;";
			counter_div_style += "background:url("+base_url+"/static/js/OpenLayers/img/state_cluster.png) top center no-repeat;"
			counter_div_style += "text-align:center;width:65px;height:65px;";

			/*Initialize Loki db for bs,ss,sector,line,polygon*/
			// Create the database:
			var db = new loki('loki.json');
			
			// Create a collection:
			all_devices_loki_db = db.addCollection('allDevices');

			/*Show The loading Icon*/
			$("#loadingIcon").show();


            // Google maps mousemove event, triggers when map mouse move on google maps
            google.maps.event.addListener(mapInstance, 'mousemove', function (event) {
                displayCoordinates(event.latLng);

                if(is_ruler_active === 1) {
					if(ruler_pt_count == 1) {
						if(!temp_line) {
							var line_path = [
								ruler_array[0].getPosition(),
								event.latLng,
							];
							temp_line = new google.maps.Polyline({
								path 			: 	line_path,
								clickable 		: 	false,
								strokeColor 	: 	ruler_line_color,
								strokeOpacity	: 	1.0,
								strokeWeight	: 	3,
								pointType 		: 	"path",
								geodesic		: 	true,
								map 			: 	mapInstance
							});
						} else {
							var line_path = [
								ruler_array[0].getPosition(),
								event.latLng,
							];
							temp_line.setPath(line_path);
						}
					}
	        	}
            });

            // Google maps idle event
            google.maps.event.addListener(mapInstance, 'idle', function() {
            	if(isDebug) {
					console.log("Google Map Idle Event");
					var start_date_idle = new Date();
				}

        		// Save current zoom value in global variable
            	current_zoom = mapInstance.getZoom();
            	
            	/* When zoom level is greater than 8 show lines */
            	if(mapInstance.getZoom() > 7) {

            		isPerfCallStopped = 0;

        			var states_with_bounds = state_lat_lon_db.where(function(obj) {
            			return mapInstance.getBounds().contains(new google.maps.LatLng(obj.lat,obj.lon))
            		});

            		if(states_with_bounds.length > 0 || mapInstance.getZoom() < 13 || searchResultData.length > 0) {

	            		var states_array = [];

	            		// Hide State Labels which are in current bounds
	            		for(var i=states_with_bounds.length;i--;) {
	            			if(state_wise_device_labels[states_with_bounds[i].name]) {
	            				states_array.push(states_with_bounds[i].name);
		            			if(!(state_wise_device_labels[states_with_bounds[i].name].isHidden_)) {
			            			// Hide Label
									state_wise_device_labels[states_with_bounds[i].name].hide();
		            			}
	            			}
	            		}

	            		// var plottable_data = searchResultData.length > 0 ? searchResultData : JSON.parse(JSON.stringify(gmap_self.updateStateCounter_gmaps(true))),
	            		var plottable_data = searchResultData.length > 0 ? searchResultData : gmap_self.updateStateCounter_gmaps(true),
	            			current_bound_devices = [],
							data_to_plot = [];

        				// IF any states exists
        				if(states_array.length > 0) {
            				for(var i=plottable_data.length;i--;) {
								var current_bs = plottable_data[i];
								if(states_array.indexOf(current_bs.state) > -1) {
									current_bound_devices.push(current_bs);
								}
            				}
        				} else {
        					current_bound_devices = plottable_data;
        				}


        				data_to_plot = current_bound_devices;

	            		var inBoundData = [];
	            		// If any data exists
	            		if(data_to_plot.length > 0) {
	            			main_devices_data_gmaps = data_to_plot;
	            			/**
							 * If anything searched n user is on zoom level 11 then reset 
							 * currentlyPlottedDevices array for removing duplicacy.
	            			 */
	            			if(mapInstance.getZoom() == 12 && searchResultData.length > 0) {
	            				// Reset currentlyPlottedDevices array
	            				currentlyPlottedDevices = [];
            				}

	            			if(currentlyPlottedDevices.length === 0) {
			            		// Clear map markers & reset variables
								gmap_self.clearMapMarkers();
								
								inBoundData = gmap_self.getInBoundDevices(data_to_plot);
								// Assign currently plotted devices to global array.
								currentlyPlottedDevices = inBoundData;
	            			} else {
	            				inBoundData = gmap_self.getNewBoundsDevices();
            					// Update currently plotted devices global array.
	            				currentlyPlottedDevices = currentlyPlottedDevices.concat(inBoundData);
	            			}

	            			// Call function to plot devices on gmap
							gmap_self.plotDevices_gmap(inBoundData,"base_station");

							// if(searchResultData.length == 0 || mapInstance.getZoom() <= 10) {
							if(mapInstance.getZoom() <= 12) {
								var polylines = allMarkersObject_gmap['path'],
									polygons = allMarkersObject_gmap['sector_polygon'],
									ss_markers = allMarkersObject_gmap['sub_station'],
									show_ss_len = $("#showAllSS").length > 0 ? $("#showAllSS:checked").length : 1;

								// Hide polylines if shown
								for(key in polylines) {
									var current_line = polylines[key];
									// If shown
									if(current_line.map) {
										current_line.setMap(null);
									}
								}

								// Hide polygons if shown
								for(key in polygons) {
									var current_polygons = polygons[key];
									// If shown
									if(current_polygons.map) {
										current_polygons.setMap(null);
									}
								}

								// Remove CROSS info label
							    for (key in cross_label_array) {
							    	cross_label_array[key].setVisible(false);
							    }

							    // Hide SS if show ss checkbox is unchecked
								for(key in ss_markers) {
									var current_ss = ss_markers[key];
									if(show_ss_len <= 0) {
										// If shown
										if(current_ss.map) {
											current_ss.setMap(null);
										}
									}
								}


							} else {
								gmap_self.showBaseStaionsInBounds(function() {
									gmap_self.showSectorDevicesInBounds(function() {
										gmap_self.showSectorPolygonInBounds(function() {
											gmap_self.showSubStaionsInBounds(function() {
												gmap_self.showLinesInBounds(function() {
													// console.log("All Shown");
												});
											});
										});
									});
								});
							}
	            		}
	            		// Show points line if exist
	            		for(key in line_data_obj) {
	            			if(!line_data_obj[key].map) {
	            				line_data_obj[key].setMap(mapInstance);
	            			}
	            		}
            		// 8 LEVEL ZOOM CONDITION
            		} else {
						gmap_self.showBaseStaionsInBounds(function() {
							gmap_self.showSectorDevicesInBounds(function() {
								gmap_self.showSectorPolygonInBounds(function() {
									gmap_self.showSubStaionsInBounds(function() {
										gmap_self.showLinesInBounds(function() {
											// console.log("All Shown");
										});
									});
								});
							});
						});
            		}
            		
            		// Start Performance API calling
            		if(isPerfCallStopped == 0 && isPerfCallStarted == 0) {
						var bs_id_list = getMarkerInCurrentBound();
		            	if(bs_id_list.length > 0 && isCallCompleted == 1) {
		            		gisPerformanceClass.start(bs_id_list);
		            	}
            		} else {
        				// also used in case of panning
            			var existing_bs_ids = convertChunksToNormalArray(current_bs_list),
	                		new_bs = gisPerformanceClass.get_intersection_bs(existing_bs_ids,getMarkerInCurrentBound(true));

	                	if(new_bs.length > 0) {
	                		var chunk_size = periodic_poll_process_count,
	                			new_bs_chunks = createArrayChunks(new_bs, chunk_size);

	                		if(!callsInProcess) {
	                			// Clear performance calling timeout
								if(recallPerf != "") {
			            			clearTimeout(recallPerf);
			            			recallPerf = "";
			            		}
	                			gisPerformanceClass.start(new_bs_chunks);
	                		} else {
	                			// Create Exisiting ids chunks
	                			current_bs_list = createArrayChunks(existing_bs_ids,chunk_size);
	                			// Concat new bs id with the existings
	                			current_bs_list = current_bs_list.concat(new_bs_chunks);
	                			// Update bsNamesList data
	                			gisPerformanceClass.bsNamesList = current_bs_list;
	                			last_counter_val += 1
	                			// sendRequest with last_counter_val
	                			gisPerformanceClass.sendRequest(last_counter_val);
	                		}
	                	}
            		}

	            } else if(mapInstance.getZoom() <= 7) {
	        		
	        		// Show only country counter below 4 level zoom
	        		gmap_self.hideStateCountersLabel();

	        		// Clear map markers & reset variables
					gmap_self.clearMapMarkers();

	        		if(mapInstance.getZoom() <= 4) {
	            		// Hide State Labels which are in current bounds
	            		var country_click_event = "onClick='gmap_self.state_label_clicked(0)'",
	            			total_devices_count = gmap_self.getCountryWiseCount();
            			var country_label_box = new InfoBox({
				            content: "<div "+country_click_event+" style='"+counter_div_style+"'><p style='position:relative;padding-top:24px;font-weight:bold;' title='Load India Data.'>"+total_devices_count+"</p></div>",
				            boxStyle: {
				                textAlign: "center",
				                fontSize: "8pt",
				                color: "black",
				                width : "100px"
				            },
				            disableAutoPan: true,
				            position: new google.maps.LatLng(24.2870,77.7832),
				            closeBoxURL: "",
				            enableEventPropagation: true,
				            zIndex: 80
				        });
				        if(country_label["india"] != "") {
				        	country_label["india"].close();
				        	country_label["india"] = "";
				        }
			        	country_label_box.open(mapInstance);
			        	country_label["india"] = country_label_box;
            		} else {
            			if(country_label["india"] != "") {
            				country_label["india"].hide();
				        	country_label["india"].close();
				        	country_label["india"] = "";
				        }
						
						// Clear performance calling timeout
						if(recallPerf != "") {
	            			clearTimeout(recallPerf);
	            			recallPerf = "";
	            		}
            			// Set Flag
            			isPerfCallStopped = 1;
            			isPerfCallStarted = 0;

            			// Reset Performance variables
            			gisPerformanceClass.resetVariable();

						var states_with_bounds = state_lat_lon_db.where(function(obj) {
	            			return mapInstance.getBounds().contains(new google.maps.LatLng(obj.lat,obj.lon))
	            		});
						for(var i=states_with_bounds.length;i--;) {
							if(state_wise_device_labels[states_with_bounds[i].name]) {
								if(state_wise_device_labels[states_with_bounds[i].name].isHidden_) {
									state_wise_device_labels[states_with_bounds[i].name].show();
								}
							}
						}

						state_lat_lon_db.where(function(obj) {
							if(state_wise_device_labels[obj.name]) {
								state_wise_device_labels[obj.name].show();return ;
							}
						});

						// Hide points line if exist
	            		for(key in line_data_obj) {
	            			if(line_data_obj[key].map) {
	            				line_data_obj[key].setMap(null);
	            			}
	            		}
            		}
	            }

	            // Save last Zoom Value
	            lastZoomLevel = mapInstance.getZoom();
	            if(isDebug) {
	            	var time_diff = (new Date().getTime() - start_date_idle.getTime())/1000;
					console.log("Google Map Idle Event End Time :- "+ time_diff + "Seconds");
					console.log("*************************************");
					start_date_idle = "";
				}
            });

			/*Search text box object*/
			var searchTxt = document.getElementById('google_loc_search');

			/*google search object for search text box*/
			var searchBox = new google.maps.places.SearchBox(searchTxt);

			/*Event listener for search text box*/
			google.maps.event.addListener(searchBox, 'places_changed', function() {
				/*place object returned from map API*/
	    		var places = searchBox.getPlaces();
	            if (places.length == 0) {
	            	return;
	            }

	            for (var i = 0, marker; marker = place_markers[i]; i++) {
	            	marker.setMap(null);
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
	            var listener = google.maps.event.addListenerOnce(mapInstance, 'bounds_changed', function(event) {
	            	/*check for current zoom level*/
	            	if(mapInstance.getZoom() >= 15) {
	            		mapInstance.setZoom(15);
	            	}

	            	google.maps.event.removeListener(listener);

			    	// searchResultData = JSON.parse(JSON.stringify(gmap_self.updateStateCounter_gmaps(true)));
			    	searchResultData = gmap_self.updateStateCounter_gmaps(true);
	            });
	        });


			var fullScreenCustomDiv = document.createElement('div'),
				fullScreenCustomControl = new FullScreenCustomControl(fullScreenCustomDiv, mapInstance);

			fullScreenCustomDiv.index = 1;
			mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].push(fullScreenCustomDiv);

			
			/*Add Full Screen Control*/
			mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].push(new FullScreenControl(mapInstance));

			/*Create performance lib instance*/
            gisPerformanceClass= new GisPerformance();

			/*Create a instance of OverlappingMarkerSpiderfier*/
			oms = new OverlappingMarkerSpiderfier(mapInstance,{markersWontMove: true, markersWontHide: true, keepSpiderfied: true});
            oms_ss = new OverlappingMarkerSpiderfier(mapInstance,{markersWontMove: true, markersWontHide: true, keepSpiderfied: true});

            // Update The usual n highlihted colors of OverlappingMarkerSpiderfier
            var oms_legends = oms.legColors,
            	oms_ss_legends = oms_ss.legColors;

        	// For BS OMS
            for(key1 in oms_legends) {
            	var MapTypes = oms_legends[key1];
            	for(key2 in MapTypes) {
            		MapTypes[key2] = "";
            	}
            }
            // For SS OMS
            for(key1 in oms_ss_legends) {
            	var MapTypes = oms_ss_legends[key1];
            	for(key2 in MapTypes) {
            		MapTypes[key2] = "";
            	}
            }
            
            prepare_oms_object(oms);
            prepare_oms_object(oms_ss);

			/*Create a instance of google map info window*/
			infowindow = new google.maps.InfoWindow({zIndex:800});

			// 1*1 icon obj
			hiddenIconImageObj = new google.maps.MarkerImage(
				base_url+'/static/img/icons/1x1.png',
				null,
				null,
				null,
				new google.maps.Size(1,1)
			);

		} else {
			$.gritter.add({
	            // (string | mandatory) the heading of the notification
	            title: 'Google Maps',
	            // (string | mandatory) the text inside the notification
	            text: 'No Internet Access',
	            // (bool | optional) if you want it to fade out on its own or just sit there
	            sticky: true
	        });
		}
	};

	/**
	 * This function fetch device inventory from server
	 * @method getDevicesData_gmap
	 */
	this.getDevicesData_gmap = function() {

		if(isDebug) {
			console.log("Device Fetch API Function");
		}

		if(counter > 0 || counter == -999) {
			if(isDebug) {
				var start_date_api = new Date();
			}
			/*Ajax call to the API*/
			$.ajax({
				url : base_url+"/"+"device/stats/?total_count="+devicesCount+"&page_number="+hitCounter,
				type : "GET",
				dataType : "json",
				/*If data fetched successful*/
				success : function(response) {
					if(isDebug) {
						var time_diff = (new Date().getTime() - start_date_api.getTime())/1000;
						console.log("Ajax End Time :- "+ time_diff +" Seconds");
						console.log("*******************************************");
						start_date_api = "";
					}

					var result = "";
					// Type check of response
					if(typeof response == 'string') {
						result = JSON.parse(response);
					} else {
						result = response;
					}

					if(result.success == 1) {
						if(result.data.objects) {
							hitCounter = hitCounter + 1;
							main_devices_data_gmaps = main_devices_data_gmaps.concat(result.data.objects.children);

							data_for_filters = main_devices_data_gmaps;

							/*Update device count with the received data*/
							if(devicesCount == 0) {
								devicesCount = result.data.meta.total_count;
							}

							/*Update showLimit with the received data*/
							showLimit = result.data.meta.limit;

							if(counter == -999) {
								counter = Math.ceil(devicesCount / showLimit);
							}

							gmap_self.showStateWiseData_gmap(result.data.objects.children);

                    		/*Decrement the counter*/
							counter = counter - 1;

							/*Call the function after 10 ms for lazyloading*/
							setTimeout(function() {
								gmap_self.getDevicesData_gmap();
							},10);
						} else {
							
							isCallCompleted = 1;
							disableAdvanceButton('no');
							gmap_self.showStateWiseData_gmap([]);
							// Hide loading spinner
        					hideSpinner();
						}
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
				},
				always : function() {

					disableAdvanceButton('no');

					/*Load tools(point,line) data*/
					gmap_self.get_tools_data_gmap();

					/*Hide The loading Icon*/
					$("#loadingIcon").hide();

					// Hide loading spinner
					hideSpinner();

					/*Recall the server after particular timeout if system is not freezed*/
					setTimeout(function(e){
						gmap_self.recallServer_gmap();
					},21600000);
				}
			});
		} else {

			disableAdvanceButton('no, enable it.');
			
			/*Load tools(point,line) data*/
			gmap_self.get_tools_data_gmap();

			gmap_self.create_old_ruler();
			get_page_status();
			
			/*Ajax call not completed yet*/
			isCallCompleted = 1;
			
			// gmap_self.plotDevices_gmap([],"base_station");
			gmap_self.showStateWiseData_gmap([]);

			// Hide loading spinner
			hideSpinner();

			/*Recall the server after particular timeout if system is not freezed*/
			setTimeout(function(e){
				gmap_self.recallServer_gmap();
			},21600000);
		}
	};

	/**
     * This function show state wise data(BS + SS) counter on gmap
     * @method showStateWiseData_gmap
     * @param dataset {Object} In case of BS, it is the devies object array & for SS it 
       contains BS marker object with SS & sector info
	 */
	this.showStateWiseData_gmap = function(dataset) {
		if(isDebug) {
			console.log("State Wise Clusters Function")
			var start_date_state = new Date();
		}

		//Loop For Base Station
		for(var i=dataset.length;i--;) {

			var current_bs = dataset[i],
				state = current_bs['state'] && na_items_list.indexOf(current_bs['state'].toLowerCase()) == -1 ? $.trim(current_bs['state']) : '',
				city = current_bs['city'] && na_items_list.indexOf(current_bs['city'].toLowerCase()) == -1  ? $.trim(current_bs['city']) : '';

			/*Create BS state,city object*/
			if(state) {

				state_city_obj[state] = state_city_obj[state] ? state_city_obj[state] : [];
				if(state_city_obj[state].indexOf(city) == -1) {
					state_city_obj[state].push(city);
				}
			}

			if(city) {
				if(all_cities_array.indexOf(city) == -1) {
					all_cities_array.push(city); 
				}
			}

			var sectors_data = current_bs.sectors ? current_bs.sectors : [],
				lat = current_bs.lat ? current_bs.lat : '',
				lon = current_bs.lon ? current_bs.lon : '',
				update_state_str = state ? $.trim(state) : "",
				state_list = state_lat_lon_db.find({"name" : update_state_str}),
				state_lat_lon_obj = state_list.length > 0 ? state_list[0] : false,
				state_param = state_lat_lon_obj ? JSON.stringify(state_lat_lon_obj) : false,
				state_click_event = "onClick='gmap_self.state_label_clicked("+state_param+")'";

			// If state is not null
			if(state) {
				var state_cluster_html = "<div "+state_click_event+" style='"+counter_div_style+"'> \
										 <p style='position:relative;padding-top:24px;font-weight:bold;' \
										 title='Load "+state+" Data.'> \
										 "+state_wise_device_counters[state]+"</p></div>";

				if(state_wise_device_counters[state]) {
					state_wise_device_counters[state] += 1;
					if(state_lat_lon_obj) {
						// Update the content of state counter label as per devices count
						state_wise_device_labels[state].setContent(state_cluster_html);
					}
				} else {
					state_wise_device_counters[state] = 1;
					if(state_lat_lon_obj) {
						var state_cluster_html = "<div "+state_click_event+" style='"+counter_div_style+"'> \
												 <p style='position:relative;padding-top:24px;font-weight:bold;' \
												 title='Load "+state+" Data.'> \
												 "+state_wise_device_counters[state]+"</p></div>";
						var device_counter_label = new InfoBox({
				            content: state_cluster_html,
				            boxStyle: {
				                textAlign: "center",
				                fontSize: "8pt",
				                color: "black",
				                width : "100px"
				            },
				            disableAutoPan: true,
				            position: new google.maps.LatLng(state_lat_lon_obj.lat, state_lat_lon_obj.lon),
				            closeBoxURL: "",
				            enableEventPropagation: true,
				            zIndex: 80
				        });
			        	device_counter_label.open(mapInstance);
					}

			        state_wise_device_labels[state] = device_counter_label;
				}
			} else {
				var allStateBoundries = state_boundries_db.data;

				// Loop to find that the lat lon of BS lies in which state.
				for(var y=allStateBoundries.length;y--;) {
					var current_state_boundries = allStateBoundries[y].boundries,
						current_state_name = allStateBoundries[y].name,
						latLonArray = [];

					if(current_state_boundries.length > 0) {
						for(var z=current_state_boundries.length;z--;) {
							latLonArray.push({
								lat: current_state_boundries[z].lat,
								lon: current_state_boundries[z].lon
							});
						}

						if(isPointInPoly(latLonArray, {lat: lat, lon: lon})) {
							//Update json with state name
							dataset[i]['state'] = current_state_name;
							state = current_state_name;
							
							var is_state_exists = state_lat_lon_db.find({"name" : state}).length > 0;

                            state_lat_lon_obj = is_state_exists ? state_lat_lon_db.find({"name" : state})[0] : false;
                            state_param = state_lat_lon_obj ? JSON.stringify(state_lat_lon_obj) : false;
                            state_click_event = "onClick='gmap_self.state_label_clicked("+state_param+")'";

							var new_lat_lon_obj = state_lat_lon_db.where(function(obj) {
								return obj.name === current_state_name;
							});

							var state_cluster_html = "<div "+state_click_event+" style='"+counter_div_style+"'> \
													 <p style='position:relative;padding-top:24px;font-weight:bold;' \
													 title='Load "+state+" Data.'> \
													 "+state_wise_device_counters[state]+"</p></div>";

							if(state_wise_device_counters[current_state_name]) {
								state_wise_device_counters[current_state_name] += 1;
								state_wise_device_labels[current_state_name].setContent(state_cluster_html);
							} else {
								state_wise_device_counters[current_state_name] = 1;
								var device_counter_label = new InfoBox({
						            content: state_cluster_html,
						            boxStyle: {
						                textAlign: "center",
						                fontSize: "8pt",
						                color: "black",
						                width : "100px"
						            },
						            disableAutoPan: true,
						            position: new google.maps.LatLng(new_lat_lon_obj[0].lat, new_lat_lon_obj[0].lon),
						            closeBoxURL: "",
						            enableEventPropagation: true,
						            zIndex: 80
						        });
					        	device_counter_label.open(mapInstance);
						        state_wise_device_labels[current_state_name] = device_counter_label;
							}

							// Break for loop if state found
							break;
						}
					}
				}
			}

			/*Insert devices object to loki db variables*/
			if(isApiResponse === 1) {
				all_devices_loki_db.insert(dataset[i]);
			}

			//Loop For Sector Devices
			for(var j=sectors_data.length;j--;) {

				var total_ss = sectors_data[j]['sub_stations'] ? sectors_data[j]['sub_stations'].length : 0;
				state_wise_device_counters[state] += total_ss;

				if(state_lat_lon_obj) {
					var state_cluster_html = "<div "+state_click_event+" style='"+counter_div_style+"'> \
											 <p style='position:relative;padding-top:24px;font-weight:bold;' \
											 title='Load "+state+" Data.'> \
											 "+state_wise_device_counters[state]+"</p></div>";
					// Update the content of state counter label as per devices count
					state_wise_device_labels[state].setContent(state_cluster_html);
				}

				var sector_tech = sectors_data[j]['technology'],
					sector_vendor = sectors_data[j]['vendor'];
				if (sector_tech != 'NA') {
					tech_vendor_obj[sector_tech] = tech_vendor_obj[sector_tech] ? tech_vendor_obj[sector_tech] : [];
					if(sector_vendor != 'NA' && tech_vendor_obj[sector_tech].indexOf(sector_vendor) == -1) {
						tech_vendor_obj[sector_tech].push(sector_vendor);
					}

					if(sector_vendor != 'NA' && all_vendor_array.indexOf(sector_vendor) == -1) {
						all_vendor_array.push(sector_vendor); 
					}
				}
			}
		}

		if(isCallCompleted == 1) {
			/*Hide The loading Icon*/
			$("#loadingIcon").hide();
			
			if(isFirstTime == 1) {
				/*Load data for basic filters*/
				gmap_self.getBasicFilters();
			}
		}

		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_state.getTime())/1000;
			console.log("State Cluster Plotting End Time :- "+ time_diff + " Seconds");
			console.log("*******************************************");
			start_date_state = "";
		}
	};

	/**
	 * This function hides all the state counter labels
	 * @method hideStateCountersLabel
	 */
	this.hideStateCountersLabel = function() {
		var states_with_bounds = state_lat_lon_db.where(function(obj) {
			return mapInstance.getBounds().contains(new google.maps.LatLng(obj.lat,obj.lon))
		});

		var states_array = [];

		// Hide State Labels which are in current bounds
		for(var i=states_with_bounds.length;i--;) {
			if(state_wise_device_labels[states_with_bounds[i].name]) {
				states_array.push(states_with_bounds[i].name);
    			if(!(state_wise_device_labels[states_with_bounds[i].name].isHidden_)) {
        			// Hide Label
					state_wise_device_labels[states_with_bounds[i].name].hide();
    			}
			}
		}
	};

	/**
	 * This function hides all the state counter labels
	 * @method showStateCountersLabel
	 */
	this.showStateCountersLabel = function() {
		var states_with_bounds = state_lat_lon_db.where(function(obj) {
			return mapInstance.getBounds().contains(new google.maps.LatLng(obj.lat,obj.lon))
		});

		var states_array = [];

		// Hide State Labels which are in current bounds
		for(var i=states_with_bounds.length;i--;) {
			if(state_wise_device_labels[states_with_bounds[i].name]) {
				states_array.push(states_with_bounds[i].name);
    			if(state_wise_device_labels[states_with_bounds[i].name].isHidden_) {
        			// Hide Label
					state_wise_device_labels[states_with_bounds[i].name].show();
    			}
			}
		}
	};

	/**
	 * This function trigger when state label is clicked & loads the state wise data.
	 * @method state_label_clicked
	 * @param state_obj, It contains the name of state which is clicked.
	 */
	this.state_label_clicked = function(state_obj) {
		if(isDebug) {
			console.log("State Label Clicked Function")
			var start_date_state_click = new Date();
		}
		if(isExportDataActive == 0) {
			if(state_obj == 0) {
				if(window.location.pathname.indexOf("gearth") > -1) {

				} else if(window.location.pathname.indexOf("wmap") > -1) {
					ccpl_map.setCenter(
						new OpenLayers.LonLat(india_center_lon, india_center_lat), // Center Lon-Lat 
						1 // Zoom Level
					);
				} else {
					mapInstance.setCenter(new google.maps.LatLng(india_center_lat,india_center_lon));
					mapInstance.setZoom(5);
				}
			} else {
				var clicked_state = state_obj ? state_obj.name : "",
					selected_state_devices = [];
				if(clicked_state) {
					//Zoom in to selected state
					if(window.location.pathname.indexOf("gearth") > -1) {
				        // Pass
				    } else if(window.location.pathname.indexOf("wmap") > -1) {
						ccpl_map.setCenter(
							new OpenLayers.LonLat(state_obj.lon, state_obj.lat),
							whiteMapSettings.zoomLevelAtWhichStateClusterExpands
						);
					} else {
						mapInstance.fitBounds(new google.maps.LatLngBounds(new google.maps.LatLng(state_obj.lat,state_obj.lon)));
						mapInstance.setZoom(8);
					}

					// Hide Clicked state Label
					if(!(state_wise_device_labels[clicked_state].isHidden_)) {
	        			// Hide Label

						if(window.location.pathname.indexOf("gearth") > -1) {
				        
				    	} else if(window.location.pathname.indexOf("wmap") > -1) {
							hideOpenLayerFeature(state_wise_device_labels[clicked_state]);
							state_wise_device_labels[clicked_state].layer.redraw();
						} else {
							state_wise_device_labels[clicked_state].hide();	
						}
	    			}
				}
			}
		}

		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_state_click.getTime())/1000;
			console.log("State Label Clicked End Time :- "+ time_diff + "Seconds");
			console.log("*****************************************");
			start_date_state_click = "";
		}
	};

	/**
	 * This function removes unmatched sectors from given data set as per applied filters(basic or advance).
	 * @method getFilteredBySectors
	 * @param dataset {Array}, It contains the bs-sector-ss hierarchy wise devices array.
	 */
	this.getFilteredBySectors = function(dataset) {
		if(isDebug) {
			console.log("Filter By Sector Function")
			var start_date_sector_filter = new Date();
		}

		var complete_filtering_data = gmap_self.getSelectedFilteringItems(),
			technology_filter = complete_filtering_data["advance"]["technology"],
			vendor_filter = complete_filtering_data["advance"]["vendor"],
			frequency_filter = complete_filtering_data["advance"]["frequency"],
			polarization_filter = complete_filtering_data["advance"]["polarization"];

		var dataset_clone = dataset;
		// Remove unmatched sectors
		for(var x=0;x<dataset_clone.length;x++) {
			var bs_sectors = dataset_clone[x].sectors,
				correct_sectors = [];

			// Loop for BS sectors
			for(var y=0;y<bs_sectors.length;y++) {
				var sector_technology = $.trim(bs_sectors[y].technology.toLowerCase()),
					sector_vendor = $.trim(bs_sectors[y].vendor.toLowerCase()),
					sector_frequency_1 = $.trim(bs_sectors[y].freq),
					sector_frequency_2 = "",
					sector_polarization = bs_sectors[y].polarization ? $.trim(bs_sectors[y].polarization.toLowerCase()) : "";

				if(technology_filter.length > 0 || vendor_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0) {
					var advance_filter_condition1 = technology_filter.length > 0 ? technology_filter.indexOf(sector_technology) > -1 : true,
						advance_filter_condition2 = vendor_filter.length > 0 ? vendor_filter.indexOf(sector_vendor) > -1 : true,
						frequency_filter_condition = frequency_filter.indexOf(sector_frequency_1) > -1,
						advance_filter_condition3 = frequency_filter.length > 0 ? frequency_filter_condition : true,
						advance_filter_condition4 = polarization_filter.length > 0 ? polarization_filter.indexOf(sector_polarization) > -1 : true;

					if(advance_filter_condition1 && advance_filter_condition2 && advance_filter_condition3 && advance_filter_condition4) {
						if($.trim($("#technology").val()).length > 0 || $.trim($("#vendor").val()).length > 0) {
							var basic_filter_technology = $.trim($("#technology").val()).length > 0 ? $.trim($("#technology option:selected").text()) : false,
								basic_filter_vendor = $.trim($("#vendor").val()).length > 0 ? $.trim($("#vendor option:selected").text()) : false,
								basic_filter_condition1 = basic_filter_technology ? $.trim(basic_filter_technology.toLowerCase()) == $.trim(sector_technology.toLowerCase()) : true,
								basic_filter_condition2 = basic_filter_vendor ? $.trim(basic_filter_vendor.toLowerCase()) == $.trim(sector_vendor.toLowerCase()) : true;
							// If condition matches
							if(basic_filter_condition1 && basic_filter_condition2) {
								correct_sectors.push(bs_sectors[y]);
							}
						}  else {
							correct_sectors.push(bs_sectors[y]);
						}
					}

				} else {
					if($.trim($("#technology").val()).length > 0 || $.trim($("#vendor").val()).length > 0) {
						var basic_filter_technology = $.trim($("#technology").val()).length > 0 ? $.trim($("#technology option:selected").text()) : false,
							basic_filter_vendor = $.trim($("#vendor").val()).length > 0 ? $.trim($("#vendor option:selected").text()) : false,
							basic_filter_condition1 = basic_filter_technology ? $.trim(basic_filter_technology.toLowerCase()) == $.trim(sector_technology.toLowerCase()) : true,
							basic_filter_condition2 = basic_filter_vendor ? $.trim(basic_filter_vendor.toLowerCase()) == $.trim(sector_vendor.toLowerCase()) : true;

						// If condition matches
						if(basic_filter_condition1 && basic_filter_condition2) {
							correct_sectors.push(bs_sectors[y]);
						}
					}
				}
			}
			// Update BS sectors.
			dataset_clone[x].sectors = correct_sectors;
		}

		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_sector_filter.getTime())/1000;
			console.log("Filter By Sector End Time :- "+ time_diff + " Seconds");
			console.log("************************************");
			start_date_sector_filter = "";
		}
		// Return the updated dataset.
		return dataset_clone;
	};

	/**
	 * This function get the filtered data from lokidb instance as per the applied filters(basic or advance).
	 * @method getFilteredData_gmap
	 */
	this.getFilteredData_gmap = function() {

		if(isDebug) {
			console.log("Filter Data Function")
			var start_date_filtered = new Date();
		}

		var complete_filtering_data = gmap_self.getSelectedFilteringItems(),
			technology_filter = complete_filtering_data["advance"]["technology"],
			vendor_filter = complete_filtering_data["advance"]["vendor"],
			city_filter = complete_filtering_data["advance"]["city"],
			state_filter = complete_filtering_data["advance"]["state"],
			frequency_filter = complete_filtering_data["advance"]["frequency"],
			polarization_filter = complete_filtering_data["advance"]["polarization"],
			filterObj = complete_filtering_data["basic"],
			isAdvanceFilterApplied = technology_filter.length > 0 || vendor_filter.length > 0 || state_filter.length > 0 || city_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0,
			isBasicFilterApplied = $.trim($("#technology").val()).length > 0 || $.trim($("#vendor").val()).length > 0 || $.trim($("#state").val()).length > 0 || $.trim($("#city").val()).length > 0;

		var filtered_Data = all_devices_loki_db.where(function(obj) {

			var bs_city = obj.city ? $.trim(obj.city.toLowerCase()) : "",
				bs_state = obj.state ? $.trim(obj.state.toLowerCase()) : "",
				sectors = obj.sectors,
				basic_filter_condition1 = filterObj['state'] != 'Select State' ? bs_state == $.trim(filterObj['state'].toLowerCase()) : true,
				basic_filter_condition2 = filterObj['city'] != 'Select City' ? bs_city == $.trim(filterObj['city'].toLowerCase()) : true,
				advance_filter_condition1 = state_filter.length > 0 ? state_filter.indexOf(bs_state) > -1 : true,
				advance_filter_condition2 = city_filter.length > 0 ? city_filter.indexOf(bs_city) > -1 : true;

        	// If any basic filter is applied
        	if(isBasicFilterApplied) {
    			var isCorrect = false;
        		if($.trim($("#technology").val()).length > 0 || $.trim($("#vendor").val()).length > 0) {
        			if(!isCorrect) {
        				// Loop sectors
						for(var i=sectors.length;i--;) {
							var sector_tech = sectors[i].technology ? $.trim(sectors[i].technology.toLowerCase()) : "",
								sector_vendor = sectors[i].vendor ? $.trim(sectors[i].vendor.toLowerCase()) : "",
								basic_filter_condition3 = $.trim($("#technology").val()).length > 0 ? sector_tech ==  filterObj['technology'].toLowerCase() : true,
								basic_filter_condition4 = $.trim($("#vendor").val()).length > 0 ? sector_vendor ==  filterObj['vendor'].toLowerCase() : true;

							if(
								basic_filter_condition1
								&&
								basic_filter_condition2
								&&
								basic_filter_condition3
								&&
								basic_filter_condition4
							) {
								// If advance Filters Applied
								if(isAdvanceFilterApplied) {

									var sector_frequency_1 = sectors[i].freq ? $.trim(sectors[i].freq) : "",
										sector_frequency_2 = "",
										frequency_filter_condition = frequency_filter.indexOf(sector_frequency_1) > -1,
										sector_polarization = sectors[i].polarization ? $.trim(sectors[i].polarization.toLowerCase()) : "",
										advance_filter_condition3 = technology_filter.length > 0 ? technology_filter.indexOf(sector_tech) > -1 : true,
						                advance_filter_condition4 = vendor_filter.length > 0 ? vendor_filter.indexOf(sector_vendor) > -1 : true,
						            	advance_filter_condition5 = frequency_filter.length > 0 ? frequency_filter_condition : true,
						            	advance_filter_condition6 = polarization_filter.length > 0 ? polarization_filter.indexOf(sector_polarization) > -1 : true;

						            if(
						            	advance_filter_condition1
						            	&&
						            	advance_filter_condition2
						            	&&
						            	advance_filter_condition3
						            	&&
						            	advance_filter_condition4
						            	&&
						            	advance_filter_condition5
						            	&&
						            	advance_filter_condition6
					            	) {
						                isCorrect = true;
						                break;
						            }
								} else {
									// return true;
					                isCorrect = true;
					                break;
								}
							}
						}
        			}
        			// Return isCorrect
					return isCorrect;
        		} else {
        			if(basic_filter_condition1 && basic_filter_condition2) {
        				var isCorrect = false;
        				// If advance Filters Applied
						if(isAdvanceFilterApplied) {
		        			if(!isCorrect) {
		        				if(
		        					technology_filter.length > 0
		        					||
		        					vendor_filter.length > 0
		        					||
		        					frequency_filter.length > 0
		        					||
		        					polarization_filter.length > 0
	        					) {
					        		for(var i=0;i<sectors.length;i++) {

					        			var sector_frequency_1 = sectors[i].freq ? $.trim(sectors[i].freq) : "",
											frequency_filter_condition = frequency_filter.indexOf(sector_frequency_1) > -1,
											advance_filter_condition3 = technology_filter.length > 0 ? technology_filter.indexOf(sectors[i].technology.toLowerCase()) > -1 : true,
							                advance_filter_condition4 = vendor_filter.length > 0 ? vendor_filter.indexOf(sectors[i].vendor.toLowerCase()) > -1 : true,
							            	advance_filter_condition5 = frequency_filter.length > 0 ? frequency_filter_condition : true,
							            	advance_filter_condition6 = polarization_filter.length > 0 ? polarization_filter.indexOf(sectors[i].orientation.toLowerCase()) > -1 : true;

							            if(
							            	advance_filter_condition1
							            	&&
							            	advance_filter_condition2
							            	&&
							            	advance_filter_condition3
							            	&&
							            	advance_filter_condition4
							            	&&
							            	advance_filter_condition5
							            	&&
							            	advance_filter_condition6
						            	) {
							                isCorrect = true;
					                		break;
							            }
						            }
						            return isCorrect;
								} else {
									if(advance_filter_condition1 && advance_filter_condition2) {
						                return true
						            } else {
						                return false;
						            }
								}
		        			} else {
		        				return isCorrect;
		        			}
						} else {
							return true;
						}
        			} else {
        				return false;
        			}
        		}
        	} else if(isAdvanceFilterApplied) {
        		var isCorrect = false;
				if(
					technology_filter.length > 0
					||
					vendor_filter.length > 0
					||
					frequency_filter.length > 0
					||
					polarization_filter.length > 0
				) {
        			if(!isCorrect) {
		        		for(var i=0;i<sectors.length;i++) {

		        			var sector_frequency_1 = sectors[i].freq ? $.trim(sectors[i].freq) : "",
								sector_frequency_2 = "",
								frequency_filter_condition = frequency_filter.indexOf(sector_frequency_1) > -1,
								advance_filter_condition3 = technology_filter.length > 0 ? technology_filter.indexOf(sectors[i].technology.toLowerCase()) > -1 : true,
				                advance_filter_condition4 = vendor_filter.length > 0 ? vendor_filter.indexOf(sectors[i].vendor.toLowerCase()) > -1 : true,
				            	advance_filter_condition5 = frequency_filter.length > 0 ? frequency_filter_condition : true,
				            	advance_filter_condition6 = polarization_filter.length > 0 ? polarization_filter.indexOf(sectors[i].polarization.toLowerCase()) > -1 : true;

				            if(
				            	advance_filter_condition1
				            	&&
				            	advance_filter_condition2
				            	&&
				            	advance_filter_condition3
				            	&&
				            	advance_filter_condition4
				            	&&
				            	advance_filter_condition5
				            	&&
				            	advance_filter_condition6
			            	) {
				                isCorrect = true;
				                break;
			                }
			            }
        			}
		            return isCorrect;
				} else {
					if(advance_filter_condition1 && advance_filter_condition2) {
		                return true
		            } else {
		                return false;
		            }
				}
        	} else {
        		return true;
        	}
    	});
		
		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_filtered.getTime())/1000;
			console.log("Filter Data End Time :- "+ time_diff + " Seconds");
			console.log("********************************");
			start_date_filtered = "";
		}
		return gmap_self.objDeepCopy_nocout(filtered_Data);
	};

	/**
	 * This function remove markers,labels,lines, etc. from gmap & reset variables
	 * @method clearMapMarkers
	 */
	this.clearMapMarkers = function() {
		// Remove perf info label
	    for (var x = 0; x < labelsArray.length; x++) {
	        labelsArray[x].close();
	    }

	    // Remove CROSS info label
	    for (key in cross_label_array) {
	        cross_label_array[key].close();
	    }

	    // Remove tooltip info label
	    for (key in tooltipInfoLabel) {
	        tooltipInfoLabel[key].close();
	    }

	    try {
	    	// Remove the loader
		    for (key in loader_icon_dict) {
		        loader_icon_dict[key].close();
		    }
	    } catch(e) {
	    	// console.log(e);
	    }
	    

        // Reset labels array 
        labelsArray = [];
        cross_label_array = {};
        tooltipInfoLabel = {};
        loader_icon_dict = {};

        // Clear base-stations
        gmap_self.toggleSpecificMarkers_gmap('base_station',null);
        // Clear sector device
        gmap_self.toggleSpecificMarkers_gmap('sector_device',null);
        // Clear sector polygon
        gmap_self.toggleSpecificMarkers_gmap('sector_polygon',null);
        // Clear sub-stations
        gmap_self.toggleSpecificMarkers_gmap('sub_station',null);
        // Clear link line
        gmap_self.toggleSpecificMarkers_gmap('path',null);

		// Reset Variables
		allMarkersArray_gmap = [];
		main_devices_data_gmaps = [];
		plottedBsIds = [];
		pollableDevices = [];
		sectorMarkersMasterObj = {};
		sectorMarkerConfiguredOn = [];
		currentlyPlottedDevices = [];
		allMarkersObject_gmap= {
			'base_station': {},
			'path': {},
			'sub_station': {},
			'sector_device': {},
			'sector_polygon': {},
			'backhaul' : {}
		};

		if (typeof nocout_getPerfTabDomId != 'undefined' && typeof live_data_tab != 'undefined') {
			all_devices_loki_db.data = [];
		}

		/*Clear master marker cluster objects*/
		if(masterClusterInstance) {
			masterClusterInstance.clearMarkers();
		}
	};

	/**
     * This function is used to get the devices which are in bound from given data set.
     * @method getInBoundDevices
     * @param dataset {Array}, It contains array of bs-sector-ss heirarchy devices.
     * @return inBoundDevices {Array}, It returns the devices which are in current bound.
	 */
	this.getInBoundDevices = function(dataset) {

		if(isDebug) {
			console.log("In Bound Devices Function");
			var start_date_inBound = new Date();
		}

		var inBoundDevices = [];

		for(var i=dataset.length;i--;) {

			var current_device_set = dataset[i],
				isBsDeviceInBound = "";
			if(window.location.pathname.indexOf("wmap")> -1) {
				isBsDeviceInBound = whiteMapClass.checkIfPointLiesInside({
					lon: current_device_set.lon,
					lat: current_device_set.lat
				});
			} else {
				isBsDeviceInBound = mapInstance.getBounds().contains(
					new google.maps.LatLng(
						current_device_set.lat,
						current_device_set.lon
					)
				);
			}
			if(isBsDeviceInBound) {
				inBoundDevices.push(current_device_set);
				plottedBsIds.push(current_device_set.bs_id);
			}
		}

		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_inBound.getTime())/1000;
			console.log("In Bound Devices End Time :- "+ time_diff + " Seconds");
			console.log("********************************");
			start_date_inBound = "";
		}
		// Return devices which are in current bounds
		return inBoundDevices;
	};

	/**
     * This function is used to get devices which are in changed bounds.
     * @method getNewBoundsDevices
     * @return newInBoundDevices {Array}, It returns the devices which are in current bound & not plotted yet.
	 */
	this.getNewBoundsDevices = function() {

		if(isDebug) {
			console.log("New Bound Devices Function");
			var start_date_new_inBound = new Date();
		}

		var newInBoundDevices = [];
		var main_devices_data = [];
		if(window.location.pathname.indexOf("wmap") > -1) {
			main_devices_data = main_devices_data_wmap;
		} else {
			main_devices_data = main_devices_data_gmaps;
		}

		for(var i=main_devices_data.length;i--;) {
			var current_device_set = main_devices_data[i];

			if(plottedBsIds.indexOf(current_device_set.bs_id) === -1) {
				var isDeviceInBound = "";
				if(window.location.pathname.indexOf("wmap") > -1) {
					isDeviceInBound = whiteMapClass.checkIfPointLiesInside({
						lon: current_device_set.lon,
						lat: current_device_set.lat
					});
				} else {
					isDeviceInBound = mapInstance.getBounds().contains(
						new google.maps.LatLng(
							current_device_set.lat,
							current_device_set.lon
						)
					);
				}
				if(isDeviceInBound) {
					newInBoundDevices.push(current_device_set);
					// Push plotted base-station id to global array
					plottedBsIds.push(current_device_set.bs_id);
				}
			}
		}
		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_new_inBound.getTime())/1000;
			console.log("New Bound Devices End Time :- "+ time_diff +" Seconds");
			console.log("************************************");
			start_date_new_inBound = "";
		}
		// Return devices which are in current bounds
		return newInBoundDevices;
	};

	/**
     * This function is used to plot BS or SS devices & their respective elements on the google maps
     * @method plotDevices_gmap
     * @param bs_ss_devices {Object} In case of BS, it is the devies object array & for SS it contains BS marker object with SS & sector info
     * @param stationType {String}, It contains that the points are for BS or SS.
	 */
	this.plotDevices_gmap = function(bs_ss_devices, stationType) {
		
		if(isDebug) {
			console.log("Plot Devices Function For "+bs_ss_devices.length+" devices.");
			var start_date_plot = new Date();
		}

		try {
			var hide_flag = !$("#show_hide_label")[0].checked;
		} catch(e) {
			var hide_flag = false;
		}

		for(var i=bs_ss_devices.length;i--;) {

			// BS marker url
			var fetched_bs_markerurl = bs_ss_devices[i]['icon_url'],
				bs_marker_url = fetched_bs_markerurl ? fetched_bs_markerurl : "static/img/icons/bs.png"; 

			// Flag to check if bs_icon with Exclamation mark is going to be displayed
			var pps_bs_image_filter = bs_ss_devices[i]['has_pps_alarm'] ? bs_ss_devices[i]['has_pps_alarm'] : 0;

			// BS marker icon obj
            var bs_marker_icon_obj = gmap_self.getMarkerImageBySize(
				base_url+"/"+bs_marker_url,
				"base_station" ,
				pps_bs_image_filter
			);

			var fetched_status = bs_ss_devices[i]['maintenance_status'],
				bs_maintenance_status = fetched_status ? $.trim(fetched_status) : "No",
				bs_lat = bs_ss_devices[i].lat,
				bs_lon = bs_ss_devices[i].lon,
				filter_info = {
	            	"bs_name" : bs_ss_devices[i].name,
	                "bs_id" : bs_ss_devices[i].bs_id
	            };

			/*Create BS Marker Info Object*/
			var bs_marker_object = getMarkerInfoJson(bs_ss_devices[i], 'base_station', filter_info);

			// Update map specific info
			bs_marker_object['position'] = new google.maps.LatLng(bs_lat, bs_lon);
			bs_marker_object['icon'] = bs_marker_icon_obj;
			bs_marker_object['oldIcon'] = bs_marker_icon_obj;
			bs_marker_object['clusterIcon'] = bs_marker_icon_obj;
			bs_marker_object['zIndex'] = 250;
			bs_marker_object['optimized'] = false;

			/*Create BS Marker*/
			var bs_marker = new google.maps.Marker(bs_marker_object);

			// Right click event on sector marker
			google.maps.event.addListener(bs_marker, 'rightclick', function(e) {
				// Close infowindow if any exists
				infowindow.close()
				gmap_self.startBsMaintenanceFunction(this);
			});

			/*Add BS Marker To Cluster*/
			masterClusterInstance.addMarker(bs_marker);

			/*Sectors Array*/
			var sector_array = bs_ss_devices[i].sectors ? bs_ss_devices[i].sectors : [],
				sector_info_list = '',
				sector_infoWindow_content = sector_info_list ? sector_info_list : [],
				deviceIDArray= [];

			/*Plot Sector*/
			for(var j=sector_array.length;j--;) {

				var fetched_azimuth = sector_array[j].azimuth_angle,
					fetched_beamWidth = sector_array[j].beam_width,
					fetched_color = sector_array[j].color && sector_array[j].color != 'NA' ? sector_array[j].color : 'rgba(74,72,94,0.58)',
					ss_infoWindow_content = sector_array[j].ss_info_list ? sector_array[j].ss_info_list : [],
					azimuth = fetched_azimuth && fetched_azimuth != 'NA' ? fetched_azimuth : 10,
					beam_width = fetched_beamWidth && fetched_beamWidth != 'NA' ? fetched_beamWidth : 10,
					sector_color = fetched_color,
					sector_perf_url = sector_array[j].perf_page_url ? sector_array[j].perf_page_url : "",
					sector_inventory_url = sector_array[j].inventory_url ? sector_array[j].inventory_url : "",
					sector_item_index = sector_array[j].item_index > -1 ? sector_array[j].item_index : 0,
					sector_tech = sector_array[j].technology ? $.trim(sector_array[j].technology.toLowerCase()) : "",
					orientation = $.trim(sector_array[j].polarization),
					sector_child = sector_array[j].sub_stations,
					rad = sector_array[j].radius && Number(sector_array[j].radius) > 0 ? sector_array[j].radius : 0.5,
					parent_info = {
						'filter_info' : {
							'bs_name' 		   : bs_ss_devices[i].name,
							'sector_name' 	   : sector_array[j].ip_address,
							'bs_id' 		   : bs_ss_devices[i].bs_id,
							'sector_id' 	   : sector_array[j].sector_id,
							'sector_device_id' : sector_array[j].device_id,
							'id' 			   : sector_array[j].id
						},
						'bs_lat'	  : bs_lat,
						'bs_lon'	  : bs_lon
					},
					startLon = "",
					startLat = "",
					sect_height = sector_array[j].antenna_height;

				var startEndObj = {};

				// if(sector_tech != "ptp" && sector_tech != "p2p") {
				if(ptp_tech_list.indexOf(sector_tech)  == -1) {
					/*Call createSectorData function to get the points array to plot the sector on google maps.*/
					gmap_self.createSectorData(bs_lat, bs_lon, rad, azimuth, beam_width, orientation, function(pointsArray) {

						var halfPt = Math.floor(pointsArray.length / (+2)),
							polyStartLat = "",
							polyStartLon = "";

						if(halfPt == 1) {
							var latLonArray = [
								pointsArray[0],
								pointsArray[1]
							];
							var centerPosition = gmap_self.getMiddlePoint(latLonArray);

							polyStartLat = centerPosition.lat * 180 / Math.PI;
							polyStartLon = centerPosition.lon * 180 / Math.PI;
						} else {
							polyStartLat = pointsArray[halfPt].lat;
							polyStartLon = pointsArray[halfPt].lon;
						}

						var sectorInfo = getMarkerInfoJson(sector_array[j], 'sector_polygon', parent_info);

						/*Plot sector on map with the retrived points*/
						gmap_self.plotSector_gmap(
							pointsArray,
							sectorInfo
						);

						startEndObj["startLat"] = polyStartLat;
						startEndObj["startLon"] = polyStartLon;

						startEndObj["sectorLat"] = polyStartLat;
						startEndObj["sectorLon"] = polyStartLon;
					});
				} else {

					startEndObj["startLat"] = bs_lat;
	    			startEndObj["startLon"] = bs_lon;
	    			
	    			startEndObj["sectorLat"] = bs_lat;
					startEndObj["sectorLon"] = bs_lon;
				}

				if(ptp_tech_list.indexOf(sector_tech) > -1) {
	
					var sector_icon_obj = gmap_self.getMarkerImageBySize(
							base_url+"/"+sector_array[j].markerUrl,
							"other"
						);

					parent_info['startLat'] = startEndObj["startLat"];
					parent_info['startLon'] = startEndObj["startLon"];

					var sectors_Markers_Obj = getMarkerInfoJson(sector_array[j], 'sector', parent_info);

					// Update map specific info
					sectors_Markers_Obj['position'] = new google.maps.LatLng(bs_lat, bs_lon);
					sectors_Markers_Obj['icon'] = hiddenIconImageObj;
					sectors_Markers_Obj['oldIcon'] = sector_icon_obj;
					sectors_Markers_Obj['clusterIcon'] = hiddenIconImageObj;
					sectors_Markers_Obj['zIndex'] = 200;
					sectors_Markers_Obj['optimized'] = false;

					/*Create Sector Marker*/
					var sector_Marker = new google.maps.Marker(sectors_Markers_Obj);

					// Right click event on sector marker
					google.maps.event.addListener(sector_Marker, 'rightclick', function(e) {
						
						var condition1 = ($.trim(this.pl) && $.trim(this.pl) != 'N/A'),
							condition2 = ($.trim(this.rta) && $.trim(this.rta) != 'N/A'),
							condition3 = ($.trim(this.pl_timestamp) && $.trim(this.pl_timestamp) != 'N/A');

						if(condition1 || condition2 || condition3) {
							var pl = $.trim(this.pl) ? this.pl : "N/A",
								rta = $.trim(this.rta) ? this.rta : "N/A",
								pl_timestamp = $.trim(this.pl_timestamp) ? this.pl_timestamp : "N/A",
								info_html = '';

							// Create hover infowindow html content
							info_html += '<table class="table table-responsive table-bordered table-hover">\
										  <tr><td>Packet Drop</td><td>'+pl+'</td></tr>\
									  	  <tr><td>Latency</td><td>'+rta+'</td></tr>\
									  	  <tr><td>Timestamp</td><td>'+pl_timestamp+'</td></tr>\
									  	  </table>';

					    	/*Set the content for infowindow*/
							infowindow.setContent(info_html);
							/*Shift the window little up*/
							infowindow.setOptions({pixelOffset: new google.maps.Size(0, -20)});
							/*Set The Position for InfoWindow*/
							infowindow.setPosition(new google.maps.LatLng(e.latLng.lat(),e.latLng.lng()));
							/*Open the info window*/
							infowindow.open(mapInstance);
						}
					});

					if(sectorMarkerConfiguredOn.indexOf(sector_array[j].ip_address) == -1) {
						sector_MarkersArray.push(sector_Marker);

						/*Push Sector marker to pollableDevices array*/
						pollableDevices.push(sector_Marker);
						
						allMarkersObject_gmap['sector_device']['sector_'+sector_array[j].ip_address] = sector_Marker;

						sectorMarkerConfiguredOn.push(sector_array[j].ip_address);
						if(sectorMarkersMasterObj[bs_ss_devices[i].name]) {
							sectorMarkersMasterObj[bs_ss_devices[i].name].push(sector_Marker)
						} else {
							sectorMarkersMasterObj[bs_ss_devices[i].name]= [];
							sectorMarkersMasterObj[bs_ss_devices[i].name].push(sector_Marker)
						}
					}

					/*End of Create Sector Marker*/
					
					// deviceIDArray.push(sector_array[j]['device_info'][1]['value']);
				}

				/*Plot Sub-Station*/
				for(var k=sector_child.length;k--;) {

					var ss_marker_obj = sector_child[k],
						ss_info_dict = ss_marker_obj.dataset ? ss_marker_obj.dataset : [],
						ss_icon_obj = gmap_self.getMarkerImageBySize(base_url+"/"+ss_marker_obj.markerUrl,"other"),
						ckt_id_val = ss_marker_obj.circuit_id ? ss_marker_obj.circuit_id : "",
						ss_antenna_height = ss_marker_obj.antenna_height,
                        parent_info = {
							'filter_info' : {
								'bs_name' 		   : bs_ss_devices[i].name,
								'sector_name' 	   : sector_array[j].ip_address,
					    		"ss_name" 		   : ss_marker_obj.name,
								'bs_id' 		   : bs_ss_devices[i].bs_id,
								'sector_id' 	   : sector_array[j].sector_id,
								'sector_device_id' : sector_array[j].device_id,
								"id" 			   : ss_marker_obj.id
							},
							'technology' : sector_array[j].technology,
							'sector_device_name' : sector_array[j].device_name
						};

					// Set the ckt id to sector marker object (only in case of PTP)
					if(ptp_tech_list.indexOf(sector_tech) > -1) {
						sector_Marker.setOptions({
							"cktId" : ckt_id_val
						});
					}

					var ss_marker_object = getMarkerInfoJson(ss_marker_obj, 'sub_station', parent_info);

					// Update map specific info
					ss_marker_object['position'] = new google.maps.LatLng(ss_marker_obj.lat,ss_marker_obj.lon);
					ss_marker_object['icon'] = ss_icon_obj;
					ss_marker_object['oldIcon'] = ss_icon_obj;
					ss_marker_object['clusterIcon'] = ss_icon_obj;
					ss_marker_object['zIndex'] = 200;
					ss_marker_object['optimized'] = false;

				    /*Create SS Marker*/
				    var ss_marker = new google.maps.Marker(ss_marker_object);

			    	if(last_selected_label && not_ss_param_labels.indexOf(last_selected_label) == -1) {
			    		var labelInfoObject = ss_marker['label_str'] ? ss_marker['label_str'].split('|') : [],
			    			labelHtml = "";
			    		
		            	if(labelInfoObject && labelInfoObject.length) {
		            		var shownVal = labelInfoObject[$('#static_label option:selected').index() - 2] ? $.trim(labelInfoObject[$('#static_label option:selected').index() - 2]) : "NA";
		                    labelHtml += shownVal;
		                }

				    	// If any html created then show label on ss
				    	if(labelHtml) {
				    		var perf_infobox = gisPerformanceClass.createInfoboxLabel(
				    			labelHtml,
				    			ssParamLabelStyle,
				    			-120,
				    			-10,
				    			ss_marker.getPosition(),
				    			false
			    			);
	                        perf_infobox.open(mapInstance, ss_marker);
	                        tooltipInfoLabel['ss_'+ss_marker_obj.name] = perf_infobox;
				    	}
				    }

				    // Right click event on sub-station marker
					google.maps.event.addListener(ss_marker, 'rightclick', function(e) {
						var condition1 = ($.trim(this.pl) && $.trim(this.pl) != 'N/A'),
							condition2 = ($.trim(this.rta) && $.trim(this.rta) != 'N/A'),
							condition3 = ($.trim(this.pl_timestamp) && $.trim(this.pl_timestamp) != 'N/A');

						if(condition1 || condition2 || condition3) {
							var pl = $.trim(this.pl) ? this.pl : "N/A",
								rta = $.trim(this.rta) ? this.rta : "N/A",
								pl_timestamp = $.trim(this.pl_timestamp) ? this.pl_timestamp : "N/A",
								info_html = '';

							// Create hover infowindow html content
							info_html += '<table class="table table-responsive table-bordered table-hover">\
										  <tr><td>Packet Drop</td><td>'+pl+'</td></tr>\
										  <tr><td>Latency</td><td>'+rta+'</td></tr>\
										  <tr><td>Timestamp</td><td>'+pl_timestamp+'</td></tr>\
										  </table>';

					    	/*Set the content for infowindow*/
							infowindow.setContent(info_html);
							/*Shift the window little up*/
							infowindow.setOptions({pixelOffset: new google.maps.Size(0, -20)});
							/*Set The Position for InfoWindow*/
							infowindow.setPosition(new google.maps.LatLng(e.latLng.lat(),e.latLng.lng()));
							/*Open the info window*/
							infowindow.open(mapInstance);
						}
					});

				    /*Add BS Marker To Cluster*/
					masterClusterInstance.addMarker(ss_marker);

				    markersMasterObj['SS'][String(ss_marker_obj.lat)+ ss_marker_obj.lon]= ss_marker;
				    markersMasterObj['SSNamae'][String(ss_marker_obj.device_name)]= ss_marker;

				    /*Add the master marker to the global master markers array*/
			    	masterMarkersObj.push(ss_marker);

			    	allMarkersObject_gmap['sub_station']['ss_'+ss_marker_obj.name] = ss_marker;

			    	/*Add parent markers to the OverlappingMarkerSpiderfier*/
				    oms_ss.addMarker(ss_marker);

				    /*Push SS marker to pollableDevices array*/
					pollableDevices.push(ss_marker)

					var ss_info = {
							"info" : ss_info_dict,
							"antenna_height" : ss_antenna_height,
							"ss_id": ss_marker_obj.id
						},
						base_info = {
							"info" : bs_ss_devices[i].dataset ? bs_ss_devices[i].dataset : [],
							"bs_id": bs_ss_devices[i].bs_id
						};

					startEndObj["nearEndLat"] = bs_ss_devices[i].lat;
					startEndObj["nearEndLon"] = bs_ss_devices[i].lon;

				    startEndObj["endLat"] = ss_marker_obj.lat;
		    		startEndObj["endLon"] = ss_marker_obj.lon;

		    		startEndObj["windowTitle"] = "BS-SS";
		    		startEndObj["startTitle"] = "BS Info";
		    		startEndObj["endTitle"] = "SS Info";

		    		/*Link color object*/
		    		var link_color = sector_color;
		    		linkColor = link_color && link_color != 'NA' ? link_color : 'rgba(74,72,94,0.58)';

	    			if(ss_marker_obj.show_link == 1) {
	    				/*Create the link between BS & SS or Sector & SS*/
				    	var ss_link_line = gmap_self.createLink_gmaps(
				    		startEndObj,
				    		linkColor,
				    		base_info,
				    		ss_info,
				    		sect_height,
				    		sector_array[j].ip_address,
				    		ss_marker_obj.name,
				    		bs_ss_devices[i].name,
				    		bs_ss_devices[i].bs_id,
				    		sector_array[j].sector_id
			    		);

				    	ssLinkArray.push(ss_link_line);
				    	ssLinkArray_filtered = ssLinkArray;

				    	allMarkersObject_gmap['path']['line_'+ss_marker_obj.name] = ss_link_line;
	    			}
				}
    		}

    		/*Add the master marker to the global master markers array*/
	    	masterMarkersObj.push(bs_marker);

	    	allMarkersObject_gmap['base_station']['bs_'+bs_ss_devices[i].name] = bs_marker;

	    	if(last_selected_label && not_ss_param_labels.indexOf(last_selected_label) > -1) {

	    		var labelHtml = bs_ss_devices[i].alias;

		    	// If any html created then show label on ss
		    	if(labelHtml) {
		    		var perf_infobox = gisPerformanceClass.createInfoboxLabel(
		    			labelHtml,
		    			ssParamLabelStyle,
		    			-120,
		    			-10,
		    			bs_marker.getPosition(),
		    			false
	    			);

                    perf_infobox.open(mapInstance, bs_marker);
                    tooltipInfoLabel['bs_'+bs_ss_devices[i].name] = perf_infobox;
		    	}
		    }

	    	//Add markers to markersMasterObj with LatLong at key so it can be fetched later.
			markersMasterObj['BS'][String(bs_ss_devices[i].lat)+bs_ss_devices[i].lon]= bs_marker;
			markersMasterObj['BSNamae'][String(bs_ss_devices[i].name)]= bs_marker;

	    	/*Add parent markers to the OverlappingMarkerSpiderfier*/
		    oms.addMarker(bs_marker);

		    /*Push All BS Lat & Lon*/
			bsLatArray.push(bs_ss_devices[i].lat);
			bsLonArray.push(bs_ss_devices[i].lon);			
		}

		if(isCallCompleted == 1) {

			/*Hide The loading Icon*/
			$("#loadingIcon").hide();

			if(isFirstTime == 1) {
				/*Load data for basic filters*/
				gmap_self.getBasicFilters();
			}
		}

		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_plot.getTime())/1000;
			console.log("Plot Devices for "+ bs_ss_devices.length +" list - End Time :- "+ time_diff + " Seconds");
			console.log("**********************************");
			start_date_plot = "";
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
	 * @param bs_id {Number}, It contains the id of connected base-station.
	 * @param sector_id {Number}, It contains the id of connected sector.
	 * @return {Object} pathConnector, It contains gmaps polyline object.
	 */
	this.createLink_gmaps = function(startEndObj,linkColor,bs_info,ss_info,sect_height,sector_name,ss_name,bs_name,bs_id,sector_id) {

		if(isDebug) {
			console.log("Create Line Function");
			var start_date_create_link = new Date();
		}

		var pathDataObject = [
				new google.maps.LatLng(startEndObj.startLat,startEndObj.startLon),
				new google.maps.LatLng(startEndObj.endLat,startEndObj.endLon)
			],
			linkObject = {},
			link_path_color = linkColor,
			ss_info_obj = "",
			ss_height = 40,
			bs_index = 0,
			ss_index = 0,
			bs_info_obj = "",
			bs_height = 40,
			ss_id = '';

		if(ss_info) {
			ss_info_obj = ss_info.info ? ss_info.info : ss_info;
			ss_index = ss_info.ss_item_index > -1 ? ss_info.ss_item_index : 0;
			ss_height = ss_info.antenna_height && ss_info.antenna_height != 'NA' ? ss_info.antenna_height : 40;
			ss_id = ss_info.ss_id ? ss_info.ss_id : '';
		}

		if(bs_info) {
			bs_info_obj = bs_info.info ? bs_info.info : bs_info;
			bs_index = bs_info.bs_item_index > -1 ? bs_info.bs_item_index : 0;
			bs_height = bs_info.antenna_height && bs_info.antenna_height != 'NA' ? bs_info.antenna_height : 40;
			bs_id = bs_info.bs_id ? bs_info.bs_id : '';
		}

        if (!sect_height || sect_height == 'NA'){
            sect_height = 47;
        }

		linkObject = {
			path 			: pathDataObject,
			strokeColor		: link_path_color,
			strokeOpacity	: 1.0,
			strokeWeight	: 3,
			pointType 		: "path",
			geodesic		: true,
			ss_dataset		: ss_info_obj,
			ss_lat 			: startEndObj.endLat,
			ss_lon 			: startEndObj.endLon,
			windowTitle 	: startEndObj.windowTitle,
			startTitle 		: startEndObj.startTitle,
			endTitle 		: startEndObj.endTitle,
			bs_height 		: sect_height,
			bs_lat 			: startEndObj.startLat,
			bs_dataset 		: bs_info_obj,
			bs_lon 			: startEndObj.startLon,
			ss_height 		: ss_height,
			sector_lat 		: startEndObj.sectorLat,
			sector_lon 		: startEndObj.sectorLon,
			filter_data 	: {
				"bs_name": bs_name,
				"sector_name": sector_name,
				"ss_name": ss_name,
				"bs_id": bs_id,
				"sector_id": sector_id,
				"ss_id": ss_id
			},
			nearLat 		: startEndObj.nearEndLat,
			nearLon 		: startEndObj.nearEndLon,
			sectorName 	    : sector_name,
			ssName 		    : ss_name,
			bsName 			: bs_name,
			zIndex 			: 9999
		};

		var pathConnector = new google.maps.Polyline(linkObject);

		/*Bind Click Event on Link Path Between Master & Slave*/
		google.maps.event.addListener(pathConnector, 'click', function(e) {
			/*Call the function to create info window content*/
			gmap_self.makeWindowContent(this, function(content) {
				$("#infoWindowContainer").html(content);
				
			});
			// Reduce infowindow size in case of point & ruler line
			if(this.startTitle && $.trim(this.startTitle.toLowerCase()) == 'point a') {

				if($("#infoWindowContainer").hasClass("col-md-4")) {
					$("#infoWindowContainer").removeClass("col-md-4")
				}

				if($("#infoWindowContainer").hasClass("col-md-offset-8")) {
					$("#infoWindowContainer").removeClass("col-md-offset-8")
				}

				if(!$("#infoWindowContainer").hasClass("col-md-3")) {
					$("#infoWindowContainer").addClass("col-md-3")
				}

				if(!$("#infoWindowContainer").hasClass("col-md-offset-9")) {
					$("#infoWindowContainer").addClass("col-md-offset-9")
				}
			}

			$("#infoWindowContainer").removeClass('hide');
		});

		markersMasterObj['Lines'][String(startEndObj.startLat)+ startEndObj.startLon+ startEndObj.endLat+ startEndObj.endLon] = pathConnector;
		markersMasterObj['LinesName'][String(bs_name)+ ss_name]= pathConnector;
		
		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_create_link.getTime())/1000;
			console.log("Create Line End Time :- "+ time_diff + " Seconds");
			console.log("*******************************************");
			start_date_create_link = "";

		}

		/*returns gmap polyline object */
		return pathConnector;
	};

	/**
	 * This function show connection lines within the bounds
	 * @method showLinesInBounds
	 */
	this.showLinesInBounds = function(callback) {

		if(isDebug) {
			console.log("Show in bound lines Function");
			var start_date_line_inBound = new Date();
		}

		var isLineChecked = $("#showConnLines").length > 0 ? $("#showConnLines:checked").length : 1;
		/*checked case*/
		if(isLineChecked > 0) {
			/*Loop for polylines*/
			for(var key in allMarkersObject_gmap['path']) {
				if(allMarkersObject_gmap['path'].hasOwnProperty(key)) {

			    	var current_line = allMarkersObject_gmap['path'][key],
			    		nearEndVisible = mapInstance.getBounds().contains(
			    			new google.maps.LatLng(current_line.nearLat,current_line.nearLon)
		    			),
				      	farEndVisible = mapInstance.getBounds().contains(
				      		new google.maps.LatLng(current_line.ss_lat,current_line.ss_lon)
			      		),
				      	connected_bs = allMarkersObject_gmap['base_station']['bs_'+current_line.filter_data.bs_name],
				      	connected_ss = allMarkersObject_gmap['sub_station']['ss_'+current_line.filter_data.ss_name];

				    if((nearEndVisible || farEndVisible) && (connected_bs && connected_ss)) {
				    	// If polyline not shown then show the polyline
				    	if(!current_line.map) {
				    		current_line.setMap(mapInstance);
				    	}

				    	// Show cross if exist
					    if(cross_label_array[key]) {
					    	cross_label_array[key].show();
					    }
				    } else {
				    	// If polyline shown then hide the polyline
				    	if(current_line.map) {
				    		current_line.setMap(null);
			    		}

			    		// Remove CROSS info label
			    		if(cross_label_array[key]) {
					    	cross_label_array[key].hide();
					    }
				    }
			    }
			}
		}

		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_line_inBound.getTime())/1000;
			console.log("Show in bound lines End Time :- "+ time_diff + " Seconds");
			console.log("**********************************");
			start_date_line_inBound = "";
		}
		// Callbacked to called function
		callback(true);
	};

	/**
	 * This function show sub-stations within the bounds
	 * @method showSubStaionsInBounds
	 */
	this.showSubStaionsInBounds = function(callback) {
		if(isDebug) {
			console.log("Show in bound SS Function");
			var start_date_ss_inBound = new Date();
		}

		var isSSChecked = $("#showAllSS").length > 0 ? $("#showAllSS:checked").length : 1;

		/*Checked case*/
		if(isSSChecked > 0) {
			/*Loop for polylines*/
			for(var key in allMarkersObject_gmap['sub_station']) {
				if(allMarkersObject_gmap['sub_station'].hasOwnProperty(key)) {
			    	var ss_marker = allMarkersObject_gmap['sub_station'][key],
			    		isMarkerExist = mapInstance.getBounds().contains(ss_marker.getPosition());
		    		if(isMarkerExist) {
				    	if(ss_marker.isActive && +(ss_marker.isActive) === 1) {
				    		// If SS Marker not shown then show the SS Marker
				    		if(!allMarkersObject_gmap['sub_station'][key].map) {
				      			allMarkersObject_gmap['sub_station'][key].setMap(mapInstance);
				    		}

				    		if(tooltipInfoLabel[key] && !tooltipInfoLabel[key].map) {
			      				tooltipInfoLabel[key].setMap(mapInstance);
			      			}
				    	} else {
				    		// If SS Marker shown then hide the SS Marker
				    		if(allMarkersObject_gmap['sub_station'][key].map) {
				      			allMarkersObject_gmap['sub_station'][key].setMap(null);
			    			}
				    	}
		    		}
			    }
			}
		}

		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_ss_inBound.getTime())/1000;
			console.log("Show in bound SS End Time :- "+ time_diff + " Seconds");
			console.log("***********************************");
			start_date_ss_inBound = "";
		}
		// Callbacked to called function
		callback(true);
	};

	/**
	 * This function show base-stations within the bounds
	 * @method showBaseStaionsInBounds
	 */
	this.showBaseStaionsInBounds = function(callback) {
		if(isDebug) {
			console.log("Show in bound BS");
			var start_date_bs_inBound = new Date();
		}
		/*Loop for polylines*/
		for(var key in allMarkersObject_gmap['base_station']) {
			if(allMarkersObject_gmap['base_station'].hasOwnProperty(key)) {
		    	var bs_marker = allMarkersObject_gmap['base_station'][key],
		      		isMarkerExist = mapInstance.getBounds().contains(bs_marker.getPosition());
	      		if(isMarkerExist) {
	      			if(tooltipInfoLabel[key] && !tooltipInfoLabel[key].map) {
	      				tooltipInfoLabel[key].setMap(mapInstance);
	      			}
		    		// If BS Marker not shown then show the BS Marker
		    		if(!allMarkersObject_gmap['base_station'][key].map) {
		      			allMarkersObject_gmap['base_station'][key].setMap(mapInstance);
		    			allMarkersObject_gmap['base_station'][key]['isActive'] = true;
		    		}
	      		}
		    }
		}

		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_bs_inBound.getTime())/1000;
			console.log("Show in bound BS End Time :- "+ time_diff + " Seconds");
			console.log("**********************************");
			start_date_bs_inBound = "";
		}
		// Callbacked to called function
		callback(true);
	};

	/**
	 * This function show base-stations devices(sector devices) within the bounds
	 * @method showSectorDevicesInBounds
	 */
	this.showSectorDevicesInBounds = function(callback) {
		if(isDebug) {
			console.log("Show in bound Sector Devices");
			var start_date_sector_inBound = new Date();
		}
		/*Loop for polylines*/
		for(var key in allMarkersObject_gmap['sector_device']) {
			if(allMarkersObject_gmap['sector_device'].hasOwnProperty(key)) {
		    	var sector_marker = allMarkersObject_gmap['sector_device'][key],
		      		isMarkerExist = mapInstance.getBounds().contains(sector_marker.getPosition());
	      		if(isMarkerExist) {
			    	if(sector_marker.isActive && +(sector_marker.isActive) === 1) {
			    		// If Sector Marker not shown then show the Sector Marker
			    		if(!allMarkersObject_gmap['sector_device'][key].map) {
			      			allMarkersObject_gmap['sector_device'][key].setMap(mapInstance);
			    		}
			    	} else {
			    		// If Sector Marker shown then hide the Sector Marker
			    		if(allMarkersObject_gmap['sector_device'][key].map) {
			    			allMarkersObject_gmap['sector_device'][key].setMap(null);
		    			}
			        }
	      		}
		  }
		}
		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_sector_inBound.getTime())/1000;
			console.log("Show in bound Sector Devices End Time :- "+ time_diff + " Seconds");
			console.log("******************************************");
			start_date_sector_inBound = "";
		}
		// Callbacked to called function
		callback(true);
	};

	/**
	 * This function show polygon(sector) within the bounds
	 * @method showSectorPolygonInBounds
	 */
	this.showSectorPolygonInBounds = function(callback) {
		if(isDebug) {
			console.log("Show in bound Sector Polygons");
			var start_date_poly_inBound = new Date();
		}
		/*Loop for polylines*/
		for(var key in allMarkersObject_gmap['sector_polygon']) {
			if(allMarkersObject_gmap['sector_polygon'].hasOwnProperty(key)) {
		    	var sector_polygon = allMarkersObject_gmap['sector_polygon'][key],
		    		isMarkerExist = mapInstance.getBounds().contains(new google.maps.LatLng(sector_polygon.ptLat,sector_polygon.ptLon));
	    		if(isMarkerExist) {
			    	if(sector_polygon.isActive && +(sector_polygon.isActive) === 1) {
			    		// If Polygon not shown then show the polygon
			    		if(!allMarkersObject_gmap['sector_polygon'][key].map) {
			      			allMarkersObject_gmap['sector_polygon'][key].setMap(mapInstance);
			    		}
			    	} else {
			    		// If Polygon shown then hide the polygon
			    		if(allMarkersObject_gmap['sector_polygon'][key].map) {
			      			allMarkersObject_gmap['sector_polygon'][key].setMap(null);
		    			}
			        }
	    		}
		    }
		}
		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_poly_inBound.getTime())/1000;
			console.log("Show in bound Sector Polygons End Time :- "+ time_diff +" Seconds");
			console.log("***********************************");
			start_date_poly_inBound = "";
		}
		// Callbacked to called function
		callback(true);
	};

	/**
	 * This function show/hide the connection line between BS & SS.
	 * @method showConnectionLines_gmap
	 */
	this.showConnectionLines_gmap = function() {
		if(isDebug) {
			console.log("Show/Hide Connection Lines");
			var start_date_toggle_line = new Date();
		}

		var isLineChecked = $("#showConnLines").length > 0 ? $("#showConnLines:checked").length : 1;

		// Update Cookie Value
		if ($("#showConnLines").length > 0) {
			$.cookie("isLineChecked", $("#showConnLines")[0].checked, {path: '/', secure : true});
		} else {
			$.cookie("isLineChecked", true, {path: '/', secure : true});
		}

		var current_lines = ssLinkArray_filtered;

		/*Unchecked case*/
		if(isLineChecked == 0) {
			for(key in allMarkersObject_gmap['path']) {
				if(allMarkersObject_gmap['path'][key].map) {
					allMarkersObject_gmap['path'][key].setMap(null);
				}

				if(cross_label_array[key] && cross_label_array[key].getVisible()) {
					cross_label_array[key].hide()
				}
			}

		} else {
			for(key in allMarkersObject_gmap['path']) {
				if(!allMarkersObject_gmap['path'][key].map) {
					allMarkersObject_gmap['path'][key].setMap(mapInstance);
				}

				if(cross_label_array[key] && !cross_label_array[key].getVisible()) {
					cross_label_array[key].show()
				}
			}
		}

		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_toggle_line.getTime())/1000;
			console.log("Show/Hide Connection Lines End Time :- "+ time_diff +" Seconds");
			console.log("********************************");
			start_date_toggle_line = "";
		}
	};

	/**
	 * This function show/hide the sub-stations.
	 * @method showSubStations_gmap
	 */
	this.showSubStations_gmap = function() {

		if(isDebug) {
			console.log("Show/Hide SS");
			var start_date_toggle_ss = new Date();
		}

		var isSSChecked = $("#showAllSS").length > 0 ? $("#showAllSS:checked").length : 1;

		// Update Cookie Value
		if ($("#showAllSS").length > 0) {
			$.cookie("isSSChecked", $("#showAllSS")[0].checked, {path: '/', secure : true});
		} else {
			$.cookie("isSSChecked", true, {path: '/', secure : true});
		}

		/*Unchecked case*/
		if(isSSChecked == 0) {
			for(key in allMarkersObject_gmap['sub_station']) {
				if(allMarkersObject_gmap['sub_station'][key].map) {
					allMarkersObject_gmap['sub_station'][key].setMap(null);
				}
			}

		} else {
			for(key in allMarkersObject_gmap['sub_station']) {
				if(!allMarkersObject_gmap['sub_station'][key].map) {
					allMarkersObject_gmap['sub_station'][key].setMap(mapInstance);
				}
			}
		}

		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_toggle_ss.getTime())/1000;
			console.log("Show/Hide SS End Time :- "+ time_diff + " Seconds");
			console.log("*********************************");
			start_date_toggle_ss = "";
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
		if(isDebug) {
			console.log("Create Sector Polygon Data");
			var start_date_sector_data = new Date();
		}
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
			/*Reset Pt Object*/
			pointObj = {};
			pointObj["lat"] = lat1;
			pointObj["lon"] = lon1;
			/*Add point object to array*/
			PGpoints.push(pointObj);

			lat2 = (+lat) + (PRlat * cos( d2r * (azimuth + beamWidth/2 )));
			lon2 = (+lng) + (PRlng * sin( d2r * (azimuth + beamWidth/2 )));
			
			var theta = 0,
				gamma = d2r * (azimuth + beamWidth/2 );

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
		if(orientation && $.trim(orientation.toLowerCase()) == "horizontal") {
			var len = Math.floor(PGpoints.length / 3);
			// First Value of Array
			triangle.push(PGpoints[0]);
			// Middle Value of Array
			triangle.push(PGpoints[(len * 2) - 1]);
			// Last Value of Array
			triangle.push(PGpoints[PGpoints.length - 1]);
			/*Assign the triangle object array to sectorDataArray for plotting the polygon*/
			sectorDataArray = triangle;
		} else {
			/*Assign the PGpoints object array to sectorDataArray for plotting the polygon*/
			sectorDataArray = PGpoints;
		}

		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_sector_data.getTime())/1000;
			console.log("Create Sector Polygon Data End Time :- "+ time_diff + " Seconds");
			console.log("***********************************");
			start_date_sector_data = "";
		}

		/*Callback with lat-lon object array.*/
        callback(sectorDataArray);
	};

	/**
	 * This function plot the sector for given lat-lon points
	 * @method plotSector_gmap.
	 * @param pointsArray [Array], It contains the points lat-lon object array.
	 * @param sectorInfo {JSON Object Array}, It contains the information about the sector.
	 */
	this.plotSector_gmap = function(pointsArray, sectorInfo) {
		if(isDebug) {
			console.log("Plot Sector Polygon");
			var start_date_plot_sector = new Date();
		}

		var polyPathArray = [],
			technology = sectorInfo.technology ? sectorInfo.technology : '';
		
		var halfPt = Math.floor(pointsArray.length / (+2)),
			startLat = pointsArray[halfPt].lat,
			startLon = pointsArray[halfPt].lon;

		for(var i=pointsArray.length;i--;) {
			var pt = new google.maps.LatLng(pointsArray[i].lat,pointsArray[i].lon);
			polyPathArray.push(pt);
		}

		var sColor = "#000000",
			sWidth = 1;

		if(technology.toLowerCase() == 'pmp') {
			sColor = '#FFFFFF';
			sWidth = 2;
		}

		var polyObj = sectorInfo;

		polyObj['path'] = polyPathArray;
		polyObj['strokeColor'] = sColor;
		polyObj['fillColor'] = sectorInfo.bg_color;
		polyObj['startLat'] = startLat;
		polyObj['startLon'] = startLon;
		polyObj['strokeOpacity'] = 1;
		polyObj['fillOpacity'] = 0.5;
		polyObj['strokeWeight'] = sWidth;
		polyObj['zIndex'] = 180;
		polyObj['geodesic'] = true;


		var poly = new google.maps.Polygon(polyObj);

        allMarkersObject_gmap['sector_polygon']['poly_'+sectorInfo.sectorName+"_"+sectorInfo.sector_id] = poly;

        /*listener for click event of sector*/
		google.maps.event.addListener(poly,'click',function(e) {

			/*Call the function to create info window content*/
			gmap_self.makeWindowContent(poly, function(content) {
				$("#infoWindowContainer").html(content);
				$("#infoWindowContainer").removeClass('hide');
			});
		});

		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_plot_sector.getTime())/1000;
			console.log("Plot Sector Polygon End Time :- "+ time_diff + " Seconds");
			console.log("***********************************");
			start_date_plot_sector = "";
		}
	};

	/**
	 * This function creates the info window content for BS,SS & link path 
	 * @method makeWindowContent
	 * @param contentObject {Object} It contains current pointer(this) information
	 * @return {String} windowContent, It contains content to be shown on info window
	 */
	this.makeWindowContent = function(contentObject, callback) {
		if(isDebug) {
			console.log("Make Info Window HTML");
			var start_date_infowindow = new Date();
		}

		getStaticInfo(contentObject, function(response) {
			// Update the 'contentObject' with the updated object
			contentObject = response;

			var windowContent = "",
				infoTable =  "",
				perfContent = "",
				clickedType = contentObject.pointType ? $.trim(contentObject.pointType) : "",
				device_id = "",
				device_name = "",
				marker_key = "",
				marker_type = "",
				maps_single_service_poll_flag = live_poll_config ? live_poll_config['maps_single_service'] : "",
				maps_themetics_poll_flag = live_poll_config ? live_poll_config['maps_themetics'] : "",
				single_service_polling = maps_single_service_poll_flag ? maps_single_service_poll_flag : false,
				themetics_polling = maps_themetics_poll_flag ? maps_themetics_poll_flag : false,
				device_tech = contentObject.technology ? $.trim(contentObject.technology.toLowerCase()) : "",
				device_type = contentObject.device_type ? $.trim(contentObject.device_type.toLowerCase()) : "",
				device_pl = contentObject.pl ? contentObject.pl : "",
				device_name = contentObject.device_name ? contentObject.device_name : "";

			if(clickedType == 'sector_Marker' || clickedType == 'sector') {
				device_id = contentObject.device_id;
				if(clickedType == 'sector_Marker') {
					marker_key = "sector_"+contentObject.filter_data.sector_name;
					marker_type = "sector_device";
				} else {
					marker_key = "poly_"+contentObject.filter_data.sector_name+"_"+contentObject.filter_data.sector_id;
					marker_type = "sector_polygon";
				}
			} else if(clickedType == 'sub_station') {
				device_id = contentObject.ss_device_id ? contentObject.ss_device_id : "";
				marker_key = "ss_"+contentObject.name;
				marker_type = "sub_station";
			} else if(clickedType == 'base_station') {
				device_id = contentObject.bh_device_id ? contentObject.bh_device_id : "";
				device_tech = contentObject.bh_device_type ? $.trim(contentObject.bh_device_type).toLowerCase() : "";
				marker_key = "bs_"+contentObject.name;
				marker_type = "base_station";
			}

			// Tabs Structure HTML
			/*Tabbale Start*/
			infoTable += '<div class="tabbable">';
			/*Tabs Creation Start*/
			infoTable += '<ul class="nav nav-tabs">\
						  <li class="active"><a href="#static_block" data-toggle="tab">\
						  <i class="fa fa-arrow-circle-o-right"></i> Static Info</a></li>\
						  <li class=""><a href="#polled_block" data-toggle="tab" id="polled_tab" \
						  device_id="'+device_id+'" point_type="'+clickedType+'" \
						  pl_value = "'+device_pl+'" device_tech="'+device_tech+'" \
						  device_type="' + device_type + '">\
						  <i class="fa fa-arrow-circle-o-right"></i> Polled Info \
						  <i class="fa fa-spinner fa fa-spin hide"> </i></a>\
						  </li>';

			if(single_service_polling && (clickedType.indexOf('sector') > -1 || clickedType == 'sub_station')) {
				infoTable += '<li><a href="#poll_now_block" data-toggle="tab" id="poll_now_tab" \
							  device_id="'+device_id+'" point_type="'+clickedType+'" >\
							  <i class="fa fa-arrow-circle-o-right"></i> Poll Now \
							  <i class="fa fa-spinner fa fa-spin hide"> </i></a>\
							  </li>';
			}
			infoTable += '</ul>';
			/*Tabs Creation Ends*/

			/*True,if clicked on the link line*/
			if(clickedType == "path") {
				try {
					var bs_item_index = contentObject.bs_item_index > -1 ? contentObject.bs_item_index : 0,
						ss_item_index = contentObject.ss_item_index > -1 ? contentObject.ss_item_index : 0,
						path_circuit_id = contentObject.ss_dataset ? gisPerformanceClass.getKeyValue(contentObject.ss_dataset,"cktid",true,ss_item_index) : "",
						lineWindowTitle = contentObject.windowTitle ? contentObject.windowTitle : "BS-SS",
						lineStartTitle = contentObject.startTitle ? contentObject.startTitle : "BS-Sector Info",
						lineEndTitle = contentObject.endTitle ? contentObject.endTitle : "SS Info",
						sector_title = lineStartTitle.toLowerCase().indexOf("point") > -1 ? lineStartTitle : "BS",
						ss_title = lineEndTitle.toLowerCase().indexOf("point") > -1 ? lineEndTitle : "SS";

					// Reset HTML String
					infoTable = "";
					
					/*Tabbale Start*/
					infoTable += '<div class="tabbable">';
					/*Tabs Creation Start*/
					infoTable += '<ul class="nav nav-tabs">';
					infoTable += '<li class="active"><a href="#near_end_block" data-toggle="tab"><i class="fa fa-arrow-circle-o-right"></i> '+lineStartTitle+'</a></li>';
					infoTable += '<li class=""><a href="#far_end_block" data-toggle="tab"><i class="fa fa-arrow-circle-o-right"></i> '+lineEndTitle+'</a></li>';
					infoTable += '</ul>';
					/*Tabs Creation Ends*/

					/*Tab-content Start*/
					infoTable += '<div class="tab-content">';

					/*First Tab Content Start*/
					infoTable += '<div class="tab-pane fade active in" id="near_end_block"><div class="divide-10"></div>';

					var bs_info = [];

					if(lineWindowTitle == "Point A-Point B") {
						bs_info = contentObject.bs_dataset;
					} else {
						bs_info = contentObject.bs_dataset ?  rearrangeTooltipArray(bs_toolTip_static,contentObject.bs_dataset) : [];
					}
					
					infoTable += "<table class='table table-bordered table-hover'><tbody>";
					infoTable += gmap_self.createTableDataHtml_map(bs_info, bs_item_index, true);
					infoTable += "</tbody></table>";

					/*BS-Sector Info End*/

					infoTable += '</div>';
					/*First Tab Content End*/

					/*Second Tab Content Start*/
					infoTable += '<div class="tab-pane fade" id="far_end_block"><div class="divide-10"></div>';
					/*SS Info Start*/
					infoTable += "<td>";			



					// var ss_info = contentObject.bs_info ?  rearrangeTooltipArray(bs_toolTip_static,contentObject.bs_info) : [];
					var tech = gisPerformanceClass.getKeyValue(contentObject.ss_dataset,"ss_technology",true,ss_item_index),
						ss_tech = tech ? $.trim(tech.toLowerCase()) : "",
						ss_tooltip_backend_data = contentObject.ss_dataset ? contentObject.ss_dataset : [],
						actual_sequence_array = ss_toolTip_static,
						ss_actual_data = [];

					if(lineWindowTitle == "Point A-Point B") {
						ss_actual_data = ss_tooltip_backend_data;
					} else {
						ss_actual_data = rearrangeTooltipArray(actual_sequence_array, ss_tooltip_backend_data);
					}

					var pos1 = "",
						pos2 = "";

					if(path_circuit_id) {
						pos1 = "<a href='"+posLink1+"="+path_circuit_id+"' class='text-warning' target='_blank'>"+path_circuit_id+"</a>";
						pos2 = "<a href='"+posLink2+"="+path_circuit_id+"' class='text-warning' target='_blank'>"+path_circuit_id+"</a>";
					}

					infoTable += "<table class='table table-bordered table-hover'><tbody>";
					infoTable += gmap_self.createTableDataHtml_map(ss_actual_data, ss_item_index, true, pos1, pos2);
					infoTable += "</tbody></table>";

					var report_download_btn = "";
					var report_type = "circuit";
					if(path_circuit_id) {
						report_download_btn = '<li><button class="btn btn-sm btn-default download_report_btn" \
											   data-complete-text="Download L2 Report"\
										  	   data-loading-text="Please Wait..."\
											   item_id="'+path_circuit_id+'"\
											   type="'+report_type+'">Download L2 Report</button></li>';
					}
					/*SS Info End*/
					infoTable += '</div>';
					/*Second Tab Content End*/

					infoTable += '</div>';
					/*Tab-content end*/

					infoTable += '</div>';
					/*Tabbale End*/

					var isBSLeft = 0;

					if(+(contentObject.nearLon) < +(contentObject.ss_lon)) {
						isBSLeft = 1;
					}

					var sect_alias = gisPerformanceClass.getKeyValue(contentObject.bs_dataset,"alias",true,bs_item_index),
						ss_custName = gisPerformanceClass.getKeyValue(contentObject.ss_dataset,"customer_alias",true,ss_item_index),
						ss_ip = gisPerformanceClass.getKeyValue(contentObject.ss_dataset,"ss_ip",true,ss_item_index),
						sector_ip = contentObject.sectorName,
						sector_ss_name_obj = {
							sector_title : sector_title,
							sector_Alias : sect_alias ? sect_alias : "",
							sector_name : sector_ip ? sector_ip : "",
							ss_title : ss_title,
							ss_name : ss_ip ? ss_ip : " ",
							ss_customerName : ss_custName ? ss_custName : "",
							ss_circuitId : path_circuit_id ? path_circuit_id : "",
							isBSLeft : isBSLeft
						};

					var sector_ss_name = JSON.stringify(sector_ss_name_obj);

					if(+(contentObject.nearLon) < +(contentObject.ss_lon)) {
						/*Concat infowindow content*/
						windowContent += "<div class='windowContainer' style='z-index: 300; position:relative;'>\
										  <div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i> \
										  "+lineWindowTitle+"</h4><div class='tools'><a title='Close' class='close_info_window'>\
										  <i class='fa fa-times text-danger'></i></a></div></div><div class='box-body'>\
										  "+infoTable+"<div class='clearfix'></div><ul class='list-unstyled list-inline'><li>\
										  <button class='btn btn-sm btn-default fresnel_btn' \
										  data-complete-text='Fresnel Zone'\
										  data-loading-text='Please Wait...'\
										  onClick='gmap_self.claculateFresnelZone(\
										  	"+contentObject.nearLat+",\
										  	"+contentObject.nearLon+",\
										  	"+contentObject.ss_lat+",\
										  	"+contentObject.ss_lon+",\
										  	"+contentObject.bs_height+",\
										  	"+contentObject.ss_height+",\
										  	"+sector_ss_name+");'>Fresnel Zone</button>\
										  </li>"+report_download_btn+"</ul></div></div></div>";
					} else {
						/*Concat infowindow content*/
						windowContent += "<div class='windowContainer' style='z-index: 300; position:relative;'>\
										  <div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i> \
										  "+lineWindowTitle+"</h4><div class='tools'><a title='Close' class='close_info_window'>\
										  <i class='fa fa-times text-danger'></i></a></div></div><div class='box-body'>\
										  "+infoTable+"<div class='clearfix'></div><ul class='list-unstyled list-inline'><li>\
										  <button class='btn btn-sm btn-default fresnel_btn' \
										  data-complete-text='Fresnel Zone'\
										  data-loading-text='Please Wait...'\
										  onClick='gmap_self.claculateFresnelZone(\
										  	"+contentObject.ss_lat+",\
										  	"+contentObject.ss_lon+",\
										  	"+contentObject.nearLat+",\
										  	"+contentObject.nearLon+",\
										  	"+contentObject.ss_height+",\
										  	"+contentObject.bs_height+",\
										  	"+sector_ss_name+");'>Fresnel Zone</button>\
										  </li>"+report_download_btn+"</ul></div></div></div>";
					}

				} catch(e) {
					// console.log(e);
				}

			} else if (clickedType == 'sector_Marker' || clickedType == 'sector') {

				var sectorWindowTitle = contentObject.windowTitle ? contentObject.windowTitle : "Base Station Device",
					nearend_perf_url = contentObject.perf_url ? base_url+""+contentObject.perf_url : "",
					nearend_inventory_url = contentObject.inventory_url ? base_url+""+contentObject.inventory_url : "",
					tools_html = "",
					// device_info = contentObject['deviceInfo'] ? contentObject['deviceInfo'] : [],
					// device_extra_info = contentObject['deviceExtraInfo'] ? contentObject['deviceExtraInfo'] : [],
					nearEndInfo = contentObject.dataset ? contentObject.dataset : [],
					item_index = contentObject.item_index > -1 ? contentObject.item_index : 0,
					lat_lon_str = "";

				/*Tab-content Start*/
				infoTable += '<div class="tab-content">';

				if(nearend_perf_url) {
					tools_html += "<a href='"+nearend_perf_url+"' target='_blank' title='Performance'><i class='fa fa-bar-chart-o text-info'> </i></a>";
				}

				if(nearend_inventory_url) {
					tools_html += "<a href='"+nearend_inventory_url+"' target='_blank' title='Inventory'><i class='fa fa-dropbox text-info'> </i></a>";
				}

				// infoTable += "<table class='table table-bordered table-hover'><tbody>";
				var sector_tech = contentObject.technology ? $.trim(contentObject.technology.toLowerCase()) : "",
					sector_device_type = contentObject.device_type ? $.trim(contentObject.device_type.toLowerCase()) : "";

				if(ptp_tech_list.indexOf(sector_tech) > -1) {
					static_info = rearrangeTooltipArray(ptp_sector_toolTip_static, nearEndInfo);
				} else if(sector_tech == 'wimax') {
					static_info = rearrangeTooltipArray(wimax_sector_toolTip_static, nearEndInfo);
				} else if(sector_tech == 'pmp') {
					static_info = rearrangeTooltipArray(pmp_sector_toolTip_static, nearEndInfo);
				} else {
					static_info = nearEndInfo;
				}
				
				/*Static Tab Content Start*/
				infoTable += '<div class="tab-pane fade active in" id="static_block"><div class="divide-10"></div>';


				var circuit_id = "",
					pos1 = "",
					pos2 = "";

				if(ptp_tech_list.indexOf(sector_tech) > -1) {
					circuit_id = gisPerformanceClass.getKeyValue(static_info,"cktid",true, item_index);	
					if(circuit_id) {
						pos1 = "<a href='"+posLink1+"="+circuit_id+"' class='text-warning' target='_blank'>"+circuit_id+"</a>";
						pos2 = "<a href='"+posLink2+"="+circuit_id+"' class='text-warning' target='_blank'>"+circuit_id+"</a>";
					}
				}


				infoTable += "<table class='table table-bordered table-hover'><tbody>";
				infoTable += gmap_self.createTableDataHtml_map(static_info, item_index, true, pos1, pos2);
				infoTable += "</tbody></table>";

				/*BS-Sector Info End*/

				infoTable += '</div>';
				/*Static Tab Content End*/

				if(contentObject['poll_info']) {

					var backend_polled_info = contentObject['poll_info'],
						actual_polled_info = backend_polled_info,
						poll_now_info = poll_now_info = rearrangeTooltipArray(common_toolTip_poll_now,backend_polled_info);

					if(ptp_tech_list.indexOf(sector_tech) > -1) {
						actual_polled_info = rearrangeTooltipArray(ptp_sector_toolTip_polled,backend_polled_info);
					} else if(sector_tech == 'wimax') {
						actual_polled_info = rearrangeTooltipArray(wimax_sector_toolTip_polled,backend_polled_info);
					} else if(sector_tech == 'pmp') {
						if(device_type == 'radwin5kbs') {
	                                    actual_polled_info = rearrangeTooltipArray(pmp_radwin5k_sector_toolTip_polled, backend_polled_info);
	                                } else {
	                                    actual_polled_info = rearrangeTooltipArray(pmp_sector_toolTip_polled, backend_polled_info);
	                                }					 
					}else {
						actual_polled_info = backend_polled_info;
					}

					/*Polled Tab Content Start*/
					infoTable += '<div class="tab-pane fade" id="polled_block"><div class="divide-10"></div>';
					/*Poll Parameter Info*/
					infoTable += "<table class='table table-bordered table-hover'><tbody>";
					infoTable += gmap_self.createTableDataHtml_map(actual_polled_info, 0, false);
					infoTable += "</tbody></table>";
					/*BS-Sector Info End*/

					infoTable += '</div>';
					/*Polled Tab Content End*/

					// 
					if(single_service_polling) {

						/*Poll Now Tab Content Start*/
						infoTable += '<div class="tab-pane fade" id="poll_now_block"><div class="divide-10"></div>';

						if (maps_themetics_poll_flag) {
							infoTable += "<button class='btn btn-default btn-xs themetic_poll_now_btn pull-right' title='Poll Now' \
										  data-complete-text='<i class=\"fa fa-flash\"></i> Poll Now' \
										  data-loading-text='<i class=\"fa fa-spinner fa fa-spin\"> </i> Please Wait'\
										  device_name='"+device_name+"' marker_key='"+marker_key+"' marker_type='"+marker_type+"'\
										  device_type='"+device_type+"'> <i class='fa fa-flash'></i> Poll Now</button>\
										  {0}\
										  <div class='clearfix'></div><div class='divide-10'></div>";

							var reboot_btn_html = '';
							if (enable_reboot_btn && device_type == 'radwin2kbs' && device_tech != 'ptp-bh') {
								reboot_btn_html = "<button title='Soft Reboot' class='btn btn-default power-actions btn-xs pull-right ' \
												  style='margin-right: 10px;' id='power_send_reboot' \
												  device_id='"+device_id+"' data-button-respone='reboot' \
					                              data-complete-text='<i class=\"fa fa-refresh\"></i> Soft Reboot' \
					                              data-loading-text='<i class=\"fa fa-spinner fa-spin\"></i> Please Wait...'> \
					                              <i class='fa fa-refresh'></i> Soft Reboot\
					                              </button>";
							}
							infoTable = infoTable.replace('{0}', reboot_btn_html);
						}

						infoTable += "<table class='table table-bordered table-hover'><tbody>";
						
						if(maps_themetics_poll_flag) {
							// Space for Poll Now Content
							infoTable += "<tr><td colspan='3' style='word-break:break-word;'>\
										  <h5 style='margin-top: 0px;text-decoration: underline;font-weight: bold;'>Polling Data :</h5>\
										  <input type='hidden' name='sparkline_val_input' id='sparkline_val_input'/>\
										  <span id='fetched_val_container'></span>\
										  <span class='divide-10'></span>\
										  <span id='sparkline_container'></span>\
										  </td></tr>";
						}

						/*Polled Parameter Info*/
						for(var i=0; i< poll_now_info.length; i++) {
							var url = "",
								text_class = "",
								service_name = "",
								ds_name = "";
							if(poll_now_info[i]["show"]) {

								// Url
								url = poll_now_info[i]["url"] ? poll_now_info[i]["url"] : "";
								text_class = "text-primary";
								service_name = poll_now_info[i]["service_name"] ? poll_now_info[i]["service_name"] : "";
								ds_name = poll_now_info[i]["ds"] ? poll_now_info[i]["ds"] : "";


								infoTable += "<tr>";
								infoTable += "<td class='"+text_class+"' url='"+url+"'>"+poll_now_info[i]['title']+"</td>";
								infoTable += "<td style='text-align:center'>\
											 <button class='btn btn-default btn-xs perf_poll_now'\
											 service_name='"+service_name+"' ds_name='"+ds_name+"' device_name='"+device_name+"'\
											 device_type='"+device_type+"' title='Poll Now' data-complete-text='<i class=\"fa fa-flash\"></i>' \
				                             data-loading-text='<i class=\"fa fa-spinner fa fa-spin\"> </i>'><i \
				                             class='fa fa-flash'></i>\
				                             </button></td>";

								infoTable += "<td style='width:40%;'>"+poll_now_info[i]['value']+"</td>\
											 </tr>";
							}
						}
						infoTable += "</tbody></table>";
						/*BS-Sector Info End*/

						infoTable += '</div>';
						/*Poll Now Tab Content End*/
					}
				}

				infoTable += '</div>';
				/*Tab-content */

				/*Final infowindow content string*/

				windowContent += "<div class='windowContainer' style='z-index: 300;position:relative;'>\
								  <div class='box border'><div class='box-title'>\
								  <h4><i class='fa fa-map-marker'></i>"+sectorWindowTitle+"</h4>";

				windowContent += "<div class='tools'>"+tools_html+"<a class='close_info_window' title='Close' marker_type='"+marker_type+"' marker_key='"+marker_key+"'>\
								  <i class='fa fa-times text-danger' title='Close'></i></a>\
								  </div></div>\
								  <div class='box-body'>\
								  <div class='' align='center'>"+infoTable+"</div>\
								  <div class='clearfix'></div><div class='pull-right'></div>\
								  <div class='clearfix'></div></div></div></div>";

			} else if(clickedType == 'sub_station') {

				var startPtInfo = [],
					ss_circuit_id = "",
					BsSsWindowTitle = contentObject.windowTitle ? contentObject.windowTitle : contentObject.pointType.toUpperCase(),
					farend_perf_url = contentObject.perf_url ? base_url+""+contentObject.perf_url : "",
					farend_inventory_url = contentObject.inventory_url ? base_url+""+contentObject.inventory_url : "",
					tools_html = "",
					item_index = contentObject.item_index > -1 ? contentObject.item_index : 0,
					ss_tech = contentObject.technology ? $.trim(contentObject.technology.toLowerCase()) : "";
					ss_device_type = contentObject.device_type ? $.trim(contentObject.device_type.toLowerCase()) : "";

				if(ss_toolTip_static && ss_toolTip_static.length > 0) {
					var ss_actual_data = rearrangeTooltipArray(ss_toolTip_static,contentObject.dataset);
					startPtInfo = ss_actual_data;
				} else {
					startPtInfo = contentObject.dataset;
				}
				
				ss_circuit_id = gisPerformanceClass.getKeyValue(startPtInfo,"cktid",true,item_index);

				var pos1 = "",
					pos2 = "";

				if(ss_circuit_id) {
					pos1 = "<a href='"+posLink1+"="+ss_circuit_id+"' class='text-warning' target='_blank'>"+ss_circuit_id+"</a>";
					pos2 = "<a href='"+posLink2+"="+ss_circuit_id+"' class='text-warning' target='_blank'>"+ss_circuit_id+"</a>";
					
					tools_html += "<a href='"+svp_link+"="+ss_circuit_id+"' title='SVP' class='svp_link text-danger' target='_blank'> \
								  SVP\
								  </a>";
				}

				if(farend_perf_url) {
					tools_html += "<a href='"+farend_perf_url+"' target='_blank' title='Performance'><i class='fa fa-bar-chart-o text-info'> </i></a>"
				}

				if(farend_inventory_url) {
					tools_html += "<a href='"+farend_inventory_url+"' target='_blank' title='Inventory'><i class='fa fa-dropbox text-info'> </i></a>";
				}

				/*Tab-content Start*/
				infoTable += '<div class="tab-content">';

				/*Static Tab Content Start*/
				infoTable += '<div class="tab-pane fade active in" id="static_block"><div class="divide-10"></div>';
				infoTable += "<table class='table table-bordered table-hover'><tbody>";

				for(var i=0;i<startPtInfo.length;i++) {

					if(startPtInfo[i]) {
						if(startPtInfo[i].name == 'pos_link1') {
							startPtInfo[i].value = pos1;
						}

						if(startPtInfo[i].name == 'pos_link2') {
							startPtInfo[i].value = pos2;
						}

						if(ptp_tech_list.indexOf(ss_tech) <= -1) {
							if(ptp_not_show_items.indexOf(startPtInfo[i].name) > -1) {
								startPtInfo[i].show = 0;
							}
						} else {
							if(startPtInfo[i].name == 'ss_ip') {
								startPtInfo[i].title = "Far End IP"
							}
						}

						if(startPtInfo[i].show == 1) {
							var val = startPtInfo[i]['value'] || startPtInfo[i]['value'] == 0 ? startPtInfo[i]['value'] : "",
								actual_val = "";

							if(direct_val_keys.indexOf(startPtInfo[i].name) > -1) {
								actual_val = val;
							} else {
								actual_val = String(val).split("|")[item_index] ? String(val).split("|")[item_index] : "";
							}

							infoTable += "<tr><td class='polled_param_td'>"+startPtInfo[i]['title']+"</td><td>"+actual_val+"</td></tr>";
						}
					}
				}

				infoTable += "</tbody></table>";
				/*SS Info End*/

				infoTable += '</div>';
				/*Static Tab Content End*/

				if(contentObject['poll_info']) {

					var backend_polled_info = contentObject['poll_info'],
						actual_polled_info = backend_polled_info,
						poll_now_info = poll_now_info = rearrangeTooltipArray(common_toolTip_poll_now,backend_polled_info);

					if(ptp_tech_list.indexOf(ss_tech) > -1) {
						actual_polled_info = rearrangeTooltipArray(ptp_ss_toolTip_polled,backend_polled_info);
					} else if(ss_tech == 'wimax') {
						actual_polled_info = rearrangeTooltipArray(wimax_ss_toolTip_polled,backend_polled_info);
					} else if(ss_tech == 'pmp'){
							if(ss_device_type == 'radwin5kss' ) {
								actual_polled_info = rearrangeTooltipArray(pmp_radwin5k_ss_toolTip_polled,backend_polled_info);
							} else {
								actual_polled_info = rearrangeTooltipArray(pmp_ss_toolTip_polled,backend_polled_info);}
					}else {
						actual_polled_info = backend_polled_info;
					}

					/*Polled Tab Content Start*/
					infoTable += '<div class="tab-pane fade" id="polled_block"><div class="divide-10"></div>';

					/*Poll Parameter Info*/
					infoTable += "<table class='table table-bordered table-hover'><tbody>";
					infoTable += gmap_self.createTableDataHtml_map(actual_polled_info, 0, false);
					infoTable += "</tbody></table>";
					/*SS Info End*/

					infoTable += '</div>';
					/*Polled Tab Content End*/

					// IF enabled from settings.py
					if(single_service_polling) {

						/*Poll Now Tab Content Start*/
						infoTable += '<div class="tab-pane fade" id="poll_now_block"><div class="divide-10"></div>';

						if (maps_themetics_poll_flag) {
							infoTable += "<button class='btn btn-default btn-xs themetic_poll_now_btn pull-right' title='Poll Now' \
										  data-complete-text='<i class=\"fa fa-flash\"></i> Poll Now' \
										  data-loading-text='<i class=\"fa fa-spinner fa fa-spin\"> </i> Please Wait'\
										  device_name='"+device_name+"' marker_key='"+marker_key+"' marker_type='"+marker_type+"'\
										  device_type='"+device_type+"'><i class='fa fa-flash'></i> Poll Now</button>\
										  {0}\
										  <div class='clearfix'></div><div class='divide-10'></div>";

							var reboot_btn_html = '';
							if (enable_reboot_btn) {
								reboot_btn_html = "<button title='Soft Reboot' class='btn btn-default power-actions btn-xs pull-right ' \
													  style='margin-right: 10px;' id='power_send_reboot' \
													  device_id='"+device_id+"' data-button-respone='reboot' \
						                              data-complete-text='<i class=\"fa fa-refresh\"></i> Soft Reboot' \
						                              data-loading-text='<i class=\"fa fa-spinner fa-spin\"></i> Please Wait...'> \
						                              <i class='fa fa-refresh'></i> Soft Reboot\
						                              </button>";
							}
							infoTable = infoTable.replace('{0}', reboot_btn_html);
						}

						infoTable += "<table class='table table-bordered table-hover'><tbody>";

						if(maps_themetics_poll_flag) {
							// Space for Poll Now Content
							infoTable += "<tr><td colspan='3' style='word-break:break-word;'>\
										  <h5 style='margin-top: 0px;text-decoration: underline;font-weight: bold;'>Polling Data :</h5>\
										  <input type='hidden' name='sparkline_val_input' id='sparkline_val_input'/>\
										  <span id='fetched_val_container'></span>\
										  <span class='divide-10'></span>\
										  <span id='sparkline_container'></span>\
										  </td></tr>";
						}

						/*Polled Parameter Info*/
						for(var i=0; i< poll_now_info.length; i++) {
							var url = "",
								text_class = "",
								service_name = "",
								ds_name = "";
							if(poll_now_info[i]["show"]) {

								// Url
								url = poll_now_info[i]["url"] ? poll_now_info[i]["url"] : "";
								text_class = "text-primary";
								service_name = poll_now_info[i]["service_name"] ? poll_now_info[i]["service_name"] : "";
								ds_name = poll_now_info[i]["ds"] ? poll_now_info[i]["ds"] : "";


								infoTable += "<tr>";
								infoTable += "<td class='"+text_class+"' url='"+url+"'>"+poll_now_info[i]['title']+"</td>";
								infoTable += "<td style='text-align:center'>\
											 <button class='btn btn-default btn-xs perf_poll_now'\
											 service_name='"+service_name+"' ds_name='"+ds_name+"' device_name='"+device_name+"'\
				                             device_type='"+device_type+"' title='Poll Now' data-complete-text='<i class=\"fa fa-flash\"></i>' \
				                             data-loading-text='<i class=\"fa fa-spinner fa fa-spin\"> </i>'><i \
				                             class='fa fa-flash'></i>\
				                             </button></td>";

								infoTable += "<td style='width:40%;'>"+poll_now_info[i]['value']+"</td>\
											 </tr>";
							}
						}
						infoTable += "</tbody></table>";
						/*BS-Sector Info End*/

						infoTable += '</div>';
						/*Poll Now Tab Content End*/
					}
				}

				/*Tab-content End*/
				infoTable += '</div>';

				/*Final infowindow content string*/
				windowContent += "<div class='windowContainer' style='z-index: 300; position:relative;'>\
								  <div class='box border'><div class='box-title'>\
								  <h4><i class='fa fa-map-marker'></i>  "+BsSsWindowTitle+"</h4>";

				windowContent += "<div class='tools'>"+tools_html+"<a class='close_info_window' marker_type='"+marker_type+"' marker_key='"+marker_key+"' title='Close'>\
								  <i class='fa fa-times text-danger'></i></a></div></div>\
								  <div class='box-body'><div class='' align='center'>"+infoTable+"</div>\
								  <div class='clearfix'></div><div class='pull-right'></div>\
								  <div class='clearfix'></div></div></div></div>";
			} else {
				/*Tab-content Start*/
				infoTable += '<div class="tab-content">';

				var startPtInfo = [],
					item_index = contentObject.item_index > -1 ? contentObject.item_index : 0,
					BsSsWindowTitle = contentObject.windowTitle ? contentObject.windowTitle : contentObject.pointType.toUpperCase(),
					bs_id = contentObject.filter_data.bs_id;
					report_type="base_station"

				if(contentObject.dataset) {
					// Rearrange BS tootip info as per actual sequence
					var bs_actual_data = rearrangeTooltipArray(bs_toolTip_static,contentObject.dataset);
					startPtInfo = bs_actual_data;
				}

				var report_download_btn = "";
					if(bs_id) {
						report_download_btn = '<li><button class="btn btn-sm btn-default download_report_btn" \
											   data-complete-text="Download L2 Report"\
										  	   data-loading-text="Please Wait..."\
											   item_id="'+bs_id+'"\
											   type="'+report_type+'">Download L2 Report</button></li>';
					}
				/*Static Tab Content Start*/
				infoTable += '<div class="tab-pane fade active in" id="static_block"><div class="divide-10"></div>';
				infoTable += "<table class='table table-bordered table-hover'><tbody>";

				for(var i=0;i<startPtInfo.length;i++) {
					if(startPtInfo[i]) {
						if(startPtInfo[i].show) {
							var val = startPtInfo[i]['value'] || startPtInfo[i]['value'] == 0 ? startPtInfo[i]['value'] : "",
								actual_val = String(val).split("|")[item_index] ? String(val).split("|")[item_index] : "";

							infoTable += "<tr><td class='polled_param_td'>"+startPtInfo[i]['title']+"</td><td>"+actual_val+"</td></tr>";
						}
					}
				}

				if(clickedType == "base_station" && contentObject.bh_dataset) {
					var severity_symbol = "",
						bhSeverity = contentObject.bhSeverity ? $.trim(contentObject.bhSeverity.toLowerCase()) : "",
						severity_title = bhSeverity ? bhSeverity.toUpperCase() : "",
						txt_color = "",
						fa_icon_class = "fa-circle";

					if(bhSeverity) {
						if(green_status_array.indexOf(bhSeverity)  > -1) {
					        txt_color = green_color ? green_color : "#468847";
					        fa_icon_class = "fa-check-circle";
					    } else if(red_status_array.indexOf(bhSeverity)  > -1) {
					        txt_color = red_color ? red_color : "#b94a48";
					        fa_icon_class = "fa-times-circle";
					    } else if(orange_status_array.indexOf(bhSeverity)  > -1) {
					        txt_color = orange_color ? orange_color : "#f0ad4e";
					        fa_icon_class = "fa-warning";
					    } else if(down_status_array.indexOf(bhSeverity)  > -1) {
					        txt_color = red_color ? red_color : "#b94a48";
					        fa_icon_class = "fa-warning";
					    } else {
					        // pass
					    }
					}
					
					severity_symbol = '';
				    severity_symbol += '<i title = "'+severity_title+'" class="fa '+fa_icon_class+'" ';
				    severity_symbol += 'style="color:'+txt_color+';vertical-align: middle;margin-left:5px;">&nbsp;</i>';

					infoTable += "<tr><td colspan='2'><b>Backhaul Info "+severity_symbol+"</b></td></tr>";

					// Rearrange BS tootip info as per actual sequence
					var bh_actual_data = rearrangeTooltipArray(bh_toolTip_static,contentObject.bh_dataset);

					for(var i=0;i<bh_actual_data.length;i++) {
						if(bh_actual_data[i].show == 1) {
							var val = bh_actual_data[i]['value'] || bh_actual_data[i]['value'] == 0 ? bh_actual_data[i]['value'] : "",
								actual_val = String(val).split("|")[item_index] ? String(val).split("|")[item_index] : "";

							infoTable += "<tr><td>"+bh_actual_data[i].title+"</td><td>"+actual_val+"</td></tr>";
						}
					}
				}

				infoTable += "</tbody></table>";
				infoTable += '</div>';
				/*Static Tab Content End*/

				/*Polled Tab Content Start*/
				infoTable += '<div class="tab-pane fade" id="polled_block"><div class="divide-10"></div>';

				infoTable += "<table class='table table-bordered table-hover'><tbody>";

				var backend_BH_polled_info = contentObject.bhInfo_polled ? contentObject.bhInfo_polled : [],
					actual_polled_params = [];

				if(contentObject.bh_device_type) {
					var bh_device_type = $.trim(contentObject.bh_device_type).toLowerCase();
					if(bh_device_type == 'pine') {
						actual_polled_params = rearrangeTooltipArray(mrotech_bh_toolTip_polled,backend_BH_polled_info);
					} else if(bh_device_type == 'switch') {
						actual_polled_params = rearrangeTooltipArray(switch_bh_toolTip_polled,backend_BH_polled_info);
					} else if(bh_device_type == 'rici') {
						actual_polled_params = rearrangeTooltipArray(rici_bh_toolTip_polled,backend_BH_polled_info);
					} else {
						actual_polled_params = backend_BH_polled_info;
					}
				}

				for(var i=0;i<actual_polled_params.length;i++) {
					var text_class = "",
						url = "";
					if(actual_polled_params[i].show == 1) {
						// Url
						url = actual_polled_params[i]["url"] ? actual_polled_params[i]["url"] : "";
						text_class = "text-primary";
						infoTable += "<tr><td class='"+text_class+"' url='"+url+"'>"+actual_polled_params[i].title+"</td><td>"+actual_polled_params[i].value+"</td></tr>";
					}
				}

				infoTable += "</tbody></table>";
				infoTable += '</div>';

				/*Final infowindow content string*/
				windowContent += "<div class='windowContainer' style='z-index: 300; position:relative;'>\
								  <div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>  \
								  "+BsSsWindowTitle+"</h4><div class='tools'><a class='close_info_window' title='Close'>\
								  <i class='fa fa-times text-danger'></i></a></div></div>\
								  <div class='box-body'><div align='center'>"+infoTable+"</div>\
								  <div class='clearfix'></div><div class='pull-right'></div><div class='clearfix'>\
								  </div><ul class='list-unstyled list-inline' align='left'>"+report_download_btn+"</ul></div></div></div>";
			}

			if(isDebug) {
				var time_diff = (new Date().getTime() - start_date_infowindow.getTime())/1000;
				console.log("Make Info Window HTML End Time :- "+ time_diff + " Seconds");
				console.log("***********************************");
				start_date_infowindow = "";
			}

			/*Return the info window content*/
			callback(windowContent);
		});
	};

	/**
	 * This function create table structur HTML for tooltip data
	 * @method createTableDataHtml_map
	 * @param data_obj {Array}, It contains the object array of items which are to be shown on tooltip
	 * @param item_index {Number}, It contains item index to show the correct info from multiple
	 * @param is_static {Boolean}, It contains the boolean flag to check that the info html is for static data for polled
	 */
	this.createTableDataHtml_map = function(data_obj, item_index, is_static, pos1, pos2) {

		var table_html = "";

		if(data_obj && data_obj.length) {
			for(var i=0; i< data_obj.length; i++) {
				var url = "",
					text_class = "",
					highlight_class = "";

				if(data_obj[i]["show"]) {
					// GET text color as per the severity of device
					var severity = data_obj[i]["severity"],
						severity_obj = nocout_getSeverityColorIcon(severity),
						text_color = severity_obj.color ? severity_obj.color : "";

					if(data_obj[i]["name"] == 'pos_link1') {
						data_obj[i]["value"] = pos1 ? pos1 : "";
					}

					if(data_obj[i]["name"] == 'pos_link2') {
						data_obj[i]["value"] = pos2 ? pos2 : "";
					}

					if(data_obj[i]["name"] == 'pmp_port') {
						highlight_class = "text-warning text-bold"
					}
					
					var val = data_obj[i]["value"];

					if(direct_val_keys.indexOf(data_obj[i].name) > -1 || !is_static) {

						// current value
						actual_val = val;

						// This is useful only for polled data
						url = data_obj[i]["url"] ? $.trim(data_obj[i]["url"]) : "";
					} else {
						actual_val = String(val).split("|")[item_index] ? String(val).split("|")[item_index] : "";
					}

					table_html += "<tr style='color:"+text_color+";'><td class='"+highlight_class+"' url='"+url+"'>\
								  "+data_obj[i]['title']+"</td><td>"+actual_val+"</td></tr>";
				}
			}
		}

		return table_html;
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
		if(isDebug) {
			console.log("Calculate Fresnel Zone");
			console.log("Calculate Fresnel Zone Start Time :- "+ new Date().toLocaleString());
		}

		// Disable Fresnel Zone Button
		$(".fresnel_btn").button("loading");

		/*Save sector & ss name in global variables*/
		bts1_name = sector_ss_obj.sector_name;
		bts2_name = sector_ss_obj.ss_name;

		fresnelData['bts1_title'] = sector_ss_obj.sector_title ? sector_ss_obj.sector_title : "BS";
		fresnelData['bts2_title'] = sector_ss_obj.ss_title ? sector_ss_obj.ss_title : "SS";
		fresnelData['bts1_alias'] = sector_ss_obj.sector_Alias;
		fresnelData['bts2_customerName'] = sector_ss_obj.ss_customerName;
		fresnelData['bts2_circuitId'] = sector_ss_obj.ss_circuitId;
		fresnel_isBSLeft = sector_ss_obj.isBSLeft;

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

	    if(isDebug) {
			console.log("Calculate Fresnel Zone End Time :- "+ new Date().toLocaleString());
			console.log("*********************************");
		}
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
		if(isDebug) {
			console.log("Get Fresnel Zone Path");
			console.log("Get Fresnel Zone Path Start Time :- "+ new Date().toLocaleString());
		}
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
	    if(isDebug) {
			console.log("Get Fresnel Zone Path End Time :- "+ new Date().toLocaleString());
			console.log("************************");
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
			var left_str = '<div class="col-md-12"><b>'+fresnelData.bts1_title+'</b><br/>'+fresnelData.bts1_alias+"<br />"+bts1_name+'<br /> (Height)</div>';
				// right_str = '<div class="col-md-12"><b>'+fresnelData.bts2_title+'</b><br/>'+fresnelData.bts2_customerName+"<br />"+fresnelData.bts2_circuitId+ "<br />"+ bts2_name+' (Height)</div>';
			var right_str = '<div class="col-md-12"><b>'+fresnelData.bts2_title+'</b><br/>'+fresnelData.bts2_circuitId+'<br />(Height)</div>';
			
			if(fresnel_isBSLeft == 0) {
				// left_str = '<div class="col-md-12"><b>'+fresnelData.bts2_title+'</b><br/>'+fresnelData.bts2_customerName+"<br />"+fresnelData.bts2_circuitId+ "<br />"+ bts2_name+' (Height)</div>';
				left_str = '<div class="col-md-12"><b>'+fresnelData.bts2_title+'</b><br/>'+fresnelData.bts2_circuitId+ '<br/> (Height)</div>';
				right_str = '<div class="col-md-12"><b>'+fresnelData.bts1_title+'</b><br/>'+fresnelData.bts1_alias+"<br />"+bts1_name+'<br /> (Height)</div>';
			}

			/*Fresnel template String*/
			var leftSlider = '<div class="col-md-2" align="center">\
							  <div class="col-md-8 col-md-offset-2">\
						 	  <input type="text" style="width:73%;float:left;background: #FFF;" id="antinaVal1" class="form-control" value="'+antenaHight1+'" disabled> \
						 	  <span style="top:5px;position:relative;">m</span>\
						 	  </div><div class="clearfix"></div>\
						 	  <div id="antina_height1" style="height:300px;" class="slider slider-blue"></div>'+left_str+'</div>';

			var chart_detail = '<div id="chart-details">\
								<div>\
								<span id="longitude-lbl" class="chart-detail-lbl">Longitude </span>\
								<span id="longitude"></span>\
								</div><div>\
								<span id="latitude-lbl" class="chart-detail-lbl">Latitude </span>\
								<span id="latitude"></span>\
								</div><div>\
								<span id="distance-lbl" class="chart-detail-lbl">Distance </span>\
								<span id="distance"></span>\
								</div><div>\
								<span id="altitude-lbl" class="chart-detail-lbl">Altitude </span>\
								<span id="altitude"></span>\
								</div><div>\
								<span id="obstacle-lbl" class="chart-detail-lbl">Obstacle </span>\
								<span id="obstacle"></span>\
								</div><div>\
								<span id="los-lbl" class="chart-detail-lbl">LOS </span>\
								<span id="los"></span>\
								</div><div>\
								<span id="fresnel1-lbl" class="chart-detail-lbl">Fresnel-1 </span>\
								<span id="fresnel1"></span>\
								</div><div>\
								<span id="fresnel2-lbl" class="chart-detail-lbl">Fresnel-2 </span>\
								<span id="fresnel2"></span>\
								</div><div>\
								<span id="fresnel2-altitude-lbl" class="chart-detail-lbl">Clearance </span>\
								<span id="fresnel-altitude"></span>\
								</div></div>';

			var middleBlock = '<div class="col-md-8 mid_fresnel_container">\
							   <div align="center">\
							   <div class="col-md-12">Clearance Factor</div>\
							   <div class="col-md-4 col-md-offset-3">\
							   <div id="clear-factor" class="slider slider-red"></div>\
							   </div><div class="col-md-2">\
							   <input type="text" id="clear-factor_val" style="background: #FFF;" class="form-control" disabled value="'+clear_factor+'">\
							   </div><div class="clearfix"></div></div>\
							   <div id="chart_div" style="width:600px;max-width:100%;height:300px;"></div>\
							   <div class="clearfix divide-10"></div>\
							   <div id="pin-points-container" class="col-md-12" align="center"></div></div>';
			
			var rightSlider = '<div class="col-md-2" align="center">\
							   <div class="col-md-8 col-md-offset-2">\
							   <input type="text" id="antinaVal2" style="width:73%;float:left;background: #FFF;" class="form-control" disabled value="'+antenaHight2+'">\
							   <span style="top:5px;position:relative;">m</span>\
							   </div><div class="clearfix"></div>\
							   <div id="antina_height2" class="slider slider-blue" style="height:300px;"></div>'+right_str+'</div>';

			var fresnelTemplate = "<div class='fresnelContainer row' \
								   style='height:400px;overflow-y:auto;z-index:9999;position:relative;'\
								   >"+leftSlider+" "+middleBlock+" "+rightSlider+"<div class='clearfix'></div>"+chart_detail+"</div>";


			/*Call the bootbox to show the popup with Fresnel Zone Graph*/
			bootbox.dialog({
				message: fresnelTemplate,
				title: '<i class="fa fa-dot-circle-o">&nbsp;</i> Fresnel Zone'
			});

			$(".modal-dialog").css("width","80%");

		} else {

			isDialogOpen = true;
		}

		// Enable Fresnel Zone Button after 0.5 sec
		setTimeout(function() {
			$(".fresnel_btn").button("complete");
		},500);

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

		/*Plotting chart with points array using jquery.flot.js*/
		var fresnelChart = $.plot(
			$("#chart_div"),
			[
				{
					data: dataPinpoints,
					label: "Pin Points",
					lines: {
						show: false
					},
					points: {
						show: true ,
						fill: true,
						radius: 1
					},
					bars: {
						show:true,
						lineWidth:1,
						fill:false,
						barWidth:0
					}
				},
				{
					data: dataAltitude,
					label: "Altitude",
					lines: {
						show: true,
						fill: 0.8,
						fillColor: altitudeColor
					}
				},
				{
					data: dataLOS,
					label: "LOS",
					lines: {
						show: true
					}
				},
				{
					data: dataFresnel1,
					label: "Fresnel-1 U"
				},
				{
					data: dataFresnel2,
					label: "Fresnel-2 L"
				}
			],
			{
				series: {
					lines: { show: true},
					points: { show: false },
					colors: [{ opacity: 0.8 }, { brightness: 0.6, opacity: 0.8 } ]
				},
				grid: { hoverable: true, clickable: true, autoHighlight: true, backgroundColor: { colors: ["#ccc", "#fff"] }},
				yaxis: { min:minYChart, max:  maxYChart},
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

		var yaxisLabel = $("<div class='axisLabel yaxisLabel'></div>").text("Height (m)").appendTo("#chart_div");
		var xaxisLabel = $("<div class='axisLabel xaxisLabel'></div>").text("Distance (km)").appendTo("#chart_div");
		// yaxisLabel.css("margin-top", yaxisLabel.width() / 2 - 20);

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
			var pin_point_html = '<div id="pin-point-'+index+'" class="pin-point col-md-5" \
								  pointid="'+ index +'"><span class="pin-point-name">Point \
								  '+ index +' - <input name="pinpoint'+ index +'" class="userpinpoint" \
								  type="text" size="2" value="0" /> m at <span class="point-distance'+ index +'">\
								  '+ parseFloat(latLongArray[index][3]).toFixed(2) +'</span> Km</span>\
								  <span id="pin-point-remove'+index+'" class="pin-point-remove">X</span></div>';

			$('#pin-points-container').append(pin_point_html);
			
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
		
		if((antenaHight1 != $("#antinaVal1").val()) || (antenaHight2 != $("#antinaVal2").val())) {
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
				"ss_circuitId" : fresnelData.bts2_circuitId,
				"isBSLeft" : fresnel_isBSLeft
			};

			gmap_self.claculateFresnelZone(fresnelLat1,fresnelLon1,fresnelLat2,fresnelLon2,antenaHight1,antenaHight2,sector_ss_obj);
		}
	};

	/**
	 * This function fetch the basic filters from appropriate API & this populate the data to respective dropdowns
	 * @method getBasicFilters
	 */
	this.getBasicFilters = function() {
		/*Populate City & State*/
		var state_array = Object.keys(state_city_obj);

		var state_option = "";
		state_option = "<option value=''>Select State</option>";

		for(var i=state_array.length;i--;) {
			state_option += "<option value='"+i+1+"'>"+state_array[i]+"</option>";
		}

		$("#state").html(state_option);

		var city_option = "";
		city_option = "<option value=''>Select City</option>";

		for(var i=all_cities_array.length;i--;) {
			city_option += "<option value='"+i+1+"'>"+all_cities_array[i]+"</option>";
		}

		$("#city").html(city_option);

		/*Populate Technology & Vendor*/
		var technology_array = Object.keys(tech_vendor_obj);

		var tech_option = "";
		tech_option = "<option value=''>Select Technology</option>";

		for(var i=technology_array.length;i--;) {
			tech_option += "<option value='"+i+1+"'>"+technology_array[i]+"</option>";
		}

		$("#technology").html(tech_option);
		// $("#polling_tech").html(tech_option);

		var vendor_option = "";
		vendor_option = "<option value=''>Select Vendor</option>";

		for(var i=all_vendor_array.length;i--;) {
			vendor_option += "<option value='"+i+1+"'>"+all_vendor_array[i]+"</option>";
		}

		$("#vendor").html(vendor_option);

		/*Ajax call for Live polling technology data*/
		$.ajax({
			url : base_url+"/"+"device/filter/1/",
			success : function(response) {

				var result = "";
				// Type check of response
				if(typeof response == 'string') {
					result = JSON.parse(response);
				} else {
					result = response;
				}

				var techData = {};
				if(typeof result === 'string') {
					techData = JSON.parse(result).data.objects.technology.data;
				} else {
					techData = result.data.objects.technology.data;
				}

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

		// Load Advance Search.
		gmap_self.loadAdvanceSearch();

		// Load Advance Filter
		gmap_self.loadAdvanceFilters();

		var SSToolTipInfo = ss_toolTip_static ? ss_toolTip_static : false;
		
		if(last_selected_label) {
			if($("#apply_label").hasClass("btn-success")) {
                $("#apply_label").removeClass("btn-success");
            }

            if(!$("#apply_label").hasClass("btn-danger")) {
                $("#apply_label").addClass("btn-danger");
                $("#apply_label").html("Remove Label")
            }
		}

		if(SSToolTipInfo) {
			var labelSelectHtml = '<option value="">Select Label</option>';
			//Loop ss info to populate 'Select Label' selectbox
			for(var i=0;i<SSToolTipInfo.length;i++) {
				var isSelected = "";
				if (SSToolTipInfo[i]['name'].indexOf('pos_link') > -1) {
					continue;
				}
				if($.trim(last_selected_label) === $.trim(SSToolTipInfo[i]['name'])) {
					isSelected = 'selected="selected"';
				}
				labelSelectHtml += '<option value="'+$.trim(SSToolTipInfo[i]['name'])+'" '+isSelected+'>'+$.trim(SSToolTipInfo[i]['title'])+'</option>';
			}
			// If select box exist them update the HTML.
			if($("#static_label").length) {
				$("#static_label").html(labelSelectHtml);
			}
		}

		/*Reset the flag*/
		isFirstTime = 0;
	};

	/**
	 * This function removes extra labels & show only filtered labels on gmap
	 */
	this.removeExtraPerformanceBoxes= function() {
		
		if(recallPerf != "") {
			clearTimeout(recallPerf);
			recallPerf = "";
		}
		
		for(var i=0; i< labelsArray.length; i++) {
			labelsArray[i].hide();
		}
		for(var j=0; j< labelsArray_filtered.length; j++) {
			labelsArray_filtered[j].show();
		}

		/*Restart Perf call as per new data*/
		if(isPerfCallStopped === 0 && isPerfCallStarted == 0) {
    		var bs_list = getMarkerInCurrentBound();
        	if(bs_list.length > 0 && isCallCompleted == 1) {
        		gisPerformanceClass.start(bs_list);
        	}
    	}
	};

	/**
	 * This function performs advance search as per given params on devices data
	 * @method applyAdvanceFilters
	 */
	this.applyAdvanceFilters = function() {

        /*Hide the spinner*/
        hideSpinner();

        if(!($("#advFilterContainerBlock").hasClass("hide"))) {
            $("#advFilterContainerBlock").addClass("hide");
        }

        if($("#removeFilterBtn").hasClass("hide")) {
            $("#removeFilterBtn").removeClass("hide");
        }
        /*show The loading Icon*/
        $("#loadingIcon").show();

        /*Enable the refresh button*/
        $("#resetFilters").button("loading");

    	if(window.location.pathname.indexOf("gearth") > -1) {
    		/************************Google Earth Code***********************/

    		/*Clear all the elements from google earth*/
	        earth_instance.clearEarthElements();
	        earth_instance.clearStateCounters();

	        var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);
			lookAt.setLatitude(21.0000);
			lookAt.setLongitude(78.0000);
			lookAt.setRange(5492875.865539902);
			// Update the view in Google Earth 
			ge.getView().setAbstractView(lookAt); 
			// data_for_filters_earth = data_to_plot;
			isApiResponse = 0;

    	} else if (window.location.pathname.indexOf('wmap') > -1) {
			ccpl_map.setCenter(
				new OpenLayers.LonLat(
					whiteMapSettings.mapCenter[0],
					whiteMapSettings.mapCenter[1]
				),
				1,
				true,
				true
			);
			ccpl_map.zoomTo(1);
    	} else {
            /*Clear Existing Labels & Reset Counters*/
            gmap_self.clearStateCounters();
            mapInstance.fitBounds(new google.maps.LatLngBounds(new google.maps.LatLng(india_center_lat,india_center_lon)));
            mapInstance.setZoom(5);
            // data_for_filters = data_to_plot;
            isApiResponse = 0;
    	}
    	gmap_self.updateStateCounter_gmaps(false);
	};

	
	/**
	 * This function loads advance filters form & bind data load events on select2
	 * @method loadAdvanceFilters
	 */
	this.loadAdvanceFilters = function() {

        /*Initialize the select2 for All Fields*/
        $("#filter_technology").select2({
        	multiple: true,
        	minimumInputLength: 2,
        	query: function (query) {
        		var bs_technology_array = [];
        		var searchPattern = new RegExp('^' + query.term, 'i');
        		var filtered_data = all_devices_loki_db.where(function(obj) {
        			var technologies = obj.tech_str.toLowerCase();
        			if(technologies.search(query.term.toLowerCase()) > -1) {
	        			return true;
        			} else {
        				return false;
        			}
        		});

		        var data = {results: []}, i, j, s;
		        // var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < filtered_data.length; i++) {
		        	var technology_list = filtered_data[i].tech_str.split("|");
        			for(var j=0;j<technology_list.length;j++) {
        				if(searchPattern.test(technology_list[j])) {
        					if(data.results.length >= 40) {
        						break;
        					} else {
					        	if(bs_technology_array.indexOf(technology_list[j]) < 0) {
					        		bs_technology_array.push(technology_list[j]);
					            	data.results.push({id: technology_list[j], text: technology_list[j], value : technology_list[j]});
					        	}
				        	}
			        	}
    				}
		        }
		        query.callback(data);
		    }
        });

        $("#filter_vendor").select2({
        	multiple: true,
        	minimumInputLength: 3,
        	query: function (query) {
        		var bs_vendor_array = [],
        			searchPattern = new RegExp('^' + query.term, 'i'),
        			selected_technology = $("#filter_technology").select2("val");

        		var filtered_data = all_devices_loki_db.where(function(obj) {
        			var vendors = obj.vendor_str.toLowerCase();
        			if(vendors.search(query.term.toLowerCase()) > -1) {
	        			return true;
        			} else {
        				return false;
        			}
        		});

		        var data = {results: []}, i, j, s;
		        var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < filtered_data.length; i++) {
		        	var sectors = filtered_data[i].sectors;
        			for(var j=0;j<sectors.length;j++) {
        				var condition = selected_technology.length > 0 ? selected_technology.indexOf(sectors[j].technology) > -1 : true;
        				if(condition) {
	        				if(searchPattern.test(sectors[j].vendor)) {
	        					if(data.results.length >= 40) {
	        						break;
	        					} else {
						        	if(bs_vendor_array.indexOf(sectors[j].vendor) < 0) {
						        		bs_vendor_array.push(sectors[j].vendor);
						            	data.results.push({id: sectors[j].vendor, text: sectors[j].vendor, value : sectors[j].vendor});
						        	}
					        	}
				        	}
        				}
    				}
		        }
		        query.callback(data);
		    }
        });

        $("#filter_state").select2({
        	multiple: true,
        	minimumInputLength: 3,
        	query: function (query) {
        		var showing_states = [];
        		var filtered_data = all_devices_loki_db.where(function(obj) {
        			var searchPattern = new RegExp('^' + query.term, 'i');
        			if(searchPattern.test(obj.state)) {
        				return true;
        			} else {
        				return false;
        			}
        		});

		        var data = {results: []}, i, j, s;
		        var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < filtered_data.length; i++) {
		        	if(showing_states.indexOf(filtered_data[i].state) < 0) {
		        		if(data.results.length >= 40) {
    						break;
    					} else {
			        		showing_states.push(filtered_data[i].state);
			            	data.results.push({
			            		id: filtered_data[i].state,
			            		text: filtered_data[i].state,
			            		value : filtered_data[i].state
		            		});
		            	}
		        	}
		        }
		        query.callback(data);
	        }
        });

        $("#filter_city").select2({
        	multiple: true,
        	minimumInputLength: 3,
        	query: function (query) {
        		var showing_cities = [],
        			selected_state = $("#filter_state").select2("val"),
        			searchPattern = new RegExp('^' + query.term, 'i');
        			
        		var filtered_data = all_devices_loki_db.where(function(obj) {
        			if(searchPattern.test(obj.city)) {
        				return true;
        			} else {
        				return false;
        			}
        		});

		        var data = {results: []}, i, j, s;
		        var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < filtered_data.length; i++) {
		        	if(showing_cities.indexOf(filtered_data[i].city) < 0) {
		        		if(data.results.length >= 40) {
    						break;
    					} else {
			        		if(selected_state.length > 0) {
			        			if(selected_state.indexOf(filtered_data[i].state) > -1) {
					            	data.results.push({id: filtered_data[i].city, text: filtered_data[i].city, value : filtered_data[i].city});
			        			}
			        		} else {
				            	data.results.push({id: filtered_data[i].city, text: filtered_data[i].city, value : filtered_data[i].city});		        			
			        		}
			        		// Push city data to array
			        		showing_cities.push(filtered_data[i].city);
		        		}
		        	}
		        }
		        query.callback(data);
		    }
        });

		$("#filter_frequency").select2({
        	multiple: true,
        	minimumInputLength: 2,
        	query: function (query) {
        		var sector_freq_array = [],
        			searchPattern = new RegExp('^' + query.term, 'i');

        		var filtered_data = all_devices_loki_db.where(function(obj) {
        			var frequencies = obj.freq_str.toLowerCase();
        			if(frequencies.search(query.term.toLowerCase()) > -1) {
	        			return true;
        			} else {
        				return false;
        			}
        		});

		        var data = {results: []}, i, j, s;
		        // var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < filtered_data.length; i++) {
		        	var freq_list = filtered_data[i].freq_str.split("|");
        			for(var j=0;j<freq_list.length;j++) {
        				if(searchPattern.test(freq_list[j])) {
        					if(data.results.length >= 40) {
        						break;
        					} else {
					        	if(sector_freq_array.indexOf(freq_list[j]) < 0 && freq_list[j] != 'NA') {
					        		sector_freq_array.push(freq_list[j]);
					            	data.results.push({id: freq_list[j], text: freq_list[j], value : freq_list[j]});
					        	}
        					}
			        	}
    				}
		        }
		        query.callback(data);
		    }
        });

		$("#filter_polarization").select2({
        	multiple: true,
        	minimumInputLength: 3,
        	query: function (query) {
        		var polarization_array = [],
        			searchPattern = new RegExp('^' + query.term, 'i');

        		var filtered_data = all_devices_loki_db.where(function(obj) {
        			var sectors = obj.sectors;
        			for(var i=0;i<sectors.length;i++) {
	        			if(searchPattern.test(sectors[i].polarization)) {
	        				return true;
	        			} else {
	        				return false;
	        			}
        			}
        		});

		        var data = {results: []}, i, j, s;
		        var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < filtered_data.length; i++) {
		        	var sectors = filtered_data[i].sectors;
        			for(var j=0;j<sectors.length;j++) {
        				if(searchPattern.test(sectors[j].polarization)) {
        					if(data.results.length >= 40) {
        						break;
        					} else {
					        	if(polarization_array.indexOf(sectors[j].polarization.toLowerCase()) < 0 && sectors[j].polarization != 'NA') {
					        		polarization_array.push(sectors[j].polarization.toLowerCase());
					            	data.results.push({id: sectors[j].polarization, text: sectors[j].polarization, value : sectors[j].polarization});
					        	}
				        	}
			        	}
    				}
		        }
		        query.callback(data);
		    }
        });

        hideSpinner();
	};

	/**
	 * This function loads advance search form & bind data load events on select2
	 * @method loadAdvanceSearch
	 */
	this.loadAdvanceSearch = function() {

        /*Initialize the select2 for All Fields*/
        $("#search_name").select2({
        	multiple: true,
        	minimumInputLength: 3,
        	query: function (query) {
        		var bs_name_array = [];
        		var filtered_data = all_devices_loki_db.where(function(obj) {
        			// Special characters handling
        			var entered_txt = query.term.replace(/[.?*+^$[\]\\(){}|-]/g, "\\$&"),
        				searchPattern = new RegExp('^' + entered_txt, 'i');

        			if(searchPattern.test(obj.alias)) {
        				return true;
        			} else {
        				return false;
        			}
        		});

		        var data = {results: []}, i, j, s;
		        var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < filtered_data.length; i++) {
		        	if(filtered_data[i].alias) {
		        		if(data.results.length >= 40) {
    						break;
    					} else {
				        	if(bs_name_array.indexOf(filtered_data[i].alias) < 0) {
				        		bs_name_array.push(filtered_data[i].alias);
				            	data.results.push({id: filtered_data[i].alias, text: filtered_data[i].alias, value : filtered_data[i].alias});
				        	}
			        	}
		        	}
		        }
		        query.callback(data);
		    }
        });

        $("#search_sector_configured_on").select2({
        	multiple: true,
        	minimumInputLength: 3,
        	query: function (query) {
        		var searchPattern = new RegExp('^' + query.term, 'i'),
        			ip_address_array = [];

        		var filtered_data = all_devices_loki_db.where(function(obj) {
        			var ipAddress = obj.sector_configured_on_devices.toLowerCase();
        			if(ipAddress.search(query.term.toLowerCase()) > -1) {
        				return true;
					} else {
						return false;
					}
        		});

		        var data = {results: []}, i, j, s;
		        var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < filtered_data.length; i++) {
		        	var ips = filtered_data[i].sector_configured_on_devices.split("|");
		        	for(var j=0;j<ips.length;j++) {
		        		if(searchPattern.test(ips[j])) {
		        			if(data.results.length >= 40) {
        						break;
        					} else {
			        			if(ip_address_array.indexOf(ips[j]) < 0) {
			        				ip_address_array.push(ips[j]);
			            			data.results.push({id: ips[j], text: ips[j], value : ips[j]});
			        			}
		        			}
		        		}
		        	}
		        }
		        query.callback(data);
		    }
        });

        $("#search_circuit_ids").select2({
        	multiple: true,
        	minimumInputLength: 3,
        	query: function (query) {
        		var entered_txt = query.term.replace(/[.?*+^$[\]\\(){}|-]/g, "\\$&"),
        			searchPattern = new RegExp('^' + entered_txt, 'i'),
        			circuit_id_array = [];
        		var filtered_data = all_devices_loki_db.where(function(obj) {
        			var circuit_Ids = obj.circuit_ids.toLowerCase();
        			if(circuit_Ids.search(query.term.toLowerCase()) > -1) {
        				return true;
        			} else {
						return false;
					}
        		});

		        var data = {results: []}, i, j, s;
		        var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < filtered_data.length; i++) {
		        	var circuit_ids = filtered_data[i].circuit_ids.split("|");
		        	for(var j=0;j<circuit_ids.length;j++) {
		        		if(searchPattern.test(circuit_ids[j])) {
		        			if(data.results.length >= 40) {
        						break;
        					} else {
			        			if(circuit_id_array.indexOf(circuit_ids[j]) === -1) {
			        				circuit_id_array.push(circuit_ids[j]);
			            			data.results.push({id: circuit_ids[j], text: circuit_ids[j], value : circuit_ids[j]});
			        			}
		        			}
		        		}
		        	}
		        }
		        query.callback(data);
	        }
        });

        $("#search_city").select2({
        	multiple: true,
        	minimumInputLength: 3,
        	query: function (query) {
        		var showing_cities = [];
        		var filtered_data = all_devices_loki_db.where(function(obj) {
        			var searchPattern = new RegExp('^' + query.term, 'i');
        			if(obj.city) {
	        			if(searchPattern.test(obj.city)) {
	        				return true;
	        			} else {
	        				return false;
	        			}
        			} else {
        				return false;
        			}
        		});

		        var data = {results: []}, i, j, s;
		        var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < filtered_data.length; i++) {
		        	if(filtered_data[i].city) {
		        		if(data.results.length >= 40) {
    						break;
    					} else {
				        	if(showing_cities.indexOf(filtered_data[i].city) < 0) {
				        		showing_cities.push(filtered_data[i].city);
				            	data.results.push({id: filtered_data[i].city, text: filtered_data[i].city, value : filtered_data[i].city});
				        	}
			        	}
		        	}
		        }
		        query.callback(data);
		    }
        });

        hideSpinner();
	};

	/**
	 * This function returns select2 selected values array as per given param
	 * @method prepareSelect2Array
	 * @param data_list {Array}, It contains the select2 selected values JSON array
	 * @return
	 */
	this.prepareSelect2Array = function(data_list) {
		var values_list = []
		
		if(data_list && data_list.length > 0) {
			for(var i=0;i<data_list.length;i++) {
				if(data_list[i] && data_list[i].value) {
					var selected_val = $.trim(String(data_list[i].value)).toLowerCase();
					if(values_list.indexOf(selected_val) == -1) {
						values_list.push(selected_val);
					}
				}
			}
		}

		return values_list;
	};

	/**
     * This function return selected filtering(Basic + Advance) items array
     * @method getSelectedFilteringItems
     * @return selected_filtering_array {JSON Object}, It contains selected filtering(Basic + Advance) items JSON list.
     */
	this.getSelectedFilteringItems = function() {

		var has_technology = $("#filter_technology").select2('val').length > 0,
			has_vendor = $("#filter_vendor").select2('val').length > 0,
			has_city_filter = $("#filter_city").select2('val').length > 0,
			has_state = $("#filter_state").select2('val').length > 0,
			has_frequency = $("#filter_frequency").select2('val').length > 0,
			has_polarization = $("#filter_polarization").select2('val').length > 0,
			technology_data = $("#filter_technology").select2('data'),
			vendor_data = $("#filter_vendor").select2('data'),
			city_filter_data = $("#filter_city").select2('data'),
			state_data = $("#filter_state").select2('data'),
			frequency_data = $("#filter_frequency").select2('data'),
			polarization_data = $("#filter_polarization").select2('data'),
			technology_filter = [],
			vendor_filter = [],
			city_filter = [],
			state_filter = [],
			frequency_filter = [],
			polarization_filter = [],
			selected_filters_data = {
				"basic" : {
					"technology" : $.trim($("#technology option:selected").text()),
					"vendor" : $.trim($("#vendor option:selected").text()),
					"state" : $.trim($("#state option:selected").text()),
					"city" : $.trim($("#city option:selected").text())
				},
				"advance" : {
					"technology" : [],
					"vendor" : [],
					"city" : [],
					"state" : [],
					"frequency" : [],
					"polarization" : []
				}
			};


		// If any technology filter is applied the get selected technology
		if(has_technology && technology_data.length > 0) {
			technology_filter = gmap_self.prepareSelect2Array(technology_data);
		}

		// If any vendor filter is applied the get selected vendores
		if(has_vendor && vendor_data.length > 0) {
			vendor_filter = gmap_self.prepareSelect2Array(vendor_data);
		}

		// If any city filter is applied the get selected cities
		if(has_city_filter && city_filter_data.length > 0) {
			city_filter = gmap_self.prepareSelect2Array(city_filter_data);
		}

		// If any state filter is applied the get selected states
		if(has_state && state_data.length > 0) {
			state_filter = gmap_self.prepareSelect2Array(state_data);
		}

		// If any frequency filter is applied the get selected frequencies
		if(has_frequency && frequency_data.length > 0) {
			frequency_filter = gmap_self.prepareSelect2Array(frequency_data);
		}

		// If any polarization filter is applied the get selected polarization
		if(has_polarization && polarization_data.length > 0) {
			polarization_filter = gmap_self.prepareSelect2Array(polarization_data);
		}

		selected_filters_data["advance"]["technology"] = technology_filter;
		selected_filters_data["advance"]["vendor"] = vendor_filter;
		selected_filters_data["advance"]["city"] = city_filter;
		selected_filters_data["advance"]["state"] = state_filter;
		selected_filters_data["advance"]["frequency"] = frequency_filter;
		selected_filters_data["advance"]["polarization"] = polarization_filter;

		return selected_filters_data;
	};

	/**
     * This function return selected search items array
     * @method getSelectedSearchItems
     * @return selected_search_array {JSON Object}, It contains the bs alias, ip address, circuit id & city selected values JSON list.
     */
	this.getSelectedSearchItems = function() {

		var has_bs_alias = $("#search_name").select2('val').length > 0,
			has_ip_address = $("#search_sector_configured_on").select2('val').length > 0,
			has_circuit_id = $("#search_circuit_ids").select2('val').length > 0,
			has_city = $("#search_city").select2('val').length > 0,
			bs_alias_data = $("#search_name").select2('data'),
			ip_address_data = $("#search_sector_configured_on").select2('data'),
			circuit_id_data = $("#search_circuit_ids").select2('data'),
			city_data = $("#search_city").select2('data'),
			selected_bs_alias = [],
			selected_ip_address = [],
			selected_circuit_id = [],
			selected_bs_city = [],
			selected_search_array = {
				"bs_alias" : [],
				"ip_address" : [],
				"circuit_id" : [],
				"city" : []
			};

		// If any bs search is applied the get selected bs alias
		if(has_bs_alias && bs_alias_data.length > 0) {
			selected_bs_alias = gmap_self.prepareSelect2Array(bs_alias_data);
		}

		// If any IP address search is applied the get selected IP addresses
		if(has_ip_address && ip_address_data.length > 0) {
			selected_ip_address = gmap_self.prepareSelect2Array(ip_address_data);
		}

		// If any circuit_id search is applied the get selected circuit_ids
		if(has_circuit_id && circuit_id_data.length > 0) {
			selected_circuit_id = gmap_self.prepareSelect2Array(circuit_id_data);
		}

		// If any city search is applied the get selected cities
		if(has_city && city_data.length > 0) {
			selected_bs_city = gmap_self.prepareSelect2Array(city_data);
		}

		selected_search_array["bs_alias"] = selected_bs_alias;
		selected_search_array["ip_address"] = selected_ip_address;
		selected_search_array["circuit_id"] = selected_circuit_id;
		selected_search_array["city"] = selected_bs_city;

		return selected_search_array;

	};

	/**
     * This function search data as per the applied search creteria
     * @method advanceSearchFunc
     */
	this.advanceSearchFunc = function() {

		var selected_search_items = gmap_self.getSelectedSearchItems(),
			selected_bs_alias = selected_search_items['bs_alias'] ? selected_search_items['bs_alias'] : [],
			selected_ip_address = selected_search_items['ip_address'] ? selected_search_items['ip_address'] : [],
			selected_circuit_id = selected_search_items['circuit_id'] ? selected_search_items['circuit_id'] : [],
			selected_bs_city = selected_search_items['city'] ? selected_search_items['city'] : [];

  		var isSearchApplied = selected_bs_alias.length > 0 || selected_ip_address.length > 0 || selected_circuit_id.length > 0 || selected_bs_city.length > 0,
  			plottable_data = gmap_self.updateStateCounter_gmaps(true),
  			data_to_plot = plottable_data ? plottable_data : [],
  			plotted_search_markers = [],
			isSearched = 0;

		// Just to check that any data is present regarding search or not.
    	for(var i=data_to_plot.length;i--;) {
    		if(isSearched > 0) {
    			break;
    		}

    		var current_city = data_to_plot[i].city ? $.trim(data_to_plot[i].city).toLowerCase() : "",
    			current_bs_alias = data_to_plot[i].alias ? $.trim(data_to_plot[i].alias).toLowerCase() : "",
    			search_condition1 = selected_bs_alias.length > 0 ? selected_bs_alias.indexOf(String(current_bs_alias)) > -1 : true,
	            search_condition2 = selected_bs_city.length > 0 ? selected_bs_city.indexOf(String(current_city)) > -1 : true,
	            circuit_id_count = selected_circuit_id.length >  0 ? $.grep(data_to_plot[i].circuit_ids.split("|"), function (elem) {
	            	return selected_circuit_id.indexOf(elem.toLowerCase()) > -1;
	            }).length : 1,
	            ip_count = selected_ip_address.length > 0 ? $.grep(data_to_plot[i].sector_configured_on_devices.split("|"), function (elem) {
	            	return selected_ip_address.indexOf(elem.toLowerCase()) > -1;
	            }).length : 1,
	            search_condition3 = ip_count > 0 ? true : false,	
	            search_condition4 = circuit_id_count > 0 ? true : false;
	            
	        if(search_condition1 && search_condition2 && search_condition3 && search_condition4) {
	            isSearched++;
	        }
    	}

    	// Is any data present related to search
    	if(isSearched > 0) {
	    	var bounds_lat_lon = "",
	    		folder= "",
	    		folderBoundArray=[],
	    		searched_flag = false;

    		search_element_bs_id = [];

	    	if(window.location.pathname.indexOf("gearth") > -1) {
	    		// pass
	    	} else if (window.location.pathname.indexOf("wmap") > -1) {
	    		bounds_lat_lon = new OpenLayers.Bounds();
	    	} else {
	    		bounds_lat_lon = new google.maps.LatLngBounds();	
	    	}

			searchResultData = data_to_plot;
			
			advJustSearch.removeSearchMarkers();
	    	advJustSearch.resetVariables();
	    	
		    for(var i=data_to_plot.length;i--;) {
		    	
		    	var onlyCityCondition = selected_bs_alias.length == 0 && selected_ip_address.length == 0 && selected_circuit_id.length == 0;

		    	if(onlyCityCondition) {
		    		var city_val = data_to_plot[i].city ? $.trim(data_to_plot[i].city).toLowerCase() : "",
		    			city_condition = selected_bs_city.indexOf(city_val.toLowerCase()) > -1;

		    		if(city_condition) {
		    			searched_flag = true;
			    		if(window.location.pathname.indexOf("gearth") > -1) {
							folderBoundArray.push({lat: data_to_plot[i].lat, lon: data_to_plot[i].lon});
				    	} else if (window.location.pathname.indexOf("wmap") > -1) {
				    		bounds_lat_lon.extend(new OpenLayers.LonLat(data_to_plot[i].lon, data_to_plot[i].lat));
				    	} else {
				    		bounds_lat_lon.extend(new google.maps.LatLng(data_to_plot[i].lat,data_to_plot[i].lon));
				    	}
		    		} else {
	    				// pass
	    			}
	    		} else {

		    		if(selected_bs_alias.length > 0) {
			    		var bs_alias = data_to_plot[i].alias ? data_to_plot[i].alias.toLowerCase() : "",
			    			alias_condition = selected_bs_alias.indexOf(bs_alias) > -1;
		    			

		    			if(alias_condition) {
		    				searched_flag = true;
		    				if(window.location.pathname.indexOf("gearth") > -1) {
		    					folderBoundArray.push({lat: data_to_plot[i].lat, lon: data_to_plot[i].lon});
					    	} else if (window.location.pathname.indexOf("wmap") > -1) {
					    		bounds_lat_lon.extend(new OpenLayers.LonLat(data_to_plot[i].lon, data_to_plot[i].lat));
					    	} else {
					    		bounds_lat_lon.extend(new google.maps.LatLng(data_to_plot[i].lat,data_to_plot[i].lon));
					    	}
		    				
		    				// Hide State Counter Label(If Visible)
		    				if(state_wise_device_labels[data_to_plot[i].state] && !state_wise_device_labels[data_to_plot[i].state].isHidden_) {
		    					if(window.location.pathname.indexOf("gearth") > -1) {
		    						state_wise_device_labels[data_to_plot[i].state].setVisibility(false);
		    					} else if (window.location.pathname.indexOf("wmap") > -1) {
		    						hideOpenLayerFeature(state_wise_device_labels[data_to_plot[i].state]);
		    					} else {
		    						state_wise_device_labels[data_to_plot[i].state].hide();
		    					}
		    				}
		    				advJustSearch.applyIconToSearchedResult(data_to_plot[i].lat, data_to_plot[i].lon);
			    			if(search_element_bs_id.indexOf(data_to_plot[i].bs_id) < 0) {
			    				search_element_bs_id.push(data_to_plot[i].bs_id);
			    			}
		    			} else {
		    				// pass
		    			}

		    		}

			    	if(selected_ip_address.length > 0 || selected_circuit_id.length > 0) {
			    		var sectors = data_to_plot[i].sectors ? data_to_plot[i].sectors : [];

			    		for(var j=0;j<sectors.length;j++) {
			    			var sub_stations = sectors[j].sub_stations ? sectors[j].sub_stations : [],
			    				ss_infoWindow_content = sectors[j].ss_info_list ? sectors[j].ss_info_list : [],
			    				sector_ip = sectors[j].ip_address ? sectors[j].ip_address.toLowerCase() : "";
							
							// If any IP address is searched	    				
		    				if(selected_ip_address.length > 0) {
				    			var sector_ip_condition = selected_ip_address.indexOf(sector_ip) > -1 ? true : false;
				    			if(sector_ip_condition) {
				    				searched_flag = true;
				    				if(window.location.pathname.indexOf("gearth") > -1) {
				    					folderBoundArray.push({lat: data_to_plot[i].lat, lon: data_to_plot[i].lon});
				    				} else if (window.location.pathname.indexOf("wmap") > -1) {
				    					bounds_lat_lon.extend(new OpenLayers.LonLat(data_to_plot[i].lon, data_to_plot[i].lat));
				    				} else {
				    					bounds_lat_lon.extend(new google.maps.LatLng(data_to_plot[i].lat,data_to_plot[i].lon));
				    				}
				    				// Hide State Counter Label(If Visible)
				    				if(state_wise_device_labels[data_to_plot[i].state] && !state_wise_device_labels[data_to_plot[i].state].isHidden_) {
										if(window.location.pathname.indexOf("gearth") > -1) {
				    						state_wise_device_labels[data_to_plot[i].state].setVisibility(false);
				    					} else if (window.location.pathname.indexOf("wmap") > -1) {
				    						hideOpenLayerFeature(state_wise_device_labels[data_to_plot[i].state]);
				    					} else {
				    						state_wise_device_labels[data_to_plot[i].state].hide();	
				    					}
				    				}
				    				advJustSearch.applyIconToSearchedResult(data_to_plot[i].lat, data_to_plot[i].lon);
				    				if(search_element_bs_id.indexOf(data_to_plot[i].bs_id) < 0) {
					    				search_element_bs_id.push(data_to_plot[i].bs_id);
					    			}
				    			} else {
				    				// pass
				    			}
		    				}

			    			for(var k=0;k<sub_stations.length;k++) {
			    				var ss_ip = sub_stations[k].ip_address ? sub_stations[k].ip_address : "",
			    					// ss_item_index = sub_stations[k].data.item_index > -1 ? sub_stations[k].data.item_index : 0,
			    					ss_info_dict = [],
			    					ss_circuit_id = sub_stations[k].circuit_id ? $.trim(sub_stations[k].circuit_id.toLowerCase()) : "";

			    				// If any IP address or Circuit ID is searched
			    				if(selected_ip_address.length > 0 || selected_circuit_id.length > 0) {
					    			var ss_ip_condition = selected_ip_address.indexOf(ss_ip) > -1,
					    				ss_circuit_condition = selected_circuit_id.indexOf(ss_circuit_id) > -1;
					    			if(ss_ip_condition || ss_circuit_condition) {
					    				searched_flag = true;
					    				if(window.location.pathname.indexOf("gearth") > -1) {
					    					folderBoundArray.push({lat: data_to_plot[k].lat, lon: data_to_plot[k].lon});
					    					folderBoundArray.push({lat: sub_stations[k].lat, lon: sub_stations[k].lon});
					    				} else if (window.location.pathname.indexOf("wmap") > -1) {
					    					bounds_lat_lon.extend(new OpenLayers.LonLat(data_to_plot[i].lon, data_to_plot[i].lat));
					    					bounds_lat_lon.extend(new OpenLayers.LonLat(sub_stations[k].lon, sub_stations[k].lat));
					    				} else {
					    					bounds_lat_lon.extend(new google.maps.LatLng(data_to_plot[i].lat,data_to_plot[i].lon));
					    					bounds_lat_lon.extend(new google.maps.LatLng(sub_stations[k].lat,sub_stations[k].lon));
					    				}
					    				// Hide State Counter Label(If Visible)
					    				if(state_wise_device_labels[data_to_plot[i].state] && !state_wise_device_labels[data_to_plot[i].state].isHidden_) {
											if(window.location.pathname.indexOf("gearth") > -1) {
					    						state_wise_device_labels[data_to_plot[i].state].setVisibility(false);
					    					} else if (window.location.pathname.indexOf("wmap") > -1) {
					    						hideOpenLayerFeature(state_wise_device_labels[data_to_plot[i].state]);
					    					} else {
					    						state_wise_device_labels[data_to_plot[i].state].hide();	
					    					}
					    				}
					    				advJustSearch.applyIconToSearchedResult(sub_stations[k].lat, sub_stations[k].lon,advJustSearch.constants.search_ss_icon);
					    				if(ss_circuit_condition) {
					    					advJustSearch.applyIconToSearchedResult(data_to_plot[i].lat, data_to_plot[i].lon);	
					    				}
					    				if(search_element_bs_id.indexOf(data_to_plot[i].bs_id) < 0) {
						    				search_element_bs_id.push(data_to_plot[i].bs_id);
						    			}
					    			} else {
					    				// pass
					    			}
			    				}
			    			}
			    		}
			    	}
		    	}
		    }

		    if(searched_flag) {
			    if(data_to_plot.length > 0) {

			    	if(window.location.pathname.indexOf("gearth") > -1) {
			    		
						showGoogleEarthInBounds(folderBoundArray, function() {

							if(AltToZoom(getEarthZoomLevel()) > 15) {
								setEarthZoomLevel(ZoomToAlt(15));
							}

							// Show search marker after some timeout
							setTimeout(function() {
								for(var i=0;i<searchMarkers_global.length;i++) {

									// Add the searchMarker to Earth.
									ge.getFeatures().appendChild(searchMarkers_global[i]);
								}
							},350);
						});

			    	} else if (window.location.pathname.indexOf("wmap") > -1) {
			    		//Zoom in to selected state
			    		ccpl_map.zoomToExtent(bounds_lat_lon);
			    		if(ccpl_map.getZoom() > 12) {
			                ccpl_map.zoomTo(12);
			            }
			    	} else {
				    	//Zoom in to selected state
						mapInstance.fitBounds(bounds_lat_lon);
						var listener = google.maps.event.addListenerOnce(mapInstance, 'bounds_changed', function(event) {
							if(mapInstance.getZoom() > 15) {
				                mapInstance.setZoom(15);
				            }
				            google.maps.event.removeListener(listener);
			            });

						// Show search marker after some timeout
						setTimeout(function() {
							for(var i=0;i<searchMarkers_global.length;i++) {
						    	searchMarkers_global[i].setMap(mapInstance);
						    }
						},350);
			    	}

			    	// Set Perf calling Flag
	    			isPerfCallStopped = 0;
	    			isPerfCallStarted = 0;
	    		}
    		} else {
    			$.gritter.add({
	        		// (string | mandatory) the heading of the notification
	                title: 'GIS : Advance Search',
	                // (string | mandatory) the text inside the notification
	                text: 'No data available for applied search.',
	                // (bool | optional) if you want it to fade out on its own or just sit there
	                sticky: false,
	                // Time in ms after which the gritter will dissappear.
	                time : 1000
	            });

	            advJustSearch.removeSearchMarkers();
    		}
	    } else {
	    	$.gritter.add({
        		// (string | mandatory) the heading of the notification
                title: 'GIS : Advance Search',
                // (string | mandatory) the text inside the notification
                text: 'No data available for applied search.',
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false,
                // Time in ms after which the gritter will dissappear.
                time : 1000
            });

            advJustSearch.removeSearchMarkers();
	    }

	    if(!($("#advSearchContainerBlock").hasClass("hide"))) {
            $("#advSearchContainerBlock").addClass("hide");
        }

	    // Hide the spinner
        hideSpinner();
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
        	appliedFilterObj_gmaps["technology"] = $.trim($("#technology option:selected").text());
        }

        if($("#vendor").val().length > 0) {
        	// selectedvendor = $("#vendor option:selected").text();
        	appliedFilterObj_gmaps["vendor"] = $.trim($("#vendor option:selected").text());
        }

        if($("#state").val().length > 0) {
        	appliedFilterObj_gmaps["state"] = $.trim($("#state option:selected").text());
        }


        try {
            if($("#city").val().length > 0) {
            	appliedFilterObj_gmaps["city"] = $.trim($("#city option:selected").text());
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
        	gmap_self.updateStateCounter_gmaps(false);
        }
        /*If no filter is applied the load all the devices*/
        else {

        	if(!$('#infoWindowContainer').hasClass("hide")) {
		    	$('#infoWindowContainer').addClass("hide");
		    }

			$('#infoWindowContainer').html("");

		    if($(".windowIFrame").length) {
		        $(".windowIFrame").remove();
		    }

        	if($.trim(mapPageType) == "gearth") {
    			
    			/************************Google Earth Code***********************/

        		/*Clear all the elements from google earth*/
		        earth_instance.clearEarthElements();
		        earth_instance.clearStateCounters();

		        /*Reset Global Variables & Filters*/
		        earth_instance.resetVariables_earth();

		        isCallCompleted = 1;

		        var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);
				lookAt.setLatitude(21.0000);
				lookAt.setLongitude(78.0000);
				lookAt.setRange(5492875.865539902);
				// lookAt.setZoom
				// Update the view in Google Earth 
				ge.getView().setAbstractView(lookAt); 
				
				// mapInstance.fitBounds(new google.maps.LatLngBounds(new google.maps.LatLng(india_center_lat,india_center_lon)));
				// mapInstance.setZoom(5);
				// data_for_filters_earth = JSON.parse(JSON.stringify(all_devices_loki_db.data));
				data_for_filters_earth = gmap_self.objDeepCopy_nocout(all_devices_loki_db.data);

				isApiResponse = 0;
				// Load all counters
				// earth_instance.showStateWiseData_earth(JSON.parse(JSON.stringify(all_devices_loki_db.data)));
				earth_instance.showStateWiseData_earth(gmap_self.objDeepCopy_nocout(all_devices_loki_db.data));

		        /*create the BS-SS network on the google earth*/
		        // earth_instance.plotDevices_earth(main_devices_data_earth,"base_station");
		    } else if($.trim(mapPageType) == "wmap") {
		    	whiteMapClass.clearStateCounters_wmaps();
		    	isCallCompleted = 1;
		    	if(ccpl_map.getZoom() != 1) {
		    		// ccpl_map.setCenter(new OpenLayers.LonLat(whiteMapSettings.mapCenter[0], whiteMapSettings.mapCenter[1]), 1, true, true);
		    		ccpl_map.setCenter(
						new OpenLayers.LonLat(
							whiteMapSettings.mapCenter[0],
							whiteMapSettings.mapCenter[1]
						),
						1,
						true,
						true
					);
					ccpl_map.zoomTo(1);
	    		}
		    	data_for_filter_wmap = JSON.parse(JSON.stringify(all_devices_loki_db.data));
		    	isApiResponse= 0;
		    	whiteMapClass.showStateWiseData_wmap(JSON.parse(JSON.stringify(all_devices_loki_db.data)));
        	} else {
        		/*Clear Existing Labels & Reset Counters*/
				gmap_self.clearStateCounters();

				if(infowindow) {
					infowindow.close();
				}
				// Reset Flag variables
				isCallCompleted = 1;
				isApiResponse = 0;
				// Update map bounds
				mapInstance.fitBounds(new google.maps.LatLngBounds(new google.maps.LatLng(india_center_lat,india_center_lon)));
				// Set zoom level to 5
				mapInstance.setZoom(5);
				data_for_filters = gmap_self.objDeepCopy_nocout(all_devices_loki_db.data);
				// Load all counters
				gmap_self.showStateWiseData_gmap(data_for_filters);
        	}
        }
    };

    /**
	 * This function updates the states devices counter as per the applied filter
	 * @method updateStateCounter_gmaps
	 * @param isIdleCase {Boolean}, It canse a boolean value to check weather the call is from idle function or from filters.
	 */
	this.updateStateCounter_gmaps = function(isIdleCase) {

		if(isDebug) {
			console.log("Update State Counters Function");
			var start_date_update_counter = new Date();
		}

		// If isIdleCase is false then clear state counters
		if(!isIdleCase) {
			/*Clear Existing Labels & Reset Counters*/
			if(window.location.pathname.indexOf("gearth") > -1) {
				/*Clear all the elements from google earth*/
		        earth_instance.clearEarthElements();
				earth_instance.clearStateCounters();
			} else if (window.location.pathname.indexOf("wmap") > -1) { 
				whiteMapClass.clearStateCounters_wmaps();			
			} else {
				gmap_self.clearStateCounters();
			}
		}

		var complete_filtering_data = gmap_self.getSelectedFilteringItems(),
			technology_filter = complete_filtering_data["advance"]["technology"],
			vendor_filter = complete_filtering_data["advance"]["vendor"],
			city_filter = complete_filtering_data["advance"]["city"],
			state_filter = complete_filtering_data["advance"]["state"],
			frequency_filter = complete_filtering_data["advance"]["frequency"],
			polarization_filter = complete_filtering_data["advance"]["polarization"],
			filterObj = complete_filtering_data["basic"],
			isAdvanceFilterApplied = technology_filter.length > 0 || vendor_filter.length > 0 || state_filter.length > 0 || city_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0,
			isBasicFilterApplied = $.trim($("#technology").val()).length > 0 || $.trim($("#vendor").val()).length > 0 || $.trim($("#state").val()).length > 0 || $.trim($("#city").val()).length > 0,
			basic_filter_condition = $.trim($("#technology").val()).length > 0 || $.trim($("#vendor").val()).length > 0,
			advance_filter_condition = technology_filter.length > 0 || vendor_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0,
			filtered_data_1 = [],
			data_to_plot_1 = [];

		if(isAdvanceFilterApplied || isBasicFilterApplied) {
			filtered_data_1 = gmap_self.getFilteredData_gmap();
		} else {
			filtered_data_1 = gmap_self.objDeepCopy_nocout(all_devices_loki_db.data);
		}

		if(advance_filter_condition || basic_filter_condition) {
        	data_to_plot_1 = gmap_self.getFilteredBySectors(filtered_data_1);
    	} else {
    		data_to_plot_1 = filtered_data_1;
    	}

    	if(isIdleCase) {
    		var response = data_to_plot_1 ? data_to_plot_1 : []; 

    		if(isDebug) {
	    		var time_diff = (new Date().getTime() - start_date_update_counter.getTime())/1000;
				console.log("Update State Counters Function(Return Data Case) for "+response.length+" Devices -  End Time :- "+ time_diff +" Seconds");
				console.log("*******************************************");
				start_date_update_counter = "";
	    	}

    		return response;
    	} else {

    		var selected_search_items = gmap_self.getSelectedSearchItems(),
				selected_bs_alias = selected_search_items['bs_alias'] ? selected_search_items['bs_alias'] : [],
				selected_ip_address = selected_search_items['ip_address'] ? selected_search_items['ip_address'] : [],
				selected_circuit_id = selected_search_items['circuit_id'] ? selected_search_items['circuit_id'] : [],
				selected_bs_city = selected_search_items['city'] ? selected_search_items['city'] : [];

    		// If any search is applied then reset it
    		var isSearchApplied = selected_bs_alias.length > 0 || selected_ip_address.length > 0 || selected_circuit_id.length > 0 || selected_bs_city.length > 0;

    		if(isSearchApplied) {
    			resetAdvanceSearch();
    		}

			if(data_to_plot_1.length > 0) {
				isCallCompleted = 1;
				isApiResponse = 0;
				if(window.location.pathname.indexOf("gearth") > -1) {
					data_for_filters_earth = data_to_plot_1;
					/*Set current position of google earth to india*/
					var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);
					lookAt.setLatitude(21.0000);
					lookAt.setLongitude(78.0000);
					lookAt.setRange(5492875.865539902);
					// Update the view in Google Earth 
					ge.getView().setAbstractView(lookAt); 
					earth_self.showStateWiseData_earth(data_to_plot_1);
				} else if (window.location.pathname.indexOf("wmap") > -1) {
					data_for_filter_wmap = data_to_plot_1;
					if(ccpl_map.getZoom() != 1) {
						ccpl_map.setCenter(
							new OpenLayers.LonLat(
								whiteMapSettings.mapCenter[0],
								whiteMapSettings.mapCenter[1]
							),
							1,
							true,
							true
						);
						ccpl_map.zoomTo(1);
					}
					whiteMapClass.showStateWiseData_wmap(data_to_plot_1);
				} else {
					data_for_filters = data_to_plot_1;
					// If any infowindow open then close it.
					if(infowindow) {
						infowindow.close();
					}

				    if(!$('#infoWindowContainer').hasClass("hide")) {
				    	$('#infoWindowContainer').addClass("hide");
				    }

					$('#infoWindowContainer').html("");

				    if($(".windowIFrame").length) {
				        $(".windowIFrame").remove();
				    }


					mapInstance.fitBounds(new google.maps.LatLngBounds(new google.maps.LatLng(india_center_lat,india_center_lon)));
					mapInstance.setZoom(5);
					gmap_self.showStateWiseData_gmap(data_to_plot_1);
				}
			} else {
				$.gritter.add({
	        		// (string | mandatory) the heading of the notification
	                title: 'GIS : Filters',
	                // (string | mandatory) the text inside the notification
	                text: 'No data available for applied filters.',
	                // (bool | optional) if you want it to fade out on its own or just sit there
	                sticky: false,
	                // Time in ms after which the gritter will dissappear.
	                time : 1000
	            });
			}
			/*Enable the refresh button*/
    		$("#resetFilters").button("complete");
    	}

    	if(isDebug) {
    		var time_diff = (new Date().getTime() - start_date_update_counter.getTime())/1000;
			console.log("Update State Counters Function for "+data_to_plot_1.length+" Devices -  End Time :- "+ time_diff +" Seconds");
			console.log("*******************************************");
			start_date_update_counter = "";
    	}
	};

	/**
	 * This function creates deep copy of js object
	 * @method objDeepCopy_nocout
	 * @param originalObj {Object}, It contains the js object
	 * @return copiedObj {Object}, It contains the deep copy of given object
	 */
	this.objDeepCopy_nocout = function(originalObj) {
		if(isDebug) {
			console.log("Object Deep Copy Function");
			var start_date_deep_copy = new Date();
		}
		var copiedObj = "";

		if(originalObj) {
			copiedObj = JSON.parse(JSON.stringify(originalObj));
		}

		if(isDebug) {
    		var time_diff = (new Date().getTime() - start_date_deep_copy.getTime())/1000;
			console.log("Object Deep Copy Function for "+originalObj.length+" Devices -  End Time :- "+ time_diff +" Seconds");
			console.log("*******************************************");
			start_date_deep_copy = "";
    	}

		return copiedObj;

	};

	/**
	 * This function returns the total number of BS & SS in fetched data
	 * @method getCountryWiseCount
	 * @return device_count {Number}, It contains the number of BS & SS in fetched data
	 */
	this.getCountryWiseCount = function() {

    	var data_to_plot_1 = gmap_self.updateStateCounter_gmaps(true),
    		devices_count = 0;

		if(data_to_plot_1 && data_to_plot_1.length > 0) {
			for(var i=data_to_plot_1.length;i--;) {
				var sectors_data = data_to_plot_1[i].sectors;
				// Increment the counter by 1
				devices_count += 1;
				//Loop For Sector Devices
				for(var j=sectors_data.length;j--;) {
					var total_ss = sectors_data[j].sub_stations ? sectors_data[j].sub_stations.length : 0;
					// Increment the counter by ss count
					devices_count += total_ss;
				}
			}
		}

		return devices_count;
	};

	/**
	 * This function clear the state counter & labels
	 * @method clearStateCounters
	 */
	this.clearStateCounters = function() {

		if(isDebug) {
			console.log("Clear State Counters Function");
			start_date_clear_counter = new Date();
		}

		for(key in state_wise_device_counters) {
			state_wise_device_counters[key] = 0;
			if(state_wise_device_labels[key]) {
				state_wise_device_labels[key].close();
			}
		}


		if(isDebug) {
			var time_diff = (new Date().getTime() - start_date_clear_counter.getTime())/1000;
			console.log("Clear State Counters Function End Time :- "+ time_diff +" Seconds");
			console.log("*******************************************");
			start_date_clear_counter = "";
		}
	};

    /**
     * This function initialize live polling
     * @method initLivePolling
     */
    this.initLivePolling = function() {

    	if(mapInstance.getZoom() > 7) {
    		/*Reset marker icon*/
			for(var i=0;i<polygonSelectedDevices.length;i++) {

	            var ss_marker = allMarkersObject_gmap['sub_station']['ss_'+polygonSelectedDevices[i].name],
	            	sector_ip = "";
	            
	            if(polygonSelectedDevices[i].pointType && ($.trim(polygonSelectedDevices[i].pointType) == 'sub_station')) {
	            	sector_ip = polygonSelectedDevices[i].sector_ip;
	            } else {
	            	sector_ip = polygonSelectedDevices[i].sectorName;
	            }

	            var sector_marker = allMarkersObject_gmap['sector_device']['sector_'+sector_ip];

				if(ss_marker) {
					ss_marker.setOptions({
						"icon" : ss_marker.oldIcon
					});
				} else if(sector_marker) {
					sector_marker.setOptions({
						"icon" : sector_marker.oldIcon
					});
				}
	    	}

			/*Reset the drawing object if exist*/
			if(drawingManager_livePoll && drawingManager_livePoll.getMap()) {
				drawingManager_livePoll.setMap(null);
			}

			/*Remove the polygon if exists*/
			if(Object.keys(currentPolygon).length > 0) {
				currentPolygon.setMap(null);
			}

			/*Set isPollingActive flag*/
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

			if(!($("#timeInterval_container").hasClass("hide"))) {
				$("#timeInterval_container").addClass("hide");
			}

			if(!($(".play_pause_btns").hasClass("hide"))) {
				$(".play_pause_btns").addClass("hide");
			}

			if(($(".play_pause_btns").hasClass("disabled"))) {
				$(".play_pause_btns").removeClass("disabled");
			}

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

			/*Disable poll interval & max interval dropdown*/
            $("#poll_interval").removeAttr("disabled");
            $("#poll_maxInterval").removeAttr("disabled");

            /*Select default value*/
            $("#poll_interval").val($("#poll_interval option:first").val());
            $("#poll_maxInterval").val($("#poll_maxInterval option:first").val());

    	} else {
    		bootbox.alert("<p style='position:relative;z-index:9999;'>Please zoom in for live poll devices.There are too many devices.</p>");
    		$("#clearPolygonBtn").trigger('click');
    	}
    };

    /**
	 * This function creates HTML for live polling selected devices
	 * @method createLivePollingHtml
	 * @param polygonSelectedDevices {Array}, It contains the selected devices(markers) object array
	 * @return devicesTemplate {String}, It contains the HTML string
	 */
	this.createLivePollingHtml = function(polygonSelectedDevices) {
		var devicesTemplate = "",
			num_counter = 0;

		if(!polygonSelectedDevices || polygonSelectedDevices.length == 0) {
			return devicesTemplate;
		}

		devicesTemplate = "<div class='deviceWellContainer'>";

		for(var i=0;i<polygonSelectedDevices.length;i++) {
			
			var new_device_name = "";
			var current_technology = polygonSelectedDevices[i].technology ? $.trim(polygonSelectedDevices[i].technology.toLowerCase()) : "";
			
			if(polygonSelectedDevices[i].device_name.indexOf(".") != -1) {
				new_device_name = polygonSelectedDevices[i].device_name.split(".");
				new_device_name = new_device_name.join("-");
			} else {
				new_device_name = polygonSelectedDevices[i].device_name;
			}

			var devices_counter = "";
			
			if(ptp_tech_list.indexOf(current_technology) > -1) {
				if(polygonSelectedDevices[i].pointType == 'sub_station') {
					devices_counter = polygonSelectedDevices[i].bs_sector_device;
				} else {
					devices_counter = polygonSelectedDevices[i].device_name;
				}

                if(!polled_device_count[devices_counter]) {
					polled_device_count[devices_counter]  = 1;
				} else {
					polled_device_count[devices_counter] += 1;
				}
			}

			if((ptp_tech_list.indexOf(current_technology) > -1) && polygonSelectedDevices[i].pointType == 'sub_station') {

				if(polygonSelectedDevices[i].bs_sector_device.indexOf(".") != -1) {
					var new_device_name2 = polygonSelectedDevices[i].bs_sector_device.split(".");
					new_device_name2 = new_device_name2.join("-");
				} else {
					var new_device_name2 = polygonSelectedDevices[i].bs_sector_device;
				}

				if(polled_device_count[devices_counter] <= 1) {
					var display_name = "Ckt. ("+polygonSelectedDevices[i].cktId+") : IP ("+polygonSelectedDevices[i].sector_ip+")";
					num_counter++;
					devicesTemplate += '<div class="well well-sm" id="div_'+new_device_name2+'"><h5>'+num_counter+') NE - '+display_name+'</h5>';
					devicesTemplate += '<div style="min-height:60px;margin-top:15px;margin-bottom: 5px;" id="livePolling_'+new_device_name2+'">';
					devicesTemplate += '<ul id="pollVal_'+new_device_name2+'" class="list-unstyled list-inline"></ul>';
					devicesTemplate += '<span class="sparkline" id="sparkline_'+new_device_name2+'"></span></div></div>';
				}
				var ss_display_name = "Ckt. ("+polygonSelectedDevices[i].cktId+") : IP ("+polygonSelectedDevices[i].ss_ip+")";
				num_counter++;
				devicesTemplate += '<div class="well well-sm" id="div_'+new_device_name+'"><h5>'+num_counter+') FE - '+ss_display_name+'</h5>';
				devicesTemplate += '<div style="min-height:60px;margin-top:15px;margin-bottom: 5px;" id="livePolling_'+new_device_name+'">';
				devicesTemplate += '<ul id="pollVal_'+new_device_name+'" class="list-unstyled list-inline"></ul>';
				devicesTemplate += '<span class="sparkline" id="sparkline_'+new_device_name+'"></span></div></div>';

			} else {
				var device_end_txt = "",
					point_name = "";

                if(polled_device_count[devices_counter] == 1) {
					if(ptp_tech_list.indexOf(current_technology) > -1) {
						if(polygonSelectedDevices[i].pointType == 'sub_station') {
							device_end_txt = "FE";
							point_name = "Ckt. ("+polygonSelectedDevices[i].cktId+") : IP ("+polygonSelectedDevices[i].ss_ip+")";
						} else {
							device_end_txt = "NE";
							point_name = "Ckt. ("+polygonSelectedDevices[i].cktId+") : IP ("+polygonSelectedDevices[i].sectorName+")";
						}
						num_counter++;
						devicesTemplate += '<div class="well well-sm" id="div_'+new_device_name+'"><h5>'+num_counter+') '+device_end_txt+' - '+point_name+'</h5>';
						devicesTemplate += '<div style="min-height:60px;margin-top:15px;margin-bottom: 5px;" id="livePolling_'+new_device_name+'">';
						devicesTemplate += '<ul id="pollVal_'+new_device_name+'" class="list-unstyled list-inline"></ul>';
						devicesTemplate += '<span class="sparkline" id="sparkline_'+new_device_name+'"></span></div></div>';
					}
				} else {

					point_name = "Ckt. ("+polygonSelectedDevices[i].cktId+") : IP ("+polygonSelectedDevices[i].ss_ip+")";
					num_counter++;
					devicesTemplate += '<div class="well well-sm" id="div_'+new_device_name+'"><h5>'+num_counter+') '+point_name+'</h5>';
					devicesTemplate += '<div style="min-height:60px;margin-top:15px;margin-bottom: 5px;" id="livePolling_'+new_device_name+'">';
					devicesTemplate += '<ul id="pollVal_'+new_device_name+'" class="list-unstyled list-inline"></ul>';
					devicesTemplate += '<span class="sparkline" id="sparkline_'+new_device_name+'"></span></div></div>';
				}
			}
		}

		devicesTemplate += "</div>";

		return devicesTemplate;
	};

    /**
     * This function initialize live polling
     * @method fetchPollingTemplate_gmap
     */
    this.fetchPollingTemplate_gmap = function() {
    	
    	var selected_technology = $.trim($("#polling_tech").val()),
    		selected_type = $.trim($("#polling_type").val()),
    		pathArray = [],
			polygon = "",
			service_type = $("#isPing")[0].checked ? "ping" : "normal";

    	/*Re-Initialize the polling*/
    	networkMapInstance.initLivePolling();
		
		/*Reset the variables*/
		polygonSelectedDevices = [];
		pointsArray = [];

    	if(selected_technology && selected_type) {
    		
    		$("#tech_send").button("loading");

    		/*ajax call for services & datasource*/
    		$.ajax({
    			url : base_url+"/"+"device/ts_templates/?technology="+selected_technology+"&device_type="+selected_type+"&service_type="+service_type,
    			// url : base_url+"/"+"static/livePolling.json",
    			success : function(response) {
					
					var result = "";
					// Type check for response
    				if(typeof response == 'string') {
    					result = JSON.parse(response);
    				} else {
    					result = response;
    				}
    				
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

    					if(($("#timeInterval_container").hasClass("hide"))) {
							$("#timeInterval_container").removeClass("hide");
						}

						if(($(".play_pause_btns").hasClass("hide"))) {
							$(".play_pause_btns").removeClass("hide");
						}

						if(($(".play_pause_btns").hasClass("disabled"))) {
							$(".play_pause_btns").removeClass("disabled");
						}

    					$("#tech_send").button("complete");
    					/*Initialize create Polygon functionality*/
    					drawingManager_livePoll = new google.maps.drawing.DrawingManager({
							drawingMode: google.maps.drawing.OverlayType.POLYGON,
							drawingControl: false,
                            polygonOptions: {
                              fillColor: '#ffffff',
                              fillOpacity: 0,
                              strokeWeight: 2,
                              clickable: false,
                              editable: true,
                              zIndex: 1
                            }
						});

						drawingManager_livePoll.setMap(mapInstance);

						google.maps.event.addListener(drawingManager_livePoll, 'overlaycomplete', function(e) {

							pathArray = e.overlay.getPath().getArray();
							polygon = new google.maps.Polygon({"path" : pathArray});
							bs_ss_array = masterMarkersObj;

							currentPolygon = e.overlay;
							currentPolygon.type = e.type;

							var allSS = pollableDevices;
							// Reset Global Variables
							allSSIds = [];
							polygonSelectedDevices = [];

							var selected_polling_technology = $("#polling_tech option:selected").text(),
								polling_technology_condition = $.trim(selected_polling_technology.toLowerCase()),
								selected_polling_type = $("#polling_type option:selected").text(),
								polling_type_condition = $.trim(selected_polling_type.toLowerCase());

							for(var k=allSS.length;k--;) {
								var point = new google.maps.LatLng(allSS[k].ptLat,allSS[k].ptLon),
									point_tech = allSS[k].technology ? $.trim(allSS[k].technology.toLowerCase()) : "";
									point_type = allSS[k].device_type ? $.trim(allSS[k].device_type.toLowerCase()) : "";

								// if point technology is PTP BH then use it as PTP
								if(ptp_tech_list.indexOf(point_tech) > -1) {
									point_tech = 'ptp';
								}

								// PTP, P2P & PTP BH are same
								if(ptp_tech_list.indexOf(polling_technology_condition) > -1) {
									polling_technology_condition = 'ptp';
								}

								if(point) {
									if(point_tech == polling_technology_condition && point_type == polling_type_condition) {
										if(google.maps.geometry.poly.containsLocation(point, polygon)) {
											if(ptp_tech_list.indexOf(point_tech) > -1) {
												if(allSSIds.indexOf(allSS[k].device_name) < 0) {
													if(allSS[k].pointType == 'sub_station') {
														if(allSSIds.indexOf(allSS[k].bs_sector_device) < 0) {
															allSSIds.push(allSS[k].bs_sector_device);
															polygonSelectedDevices.push(allMarkersObject_gmap['sector_device']['sector_'+allSS[k].sector_ip]);
														}
													}
													allSSIds.push(allSS[k].device_name);
													polygonSelectedDevices.push(allSS[k]);
												}
											} else {
												if(allSS[k].pointType == 'sub_station') {
													if(allSSIds.indexOf(allSS[k].device_name) < 0) {
														allSSIds.push(allSS[k].device_name);
														polygonSelectedDevices.push(allSS[k]);
													}
												}
											}
										}
									}
								}
							}

							if(polygonSelectedDevices.length == 0) {

								/*Remove current polygon from map*/
								gmap_self.initLivePolling();

								/*Reset polling technology and polling type select box*/
								$("#polling_tech").val($("#polling_tech option:first").val());
								$("#polling_type").val($("#polling_type option:first").val());

								bootbox.alert("No SS found under the selected area.");

							} else if(polygonSelectedDevices.length > 200) {

								/*Remove current polygon from map*/
								gmap_self.initLivePolling();

								/*Reset polling technology select box*/
								$("#polling_tech").val($("#polling_tech option:first").val());

								bootbox.alert("Max. limit for selecting devices is 200.");

							} else {
								var devicesTemplate = gmap_self.createLivePollingHtml(polygonSelectedDevices);

								$("#sideInfo > .panel-body > .col-md-12 > .devices_container").html(devicesTemplate);
							}

							/*Remove drawing mode*/
							if(drawingManager_livePoll && drawingManager_livePoll.getMap()) {
								drawingManager_livePoll.setMap(null);
							}
						});


    				} else {
    					
    					$("#tech_send").button("complete");
    					$("#sideInfo .panel-body .col-md-12 .template_container").html("");

    					if(!($("#timeInterval_container").hasClass("hide"))) {
							$("#timeInterval_container").addClass("hide");
						}

						if(!($(".play_pause_btns").hasClass("hide"))) {
							$(".play_pause_btns").addClass("hide");
						}

						if(($(".play_pause_btns").hasClass("disabled"))) {
							$(".play_pause_btns").removeClass("disabled");
						}

    					if(!($("#fetch_polling").hasClass("hide"))) {
    						$("#fetch_polling").addClass("hide");
    					}

    					$.gritter.add({
				            // (string | mandatory) the heading of the notification
				            title: 'Live Polling - Error',
				            // (string | mandatory) the text inside the notification
				            text: result.message,
				            // (bool | optional) if you want it to fade out on its own or just sit there
				            sticky: false,
				            // Time in ms after which the gritter will dissappear.
	                		time : 1000
				        });
    				}

    			},
    			error : function(err) {
    				
    				$("#tech_send").button("complete");
    				$("#sideInfo .panel-body .col-md-12 .template_container").html("");

    				if(!($("#timeInterval_container").hasClass("hide"))) {
						$("#timeInterval_container").addClass("hide");
					}

					if(!($(".play_pause_btns").hasClass("hide"))) {
						$(".play_pause_btns").addClass("hide");
					}

					if(($(".play_pause_btns").hasClass("disabled"))) {
						$(".play_pause_btns").removeClass("disabled");
					}

    				if(!($("#fetch_polling").hasClass("hide"))) {
						$("#fetch_polling").addClass("hide");
					}
    				
    				$.gritter.add({
			            // (string | mandatory) the heading of the notification
			            title: 'Live Polling - Error',
			            // (string | mandatory) the text inside the notification
			            text: err.statusText,
			            // (bool | optional) if you want it to fade out on its own or just sit there
			            sticky: false,
			            // Time in ms after which the gritter will dissappear.
	                	time : 1000
			        });
    			}
    		});

    	} else {
    		alert("Please select technology & type.");
    	}
    };

    /**
	 * This function fetch the polling value for selected devices periodically as per the selected intervals.
	 * @method startDevicePolling_gmap
	 */
    this.startDevicePolling_gmap = function() {
    	if(remainingPollCalls > 0) {
			if(isPollingPaused == 0) {
				var timeout_time = pollingInterval*1000;
				// Call function to fetch polled data for selected devices
				gmap_self.getPollingData_gmap(function(response) {
					pollCallingTimeout = setTimeout(function() {
						remainingPollCalls--;
						gmap_self.startDevicePolling_gmap();
					},timeout_time);
				});
			} else {
				if($("#play_btn").hasClass("disabled")) {
	                $("#play_btn").removeClass("disabled");
	            }
	    		clearTimeout(pollCallingTimeout);
			}
    	} else {
    		if($("#play_btn").hasClass("disabled")) {
                $("#play_btn").removeClass("disabled");
            }
    		clearTimeout(pollCallingTimeout);
    	}
    };

    /**
	 * This function calls getPollingData_gmap() to fetch polled data for selected devices once.
	 * @method fetchDevicesPollingData
	 */
    this.fetchDevicesPollingData = function() {

    	if(polygonSelectedDevices.length > 0 && $("#lp_template_select").val() != "") {

    		$("#fetch_polling").button("loading");

			if(!($(".play_pause_btns").hasClass("disabled"))) {
				$(".play_pause_btns").addClass("disabled");
			}

			// Call function to fetch polled data for selected devices
    		gmap_self.getPollingData_gmap(function(response) {
    			if(($(".play_pause_btns").hasClass("disabled"))) {
					$(".play_pause_btns").removeClass("disabled");
				}
    		});

    	} else {
    		bootbox.alert("Please select devices & polling template first.");
    	}
    };

    /**
	 * This function fetch the polled data for selected devices.
	 * @method getPollingData_gmap
	 */
    this.getPollingData_gmap = function(callback) {

    	var service_type = $("#isPing")[0].checked ? "ping" : "normal",
    		selected_device_type = $.trim($('#polling_type option:selected').text()),
    		is_radwin5 = selected_device_type && selected_device_type.toLowerCase().indexOf('radwin5') > -1 ? 1 : 0,
    		is_first_call = 0;

    	if($(".deviceWellContainer div.well div ul li").length == 0) {
    		is_first_call = 1;
		}

		/*Disable service templates dropdown*/
		$("#lp_template_select").attr("disabled","disabled");

		var selected_lp_template = $("#lp_template_select").val();

    	$.ajax({
			url : base_url+"/"+"device/lp_bulk_data/?ts_template="+selected_lp_template+"&devices="+JSON.stringify(allSSIds)+"&service_type="+service_type+"&is_radwin5="+is_radwin5+"&is_first_call="+is_first_call,
			// url : base_url+"/"+"static/services.json?ts_template="+selected_lp_template+"&devices="+JSON.stringify(allSSIds)+"&service_type="+service_type,
			success : function(response) {
				
				var result = "";
				// Type check for response
				if(typeof response == 'string') {
					result = JSON.parse(response);
				} else {
					result = response;
				}
				
				if(result.success == 1) {

					/*Remove 'text-info' class from all li's*/
					if($(".deviceWellContainer div div ul li")) {
						$(".deviceWellContainer div div ul li").removeClass("text-info");
					}

					if($(".devices_container").hasClass("hide")) {
						$(".devices_container").removeClass("hide");
					}
					var hasPolledInfo = true;
					for(var i=allSSIds.length;i--;) {
						var new_device_name = "";
						if(allSSIds[i] && allSSIds[i].indexOf(".") != -1) {
							new_device_name = allSSIds[i].split('.');
							new_device_name = new_device_name.join('-');
						} else {
							new_device_name = allSSIds[i];
						}

						if(result.data.devices[allSSIds[i]]) {

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
								current_day = dateObj.getDate(),
								current_month = dateObj.getMonth() + 1,
								current_year = dateObj.getFullYear(),
								today_day = current_day+"-"+current_month+"-"+current_year,
								current_time = dateObj.getHours()+":"+dateObj.getMinutes()+":"+dateObj.getSeconds(), //+":"+dateObj.getMilliseconds(),
								shown_datetime = today_day+" "+current_time,
								final_chart_data = [];
							
							if($("#pollVal_"+new_device_name+" li").length == 0) {

								var fetchValString = "";
								fetchValString += "<li class='fetchVal_"+new_device_name+" text-info' style='padding:0px;'> (<i class='fa fa-clock-o'></i> "+shown_datetime+", <i class='fa fa-arrow-circle-o-right'></i> "+result.data.devices[allSSIds[i]].value+")  <input type='hidden' name='chartVal_"+new_device_name+"' id='chartVal_"+new_device_name+"' value='"+result.data.devices[allSSIds[i]].value+"'/></li>";

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

								$("#pollVal_"+new_device_name).append("<li class='fetchVal_"+new_device_name+" text-info' style='padding:0px;'> , (<i class='fa fa-clock-o'></i> "+shown_datetime+", <i class='fa fa-arrow-circle-o-right'></i> "+result.data.devices[allSSIds[i]].value+")</li>");
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

							var marker_name = "",
								sector_ip = "";

							for(var x=0;x<polygonSelectedDevices.length;x++) {
								if(polygonSelectedDevices[x].device_name === allSSIds[i]) {
									marker_name = polygonSelectedDevices[x].name;
									if(polygonSelectedDevices[x].pointType === 'sub_station') {
										sector_ip = "";
									} else {
										sector_ip = polygonSelectedDevices[x].sectorName ? polygonSelectedDevices[x].sectorName : "";
									}
								}
							}

							var newIcon = base_url+"/"+result.data.devices[allSSIds[i]].icon;

							var allMarkerObject = {};
							if(window.location.pathname.indexOf("gearth") > -1) {
								allMarkerObject = allMarkersObject_earth;
							} else if(window.location.pathname.indexOf("wmap") > -1) {
								allMarkerObject = allMarkersObject_wmap;
							} else {
								allMarkerObject = allMarkersObject_gmap;
							}
							var ss_marker = allMarkerObject['sub_station']['ss_'+marker_name],
								sector_marker = allMarkerObject['sector_device']['sector_'+sector_ip],
								marker_polling_obj = {
									"device_name" : allSSIds[i],
									"polling_icon" : newIcon,
									"polling_time" : shown_datetime,
									"polling_value" : result.data.devices[allSSIds[i]].value,
									"ip": ""
								};

							if(polled_devices_names.indexOf(allSSIds[i]) == -1) {
								polled_devices_names.push(allSSIds[i]);
							}
							
							if(!complete_polled_devices_icon[allSSIds[i]]) {
								complete_polled_devices_icon[allSSIds[i]] = [];
							}

							complete_polled_devices_icon[allSSIds[i]].push(newIcon);
							
							/*Update the marker icons*/
							if(ss_marker) {
								if(window.location.pathname.indexOf("gearth") > -1) {
									try {
										updateGoogleEarthPlacemark(ss_marker, newIcon);
									} catch(e) {
										// console.log(e);
									}
								} else if(window.location.pathname.indexOf("wmap") > -1) {
									ss_marker.style.externalGraphic = newIcon;
									var layer = ss_marker.layer ? ss_marker.layer : ss_marker.layerReference;
									layer.redraw();
								} else {
									var ss_live_polled_icon = gmap_self.getMarkerImageBySize(newIcon,"other");
									ss_marker.setOptions({
										"icon" : ss_live_polled_icon
									});
								}
								marker_polling_obj.ip = ss_marker.cktId+" - "+ss_marker.ss_ip;
							}

							if(sector_marker) {
								if(window.location.pathname.indexOf("gearth") > -1) {
									try {
										updateGoogleEarthPlacemark(sector_marker, newIcon);
									} catch(e) {
										// console.log(e);
									}
								} else if(window.location.pathname.indexOf("wmap") > -1) {
									sector_marker.style.externalGraphic = newIcon
									var layer = sector_marker.layer ? sector_marker.layer : sector_marker.layerReference;
									layer.redraw();
								} else {
		                            var sector_live_polled_icon = gmap_self.getMarkerImageBySize(newIcon,"other");
			                        // Update sector marker icon
									sector_marker.setOptions({
										"icon" : sector_live_polled_icon,
										// "clusterIcon" : new google.maps.MarkerImage(base_url+'/static/img/icons/1x1.png',null,null,null,null),
										// "oldIcon" : new google.maps.MarkerImage(newIcon,null,null,null,new google.maps.Size(32, 37))
									});
								}
								marker_polling_obj.ip = sector_marker.cktId+" - "+sector_marker.sectorName;
							}

							complete_polled_devices_data.push(marker_polling_obj);

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
					// callback with true
					callback(true);
				} else {

					$.gritter.add({
			            // (string | mandatory) the heading of the notification
			            title: 'Live Polling - Error',
			            // (string | mandatory) the text inside the notification
			            text: result.message,
			            // (bool | optional) if you want it to fade out on its own or just sit there
			            sticky: false,
			            // Time in ms after which the gritter will dissappear.
	                	time : 1000
			        });

					// callback with false
			        callback(false);
				}
			},
			error : function(err) {

				$.gritter.add({
		            // (string | mandatory) the heading of the notification
		            title: 'Live Polling - Error',
		            // (string | mandatory) the text inside the notification
		            text: err.statusText,
		            // (bool | optional) if you want it to fade out on its own or just sit there
		            sticky: false,
		            // Time in ms after which the gritter will dissappear.
	                time : 1000
		        });
		        // callback with false
		        callback(false);
			},
			complete : function() {
				$("#fetch_polling").button("complete");
			}
		});
    };

    /**
     * This function shows the previous polled icon(if available) on google maps for selected devices
     * @method show_previous_polled_icon
     */
    this.show_previous_polled_icon = function() {
    	if(nav_click_counter > 0) {
    		nav_click_counter--;
    	}
    	/*Remove 'text-info' class from all li's*/
    	$(".deviceWellContainer div div ul li").removeClass("text-info");

    	for(var i=polled_devices_names.length;i--;) {

    		var marker_name = "",
				sector_ip = "";

			for(var x=0;x<polygonSelectedDevices.length;x++) {
				if(polygonSelectedDevices[x].device_name === polled_devices_names[i]) {
					marker_name = polygonSelectedDevices[x].name
					if(polygonSelectedDevices[x].pointType === 'sub_station') {
						sector_ip = polygonSelectedDevices[x].sector_ip ? polygonSelectedDevices[x].sector_ip : "";
					} else {
						sector_ip = polygonSelectedDevices[x].sectorName ? polygonSelectedDevices[x].sectorName : "";
					}
				}
			}

			var ss_marker = allMarkersObject_gmap['sub_station']['ss_'+marker_name],
				sector_marker = allMarkersObject_gmap['sector_device']['sector_'+sector_ip],
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

			var live_polled_icon = gmap_self.getMarkerImageBySize(newIcon,"other");

			if(ss_marker) {
				ss_marker.setOptions({
					"icon" : live_polled_icon
				});
			} else if(sector_marker) {
				sector_marker.setOptions({
					"icon" : live_polled_icon
				});
			}
			$("#pollVal_"+new_device_name+" li.fetchVal_"+new_device_name)[nav_click_counter-1].className = $("#pollVal_"+new_device_name+" li.fetchVal_"+new_device_name)[nav_click_counter-1].className+' text-info';
    	}

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
    this.show_next_polled_icon = function() {

		if(nav_click_counter <= total_polled_occurence) {
    		nav_click_counter++;
    	}

    	$(".deviceWellContainer div div ul li").removeClass("text-info");


    	for(var i=polled_devices_names.length;i--;) {

			var marker_name = "",
				sector_ip = "";

			for(var x=0;x<polygonSelectedDevices.length;x++) {
				if(polygonSelectedDevices[x].device_name === polled_devices_names[i]) {
					marker_name = polygonSelectedDevices[x].name
					if(polygonSelectedDevices[x].pointType === 'sub_station') {
						sector_ip = polygonSelectedDevices[x].sector_ip ? polygonSelectedDevices[x].sector_ip : "";
					} else {
						sector_ip = polygonSelectedDevices[x].sectorName ? polygonSelectedDevices[x].sectorName : "";
					}
				}
			}

			var ss_marker = allMarkersObject_gmap['sub_station']['ss_'+marker_name],
				sector_marker = allMarkersObject_gmap['sector_device']['sector_'+sector_ip],
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

			var live_polled_icon = gmap_self.getMarkerImageBySize(newIcon,"other");

			if(ss_marker) {
				ss_marker.setOptions({
					"icon" : live_polled_icon
				});
			} else if(sector_marker) {
				sector_marker.setOptions({
					"icon" : live_polled_icon
				});
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
	 * This function clear the polygon selection from the map
	 * @method clearPolygon
	 */
	this.clearPolygon = function() {
		
		/*Reset drawing object if exists*/
		if(drawingManager_livePoll && drawingManager_livePoll.getMap()) {
			drawingManager_livePoll.setMap(null);
		}

		/*Clear polygon if exist*/
		if(Object.keys(currentPolygon).length > 0) {
			/*Remove the current polygon from the map*/
			currentPolygon.setMap(null);
		}

		/*Reset marker icon*/
		for(var i=0;i<polygonSelectedDevices.length;i++) {

            var ss_marker = allMarkersObject_gmap['sub_station']['ss_'+polygonSelectedDevices[i].name],
            	sector_ip = "";
            
            if(polygonSelectedDevices[i].pointType && ($.trim(polygonSelectedDevices[i].pointType) == 'sub_station')) {
            	// sector_ip = polygonSelectedDevices[i].sector_ip;
            	sector_ip = "";
            } else {
            	sector_ip = polygonSelectedDevices[i].sectorName;
            }

            var sector_marker = allMarkersObject_gmap['sector_device']['sector_'+sector_ip];

			if(ss_marker) {
				ss_marker.setOptions({
					"icon" : ss_marker.oldIcon
				});
			} else if(sector_marker) {
				sector_marker.setOptions({
					"icon" : sector_marker.oldIcon
				});
			}
    	}

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

    	/*Disable poll interval & max interval dropdown*/
        $("#poll_interval").removeAttr("disabled");
        $("#poll_maxInterval").removeAttr("disabled");
        
        /*Select default value*/
        $("#poll_interval").val($("#poll_interval option:first").val());
        $("#poll_maxInterval").val($("#poll_maxInterval option:first").val());

		/*Reset isPollingActive flag*/
    	isPollingActive = 0;

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

		if(isPerfCallStopped === 0 && isPerfCallStarted == 0) {
			/*Restart performance calling*/
	    	gisPerformanceClass.restart();
    	}
	};

    /**
     * This function show the polled devices data in tabular format & also give option to download that data
     * @method show_polling_datatable
     */
    this.show_polling_datatable = function() {

    	var table_html = "";

    	if(window.location.pathname.indexOf("gearth") > -1) {
    		table_html+= '<iframe allowTransparency="true" style="position:absolute; top:0px; right:0px; width:100%; height:100%;overflow-y:auto; z-index:100;"></iframe>';
    	}

    	table_html += "<div class='polling_table_container'><table style='z-index:9999;' id='polling_data_table' class='datatable table table-striped table-bordered table-hover'><thead><tr><th>Device Name</th><th>Time</th><th>Value</th></tr><thead><tbody>";

    	for(var i=0;i<complete_polled_devices_data.length;i++) {
    		var poll_val = complete_polled_devices_data[i].polling_value;
    			// shown_val = poll_val == "" ? "-" : poll_val;
    		table_html += '<tr>';
    		table_html += '<td>'+complete_polled_devices_data[i].ip+'</td>';
    		table_html += '<td>'+complete_polled_devices_data[i].polling_time+'</td>';
    		table_html += '<td>'+poll_val+'</td>';
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
	                        sFileName : "*.xls",
	                        fnComplete : function(nButton, oConfig, oFlash, sFlash) {
                        		$.gritter.add({
						            title: "Live Polling Report",
						            text: "Live polling report successfully downloaded.",
						            sticky: false,
						            time : 1500
						        });    	
	                        }
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
     * This function retunrns middle point lat lon as per given two points
     * @method getMiddlePoint
     * @param latLonArray {Array}, It contains two lat lon object.
     * @return latLonArray {Object}, It returns center lat lon object.
     */
    this.getMiddlePoint = function(latLonArray) {
    	
    	var lat1 = latLonArray[0].lat * Math.PI / 180,
        	lat2 = latLonArray[1].lat * Math.PI / 180,
        	lon1 = latLonArray[0].lon * Math.PI / 180,
        	dLon = (latLonArray[1].lon - latLonArray[0].lon) * Math.PI / 180,
        	Bx = Math.cos(lat2) * Math.cos(dLon),
        	By = Math.cos(lat2) * Math.sin(dLon);

        var center_lat = Math.atan2(Math.sin(lat1) + Math.sin(lat2), Math.sqrt((Math.cos(lat1) + Bx) * (Math.cos(lat1) + Bx) + By * By)),
            center_lon = lon1 + Math.atan2(By, Math.cos(lat1) + Bx);

        return {"lat" : center_lat, "lon" : center_lon};
    };

    /**
     * This function retunrns the distance between 2 points & middle point lat lon as per given param
     * @method calculateDistance
     */
    this.calculateDistance = function(array) {

    	var latLon1 = new google.maps.LatLng(array[0].getPosition().lat(), array[0].getPosition().lng()),
    		latLon2 = new google.maps.LatLng(array[1].getPosition().lat(), array[1].getPosition().lng());

    	/*Distance in m's */
    	var distance = (google.maps.geometry.spherical.computeDistanceBetween(latLon1, latLon2) / 1000).toFixed(2) * 1000;

    	var latLonArray = [
            {"lat" : array[0].getPosition().lat(), "lon" : array[0].getPosition().lng()},
            {"lat" : array[1].getPosition().lat(), "lon" : array[1].getPosition().lng()},
        ];

        var center_obj = gmap_self.getMiddlePoint(latLonArray);

    	return {distance: distance, lat: center_obj.lat, lon: center_obj.lon};
    };

    /**
     * This function create ruler distance infobox
     * @method createDistanceInfobox
     */
    this.createDistanceInfobox = function(distanceObject) {
    	var distanceInfoBox= new InfoBox({
    		content: distanceObject.distance+" m",
    		boxStyle: {
    			border        : "1px solid #B0AEAE",
    			background 	  : "white",
    			textAlign     : "center",
		        fontSize      : "10px",
		        color         : "black",
		        padding       : '2px',
		        borderRadius  : "5px",
    			width 		  : "60px"
    		},
    		disableAutoPan: true,
    		pixelOffset: new google.maps.Size(-30, -10),
    		position: new google.maps.LatLng(
    			distanceObject.lat3 * 180 / Math.PI,
    			distanceObject.lon3 * 180 / Math.PI
			),
    		closeBoxURL: "",
    		isHidden: false,
    		enableEventPropagation: true,
    		zIndex_: 9999
    	});

    	return distanceInfoBox;
    };

    /**
     * This function clear/reset all the variables and Point related to Rulers in tools
     * @method clearRulerTool_gmap
     */
    this.clearRulerTool_gmap = function() {

    	// clear temporary line if exists
    	if(temp_line) {
    		if(temp_line.map) {
    			temp_line.setMap(null);
    		}
    		temp_line = "";
    	}

    	//Remove Ruler markers
    	for(var i=0;i<ruler_array.length;i++) {
    		if(window.location.pathname.indexOf('gearth') > -1) {
    			ruler_array[i].setVisibility(false);
    		} else {
    			ruler_array[i].setMap(null);	
    		}
    	}
    	ruler_array = [];

    	/*Remove line between two points*/
    	for(var j=0;j<tools_rule_array.length;j++) {
    		if(window.location.pathname.indexOf('gearth') > -1) {
    			tools_rule_array[j].setVisibility(false);
    		} else {
    			tools_rule_array[j].setMap(null);
    		}
    	}
    	tools_rule_array = [];

    	/*Remove Distance Label*/
    	if(distance_label.map != undefined) {
    		if(window.location.pathname.indexOf('gearth') > -1) {
    			distance_label.setVisibility(false);
    		} else {
    			distance_label.setMap(null);
    		}
    	}

    	//set isCreated = 0
    	isCreated= 0;

    	//Reset Cookie
    	$.cookie('tools_ruler', 0, {path: '/', secure : true});


    	tools_ruler = $.cookie("tools_ruler");

    	//reset ruler point count
    	ruler_pt_count = 0;

    	is_ruler_active = -1;
    }

    /**
     * This function create a ruler if any ruler exist in cookie
     * @method create_old_ruler
     */
    this.create_old_ruler = function() {

    	if($.cookie('tools_ruler')) {
    		var ruler_Obj= JSON.parse($.cookie('tools_ruler'));
    		if(ruler_Obj) {
    			var image_a = gmap_self.getMarkerImageBySize(base_url+"/"+letter_a_img_url,"other"),
    				image_b = gmap_self.getMarkerImageBySize(base_url+"/"+letter_b_img_url,"other");
    			var first_point = new google.maps.Marker({
    				position: new google.maps.LatLng(ruler_Obj["startLat"], ruler_Obj["startLon"]),
    				icon : image_a,
    				map: mapInstance
    			});
    			ruler_array.push(first_point);

    			var second_point = new google.maps.Marker({
    				position: new google.maps.LatLng(ruler_Obj["endLat"], ruler_Obj["endLon"]),
    				icon : image_b,
    				map: mapInstance
    			});
    			ruler_array.push(second_point);
    			// Base station info
    			var bs_info = [
					{
			            "title": "Latitude",
			            "name": "latitude",
			            "value": ruler_Obj["startLat"],
			            "show": 1
			        },
			        {
			            "title": "Longitude",
			            "name": "longitude",
			            "value": ruler_Obj["startLon"],
			            "show": 1
			        }
				];
				// Sub station info
    			var ss_info = [
					{
			            "title": "Latitude",
			            "name": "latitude",
			            "value": ruler_Obj["startLat"],
			            "show": 1
			        },
			        {
			            "title": "Longitude",
			            "name": "longitude",
			            "value": ruler_Obj["startLon"],
			            "show": 1
			        }
				];

    			var current_line =  gmap_self.createLink_gmaps(ruler_Obj,ruler_line_color,bs_info,ss_info);
    			// Show line on map
    			current_line.setMap(mapInstance);

    			tools_rule_array.push(current_line);

    			// Update the cookie
    			$.cookie('tools_ruler',JSON.stringify(ruler_Obj),{path: '/', secure : true});

    			tools_ruler = $.cookie("tools_ruler");

				distance_label= gmap_self.createDistanceInfobox(ruler_Obj);

				/*Show distance infobox*/
				distance_label.open(mapInstance);

    			isCreated = 1;

    			hasTools = 1;
    		}
    	}
    }

	/**
	 * This function enables ruler tool & perform corresponding functionality.
	 * @method addRulerTool_gmap
	 */
	this.addRulerTool_gmap = function(tool_type) {
       
        //first clear the click listners. point tool might be in use
        google.maps.event.clearListeners(mapInstance,'click');
        
        //Set the cursor to pointer(Arrow)
        mapInstance.setOptions({'draggableCursor' : 'default'});

		google.maps.event.addListener(mapInstance,'click',function(e) {

			if(tools_rule_array.length) {
				gmap_self.clearRulerTool_gmap();
				return ;
			}
			
			is_ruler_active = 1;
			var pt_image = "";
			if(ruler_pt_count == 0) {
				pt_image = gmap_self.getMarkerImageBySize(base_url+"/"+letter_a_img_url,"other");
			} else {
				pt_image = gmap_self.getMarkerImageBySize(base_url+"/"+letter_b_img_url,"other");
			}

			ruler_point = new google.maps.Marker({
				position: e.latLng, map: mapInstance,
				icon : pt_image
			});
			ruler_array.push(ruler_point);

			if(ruler_pt_count == 1) {
				var distanceObject= gmap_self.calculateDistance(ruler_array);

				/*Lat lon object for poly line*/
				var latLonObj = {
					"startLat" : ruler_array[0].getPosition().lat(),
					"startLon" : ruler_array[0].getPosition().lng(),
					"endLat" : ruler_array[1].getPosition().lat(),
					"endLon" : ruler_array[1].getPosition().lng(),
					"distance": distanceObject.distance,
					"lat3": distanceObject.lat,
					"lon3": distanceObject.lon,
					"nearEndLat" : ruler_array[0].getPosition().lat(),
					"nearEndLon" : ruler_array[0].getPosition().lng(),
					"windowTitle" : "Point A-Point B",
		    		"startTitle" : "Point A",
		    		"endTitle" : "Point B"
				};
				
				// Base station info
    			var bs_info = [
					{
			            "title": "Latitude",
			            "name": "latitude",
			            "value": ruler_array[0].getPosition().lat(),
			            "show": 1
			        },
			        {
			            "title": "Longitude",
			            "name": "longitude",
			            "value": ruler_array[0].getPosition().lng(),
			            "show": 1
			        }
				];
				// Sub station info
    			var ss_info = [
					{
			            "title": "Latitude",
			            "name": "latitude",
			            "value": ruler_array[1].getPosition().lat(),
			            "show": 1
			        },
			        {
			            "title": "Longitude",
			            "name": "longitude",
			            "value": ruler_array[1].getPosition().lng(),
			            "show": 1
			        }
				];

				var ruler_line = gmap_self.createLink_gmaps(latLonObj,ruler_line_color,bs_info,ss_info);
				/*Show Line on Map*/
				ruler_line.setMap(mapInstance);

				// Remove mousemove listener
				// google.maps.event.clearListeners(mapInstance,'mousemove');

				if(temp_line) {
					temp_line.setMap(null);
					temp_line = "";
				}
				
				tools_rule_array.push(ruler_line);

				$.cookie('tools_ruler',JSON.stringify(latLonObj),{path: '/', secure : true});

				tools_ruler = $.cookie("tools_ruler");

				distance_label= gmap_self.createDistanceInfobox(latLonObj);

				/*Show distance infobox*/
				distance_label.open(mapInstance);

				/*True the flag value*/
				isCreated = 1;

				hasTools = 1;
			}

			ruler_pt_count++;
		});
	};

    /**
	 * This function clear/reset all the point drawn by user
	 * @method clearPointsTool_gmap
	 */
    this.clearPointsTool_gmap= function() {

    	if(window.location.pathname.indexOf("gearth") > -1) {
        	for(var i=0; i< map_points_array.length; i++) {
	    		map_points_array[i].setVisibility(false);
	    	}
	    } else if(window.location.pathname.indexOf("wmap") > -1) {

	    } else {
	    	for(var i=0; i< map_points_array.length; i++) {
	    		map_points_array[i].setMap(null);
	    	}
	    }


    	map_points_array= [];

    	map_points_lat_lng_array= [];

    	map_point_count= 0;
    };

    /**
	 * This function draw old/existing points drawn by user
	 * @method create_old_points
	 */
    this.create_old_points = function() {

    	var image = gmap_self.getMarkerImageBySize(base_url+"/static/img/icons/caution.png","other");
    	// var image = new google.maps.MarkerImage(base_url+"/static/img/icons/caution.png",null,null,null,new google.maps.Size(32, 37));


    	if($.cookie("isMaintained")) {

    		var arr= JSON.parse($.cookie("isMaintained"));

    		for(var i=0; i< arr.length; i++) {

    			map_point = new google.maps.Marker({position: new google.maps.LatLng(arr[i]['latLng']["k"], arr[i]['latLng']["B"]), map: mapInstance, icon: image,zIndex: 500});		

    			map_points_array.push(map_point);

    			var ob= {'latLng': arr[i]['latLng'], 'icon': base_url+"/static/img/icons/caution.png"};

    			map_points_lat_lng_array.push(ob);

    			isMaintained = $.cookie("isMaintained");

    			hasTools = 1;

    			map_point_count ++;
	        }
	        return ;
	    }
    };

    /**
	 * This function enables point tool & perform corresponding functionality.
	 * @method addPointTool_gmap
	 */
	this.addPointTool_gmap = function() {

		if(window.location.pathname.indexOf("gearth") > -1) {
			if(pointEventHandler) {
				google.earth.removeEventListener(ge.getGlobe(), 'click', pointEventHandler);
				pointEventHandler = "";
			}

			pointEventHandler = function(event) {
				if (!(event.getTarget().getType() == 'KmlPlacemark' && event.getTarget().getGeometry().getType() == 'KmlPoint') && event.getButton() == 0) {
					if(pointAdded == 1) {
						var infoObj = {};

						infoObj = {
							'lat' : event.getLatitude(),
							'lon' : event.getLongitude(),
							'name' : "",
							'desc' : "",
							'connected_lat' : 0,
							'connected_lon' : 0,
							'connected_point_type' : '',
							'connected_point_info' : '',
							'is_delete_req' : 0,
							'is_update_req' : 0,
							'point_id' : "",
							"icon_url" : point_icon_url
						};
						/*Call function to plot point on gmap*/
						earth_self.plotPoint_earth(infoObj);
					}
				}
				event.preventDefault();
				event.stopPropagation();
			};
			google.earth.addEventListener(ge.getGlobe(), 'click', pointEventHandler);
		} else {
	        //first clear the listners. as ruler tool might be in place
	        google.maps.event.clearListeners(mapInstance,'click');

			google.maps.event.addListener(mapInstance,'click',function(e) {
				
				if(pointAdded == 1) {

					var infoObj = {};

					infoObj = {
						'lat' : e.latLng.lat(),
						'lon' : e.latLng.lng(),
						'name' : "",
						'desc' : "",
						'connected_lat' : 0,
						'connected_lon' : 0,
						'connected_point_type' : '',
						'connected_point_info' : '',
						'is_delete_req' : 0,
						'is_update_req' : 0,
						'point_id' : "",
						"icon_url" : point_icon_url
					};
					/*Call function to plot point on gmap*/
					gmap_self.plotPoint_gmap(infoObj);
				}
			});
		}
	};

	/**
	 * This function plot the point on google map as per the given details
	 * @method plotPoint_gmap
	 * @param {Object} infoObj, It contains information regarding plotting(i.e. lat,lon etc)
	 */
	this.plotPoint_gmap = function(infoObj) {

		var image = gmap_self.getMarkerImageBySize(base_url+""+infoObj.icon_url,"other");

		var map_point = new google.maps.Marker({
			position   	    	 : new google.maps.LatLng(infoObj.lat,infoObj.lon),
			map 	   	    	 : mapInstance,
			icon 	   	    	 : image,
			icon_url   	    	 : infoObj.icon_url,
			zIndex 	   	    	 : 500,
			point_name 	    	 : infoObj.name,
			lat 		    	 : infoObj.lat,
			lon 		    	 : infoObj.lon,
			connected_lat   	 : infoObj.connected_lat,
			connected_lon   	 : infoObj.connected_lon,
			connected_point_type : infoObj.connected_point_type,
			connected_point_info : infoObj.connected_point_info,
			point_desc 	    	 : infoObj.desc,
			point_id 	    	 : infoObj.point_id,
			is_delete_req   	 : infoObj.is_delete_req,
			is_update_req   	 : infoObj.is_update_req
		});

		point_data_obj["point_"+String(infoObj.lat).split(".").join("-")+"_"+String(infoObj.lon).split(".").join("-")] = "";
		point_data_obj["point_"+String(infoObj.lat).split(".").join("-")+"_"+String(infoObj.lon).split(".").join("-")] = map_point;

		// Bind right click event to marker
		(function bindRightMenuToMarker(marker) {
			var markerRightClick= google.maps.event.addListener(marker, 'rightclick', function(event) {
				gmap_self.openPointRightClickMenu(this);
			});

			return markerRightClick;
		})(map_point);

		// Bind click event to marker
		(function bindClickToMarker(marker) {
			var markerClick= google.maps.event.addListener(marker, 'click', function(event) {
				if(marker.point_id) {
					connected_end_obj = {
						"lat" : marker.lat,
						"lon" : marker.lon
					};

					if(current_point_for_line) {
						gmap_self.plot_point_line(marker);
					}
				} else {
					bootbox.alert("This point not saved yet. Please select another.")
				}
			});

			return markerClick;
		})(map_point);
	};

	/**
	 * This function draw the menu item for right click event
	 * @method openPointRightClickMenu
	 * @param {Object} marker, It contains the right clicked marker object
	 */
	this.openPointRightClickMenu = function(marker) {

		var right_click_html = "",
			markerInfo = {
				'name' 				: 	marker['point_name'],
				'desc' 				: 	marker['point_desc'],
				'lat'  				: 	marker['lat'],
				'lon'  				: 	marker['lon'],
				'connected_lat' 	: 	marker['connected_lat'],
				'connected_lon' 	: 	marker['connected_lon'],
				'point_id' 			: 	marker['point_id'],
				'icon_url' 			: 	marker['icon_url'],
				'is_delete_req' 	: 	marker['is_delete_req'],
				'is_update_req' 	: 	marker['is_update_req']
			},
			method_var = JSON.stringify(markerInfo);

		right_click_html += "<div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>Point Tool</h4></div><div class='box-body' style='width:300px;'>";
		right_click_html += "<table class='table table-bordered'><tbody>";
		right_click_html += "<tr><td>Name</td><td><input type='text' class='form-control' name='point_name' id='point_name' value='"+marker.point_name+"'/></td></tr>";
		right_click_html += "<tr><td>Description</td><td><textarea name='point_desc' id='point_desc' class='form-control'>"+marker.point_desc+"</textarea></td></tr>";
		right_click_html += "<tr><td align='center'><button type='button' class='btn btn-sm btn-default' id='point_info_remove_btn' onClick='gmap_self.removePointInfo_gmap("+method_var+")'>Remove Point</button></td><td align='center'><button type='button' class='btn btn-sm btn-default' id='point_info_save_btn' onClick='gmap_self.savePointInfo_gmap("+method_var+")'>Save Point</button></td></tr>";

		/*If point saved then show add/remove line option*/
		if(marker.point_id > 0) {
			if(marker.connected_lat == "" && marker.connected_lon == "") {
				right_click_html += "<tr><td colspan='2' align='center'><button type='button' class='btn btn-sm btn-default' onClick='gmap_self.addLineToPoint_gmap("+method_var+")' id='add_line_from_pt_btn'>Add Line</button></td></tr>";
			}
		}

		right_click_html += "<tr><td colspan='2' align='center' id='response_msg_container'></td></tr>"
		right_click_html +="</tbody></table>";
		right_click_html += "<div class='clearfix'></div></div></div>";


		// openGoogleEarthBaloon(right_click_html, marker)
		if(window.location.pathname.indexOf("gearth") > -1) {
			openGoogleEarthBaloon(right_click_html, marker);
		} else {
			/*Close infowindow if any opened*/
			infowindow.close();
			/*Set the content for infowindow*/
			infowindow.setContent(right_click_html);
			/*Open the info window*/
			infowindow.open(mapInstance,marker);
			
		}
	};

	/**
	 * This function save current point information in db by calling the respective API
	 * @method savePointInfo_gmap
	 */
	this.savePointInfo_gmap = function(marker) {

		var marker_lat_str = String(marker['lat']).split(".").join("-"),
			marker_lon_str = String(marker['lon']).split(".").join("-"),
			current_marker = point_data_obj["point_"+marker_lat_str+"_"+marker_lon_str];

		if($.trim($("#point_name").val()) == '') {
			bootbox.alert("Please enter point name");
		} else {
			try {
				marker['name'] = current_marker['point_name'] = document.getElementById("point_name").value;
				marker['desc'] = current_marker['point_desc'] = document.getElementById("point_desc").value;
				marker['point_id'] = current_marker['point_id'];
				marker['is_update_req'] = current_marker['is_update_req'];
				marker['is_delete_req'] = current_marker['is_delete_req'];

				$.ajax({
	            	url: base_url+'/network_maps/tools/point/',
	            	data: JSON.stringify(marker),
	            	type: 'POST',
	            	dataType: 'json',
	            	success : function(response) {
	            		
	            		var result = "";
						// Type check of response
						if(typeof response == 'string') {
							result = JSON.parse(response);
						} else {
							result = response;
						}

	            		if(result.success === 1) {
	            			current_marker['point_id'] = result.data.point_id;
	            			current_marker['is_update_req'] = result.data.point_id;
	            		} else {
	            			current_marker['name'] = "";
	            			current_marker['desc'] = "";
	            			$("#point_name").val("");
	            			$("#point_desc").val("");
	            			current_marker['point_id'] = 0;
	            			current_marker['is_update_req'] = 0;
	            		}
	            		$("#response_msg_container").html(result.message);
	            	},
	            	error : function(err) {
	            		// console.log(err);
	            	}
	        	});
			} catch(e) {
				// console.log(e);
			}
		}
	};

	/**
	 * This function remove current point information from db if it is saved by calling the respective API
	 * @method removePointInfo_gmap
	 */
	this.removePointInfo_gmap = function(marker) {
		var current_marker = point_data_obj["point_"+String(marker.lat).split(".").join("-")+"_"+String(marker.lon).split(".").join("-")],
			current_line = line_data_obj["point_"+String(marker.lat).split(".").join("-")+"_"+String(marker.lon).split(".").join("-")];
		if(current_marker.point_id > 0) {
			marker.is_delete_req = 1;
			marker.point_id = current_marker.point_id;
			/*Ajax call to delete marker from db*/
			$.ajax({
				url: base_url+'/network_maps/tools/point/',
            	data: JSON.stringify(marker),
            	type: 'POST',
            	dataType: 'json',
            	success : function(response) {
            		
            		var result = "";
					// Type check of response
					if(typeof response == 'string') {
						result = JSON.parse(response);
					} else {
						result = response;
					}

            		if(result.success === 1) {
            			/*Remove point marker from google map*/
            			if(window.location.pathname.indexOf('gearth') > -1) {
							current_marker.setVisibility(false);
							if(current_line) {
								current_line.setVisibility(false);
							}
						} else {
							current_marker.setMap(null);
							if(current_line) {
								current_line.setMap(null);
							}
						}
						/*Delete point from global object*/
						delete point_data_obj["point_"+String(marker.lat).split(".").join("-")+"_"+String(marker.lon).split(".").join("-")];
						delete line_data_obj["point_"+String(marker.lat).split(".").join("-")+"_"+String(marker.lon).split(".").join("-")];
        			} else {
        				$("#response_msg_container").html("Point not removed.Please try again.");		
        			}
            	},
            	error : function(err) {
            		// console.log(err);
            	}
			});
		} else {
			/*Remove point marker from google map*/
			if(window.location.pathname.indexOf('gearth') > -1) {
				current_marker.setVisibility(false);
				if(current_line) {
					current_line.setVisibility(false);
				}
			} else {
				current_marker.setMap(null);
				if(current_line) {
					current_line.setMap(null);
				}
			}
			
			/*Delete point from global object*/
			delete point_data_obj["point_"+String(marker.lat).split(".").join("-")+"_"+String(marker.lon).split(".").join("-")];
			delete line_data_obj["point_"+String(marker.lat).split(".").join("-")+"_"+String(marker.lon).split(".").join("-")];
		}
	};

	/**
	 * This function add line between two points
	 * @method addLineToPoint_gmap
	 */
	this.addLineToPoint_gmap = function(marker) {

		// Close current info window
		if(window.location.pathname.indexOf("gearth") > -1) {
			ge.setBalloon(null);
		} else if(window.location.pathname.indexOf("wmap") > -1) {
			// pass
		} else {
			infowindow.close();
		}

		pointAdded= 1;

		current_point_for_line = "point_"+String(marker.lat).split(".").join("-")+"_"+String(marker.lon).split(".").join("-");

		// infowindow.close();
		$("#infoWindowContainer").addClass('hide');

		//first clear the listners. as ruler tool might be in place
		if(window.location.pathname.indexOf("gearth") > -1) {
			pointEventHandler = "";
			google.earth.removeEventListener(ge.getGlobe(), 'click', pointEventHandler);
			google.earth.addEventListener(ge.getGlobe(), 'click', pointEventHandler);

			pointEventHandler = function(e) {
				if(Object.keys(connected_end_obj).length === 0) {
					bootbox.alert("Please select other point");
				} else {
					$("#point_select").trigger("click");
					connected_end_obj = {};
				}
			}
		} else if(window.location.pathname.indexOf("wmap") > -1) {
			// pass
		} else {
	        google.maps.event.clearListeners(mapInstance,'click');

			google.maps.event.addListener(mapInstance,'click',function(e) {
				if(Object.keys(connected_end_obj).length === 0) {
					bootbox.alert("Please select other point");
				} else {
					$("#point_select").trigger("click");
					connected_end_obj = {};
				}
			});
		}
	};

	/**
	 * This function plot lines between selected points & also call API to update the info in db
	 * @method plot_point_line
	 * @param {Object} marker, It is the google marker objects
	 */
	this.plot_point_line = function(marker) {

		var current_pt = current_point_for_line,
			point_1_name = point_data_obj[current_pt]['point_name'] ? point_data_obj[current_pt]['point_name'] : point_data_obj[current_pt]['alias'],
			point_2_name = marker['point_name'] ? marker['point_name'] : marker['alias'];

		if(!point_1_name) {
			point_1_name = "Point A";
		}

		if(!point_2_name) {
			point_2_name = "Point B";
		}

		var line_obj = {
			"startLat" : point_data_obj[current_pt].lat,
			"startLon" : point_data_obj[current_pt].lon,
			"endLat" : connected_end_obj.lat,
			"endLon" : connected_end_obj.lon,
			"nearEndLat" : point_data_obj[current_pt].lat,
			"nearEndLon" : point_data_obj[current_pt].lon,
			"windowTitle" : "Point A-Point B",
    		"startTitle" : point_1_name,
    		"endTitle" : point_2_name
		};

		var current_line;
		// Base station info
		var bs_info = [
			{
	            "title": "Latitude",
	            "name": "latitude",
	            "value": point_data_obj[current_pt].lat,
	            "show": 1
	        },
	        {
	            "title": "Longitude",
	            "name": "longitude",
	            "value": point_data_obj[current_pt].lon,
	            "show": 1
	        }
		];
		// Sub station info
		var ss_info = [
			{
	            "title": "Latitude",
	            "name": "latitude",
	            "value": connected_end_obj.lat,
	            "show": 1
	        },
	        {
	            "title": "Longitude",
	            "name": "longitude",
	            "value": connected_end_obj.lon,
	            "show": 1
	        }
		];
		/*Create line between the point & device*/
		if(window.location.pathname.indexOf("gearth") > -1) {
			current_line = earth_instance.createLink_earth(line_obj);		
		} else {
			current_line =  gmap_self.createLink_gmaps(line_obj,ruler_line_color,bs_info,ss_info);
		}
		/*Show Line on Map*/
		if(window.location.pathname.indexOf("gearth") > -1) {
			if(getRangeInZoom() > 7) {
				current_line.setVisibility(true);
			} else {
				current_line.setVisibility(false);
			}
		} else {
			if(mapInstance.getZoom() > 7) {
				current_line.setMap(mapInstance);
			} else {
				current_line.setMap(null);
			}
		}
		/*Update Connected Lat Lon info in marker object*/
		point_data_obj[current_pt].connected_lat = connected_end_obj.lat;
		point_data_obj[current_pt].connected_lon = connected_end_obj.lon;
		point_data_obj[current_pt].connected_point_type = marker.pointType ? marker.pointType : "point";
		
		var connected_pt_info = marker.filter_data ? marker.filter_data : "";
		// Add point alias to the filter info if the point is SS, BS or Sector
		if(connected_pt_info) {
			connected_pt_info['alias'] = marker['alias'] ? marker['alias'] : "";
		}

		point_data_obj[current_pt].connected_point_info = JSON.stringify(connected_pt_info);

		line_data_obj[current_pt] = current_line;

		var request_obj = {
			"point_id" 			   : point_data_obj[current_pt].point_id,
			'name' 				   : point_data_obj[current_pt].point_name,
			'desc' 				   : point_data_obj[current_pt].point_desc,
			'connected_lat' 	   : point_data_obj[current_pt].connected_lat,
			'connected_lon' 	   : point_data_obj[current_pt].connected_lon,
			'connected_point_type' : point_data_obj[current_pt].connected_point_type,
			'connected_point_info' : point_data_obj[current_pt].connected_point_info,
			'is_delete_req' 	   : 0,
			'is_update_req' 	   : 1
		};

		/*Save connected line info in db*/
		$.ajax({
        	url: base_url+'/network_maps/tools/point/',
        	data: JSON.stringify(request_obj),
        	type: 'POST',
        	dataType: 'json',
        	success : function(response) {
        		
        		var result = "";
				// Type check of response
				if(typeof response == 'string') {
					result = JSON.parse(response);
				} else {
					result = response;
				}

        		if(result.success === 1) {
        			if(result.data) {
            			point_data_obj[current_pt].point_id = result.data.point_id;
            			point_data_obj[current_pt].is_update_req = result.data.point_id;
        			}
        		}
        	},
        	error : function(err) {
        		// console.log(err);
        	}
    	});


		if(window.location.pathname.indexOf("gearth") > -1) {
			
		} else {
			google.maps.event.addListener(current_line, 'rightclick', function(e) {
				
				var current_line_ptr = this,
					info_window_content = "<button class='btn btn-danger btn-xs' id='remove_tool_line'>Remove Line</button>";
				
				/*Close infowindow if any opened*/
				infowindow.close();
				// $("#infoWindowContainer").addClass('hide');

				/*Set the content for new infowindow*/
				infowindow.setContent(info_window_content);
				
				/*Set The Position for InfoWindow*/
				infowindow.setPosition(e.latLng);
				
				/*Open the info window*/
				infowindow.open(mapInstance);

				// $("#infoWindowContainer").html(info_window_content);
				// $("#infoWindowContainer").removeClass('hide');
				
				/*Triggers when remove line button clicked*/
				$("#remove_tool_line").click(function(e) {
					/*Close infowindow if any opened*/
					infowindow.close();
					gmap_self.remove_point_line(current_pt,current_line_ptr);
				});
			});
		}

		current_point_for_line = "";
	};

	/**
	 * This function removed the given line from gmap & also update the global object
	 * @method remove_point_line
	 */
	this.remove_point_line = function(current_pt,current_line_ptr) {
		if(point_data_obj[current_pt]) {
			var request_obj = {
				"point_id" 		: point_data_obj[current_pt].point_id,
				'name' 			: point_data_obj[current_pt].point_name,
				'desc' 			: point_data_obj[current_pt].point_desc,
				'connected_lat' : 0,
				'connected_lon' : 0,
				'connected_point_type' : '',
				'connected_point_info' : '',
				'is_delete_req' : 0,
				'is_update_req' : 1
			};
			/*Save connected line info in db*/
			$.ajax({
	        	url: base_url+'/network_maps/tools/point/',
	        	data: JSON.stringify(request_obj),
	        	type: 'POST',
	        	dataType: 'json',
	        	success : function(response) {

	        		var result = "";
					// Type check of response
					if(typeof response == 'string') {
						result = JSON.parse(response);
					} else {
						result = response;
					}

	        		if(result.success === 1) {
						// infowindow.close();
						$("#infoWindowContainer").addClass('hide');
						if(window.location.pathname.indexOf("gearth") > -1) {
							current_line_ptr.setVisibility(false);
						} else {
							current_line_ptr.setMap(null);
						}
						// Remove line object from global array
						delete line_data_obj[current_pt];

						/*Update marker object*/
						point_data_obj[current_pt].connected_lat = 0;
						point_data_obj[current_pt].connected_lon = 0;
	        			point_data_obj[current_pt].point_id = result.data.point_id;
	        			point_data_obj[current_pt].is_update_req = result.data.point_id;
	        			point_data_obj[current_pt].connected_point_type = '';
	        			point_data_obj[current_pt].connected_point_info = '';
	        		}
	        	},
	        	error : function(err) {
	        		// console.log(err);
	        	},
	        	complete : function() {
	        		if(infowindow) {
	        			infowindow.close();
	        		}
	        	}
	    	});
		}
	};

	/**
	 * This function call the get_tools_data API to populate available point on gmap
	 * @method get_tools_data_gmap
	 */
	this.get_tools_data_gmap = function() {

		$.ajax({
			url : base_url+"/network_maps/get_tools_data/",
			type : "GET",
			success : function(result) {

				var resultant_data = "";
				if(typeof result == 'string') {
					resultant_data = JSON.parse(result);
				} else {
					resultant_data = result;
				}

				var point_array = resultant_data.data.points;

				for(var i=0;i<point_array.length;i++) {

					var current_point = point_array[i],
						infoObj = {
						'lat' : current_point.lat,
						'lon' : current_point.lon,
						'name' : current_point.name,
						'desc' : current_point.desc,
						'connected_lat' : current_point.connected_lat,
						'connected_lon' : current_point.connected_lon,
						'connected_point_type' : current_point.connected_point_type,
						'connected_point_info' : current_point.connected_point_info,
						'is_delete_req' : 0,
						'is_update_req' : 1,
						'point_id' : current_point.point_id,
						"icon_url" : current_point.icon_url
					};
					/*Call function to plot point on gmap*/
					if(window.location.pathname.indexOf('gearth') > -1) {
						earth_self.plotPoint_earth(infoObj);
					} else {
						gmap_self.plotPoint_gmap(infoObj);
					}

					var start_lat_str = String(current_point.lat).split(".").join("-"),
						start_lon_str = String(current_point.lon).split(".").join("-"),
						end_lat_str = String(current_point.connected_lat).split(".").join("-"),
						end_lon_str = String(current_point.connected_lon).split(".").join("-"),
						point_custom_id = "point_"+start_lat_str+"_"+start_lon_str,
						point_1_name = "",
						point_2_name = "";

					// If any connected point exists
					if(current_point.connected_lat && current_point.connected_lon) {
						if(current_point.connected_point_type &&  current_point.connected_point_type != 'point') {
							var conn_pt_info = JSON.parse(current_point.connected_point_info);
							point_2_name = conn_pt_info['alias'] ? conn_pt_info['alias'] : "";
						} else {
							var end_point_obj = point_data_obj["point_"+end_lat_str+"_"+end_lon_str];
							point_2_name = end_point_obj['point_name'] ? end_point_obj['point_name'] : end_point_obj['alias'];
						}

						if(current_point['name']) {
							point_1_name = current_point['name'];
						} else if(current_point['point_name']) {
							point_1_name = current_point['point_name'];
						} else if(current_point['alias']) {
							point_1_name = current_point['alias'];
						} else {
							point_1_name = "Point A";
						}

						if(!point_2_name) {
							point_2_name = "Point B";
						}

						var line_obj = {
							"startLat"   : current_point.lat,
							"startLon"   : current_point.lon,
							"endLat"     : current_point.connected_lat,
							"endLon"     : current_point.connected_lon,
							"nearEndLat" : current_point.lat,
							"nearEndLon" : current_point.lon,
							"windowTitle" : "Point A-Point B",
				    		"startTitle" : point_1_name,
				    		"endTitle" : point_2_name
						};

						// Base station info
						var bs_info = [
							{
					            "title": "Latitude",
					            "name": "latitude",
					            "value": current_point.lat,
					            "show": 1
					        },
					        {
					            "title": "Longitude",
					            "name": "longitude",
					            "value": current_point.lon,
					            "show": 1
					        }
						];
						// Sub station info
						var ss_info = [
							{
					            "title": "Latitude",
					            "name": "latitude",
					            "value": current_point.connected_lat,
					            "show": 1
					        },
					        {
					            "title": "Longitude",
					            "name": "longitude",
					            "value": current_point.connected_lon,
					            "show": 1
					        }
						];

						/*Create line between the point & device*/
						var current_line = "";
						if(window.location.pathname.indexOf('gearth') > -1) {
							current_line =  earth_self.createLink_earth(line_obj);
						} else {
							current_line =  gmap_self.createLink_gmaps(line_obj,ruler_line_color,bs_info,ss_info);
						}
						
						if(window.location.pathname.indexOf("gearth") > -1) {
							if(getRangeInZoom() > 7) {
								current_line.setVisibility(true);
							} else {
								current_line.setVisibility(false);
							}
						} else {
							if(mapInstance.getZoom() > 7) {
								current_line.setMap(mapInstance);
							} else {
								current_line.setMap(null);
							}
						}
						line_data_obj[point_custom_id] = current_line;

						if(window.location.pathname.indexOf("gearth") > -1) {

						} else {
							google.maps.event.addListener(current_line, 'rightclick', function(e) {
						
								var current_line_ptr = this,
									info_window_content = "<button class='btn btn-danger btn-xs' id='remove_tool_line'>Remove Line</button>";
								
								/*Close infowindow if any opened*/
								infowindow.close();
								// $("#infoWindowContainer").addClass('hide');

								/*Set the content for new infowindow*/
								infowindow.setContent(info_window_content);
								
								/*Set The Position for InfoWindow*/
								infowindow.setPosition(e.latLng);
								
								/*Open the info window*/
								infowindow.open(mapInstance);
								// $("#infoWindowContainer").html(info_window_content);
								// $("#infoWindowContainer").removeClass('hide');
								
								/*Triggers when remove line button clicked*/
								$("#remove_tool_line").click(function(e) {

									gmap_self.remove_point_line(point_custom_id,current_line_ptr);
								});
							});
						}
					}
				}
			},
			error : function(err) {
				// console.log(err.statusText);
			}
		})
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
		// infowindow.close();
		$("#infoWindowContainer").addClass('hide');

		for(var i=0;i<ruler_array.length;i++) {
			ruler_array[i].setMap(null);
		}
		ruler_array = [];

		/*Remove line between two points*/
		for(var j=0;j<tools_rule_array.length;j++) {
			tools_rule_array[j].setMap(null);
		}
		tools_rule_array = [];

		/*Remove Distance Label*/
		if(distance_label.map != undefined) {
			distance_label.setMap(null);
		}

		$.cookie('tools_ruler',0,{path: '/', secure : true});

        if (map_point_count == 0){
            /*Remove click listener from google maps*/
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
	 	$.cookie("isFreezeSelected", isFreeze, {path: '/', secure : true});

	 	freezedAt = (new Date()).getTime();
	 	$.cookie("freezedAt", freezedAt, {path: '/', secure : true});

	 	/*Set Live Polling flag*/
	 	// isPollingActive = 1;
	 	
		if(isPerfCallStopped === 0 && isPerfCallStarted == 0) {
		 	var bs_list = getMarkerInCurrentBound();
	    	if(bs_list.length > 0 && isCallCompleted == 1) {
	    		if(recallPerf != "") {
	    			clearTimeout(recallPerf);
	    			recallPerf = "";
	    		}
	    		gisPerformanceClass.start(bs_list);
	    	}
    	} else {
    		clearTimeout(recallPerf);
            recallPerf = "";
            current_bs_list = [];
    	}
	};

	 /**
	 * This function unfreeze the system & call other function to recall the server
	 * @method unfreezeDevices_gmap
	 */
	this.unfreezeDevices_gmap = function() {

	 	/*Enable freeze flag*/
	 	isFreeze = 0;
	 	$.cookie("isFreezeSelected", isFreeze, {path: '/', secure : true});

	 	freezedAt = 0;
		$.cookie("freezedAt", freezedAt, {path: '/', secure : true});

	 	// Call function to restart perf calling
		gmap_self.restartPerfCalling();
	};

	/**
	 * This function restarts perf calling after 10 seconds interval.
	 * @method restartPerfCalling
	 */
	this.restartPerfCalling = function() {
		// After 10 Seconds restart perf call
	 	setTimeout(function() {
			if(isPerfCallStopped === 0) {
		 		var bs_list = getMarkerInCurrentBound();
		    	if(bs_list.length > 0 && isCallCompleted == 1) {
		    		if(recallPerf) {
		    			clearTimeout(recallPerf);
		    			recallPerf = "";
		    		}
		    		current_bs_list = [];
		    		gisPerformanceClass.start(bs_list);
		    	}
	    	} else {
	    		if(recallPerf) {
	    			clearTimeout(recallPerf);
	    			recallPerf = "";
	    		}
	    	}
	 	},10000);
	};

	/**
	 * This function zoom in to the entered location & add a marker to that position.
	 * @method pointToLatLon
	 * @param lat_lon_str [String], It contains the comma seperated lat,lon value
	 */
	this.pointToLatLon = function(lat_lon_str) {
		
		if(lastSearchedPt.position) {
			lastSearchedPt.setMap(null);
		}

		var lat = +lat_lon_str.split(",")[0],
			lng = +lat_lon_str.split(",")[1];

		var marker = new google.maps.Marker({
			position : new google.maps.LatLng(lat,lng),
			map 	 : mapInstance
		});

		var bounds = new google.maps.LatLngBounds(new google.maps.LatLng(lat,lng));
		mapInstance.fitBounds(bounds);

		var listener = google.maps.event.addListenerOnce(mapInstance, 'bounds_changed', function(event) {
			
			if(mapInstance.getZoom() > 15) {
                mapInstance.setZoom(15);
            }
            
            google.maps.event.removeListener(listener);

            // searchResultData = JSON.parse(JSON.stringify(gmap_self.updateStateCounter_gmaps(true)));
            searchResultData = gmap_self.updateStateCounter_gmaps(true);

            // Set Perf calling Flag
			isPerfCallStopped = 0;
			isPerfCallStarted = 0;

        });

		lastSearchedPt = marker;
	};

	/**
	 * This function hide all items from google map
	 * @method hide_all_elements_gmap
	 */
	this.hide_all_elements_gmap = function() {

		// Clear base-stations
        gmap_self.toggleSpecificMarkers_gmap('base_station',null);
        // Clear sector device
        gmap_self.toggleSpecificMarkers_gmap('sector_device',null);
        // Clear sector polygon
        gmap_self.toggleSpecificMarkers_gmap('sector_polygon',null);
        // Clear sub-stations
        gmap_self.toggleSpecificMarkers_gmap('sub_station',null);
        // Clear link line
        gmap_self.toggleSpecificMarkers_gmap('path',null);

		/*Hide drawn points & lines from tools*/
		var connected_points_array = Object.keys(point_data_obj),
			bs_connected_points = [],
			ss_connected_points = [];

		for(var z=0;z<connected_points_array.length;z++) {
			var point_type = $.trim(point_data_obj[connected_points_array[z]].connected_point_type);
			if(point_type == 'base_station') {
				bs_connected_points.push(connected_points_array[z]);
			} else if(point_type == 'sub_station') {
				ss_connected_points.push(connected_points_array[z]);
			}
		}

		for(var j=0;j<ss_connected_points.length;j++) {
			point_data_obj[ss_connected_points[j]].setMap(null);
			line_data_obj[ss_connected_points[j]].setMap(null);
		}

		for(var j=0;j<bs_connected_points.length;j++) {
			point_data_obj[bs_connected_points[j]].setMap(null);
			line_data_obj[bs_connected_points[j]].setMap(null);
		}

		/*Clear master marker cluster objects*/
		if(masterClusterInstance) {
			masterClusterInstance.clearMarkers();
		}
	};

	/**
	 * This function show all items from google map
	 * @method show_all_elements_gmap
	 */
	this.show_all_elements_gmap = function() {

		// Clear base-stations
        gmap_self.toggleSpecificMarkers_gmap('base_station',mapInstance);
        // Clear sector device
        gmap_self.toggleSpecificMarkers_gmap('sector_device',mapInstance);
        // Clear sector polygon
        gmap_self.toggleSpecificMarkers_gmap('sector_polygon',mapInstance);
        // Clear sub-stations
        gmap_self.toggleSpecificMarkers_gmap('sub_station',mapInstance);
        // Clear link line
        gmap_self.toggleSpecificMarkers_gmap('path',mapInstance);

		/*Show everything on map except connection line*/
		// $.grep(allMarkersArray_gmap,function(marker) {
		// 	marker.setOptions({"isActive" : 1});
		// });

		/*Show drawn points & lines from tools*/
		var connected_points_array = Object.keys(point_data_obj),
			bs_connected_points = [],
			ss_connected_points = [];

		for(var z=0;z<connected_points_array.length;z++) {
			var point_type = $.trim(point_data_obj[connected_points_array[z]].connected_point_type);
			if(point_type == 'base_station') {
				bs_connected_points.push(connected_points_array[z]);
			} else if(point_type == 'sub_station') {
				ss_connected_points.push(connected_points_array[z]);
			}
		}

		for(var j=0;j<ss_connected_points.length;j++) {
			point_data_obj[ss_connected_points[j]].setMap(mapInstance);
			line_data_obj[ss_connected_points[j]].setMap(mapInstance);
		}

		for(var j=0;j<bs_connected_points.length;j++) {
			point_data_obj[bs_connected_points[j]].setMap(mapInstance);
			line_data_obj[bs_connected_points[j]].setMap(mapInstance);
		}

		/*Clear master marker cluster objects*/
		if(masterClusterInstance) {
			masterClusterInstance.clearMarkers();
		}

		/*Add markers to cluster*/
      masterClusterInstance.addMarkers(masterMarkersObj);

      /*Enable Reset Button*/
		$("#resetFilters").button("complete");
	};

	/**
	 * This function show marker which satisfied the filtered data condition
	 * @method showHideMarkers_gmap
	 * @param {Array} dataArray, It contains filtered data array
	 */
	this.showHideMarkers_gmap = function(dataArray) {

		var currently_plotted_bs_ss_markers = [];

		if(dataArray && dataArray.length > 0) {
			gmap_self.hide_all_elements_gmap();
		}

		/*Clear master marker cluster objects*/
		if(masterClusterInstance) {
			masterClusterInstance.clearMarkers();
		}

		var connected_points_array = Object.keys(point_data_obj),
			bs_connected_points = [],
			ss_connected_points = [];

		for(var z=0;z<connected_points_array.length;z++) {
			var point_type = $.trim(point_data_obj[connected_points_array[z]].connected_point_type);
			if(point_type == 'base_station') {
				bs_connected_points.push(connected_points_array[z]);
			} else if(point_type == 'sub_station') {
				ss_connected_points.push(connected_points_array[z]);
			}
		}

		for(var i=0;i<dataArray.length;i++) {
			
			var sectorsArray = dataArray[i].sectors;

			for(var j=0;j<sectorsArray.length;j++) {

				/*Check that the current sector name is present in filtered data or not*/
				var subStationsArray = sectorsArray[j].sub_stations,
					sectorName = sectorsArray[j].ip_address ? $.trim(sectorsArray[j].ip_address) : "",
					radius = sectorsArray[j].radius,
					sector_id = sectorsArray[j].sector_id,
					azimuth = sectorsArray[j].azimuth_angle,
					beamWidth = sectorsArray[j].beam_width,
					bsName = dataArray[i].name ? $.trim(dataArray[i].name) : "",
					bs_marker = allMarkersObject_gmap['base_station']["bs_"+bsName],
					sector_device = allMarkersObject_gmap['sector_device']["sector_"+sectorName],
					sector_polygon = allMarkersObject_gmap['sector_polygon']["poly_"+sectorName+"_"+sector_id];

				for(var k=0;k<subStationsArray.length;k++) {
					/*BS, SS & Sectors from filtered data array*/
					var ssName = subStationsArray[k].name ? $.trim(subStationsArray[k].name) : "",
						ss_marker = allMarkersObject_gmap['sub_station']["ss_"+ssName];

					if(ss_marker) {
						// ss_marker.setMap(mapInstance);
						ss_marker.setOptions({"isActive" : 1});
						// currently_plotted_bs_ss_markers.push(ss_marker);
						/*Add the ss markers to the cluster MarkerCluster object*/
						masterClusterInstance.addMarker(ss_marker);
					}
				}
				
				if(bs_marker) {
					// bs_marker.setMap(mapInstance);
					bs_marker.setOptions({"isActive" : 1});
					// currently_plotted_bs_ss_markers.push(bs_marker);
					/*Add the bs markers to the cluster MarkerCluster object*/
					masterClusterInstance.addMarker(bs_marker);
				}

				if(sector_device) {
					// sector_device.setMap(mapInstance);
					sector_device.setOptions({"isActive" : 1});
				}

				if(sector_polygon) {
					sector_polygon.setOptions({"isActive" : 1});
					// sector_polygon.setMap(mapInstance);
				}

				/*Loop to show/hide points connected to SS*/
				for(var m=0;m<ss_connected_points.length;m++) {
					var point = point_data_obj[ss_connected_points[m]],
						line = line_data_obj[ss_connected_points[m]],
						connected_info = point_data_obj[ss_connected_points[m]].connected_point_info,
						pt_bs_name = connected_info ? $.trim(JSON.parse(connected_info).bs_name) : '',
						pt_ss_name = connected_info ? $.trim(JSON.parse(connected_info).ss_name) : '',
						pt_sector_name = connected_info ? $.trim(JSON.parse(connected_info).sector_name) : '';

					if(pt_bs_name == bsName && pt_ss_name == ssName && pt_sector_name == sectorName) {
						point.setMap(mapInstance);
						line.setMap(mapInstance);
					}
				}

				/*Loop to show/hide points connected to BS*/
				for(var l=0;l<bs_connected_points.length;l++) {
					var point = point_data_obj[bs_connected_points[l]],
						line = line_data_obj[bs_connected_points[l]],
						connected_info = point_data_obj[bs_connected_points[l]].connected_point_info,
						connected_bs_name = connected_info ? $.trim(JSON.parse(connected_info).bs_name) : '';

					if(connected_bs_name == bsName) {
						point.setMap(mapInstance);
						line.setMap(mapInstance);
					}
				}
			}
		}

		/* if zoom level is greater than 8 show all points within the bounds*/
	   	if(mapInstance.getZoom() > 8) {
			gmap_self.showLinesInBounds();
			gmap_self.showSubStaionsInBounds();
			gmap_self.showBaseStaionsInBounds();
			gmap_self.showSectorDevicesInBounds();
			// gmap_self.showBackhaulDevicesInBounds();
			gmap_self.showSectorPolygonInBounds();
			// setTimeout(function(){
			// },350);
	    }
	};

	/**
	 * This function show/hide markers or elements of given key from global object
	 * @method toggleSpecificMarkers_gmap
	 * @param key {String}, It contains one of the key from global object which are to be shown or hide
	 * @param map {null or Object}, It contains null to hide marker & map object to show markers
	 */
	this.toggleSpecificMarkers_gmap = function(key,map) {
		var markers = allMarkersObject_gmap[key];
		if(markers) {
			var marker_keys = Object.keys(markers);
			// Loop object key to show/hide markers
			for(var i=marker_keys.length;i--;) {
				if(markers[marker_keys[i]] && markers[marker_keys[i]].map) {
					markers[marker_keys[i]].setMap(map);
				}
			}
		}
	};

	/**
	 * This function export selected BS inventory by calling respective API
	 * @method exportData_gmap
	 */
	this.exportData_gmap = function() {

		exportDataPolygon = {};

		/*Initialize create Polygon functionality*/
		drawingManager = new google.maps.drawing.DrawingManager({
			drawingMode: google.maps.drawing.OverlayType.POLYGON,
			drawingControl: false,
            polygonOptions: {
              fillColor: '#ffffff',
              fillOpacity: 0,
              strokeWeight: 2,
              clickable: false,
              editable: true,
              zIndex: 1
            }
		});
		
		drawingManager.setMap(mapInstance);

		google.maps.event.addListener(drawingManager, 'overlaycomplete', function(e) {

			var pathArray = e.overlay.getPath().getArray(),
				polygon = new google.maps.Polygon({"path" : pathArray});

			exportDataPolygon = e.overlay;
			exportDataPolygon.type = e.type;
			
			// If markers showing
			if(mapInstance.getZoom() > 7) {
				var bs_obj = allMarkersObject_gmap['base_station'],
					selected_bs_ids = [],
					selected_bs_markers = [];
				for(key in bs_obj) {
					var markerVisible = mapInstance.getBounds().contains(bs_obj[key].getPosition());
		            if(markerVisible) {
		            	if(google.maps.geometry.poly.containsLocation(bs_obj[key].getPosition(),polygon)) {
		            		if(selected_bs_ids.indexOf(bs_obj[key].filter_data.bs_id) == -1) {
		            			selected_bs_ids.push(bs_obj[key].filter_data.bs_id);
		            			selected_bs_markers.push(bs_obj[key]);
		            		} 
		            			
		            	}
	            	}
				}
				
				// If any bs exists
				if(selected_bs_ids.length > 0) {

					inventory_bs_ids = selected_bs_ids;

					var devicesTemplate = "";
					for(var i=0;i<selected_bs_markers.length;i++) {
						var current_bs = selected_bs_markers[i];
						devicesTemplate += '<div class="well well-sm" id="bs_'+current_bs.filter_data.bs_id+'"><h5>'+(i+1)+'.) '+current_bs.bs_alias+'</h5></div>';
					}

					$("#exportData_sideInfo > .panel-body > .bs_list").html(devicesTemplate);

					if($("#exportDeviceContainerBlock").hasClass('hide')) {
						$("#exportDeviceContainerBlock").removeClass('hide');
					}
				// } else if(bs_id_array.length > 200) {
				// 	gmap_self.removeInventorySelection();
				// 	bootbox.alert("Selected BS exceeds maximum limit i.e 200.");
				} else {
					gmap_self.removeInventorySelection();

					bootbox.alert("No BS found in the selected area.");
				}

			} else {
					
				var bs_id_array = [],
					bs_obj_array = [],
        			states_array = [],
        			complete_filtering_data = gmap_self.getSelectedFilteringItems(),
					technology_filter = complete_filtering_data["advance"]["technology"],
					vendor_filter = complete_filtering_data["advance"]["vendor"],
					city_filter = complete_filtering_data["advance"]["city"],
					state_filter = complete_filtering_data["advance"]["state"],
					frequency_filter = complete_filtering_data["advance"]["frequency"],
					polarization_filter = complete_filtering_data["advance"]["polarization"],
					filterObj = complete_filtering_data["basic"],
					isAdvanceFilterApplied = technology_filter.length > 0 || vendor_filter.length > 0 || state_filter.length > 0 || city_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0,
					isBasicFilterApplied = filterObj['technology'] != 'Select Technology' || filterObj['vendor'] != 'Select Vendor' || filterObj['state'] != 'Select State' || filterObj['city'] != 'Select City';

				var states_within_polygon = state_lat_lon_db.where(function(obj) {
        			return google.maps.geometry.poly.containsLocation(new google.maps.LatLng(obj.lat,obj.lon),polygon);
        		});

        		for(var i=0;i<states_within_polygon.length;i++) {
        			if(state_wise_device_labels[states_within_polygon[i].name]) {
        				states_array.push(states_within_polygon[i].name);
        			}
        		}


        		if(states_within_polygon.length > 0) {
					
					var current_bound_devices = all_devices_loki_db.where(function( obj ) {
            			if(!isAdvanceFilterApplied && !isBasicFilterApplied) {
            				if(states_array.indexOf(obj.state) > -1) {
	            				bs_id_array.push(obj.bs_id);
	            				return true;
            				} else {
            					return false;
            				}
            			} else if(isAdvanceFilterApplied) {
            				var technology_count = technology_filter.length >  0 ? $.grep(obj.tech_str.split("|"), function (elem) {
						        	return technology_filter.indexOf(elem) > -1;
						        }).length : 1,
				            	filter_condition1 = technology_count > 0 ? true : false,
				            	vendor_count = vendor_filter.length >  0 ? $.grep(obj.vendor_str.split("|"), function (elem) {
						        	return vendor_filter.indexOf(elem) > -1;
						        }).length : 1,
				                filter_condition2 = vendor_count > 0 ? true : false,
				                filter_condition3 = state_filter.length > 0 ? state_filter.indexOf(obj.state) > -1 : true,
				                filter_condition4 = city_filter.length > 0 ? city_filter.indexOf(obj.city) > -1 : true;
					            
					            // Condition to check for applied advance filters
					            if(filter_condition1 && filter_condition2 && filter_condition3 && filter_condition4) {
					            	if(states_array.indexOf(obj.state) > -1) {
			            				bs_id_array.push(obj.bs_id);
			            				return true;
		            				} else {
		            					return false;
		            				}
					            } else {
					                return false;
					            }
            			} else if(isBasicFilterApplied) {

            				var sectors = obj.sectors,
								basic_filter_condition1 = filterObj['state'] != 'Select State' ? obj.state == filterObj['state'] : true,
								basic_filter_condition2 = filterObj['city'] != 'Select City' ? obj.city == filterObj['city'] : true;;
							for(var i=sectors.length;i--;) {
								var basic_filter_condition3 = filterObj['technology'] != 'Select Technology' ? $.trim(sectors[i]['technology'].toLowerCase()) == $.trim(filterObj['technology'].toLowerCase()) : true,
									basic_filter_condition4 = filterObj['vendor'] != 'Select Vendor' ? $.trim(sectors[i]['vendor'].toLowerCase()) == $.trim(filterObj['vendor'].toLowerCase()) : true

								if(basic_filter_condition1 && basic_filter_condition2 && basic_filter_condition3 && basic_filter_condition4) {
									if(states_array.indexOf(obj.state) > -1) {
			            				bs_id_array.push(obj.bs_id);
			            				return true;
		            				} else {
		            					return false;
		            				}
								} else {
									return false;
								}
							}
        				}
            		});
					
					// Remove unmatched sectors
					for(var x=0;x<current_bound_devices.length;x++) {
						var sectors = current_bound_devices[x].sectors,
							delete_index = [];
						for(var y=0;y<sectors.length;y++) {
							var sector_technology = $.trim(sectors[y].technology.toLowerCase()),
								sector_vendor = $.trim(sectors[y].vendor.toLowerCase());
							if(technology_filter.length > 0 || vendor_filter.length > 0) {
								var advance_filter_condition1 = technology_filter.length ? technology_filter.indexOf(sector_technology) > -1 : true,
									advance_filter_condition1 = vendor_filter.length ? vendor_filter.indexOf(sector_vendor) > -1 : true;
									
								if(!advance_filter_condition1 || !advance_filter_condition2) {
									delete_index.push(y);
								}

							} else {

								if(filterObj['technology'] != 'Select Technology' || filterObj['vendor'] != 'Select Vendor') {
									var basic_filter_technology = filterObj['technology'] != 'Select Technology' ? filterObj['technology'] : false,
										basic_filter_vendor = filterObj['vendor'] != 'Select Vendor' ? filterObj['vendor'] : false,
										basic_filter_condition1 = basic_filter_technology ? basic_filter_technology === sector_technology : true,
										basic_filter_condition2 = basic_filter_vendor ? basic_filter_vendor === sector_vendor : true;
										
									if(!basic_filter_condition1 || !basic_filter_condition2) {
										delete_index.push(y);
									}
								}
							}
						}
						// Delete Unmatched Values
						for(var z=0;z<delete_index.length;z++) {
							current_bound_devices[x].sectors.splice(delete_index[z],1);
						}
					}

					// If any bs exists
					// if(bs_id_array.length > 0 && bs_id_array.length < 200) {
					if(bs_id_array.length > 0) {

						inventory_bs_ids = bs_id_array;

						var devicesTemplate = "";
						for(var i=0;i<current_bound_devices.length;i++) {
							var current_bs = current_bound_devices[i];
							devicesTemplate += '<div class="well well-sm" id="bs_'+current_bs.bs_id+'"><h5>'+(i+1)+'.) '+current_bs.alias+'</h5></div>';
						}

						$("#exportData_sideInfo > .panel-body > .bs_list").html(devicesTemplate);

						if($("#exportDeviceContainerBlock").hasClass('hide')) {
							$("#exportDeviceContainerBlock").removeClass('hide');
						}

					// } else if(bs_id_array.length > 200) {
					// 	gmap_self.removeInventorySelection();
					// 	bootbox.alert("Selected BS exceeds maximum limit i.e 200.");
					} else {
						gmap_self.removeInventorySelection();
						bootbox.alert("No BS found in the selected area.");	
					}

        		} else {
        			gmap_self.removeInventorySelection();

					bootbox.alert("No BS found in the selected area.");	
        		}
			}

			/*Remove drawing mode*/
			if(drawingManager && drawingManager.getMap()) {
				drawingManager.setMap(null);
			}
		});
	};

	/**
     * This function request the server to download select bs inventory report
     * @method downloadInventory_gmap
     */
    this.downloadInventory_gmap = function() {

    	$.ajax({
    		url : base_url+"/inventory/export_selected_bs_inventory/",
    		type : "POST",
    		data : {
    			"base_stations" : JSON.stringify(inventory_bs_ids)
    		},
    		success : function(response) {
    			
    			var result = "";
    			// Type check for API response
    			if(typeof response == 'string') {
    				result = JSON.parse(response);
    			} else {
    				result = response;
    			}

    			$.gritter.add({
		            title: "Export Inventory Devices",
		            text: result.message,
		            sticky: true
		        });
    		},
    		error : function(err) {
    			$.gritter.add({
		            title: "Export Inventory Devices",
		            text: err.statusText,
		            sticky: true
		        });
    		}
    	});

    	// window.open(base_url+"/inventory/export_selected_bs_inventory/?base_stations="+JSON.stringify(inventory_bs_ids),"_blank");
	};

	/**
     * This function remove the selection of downloaded inventory and clear & hide bs list container DIV
     * @method removeInventorySelection
     */
	this.removeInventorySelection = function() {

		$("#exportData_sideInfo > .panel-body > .bs_list").html("");

		if(!$("#exportDeviceContainerBlock").hasClass('hide')) {
			$("#exportDeviceContainerBlock").addClass('hide');
		}

		if(!$("#clearExportDataBtn").hasClass('hide')) {
			$("#clearExportDataBtn").addClass('hide');
		}

		if($("#export_data_gmap").hasClass('hide')) {
			$("#export_data_gmap").removeClass('hide');
		}

		/*Reset the drawing object if exist*/
		if(window.location.pathname.indexOf('gearth') > -1) {
			if(polyPlacemark) {
				polyPlacemark.setVisibility(false);
				gexInstance.edit.endEditLineString(polyPlacemark);
				polyPlacemark = "";
			}
			$("#exportDevices_Iframe").addClass('hide');
		} else if(window.location.pathname.indexOf("wmap") > -1) {
			if(whiteMapClass.livePollingPolygonControl) {
				whiteMapClass.livePollingPolygonControl.deactivate();
				ccpl_map.getLayersByName('export_Polling')[0].removeAllFeatures();
				ccpl_map.getLayersByName('export_Polling')[0].setVisibility(false);
			}
		} else {
			/*Remove drawing mode*/
			if(drawingManager && drawingManager.getMap()) {
				drawingManager.setMap(null);
			}
		}

		/*Remove the polygon if exists*/
		if((typeof exportDataPolygon == 'object' && Object.keys(exportDataPolygon).length > 0) || (typeof exportDataPolygon == 'function' && exportDataPolygon)) {
			if(window.location.pathname.indexOf('gearth') > -1) {
				exportDataPolygon.setVisibility(false);
			} else if(window.location.pathname.indexOf("wmap") > -1) {
				if(whiteMapClass.livePollingPolygonControl) {
					whiteMapClass.livePollingPolygonControl.deactivate();
					ccpl_map.getLayersByName('export_Polling')[0].removeAllFeatures();
					ccpl_map.getLayersByName('export_Polling')[0].setVisibility(false);
				}	
			} else {
				exportDataPolygon.setMap(null);
			}
			exportDataPolygon = {}
		}
	};

	/**
	 * This function removes SS or BS prop labels as per given param
	 * @method removeExistingLabels_gmap
	 * @param element_type {String}, It contains the string value as 'base_station' or 'sub_station'
	 */
	this.removeExistingLabels_gmap = function(element_type) {

		var elements_object = {};
		if(!element_type) {
			return true;
		}

		if(window.location.pathname.indexOf("gearth") > -1) {
        	return true;
        } else if(window.location.pathname.indexOf("wmap") > -1) {
        	elements_object = allMarkersObject_wmap[element_type];
        } else {
        	elements_object = allMarkersObject_gmap[element_type];
        }

        for(key in elements_object) {
        	// If label exists
        	if(tooltipInfoLabel && tooltipInfoLabel[key]) {

        		if(window.location.pathname.indexOf("gearth") > -1) {
		        	return true;
		        } else if(window.location.pathname.indexOf("wmap") > -1) {
		        	tooltipInfoLabel[key].destroy();
		        } else {
		        	tooltipInfoLabel[key].close();
		        }

		        // Delete the label from glabal variable
		        delete tooltipInfoLabel[key];
        	}
    	}

	};

	/**
     * This function create/update selected tooltip value label from/on ss marker
     * @method updateTooltipLabel_gmap
     */
	this.updateTooltipLabel_gmap = function() {

		// var hide_flag = !$("#show_hide_label")[0].checked;
		var hide_flag = false,
			allMarkersObject = {},
			elements_type = 'sub_station',
			dataset_key = 'dataset',
			remove_element_keys = 'base_station',
			param_label_gritter_title = 'SS Parameter Label';

		// In case of BS label
		if(not_ss_param_labels.indexOf(last_selected_label) > -1) {
			elements_type = 'base_station';
			remove_element_keys = 'sub_station';
			dataset_key = 'alias';
			param_label_gritter_title = 'BS Parameter Label';
		}

		// remove all BS or SS labels
		gmap_self.removeExistingLabels_gmap(remove_element_keys);

		if(window.location.pathname.indexOf("gearth") > -1) {
        	allMarkersObject = allMarkersObject_earth;
        } else if(window.location.pathname.indexOf("wmap") > -1) {
        	allMarkersObject = allMarkersObject_wmap;
        } else {
        	allMarkersObject = allMarkersObject_gmap;
        }

		var markers_list = allMarkersObject[elements_type];

		// If any tooltip label exist
		if(Object.keys(tooltipInfoLabel).length < 1) {

			for(key in markers_list) {
				var marker = markers_list[key],
					labelHtml = "";

				if(elements_type == 'base_station') {
					labelHtml = marker[dataset_key];
				} else {
					var labelInfoObject = marker['label_str'] ? marker['label_str'].split('|') : [],
						labelHtml = "";

	            	if(labelInfoObject && labelInfoObject.length) {
	            		var shownVal = labelInfoObject[$('#static_label option:selected').index() - 2] ? $.trim(labelInfoObject[$('#static_label option:selected').index() - 2]) : "NA";
	                    labelHtml += shownVal;
	                }
				}

                // If labelHtml
                if(labelHtml) {

	                var toolTip_infobox = "";

	                if(window.location.pathname.indexOf("gearth") > -1) {
		            	// pass
		            } else if(window.location.pathname.indexOf("wmap") > -1) {
	            	    
	            	    toolTip_infobox = new OpenLayers.Popup(key,
	            	    	new OpenLayers.LonLat(marker.ptLon,marker.ptLat),
	            	    	new OpenLayers.Size(110,18),
	            	    	labelHtml,
	            	    	false
	        	    	);
						

						ccpl_map.addPopup(toolTip_infobox);

						// Remove height prop from div's
	        	    	$('.olPopupContent').css('height','');
	        	    	$('.olPopup').css('height','');

						if($("#"+key).length > 0) {
							// Shift label to left side of marker
		                    var current_left = $("#"+key).position().left;
		                    current_left = current_left - 125;
		                    $("#"+key).css("left",current_left+"px");
						}
		            } else {
		            	toolTip_infobox = gisPerformanceClass.createInfoboxLabel(
	                        labelHtml,
	                        ssParamLabelStyle,
	                        -120,
	                        -10,
	                        marker.getPosition(),
	                        false
	                    );

		                toolTip_infobox.open(mapInstance, marker);
		            }

	                tooltipInfoLabel[key] = toolTip_infobox;
            	}
			}
		} else {
			for(key in markers_list) {
				var marker = markers_list[key],
					labelHtml = "";

				if(elements_type == 'base_station') {
					labelHtml = marker[dataset_key];
				} else {
					var labelInfoObject = marker['label_str'] ? marker['label_str'].split('|') : [];

	            	if(labelInfoObject && labelInfoObject.length) {
	            		var shownVal = labelInfoObject[$('#static_label option:selected').index() - 2] ? $.trim(labelInfoObject[$('#static_label option:selected').index() - 2]) : "NA";
	                    labelHtml = shownVal;
	                }
                }
                // if labelHtml
                if(labelHtml) {

	                if(window.location.pathname.indexOf("gearth") > -1) {
		            	// pass
		            } else if(window.location.pathname.indexOf("wmap") > -1) {
		            	// If label exist for current ss
		                if(tooltipInfoLabel[key]) {
		                	tooltipInfoLabel[key].setContentHTML(labelHtml);
		                } else {
			            	var toolTip_infobox = new OpenLayers.Popup(key,
		            	    	new OpenLayers.LonLat(marker.ptLon,marker.ptLat),
		            	    	new OpenLayers.Size(110,18),
		            	    	labelHtml,
		            	    	false
		        	    	);

							tooltipInfoLabel[key] = toolTip_infobox;

							ccpl_map.addPopup(toolTip_infobox);

							// if(hide_flag) {
							// 	toolTip_infobox.hide();
							// }

							// Remove height prop from div's
		        	    	$('.olPopupContent').css('height','');
		        	    	$('.olPopup').css('height','');

							if($("#"+key).length > 0) {
								// Shift label to left side of marker
		                        var current_left = $("#"+key).position().left;
		                        current_left = current_left - 125;
		                        $("#"+key).css("left",current_left+"px");
	                        }
		                        
						}
		            } else {
		                // If label exist for current ss
		                if(tooltipInfoLabel[key]) {
		                	tooltipInfoLabel[key].setContent(labelHtml);
		                } else {
		                	var toolTip_infobox = gisPerformanceClass.createInfoboxLabel(
		                        labelHtml,
		                        ssParamLabelStyle,
		                        -120,
		                        -10,
		                        marker.getPosition(),
		                        false
		                    );

			                toolTip_infobox.open(mapInstance, marker);
			                tooltipInfoLabel[key] = toolTip_infobox;
		                }
	                }
                }
			}
		}

		$.gritter.add({
            title: param_label_gritter_title,
            text: $.trim($("#static_label option:selected").text())+" - Label Applied Successfully.",
            sticky: false,
            time : 1000
        });
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
		$("#infoWindowContainer").addClass('hide');

		/*Clear lat-lon searched marker if exist*/
        if(lastSearchedPt.position != undefined) {
			lastSearchedPt.setMap(null);
		}

		/*Remove all elements from map*/
		gmap_self.hide_all_elements_gmap();

		/*Clear the marker array of OverlappingMarkerSpiderfier*/
		oms.clearMarkers();
        oms_ss.clearMarkers();

        /*Hide The loading Icon*/
		$("#loadingIcon").hide();

		/*Enable the refresh button*/
		$("#resetFilters").button("complete");
	};

	/**
	 * This function returns the markerImage object for given marker url as per default size
	 * @method getMarkerImageBySize
	 * param markerUrl {String}, It contains the url of marker icon.
	 */
	this.getMarkerImageBySize = function(markerUrl,marker_type,has_pps) {
		// console.log(markerUrl)
		var largeur = 32/1.4,
			hauteur = 37/1.4,
			divideBy = 0.8,
			anchorX = -0.2,
			markerImageObj = "";

		if(marker_type == 'base_station') {
			if(has_pps)
			{	
				largeur = 40/1.4;
				hauteur = 80/1.4;
			} else{
				largeur = 20/1.4;
				hauteur = 40/1.4;
			}
		}

		if(current_icon_size == 'small') {
			divideBy = 1.4;
			anchorX = 0.4;
		} else if(current_icon_size == 'medium') {
			divideBy = 1;
			anchorX = 0;
		} else {
			divideBy = 0.8;
			anchorX = -0.2;
		}

		markerImageObj = new google.maps.MarkerImage(
			markerUrl,
			new google.maps.Size(Math.ceil(largeur/divideBy), Math.ceil(hauteur/divideBy)),
			new google.maps.Point(0, 0), 
			new google.maps.Point(Math.ceil(16-(16*anchorX)), Math.ceil(hauteur/divideBy)),
			new google.maps.Size(Math.ceil(largeur/divideBy), Math.ceil(hauteur/divideBy))
		);

		return markerImageObj;
	};

	/**
	 * This function updates the Marker Icon with the new Size.
	 * @method updateAllMarkersWithNewIcon_gmap
	 */
	this.updateAllMarkersWithNewIcon_gmap = function(iconSize) {

		var largeur = 32/1.4,
			hauteur = 37/1.4,
			largeur_bs = 32/1.4,
			hauteur_bs = 37/1.4,
			divideBy;

		var anchorX, i, markerImage, markerImage2, icon;
		if(iconSize == 'small') {
			divideBy = 1.4;
			anchorX = 0.4;
		} else if(iconSize == 'medium') {
			divideBy = 1;
			anchorX = 0;
		} else {
			divideBy = 0.8;
			anchorX = -0.2;
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
				//Create a new OLD marker Image according to the value selected
				markerImage= new google.maps.MarkerImage(
					iconUrl,
					new google.maps.Size(Math.ceil(largeur/divideBy), Math.ceil(hauteur/divideBy)),
					new google.maps.Point(0, 0), 
					new google.maps.Point(Math.ceil(16-(16*anchorX)), Math.ceil(hauteur/divideBy)),
					new google.maps.Size(Math.ceil(largeur/divideBy), Math.ceil(hauteur/divideBy)));
				//Set oldIcon for Sector Marker to the new image.
				markerIcon.oldIcon= markerImage;

				markerImage= new google.maps.MarkerImage(
					base_url+'/static/img/icons/1x1.png',
					null,
					null,
					null,
					null
					);
				markerIcon.setIcon(markerImage);

				markerImage= new google.maps.MarkerImage(
					base_url+'/static/img/icons/1x1.png',
					null,
					null,
					null,
					null
					);
				markerIcon.clusterIcon= markerImage;
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
						new google.maps.Size(Math.ceil(largeur_bs/divideBy)-5, Math.ceil(hauteur_bs/divideBy)+5),
						new google.maps.Point(0, 0), 
						new google.maps.Point(Math.ceil(16-(16*anchorX)), Math.ceil(hauteur_bs/divideBy)),
						new google.maps.Size(Math.ceil(largeur_bs/divideBy)-5, Math.ceil(hauteur_bs/divideBy)+5));
					//Set oldIcon for BS Marker to the new image
					markerIcon.oldIcon= markerImage;
					markerIcon.setIcon(markerImage);
					markerIcon.clusterIcon= markerImage;
					//Else icon is for SSpointType	     : "sub_station",
				} else if (markerIcon.pointType === "sub_station") {

					//Create a new marker Imge for SS marker according to the value selected for OLD ICON.
					markerImage2= new google.maps.MarkerImage(
						markerIcon.oldIcon.url,
						new google.maps.Size(Math.ceil(largeur/divideBy), Math.ceil(hauteur/divideBy)),
						new google.maps.Point(0, 0), 
						new google.maps.Point(Math.ceil(16-(16*anchorX)), Math.ceil(hauteur/divideBy)),
						new google.maps.Size(Math.ceil(largeur/divideBy), Math.ceil(hauteur/divideBy))
					);
					//Set icon to Marker Image
					markerIcon.setIcon(markerImage2);
					// //Set oldIcon to Marker Image
					markerIcon.oldIcon= markerImage2;
					markerIcon.clusterIcon= markerImage2;
				}
			})(masterMarkersObj[i]);
		}
		//End of Loop through the Master Markers
	};

	/**
	 * This function reset all global variable used in the process
	 * @method resetVariables_gmap
	 */
	this.resetVariables_gmap = function() {

		/*Reset All The Variables*/
		hitCounter = 1;
		showLimit = 0;
		counter = -999;
		devicesObject = {};
		masterMarkersObj = [];
		ssLinkArray = [];
		// labelsArray = [];
		sector_MarkersArray = [];
		sectorMarkersMasterObj = {};
		sectorMarkerConfiguredOn = [];
	};

	/**
	 * This function get the filtered lables & lines as per filtered data
	 * @param {Array} filteredDataArray, It contains the filtered map data object array
	 */
	this.getFilteredLineLabel = function(filteredDataArray) {

		var filtered_label = [],
			shownLinks = [];

		for(var i=0;i<filteredDataArray.length;i++) {

            /*Deep Copy of the filteredDataArray*/
            var bs_data= $.extend( true, {}, filteredDataArray[i]);

            bs_data.sectors=[];            
            /*Sectors Array*/
            for(var j=0;j<filteredDataArray[i].sectors.length;j++) {
                var sector = filteredDataArray[i].sectors[j];

                var ss_data = filteredDataArray[i].sectors[j].sub_stations;
            
                for(var k=0;k<ss_data.length;k++) {
                	var ssName = $.trim(ss_data[k].name),
                		bsName = $.trim(filteredDataArray[i].name),
            			sectorName = $.trim(sector.ip_address);

            		/*Loop For Connection Lines*/
        			for(var l=0;l<ssLinkArray.length;l++) {
        				if((ssLinkArray[l].ssName == ssName) && (ssLinkArray[l].bsName == bsName) && (ssLinkArray[l].sectorName == sectorName)) {
        					shownLinks.push(ssLinkArray[l]);
        				}
        			}

        			/*Loop For Marker Labels*/
        			for (var x = 0; x < labelsArray.length; x++) {
                        var move_listener_obj = labelsArray[x].moveListener_;
                        if (move_listener_obj) {
                            var keys_array = Object.keys(move_listener_obj);
                            for(var z=0;z<keys_array.length;z++) {
                            	var label_marker = move_listener_obj[keys_array[z]];
                                if(typeof label_marker === 'object') {
                                   if((label_marker && label_marker["filter_data"]["bs_name"]) && (label_marker && label_marker["filter_data"]["sector_name"])) {
                                   		if(label_marker.pointType == 'sector_Marker') {
                                   			if (($.trim(label_marker.filter_data.bs_name) == bsName) && ($.trim(label_marker.filter_data.sector_name) == sectorName) ) {
	                                            filtered_label.push(labelsArray[x]);
	                                        }
                                   		} else {
	                                        if (($.trim(label_marker.filter_data.ss_name) == ssName) && ($.trim(label_marker.filter_data.bs_name) == bsName) && ($.trim(label_marker.filter_data.sector_name) == sectorName) ) {
	                                            filtered_label.push(labelsArray[x]);
	                                        }
                                   		}
                                   }
                                }
                            }
                        }
                    }
                }
            }
        }

        /*Reset Search*/
        $("#resetSearchForm").trigger('click');

        ssLinkArray_filtered = shownLinks;

    	labelsArray_filtered = filtered_label;

        gmap_self.removeExtraPerformanceBoxes();
	};

	/**
	 * This function initialized BS maintenance functionality 
	 * @method startBsMaintenanceFunction
	 */
	this.startBsMaintenanceFunction = function(clicked_bs) {
		
		// If user is admin then proceed else do nothing
		if(is_super_admin && admin_val_list.indexOf(is_super_admin) > -1) {

			var base_station_id = clicked_bs.filter_data.bs_id,
				current_maintenance_status = clicked_bs.maintenance_status ? clicked_bs.maintenance_status : "No",
				isChecked = current_maintenance_status == 'Yes' ? "Checked" : "",
				maintenance_html_str = '';

			maintenance_html_str = '<div align="center">\
										<strong>Maintenance Status</strong>\
										<div class="make-switch switch-small">\
											<input type="checkbox" value="'+base_station_id+'" id="yes_no" '+isChecked+'>\
										<div class="clearfix"></div></div>\
										<div class="divide-10"></div>\
										<div>\
											<input type="hidden" name="previous_maintenance_val" id="previous_maintenance_val" \
											value="'+current_maintenance_status+'"/>\
											<button class="btn btn-xs btn-default" id="change_maintenance_status_btn" \
											title="Update Maintenance Status" onClick="gmap_self.updateBSMaintenanceStatus()"\
											>Update</button>\
										</div><div class="clearfix"></div>\
									</div>';

			if(window.location.pathname.indexOf("gearth") > -1) {
		        // pass
		    } else if(window.location.pathname.indexOf("wmap") > -1) {
		        maintenance_popup = new OpenLayers.Popup('bs_main_popup',
		            new OpenLayers.LonLat(clicked_bs.ptLon,clicked_bs.ptLat),
		            new OpenLayers.Size(125,80),
		            maintenance_html_str,
		            false
		        );

		        ccpl_map.addPopup(maintenance_popup);

		        // Remove height prop from div's
    	    	$('.olPopupContent').css('height','');
    	    	$('.olPopup').css('height','');
		    } else {
				// Set Infowindow content
				infowindow.setContent(maintenance_html_str);
				/*Set The Position for InfoWindow*/
				infowindow.setPosition(new google.maps.LatLng(clicked_bs.ptLat,clicked_bs.ptLon));
				/*Shift the window little up*/
				infowindow.setOptions({pixelOffset: new google.maps.Size(-10, -25)});
				// Open infowindow on map
				infowindow.open(mapInstance);       
		    }

		    $("#yes_no").bootstrapSwitch({
				"size" : "small",
				"animate" : true,
				"onText" : "Yes",
				"offText" : "No",
				"onColor" : "danger",
				"offColor" : "primary",
				"disabled" : false
			});
    	}
	};

	/**
	 * This function triggers when 'Update' button on maintenance status popup clicked. It updates the new maintenance status in DB
	 * @method updateBSMaintenanceStatus
	 */
	this.updateBSMaintenanceStatus = function() {

		var updated_maintenance_status = "No",
	        current_bs_id = $("#yes_no").val(),
	        previous_status = $.trim($("#previous_maintenance_val").val());

	    if($("#yes_no")[0].checked) {
	        updated_maintenance_status = "Yes"
	    }

	    // If updated value & previous value are not same then proceed
	    if(previous_status != updated_maintenance_status) {
	        // If we have status & bs id
	        if(String(current_bs_id).length > 0 && String(updated_maintenance_status).length > 0) {

	            // Disable update button
	            $(this).addClass("disabled");
	            $(this).html("Updating...");

	            // Disable bootstrap switch
	            $("#yes_no").bootstrapSwitch('toggleDisabled',true,true);

	            var get_param_str = "?bs_id="+current_bs_id+"&maintenance_status="+updated_maintenance_status;

	            // Make AJAX Call
	            $.ajax({
	                url : base_url+"/network_maps/update_maintenance_status/"+get_param_str,
	                type : "GET",
	                success : function(response) {
	                    var result = "";
	                    // Type check for response
	                    if(typeof response == 'string') {
	                        result = JSON.parse(response);
	                    } else {
	                        result = response;
	                    }

	                    if(result.success == 1) {
	                        var new_status = result.data.maintenance_status ? $.trim(result.data.maintenance_status) : false,
	                            bs_id = result.data.bs_id ? $.trim(result.data.bs_id) : false,
	                            new_icon_url = result.data.icon ? $.trim(result.data.icon) : false;

	                        // If API returns BS ID, Updated Status & Marker URL the proceed
	                        if(new_status && bs_id && new_icon_url) {

	                            // Update new status in input field
	                            $("#previous_maintenance_val").val(new_status);

	                            // Fetch BS data object from loki object
	                            var bs_loki_obj = all_devices_loki_db.where(function(obj) {
	                                    return obj.bs_id == bs_id
	                                }),
	                                bs_data_object = bs_loki_obj.length > 0 ? JSON.parse(JSON.stringify(bs_loki_obj[0])) : false,
	                                bs_name = bs_data_object ? bs_data_object.name : false,
	                                bs_marker = "";


	                            if(window.location.pathname.indexOf("gearth") > -1) {
	                                // pass
	                            } else if(window.location.pathname.indexOf("wmap") > -1) {
	                                bs_marker = bs_name ? allMarkersObject_wmap['base_station']['bs_'+bs_name] : false;
	                            } else {
	                                bs_marker = bs_name ? allMarkersObject_gmap['base_station']['bs_'+bs_name] : false;
	                            }

	                            if(bs_data_object) {
	                                bs_data_object['data']['markerUrl'] = new_icon_url;
	                                bs_data_object['data']['maintenance_status'] = new_status;
	                                // Update Loki Object
	                                all_devices_loki_db.update(bs_data_object);
	                                // If bs marker exist then update 
	                                if(bs_marker) {
	                                    bs_marker['maintenance_status'] = new_status;
	                                    gisPerformanceClass.updateMarkerIcon(bs_marker, new_icon_url, 'base_station');
	                                }
	                            }
	                        } else {

	                            // Revert bootstrap switch status
	                            $("#yes_no").bootstrapSwitch('toggleState',true);

	                            $.gritter.add({
	                                // (string | mandatory) the heading of the notification
	                                title: 'Base Station Maintenance Status',
	                                // (string | mandatory) the text inside the notification
	                                text: "Maintenance status not updated. Please try again later.",
	                                // (bool | optional) if you want it to fade out on its own or just sit there
	                                sticky: false,
	                                // Time in ms after which the gritter will dissappear.
	                                time : 1000
	                            });
	                        }

	                    } else {

	                        // Revert bootstrap switch status
	                        $("#yes_no").bootstrapSwitch('toggleState',true);

	                        $.gritter.add({
	                            // (string | mandatory) the heading of the notification
	                            title: 'Base Station Maintenance Status',
	                            // (string | mandatory) the text inside the notification
	                            text: result.message,
	                            // (bool | optional) if you want it to fade out on its own or just sit there
	                            sticky: false,
	                            // Time in ms after which the gritter will dissappear.
	                            time : 1000
	                        });
	                    }
	                },
	                error : function(err) {

	                    $.gritter.add({
	                        // (string | mandatory) the heading of the notification
	                        title: 'Base Station Maintenance Status',
	                        // (string | mandatory) the text inside the notification
	                        text: err.statusText,
	                        // (bool | optional) if you want it to fade out on its own or just sit there
	                        sticky: false,
	                        // Time in ms after which the gritter will dissappear.
	                        time : 1000
	                    });
	                },
	                complete : function(e) {

	                    // Enable bootstrap switch
	                    $("#yes_no").bootstrapSwitch('toggleDisabled',true,true);

	                    if(e.status != 200) {
	                        // Revert bootstrap switch status
	                        $("#yes_no").bootstrapSwitch('toggleState',true);
	                    }

	                    // Enable Update Button
	                    $("#change_maintenance_status_btn").removeClass("disabled");
	                    $("#change_maintenance_status_btn").html("Update")

	                }
	            });
	        }
	    } else {
	        bootbox.alert("Please Change The Status");
	    }
	    return false;
	};
}