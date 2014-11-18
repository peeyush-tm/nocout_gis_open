/*Global Variables*/

/*global instance & other variables*/
var mapInstance = "",
	gmap_self = "",
	gisPerformanceClass = {},
	infowindow = "",
	drawingManager = "",
	masterClusterInstance = "",
	base_url = "",
	defaultIconSize= 'medium',
	state_lat_lon_db = [],
	counter_div_style = "";

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
	isApiResponse = 1;

/*Global data objects & arrays of map data & filters*/
var main_devices_data_gmaps = [],
	currentlyPlottedDevices = [],
	plottedBsIds = [],
	lastZoomLevel = 5,
	all_devices_loki_db = [],
	state_wise_device_counters = {},
	state_wise_device_labels = {},
	null_state_device_counters = {},
	searchResultData = [],
	clusterOptions = {gridSize: 60, maxZoom: 8},
	markersMasterObj= {'BS': {}, 'Lines': {}, 'SS': {}, 'BSNamae': {}, 'SSNamae': {}, 'LinesName': {}, 'Poly': {}},
    allMarkersObject_gmap= {'base_station': {}, 'path': {}, 'sub_station': {}, 'sector_device': {}, 'sector_polygon': {}},
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
	ssLatArray = [],
	ssLonArray = [],
	masterMarkersObj = [],
	labelsArray = [],
	labelsArray_filtered = [],
	appliedFilterObj_gmaps = {},
	ssLinkArray = [],
	ssLinkArray_filtered = [],
	lastSearchedPt = {},
	pollableDevices = [],
    data_for_filters = [],
    sector_MarkersArray= [],
    sectorMarkersMasterObj= {},
    sectorMarkerConfiguredOn= [],
    place_markers = [],
    allSSIds = [],
	polygonSelectedDevices = [],
	currentPolygon = {},
	polled_devices_names = [],
	complete_polled_devices_data = [],
	complete_polled_devices_icon = {},
	total_polled_occurence = 0,
	nav_click_counter = 0,
	polled_device_count = {},
	currentDevicesObject_gmap= {'base_station': {}, 'path': {}, 'sub_station': {}, 'sector_device': {}};

/*Tools Global Variables*/
var is_line_active = 0,
	is_bs_clicked = 0,
	is_ruler_active= -1,
	line_pt_array =[],
	ruler_array = [],
	tools_rule_array = [],
	isCreated = 0,
	ruler_pt_count = 0,
	distance_label = {},
    map_points_array = [],
    map_points_lat_lng_array= [],
    map_point_count = 0,
    pointAdded= -1,
    tools_line_array =[],
	tools_line_marker_array= [],
	distance_line_label= "",
	point_icon_url = "static/img/icons/tools/point/caution.png",
	point_data_obj = {},
	line_data_obj = {},
	connected_end_obj = {},
	current_point_for_line = "";

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
	fresnel2Color = 'rgb(148,64,237)';



function displayCoordinates(pnt) {
      var coordsLabel = $("#cursor_lat_long");
      var lat = pnt.lat();
      lat = lat.toFixed(4);
      var lng = pnt.lng();
      lng = lng.toFixed(4);
      coordsLabel.html("Latitude: " + lat + "  Longitude: " + lng);
}

var sectorMarkersInMap= [];
var sectorOmsMarkers= [];

function clearPreviousSectorMarkers() {

	for(var i=0; i< sectorMarkersInMap.length; i++) {
		sectorMarkersInMap[i].setMap(null);
	}
	for(var i=0; i< sectorOmsMarkers.length; i++) {
		oms.removeMarker(sectorOmsMarkers[i]);
	}
	sectorMarkersInMap= [];
	sectorOmsMarkers= [];
}

function prepare_oms_object(oms_instance) {
	
	oms_instance.addListener('click', function(marker,e) {

		var image = base_url+'/'+point_icon_url;
		if(pointAdded === 1) {
			
			connected_end_obj = {
				"lat" : e.latLng.lat(),
				"lon" : e.latLng.lng()
			};

			if(current_point_for_line) {
				gmap_self.plot_point_line(marker);
			}

			return ;
		}

		if(is_line_active == 1) {
			is_bs_clicked = 1;
			line_pt_array.push(e.latLng);
			return ;
		}	

		var sectorMarker,
			sectorMarkerOms;
		
		if(marker.pointType === "base_station") {
			//if marker is not spiderfied, stop event and add sector markers here and in oms
			if(!marker.isMarkerSpiderfied) {
				var sectorMarkersAtThePoint = sectorMarkersMasterObj[marker.name];
				if(sectorMarkersAtThePoint && sectorMarkersAtThePoint.length) {
					for(var j=0; j< sectorMarkersAtThePoint.length; j++) {
						if(sectorMarkersAtThePoint[j].isActive == 1) {
							sectorMarker = sectorMarkersAtThePoint[j].setMap(mapInstance);
							sectorMarkersInMap.push(sectorMarker);
							sectorMarkerOms = oms.addMarker(sectorMarkersAtThePoint[j]);
							sectorOmsMarkers.push(sectorMarkerOms);
						}
					}
				}
				marker.isMarkerSpiderfied= true;
				google.maps.event.trigger(marker, 'click');
				return ;
			}
		}

		/*Call the function to create info window content*/
		var content = gmap_self.makeWindowContent(marker);
		/*Set the content for infowindow*/
		$("#infoWindowContainer").html(content);
		$("#infoWindowContainer").removeClass('hide');
		// infowindow.setContent(content);

		// if(e) {
		// 	/*Set The Position for InfoWindow*/
		// 	infowindow.setPosition(e.latLng);
		// } else {
		// 	Set The Position for InfoWindow
		// 	infowindow.setPosition(new google.maps.LatLng(marker.ptLat,marker.ptLon));
		// }
		/*Open the info window*/
		// infowindow.open(mapInstance,marker);

		/*Show only 5 rows, hide others*/
		// gmap_self.show_hide_info();
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
						pathArray.push(new google.maps.LatLng(ssLinkArray[j].bs_lat,ssLinkArray[j].bs_lon));						
						pathArray.push(new google.maps.LatLng(e[i].position.lat(),e[i].position.lng()));
						ssLinkArray[j].setPath(pathArray);
					}
				} else if(pt_type == "base_station") {
					if($.trim(ssLinkArray[j].bsName) == $.trim(e[i].name)) {
						var pathArray = [];

						pathArray.push(new google.maps.LatLng(e[i].position.lat(),e[i].position.lng()));
						pathArray.push(new google.maps.LatLng(ssLinkArray[j].ss_lat,ssLinkArray[j].ss_lon));
						ssLinkArray[j].setPath(pathArray);
					}
				} else if(pt_type == "sector_Marker") {
					if($.trim(ssLinkArray[j].sectorName) == $.trim(e[i].sectorName)) {
						var pathArray = [];
						pathArray.push(new google.maps.LatLng(e[i].position.lat(),e[i].position.lng()));
						pathArray.push(new google.maps.LatLng(ssLinkArray[j].ss_lat,ssLinkArray[j].ss_lon));
						ssLinkArray[j].setPath(pathArray);
					}
				}
			}
		}
        infowindow.close();
    });

    /*Event when markers cluster is collapsed or unspiderify*/
    oms_instance.addListener('unspiderfy', function(e,markers) {
        //un freeze the map when in normal state
        // isFreeze = 0;
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
        	for(var j=0;j<ssLinkArray.length;j++) {
        		var pt_type = $.trim(e[i].pointType);


        		if(pt_type == "sub_station") {
        			if($.trim(ssLinkArray[j].ssName) == $.trim(e[i].name)) {
        				var pathArray = [];
        				pathArray.push(new google.maps.LatLng(ssLinkArray[j].bs_lat,ssLinkArray[j].bs_lon));
        				pathArray.push(new google.maps.LatLng(e[i].ptLat,e[i].ptLon));        				
        				ssLinkArray[j].setPath(pathArray);
        			}
        		} else if(pt_type == "base_station") {
        			if($.trim(ssLinkArray[j].bsName) == $.trim(e[i].name)) {
        				var pathArray = [];
        				pathArray.push(new google.maps.LatLng(ssLinkArray[j].bs_lat,ssLinkArray[j].bs_lon));
        				pathArray.push(new google.maps.LatLng(ssLinkArray[j].ss_lat,ssLinkArray[j].ss_lon));
        				ssLinkArray[j].setPath(pathArray);
        			}
        		} else if(pt_type == "sector_Marker") {
					if($.trim(ssLinkArray[j].sectorName) == $.trim(e[i].sectorName)) {
						var pathArray = [];
						pathArray.push(new google.maps.LatLng(ssLinkArray[j].sector_lat,ssLinkArray[j].sector_lon));
						pathArray.push(new google.maps.LatLng(ssLinkArray[j].ss_lat,ssLinkArray[j].ss_lon));
						ssLinkArray[j].setPath(pathArray);
					}
				}
        	}
        }

        for(var i=0; i< e.length; i++) {
        	if(e[i].name==="base_station") {
				clearPreviousSectorMarkers();
				e[i].isMarkerSpiderfied = false;
        	}
        }
    });
}

function FullScreenCustomControl(controlDiv, map) {

  // Set CSS styles for the DIV containing the control
  // Setting padding to 5 px will offset the control
  // from the edge of the map
  controlDiv.style.padding = '5px';
  $(controlDiv).addClass('custom_fullscreen');

  // Set CSS for the control border
  var controlUI = document.createElement('div');
  controlUI.style.backgroundColor = 'white';
    controlUI.style.borderStyle = 'solid';
    controlUI.style.borderWidth = '1px';
    controlUI.style.borderColor = '#717b87';
    controlUI.style.cursor = 'pointer';
    controlUI.style.textAlign = 'center';
  controlUI.title = 'Click here to full screen';
  controlDiv.appendChild(controlUI);

  // Set CSS for the control interior
  var controlText = document.createElement('div');

    controlText.style.fontFamily = 'Roboto,Arial,sans-serif';
    controlText.style.fontSize = '11px';
    controlText.style.fontWeight = '400';
    controlText.style.paddingTop = '1px';
    controlText.style.paddingBottom = '1px';
    controlText.style.paddingLeft = '6px';
    controlText.style.paddingRight = '6px';
  controlText.innerHTML = '<b>Full Screen</b>';
  controlUI.appendChild(controlText);

  // Setup the click event listeners: simply set the map to
  // Chicago
  google.maps.event.addDomListener(controlUI, 'click', function() {
  	var currentMode= $(this).find('b').html();
  	if(currentMode=== "Full Screen") {
  		$(this).find('b').html("Exit Full Screen");
  	} else {
  		$(this).find('b').html("Full Screen");
  	}
  	$("#goFullScreen").trigger('click');
    // map.setCenter(chicago)
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
			var mapObject = {};
			if(window.location.pathname.indexOf("google_earth") > -1) {
				mapObject = {
					center    : new google.maps.LatLng(21.1500,79.0900),
					zoom      : 5,
					mapTypeId : google.maps.MapTypeId.HYBRID/*google.maps.MapTypeId.SATELLITE*/,
					mapTypeControl : true,
					mapTypeControlOptions: {
						mapTypeIds: [google.maps.MapTypeId.SATELLITE, google.maps.MapTypeId.HYBRID],
						style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
					}
				};
			} else {
				mapObject = {
					center    : new google.maps.LatLng(21.1500,79.0900),
					zoom      : 5,
					mapTypeId : google.maps.MapTypeId.ROADMAP,
					mapTypeControl : true,
					mapTypeControlOptions: {
						mapTypeIds: [google.maps.MapTypeId.ROADMAP, google.maps.MapTypeId.TERRAIN,google.maps.MapTypeId.SATELLITE, google.maps.MapTypeId.HYBRID],
						style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
					},
					draggableCursor : ''
				};
			}

			/*Create Map Type Object*/
			mapInstance = new google.maps.Map(document.getElementById(domElement),mapObject);

			/*Initialize markercluster*/
         	masterClusterInstance = new MarkerClusterer(mapInstance, [], clusterOptions);

         	//display advance search, filter etc button when call is going on.
			disableAdvanceButton();

			/*style for state wise counter label*/
			counter_div_style = "margin-left:-30px;margin-top:-30px;cursor:pointer;background:url("+base_url+"/static/js/OpenLayers/img/state_cluster.png) top center no-repeat;text-align:center;width:65px;height:65px;";

			/*Initialize Loki db for bs,ss,sector,line,polygon*/
			// Create the database:
			var db = new loki('loki.json');

			// Create a collection:
			bs_loki_db = db.addCollection('base_station')
			ss_loki_db = db.addCollection('sub_station')
			sector_loki_db = db.addCollection('sector_device')
			polygon_loki_db = db.addCollection('sector_polygon')
			line_loki_db = db.addCollection('path')
			all_devices_loki_db = db.addCollection('allDevices');

			state_lat_lon_db = db.addCollection('state_lat_lon');

			state_lat_lon_db.insert({"name" : "Andhra Pradesh","lat" : 16.50,"lon" : 80.64});
			state_lat_lon_db.insert({"name" : "Arunachal Pradesh","lat" : 27.06,"lon" : 93.37});
			state_lat_lon_db.insert({"name" : "Assam","lat" : 26.14,"lon" : 91.77});
			state_lat_lon_db.insert({"name" : "Bihar","lat" : 25.37,"lon" : 85.13});
			state_lat_lon_db.insert({"name" : "Chhattisgarh","lat" : 21.27,"lon" : 81.60});
			state_lat_lon_db.insert({"name" : "Delhi","lat" : 28.61,"lon" : 77.23});
			state_lat_lon_db.insert({"name" : "Goa","lat" : 15.4989,"lon" : 73.8278});
			state_lat_lon_db.insert({"name" : "Gujrat","lat" : 23.2167,"lon" : 72.6833});
			state_lat_lon_db.insert({"name" : "Haryana","lat" : 30.73,"lon" : 76.78});
			state_lat_lon_db.insert({"name" : "Himachal Pradesh","lat" : 31.1033,"lon" : 77.1722});
			state_lat_lon_db.insert({"name" : "Jammu and Kashmir","lat" : 33.45,"lon" : 76.24});
			state_lat_lon_db.insert({"name" : "Jharkhand","lat" : 23.3500,"lon" : 85.3300});
			state_lat_lon_db.insert({"name" : "Karnataka","lat" : 12.9702,"lon" : 77.5603});
			state_lat_lon_db.insert({"name" : "Kerala","lat" : 8.5074,"lon" : 76.9730});
			state_lat_lon_db.insert({"name" : "Madhya Pradesh","lat" : 23.2500,"lon" : 77.4170});
			state_lat_lon_db.insert({"name" : "Maharashtra","lat" : 18.9600,"lon" : 72.8200});
			state_lat_lon_db.insert({"name" : "Manipur","lat" : 24.8170,"lon" : 93.9500});
			state_lat_lon_db.insert({"name" : "Meghalaya","lat" : 25.5700,"lon" : 91.8800});
			state_lat_lon_db.insert({"name" : "Mizoram","lat" : 23.3600,"lon" : 92.0000});
			state_lat_lon_db.insert({"name" : "Nagaland","lat" : 25.6700,"lon" : 94.1200});
			state_lat_lon_db.insert({"name" : "Orissa","lat" : 20.1500,"lon" : 85.5000});
			state_lat_lon_db.insert({"name" : "Punjab","lat" : 30.7900,"lon" : 76.7800});
			state_lat_lon_db.insert({"name" : "Rajasthan","lat" : 26.5727,"lon" : 73.8390});
			state_lat_lon_db.insert({"name" : "Sikkim","lat" : 27.3300,"lon" : 88.6200});
			state_lat_lon_db.insert({"name" : "Tamil Nadu","lat" : 13.0900,"lon" : 80.2700});
			state_lat_lon_db.insert({"name" : "Tripura","lat" : 23.8400,"lon" : 91.2800});
			state_lat_lon_db.insert({"name" : "Uttarakhand","lat" : 30.3300,"lon" : 78.0600});
			state_lat_lon_db.insert({"name" : "Uttar Pradesh","lat" : 26.8500,"lon" : 80.9100});
			state_lat_lon_db.insert({"name" : "West Bengal","lat" : 22.5667,"lon" : 88.3667});
			state_lat_lon_db.insert({"name" : "Andaman and Nicobar Islands","lat" : 11.6800,"lon" : 92.7700});
			state_lat_lon_db.insert({"name" : "Lakshadweep","lat" : 10.5700,"lon" : 72.6300});
			state_lat_lon_db.insert({"name" : "Pondicherry","lat" : 11.9300,"lon" : 79.8300});
			state_lat_lon_db.insert({"name" : "Dadra And Nagar Haveli","lat" : 20.2700,"lon" : 73.0200});

			/*Show The loading Icon*/
			$("#loadingIcon").show();

			/*Disable the refresh button*/
			$("#resetFilters").button("loading");


            /*show co ordinates on mouse move*/
            google.maps.event.addListener(mapInstance, 'mousemove', function (event) {
                displayCoordinates(event.latLng);
            });

            google.maps.event.addListener(mapInstance, 'idle', function() {
            	
            	/* When zoom level is greater than 8 show lines */
            	if(mapInstance.getZoom() > 7) {
            		
            		if(mapInstance.getZoom() === 8) {

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

	            		var technology_filter = $("#filter_technology").select2('val').length > 0 ? $("#filter_technology").select2('val').join(',').split(',') : [],
							vendor_filter = $("#filter_vendor").select2('val').length > 0 ? $("#filter_vendor").select2('val').join(',').split(',') : [],
							city_filter = $("#filter_city").select2('val').length > 0 ? $("#filter_city").select2('val').join(',').split(',') : [],
							state_filter = $("#filter_state").select2('val').length > 0 ? $("#filter_state").select2('val').join(',').split(',') : [],
							frequency_filter = $("#filter_frequency").select2('val').length > 0 ? $("#filter_frequency").select2('val').join(',').split(',') : [],
							polarization_filter = $("#filter_polarization").select2('val').length > 0 ? $("#filter_polarization").select2('val').join(',').split(',') : [],
							filterObj = {
								"technology" : $.trim($("#technology option:selected").text()),
								"vendor" : $.trim($("#vendor option:selected").text()),
								"state" : $.trim($("#state option:selected").text()),
								"city" : $.trim($("#city option:selected").text())
							},
							isAdvanceFilterApplied = technology_filter.length > 0 || vendor_filter.length > 0 || state_filter.length > 0 || city_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0,
							isBasicFilterApplied = filterObj['technology'] != 'Select Technology' || filterObj['vendor'] != 'Select Vendor' || filterObj['state'] != 'Select State' || filterObj['city'] != 'Select City',
							advance_filter_condition = technology_filter.length > 0 || vendor_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0,
							basic_filter_condition = $.trim($("#technology").val()) || $.trim($("#vendor").val()),
							data_to_plot = [];

	            		if(searchResultData.length > 0) {
	            			data_to_plot = searchResultData;
	            		} else {

	            			var filtered_devices = [],
	            				current_bound_devices = [];

	            			if(isAdvanceFilterApplied || isBasicFilterApplied) {
	            				filtered_devices = gmap_self.getFilteredData_gmap();
            				} else {
            					filtered_devices = all_devices_loki_db.data;
            				}
            				// IF any states exists
            				if(states_array.length > 0) {
	            				for(var i=filtered_devices.length;i--;) {
									var current_bs = filtered_devices[i];
									if(states_array.indexOf(current_bs.data.state) > -1) {
										current_bound_devices.push(current_bs);
									}
	            				}
            				} else {
            					current_bound_devices = filtered_devices;
            				}

							if(advance_filter_condition || basic_filter_condition) {
								data_to_plot = gmap_self.getFilteredBySectors(current_bound_devices);
							} else {
		            			data_to_plot = current_bound_devices;
							}
	            		}

	            		// If any data exists
	            		if(data_to_plot.length > 0) {
	            			// if(lastZoomLevel < mapInstance.getZoom()) {
			            		/*Clear all everything from map*/
								$.grep(allMarkersArray_gmap,function(marker) {
									marker.setMap(null);
								});
								// Reset Variables
								allMarkersArray_gmap = [];
								main_devices_data_gmaps = [];
								currentlyPlottedDevices = [];
								allMarkersObject_gmap= {
									'base_station': {},
									'path': {},
									'sub_station': {},
									'sector_device': {},
									'sector_polygon': {}
								};

								/*Clear master marker cluster objects*/
								if(masterClusterInstance) {
									masterClusterInstance.clearMarkers();
								}
	            			// }

							main_devices_data_gmaps = data_to_plot;
							
							// var inBoundData = gmap_self.getNewBoundsDevices();

							// currentlyPlottedDevices = inBoundData;

							// Call function to plot devices on gmap
							gmap_self.plotDevices_gmap(data_to_plot,"base_station");

							var polylines = allMarkersObject_gmap['path'],
								polygons = allMarkersObject_gmap['sector_polygon'];

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
	            		}

	            		// Show points line if exist
	            		for(key in line_data_obj) {
	            			line_data_obj[key].setMap(mapInstance);
	            		}
            		// 8 LEVEL ZOOM CONDITION
            		} else {

    					gmap_self.showLinesInBounds();
						gmap_self.showSubStaionsInBounds();
						gmap_self.showBaseStaionsInBounds();
						gmap_self.showSectorDevicesInBounds();
						gmap_self.showSectorPolygonInBounds();
            		}

            		// Start performance calling after 1.5 Second
					setTimeout(function() {
	    				var bs_id_list = getMarkerInCurrentBound();
		            	if(bs_id_list.length > 0 && isCallCompleted == 1) {
		            		if(recallPerf != "") {
		            			clearTimeout(recallPerf);
		            			recallPerf = "";
		            		}
		            		gisPerformanceClass.start(bs_id_list);
		            	}
	            	},500);

	            } else if(mapInstance.getZoom() <= 7) {
	            	
					// Clear performance calling timeout
					if(recallPerf != "") {
            			clearTimeout(recallPerf);
            			recallPerf = "";
            		}

					/*Loop to hide Marker Labels*/
        			for (var x = 0; x < labelsArray.length; x++) {
                        var move_listener_obj = labelsArray[x].moveListener_;
                        if (move_listener_obj) {
                            var keys_array = Object.keys(move_listener_obj);
                            for(var z=0;z<keys_array.length;z++) {
                            	var label_marker = move_listener_obj[keys_array[z]];
                                if(typeof label_marker === 'object') {
                                   if((label_marker && label_marker["filter_data"]["bs_name"]) && (label_marker && label_marker["filter_data"]["sector_name"])) {
                                   		labelsArray[x].close();
                                   }
                                }
                            }
                        }
                    }

                    // Reset labels array 
                    labelsArray = [];

                    /*Clear all everything from map*/
					$.grep(allMarkersArray_gmap,function(marker) {
						marker.setOptions({"isActive" : 0});
						marker.setMap(null);
					});
					// Reset Variables
					allMarkersArray_gmap = [];
					main_devices_data_gmaps = [];
					plottedBsIds = [];
					currentlyPlottedDevices = [];
					allMarkersObject_gmap= {
						'base_station': {},
						'path': {},
						'sub_station': {},
						'sector_device': {},
						'sector_polygon': {}
					};

					/*Clear master marker cluster objects*/
					if(masterClusterInstance) {
						masterClusterInstance.clearMarkers();
					}


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
            			line_data_obj[key].setMap(null);
            		}
	            }

	            // Save last Zoom Value
	            lastZoomLevel = mapInstance.getZoom();
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
            var listener = google.maps.event.addListener(mapInstance, "idle", function() {
            	/*check for current zoom level*/
            	if(mapInstance.getZoom() >= 15) {
            		mapInstance.setZoom(15);
            	}
            	google.maps.event.removeListener(listener);
            });
        });


			var fullScreenCustomDiv = document.createElement('div');
			var fullScreenCustomControl = new FullScreenCustomControl(fullScreenCustomDiv, mapInstance);
			fullScreenCustomDiv.index = 1;
			mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].push(fullScreenCustomDiv);

			
			/*Add Full Screen Control*/
			mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].push(new FullScreenControl(mapInstance));

			/*Create performance lib instance*/
            gisPerformanceClass= new GisPerformance();

			/*Create a instance of OverlappingMarkerSpiderfier*/
			oms = new OverlappingMarkerSpiderfier(mapInstance,{markersWontMove: true, markersWontHide: true, keepSpiderfied: true});
            oms_ss = new OverlappingMarkerSpiderfier(mapInstance,{markersWontMove: true, markersWontHide: true, keepSpiderfied: true});

            prepare_oms_object(oms);
            prepare_oms_object(oms_ss);

			/*Create a instance of google map info window*/
			infowindow = new google.maps.InfoWindow({zIndex:800});
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

		if(counter > 0 || counter == -999) {
			/*Ajax call to the API*/
			$.ajax({
				url : base_url+"/"+"device/stats/?total_count="+devicesCount+"&page_number="+hitCounter,
				type : "GET",
				dataType : "json",
				/*If data fetched successful*/
				success : function(result) {
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
							// gmap_self.plotDevices_gmap(result.data.objects.children,"base_station");
							gmap_self.showStateWiseData_gmap(result.data.objects.children);

                    		/*Decrement the counter*/
							counter = counter - 1;

							/*Call the function after 3 sec. for lazyloading*/
							setTimeout(function() {
								gmap_self.getDevicesData_gmap();
							},10);
						} else {
							
							isCallCompleted = 1;
							disableAdvanceButton('no');
							gmap_self.showStateWiseData_gmap([]);
							// gmap_self.plotDevices_gmap([],"base_station");
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

					/*Enable the refresh button*/
					$("#resetFilters").button("complete");

					setTimeout(function() {
						var current_zoom_level = mapInstance.getZoom();
    					if(current_zoom_level > 7) {
							var bs_list = getMarkerInCurrentBound();
			            	if(bs_list.length > 0 && isCallCompleted == 1) {            		
			            		if(recallPerf != "") {
			            			clearTimeout(recallPerf);
			            			recallPerf = "";
			            		}
			            		gisPerformanceClass.start(bs_list);
			            	}
		            	}
						// gisPerformanceClass.start(getMarkerInCurrentBound());
					}, 30000);

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
			setTimeout(function() {
				var current_zoom_level = mapInstance.getZoom();
				if(current_zoom_level > 7) {
					var bs_list = getMarkerInCurrentBound();
	            	if(bs_list.length > 0 && isCallCompleted == 1) {            		
	            		if(recallPerf != "") {
	            			clearTimeout(recallPerf);
	            			recallPerf = "";
	            		}
	            		gisPerformanceClass.start(bs_list);
	            	}
            	}
				// gisPerformanceClass.start(getMarkerInCurrentBound());
			}, 30000);
			/*Recall the server after particular timeout if system is not freezed*/
			setTimeout(function(e){
				gmap_self.recallServer_gmap();
			},21600000);
		}
	};

	/**
     * This function show counter of state wise data on gmap
     * @method showStateWiseData_gmap
     * @param dataset {Object} In case of BS, it is the devies object array & for SS it contains BS marker object with SS & sector info
	 */
	this.showStateWiseData_gmap = function(dataset) {
		//Loop For Base Station
		for(var i=dataset.length;i--;) {

			/*Create BS state,city object*/
			if(dataset[i].data.state) {

				state_city_obj[dataset[i].data.state] = state_city_obj[dataset[i].data.state] ? state_city_obj[dataset[i].data.state] : [];
				if(state_city_obj[dataset[i].data.state].indexOf(dataset[i].data.city) == -1) {
					state_city_obj[dataset[i].data.state].push(dataset[i].data.city);
				}
			}

			if(dataset[i].data.city) {
				if(all_cities_array.indexOf(dataset[i].data.city) == -1) {
					all_cities_array.push(dataset[i].data.city); 
				}
			}

			var current_bs = dataset[i],
				state = current_bs.data.state,
				sectors_data = current_bs.data.param.sector ? current_bs.data.param.sector : [],
				update_state_str = state ? state : "",
				state_lat_lon_obj = state_lat_lon_db.find({"name" : update_state_str}).length > 0 ? state_lat_lon_db.find({"name" : update_state_str})[0] : false,
				state_param = state_lat_lon_obj ? JSON.stringify(state_lat_lon_obj) : false,
				state_click_event = "onClick='gmap_self.state_label_clicked("+state_param+")'";

			// If state is not null
			if(state) {
				if(state_wise_device_counters[state]) {
					state_wise_device_counters[state] += 1;
					if(state_lat_lon_obj) {
						// Update the content of state counter label as per devices count
						state_wise_device_labels[state].setContent("<div "+state_click_event+" style='"+counter_div_style+"'><p style='position:relative;padding-top:24px;font-weight:bold;' title='Load "+state+" Data.'>"+state_wise_device_counters[state]+"</p></div>");
					}
				} else {
					state_wise_device_counters[state] = 1;
					if(state_lat_lon_obj) {
						var device_counter_label = new InfoBox({
				            content: "<div "+state_click_event+" style='"+counter_div_style+"'><p style='position:relative;padding-top:24px;font-weight:bold;' title='Load "+state+" Data.'>"+state_wise_device_counters[state]+"</p></div>",
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
				var lat = current_bs.data.lat,
					lon = current_bs.data.lon,
					allStateBoundries = state_boundries_db.data,
					bs_point = new google.maps.LatLng(lat,lon);

				// Loop to find that the lat lon of BS lies in which state.
				for(var y=allStateBoundries.length;y--;) {
					var current_state_boundries = allStateBoundries[y].boundries,
						current_state_name = allStateBoundries[y].name,
						latLonArray = [];;
					if(current_state_boundries.length > 0) {
						for(var z=current_state_boundries.length;z--;) {
							latLonArray.push(new google.maps.LatLng(current_state_boundries[z].lat,current_state_boundries[z].lon));
						}
						var state_polygon = new google.maps.Polygon({"path" : latLonArray});
						if(google.maps.geometry.poly.containsLocation(bs_point, state_polygon)) {
							//Update json with state name
							dataset[i]['data']['state'] = current_state_name;
							state = current_state_name;
                            state_lat_lon_obj = state_lat_lon_db.find({"name" : state}).length > 0 ? state_lat_lon_db.find({"name" : state})[0] : false;
                            state_param = state_lat_lon_obj ? JSON.stringify(state_lat_lon_obj) : false;
                            state_click_event = "onClick='gmap_self.state_label_clicked("+state_param+")'";

							var new_lat_lon_obj = state_lat_lon_db.where(function(obj) {
								return obj.name === current_state_name;
							});
							if(state_wise_device_counters[current_state_name]) {
								state_wise_device_counters[current_state_name] += 1;
								state_wise_device_labels[current_state_name].setContent("<div "+state_click_event+" style='"+counter_div_style+"'><p style='position:relative;padding-top:24px;font-weight:bold;' title='Load "+state+" Data.'>"+state_wise_device_counters[current_state_name]+"</p></div>");
							} else {
								state_wise_device_counters[current_state_name] = 1;
								var device_counter_label = new InfoBox({
						            content: "<div "+state_click_event+" style='"+counter_div_style+"'><p style='position:relative;padding-top:24px;font-weight:bold;' title='Load "+state+" Data.'>"+state_wise_device_counters[current_state_name]+"</p></div>",
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

				tech_vendor_obj[sectors_data[j].technology] = tech_vendor_obj[sectors_data[j].technology] ? tech_vendor_obj[sectors_data[j].technology] : [];
				if(tech_vendor_obj[sectors_data[j].technology].indexOf(sectors_data[j].vendor) == -1) {
					tech_vendor_obj[sectors_data[j].technology].push(sectors_data[j].vendor);
				}

				if(all_vendor_array.indexOf(sectors_data[j].vendor) == -1) {
					all_vendor_array.push(sectors_data[j].vendor); 
				}

				var total_ss = sectors_data[j].sub_station ? sectors_data[j].sub_station.length : 0;
				// state_wise_device_counters[state] += 1;
				state_wise_device_counters[state] += total_ss;
				if(state_lat_lon_obj) {
					// Update the content of state counter label as per devices count
					state_wise_device_labels[state].setContent("<div "+state_click_event+" style='"+counter_div_style+"'><p style='position:relative;padding-top:24px;font-weight:bold;' title='Load "+state+" Data.'>"+state_wise_device_counters[state]+"</p></div>");
				}
			}
		}

		if(isCallCompleted == 1) {
			/*Hide The loading Icon*/
			$("#loadingIcon").hide();

			/*Enable the refresh button*/
			$("#resetFilters").button("complete");
			
			if(isFirstTime == 1) {
				/*Load data for basic filters*/
				gmap_self.getBasicFilters();
			}
		}
	};

	/**
	 * This function trigger when state label is clicked & loads the state wise data.
	 * @method state_label_clicked
	 * @param state_obj, It contains the name of state which is clicked.
	 */
	this.state_label_clicked = function(state_obj) {
		if(isExportDataActive == 0) {
			var clicked_state = state_obj ? state_obj.name : "",
				selected_state_devices = [];

			if(clicked_state) {
				//Zoom in to selected state
				mapInstance.fitBounds(new google.maps.LatLngBounds(new google.maps.LatLng(state_obj.lat,state_obj.lon)));
				mapInstance.setZoom(8);

				// Hide Clicked state Label
				if(!(state_wise_device_labels[clicked_state].isHidden_)) {
        			// Hide Label
					state_wise_device_labels[clicked_state].hide();
    			}
			}
		}
	};

	/**
	 * This function removes unmatched sectors from given data set as per applied filters(basic or advance).
	 * @method getFilteredBySectors
	 * @param dataset {Array}, It contains the bs-sector-ss hierarchy wise devices array.
	 */
	this.getFilteredBySectors = function(dataset) {

		var technology_filter = $("#filter_technology").select2('val').length > 0 ? $("#filter_technology").select2('val').join(',').split(',') : [],
			vendor_filter = $("#filter_vendor").select2('val').length > 0 ? $("#filter_vendor").select2('val').join(',').split(',') : [],
			frequency_filter = $("#filter_frequency").select2('val').length > 0 ? $("#filter_frequency").select2('val').join(',').split(',') : [],
			polarization_filter = $("#filter_polarization").select2('val').length > 0 ? $("#filter_polarization").select2('val').join(',').split(',') : [];

		// Remove unmatched sectors
		for(var x=dataset.length;x--;) {
			var sectors = dataset[x].data.param.sector,
				delete_index = [];
			for(var y=0;y<sectors.length;y++) {
				var sector_technology = $.trim(sectors[y].technology),
					sector_vendor = $.trim(sectors[y].vendor),
					sector_frequency = $.trim(sectors[y].planned_frequency),
					sector_polarization = sectors[y].orientation ? $.trim(sectors[y].orientation) : "";

				if(technology_filter.length > 0 || vendor_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0) {
					var advance_filter_condition1 = technology_filter.length ? technology_filter.indexOf(sector_technology) > -1 : true,
						advance_filter_condition2 = vendor_filter.length ? vendor_filter.indexOf(sector_vendor) > -1 : true,
						advance_filter_condition3 = frequency_filter.length ? frequency_filter.indexOf(sector_frequency) > -1 : true,
						advance_filter_condition4 = polarization_filter.length ? polarization_filter.indexOf(sector_polarization) > -1 : true;

					if(!advance_filter_condition1 || !advance_filter_condition2 || !advance_filter_condition3 || !advance_filter_condition4) {
						delete_index.push(y);
					} else {
						if($.trim($("#technology").val()) || $.trim($("#vendor").val())) {
							var basic_filter_technology = $.trim($("#technology").val()) ? $.trim($("#technology option:selected").text()) : false,
								basic_filter_vendor = $.trim($("#vendor").val()) ? $.trim($("#vendor option:selected").text()) : false,
								basic_filter_condition1 = basic_filter_technology ? basic_filter_technology === sector_technology : true,
								basic_filter_condition2 = basic_filter_vendor ? basic_filter_vendor === sector_vendor : true;
								
							if(!basic_filter_condition1 || !basic_filter_condition2) {
								delete_index.push(y);
							}
						}
					}

				} else {

					if($.trim($("#technology").val()) || $.trim($("#vendor").val())) {
						var basic_filter_technology = $.trim($("#technology").val()) ? $.trim($("#technology option:selected").text()) : false,
							basic_filter_vendor = $.trim($("#vendor").val()) ? $.trim($("#vendor option:selected").text()) : false,
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
				dataset[x].data.param.sector.splice(delete_index[z],1);
			}
		}

		// Return the updated dataset.
		return dataset;
	};

	/**
	 * This function get the filtered data from lokidb instance as per the applied filters(basic or advance).
	 * @method getFilteredData_gmap
	 */
	this.getFilteredData_gmap = function() {

		var technology_filter = $("#filter_technology").select2('val').length > 0 ? $("#filter_technology").select2('val').join(',').split(',') : [],
			vendor_filter = $("#filter_vendor").select2('val').length > 0 ? $("#filter_vendor").select2('val').join(',').split(',') : [],
			city_filter = $("#filter_city").select2('val').length > 0 ? $("#filter_city").select2('val').join(',').split(',') : [],
			state_filter = $("#filter_state").select2('val').length > 0 ? $("#filter_state").select2('val').join(',').split(',') : [],
			frequency_filter = $("#filter_frequency").select2('val').length > 0 ? $("#filter_frequency").select2('val').join(',').split(',') : [],
			polarization_filter = $("#filter_polarization").select2('val').length > 0 ? $("#filter_polarization").select2('val').join(',').split(',') : [],
			filterObj = {
				"technology" : $.trim($("#technology option:selected").text()),
				"vendor" : $.trim($("#vendor option:selected").text()),
				"state" : $.trim($("#state option:selected").text()),
				"city" : $.trim($("#city option:selected").text())
			},
			isAdvanceFilterApplied = technology_filter.length > 0 || vendor_filter.length > 0 || state_filter.length > 0 || city_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0,
			isBasicFilterApplied = filterObj['technology'] != 'Select Technology' || filterObj['vendor'] != 'Select Vendor' || filterObj['state'] != 'Select State' || filterObj['city'] != 'Select City';

		var filtered_Data = all_devices_loki_db.where(function(obj) {
			var sectors = obj.data.param.sector,
				basic_filter_condition1 = filterObj['state'] != 'Select State' ? obj.data.state == filterObj['state'] : true,
				basic_filter_condition2 = filterObj['city'] != 'Select City' ? obj.data.city == filterObj['city'] : true,
				advance_filter_condition1 = state_filter.length > 0 ? state_filter.indexOf(obj.data.state) > -1 : true,
				advance_filter_condition2 = city_filter.length > 0 ? city_filter.indexOf(obj.data.city) > -1 : true;

        	// If any basic filter is applied
        	if(isBasicFilterApplied) {

				for(var i=sectors.length;i--;) {

					var basic_filter_condition3 = $.trim($("#technology").val()) ? sectors[i].technology ===  filterObj['technology'] : true,
						basic_filter_condition4 = $.trim($("#vendor").val()) ? sectors[i].vendor ===  filterObj['vendor'] : true;

					if(basic_filter_condition1 && basic_filter_condition2 && basic_filter_condition3 && basic_filter_condition4) {
						// If advance Filters Applied
						if(isAdvanceFilterApplied) {
							var advance_filter_condition3 = technology_filter.length > 0 ? technology_filter.indexOf(sectors[i].technology) > -1 : true,
				                advance_filter_condition4 = vendor_filter.length > 0 ? vendor_filter.indexOf(sectors[i].vendor) > -1 : true,
				            	advance_filter_condition5 = frequency_filter.length > 0 ? frequency_filter.indexOf(sectors[i].planned_frequenc) > -1 : true,
				            	advance_filter_condition6 = polarization_filter.length > 0 ? polarization_filter.indexOf(sectors[i].orientation) > -1 : true;

				            if(advance_filter_condition1 && advance_filter_condition2 && advance_filter_condition3 && advance_filter_condition4 && advance_filter_condition5 && advance_filter_condition6) {
				                return true
				            } else {
				                return false;
				            }
						} else {
							return true;
						}
					} else {
						return false;
					}
				}


        	} else if(isAdvanceFilterApplied) {
        		
        		for(var i=0;i<sectors.length;i++) {

	        		var advance_filter_condition3 = technology_filter.length > 0 ? technology_filter.indexOf(sectors[i].technology) > -1 : true,
		                advance_filter_condition4 = vendor_filter.length > 0 ? vendor_filter.indexOf(sectors[i].vendor) > -1 : true,
		            	advance_filter_condition5 = frequency_filter.length > 0 ? frequency_filter.indexOf(sectors[i].planned_frequenc) > -1 : true,
		            	advance_filter_condition6 = polarization_filter.length > 0 ? polarization_filter.indexOf(sectors[i].orientation) > -1 : true;

		            if(advance_filter_condition1 && advance_filter_condition2 && advance_filter_condition3 && advance_filter_condition4 && advance_filter_condition5 && advance_filter_condition6) {
		                return true
		            } else {
		                return false;
		            }
	            }
        	} else {
        		return true;
        	}
    	});

		return filtered_Data;
	};

	/**
     * This function is used to get the devices which are in bound from given data set.
     * @method getInBoundDevices
     * @param dataset {Array}, It contains array of bs-sector-ss heirarchy devices.
     * @return inBoundDevices {Array}, It returns the devices which are in current bound.
	 */
	this.getInBoundDevices = function(dataset) {

		var inBoundDevices = [];

		for(var i=dataset.length;i--;) {

			var current_device_set = dataset[i],
				isDeviceInBound = mapInstance.getBounds().contains(new google.maps.LatLng(current_device_set.data.lat,current_device_set.data.lon));
			if(isDeviceInBound) {
				inBoundDevices.push(current_device_set);
				plottedBsIds.push(current_device_set.id);
			}
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

		var newInBoundDevices = [];

		for(var i=main_devices_data_gmaps.length;i--;) {
			var current_device_set = main_devices_data_gmaps[i];

			if(plottedBsIds.indexOf(current_device_set.id) === -1) {
				var isDeviceInBound = mapInstance.getBounds().contains(new google.maps.LatLng(current_device_set.data.lat,current_device_set.data.lon));
				if(isDeviceInBound) {
					newInBoundDevices.push(current_device_set);
					plottedBsIds.push(current_device_set.id);
				}

			}
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
	this.plotDevices_gmap = function(bs_ss_devices,stationType) {
		// for(var i=0;i<bs_ss_devices.length;i++) {
		for(var i=bs_ss_devices.length;i--;) {
			
			/*Create BS Marker Object*/
			var bs_marker_object = {
				position  	       : 	new google.maps.LatLng(bs_ss_devices[i].data.lat,bs_ss_devices[i].data.lon),
				ptLat 		       : 	bs_ss_devices[i].data.lat,
				ptLon 		       : 	bs_ss_devices[i].data.lon,
				// map       	       : 	mapInstance,
				icon 	  	       : 	new google.maps.MarkerImage(base_url+"/static/img/icons/bs.png",null,null,null,new google.maps.Size(20, 40)),
				oldIcon 	       : 	new google.maps.MarkerImage(base_url+"/static/img/icons/bs.png",null,null,null,new google.maps.Size(20, 40)),
				clusterIcon 	   : 	new google.maps.MarkerImage(base_url+"/static/img/icons/bs.png",null,null,null,new google.maps.Size(20, 40)),
				pointType	       : 	stationType,
				child_ss   	       : 	bs_ss_devices[i].data.param.sector,
				dataset 	       : 	bs_ss_devices[i].data.param.base_station,
				device_name 	   : 	bs_ss_devices[i].data.device_name,
				bsInfo 			   : 	bs_ss_devices[i].data.param.base_station,
				bhInfo 			   : 	bs_ss_devices[i].data.param.backhual,
				bs_name 		   : 	bs_ss_devices[i].name,
				name 		 	   : 	bs_ss_devices[i].name,
				filter_data 	   : 	{"bs_name" : bs_ss_devices[i].name, "bs_id" : bs_ss_devices[i].originalId},
				antenna_height     : 	bs_ss_devices[i].data.antenna_height,
				zIndex 			   : 	250,
				optimized 		   : 	false,
				markerType 		   : 	'BS',
				isMarkerSpiderfied : 	false,
				isActive 		   : 	1
			};

			/*Create BS Marker*/
			var bs_marker = new google.maps.Marker(bs_marker_object);

			/*Add BS Marker To Cluster*/
			masterClusterInstance.addMarker(bs_marker);

			/*Sectors Array*/
			var sector_array = bs_ss_devices[i].data.param.sector;
			var deviceIDArray= [];

			/*Plot Sector*/
			for(var j=sector_array.length;j--;) {

				var lat = bs_ss_devices[i].data.lat,
					lon = bs_ss_devices[i].data.lon,
					azimuth = sector_array[j].azimuth_angle,
					beam_width = sector_array[j].beam_width,
					sector_color = sector_array[j].color,
					sectorInfo = {
						"info" : sector_array[j].info,
						"bs_name" : bs_ss_devices[i].name,
						"sector_name" : sector_array[j].sector_configured_on,
						"sector_id" : sector_array[j].sector_id,
						"device_info" : sector_array[j].device_info,
						"technology" : sector_array[j].technology,
						"vendor" : sector_array[j].vendor
					},
					orientation = $.trim(sector_array[j].orientation),
					sector_child = sector_array[j].sub_station,
					rad = 4,
					sectorRadius = (+sector_array[j].radius),
					startLon = "",
					startLat = "";

				/*If radius is greater than 4 Kms then set it to 4.*/
				if(sectorRadius && (sectorRadius > 0)) {
					rad = sectorRadius;
				}

				var startEndObj = {};

				/*Call createSectorData function to get the points array to plot the sector on google maps.*/
				gmap_self.createSectorData(lat,lon,rad,azimuth,beam_width,orientation,function(pointsArray) {
				
					var halfPt = Math.floor(pointsArray.length / (+2));

					if($.trim(sector_array[j].technology) != "PTP" && $.trim(sector_array[j].technology) != "P2P") {
						/*Plot sector on map with the retrived points*/
						gmap_self.plotSector_gmap(lat,lon,pointsArray,sectorInfo,sector_color,sector_child,$.trim(sector_array[j].technology),orientation,rad,azimuth,beam_width);

						startEndObj["startLat"] = pointsArray[halfPt].lat;
						startEndObj["startLon"] = pointsArray[halfPt].lon;

						startEndObj["sectorLat"] = pointsArray[halfPt].lat;
						startEndObj["sectorLon"] = pointsArray[halfPt].lon;

					} else {

						startEndObj["startLat"] = bs_ss_devices[i].data.lat;
		    			startEndObj["startLon"] = bs_ss_devices[i].data.lon;
		    			
		    			startEndObj["sectorLat"] = bs_ss_devices[i].data.lat;
						startEndObj["sectorLon"] = bs_ss_devices[i].data.lon;
					}
				});

				if($.trim(sector_array[j].technology.toLowerCase()) == "ptp" || $.trim(sector_array[j].technology.toLowerCase()) == "p2p") {

					if(deviceIDArray.indexOf(sector_array[j]['device_info'][1]['value']) === -1) {

						var sectors_Markers_Obj = {
							position 		 	: new google.maps.LatLng(lat, lon),
							// map 				: mapInstance,
							ptLat 			 	: lat,
							ptLon 			 	: lon,
							icon 			 	: new google.maps.MarkerImage(base_url+'/static/img/icons/1x1.png',null,null,null,new google.maps.Size(1,1)),
							oldIcon 		 	: new google.maps.MarkerImage(base_url+"/"+sector_array[j].markerUrl,null,null,null,new google.maps.Size(32,37)),
							clusterIcon 	 	: new google.maps.MarkerImage(base_url+"/static/img/icons/1x1.png",null,null,null,new google.maps.Size(1,1)),
							pointType 		 	: 'sector_Marker',
							technology 		 	: sector_array[j].technology,
							vendor 				: sector_array[j].vendor,
							deviceExtraInfo 	: sector_array[j].info,
							deviceInfo 			: sector_array[j].device_info,
							poll_info 			: [],
							sectorName  		: sector_array[j].sector_configured_on,
							device_name  		: sector_array[j].sector_configured_on_device,
							name  				: sector_array[j].sector_configured_on_device,
							filter_data 	    : {"bs_name" : bs_ss_devices[i].name, "sector_name" : sector_array[j].sector_configured_on, "bs_id" : bs_ss_devices[i].originalId, "sector_id" : sector_array[j].sector_id},
							sector_lat  		: startEndObj["startLat"],
							sector_lon  		: startEndObj["startLon"],
							zIndex 				: 200,
							optimized 			: false,
							hasPerf  			: 0,
	                        antenna_height 		: sector_array[j].antenna_height,
	                        isActive 			: 1
	                    }
	                }

	                var sect_height = sector_array[j].antenna_height;

					/*Create Sector Marker*/
					var sector_Marker = new google.maps.Marker(sectors_Markers_Obj);

					if(sectorMarkerConfiguredOn.indexOf(sector_array[j].sector_configured_on) == -1) {
						sector_MarkersArray.push(sector_Marker);
						allMarkersArray_gmap.push(sector_Marker);

						/*Push Sector marker to pollableDevices array*/
						pollableDevices.push(sector_Marker);
						
						allMarkersObject_gmap['sector_device']['sector_'+sector_array[j].sector_configured_on] = sector_Marker;

						/*Add Sector Device To Cluster*/
						// masterClusterInstance.addMarker(sector_Marker);

						sectorMarkerConfiguredOn.push(sector_array[j].sector_configured_on);
						if(sectorMarkersMasterObj[bs_ss_devices[i].name]) {
							sectorMarkersMasterObj[bs_ss_devices[i].name].push(sector_Marker)
						} else {
							sectorMarkersMasterObj[bs_ss_devices[i].name]= [];
							sectorMarkersMasterObj[bs_ss_devices[i].name].push(sector_Marker)
						}	
					}

					/*End of Create Sector Marker*/
					
					deviceIDArray.push(sector_array[j]['device_info'][1]['value']);
				}

				/*Plot Sub-Station*/
				for(var k=sector_child.length;k--;) {

				
					var ss_marker_obj = sector_child[k];

					/*Create SS Marker Object*/
					var ss_marker_object = {
						position 		 : 	new google.maps.LatLng(ss_marker_obj.data.lat,ss_marker_obj.data.lon),
				    	ptLat 			 : 	ss_marker_obj.data.lat,
				    	ptLon 			 : 	ss_marker_obj.data.lon,
				    	technology 		 : 	ss_marker_obj.data.technology,
				    	// map 			 : 	mapInstance,
				    	icon 			 : 	new google.maps.MarkerImage(base_url+"/"+ss_marker_obj.data.markerUrl,null,null,null,new google.maps.Size(32,37)),
				    	oldIcon 		 : 	new google.maps.MarkerImage(base_url+"/"+ss_marker_obj.data.markerUrl,null,null,null,new google.maps.Size(32,37)),
				    	clusterIcon 	 : 	new google.maps.MarkerImage(base_url+"/"+ss_marker_obj.data.markerUrl,null,null,null,new google.maps.Size(32,37)),
				    	pointType	     : 	"sub_station",
				    	dataset 	     : 	ss_marker_obj.data.param.sub_station,
				    	bhInfo 			 : 	[],
				    	poll_info 		 :  [],
				    	antenna_height   : 	ss_marker_obj.data.antenna_height,
				    	name 		 	 : 	ss_marker_obj.name,
				    	bs_name 		 :  bs_ss_devices[i].name,
				    	bs_sector_device :  sector_array[j].sector_configured_on_device,
				    	filter_data 	 :  {"bs_name" : bs_ss_devices[i].name, "sector_name" : sector_array[j].sector_configured_on, "ss_name" : ss_marker_obj.name, "bs_id" : bs_ss_devices[i].originalId, "sector_id" : sector_array[j].sector_id},
				    	device_name 	 : 	ss_marker_obj.device_name,
				    	ss_ip 	 		 : 	ss_marker_obj.data.substation_device_ip_address,
				    	sector_ip 		 :  sector_array[j].sector_configured_on,
				    	zIndex 			 : 	200,
				    	hasPerf 		 :  0,
				    	optimized 		 : 	false,
				    	isActive 		 : 1
				    };

				    /*Create SS Marker*/
				    var ss_marker = new google.maps.Marker(ss_marker_object);

				    /*Add BS Marker To Cluster*/
					masterClusterInstance.addMarker(ss_marker);

				    markersMasterObj['SS'][String(ss_marker_obj.data.lat)+ ss_marker_obj.data.lon]= ss_marker;
				    markersMasterObj['SSNamae'][String(ss_marker_obj.device_name)]= ss_marker;

				    /*Add the master marker to the global master markers array*/
			    	masterMarkersObj.push(ss_marker);

			    	allMarkersObject_gmap['sub_station']['ss_'+ss_marker_obj.name] = ss_marker;

			    	allMarkersArray_gmap.push(ss_marker);

			    	/*Add parent markers to the OverlappingMarkerSpiderfier*/
				    oms_ss.addMarker(ss_marker);

				    /*Push SS marker to pollableDevices array*/
					pollableDevices.push(ss_marker)

				    /*Push All SS Lat & Lon*/
		    	    ssLatArray.push(ss_marker_obj.data.lat);
					ssLonArray.push(ss_marker_obj.data.lon);

					var ss_info = {
							"info" : ss_marker_obj.data.param.sub_station,
							"antenna_height" : ss_marker_obj.data.antenna_height
						},
						base_info = {
							"info" : bs_ss_devices[i].data.param.base_station,
							"antenna_height" : bs_ss_devices[i].data.antenna_height
						};

					startEndObj["nearEndLat"] = bs_ss_devices[i].data.lat;
					startEndObj["nearEndLon"] = bs_ss_devices[i].data.lon;

				    startEndObj["endLat"] = ss_marker_obj.data.lat;
		    		startEndObj["endLon"] = ss_marker_obj.data.lon;

		    		/*Sub station info Object*/
		    		// ss_info["info"] = ss_marker_obj.data.param.sub_station;
		    		// ss_info["antenna_height"] = ss_marker_obj.data.antenna_height;

		    		/*Link color object*/
		    		linkColor = ss_marker_obj.data.link_color;
		    			
	    			// base_info["info"] = bs_ss_devices[i].data.param.base_station;
	    			// base_info["antenna_height"] = bs_ss_devices[i].data.antenna_height;
	    			
	    			if(ss_marker_obj.data.show_link == 1) {
	    				/*Create the link between BS & SS or Sector & SS*/
				    	var ss_link_line = gmap_self.createLink_gmaps(startEndObj,linkColor,base_info,ss_info,sect_height,sector_array[j].sector_configured_on,ss_marker_obj.name,bs_ss_devices[i].name,bs_ss_devices[i].id,sector_array[j].sector_id);
				    	ssLinkArray.push(ss_link_line);
				    	ssLinkArray_filtered = ssLinkArray;

				    	allMarkersObject_gmap['path']['line_'+ss_marker_obj.name] = ss_link_line;

				    	allMarkersArray_gmap.push(ss_link_line);
	    			}

				}
    		}

    		/*Add the master marker to the global master markers array*/
	    	masterMarkersObj.push(bs_marker);

	    	allMarkersObject_gmap['base_station']['bs_'+bs_ss_devices[i].name] = bs_marker;

	    	allMarkersArray_gmap.push(bs_marker);

	    	//Add markers to markersMasterObj with LatLong at key so it can be fetched later.
			markersMasterObj['BS'][String(bs_ss_devices[i].data.lat)+bs_ss_devices[i].data.lon]= bs_marker;
			markersMasterObj['BSNamae'][String(bs_ss_devices[i].name)]= bs_marker;

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


			var oms_bs_markers = oms.getMarkers(),
				oms_ss_markers = oms_ss.getMarkers();			

			/*Loop to change the icon for same location BS markers(to cluster icon)*/
			for(var k=oms_bs_markers.length;k--;) {
				
				if(oms_bs_markers[k] != undefined) {
	
					/*if two BS or SS on same position*/
					var bsLatOccurence = $.grep(bsLatArray, function (elem) {return elem === oms_bs_markers[k].ptLat;}).length;
					var bsLonOccurence = $.grep(bsLonArray, function (elem) {return elem === oms_bs_markers[k].ptLon;}).length;

					if(bsLatOccurence > 1 && bsLonOccurence > 1) {
						oms_bs_markers[k].setOptions({"icon" : base_url+"/static/img/icons/bs.png"});
					}
				}
			}

			/*Loop to change the icon for same location SS markers(to cluster icon)*/
//			for(var k=0;k<oms_ss_markers.length;k++) {
//
//				if(oms_ss_markers[k] != undefined) {
//
//					/*if two BS or SS on same position*/
//					var bsLatOccurence = $.grep(ssLatArray, function (elem) {return elem === oms_ss_markers[k].ptLat;}).length;
//					var bsLonOccurence = $.grep(ssLonArray, function (elem) {return elem === oms_ss_markers[k].ptLon;}).length;
//
//					if(bsLatOccurence > 1 && bsLonOccurence > 1) {
//						oms_ss_markers[k].setOptions({"icon" : new google.maps.MarkerImage(base_url+'/static/img/icons/1x1.png',null,null,null,new google.maps.Size(1,1))});
//					}
//				}
//			}
			
			if(isFirstTime == 1) {
				/*Load data for basic filters*/
				gmap_self.getBasicFilters();
			}

			gmap_self.updateAllMarkersWithNewIcon(defaultIconSize);
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
			sector_lat 		: startEndObj.sectorLat,
			sector_lon 		: startEndObj.sectorLon,
			filter_data 	: {"bs_name" : bs_name, "sector_name" : sector_name, "ss_name" : ss_name, "bs_id" : bs_id, "sector_id" : sector_id},
			nearLat 		: startEndObj.nearEndLat,
			nearLon 		: startEndObj.nearEndLon,
			sectorName 	    : sector_name,
			ssName 		    : ss_name,
			bsName 			: bs_name,
			zIndex 			: 9999
		};

		var pathConnector = new google.maps.Polyline(linkObject);

		/*Plot the link line between master & slave*/
		// pathConnector.setMap(mapInstance);

		/*Bind Click Event on Link Path Between Master & Slave*/
		google.maps.event.addListener(pathConnector, 'click', function(e) {
			/*Call the function to create info window content*/
			var content = gmap_self.makeWindowContent(this);
			$("#infoWindowContainer").html(content);
			$("#infoWindowContainer").removeClass('hide');
			/*Set the content for infowindow*/
			// infowindow.setContent(content);
			/*Set The Position for InfoWindow*/
			// infowindow.setPosition(e.latLng);
			/*Open the  info window*/
			// infowindow.open(mapInstance);

			/*Show only 5 rows, hide others*/
			// gmap_self.show_hide_info();
		});

		markersMasterObj['Lines'][String(startEndObj.startLat)+ startEndObj.startLon+ startEndObj.endLat+ startEndObj.endLon]= pathConnector;
		markersMasterObj['LinesName'][String(bs_name)+ ss_name]= pathConnector;
		

		/*returns gmap polyline object */
		return pathConnector;
	};

	/**
	 * This function show connection lines within the bounds
	 * @method showLinesInBounds
	 */
	this.showLinesInBounds = function() {
		/*Loop for polylines*/
		for(var key in allMarkersObject_gmap['path']) {
			if(allMarkersObject_gmap['path'].hasOwnProperty(key)) {
		    	var current_line = allMarkersObject_gmap['path'][key];
		    	if(current_line) {
				    var nearEndVisible = mapInstance.getBounds().contains(new google.maps.LatLng(current_line.nearLat,current_line.nearLon)),
				      	farEndVisible = mapInstance.getBounds().contains(new google.maps.LatLng(current_line.ss_lat,current_line.ss_lon)),
				      	connected_bs = allMarkersObject_gmap['base_station']['bs_'+current_line.filter_data.bs_name],
				      	connected_ss = allMarkersObject_gmap['sub_station']['ss_'+current_line.filter_data.ss_name];

				    if((nearEndVisible || farEndVisible) && ((connected_bs && connected_ss) && (connected_bs.isActive != 0 && connected_ss.isActive != 0))) {
				    	// If polyline not shown then show the polyline
				    	if(!current_line.map) {
				    		current_line.setMap(mapInstance);
				    	}
				    } else {
				    	// If polyline shown then hide the polyline
				    	if(current_line.map) {
				    		current_line.setMap(null);
			    		}
				    }
		    	}
		    }
		}
	};

	/**
	 * This function show sub-stations within the bounds
	 * @method showSubStaionsInBounds
	 */
	this.showSubStaionsInBounds = function() {
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
			    	} else {
			    		// If SS Marker shown then hide the SS Marker
			    		if(allMarkersObject_gmap['sub_station'][key].map) {
			      			allMarkersObject_gmap['sub_station'][key].setMap(null);
		    			}
			    	}
	    		}
		    }
		}
	};

	/**
	 * This function show base-stations within the bounds
	 * @method showBaseStaionsInBounds
	 */
	this.showBaseStaionsInBounds = function() {
		/*Loop for polylines*/
		for(var key in allMarkersObject_gmap['base_station']) {
			if(allMarkersObject_gmap['base_station'].hasOwnProperty(key)) {
		    	var bs_marker = allMarkersObject_gmap['base_station'][key],
		      		isMarkerExist = mapInstance.getBounds().contains(bs_marker.getPosition());
	      		if(isMarkerExist) {
			    	if(bs_marker.isActive && +(bs_marker.isActive) === 1) {
			    		// If BS Marker not shown then show the BS Marker
			    		if(!allMarkersObject_gmap['base_station'][key].map) {
			      			allMarkersObject_gmap['base_station'][key].setMap(mapInstance);
			    		}
			        } else {
			        	// If BS Marker shown then hide the BS Marker
			        	if(allMarkersObject_gmap['base_station'][key].map) {
			      			allMarkersObject_gmap['base_station'][key].setMap(null);
		        		}
			        }
	      		}
		    }
		}
	};

	/**
	 * This function show base-stations devices(sector devices) within the bounds
	 * @method showSectorDevicesInBounds
	 */
	this.showSectorDevicesInBounds = function() {
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
	};

	/**
	 * This function show polygon(sector) within the bounds
	 * @method showSectorPolygonInBounds
	 */
	this.showSectorPolygonInBounds = function() {
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
	};

	/**
	 * This function show/hide the connection line between BS & SS.
	 * @method showConnectionLines_gmap
	 */
	this.showConnectionLines_gmap = function() {

		var isLineChecked = $("#showConnLines:checked").length;

		var current_lines = ssLinkArray_filtered;

		/*Unchecked case*/
		if(isLineChecked == 0) {

			for (var i = 0; i < ssLinkArray.length; i++) {
				ssLinkArray[i].setMap(null);
			}

		} else {
			for (var i = 0; i < current_lines.length; i++) {
				current_lines[i].setMap(mapInstance);
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
	 * @param technology {String}, It contains the technology of sector device.
	 * @param polarisation {String}, It contains the polarisation(horizontal or vertical) of sector device.
	 */
	this.plotSector_gmap = function(lat,lon,pointsArray,sectorInfo,bgColor,sector_child,technology,polarisation,rad,azimuth,beam_width) {
		var polyPathArray = [];
		
		var halfPt = Math.floor(pointsArray.length / (+2));
		
		var startLat = pointsArray[halfPt].lat;
		var startLon = pointsArray[halfPt].lon;

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

		var poly = new google.maps.Polygon({
			path 		     : polyPathArray,
			ptLat 		     : lat,
			ptLon 		     : lon,
			strokeColor      : sColor,
			fillColor 	     : bgColor,
			pointType	     : "sector",
			strokeOpacity    : 1,
			fillOpacity 	 : 0.5,
			strokeWeight     : sWidth,
			poll_info 		 : [],
			radius 			 : rad,
			azimuth 		 : azimuth,
			beam_width 		 : beam_width,
			technology 		 : sectorInfo.technology,
			vendor 			 : sectorInfo.vendor,
			deviceExtraInfo  : sectorInfo.info,
			deviceInfo 		 : sectorInfo.device_info,
			startLat 	     : startLat,
			startLon 	     : startLon,
			filter_data 	 : {"bs_name" : sectorInfo.bs_name, "sector_name" : sectorInfo.sector_name},
			bhInfo 			 : [],
			child_ss 	     : sector_child,
			polarisation 	 : polarisation,
			original_sectors : sector_child,
			zIndex 			 : 180,
			geodesic		 : true,
			isActive 		 : 1
        });
        // poly.setMap(mapInstance);
        allMarkersArray_gmap.push(poly);

        allMarkersObject_gmap['sector_polygon']['poly_'+sectorInfo.sector_name+"_"+sectorInfo.sector_id] = poly;

		if(sector_child) {
			for(var i=sector_child.length;i--;) {
				markersMasterObj['Poly'][sector_child[i]["device_name"]]= poly;
			}			
		}
        

        /*listener for click event of sector*/
		google.maps.event.addListener(poly,'click',function(e) {

			/*Call the function to create info window content*/
			var content = gmap_self.makeWindowContent(poly);
			$("#infoWindowContainer").html(content);
			$("#infoWindowContainer").removeClass('hide');
			/*Set the content for infowindow*/
			// infowindow.setContent(content);
			/*Set The Position for InfoWindow*/
			// infowindow.setPosition(e.latLng);
			/*Open the info window*/
			// infowindow.open(mapInstance);
			/*Show only 5 rows, hide others*/
			// gmap_self.show_hide_info();
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
			var path_circuit_id = "";
			/*Tabbale Start*/
			infoTable += '<div class="tabbable">';
			/*Tabs Creation Start*/
			infoTable += '<ul class="nav nav-tabs">';
			infoTable += '<li class="active"><a href="#near_end_block" data-toggle="tab"><i class="fa fa-arrow-circle-o-right"></i> BS-Sector Info</a></li>';
			infoTable += '<li class=""><a href="#far_end_block" data-toggle="tab"><i class="fa fa-arrow-circle-o-right"></i> SS Info</a></li>';
			infoTable += '</ul>';
			/*Tabs Creation Ends*/

			/*Tab-content Start*/
			infoTable += '<div class="tab-content">';

			/*First Tab Content Start*/
			infoTable += '<div class="tab-pane fade active in" id="near_end_block"><div class="divide-10"></div>';

			infoTable += "<table class='table table-bordered'><tbody>";
			
			/*Loop for BS or Sector info object array*/
			for(var i=0;i<contentObject.bs_info.length;i++) {

				if(contentObject.bs_info[i].show == 1) {
					infoTable += "<tr><td>"+contentObject.bs_info[i].title+"</td><td>"+contentObject.bs_info[i].value+"</td></tr>";
				}
			}

			infoTable += "<tr><td>Lat, Long</td><td>"+contentObject.nearLat+", "+contentObject.nearLon+"</td></tr>";
			infoTable += "</tbody></table>";			
			infoTable += "</td>";
			/*BS-Sector Info End*/

			infoTable += '</div>';
			/*First Tab Content End*/

			/*Second Tab Content Start*/
			infoTable += '<div class="tab-pane fade" id="far_end_block"><div class="divide-10"></div>';
			/*SS Info Start*/
			infoTable += "<td>";			
			infoTable += "<table class='table table-bordered'><tbody>";
			
			/*Loop for ss info object array*/
			for(var i=0;i<contentObject.ss_info.length;i++) {
				if(contentObject.ss_info[i].title && $.trim(contentObject.ss_info[i].title.toLowerCase()) === 'circuit id') {
					path_circuit_id = contentObject.ss_info[i].value;
				}

				if(contentObject.ss_info[i].show == 1) {
					infoTable += "<tr><td>"+contentObject.ss_info[i].title+"</td><td>"+contentObject.ss_info[i].value+"</td></tr>";
				}
			}

			var link1 = "http://10.209.19.190:10080/ISCWebServiceUI/JSP/types/ISCType.faces?serviceId",
				link2 = "http://10.209.19.190:10080/ExternalLinksWSUI/JSP/ProvisioningDetails.faces?serviceId";

			infoTable += "<tr><td>Lat, Long</td><td>"+contentObject.ss_lat+", "+contentObject.ss_lon+"</td></tr>";
			if(path_circuit_id) {
				infoTable += "<tr><td>POSLink1</td><td><a href='"+link1+"="+path_circuit_id+"' class='text-warning' target='_blank'>"+path_circuit_id+"</a></td></tr>";
				infoTable += "<tr><td>POSLink2</td><td><a href='"+link2+"="+path_circuit_id+"' class='text-warning' target='_blank'>"+path_circuit_id+"</a></td></tr>";
			}
			infoTable += "</tbody></table>";
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

			var sector_ss_name_obj = {
				sector_Alias: contentObject.bs_info ? contentObject.bs_info[0].value : " ",
				sector_name : contentObject.sectorName ? contentObject.sectorName : " ",
				ss_name : contentObject.ssName ? contentObject.ssName : " ",
				ss_customerName: contentObject.ss_info.length >= 18 ? contentObject.ss_info[17].value : " ",
				ss_circuitId: contentObject.ss_info.length >= 4 ? contentObject.ss_info[3].value : " ",
				isBSLeft : isBSLeft
			};

			var sector_ss_name = JSON.stringify(sector_ss_name_obj);

			if(+(contentObject.nearLon) < +(contentObject.ss_lon)) {
				/*Concat infowindow content*/
				windowContent += "<div class='windowContainer' style='z-index: 300; position:relative;'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i> BS-SS</h4><div class='tools'><a style='cursor:pointer;' class='close_info_window'><i class='fa fa-times'></i></a></div></div><div class='box-body'>"+infoTable+"<div class='clearfix'></div><ul class='list-unstyled list-inline'><li><button class='btn btn-sm btn-info' onClick='gmap_self.claculateFresnelZone("+contentObject.nearLat+","+contentObject.nearLon+","+contentObject.ss_lat+","+contentObject.ss_lon+","+contentObject.bs_height+","+contentObject.ss_height+","+sector_ss_name+");'>Fresnel Zone</button></li></ul></div></div></div>";
			} else {
				/*Concat infowindow content*/
				windowContent += "<div class='windowContainer' style='z-index: 300; position:relative;'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i> BS-SS</h4><div class='tools'><a style='cursor:pointer;' class='close_info_window'><i class='fa fa-times'></i></a></div></div><div class='box-body'>"+infoTable+"<div class='clearfix'></div><ul class='list-unstyled list-inline'><li><button class='btn btn-sm btn-info' onClick='gmap_self.claculateFresnelZone("+contentObject.ss_lat+","+contentObject.ss_lon+","+contentObject.nearLat+","+contentObject.nearLon+","+contentObject.ss_height+","+contentObject.bs_height+","+sector_ss_name+");'>Fresnel Zone</button></li></ul></div></div></div>";
			}

		} else if (clickedType == 'sector_Marker' || clickedType == 'sector') {

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

			if(contentObject['poll_info']) {
				/*Poll Parameter Info*/
				for(var i=0; i< contentObject['poll_info'].length; i++) {
					if(contentObject['poll_info'][i].show) {
						infoTable += "<tr><td>"+contentObject['poll_info'][i]['title']+"</td><td>"+contentObject['poll_info'][i]['value']+"</td></tr>";
					}
				}
			}

			infoTable += "</tbody></table>";

			/*Final infowindow content string*/
			windowContent += "<div class='windowContainer' style='z-index: 300; position:relative;'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>Base Station Device</h4><div class='tools'><a style='cursor:pointer;' class='close_info_window'><i class='fa fa-times'></i></a></div></div><div class='box-body'><div class='' align='center'>"+infoTable+"</div><div class='clearfix'></div><div class='pull-right'></div><div class='clearfix'></div></div></div></div>";
		} else {

			infoTable += "<table class='table table-bordered'><tbody>";
			var startPtInfo = [],
				ss_circuit_id = "";

			if(contentObject.bsInfo != undefined) {
				startPtInfo = contentObject.bsInfo;
			} else {
				startPtInfo = contentObject.dataset;
			}

			for(var i=0;i<startPtInfo.length;i++) {
				if(startPtInfo[i].title && $.trim(startPtInfo[i].title.toLowerCase()) === 'circuit id') {
					ss_circuit_id = startPtInfo[i].value;
				}
				if(startPtInfo[i].show == 1) {
					infoTable += "<tr><td>"+startPtInfo[i].title+"</td><td>"+startPtInfo[i].value+"</td></tr>";
				}
			}

			if(contentObject['poll_info']) {
				/*Poll Parameter Info*/
				for(var i=0; i< contentObject['poll_info'].length; i++) {
					if(contentObject['poll_info'][i].show) {
						infoTable += "<tr><td>"+contentObject['poll_info'][i]['title']+"</td><td>"+contentObject['poll_info'][i]['value']+"</td></tr>";
					}
				}
			}

			/*Set the lat lon of the point*/
			infoTable += "<tr><td>Lat, Long</td><td>"+contentObject.ptLat+", "+contentObject.ptLon+"</td></tr>";

			var link1 = "http://10.209.19.190:10080/ISCWebServiceUI/JSP/types/ISCType.faces?serviceId",
				link2 = "http://10.209.19.190:10080/ExternalLinksWSUI/JSP/ProvisioningDetails.faces?serviceId";

			// infoTable += "<tr><td>Lat, Long</td><td>"+contentObject.ss_lat+", "+contentObject.ss_lon+"</td></tr>";
			
			if(clickedType == "sub_station") {
				if(ss_circuit_id) {
					infoTable += "<tr><td>POSLink1</td><td><a href='"+link1+"="+ss_circuit_id+"' class='text-warning' target='_blank'>"+ss_circuit_id+"</a></td></tr>";
					infoTable += "<tr><td>POSLink2</td><td><a href='"+link2+"="+ss_circuit_id+"' class='text-warning' target='_blank'>"+ss_circuit_id+"</a></td></tr>";
				}
			}

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
			windowContent += "<div class='windowContainer' style='z-index: 300; position:relative;'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>  "+contentObject.pointType.toUpperCase()+"</h4><div class='tools'><a style='cursor:pointer;' class='close_info_window'><i class='fa fa-times'></i></a></div></div><div class='box-body'><div class='' align='center'>"+infoTable+"</div><div class='clearfix'></div><div class='pull-right'></div><div class='clearfix'></div></div></div></div>";
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
			
			var left_str = '<div class="col-md-12"><b>BS</b><br/>'+fresnelData.bts1_alias+"<br />"+bts1_name+'<br /> (Height)</div>',
				right_str = '<div class="col-md-12"><b>SS</b><br/>'+fresnelData.bts2_customerName+"<br />"+fresnelData.bts2_circuitId+ "<br />"+ bts2_name+' (Height)</div>';
			
			if(fresnel_isBSLeft == 0) {
				left_str = '<div class="col-md-12"><b>SS</b><br/>'+fresnelData.bts2_customerName+"<br />"+fresnelData.bts2_circuitId+ "<br />"+ bts2_name+' (Height)</div>';
				right_str = '<div class="col-md-12"><b>BS</b><br/>'+fresnelData.bts1_alias+"<br />"+bts1_name+'<br /> (Height)</div>';
			}

			/*Fresnel template String*/
			var leftSlider = '<div class="col-md-2" align="center"><div class="col-md-8 col-md-offset-2"><input type="text" id="antinaVal1" class="form-control" value="'+antenaHight1+'"></div><div class="clearfix"></div><div id="antina_height1" style="height:300px;" class="slider slider-blue"></div>'+left_str+'</div>';
			var chart_detail = '<div id="chart-details"><div><span id="longitude-lbl" class="chart-detail-lbl">Longitude </span> <span id="longitude"></span></div><div><span id="latitude-lbl" class="chart-detail-lbl">Latitude </span> <span id="latitude"></span></div><div><span id="distance-lbl" class="chart-detail-lbl">Distance </span> <span id="distance"></span></div><div><span id="altitude-lbl" class="chart-detail-lbl">Altitude </span> <span id="altitude"></span></div><div><span id="obstacle-lbl" class="chart-detail-lbl">Obstacle </span> <span id="obstacle"></span></div><div><span id="los-lbl" class="chart-detail-lbl">LOS </span> <span id="los"></span></div><div><span id="fresnel1-lbl" class="chart-detail-lbl">Fresnel-1 </span> <span id="fresnel1"></span></div><div><span id="fresnel2-lbl" class="chart-detail-lbl">Fresnel-2 </span> <span id="fresnel2"></span></div><div><span id="fresnel2-altitude-lbl" class="chart-detail-lbl">Clearance </span> <span id="fresnel-altitude"></span></div></div>';
			var middleBlock = '<div class="col-md-8 mid_fresnel_container"><div align="center"><div class="col-md-12">Clearance Factor</div><div class="col-md-4 col-md-offset-3"><div id="clear-factor" class="slider slider-red"></div></div><div class="col-md-2"><input type="text" id="clear-factor_val" class="form-control" value="'+clear_factor+'"></div><div class="clearfix"></div></div><div id="chart_div" style="width:600px;max-width:100%;height:300px;"></div><div class="clearfix divide-10"></div><div id="pin-points-container" class="col-md-12" align="center"></div></div>';
			var rightSlider = '<div class="col-md-2" align="center"><div class="col-md-8 col-md-offset-2"><input type="text" id="antinaVal2" class="form-control" value="'+antenaHight2+'"></div><div class="clearfix"></div><div id="antina_height2" class="slider slider-blue" style="height:300px;"></div>'+right_str+'</div>';

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
				{ data: dataFresnel1, label: "Fresnel-1 U"},
				{ data: dataFresnel2, label: "Fresnel-2 L"}
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
			"ss_circuitId" : fresnelData.bts2_circuitId,
			"isBSLeft" : fresnel_isBSLeft
		};

		gmap_self.claculateFresnelZone(fresnelLat1,fresnelLon1,fresnelLat2,fresnelLon2,antenaHight1,antenaHight2,sector_ss_obj);
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
			url : base_url+"/"+"device/filter/",
			success : function(result) {
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
				console.log(err.statusText);
			}
		});

		// Load Advance Search.
		gmap_self.loadAdvanceSearch();

		// Load Advance Filter
		gmap_self.loadAdvanceFilters();

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
		setTimeout(function() {
			var current_zoom_level = mapInstance.getZoom();
			if(current_zoom_level > 7) {
	    		var bs_list = getMarkerInCurrentBound();
	        	if(bs_list.length > 0 && isCallCompleted == 1) {
	        		gisPerformanceClass.start(bs_list);
	        	}
        	}
    	},500);
	}

	/**
	 * This function filters bs-ss object as per the applied filters
	 * @method applyFilter_gmaps
	 * @param filtersArray [JSON Array] It is an object array of filters with keys
	 * @param page_type {String} It is the type of opened page i.e. gmap or earth
	 */
	this.applyFilter_gmaps = function(filtersArray,page_type) {

		var current_data = [],
			filteredData = [],
			filteredBsArray = [],
			filteredSectorArray = [];

		if(page_type && page_type == 'googleEarth') {
			current_data = main_devices_data_earth;
		} else if (page_type && page_type == 'white_background') {
			current_data = main_devices_data_wmap;
		} else {
			current_data = main_devices_data_gmaps
		}


        for(var i=current_data.length;i--;) {

            /*Deep Copy of the current_data*/
            var bs_data= $.extend( true, {}, current_data[i]);

            bs_data.data.param.sector=[];
            /*Sectors Array*/
            for(var j=0;j< current_data[i].data.param.sector.length;j++) {
                
                var sector = current_data[i].data.param.sector[j],
                	current_tech = sector.technology ? sector.technology : '',
                	current_vendor = sector.vendor ? sector.vendor : '',
                	current_city = current_data[i].data.city ? current_data[i].data.city : '',
                	current_state = current_data[i].data.state ? current_data[i].data.state : '';

                if ((filtersArray['technology'] ? $.trim(filtersArray['technology'].toLowerCase()) == $.trim(current_tech.toLowerCase()) : true) &&
                    (filtersArray['vendor'] ? $.trim(filtersArray['vendor'].toLowerCase()) == $.trim(current_vendor.toLowerCase()) : true) &&
                    (filtersArray['city'] ? $.trim(filtersArray['city'].toLowerCase()) == $.trim(current_city.toLowerCase()) : true) &&
                    (filtersArray['state'] ? $.trim(filtersArray['state'].toLowerCase()) == $.trim(current_state.toLowerCase()) : true))
                {
                	bs_data.data.param.sector.push(sector);
                	
                	/*Add Filtered sector name to array*/
                	filteredSectorArray.push(sector.sector_configured_on);
                }
            }

            if ( bs_data.data.param.sector.length >0){
                filteredData.push(bs_data);
                /*Add Filtered BS name to array*/
                filteredBsArray.push(current_data[i].name);
            }

        }

        /*Check that after applying filters any data exist or not*/
        if(filteredData.length === 0) {

        	$.gritter.add({
        		// (string | mandatory) the heading of the notification
                title: 'GIS : Filters',
                // (string | mandatory) the text inside the notification
                text: 'No data available for applied filters.',
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false
            });

        	if(page_type && page_type == 'googleEarth') {
        		earth_instance.clearEarthElements();
        	} else if (page_type && page_type == 'white_background') {
        		data_for_filter_wmap = [];
        		whiteMapClass.hideAllFeatures();
        	} else {
        		data_for_filters = [];
        		// masterMarkersObj = [];
        		gmap_self.hide_all_elements_gmap();
        		/*Filter Line & label array as per filtered data*/
        		gmap_self.getFilteredLineLabel(data_for_filters);
        	}

        } else {
        	if(page_type && page_type == 'googleEarth') {

	            data_for_filters_earth = filteredData;

            	isCallCompleted = 1;

            	earth_instance.clearEarthElements();
            	/*Populate the map with the filtered markers*/
	            earth_instance.plotDevices_earth(filteredData,"base_station");

	        } else if (page_type && page_type == 'white_background') {

	        	data_for_filter_wmap = filteredData;

	        	whiteMapClass.hideAllFeatures();

	        	showWmapFilteredData(filteredData);
            } else {
					
				data_for_filters = filteredData;

            	gmap_self.showHideMarkers_gmap(data_for_filters);

            	/*Filter Line & label array as per filtered data*/
	            gmap_self.getFilteredLineLabel(data_for_filters);
            }
            /*Resetting filter data to Empty.*/
            filteredData=[]
        }
	};

	/**
	 * This function performs advance search as per given params on devices data
	 * @method applyAdvanceFilters
	 */
	this.applyAdvanceFilters = function() {

		var technology_filter = $("#filter_technology").select2('val').length > 0 ? $("#filter_technology").select2('val').join(',').split(',') : [],
			vendor_filter = $("#filter_vendor").select2('val').length > 0 ? $("#filter_vendor").select2('val').join(',').split(',') : [],
			city_filter = $("#filter_city").select2('val').length > 0 ? $("#filter_city").select2('val').join(',').split(',') : [],
			state_filter = $("#filter_state").select2('val').length > 0 ? $("#filter_state").select2('val').join(',').split(',') : [],
			frequency_filter = $("#filter_frequency").select2('val').length > 0 ? $("#filter_frequency").select2('val').join(',').split(',') : [],
			polarization_filter = $("#filter_polarization").select2('val').length > 0 ? $("#filter_polarization").select2('val').join(',').split(',') : [],
			filterObj = {
				"technology" : $.trim($("#technology option:selected").text()),
				"vendor" : $.trim($("#vendor option:selected").text()),
				"state" : $.trim($("#state option:selected").text()),
				"city" : $.trim($("#city option:selected").text())
			},
			isAdvanceFilterApplied = technology_filter.length > 0 || vendor_filter.length > 0 || state_filter.length > 0 || city_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0,
			isBasicFilterApplied = filterObj['technology'] != 'Select Technology' || filterObj['vendor'] != 'Select Vendor' || filterObj['state'] != 'Select State' || filterObj['city'] != 'Select City';

		var data_to_plot = [],
			filtered_data = [],
			advance_filter_condition = technology_filter.length > 0 || vendor_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0,
			basic_filter_condition = $.trim($("#technology").val()) || $.trim($("#vendor").val());

		if(isAdvanceFilterApplied || isBasicFilterApplied) {
        	filtered_data = gmap_self.getFilteredData_gmap();
    	} else {
    		filtered_data = all_devices_loki_db.data;
    	}

		if(advance_filter_condition || basic_filter_condition) {
        	data_to_plot = gmap_self.getFilteredBySectors(filtered_data);
    	} else {
    		data_to_plot = filtered_data;
    	}

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

        if(data_to_plot.length > 0) {
            /*Clear Existing Labels & Reset Counters*/
            gmap_self.clearStateCounters();
            mapInstance.fitBounds(new google.maps.LatLngBounds(new google.maps.LatLng(21.1500,79.0900)));
            mapInstance.setZoom(5);
            data_for_filters = data_to_plot;
            isApiResponse = 0;
            gmap_self.showStateWiseData_gmap(data_to_plot);

        } else {
            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: 'GIS : Advance Filters',
                // (string | mandatory) the text inside the notification
                text: 'No data available for applied filters.',
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false
            });
        }
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
        			var technologies = obj.sector_ss_technology.toLowerCase();
        			if(technologies.search(query.term.toLowerCase()) > -1) {
	        			return true;
        			} else {
        				return false;
        			}
        		});

		        var data = {results: []}, i, j, s;
		        var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < limit; i++) {
		        	var technology_list = filtered_data[i].sector_ss_technology.split("|");
        			for(var j=0;j<technology_list.length;j++) {
        				if(searchPattern.test(technology_list[j])) {
				        	if(bs_technology_array.indexOf(technology_list[j]) < 0) {
				        		bs_technology_array.push(technology_list[j]);
				            	data.results.push({id: technology_list[j], text: technology_list[j], value : technology_list[j]});
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
        			var vendors = obj.sector_ss_vendor.toLowerCase();
        			if(vendors.search(query.term.toLowerCase()) > -1) {
	        			return true;
        			} else {
        				return false;
        			}
        		});

		        var data = {results: []}, i, j, s;
		        var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < limit; i++) {
		        	var sectors = filtered_data[i].data.param.sector;
        			for(var j=0;j<sectors.length;j++) {
        				var condition = selected_technology.length > 0 ? selected_technology.indexOf(sectors[j].technology) > -1 : true;
        				if(condition) {
	        				if(searchPattern.test(sectors[j].vendor)) {
					        	if(bs_vendor_array.indexOf(sectors[j].vendor) < 0) {
					        		bs_vendor_array.push(sectors[j].vendor);
					            	data.results.push({id: sectors[j].vendor, text: sectors[j].vendor, value : sectors[j].vendor});
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
        			if(searchPattern.test(obj.data.state)) {
        				return true;
        			} else {
        				return false;
        			}
        		});

		        var data = {results: []}, i, j, s;
		        var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < limit; i++) {
		        	if(showing_states.indexOf(filtered_data[i].data.state) < 0) {
		        		showing_states.push(filtered_data[i].data.state);
		            	data.results.push({id: filtered_data[i].data.state, text: filtered_data[i].data.state, value : filtered_data[i].data.state});
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
        			if(searchPattern.test(obj.data.city)) {
        				return true;
        			} else {
        				return false;
        			}
        		});

		        var data = {results: []}, i, j, s;
		        var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < limit; i++) {
		        	if(showing_cities.indexOf(filtered_data[i].data.city) < 0) {
		        		if(selected_state.length > 0) {
		        			if(selected_state.indexOf(filtered_data[i].data.state) > -1) {
				            	data.results.push({id: filtered_data[i].data.city, text: filtered_data[i].data.city, value : filtered_data[i].data.city});
		        			}
		        		} else {
			            	data.results.push({id: filtered_data[i].data.city, text: filtered_data[i].data.city, value : filtered_data[i].data.city});		        			
		        		}
		        		// Push city data to array
		        		showing_cities.push(filtered_data[i].data.city);
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
        			var frequencies = obj.sector_planned_frequencies.toLowerCase();
        			if(frequencies.search(query.term.toLowerCase()) > -1) {
	        			return true;
        			} else {
        				return false;
        			}
        		});

		        var data = {results: []}, i, j, s;
		        var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < limit; i++) {
		        	var freq_list = filtered_data[i].sector_planned_frequencies.split("|");
        			for(var j=0;j<freq_list.length;j++) {
        				if(searchPattern.test(freq_list[j])) {
				        	if(sector_freq_array.indexOf(freq_list[j]) < 0 && freq_list[j] != 'NA') {
				        		sector_freq_array.push(freq_list[j]);
				            	data.results.push({id: freq_list[j], text: freq_list[j], value : freq_list[j]});
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
        			var sectors = obj.data.param.sector;
        			for(var i=0;i<sectors.length;i++) {
	        			if(searchPattern.test(sectors[i].orientation)) {
	        				return true;
	        			} else {
	        				return false;
	        			}
        			}
        		});

		        var data = {results: []}, i, j, s;
		        var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < limit; i++) {
		        	var sectors = filtered_data[i].data.param.sector;
        			for(var j=0;j<sectors.length;j++) {
        				if(searchPattern.test(sectors[j].orientation)) {
				        	if(polarization_array.indexOf(sectors[j].orientation.toLowerCase()) < 0 && sectors[j].orientation != 'NA') {
				        		polarization_array.push(sectors[j].orientation.toLowerCase());
				            	data.results.push({id: sectors[j].orientation, text: sectors[j].orientation, value : sectors[j].orientation});
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
        			var searchPattern = new RegExp('^' + query.term, 'i');
        			if(searchPattern.test(obj.alias)) {
        				return true;
        			} else {
        				return false;
        			}
        		});

		        var data = {results: []}, i, j, s;
		        var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < limit; i++) {
		        	if(bs_name_array.indexOf(filtered_data[i].alias) < 0) {
		        		bs_name_array.push(filtered_data[i].alias);
		            	data.results.push({id: filtered_data[i].alias, text: filtered_data[i].alias, value : filtered_data[i].alias});
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
		        for (i = 0; i < limit; i++) {
		        	var ips = filtered_data[i].sector_configured_on_devices.split("|");
		        	for(var j=0;j<ips.length;j++) {
		        		if(searchPattern.test(ips[j])) {
		        			if(ip_address_array.indexOf(ips[j]) < 0) {
		        				ip_address_array.push(ips[j]);
		            			data.results.push({id: ips[j], text: ips[j], value : ips[j]});
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
        		var searchPattern = new RegExp('^' + query.term, 'i'),
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
		        for (i = 0; i < limit; i++) {
		        	var circuit_ids = filtered_data[i].circuit_ids.split("|");
		        	for(var j=0;j<circuit_ids.length;j++) {
		        		if(searchPattern.test(circuit_ids[j])) {
		        			if(circuit_id_array.indexOf(circuit_ids[j]) === -1) {
		        				circuit_id_array.push(circuit_ids[j]);
		            			data.results.push({id: circuit_ids[j], text: circuit_ids[j], value : circuit_ids[j]});
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
        			if(searchPattern.test(obj.data.city)) {
        				return true;
        			} else {
        				return false;
        			}
        		});

		        var data = {results: []}, i, j, s;
		        var limit = filtered_data.length <= 40 ? filtered_data.length : 40;
		        for (i = 0; i < limit; i++) {
		        	if(showing_cities.indexOf(filtered_data[i].data.city) < 0) {
		        		showing_cities.push(filtered_data[i].data.city);
		            	data.results.push({id: filtered_data[i].data.city, text: filtered_data[i].data.city, value : filtered_data[i].data.city});
		        	}
		        }
		        query.callback(data);
		    }
        });

        hideSpinner();
	};

	/**
     * This function search data as per the applied search creteria
     * @method advanceSearchFunc
     */
	this.advanceSearchFunc = function() {


		var technology_filter = $("#filter_technology").select2('val').length > 0 ? $("#filter_technology").select2('val').join(',').split(',') : [],
			vendor_filter = $("#filter_vendor").select2('val').length > 0 ? $("#filter_vendor").select2('val').join(',').split(',') : [],
			city_filter = $("#filter_city").select2('val').length > 0 ? $("#filter_city").select2('val').join(',').split(',') : [],
			state_filter = $("#filter_state").select2('val').length > 0 ? $("#filter_state").select2('val').join(',').split(',') : [],
			frequency_filter = $("#filter_frequency").select2('val').length > 0 ? $("#filter_frequency").select2('val').join(',').split(',') : [],
			polarization_filter = $("#filter_polarization").select2('val').length > 0 ? $("#filter_polarization").select2('val').join(',').split(',') : [],
			isAdvanceFilterApplied = technology_filter.length > 0 || vendor_filter.length > 0 || state_filter.length > 0 || city_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0,
			isBasicFilterApplied = $.trim($("#technology").val()) || $.trim($("#vendor").val()) || $.trim($("#state").val()) || $.trim($("#city").val()),
			basic_filter_condition = $.trim($("#technology").val()) || $.trim($("#vendor").val()),
			advance_filter_condition = technology_filter.length > 0 || vendor_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0,
			selected_bs_alias = $("#search_name").select2('val').length > 0 ? $("#search_name").select2('val').join(',').split(',') : [],
			selected_ip_address = $("#search_sector_configured_on").select2('val').length > 0 ? $("#search_sector_configured_on").select2('val').join(',').split(',') : [],
			selected_circuit_id = $("#search_circuit_ids").select2('val').length > 0 ? $("#search_circuit_ids").select2('val').join(',').split(',') : [],
			selected_bs_city = $("#search_city").select2('val').length > 0 ? $("#search_city").select2('val').join(',').split(',') : [],
			isSearchApplied = selected_bs_alias.length > 0 || selected_ip_address.length > 0 || selected_circuit_id.length > 0 || selected_bs_city.length > 0,
			filtered_data = [],
			data_to_plot = [];

		if(isAdvanceFilterApplied || isBasicFilterApplied) {
			filtered_data = gmap_self.getFilteredData_gmap();
		} else {
			filtered_data = all_devices_loki_db.data;
		}
			
		if(advance_filter_condition || basic_filter_condition) {
        	data_to_plot = gmap_self.getFilteredBySectors(filtered_data);
    	} else {
    		data_to_plot = filtered_data;
    	}

    	if(isSearchApplied) {
    		var plotted_search_markers = [],
    			isSearched = 0;

	    	for(var i=data_to_plot.length;i--;) {
	    		if(isSearched > 0) {
	    			break;
	    		}

	    		var search_condition1 = selected_bs_alias.length > 0 ? selected_bs_alias.indexOf(String(data_to_plot[i].alias)) > -1 : true,
		            search_condition2 = selected_bs_city.length > 0 ? selected_bs_city.indexOf(String(data_to_plot[i].data.city)) > -1 : true,
		            circuit_id_count = selected_circuit_id.length >  0 ? $.grep(data_to_plot[i].circuit_ids.split("|"), function (elem) {
		            	return selected_circuit_id.indexOf(elem) > -1;
		            }).length : 1,
		            ip_count = selected_ip_address.length > 0 ? $.grep(data_to_plot[i].sector_configured_on_devices.split("|"), function (elem) {
		            	return selected_ip_address.indexOf(elem) > -1;
		            }).length : 1,
		            search_condition3 = ip_count > 0 ? true : false,	
		            search_condition4 = circuit_id_count > 0 ? true : false;
		            
		        if(search_condition1 && search_condition2 && search_condition3 && search_condition4) {
		            isSearched++;
		        }
	    	}
    	}

    	var bounds_lat_lon = new google.maps.LatLngBounds();

		searchResultData = data_to_plot;
		
		advJustSearch.removeSearchMarkers();
    	advJustSearch.resetVariables();

	    for(var i=data_to_plot.length;i--;) {
	    	if(selected_bs_city.length <= 0) {
	    		if(selected_bs_alias.length > 0) {
		    		var bs_alias = data_to_plot[i].alias,
		    			alias_condition = selected_bs_alias.indexOf(bs_alias) > -1 ? true : false;
		    			if(alias_condition) {
		    				bounds_lat_lon.extend(new google.maps.LatLng(data_to_plot[i].data.lat,data_to_plot[i].data.lon));
		    				// Hide State Counter Label(If Visible)
		    				if(state_wise_device_labels[data_to_plot[i].data.state] && !state_wise_device_labels[data_to_plot[i].data.state].isHidden_) {
								state_wise_device_labels[data_to_plot[i].data.state].hide();
		    				}

		    				advJustSearch.applyIconToSearchedResult(data_to_plot[i].data.lat, data_to_plot[i].data.lon);
		    			}
	    		}
		    	if(selected_ip_address.length > 0 || selected_circuit_id.length > 0) {
		    		var sectors = data_to_plot[i].data.param.sector;
		    		for(var j=0;j<sectors.length;j++) {
		    			var sub_stations = sectors[j].sub_station,
		    				sector_ip = sectors[j].sector_configured_on;
						
						// If any IP address is searched	    				
	    				if(selected_ip_address.length > 0) {
			    			var sector_ip_condition = selected_ip_address.indexOf(sector_ip) > -1 ? true : false;
			    			if(sector_ip_condition) {
			    				bounds_lat_lon.extend(new google.maps.LatLng(data_to_plot[i].data.lat,data_to_plot[i].data.lon));
			    				// Hide State Counter Label(If Visible)
			    				if(state_wise_device_labels[data_to_plot[i].data.state] && !state_wise_device_labels[data_to_plot[i].data.state].isHidden_) {
									state_wise_device_labels[data_to_plot[i].data.state].hide();
			    				}

			    				advJustSearch.applyIconToSearchedResult(data_to_plot[i].data.lat, data_to_plot[i].data.lon);
			    			}
	    				}

		    			for(var k=0;k<sub_stations.length;k++) {
		    				var ss_ip = sub_stations[k].data.substation_device_ip_address ? sub_stations[k].data.substation_device_ip_address : "",
		    					ss_circuit_id = sub_stations[k].data.param.sub_station[3].value ? sub_stations[k].data.param.sub_station[3].value : "";

		    				// If any IP address is searched
		    				if(selected_ip_address.length > 0) {
				    			var ss_ip_condition = selected_ip_address.indexOf(ss_ip) > -1 ? true : false;
				    			if(ss_ip_condition) {
				    				bounds_lat_lon.extend(new google.maps.LatLng(sub_stations[k].data.lat,sub_stations[k].data.lon));
				    				// Hide State Counter Label(If Visible)
				    				if(state_wise_device_labels[data_to_plot[i].data.state] && !state_wise_device_labels[data_to_plot[i].data.state].isHidden_) {
										state_wise_device_labels[data_to_plot[i].data.state].hide();
				    				}
				    				advJustSearch.applyIconToSearchedResult(sub_stations[k].data.lat, sub_stations[k].data.lon,advJustSearch.constants.search_ss_icon);
				    			}
		    				}

		    				// If any circuit id is searched
		    				if(selected_circuit_id.length > 0) {
				    			var ss_circuit_condition = selected_circuit_id.indexOf(ss_circuit_id) > -1 ? true : false;
				    			if(ss_circuit_condition) {
				    				bounds_lat_lon.extend(new google.maps.LatLng(data_to_plot[i].data.lat,data_to_plot[i].data.lon));
				    				bounds_lat_lon.extend(new google.maps.LatLng(sub_stations[k].data.lat,sub_stations[k].data.lon));
				    				// Hide State Counter Label(If Visible)
				    				if(state_wise_device_labels[data_to_plot[i].data.state] && !state_wise_device_labels[data_to_plot[i].data.state].isHidden_) {
										state_wise_device_labels[data_to_plot[i].data.state].hide();
				    				}
				    				advJustSearch.applyIconToSearchedResult(data_to_plot[i].data.lat, data_to_plot[i].data.lon);
				    				advJustSearch.applyIconToSearchedResult(sub_stations[k].data.lat, sub_stations[k].data.lon,advJustSearch.constants.search_ss_icon);
				    			}
		    				}
		    			}
		    		}
		    	}
	    	} else {

	    	}
	    }

	    if(isSearchApplied && data_to_plot.length > 0) {
	    	//Zoom in to selected state
			mapInstance.fitBounds(bounds_lat_lon);
			if(mapInstance.getZoom() > 15) {
                mapInstance.setZoom(15);
            }

            /*Clear all everything from map*/
			$.grep(allMarkersArray_gmap,function(marker) {
				marker.setMap(null);
			});

			// Reset variables
			allMarkersArray_gmap = [];
			main_devices_data_gmaps = [];
			currentlyPlottedDevices = [];
			allMarkersObject_gmap= {
				'base_station': {},
				'path': {},
				'sub_station': {},
				'sector_device': {},
				'sector_polygon': {}
			};

			/*Clear master marker cluster objects*/
			if(masterClusterInstance) {
				masterClusterInstance.clearMarkers();
			}

			main_devices_data_gmaps = data_to_plot;

            var inBoundData = gmap_self.getNewBoundsDevices();

			currentlyPlottedDevices = inBoundData;

            // Plot devices
            gmap_self.plotDevices_gmap(inBoundData,"base_station");

			// Show search marker after some timeout
			setTimeout(function() {
				for(var i=0;i<searchMarkers_global.length;i++) {
			    	searchMarkers_global[i].setMap(mapInstance);
			    }
			},350);
	    } else {
	    	$.gritter.add({
        		// (string | mandatory) the heading of the notification
                title: 'GIS : Advance Search',
                // (string | mandatory) the text inside the notification
                text: 'No data available for applied search.',
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false
            });
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
        	
        	if($.trim(mapPageType) == "googleEarth") {
        		gmap_self.updateStateCounter_gmaps(appliedFilterObj_gmaps);
        		// gmap_self.applyFilter_gmaps(appliedFilterObj_gmaps,$.trim(mapPageType));
    		} else if($.trim(mapPageType) == "white_background") {
    			gmap_self.applyFilter_gmaps(appliedFilterObj_gmaps,$.trim(mapPageType));
			} else {
				// if(mapInstance.getZoom() < 7) {
					gmap_self.updateStateCounter_gmaps(appliedFilterObj_gmaps);
				// } else {
				// 	gmap_self.applyFilter_gmaps(appliedFilterObj_gmaps,$.trim(mapPageType));
				// }
			}
        }
        /*If no filter is applied the load all the devices*/
        else {

        	if($.trim(mapPageType) == "googleEarth") {
    			
    			/************************Google Earth Code***********************/

        		/*Clear all the elements from google earth*/
		        earth_instance.clearEarthElements();

		        /*Reset Global Variables & Filters*/
		        earth_instance.resetVariables_earth();

		        /*Save updated data to global variable*/
				data_for_filters_earth = main_devices_data_earth;

		        /*create the BS-SS network on the google earth*/
		        earth_instance.plotDevices_earth(main_devices_data_earth,"base_station");
		    } else if($.trim(mapPageType) == "white_background") {

		    	whiteMapClass.hideAllFeatures();
		    	data_for_filter_wmap = main_devices_data_wmap;
		    	
		    	whiteMapClass.showAllFeatures();
        	} else {

        		/*Clear Existing Labels & Reset Counters*/
				gmap_self.clearStateCounters();

				isCallCompleted = 1;
				mapInstance.fitBounds(new google.maps.LatLngBounds(new google.maps.LatLng(21.1500,79.0900)));
				mapInstance.setZoom(5);
				data_for_filters = all_devices_loki_db.data;
				isApiResponse = 0;
				// Load all counters
				gmap_self.showStateWiseData_gmap(all_devices_loki_db.data);



    //     		gmap_self.show_all_elements_gmap();

				// /*Call showLinesInBounds to show the line within the bounds*/
				// /* When zoom level is greater than 8 show lines */
				// if(mapInstance.getZoom() > 8) {
				// 	/*
				// 	setTimeout is added because idle is event is trigger by marker cluster library when clicked on cluster,
				// 	so this function not called.Hence I called it after 0.35 sec
				// 	*/
				// 	setTimeout(function(){
				// 		gmap_self.showLinesInBounds();
				// 		gmap_self.showSubStaionsInBounds();
				// 		gmap_self.showBaseStaionsInBounds();
				// 		gmap_self.showSectorDevicesInBounds();
				// 		gmap_self.showSectorPolygonInBounds();
				// 	},350);
				// }

    //     		/*Save updated data to global variable*/
				// data_for_filters = main_devices_data_gmaps;

				// /*Filtered links global variable*/
				// ssLinkArray_filtered = ssLinkArray;

				// gmap_self.getFilteredLineLabel(data_for_filters);
        	}
        }
    };

    /**
	 * This function updates the states devices counter as per the applied filter
	 * @method updateStateCounter_gmaps
	 * @param filterObj, It contains the applied basic filters data object
	 */
	this.updateStateCounter_gmaps = function(filterObj) {

		/*Clear Existing Labels & Reset Counters*/
		if(window.location.pathname.indexOf("googleEarth") > -1) {
			earth_self.clearStateCounters();
		} else {
			gmap_self.clearStateCounters();
		}

		var technology_filter = $("#filter_technology").select2('val').length > 0 ? $("#filter_technology").select2('val').join(',').split(',') : [],
			vendor_filter = $("#filter_vendor").select2('val').length > 0 ? $("#filter_vendor").select2('val').join(',').split(',') : [],
			city_filter = $("#filter_city").select2('val').length > 0 ? $("#filter_city").select2('val').join(',').split(',') : [],
			state_filter = $("#filter_state").select2('val').length > 0 ? $("#filter_state").select2('val').join(',').split(',') : [],
			frequency_filter = $("#filter_frequency").select2('val').length > 0 ? $("#filter_frequency").select2('val').join(',').split(',') : [],
			polarization_filter = $("#filter_polarization").select2('val').length > 0 ? $("#filter_polarization").select2('val').join(',').split(',') : [],
			isAdvanceFilterApplied = technology_filter.length > 0 || vendor_filter.length > 0 || state_filter.length > 0 || city_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0,
			isBasicFilterApplied = filterObj['technology'] != 'Select Technology' || filterObj['vendor'] != 'Select Vendor' || filterObj['state'] != 'Select State' || filterObj['city'] != 'Select City',
			basic_filter_condition = $.trim($("#technology").val()) || $.trim($("#vendor").val()),
			advance_filter_condition = technology_filter.length > 0 || vendor_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0,
			filtered_data = [],
			data_to_plot = [];

		if(isAdvanceFilterApplied || isBasicFilterApplied) {
			filtered_data = gmap_self.getFilteredData_gmap();
		} else {
			filtered_data = all_devices_loki_db.data;
		}
			
		if(advance_filter_condition || basic_filter_condition) {
        	data_to_plot = gmap_self.getFilteredBySectors(filtered_data);
    	} else {
    		data_to_plot = filtered_data;
    	}

		if(data_to_plot.length > 0) {
			if(window.location.pathname.indexOf("googleEarth") > -1) {
				data_for_filters_earth = data_to_plot;
				isCallCompleted = 1;
				/*Set current position of google earth to india*/
				var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);
				lookAt.setLatitude(21.0000);
				lookAt.setLongitude(78.0000);
				// lookAt.setZoom
				// Update the view in Google Earth 
				ge.getView().setAbstractView(lookAt); 

				// mapInstance.fitBounds(new google.maps.LatLngBounds(new google.maps.LatLng(21.1500,79.0900)));
				// mapInstance.setZoom(5);
				isApiResponse = 0;
				earth_self.showStateWiseData_gmap(data_to_plot);
			} else {
				data_for_filters = data_to_plot;
				isCallCompleted = 1;
				mapInstance.fitBounds(new google.maps.LatLngBounds(new google.maps.LatLng(21.1500,79.0900)));
				mapInstance.setZoom(5);
				isApiResponse = 0;
				gmap_self.showStateWiseData_gmap(data_to_plot);
			}
		} else {
			$.gritter.add({
        		// (string | mandatory) the heading of the notification
                title: 'GIS : Filters',
                // (string | mandatory) the text inside the notification
                text: 'No data available for applied filters.',
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false
            });
		}

	};

	/**
	 * This function clear the state counter & labels
	 * @method clearStateCounters
	 */
	this.clearStateCounters = function() {
		for(key in state_wise_device_counters) {
			state_wise_device_counters[key] = 0;
			if(state_wise_device_labels[key]) {
				state_wise_device_labels[key].close();
			}
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
			if(drawingManager) {
				drawingManager.setDrawingMode(null);
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
    	} else {
    		bootbox.alert("Please zoom in for live poll devices.There are too many devices.");
    		$("#clearPolygonBtn").trigger('click');
    	}
    };

    /**
     * This function initialize live polling
     * @method fetchPollingTemplate_gmap
     */
    this.fetchPollingTemplate_gmap = function() {
    	
    	var selected_technology = $("#polling_tech").val(),
    		pathArray = [],
			polygon = "",
			service_type = $("#isPing")[0].checked ? "ping" : "other";

    	/*Re-Initialize the polling*/
    	networkMapInstance.initLivePolling();
		
		/*Reset the variables*/
		polygonSelectedDevices = [];
		pointsArray = [];

    	if(selected_technology != "") {
    		
    		$("#tech_send").button("loading");

    		/*ajax call for services & datasource*/
    		$.ajax({
    			url : base_url+"/"+"device/ts_templates/?technology="+$.trim(selected_technology)+"&service_type="+service_type,
    			// url : base_url+"/"+"static/livePolling.json",
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

							var allSS = pollableDevices;
							allSSIds = [];

							var selected_polling_technology = $("#polling_tech option:selected").text();

							for(var k=allSS.length;k--;) {
								var point = new google.maps.LatLng(allSS[k].ptLat,allSS[k].ptLon);
								if(point) {
									if (google.maps.geometry.poly.containsLocation(point, polygon)) {
										if($.trim(allSS[k].technology.toLowerCase()) == $.trim(selected_polling_technology.toLowerCase())) {
											if($.trim(allSS[k].technology.toLowerCase()) == "ptp" || $.trim(allSS[k].technology.toLowerCase()) == "p2p") {
												if(allSS[k].device_name && (allSSIds.indexOf(allSS[k].device_name) == -1)) {
													allSSIds.push(allSS[k].device_name);
													polygonSelectedDevices.push(allSS[k]);
												}
											} else {
												if(allSS[k].pointType == 'sub_station') {
													if(allSS[k].device_name && (allSSIds.indexOf(allSS[k].device_name) == -1)) {
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

								if(drawingManager) {
									drawingManager.setDrawingMode(null);
								}

								if(Object.keys(currentPolygon).length > 0) {
									/*Remove the current polygon from the map*/
									currentPolygon.setMap(null);
								}

								/*Remove current polygon from map*/
								gmap_self.initLivePolling();

								/*Reset polling technology select box*/
								$("#polling_tech").val($("#polling_tech option:first").val());

								bootbox.alert("No SS found under the selected area.");

							} else if(polygonSelectedDevices.length > 200) {

								if(drawingManager) {
									drawingManager.setDrawingMode(null);
								}

								if(Object.keys(currentPolygon).length > 0) {
									/*Remove the current polygon from the map*/
									currentPolygon.setMap(null);
								}

								/*Remove current polygon from map*/
								gmap_self.initLivePolling();

								/*Reset polling technology select box*/
								$("#polling_tech").val($("#polling_tech option:first").val());

								bootbox.alert("Max. limit for selecting devices is 200.");

							} else {

								var devicesTemplate = "<div class='deviceWellContainer'>";

								for(var i=0;i<polygonSelectedDevices.length;i++) {
									
									var new_device_name = "";
									var current_technology = $.trim(polygonSelectedDevices[i].technology.toLowerCase());
									
									if(polygonSelectedDevices[i].device_name.indexOf(".") != -1) {
										new_device_name = polygonSelectedDevices[i].device_name.split(".");
										new_device_name = new_device_name.join("-");
									} else {
										new_device_name = polygonSelectedDevices[i].device_name;
									}

									var devices_counter = "";
									
									if(polygonSelectedDevices[i].pointType == 'sub_station') {
										devices_counter = polygonSelectedDevices[i].bs_sector_device;
									} else {
										devices_counter = polygonSelectedDevices[i].device_name;
									}

                                        if(!polled_device_count[devices_counter]) {
										polled_device_count[devices_counter]  = 1;
									} else {
										polled_device_count[devices_counter] = polled_device_count[devices_counter] +1;
									}


									if((current_technology == 'ptp' || current_technology == 'p2p') && polygonSelectedDevices[i].pointType == 'sub_station') {

										if(polygonSelectedDevices[i].bs_sector_device.indexOf(".") != -1) {
											var new_device_name2 = polygonSelectedDevices[i].bs_sector_device.split(".");
											new_device_name2 = new_device_name2.join("-");
										} else {
											var new_device_name2 = polygonSelectedDevices[i].bs_sector_device;
										}

										if(polled_device_count[devices_counter] <= 1) {
											devicesTemplate += '<div class="well well-sm" id="div_'+new_device_name2+'"><h5>Near-End '+(i+1)+'.) '+polygonSelectedDevices[i].sector_ip+'</h5>';
											devicesTemplate += '<div style="min-height:60px;margin-top:15px;margin-bottom: 5px;" id="livePolling_'+new_device_name2+'">';
											devicesTemplate += '<ul id="pollVal_'+new_device_name2+'" class="list-unstyled list-inline"></ul>';
											devicesTemplate += '<span class="sparkline" id="sparkline_'+new_device_name2+'"></span></div></div>';
										}

										devicesTemplate += '<div class="well well-sm" id="div_'+new_device_name+'"><h5>Far-End '+(i+1)+'.) '+polygonSelectedDevices[i].ss_ip+'</h5>';
										devicesTemplate += '<div style="min-height:60px;margin-top:15px;margin-bottom: 5px;" id="livePolling_'+new_device_name+'">';
										devicesTemplate += '<ul id="pollVal_'+new_device_name+'" class="list-unstyled list-inline"></ul>';
										devicesTemplate += '<span class="sparkline" id="sparkline_'+new_device_name+'"></span></div></div>';

									} else {
										if(polled_device_count[devices_counter] ) //<= 1) //why do we have this condition ???
                                        {
											var device_end_txt = "",
												point_name = "";
											if(polygonSelectedDevices[i].pointType == 'sub_station') {
												device_end_txt = "Far End";
												point_name = polygonSelectedDevices[i].ss_ip
											} else {
												device_end_txt = "Near End";
												point_name = polygonSelectedDevices[i].sectorName
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

    		var service_type = $("#isPing")[0].checked ? "ping" : "other";

    		$("#getDevicesPollingData").button("loading");

    		/*Disable service templates dropdown*/
    		$("#lp_template_select").attr("disabled","disabled");

			var selected_lp_template = $("#lp_template_select").val();

            // start spinner
            if($("#fetch_spinner").hasClass("hide")) {
				$("#fetch_spinner").removeClass("hide");
			}

	    	$.ajax({
				url : base_url+"/"+"device/lp_bulk_data/?ts_template="+selected_lp_template+"&devices="+JSON.stringify(allSSIds)+"&service_type="+service_type,
				// url : base_url+"/"+"static/services.json",
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
						for(var i=allSSIds.length;i--;) {

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

								var marker_name = "",
									sector_ip = "";

								for(var x=0;x<polygonSelectedDevices.length;x++) {
									if(polygonSelectedDevices[x].device_name === allSSIds[i]) {
										marker_name = polygonSelectedDevices[x].name
										if(polygonSelectedDevices[x].pointType === 'sub_station') {
											sector_ip = polygonSelectedDevices[x].sector_ip ? polygonSelectedDevices[x].sector_ip : "";
										} else {
											sector_ip = polygonSelectedDevices[x].sectorName ? polygonSelectedDevices[x].sectorName : "";
										}
									}
								}

								// var newIcon = base_url+"/"+result.data.devices[allSSIds[i]].icon,
								var num = Math.floor(Math.random() * (4 - 1 + 1)) + 1;
								var newIcon = base_url+"/static/img/marker/icon"+ num +"_small.png",
									ss_marker = allMarkersObject_gmap['sub_station']['ss_'+marker_name],
									sector_marker = allMarkersObject_gmap['sector_device']['sector_'+sector_ip],
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
									ss_marker.setOptions({
										"icon" : new google.maps.MarkerImage(newIcon,null,null,null,new google.maps.Size(32, 37))
									});
								} else if(sector_marker) {
									sector_marker.setOptions({
										"icon" : new google.maps.MarkerImage(newIcon,null,null,null,new google.maps.Size(32, 37))
									});
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

			if(ss_marker) {
				ss_marker.setOptions({
					"icon" : new google.maps.MarkerImage(newIcon,null,null,null,new google.maps.Size(32, 37))
				});
			} else if(sector_marker) {
				sector_marker.setOptions({
					"icon" : new google.maps.MarkerImage(newIcon,null,null,null,new google.maps.Size(32, 37))
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

			if(ss_marker) {
				ss_marker.setOptions({
					"icon" : new google.maps.MarkerImage(newIcon,null,null,null,new google.maps.Size(32, 37))
				});
			} else if(sector_marker) {
				sector_marker.setOptions({
					"icon" : new google.maps.MarkerImage(newIcon,null,null,null,new google.maps.Size(32, 37))
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
		if(drawingManager) {
			drawingManager.setDrawingMode(null);
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

		var current_zoom_level = mapInstance.getZoom();
		if(current_zoom_level > 7) {
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
    

    this.calculateDistance = function(array) {

    	var latLon1 = new google.maps.LatLng(array[0].getPosition().lat(), array[0].getPosition().lng()),
    		latLon2 = new google.maps.LatLng(array[1].getPosition().lat(), array[1].getPosition().lng());

    	/*Distance in m's */
    	var distance = (google.maps.geometry.spherical.computeDistanceBetween(latLon1, latLon2) / 1000).toFixed(2) * 1000;

    	//convert degree to radians
    	var lat1 = array[0].getPosition().lat() * Math.PI / 180;
    	var lat2 = array[1].getPosition().lat() * Math.PI / 180;
    	var lon1 = array[0].getPosition().lng() * Math.PI / 180;

    	var dLon = (array[1].getPosition().lng() - array[0].getPosition().lng()) * Math.PI / 180;

    	var Bx = Math.cos(lat2) * Math.cos(dLon);
    	var By = Math.cos(lat2) * Math.sin(dLon);
    	var lat3 = Math.atan2(Math.sin(lat1) + Math.sin(lat2), Math.sqrt((Math.cos(lat1) + Bx) * (Math.cos(lat1) + Bx) + By * By));
    	var lon3 = lon1 + Math.atan2(By, Math.cos(lat1) + Bx);

    	return {distance: distance, lat: lat3, lon: lon3};
    }

    this.createDistanceInfobox = function(distanceObject) {
    	var distanceInfoBox= new InfoBox({
    		content: distanceObject.distance+" m<br />Starting Point: ("+distanceObject['startLat'].toFixed(4)+","+distanceObject['startLon'].toFixed(4)+")<br />End Point: ("+distanceObject['endLat'].toFixed(4)+","+distanceObject['endLon'].toFixed(4)+")",
    		boxStyle: {
    			border: "2px solid black",
    			background: "white",
    			textAlign: "center",
    			fontSize: "9pt",
    			color: "black",
    			width: "210px"
    		},
    		disableAutoPan: true,
    		pixelOffset: new google.maps.Size(-90, 0),
    		position: new google.maps.LatLng(distanceObject.lat3 * 180 / Math.PI,distanceObject.lon3 * 180 / Math.PI),
    		closeBoxURL: "",
    		isHidden: false,
    		enableEventPropagation: true,
    		zIndex_: 9999
    	});

    	return distanceInfoBox;
    }

    /*
    Here we clear All The Variables and Point related to Rulers in tools
     */
    this.clearRulerTool_gmap= function() {

    	//Remove Ruler markers
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
     */
    this.create_old_ruler = function() {
    	if($.cookie('tools_ruler')) {
    		var ruler_Obj= JSON.parse($.cookie('tools_ruler'));
    		if(ruler_Obj) {
    			
    			var first_point = new google.maps.Marker({position: new google.maps.LatLng(ruler_Obj["startLat"], ruler_Obj["startLon"]), map: mapInstance});
    			ruler_array.push(first_point);

    			var second_point = new google.maps.Marker({position: new google.maps.LatLng(ruler_Obj["endLat"], ruler_Obj["endLon"]), map: mapInstance});
    			ruler_array.push(second_point);

    			var current_line =  gmap_self.createLink_gmaps(ruler_Obj);
    			tools_rule_array.push(current_line);

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
        mapInstance.setOptions({'draggableCursor' : 'default'});

		google.maps.event.addListener(mapInstance,'click',function(e) {

			if(tools_rule_array.length) {
				gmap_self.clearRulerTool_gmap();
				return ;
			}

			ruler_point = new google.maps.Marker({position: e.latLng, map: mapInstance});
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
				};
				
				var ruler_line = gmap_self.createLink_gmaps(latLonObj);
				/*Show Line on Map*/
				ruler_line.setMap(mapInstance);
				
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

	/*
	This function clears the Lines drawn in Tool
	 */
	this.clearLineTool_gmap= function() {
		// google.maps.event.clearListeners(mapInstance, 'click');
    	//Remove Ruler markers
    	for(var i=0;i<tools_line_array.length;i++) {
    		tools_line_array[i].setMap(null);
    	}
    	tools_line_array = [];

    	/*Remove line between two points*/
    	for(var j=0;j<tools_line_marker_array.length;j++) {
    		tools_line_marker_array[j].setMap(null);
    	}
    	tools_line_marker_array = [];

    	/*Remove Distance Label*/
    	if(distance_line_label.map != undefined) {
    		distance_line_label.setMap(null);
    	}

    	line_pt_array= [];

    	is_bs_clicked= 0;

    	//Reset Cookie
    	$.cookie('tools_line', 0, {path: '/', secure : true});


    	tools_line = $.cookie("tools_line");
	}

	this.create_old_line= function() {
		if($.cookie('tools_line')) {
    		var line_obj= JSON.parse($.cookie('tools_line'));
    		if(line_obj) {
    			
    			var first_point = new google.maps.Marker({position: new google.maps.LatLng(line_obj["startLat"], line_obj["startLon"]), map: mapInstance});
    			tools_line_marker_array.push(first_point);

    			var second_point = new google.maps.Marker({position: new google.maps.LatLng(line_obj["endLat"], line_obj["endLon"]), map: mapInstance});
    			tools_line_marker_array.push(second_point);

    			var current_line =  gmap_self.createLink_gmaps(line_obj);
    			tools_line_array.push(current_line);

    			$.cookie('tools_line',JSON.stringify(line_obj),{path: '/', secure : true});

    			tools_line = $.cookie("tools_line");

				distance_line_label= gmap_self.createDistanceInfobox(line_obj);

				/*Show distance infobox*/
				distance_line_label.open(mapInstance);

				hasTools = 1;
    		}
    	}
	}

	/*
	This function enables Line tool & perform corresponding functionality.
	 */
    this.createLineTool_gmap = function() {
    	google.maps.event.clearListeners(mapInstance, 'click');

    	google.maps.event.addListener(mapInstance, 'click', function(e) {
    		if(tools_line_array.length) {
				gmap_self.clearLineTool_gmap();
    			return ;
    		}

    		if(!is_bs_clicked) {
    			bootbox.alert("Select BS First");
    		} else {
    			var marker= new google.maps.Marker({position: line_pt_array[0], map: mapInstance, icon: base_url+'/static/img/icons/1x1.png'});
    			tools_line_marker_array.push(marker);
    			marker= new google.maps.Marker({position: e.latLng, map: mapInstance, icon: base_url+'/static/img/icons/1x1.png'});
    			tools_line_marker_array.push(marker);

    			var distanceObject= gmap_self.calculateDistance(tools_line_marker_array);

				/*Lat lon object for poly line*/
				var latLonObj = {
					"startLat" : tools_line_marker_array[0].getPosition().lat(),
					"startLon" : tools_line_marker_array[0].getPosition().lng(),
					"endLat" : tools_line_marker_array[1].getPosition().lat(),
					"endLon" : tools_line_marker_array[1].getPosition().lng(),
					"distance": distanceObject.distance,
					"lat3": distanceObject.lat,
					"lon3": distanceObject.lon,
					"nearEndLat" : tools_line_marker_array[0].getPosition().lat(),
					"nearEndLon" : tools_line_marker_array[0].getPosition().lng()
				};

				var ruler_line = gmap_self.createLink_gmaps(latLonObj);

				tools_line_array.push(ruler_line);

				$.cookie('tools_line',JSON.stringify(latLonObj),{path: '/', secure : true});

				tools_line = $.cookie("tools_line");

				distance_line_label= gmap_self.createDistanceInfobox(latLonObj);

				/*Show distance infobox*/
				distance_line_label.open(mapInstance);

				hasTools = 1;
    		}
    	});
    }

    this.clearPointsTool_gmap= function() {

    	for(var i=0; i< map_points_array.length; i++) {

    		map_points_array[i].setMap(null);
    	}

    	map_points_array= [];

    	map_points_lat_lng_array= [];

    	map_point_count= 0;
    }

    this.create_old_points= function() {

    	var image = new google.maps.MarkerImage(base_url+"/static/img/icons/caution.png",null,null,null,new google.maps.Size(32, 37));

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
    }

    /**
	 * This function enables point tool & perform corresponding functionality.
	 * @method addPointTool_gmap
	 */
	this.addPointTool_gmap = function() {
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
	};

	/**
	 * This function plot the point on google map as per the given details
	 * @method plotPoint_gmap
	 * @param {Object} infoObj, It contains information regarding plotting(i.e. lat,lon etc)
	 */
	this.plotPoint_gmap = function(infoObj) {

		var image = new google.maps.MarkerImage(base_url+"/"+infoObj.icon_url,null,null,null,new google.maps.Size(32, 37));
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
			var markerRightClick= google.maps.event.addListener(marker, 'click', function(event) {
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

			return markerRightClick;
		})(map_point);
	};

	this.openPointRightClickMenu = function(marker) {

		var right_click_html = "",
			markerInfo = {
				'name' 				: 	marker.point_name,
				'desc' 				: 	marker.point_desc,
				'lat'  				: 	marker.lat,
				'lon'  				: 	marker.lon,
				'connected_lat' 	: 	marker.connected_lat,
				'connected_lon' 	: 	marker.connected_lon,
				'point_id' 			: 	marker.point_id,
				'icon_url' 			: 	marker.icon_url,
				'is_delete_req' 	: 	marker.is_delete_req,
				'is_update_req' 	: 	marker.is_update_req
			},
			method_var = JSON.stringify(markerInfo);

		right_click_html += "<div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>Point Tool</h4></div><div class='box-body' style='width:300px;'>";
		right_click_html += "<table class='table table-bordered'><tbody>";
		right_click_html += "<tr><td>Name</td><td><input type='text' class='form-control' name='point_name' id='point_name' value='"+marker.point_name+"'/></td></tr>";
		right_click_html += "<tr><td>Description</td><td><textarea name='point_desc' id='point_desc' class='form-control'>"+marker.point_desc+"</textarea></td></tr>";
		right_click_html += "<tr><td align='center'><button type='button' class='btn btn-sm btn-primary' id='point_info_remove_btn' onClick='gmap_self.removePointInfo_gmap("+method_var+")'>Remove Point</button></td><td align='center'><button type='button' class='btn btn-sm btn-primary' id='point_info_save_btn' onClick='gmap_self.savePointInfo_gmap("+method_var+")'>Save Point</button></td></tr>";

		/*If point saved then show add/remove line option*/
		if(marker.point_id > 0) {
			if(marker.connected_lat == "" && marker.connected_lon == "") {
				right_click_html += "<tr><td colspan='2' align='center'><button type='button' class='btn btn-sm btn-primary' onClick='gmap_self.addLineToPoint_gmap("+method_var+")' id='add_line_from_pt_btn'>Add Line</button></td></tr>";
			}
		}

		right_click_html += "<tr><td colspan='2' align='center' id='response_msg_container'></td></tr>"
		right_click_html +="</tbody></table>";
		right_click_html += "<div class='clearfix'></div></div></div>";

		/*Close infowindow if any opened*/
		infowindow.close();

		/*Set the content for infowindow*/
		infowindow.setContent(right_click_html);
		/*Open the info window*/
		infowindow.open(mapInstance,marker);
	};

	/**
	 * This function save current point information in db by calling the respective API
	 * @method savePointInfo_gmap
	 */
	this.savePointInfo_gmap = function(marker) {

		var marker_lat_str = String(marker.lat).split(".").join("-"),
			marker_lon_str = String(marker.lon).split(".").join("-"),
			current_marker = point_data_obj["point_"+marker_lat_str+"_"+marker_lon_str];

		if($.trim($("#point_name").val()) == '') {
			bootbox.alert("Please enter point name");
		} else {

			marker.name = current_marker.point_name = $("#point_name").val();
			marker.desc = current_marker.point_desc = $("#point_desc").val();
			marker.point_id = current_marker.point_id;
			marker.is_update_req = current_marker.is_update_req;
			marker.is_delete_req = current_marker.is_delete_req;

			$.ajax({
            	url: base_url+'/network_maps/tools/point/',
            	data: JSON.stringify(marker),
            	type: 'POST',
            	dataType: 'json',
            	success : function(result) {
            		if(result.success === 1) {
            			current_marker.point_id = result.data.point_id;
            			current_marker.is_update_req = result.data.point_id;
            		} else {
            			current_marker.name = "";
            			current_marker.desc = "";
            			$("#point_name").val("");
            			$("#point_desc").val("");
            			current_marker.point_id = 0;
            			current_marker.is_update_req = 0;
            		}
            		$("#response_msg_container").html(result.message);
            	},
            	error : function(err) {
            		console.log(err);
            	}
        	});
		}
	}

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
            	success : function(result) {
            		if(result.success === 1) {
            			/*Remove point marker from google map*/
						current_marker.setMap(null);
						if(current_line) {
							current_line.setMap(null);
						}

						/*Delete point from global object*/
						delete point_data_obj["point_"+String(marker.lat).split(".").join("-")+"_"+String(marker.lon).split(".").join("-")];
						delete line_data_obj["point_"+String(marker.lat).split(".").join("-")+"_"+String(marker.lon).split(".").join("-")];
        			} else {
        				$("#response_msg_container").html("Point not removed.Please try again.");		
        			}
            	},
            	error : function(err) {
            		console.log(err);
            	}
			});
		} else {
			/*Remove point marker from google map*/
			current_marker.setMap(null);
			if(current_line) {
				current_line.setMap(null);
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

		pointAdded= 1;

		current_point_for_line = "point_"+String(marker.lat).split(".").join("-")+"_"+String(marker.lon).split(".").join("-");

		// infowindow.close();
		$("#infoWindowContainer").addClass('hide');

		//first clear the listners. as ruler tool might be in place
        google.maps.event.clearListeners(mapInstance,'click');

		google.maps.event.addListener(mapInstance,'click',function(e) {

			if(Object.keys(connected_end_obj).length === 0) {
				alert("Please select other point");
			} else {
				$("#point_select").trigger("click");
				connected_end_obj = {};
			}
		});
	};

	/**
	 * This function plot lines between selected points & also call API to update the info in db
	 * @method plot_point_line
	 * @param {Object} marker, It is the google marker objects
	 */
	this.plot_point_line = function(marker) {

		var current_pt = current_point_for_line;
		var line_obj = {
			"startLat" : point_data_obj[current_pt].lat,
			"startLon" : point_data_obj[current_pt].lon,
			"endLat" : connected_end_obj.lat,
			"endLon" : connected_end_obj.lon,
			"nearEndLat" : point_data_obj[current_pt].lat,
			"nearEndLon" : point_data_obj[current_pt].lon,
		};


		/*Create line between the point & device*/
		var current_line =  gmap_self.createLink_gmaps(line_obj);
		/*Show Line on Map*/
		if(mapInstance.getZoom() > 7) {
			current_line.setMap(mapInstance);
		} else {
			current_line.setMap(null);
		}
		/*Update Connected Lat Lon info in marker object*/
		point_data_obj[current_pt].connected_lat = connected_end_obj.lat;
		point_data_obj[current_pt].connected_lon = connected_end_obj.lon;
		point_data_obj[current_pt].connected_point_type = marker.pointType ? marker.pointType : "point";
		point_data_obj[current_pt].connected_point_info = marker.filter_data ? JSON.stringify(marker.filter_data) : "";

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
        	success : function(result) {
        		if(result.success === 1) {
        			if(result.data) {
            			point_data_obj[current_pt].point_id = result.data.point_id;
            			point_data_obj[current_pt].is_update_req = result.data.point_id;
        			}
        		}
        	},
        	error : function(err) {
        		console.log(err);
        	}
    	});

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

				gmap_self.remove_point_line(current_pt,current_line_ptr);
			});
		});

		current_point_for_line = "";
	};

	/**
	 * This function removed the given line from gmap & also update the global object
	 * @method remove_point_line
	 */
	this.remove_point_line = function(current_pt,current_line_ptr) {

		/*Update marker object*/
		point_data_obj[current_pt].connected_lat = 0;
		point_data_obj[current_pt].connected_lon = 0;
		
		// infowindow.close();
		$("#infoWindowContainer").addClass('hide');
		current_line_ptr.setMap(null);

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
        	success : function(result) {
        		if(result.success === 1) {
        			point_data_obj[current_pt].point_id = result.data.point_id;
        			point_data_obj[current_pt].is_update_req = result.data.point_id;
        			point_data_obj[current_pt].connected_point_type = '';
        			point_data_obj[current_pt].connected_point_info = '';
        		}
        	},
        	error : function(err) {
        		console.log(err);
        	}
    	});
	};

	/**
	 * This function call the get_tools_data API  to populate available point & line on gmap
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

					var current_point = point_array[i];
					var infoObj = {
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
					gmap_self.plotPoint_gmap(infoObj);

					if(current_point.connected_lat != 0 && current_point.connected_lon != 0) {
						var point_custom_id = "point_"+String(current_point.lat).split(".").join("-")+"_"+String(current_point.lon).split(".").join("-");
						var line_obj = {
							"startLat"   : current_point.lat,
							"startLon"   : current_point.lon,
							"endLat"     : current_point.connected_lat,
							"endLon"     : current_point.connected_lon,
							"nearEndLat" : current_point.lat,
							"nearEndLon" : current_point.lon,
						};

						/*Create line between the point & device*/
						var current_line =  gmap_self.createLink_gmaps(line_obj);
						if(mapInstance.getZoom() > 7) {
							current_line.setMap(mapInstance);
						} else {
							current_line.setMap(null);
						}
						line_data_obj[point_custom_id] = current_line;

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

			},
			error : function(err) {
				console.log(err.statusText);
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
	 	var current_zoom_level = mapInstance.getZoom();
		if(current_zoom_level > 7) {
		 	var bs_list = getMarkerInCurrentBound();
	    	if(bs_list.length > 0 && isCallCompleted == 1) {
	    		if(recallPerf != "") {
	    			clearTimeout(recallPerf);
	    			recallPerf = "";
	    		}
	    		gisPerformanceClass.start(bs_list);
	    	}
    	}
	 };

	 /**
	 * This function unfreeze the system & recall the server
	 * @method unfreezeDevices_gmap
	 */
	 this.unfreezeDevices_gmap = function() {

	 	/*Enable freeze flag*/
	 	isFreeze = 0;
	 	$.cookie("isFreezeSelected", isFreeze, {path: '/', secure : true});

	 	freezedAt = 0;
	 	$.cookie("freezedAt", freezedAt, {path: '/', secure : true});


	 	/*Set Live Polling flag*/
	 	// isPollingActive = 0;

	 	var current_zoom_level = mapInstance.getZoom();
		if(current_zoom_level > 7) {
		 	var bs_list = getMarkerInCurrentBound();
	    	if(bs_list.length > 0 && isCallCompleted == 1) {
	    		if(recallPerf != "") {
	    			clearTimeout(recallPerf);
	    			recallPerf = "";
	    		}
	    		gisPerformanceClass.start(bs_list);
	    	}
    	}

	 	/*Recall the server*/
	 	// gmap_self.recallServer_gmap();
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
		mapInstance.setZoom(15);

		lastSearchedPt = marker;
	};

	/**
	 * This function hide all items from google map
	 * @method hide_all_elements_gmap
	 */
	this.hide_all_elements_gmap = function() {
		/*Clear all everything from map*/
		$.grep(allMarkersArray_gmap,function(marker) {
			marker.setOptions({"isActive" : 0});
			marker.setMap(null);
		});

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
	}

	/**
	 * This function show all items from google map
	 * @method show_all_elements_gmap
	 */
	this.show_all_elements_gmap = function() {

		/*Show everything on map except connection line*/
		$.grep(allMarkersArray_gmap,function(marker) {
			marker.setOptions({"isActive" : 1});
			// if(marker.pointType && ($.trim(marker.pointType) != 'path') && ($.trim(marker.pointType) != 'sub_station')) {
			// 	marker.setMap(mapInstance);
			// } else {
			// 	if(marker.pointType && $.trim(marker.pointType) == 'sub_station') {
			// 		marker.setOptions({"isActive" : 1});
			// 	}
			// }
		});

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
	}

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
			
			var sectorsArray = dataArray[i].data.param.sector;

			for(var j=0;j<sectorsArray.length;j++) {

				/*Check that the current sector name is present in filtered data or not*/
				var subStationsArray = sectorsArray[j].sub_station,
					sectorName = sectorsArray[j].sector_configured_on ? $.trim(sectorsArray[j].sector_configured_on) : "",
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
			gmap_self.showSectorPolygonInBounds();
			// setTimeout(function(){
			// },350);
	    }
	};

	/**
	 * This function export selected data by calling respective API
	 * @method exportData_gmap
	 */
	this.exportData_gmap = function() {

		var exportDataPolygon = {};

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

			var pathArray = e.overlay.getPath().getArray(),
				polygon = new google.maps.Polygon({"path" : pathArray}),
				bs_ss_array = masterMarkersObj;

			exportDataPolygon = e.overlay;
			exportDataPolygon.type = e.type;
			
			// If markers showing
			if(mapInstance.getZoom() > 7) {
				var bs_obj = allMarkersObject_gmap['base_station'],
					selected_bs = [];
				for(key in bs_obj) {
					var markerVisible = mapInstance.getBounds().contains(bs_obj[key].getPosition());
		            if(markerVisible) {
		            	if(google.maps.geometry.poly.containsLocation(bs_obj[key].getPosition(),polygon)) {
		            		if(selected_bs.indexOf(bs_obj[key].filter_data.bs_id) == -1) {
		            			selected_bs.push(bs_obj[key].filter_data.bs_id);
		            		} 
		            			
		            	}
	            	}
				}
				// If any bs exists
				if(selected_bs.length > 0) {

					// Send ajax call to download selected inventory report
					$.ajax({
						url : base_url+"/?ids="+JSON.stringify(selected_bs),
						type : "GET",
						success : function(result) {
							console.log(result);
						},
						error : function(err) {
							console.log(err.statusText);
						},
						complete : function() {
							/*Reset the drawing object if exist*/
							if(drawingManager) {
								drawingManager.setDrawingMode(null);
							}

							/*Remove the polygon if exists*/
							if(Object.keys(exportDataPolygon).length > 0) {
								exportDataPolygon.setMap(null);
								exportDataPolygon = {}
							}

							if($("#export_data_gmap").hasClass('btn-warning')) {
						        $("#export_data_gmap").removeClass('btn-warning');
						        $("#export_data_gmap").addClass('btn-info');
						    }
						}
					});
				} else {
					bootbox.alert("No BS found in the selected area.");	
				}

			} else {
			
				var technology_filter = $("#filter_technology").select2('val').length > 0 ? $("#filter_technology").select2('val').join(',').split(',') : [],
					vendor_filter = $("#filter_vendor").select2('val').length > 0 ? $("#filter_vendor").select2('val').join(',').split(',') : [],
					city_filter = $("#filter_city").select2('val').length > 0 ? $("#filter_city").select2('val').join(',').split(',') : [],
					state_filter = $("#filter_state").select2('val').length > 0 ? $("#filter_state").select2('val').join(',').split(',') : [],
					frequency_filter = $("#filter_frequency").select2('val').length > 0 ? $("#filter_frequency").select2('val').join(',').split(',') : [],
					polarization_filter = $("#filter_polarization").select2('val').length > 0 ? $("#filter_polarization").select2('val').join(',').split(',') : [],
					filterObj = {
						"technology" : $.trim($("#technology option:selected").text()),
						"vendor" : $.trim($("#vendor option:selected").text()),
						"state" : $.trim($("#state option:selected").text()),
						"city" : $.trim($("#city option:selected").text())
					},
					isAdvanceFilterApplied = technology_filter.length > 0 || vendor_filter.length > 0 || state_filter.length > 0 || city_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0,
					isBasicFilterApplied = filterObj['technology'] != 'Select Technology' || filterObj['vendor'] != 'Select Vendor' || filterObj['state'] != 'Select State' || filterObj['city'] != 'Select City';

				var states_within_polygon = state_lat_lon_db.where(function(obj) {
        			return google.maps.geometry.poly.containsLocation(new google.maps.LatLng(obj.lat,obj.lon),polygon);
        		});

        		var bs_id_array = [],
        			states_array = [];

        		for(var i=0;i<states_within_polygon.length;i++) {
        			if(state_wise_device_labels[states_within_polygon[i].name]) {
        				states_array.push(states_within_polygon[i].name);
        			}
        		}


        		if(states_within_polygon.length > 0) {
					
					var current_bound_devices = all_devices_loki_db.where(function( obj ) {
            			if(!isAdvanceFilterApplied && !isBasicFilterApplied) {
            				if(states_array.indexOf(obj.data.state) > -1) {
	            				bs_id_array.push(obj.id);
	            				return true;
            				} else {
            					return false;
            				}
            			} else if(isAdvanceFilterApplied) {
            				var technology_count = technology_filter.length >  0 ? $.grep(obj.sector_ss_technology.split("|"), function (elem) {
						        	return technology_filter.indexOf(elem) > -1;
						        }).length : 1,
				            	filter_condition1 = technology_count > 0 ? true : false,
				            	vendor_count = vendor_filter.length >  0 ? $.grep(obj.sector_ss_vendor.split("|"), function (elem) {
						        	return vendor_filter.indexOf(elem) > -1;
						        }).length : 1,
				                filter_condition2 = vendor_count > 0 ? true : false,
				                filter_condition3 = state_filter.length > 0 ? state_filter.indexOf(obj.data.state) > -1 : true,
				                filter_condition4 = city_filter.length > 0 ? city_filter.indexOf(obj.data.city) > -1 : true;
					            
					            // Condition to check for applied advance filters
					            if(filter_condition1 && filter_condition2 && filter_condition3 && filter_condition4) {
					            	if(states_array.indexOf(obj.data.state) > -1) {
			            				bs_id_array.push(obj.id);
			            				return true;
		            				} else {
		            					return false;
		            				}
					            } else {
					                return false;
					            }
            			} else if(isBasicFilterApplied) {

            				var sectors = obj.data.param.sector,
								basic_filter_condition1 = filterObj['state'] != 'Select State' ? obj.data.state == filterObj['state'] : true,
								basic_filter_condition2 = filterObj['city'] != 'Select City' ? obj.data.city == filterObj['city'] : true;;
							for(var i=sectors.length;i--;) {
								var basic_filter_condition3 = filterObj['technology'] != 'Select Technology' ? $.trim(sectors[i]['technology'].toLowerCase()) == $.trim(filterObj['technology'].toLowerCase()) : true,
									basic_filter_condition4 = filterObj['vendor'] != 'Select Vendor' ? $.trim(sectors[i]['vendor'].toLowerCase()) == $.trim(filterObj['vendor'].toLowerCase()) : true

								if(basic_filter_condition1 && basic_filter_condition2 && basic_filter_condition3 && basic_filter_condition4) {
									if(states_array.indexOf(obj.data.state) > -1) {
			            				bs_id_array.push(obj.id);
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
						var sectors = current_bound_devices[x].data.param.sector,
							delete_index = [];
						for(var y=0;y<sectors.length;y++) {
							var sector_technology = $.trim(sectors[y].technology),
								sector_vendor = $.trim(sectors[y].vendor);
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
							current_bound_devices[x].data.param.sector.splice(delete_index[z],1);
						}
					}

					// If any bs exists
					if(bs_id_array.length > 0) {

						// Send ajax call to download selected inventory report
						$.ajax({
							url : base_url+"/?ids="+JSON.stringify(bs_id_array),
							type : "GET",
							success : function(result) {
								console.log(result);
							},
							error : function(err) {
								console.log(err.statusText);
							},
							complete : function() {
								/*Reset the drawing object if exist*/
								if(drawingManager) {
									drawingManager.setDrawingMode(null);
								}

								/*Remove the polygon if exists*/
								if(Object.keys(exportDataPolygon).length > 0) {
									exportDataPolygon.setMap(null);
									exportDataPolygon = {}
								}

								if($("#export_data_gmap").hasClass('btn-warning')) {
							        $("#export_data_gmap").removeClass('btn-warning');
							        $("#export_data_gmap").addClass('btn-info');
							    }
							}
						});
					} else {
						bootbox.alert("No BS found in the selected area.");	
					}

        		} else {
        			bootbox.alert("No BS found in the selected area.");
        		}
			}
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

	//This function updates the Marker Icon with the new Size.
	this.updateAllMarkersWithNewIcon= function(iconSize) {

		var largeur= 32, hauteur= 37,largeur_bs = 32, hauteur_bs= 37, divideBy;
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
						new google.maps.Size(Math.ceil(largeur/divideBy), Math.ceil(hauteur/divideBy)));
					//Set icon to Marker Image
					markerIcon.setIcon(markerImage2);
					// //Set oldIcon to Marker Image
					markerIcon.oldIcon= markerImage2;
					markerIcon.clusterIcon= markerImage2;
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

            bs_data.data.param.sector=[];            
            /*Sectors Array*/
            for(var j=0;j<filteredDataArray[i].data.param.sector.length;j++) {
                var sector = filteredDataArray[i].data.param.sector[j];

                var ss_data = filteredDataArray[i].data.param.sector[j].sub_station;
            
                for(var k=0;k<ss_data.length;k++) {
                	var ssName = $.trim(ss_data[k].name),
                		bsName = $.trim(filteredDataArray[i].name),
            			sectorName = $.trim(sector.sector_configured_on);

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
}


function prepare_data_for_filter() {

    var filter_data_bs_city_collection=[];
        filter_data_bs_state_collection=[];
        filter_data_sector_ss_technology_collection=[];
        filter_data_sector_ss_vendor_collection=[],
    	current_data = [];

    if(window.location.pathname.indexOf("googleEarth") > -1) {
		current_data = main_devices_data_earth;
	} else if(window.location.pathname.indexOf("white_background") > -1) {
		current_data = main_devices_data_wmap;
	} else {
		current_data = main_devices_data_gmaps;
	}

    if (current_data.length > 0) {
    		var city_array = [],
    			state_array = [];
            for (i=0; i< current_data.length; i++) {

            	filter_data_bs_state_collection.push({ 'id': current_data[i].id, 'value': current_data[i].data.state });
            	filter_data_bs_city_collection.push({ 'id': current_data[i].id, 'value': current_data[i].data.city});

				/*Sector Devices Array*/
				var sector_device = current_data[i].data.param.sector;

				/*Reset technology & vendor Array*/
				filter_data_sector_ss_technology_value = [];
				filter_data_sector_ss_vendor_value = [];
				tech_for_vendor = []

				for(var j=0;j<sector_device.length;j++) {
					
					if(filter_data_sector_ss_technology_value.indexOf(sector_device[j].technology) == -1) {
						filter_data_sector_ss_technology_value.push(sector_device[j].technology);
					}

					if(filter_data_sector_ss_vendor_value.indexOf(sector_device[j].vendor) == -1) {
						filter_data_sector_ss_vendor_value.push(sector_device[j].vendor);
						tech_for_vendor.push(sector_device[j].technology);
					}
				}

				filter_data_sector_ss_technology_collection.push({ 'id': current_data[i].id , 'value':filter_data_sector_ss_technology_value });

				filter_data_sector_ss_vendor_collection.push({ 'id':current_data[i].id, 'value':filter_data_sector_ss_vendor_value , 'parent_name' : tech_for_vendor});
            }

            filter_data_bs_state_collection= unique_values_field_and_with_base_station_ids(filter_data_bs_state_collection);
            filter_data_bs_city_collection= unique_values_field_and_with_base_station_ids(filter_data_bs_city_collection);
            filter_data_sector_ss_technology_collection= unique_values_field_and_with_base_station_ids(filter_data_sector_ss_technology_collection,'technology');
            filter_data_sector_ss_vendor_collection = unique_values_field_and_with_base_station_ids(filter_data_sector_ss_vendor_collection,'vendor');


            var filter_data=[
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
            ];
    }//if condition closed
    return filter_data

}//function closed


function getDataForAdvanceSearch() {
	//extra form elements that will be showing in Advance Search. We will get other Elements like City, Vendor, Technology from prepare_data_for_filter();
	var filter_data_bs_name_collection=[],
		filter_data_sector_configured_on_collection=[],
		filter_data_sector_circuit_ids_collection=[],
		filter_data_bs_city_collection=[],
		current_data = [];

	if(window.location.pathname.indexOf("googleEarth") > -1) {
		current_data = main_devices_data_earth;
	} else if(window.location.pathname.indexOf("white_background") > -1) {		
		current_data = main_devices_data_wmap;
	} else {
		current_data = main_devices_data_gmaps;
	}

    if(current_data.length >0) {
    	for (i=0; i< current_data.length; i++) {
    		if (current_data[i].data.city != 'N/A'){
    			filter_data_bs_city_collection.push({ 'id': current_data[i].id,
    				'value': current_data[i].data.city });
    		}


    		filter_data_bs_name_collection.push({ 'id':[current_data[i].id], 'value':current_data[i].name, 'alias':current_data[i].alias  });

    		filter_data_sector_configured_on_value= current_data[i].sector_configured_on_devices.split('|').filter(function (n) { return n != ""});

    		for (var k=0;k<filter_data_sector_configured_on_value.length;k++) {
    			filter_data_sector_configured_on_collection.push({ 'id':[current_data[i].id], 'value':filter_data_sector_configured_on_value[k] });
    		}

    		filter_data_sector_circuit_ids_values= current_data[i].circuit_ids.split('|').filter(function (n) { return n != ""});

    		for (var k=0;k<filter_data_sector_circuit_ids_values.length;k++){
    			filter_data_sector_circuit_ids_collection.push({ 'id':[current_data[i].id], 'value':filter_data_sector_circuit_ids_values[k] });
    		}
    	}
    	filter_data_bs_city_collection= unique_values_field_and_with_base_station_ids(filter_data_bs_city_collection);

    	var advanceSearchFilterData= []; //prepare_data_for_filter();

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
		
		advanceSearchFilterData.push({
            'element_type':'multiselect',
            'field_type':'string',
            'key':'city',
            'title':'BS City',
            'values':filter_data_bs_city_collection
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
    for (var i=0;i< unique_names.length; i++) {

            var unique_device_ids=[],
            	parent_name = [];

            for(var j=0;j< filter_data_collection.length; j++) {

                if (type=='technology' || type=='vendor') {
                    if (filter_data_collection[j].value.length>1) {

                       for(var k=0;k< filter_data_collection[j].value.length; k++) {

                          if(unique_names[i]== filter_data_collection[j].value[k]) {
                            unique_device_ids.push(filter_data_collection[j].id)
                          }
                       }                       
                    }
                    else {
                        if(unique_names[i]== filter_data_collection[j].value[0]) {
                            unique_device_ids.push(filter_data_collection[j].id)
                        }
                    }
                } else {
                        if (unique_names[i]== filter_data_collection[j].value) {
                            unique_device_ids.push(filter_data_collection[j].id)
                        }
                }
            }            
        result_bs_collection.push({'id':unique_device_ids, 'value': unique_names[i]});
        }
    return result_bs_collection
}

function getMarkerInCurrentBound() {
    var bsMarkersInBound = [];
    for(var key in markersMasterObj['BS']) {
        if(markersMasterObj['BS'].hasOwnProperty(key)) {
            var markerVisible = mapInstance.getBounds().contains(markersMasterObj['BS'][key].getPosition());
            if(markerVisible) {
            	if(markersMasterObj['BS'][key].isActive && markersMasterObj['BS'][key].isActive == 1) {
            		bsMarkersInBound.push(markersMasterObj['BS'][key]['filter_data']['bs_id']);
            	}
            }
        }
    }
    return bsMarkersInBound;
}