/*Global Variables*/
var g_earth = "",
	earth_self = "",
	gexInstance = "",
	networkMapInstance = "",
	tech_vendor_obj = {},
	all_vendor_array = [],
	isFirstTime = 1,
	current_zoom = "",
	ge = "",
	plotted_bs_earth = [],
	plotted_sector_earth = [],
	plotted_ss_earth = [],
	plottedLinks_earth = [],
	devices_earth = [],
	masterMarkersObj_earth = [],
	main_devices_data_earth = [],
	data_for_filters_earth = [],
	appliedFilterObj_earth = {},
	devicesObject_earth = {},
	hitCounter = 1,
	showLimit = 0,
	devicesCount = 0,
	counter = -999,
	marker_count = 0;
var gisPerformanceClass;
var markersMasterObj;
var allMarkersObject_earth= {
	'base_station': {},
	'path': {},
	'sub_station': {},
	'sector_device': {},
	'sector_polygon': {}
};
var bsLatArray = [],
	bsLonArray = [],
	ssLatArray = [],
	ssLonArray = [],
	ssLinkArray = [],
	ssLinkArray_filtered = [];
var sectorMarkerConfiguredOn_earth = [], sector_MarkersArray= [], pollableDevices= [], sectorMarkersMasterObj= {};
var counter_div_style = "",
	state_lat_lon_db= [],
	bs_loki_db = [],
    ss_loki_db = [],
    sector_loki_db = [],
    polygon_loki_db = [],
    line_loki_db = [],
    all_devices_loki_db = [],
	state_wise_device_counters = {},
	state_wise_device_labels = {},
	null_state_device_counters = {},
	tech_vendor_obj = {},
	all_vendor_array = [],
	state_city_obj = {},
	all_cities_array = [];
var plottedBsIds = [], allMarkersArray_earth= [];
var isApiResponse = 1;

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

		//display advance search, filter etc button when call is going on.
		disableAdvanceButton();

		/*Show The loading Icon*/
		$("#loadingIcon").show();

		/*Disable the refresh button*/
		$("#resetFilters").button("loading");


		g_earth = google.earth.createInstance(domElement, earth_self.earthInitCallback, earth_self.earthFailureCallback);
	};

	function getCurrentEarthBoundPolygon() {
		var globeBounds = ge.getView().getViewportGlobeBounds();
		var poly = [
							{lat: globeBounds.getNorth(), lon: globeBounds.getWest()},
							{lat: globeBounds.getNorth(), lon: globeBounds.getEast()},
							{lat: globeBounds.getSouth(), lon: globeBounds.getEast()},
							{lat: globeBounds.getSouth(), lon: globeBounds.getWest()},
							{lat: globeBounds.getNorth(), lon: globeBounds.getWest()}]
		return poly;
	}

	var lastStateBounds = [];
	var statesDataShown = [];
	/**
	 * This function handles the initialization callback of google earth creation function
	 * @method earthInitCallback
	 * @param pluginInstance {Object}, It is the JSON object returned from google earth create instance function on successful creation of google earth.
	 */
	this.earthInitCallback = function(pluginInstance) {
		// var mapTypeId = myMap.getMapTypeId();
		// myMapObject.setMapTypeId(google.maps.MapTypeId.SATELLITE);

		ge = pluginInstance;

		

		ge.getWindow().setVisibility(true);

		/*Create Instance of google earth extension library*/
		gexInstance = new GEarthExtensions(ge);
		gexInstance.dom.clearFeatures();


		/*Set current position of google earth to india*/
		var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);
		lookAt.setLatitude(21.0000);
		lookAt.setLongitude(78.0000);
		lookAt.setRange(5019955);

		// Update the view in Google Earth 
		ge.getView().setAbstractView(lookAt); 
		// add a navigation control
		ge.getNavigationControl().setVisibility(ge.VISIBILITY_AUTO);

		// add some layers
		ge.getLayerRoot().enableLayerById(ge.LAYER_BORDERS, true);
		ge.getLayerRoot().enableLayerById(ge.LAYER_ROADS, true);


		google.earth.addEventListener(ge.getView(), 'viewchange', function(){
			if(timer){
				clearTimeout(timer);
			}
			function eventHandler() {
				
				// get the globe bounds (method 1)
				var globeBounds = ge.getView().getViewportGlobeBounds(),
					zoom_check = current_zoom ? current_zoom :400000;

				if (globeBounds) {
					console.log("Globe mai aa gya");
					var poly = [
							{lat: globeBounds.getNorth(), lon: globeBounds.getWest()},
							{lat: globeBounds.getNorth(), lon: globeBounds.getEast()},
							{lat: globeBounds.getSouth(), lon: globeBounds.getEast()},
							{lat: globeBounds.getSouth(), lon: globeBounds.getWest()},
							{lat: globeBounds.getNorth(), lon: globeBounds.getWest()}]
					var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);

					if(lookAt.getRange() <= 600540) {

						// earth_self.clearLabelElements();
						var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);
						if(Math.floor(lookAt.getRange()/100000) === 4) {
							
							var states_with_bounds = state_lat_lon_db.where(function(obj) {
								return isPointInPoly(poly, {lat: obj.lat, lon: obj.lon});
							});

							if(Math.floor(lookAt.getRange()/100000) === 4 && Math.floor(lastZoomLevel/100000) === 4 && arraysEqual(lastStateBounds, states_with_bounds)) {
								return ;
							}
							var states_array = [];
							lastStateBounds= states_with_bounds;

		            		// Hide State Labels which are in current bounds
		            		for(var i=states_with_bounds.length;i--;) {
		            			if(state_wise_device_labels[states_with_bounds[i].name]) {
		            				states_array.push(states_with_bounds[i].name);
			            			if(!(state_wise_device_labels[states_with_bounds[i].name].isHidden_)) {
				            			// Hide Label
										state_wise_device_labels[states_with_bounds[i].name].setVisibility(false);
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

								// If any data exists
			            		if(data_to_plot.length > 0) {
			            			// if(lastZoomLevel > lookAt.getRange()) {
					            		/*Clear all everything from map*/
									$.grep(allMarkersArray_earth,function(marker) {
										marker.setVisibility(false);
										// lastStateBounds
									});
									// Reset Variables
									allMarkersArray_earth = [];
									main_devices_data_earth = [];
									currentlyPlottedDevices = [];
									allMarkersObject_earth= {
										'base_station': {},
										'path': {},
										'sub_station': {},
										'sector_device': {},
										'sector_polygon': {}
									};
			            			// }

									main_devices_data_earth = data_to_plot;
									
									var inBoundData = earth_self.getNewBoundsDevices();

									currentlyPlottedDevices = inBoundData;


									// Call function to plot devices on gmap
									earth_self.plotDevices_earth(inBoundData,"base_station");

									/*Show The loading Icon*/
									$("#loadingIcon").hide();

									/*Disable the refresh button*/
									$("#resetFilters").button("complete");
			            		}

			            		// Show points line if exist
			            		for(key in line_data_obj) {
			            			line_data_obj[key].setVisibility(true);
			            		}
							}
							statesDataShown = states_with_bounds;
						} else {

	    					earth_self.showLinesInBounds();
							earth_self.showSubStaionsInBounds();
							earth_self.showBaseStaionsInBounds();
							earth_self.showSectorDevicesInBounds();
							earth_self.showSectorPolygonInBounds();

						}
						

	            		// Start performance calling after 1.5 Second
						// setTimeout(function() {
				   	 	// 				var bs_id_list = getMarkerInCurrentBound();
					   //          	if(bs_id_list.length > 0 && isCallCompleted == 1) {
					   //          		if(recallPerf != "") {
					   //          			clearTimeout(recallPerf);
					   //          			recallPerf = "";
					   //          		}
					   //          		gisPerformanceClass.start(bs_id_list);
					   //          	}
				 	   //         	},500);
	            		
					} else {
						earth_self.showLabelElements();
						// for (var x = 0; x < labelsArray.length; x++) {
	                    //     var move_listener_obj = labelsArray[x].moveListener_;
	                    //     if (move_listener_obj) {
	                    //         var keys_array = Object.keys(move_listener_obj);
	                    //         for(var z=0;z<keys_array.length;z++) {
	                    //         	var label_marker = move_listener_obj[keys_array[z]];
	                    //             if(typeof label_marker === 'object') {
	                    //                if((label_marker && label_marker["filter_data"]["bs_name"]) && (label_marker && label_marker["filter_data"]["sector_name"])) {
	                    //                		labelsArray[x].close();
	                    //                }
	                    //             }
	                    //         }
	                    //     }
	                    // }

	                    // // Reset labels array 
	                    // labelsArray = [];

						/*Clear all everything from map*/
						$.grep(allMarkersArray_earth,function(marker) {
							marker.isActive= 0;
							marker.setVisibility(false);
						});
						// Reset Variables
						allMarkersArray_earth = [];
						main_devices_data_earth = [];
						plottedBsIds = [];
						currentlyPlottedDevices = [];
						allMarkersObject_earth= {
							'base_station': {},
							'path': {},
							'sub_station': {},
							'sector_device': {},
							'sector_polygon': {}
						};

	                    // Reset labels array 
	                    labelsArray = [];


						var states_with_bounds = state_lat_lon_db.where(function(obj) {
							return isPointInPoly(poly, {lat: obj.lat, lon: obj.lon});
	            		});
						for(var i=states_with_bounds.length;i--;) {
							if(state_wise_device_labels[states_with_bounds[i].name]) {
								if(state_wise_device_labels[states_with_bounds[i].name].isHidden_) {
									state_wise_device_labels[states_with_bounds[i].name].setVisibility(true);
								}
							}
						}

						state_lat_lon_db.where(function(obj) {
							if(state_wise_device_labels[obj.name]) {
								state_wise_device_labels[obj.name].setVisibility(true);return ;
							}
						});

						// Hide points line if exist
	            		for(key in line_data_obj) {
	            			line_data_obj[key].setVisibility(false);
	            		}
		            }

		            // Save last Zoom Value
		            lastZoomLevel = lookAt.getRange();
				}
			}
			timer = setTimeout(eventHandler, 100);
		}
		);

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

		/*Call get devices function*/
		earth_self.getDevicesData_earth();

		/*Create performance lib instance*/
		gisPerformanceClass= new GisPerformance();
	};

	/**
	 * This function handles the failure callback of google earth creation function
	 * @method earthFailureCallback
	 * @param errorCode {Object}, It is the JSON object returned from google earth create instance function when google earth creation was not successful or failed.
	 */
	this.earthFailureCallback = function(errorCode) {
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

		// var get_param_filter = "";
		// /*If any advance filters are applied then pass the advance filer with API call else pass blank array*/
		// if(appliedAdvFilter.length > 0) {
		// 	get_param_filter = JSON.stringify(appliedAdvFilter);
		// } else {
		// 	get_param_filter = "";
		// }

		if(counter > 0 || counter == -999) {

			/*Ajax call not completed yet*/
			isCallCompleted = 0;

			/*To Enable The Cross Domain Request*/
			$.support.cors = true;

			/*Ajax call to the API*/
			$.ajax({
				url : base_url+"/"+"device/stats/?total_count="+devicesCount+"&page_number="+hitCounter,
				// url : base_url+"/"+"static/new_format.json",
				type : "GET",
				dataType : "json",
				/*If data fetched successful*/
				success : function(result) {

					if(result.success == 1) {

						if(result.data.objects != null) {

							hitCounter = hitCounter + 1;
							/*First call case*/
							// if(devicesObject_earth.data == undefined) {

							// 	/*Save the result json to the global variable for global access*/
							devicesObject_earth = result;
							// 	This will update if any filer is applied
							// 	devices_earth = devicesObject_earth.data.objects.children;

							// } else {

							// 	devices_earth = devices_earth.concat(result.data.objects.children);
							// }

							main_devices_data_earth = main_devices_data_earth.concat(result.data.objects.children);;
							data_for_filters_earth = main_devices_data_earth;

							if(devicesObject_earth.data.objects.children.length > 0) {

								/*Update the device count with the received data*/
								if(devicesCount == 0) {
									devicesCount = devicesObject_earth.data.meta.total_count;
								}

								/*Update showLimit with the received data*/
								showLimit = result.data.meta.limit;

								if(counter == -999) {

									counter = Math.ceil(devicesCount / showLimit);
								}


								/*Check that any advance filter is applied or not*/
								// if(appliedAdvFilter.length <= 0) {

								// 	/*applied basic filters count*/
								// 	var appliedFilterLength_earth = Object.keys(appliedFilterObj_earth).length;

								// 	/*Check that any basic filter is applied or not*/
								// 	if(appliedFilterLength_earth > 0) {
								// 		/*If any filter is applied then plot the fetch data as per the filters*/
								// 		earth_self.applyFilter_earth(appliedFilterObj_earth);
								// 	} else {
									
								// 		/*Call the plotDevices_earth to show the markers on the map*/
								// 		earth_self.plotDevices_earth(result.data.objects.children,"base_station");
										
								// 	}

								// } else {
        //                             /*Call the plotDevices_earth to show the markers on the map*/
								// 	earth_self.plotDevices_earth(result.data.objects.children,"base_station");
        //                         }

        						earth_self.showStateWiseData_earth(result.data.objects.children);

                                /*Decrement the counter*/
								counter = counter - 1;

								/*Call the function after 3 sec. for lazyloading*/
								setTimeout(function() {
									earth_self.getDevicesData_earth();
								},10);
								
							} else {
								isCallCompleted = 1;
								// earth_self.plotDevices_earth([],"base_station");
								earth_self.showStateWiseData_earth([],"base_station");

								disableAdvanceButton('no');

								/*Recall the server after particular timeout if system is not freezed*/
						        /*Hide The loading Icon*/
								$("#loadingIcon").hide();

								// earth_self.clearLabelElements();

								/*Enable the refresh button*/
								$("#resetFilters").button("complete");

								setTimeout(function(e){
									earth_self.recallServer_earth();
								},21600000);
							}							

						} else {
							
							isCallCompleted = 1;
							disableAdvanceButton('no');
							// earth_self.plotDevices_earth([],"base_station");
							earth_self.showStateWiseData_earth([],"base_station");

							get_page_status();
							/*Hide The loading Icon*/
							$("#loadingIcon").hide();

							// earth_self.clearLabelElements();

							/*Enable the refresh button*/
							$("#resetFilters").button("complete");

							setTimeout(function(e){
								earth_self.recallServer_earth();
							},21600000);
						}

					} else {

						isCallCompleted = 1;
						disableAdvanceButton('no');
						// earth_self.plotDevices_earth([],"base_station");
						earth_self.showStateWiseData_earth([],"base_station");

						get_page_status();
						disableAdvanceButton('no, enable it.');

						// earth_self.clearLabelElements();

						/*Recall the server after particular timeout if system is not freezed*/
						setTimeout(function(e) {
							earth_self.recallServer_earth();
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

			        disableAdvanceButton('no');
					/*Hide The loading Icon*/
					$("#loadingIcon").hide();

					/*Enable the refresh button*/
					$("#resetFilters").button("complete");
					/*Recall the server after particular timeout if system is not freezed*/
					setTimeout(function(e){
						earth_self.recallServer_earth();
					},21600000);
				}
			});
		} else {

			/*Ajax call not completed yet*/
			isCallCompleted = 1;
			disableAdvanceButton('no');
			// earth_self.plotDevices_earth([],"base_station");
			earth_self.showStateWiseData_earth([],"base_station");

			disableAdvanceButton('no, enable it.');
			get_page_status();

			// earth_self.clearLabelElements();

			/*Recall the server after particular timeout if system is not freezed*/
			setTimeout(function(e){
				earth_self.recallServer_earth();
			},21600000);
		}
	};



var state_wise_device_label_text= {};
	/**
     * This function show counter of state wise data on Earth
     * @method showStateWiseData_earth
     * @param dataset {Object} In case of BS, it is the devies object array & for SS it contains BS marker object with SS & sector info
	 */
	this.showStateWiseData_earth = function(dataset) {
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
				state_click_event = "onClick='earth_self.state_label_clicked("+state_param+")'";

			// If state is not null
			if(state) {
				if(state_wise_device_counters[state]) {
					state_wise_device_counters[state] += 1;
					if(state_lat_lon_obj) {
						// Update the content of state counter label as per devices count
						state_wise_device_labels[state].setName(String(state_wise_device_counters[state]));
						// state_wise_device_label_text[state].setName(String(state_wise_device_counters[state]));
					}
				} else {
					state_wise_device_counters[state] = 1;
					if(state_lat_lon_obj) {	  
			   			//Create the placemark
			   			var device_counter_label = ge.createPlacemark('');
			   			device_counter_label.setName(String(state_wise_device_counters[state]));

			   			var clusterIcon = ge.createIcon('');
						clusterIcon.setHref(base_url+"/static/js/OpenLayers/img/state_cluster.png");
						var clusterIconStyle = ge.createStyle(''); //create a new style
						clusterIconStyle.getIconStyle().setIcon(clusterIcon); //apply the icon to the style
						device_counter_label.setStyleSelector(clusterIconStyle); //apply the style to the placemark
						clusterIconStyle.getIconStyle().setScale(5.0);

			   			//Set the placemark location;
			   			var clusterPoint = ge.createPoint('');
			   			clusterPoint.setLatitude(+state_lat_lon_obj.lat);
			   			clusterPoint.setLongitude(+state_lat_lon_obj.lon);
			   			device_counter_label.setGeometry(clusterPoint);

						ge.getFeatures().appendChild(device_counter_label);

						(function(state_param) {
							google.earth.addEventListener(device_counter_label, 'click', function(event) {
			   					event.preventDefault();
								earth_self.state_label_clicked(state_param);
				   			});

						}(state_param));

						// (function() {
				  //       	// Create the placemark.
						// 	var device_counter_text = ge.createPlacemark('');
						// 	device_counter_text.setName(String(state_wise_device_counters[state]));

						// 	// Define a custom icon.
						// 	var icon = ge.createIcon('');
						// 	icon.setHref(base_url+'/static/img/icons/1x1.png');
						// 	var style = ge.createStyle(''); //create a new style
						// 	style.getIconStyle().setIcon(icon); //apply the icon to the style
						// 	device_counter_text.setStyleSelector(style); //apply the style to the placemark
						// 	style.getIconStyle().setScale(0);

						// 	// Set the placemark's location.  
						// 	var point = ge.createPoint('');
						// 	var nLat = ((+state_lat_lon_obj.lat*1000)-0)/1000;
						// 	var nLng = ((+state_lat_lon_obj.lon*1000)-0)/1000;
						// 	point.setLatitude(nLat);
						// 	point.setLongitude(nLng);
						// 	device_counter_text.setGeometry(point);

						// 	device_counter_text.placemarkerType = 'label_icon';

						// 	// Add the placemark to Earth.
						// 	ge.getFeatures().appendChild(device_counter_text);

					 //        state_wise_device_label_text[state] = device_counter_text;

				  //       }());
					}
			        state_wise_device_labels[state] = device_counter_label;
				}
			} else {
				var lat = current_bs.data.lat,
					lon = current_bs.data.lon,
					allStateBoundries = state_boundries_db.data;
					// bs_point = new google.maps.LatLng(lat,lon);

				// Loop to find that the lat lon of BS lies in which state.
				for(var y=allStateBoundries.length;y--;) {
					var current_state_boundries = allStateBoundries[y].boundries,
						current_state_name = allStateBoundries[y].name,
						latLonArray = [];;
					if(current_state_boundries.length > 0) {
						for(var z=current_state_boundries.length;z--;) {
							latLonArray.push({lat: current_state_boundries[z].lat, lon: current_state_boundries[z].lon});
						}
						// var state_polygon = new google.maps.Polygon({"path" : latLonArray});
						if(isPointInPoly(latLonArray, {lat: lat, lon: lon})) {
							//Update json with state name
							dataset[i]['data']['state'] = current_state_name;
							state = current_state_name;
							state_lat_lon_obj = state_lat_lon_db.find({"name" : state}).length > 0 ? state_lat_lon_db.find({"name" : state})[0] : false;
							state_param = state_lat_lon_obj ? JSON.stringify(state_lat_lon_obj) : false;

							var new_lat_lon_obj = state_lat_lon_db.where(function(obj) {
								return obj.name === current_state_name;
							});

							if(state_wise_device_counters[current_state_name]) {
								state_wise_device_counters[current_state_name] += 1;
								state_wise_device_labels[current_state_name].setName(String(state_wise_device_counters[state]));
								// state_wise_device_label_text[state].setName(String(state_wise_device_counters[state]));
							} else {
								state_wise_device_counters[current_state_name] = 1;
							
						        //Create the placemark
					   			var device_counter_label = ge.createPlacemark('');
					   			device_counter_label.setName(String(state_wise_device_counters[state]));

					   			var clusterIcon = ge.createIcon('');
								clusterIcon.setHref(base_url+"/static/js/OpenLayers/img/state_cluster.png");
								var clusterIconStyle = ge.createStyle(''); //create a new style
								clusterIconStyle.getIconStyle().setIcon(clusterIcon); //apply the icon to the style
								device_counter_label.setStyleSelector(clusterIconStyle); //apply the style to the placemark
								clusterIconStyle.getIconStyle().setScale(5.0);


					   			//Set the placemark location;
					   			var clusterPoint = ge.createPoint('');
					   			clusterPoint.setLatitude(new_lat_lon_obj[0].lat);
					   			clusterPoint.setLongitude(new_lat_lon_obj[0].lon);

					   			device_counter_label.setGeometry(clusterPoint);

					   			(function(state_param) {
									google.earth.addEventListener(device_counter_label, 'click', function(event) {
					   					event.preventDefault();
										earth_self.state_label_clicked(state_param);
						   			});

								}(state_param));

								//Add the placemark to Earth.
								ge.getFeatures().appendChild(device_counter_label);

								state_wise_device_labels[current_state_name] = device_counter_label;

								// (function() {
							 //        // Create the placemark.
								// 	var device_counter_text = ge.createPlacemark('');
								// 	device_counter_text.setName(String(state_wise_device_counters[state]));

								// 	// Define a custom icon.
								// 	var icon = ge.createIcon('');
								// 	icon.setHref(base_url+'/static/img/icons/1x1.png');
								// 	var style = ge.createStyle(''); //create a new style
								// 	style.getIconStyle().setIcon(icon); //apply the icon to the style
								// 	device_counter_text.setStyleSelector(style); //apply the style to the placemark
								// 	style.getIconStyle().setScale(0);

								// 	// Set the placemark's location.  
								// 	var point = ge.createPoint('');
								// 	var nLat = ((+state_lat_lon_obj.lat*1000)-0)/1000;
								// 	var nLng = ((+state_lat_lon_obj.lon*1000)-0)/1000;
								// 	point.setLatitude(nLat);
								// 	point.setLongitude(nLng);
								// 	device_counter_text.setGeometry(point);

								// 	device_counter_text.placemarkerType = 'label_icon';

								// 	// Add the placemark to Earth.
								// 	ge.getFeatures().appendChild(device_counter_text);

							 //        state_wise_device_label_text[state] = device_counter_text;

						  //       }());
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
					state_wise_device_labels[state].setName(String(state_wise_device_counters[state]));
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
	 * This function clear the state counter & labels
	 * @method clearStateCounters
	 */
	this.clearStateCounters = function() {
		for(key in state_wise_device_counters) {
			state_wise_device_counters[key] = 0;
			if(state_wise_device_labels[key]) {
				state_wise_device_labels[key].setVisibility(false);
				// var markerLabel= ge.getElementById(key);
				// ge.getFeatures().removeChild(markerLabel);
			}
		}
		state_wise_device_counters= {};
		state_wise_device_labels= {};
	};


	/**
	 * This function trigger when state label is clicked & loads the state wise data.
	 * @method state_label_clicked
	 * @param state_obj, It contains the name of state which is clicked.
	 */
	this.state_label_clicked = function(state_obj) {
		if(isExportDataActive == 0) {
			var clicked_state = state_obj ? JSON.parse(state_obj).name : "",
				selected_state_devices = [];

			if(clicked_state) {

				// Get the current view.
				var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);

				// Pan to state latitude and longitude values.
				lookAt.setLatitude(JSON.parse(state_obj).lat);
				lookAt.setLongitude(JSON.parse(state_obj).lon);

				// Update the view in Google Earth.
				ge.getView().setAbstractView(lookAt);

				// Zoom out to 8times the current range.
				lookAt.setRange(420000);		

		
				ge.getView().setAbstractView(lookAt);

				current_zoom = lookAt.getRange();
	
				// Hide Clicked state Label
				if(!(state_wise_device_labels[clicked_state].isHidden_)) {
        			// Hide Label
					state_wise_device_labels[clicked_state].setVisibility(false);
					// state_wise_device_labels[clicked_state].hide();
    			}
			}
		}
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

			var current_device_set = dataset[i];
			var globeBounds = ge.getView().getViewportGlobeBounds();

			if (globeBounds) {
				var poly = [
						{lat: globeBounds.getNorth(), lon: globeBounds.getWest()},
						{lat: globeBounds.getNorth(), lon: globeBounds.getEast()},
						{lat: globeBounds.getSouth(), lon: globeBounds.getEast()},
						{lat: globeBounds.getSouth(), lon: globeBounds.getWest()},
						{lat: globeBounds.getNorth(), lon: globeBounds.getWest()}]

				var isDeviceInBound =  isPointInPoly(poly, {lat: current_device_set.data.lat, lon: current_device_set.data.lon});
				if(isDeviceInBound) {
					newInBoundDevices.push(current_device_set);
					plottedBsIds.push(current_device_set.id);
				}
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

		for(var i=main_devices_data_earth.length;i--;) {
			var current_device_set = main_devices_data_earth[i];
			// if(plottedBsIds.indexOf(current_device_set.id) === -1) {

				var globeBounds = ge.getView().getViewportGlobeBounds();

				if (globeBounds) {
					var poly = [
							{lat: globeBounds.getNorth(), lon: globeBounds.getWest()},
							{lat: globeBounds.getNorth(), lon: globeBounds.getEast()},
							{lat: globeBounds.getSouth(), lon: globeBounds.getEast()},
							{lat: globeBounds.getSouth(), lon: globeBounds.getWest()},
							{lat: globeBounds.getNorth(), lon: globeBounds.getWest()}]

					var isDeviceInBound =  isPointInPoly(poly, {lat: current_device_set.data.lat, lon: current_device_set.data.lon});
					if(isDeviceInBound) {
						newInBoundDevices.push(current_device_set);
						// plottedBsIds.push(current_device_set.id);
					}
				}
			// }
		}
		// Return devices which are in current bounds
		return newInBoundDevices;
	};


	/**
     * This function is used to populate the BS & SS on the google earth
     * @method plotDevices_earth
     * @param devicesList {Object Array}, It is the devices object array
     * @uses gmap_devicePlottingLib
	 */
	this.plotDevices_earth = function(resultantMarkers,station_type) {



		for(var i=0;i<resultantMarkers.length;i++) {
			var bs_marker_icon = base_url+"/static/img/icons/bs.png";

			var bsInfo = {
				map: 'current',
				ptLat: resultantMarkers[i].data.lat,
				ptLon: resultantMarkers[i].data.lon,
				icon: base_url+"/static/img/icons/bs.png",
				oldIcon: base_url+"/static/img/icons/bs.png",
				clusterIcon: base_url+"/static/img/icons/bs.png",
				pointType: "base_station",
				child_ss: resultantMarkers[i].data.param.sector,
				dataset: resultantMarkers[i].data.param.base_station,
				device_name: resultantMarkers[i].data.device_name,
				bsInfo: resultantMarkers[i].data.param.base_station,
				bhInfo: resultantMarkers[i].data.param.backhual,
				bs_name: resultantMarkers[i].name,
				name: resultantMarkers[i].name,
				filter_data: {"bs_name" : resultantMarkers[i].name, "bs_id" : resultantMarkers[i].originalId},
				antenna_height: resultantMarkers[i].data.antenna_height,
				markerType: 'BS',
				isMarkerSpiderfied: false,
				isActive: 1,
				state: resultantMarkers[i].data.state
			};

			// Create BS placemark.
			var bs_marker = earth_self.makePlacemark(bs_marker_icon,resultantMarkers[i].data.lat,resultantMarkers[i].data.lon,'bs_'+resultantMarkers[i].id,bsInfo);

			/*Push BS placemark to bs placemark array*/
			plotted_bs_earth.push(bs_marker);

			masterMarkersObj_earth.push(bs_marker);

			allMarkersObject_earth['base_station']['bs_'+resultantMarkers[i].name] = bs_marker;

			allMarkersArray_earth.push(bs_marker);

			markersMasterObj['BS'][String(resultantMarkers[i].data.lat)+resultantMarkers[i].data.lon]= bs_marker;
			markersMasterObj['BSNamae'][String(resultantMarkers[i].name)]= bs_marker;

			google.earth.addEventListener(bs_marker, 'click', function(event) {
				var content = gmap_self.makeWindowContent(bs_marker);
				$("#infoWindowContainer").html('<iframe allowTransparency="true" style="position:absolute; top:0px; right:0px; width:100%; height:100%;overflow-y:auto; z-index:100;"></iframe>'+content);
				$("#infoWindowContainer").removeClass('hide');
				event.preventDefault();
			});
// console.log(resultantMarkers[i]);
			var sectorsArray = resultantMarkers[i].data.param.sector;
			var deviceIDArray= [];
// console.log(sectorsArray);

    		// $.grep(sectorsArray,function(sector) { 
			for(var j=0;j<sectorsArray.length;j++) {
				

				var lon = resultantMarkers[i].data.lon,
					lat = resultantMarkers[i].data.lat,
					rad = 4,
					azimuth = sectorsArray[j].azimuth_angle,
					beam_width = sectorsArray[j].beam_width,
					sector_color = earth_self.makeRgbaObject(sectorsArray[j].color),
					sectorInfo = {
						map: 'current',
						"info" : sectorsArray[j].info,
						"bs_name" : resultantMarkers[i].name,
						"sector_name" : sectorsArray[j].sector_configured_on,
						"sector_id" : sectorsArray[j].sector_id,
						"device_info" : sectorsArray[j].device_info,
						"technology" : sectorsArray[j].technology,
						"vendor" : sectorsArray[j].vendor
					},
					orientation = $.trim(sectorsArray[j].orientation),
					sector_child = sectorsArray[j].sub_station,
					childSS = JSON.stringify(sectorsArray[j].sub_station),
					device_technology = $.trim(sectorsArray[j].technology),
					orientation = $.trim(sectorsArray[j].orientation),
					sectorRadius = (+sectorsArray[j].radius),
					startEndObj = {},
					startLon = "",
					startLat = "";

				/*If radius is greater than 4 Kms then set it to 4.*/
				if((sectorRadius != null) && (sectorRadius > 0)) {
					rad = +sectorsArray[j].radius;
				}
				
				/*Call createSectorData function to get the points array to plot the sector on google earth.*/
				networkMapInstance.createSectorData(lat,lon,rad,azimuth,beam_width,orientation,function(pointsArray) {
					
					var halfPt = Math.floor(pointsArray.length / (+2));

					/*In case of PMP & WIMAX*/
					if($.trim(sectorsArray[j].technology) != "PTP" && $.trim(sectorsArray[j].technology) != "P2P") {

						/*Plot sector on google earth with the retrived points*/
						earth_self.plotSector_earth(lat,lon,pointsArray,sectorInfo,sector_color,childSS,$.trim(sectorsArray[j].technology),orientation,rad,azimuth,beam_width);

						startEndObj["startLat"] = pointsArray[halfPt].lat;
						startEndObj["startLon"] = pointsArray[halfPt].lon;

						startEndObj["sectorLat"] = pointsArray[halfPt].lat;
						startEndObj["sectorLon"] = pointsArray[halfPt].lon;
					} else {
						startEndObj["startLat"] = lat;
		    			startEndObj["startLon"] = lon;
		    			
		    			startEndObj["sectorLat"] = lat;
						startEndObj["sectorLon"] = lon;
					}
				});

				if($.trim(sectorsArray[j].technology.toLowerCase()) == "ptp" || $.trim(sectorsArray[j].technology.toLowerCase()) == "p2p") {

					if(deviceIDArray.indexOf(sectorsArray[j]['device_info'][1]['value']) === -1) {
						var sectorMarkerIcon = base_url+"/"+sectorsArray[j].markerUrl;
						var sectorInfo = {
							map: 'current',
							ptLat: lat,
							ptLon: lon,
							icon: base_url+"/"+sectorsArray[j].markerUrl,
							oldIcon: base_url+"/"+sectorsArray[j].markerUrl,
							clusterIcon: base_url+"/"+sectorsArray[j].markerUrl,
							pointType: 'sector_Marker',
							technology: sectorsArray[j].technology,
							vendor: sectorsArray[j].vendor,
							deviceExtraInfo: sectorsArray[j].info,
							deviceInfo: sectorsArray[j].device_info,
							poll_info: [],
							sectorName: sectorsArray[j].sector_configured_on,
							device_name: sectorsArray[j].sector_configured_on_device,
							name: sectorsArray[j].sector_configured_on_device,
							filter_data: {"bs_name" : resultantMarkers[i].name, "sector_name" : sectorsArray[j].sector_configured_on, "bs_id" : resultantMarkers[i].originalId, "sector_id" : sectorsArray[j].sector_id},
							sector_lat: startEndObj["startLat"],
							sector_lon: startEndObj["startLon"],
							hasPerf: 0,
							antenna_height: sectorsArray[j].antenna_height,
							isActive: 1,
							state: resultantMarkers[i].data.state
						};

						var sect_height = sectorsArray[j].antenna_height;
						// Create Sector placemark.
						var sector_marker = earth_self.makePlacemark(sectorMarkerIcon,resultantMarkers[i].data.lat,resultantMarkers[i].data.lon,sectorsArray[j].sector_configured_on+"_"+j,sectorInfo);
						/*Push Sector placemark to sector placemark array*/
						plotted_sector_earth.push(sector_marker);

						allMarkersArray_earth.push(sector_marker);

						google.earth.addEventListener(sector_marker, 'click', function(event) {
							var content = gmap_self.makeWindowContent(sector_marker);
							$("#infoWindowContainer").html('<iframe allowTransparency="true" style="position:absolute; top:0px; right:0px; width:100%; height:100%;overflow-y:auto; z-index:100;"></iframe>'+content);
							$("#infoWindowContainer").removeClass('hide');
							event.preventDefault();
						});

						if(sectorMarkerConfiguredOn_earth.indexOf(sectorsArray[j].sector_configured_on) == -1) {

							sector_MarkersArray.push(sector_marker);
							// allMarkersArray_earth.push(sector_marker);

							/*Push Sector marker to pollableDevices array*/
							pollableDevices.push(sector_marker);
							
							allMarkersObject_earth['sector_device']['sector_'+sectorsArray[j].sector_configured_on] = sector_marker;


							sectorMarkerConfiguredOn_earth.push(sectorsArray[j].sector_configured_on);
							if(sectorMarkersMasterObj[resultantMarkers[i].name]) {
								sectorMarkersMasterObj[resultantMarkers[i].name].push(sector_marker)
							} else {
								sectorMarkersMasterObj[resultantMarkers[i].name]= [];
								sectorMarkersMasterObj[resultantMarkers[i].name].push(sector_marker)
							}	
						}

						/*End of Create Sector Marker*/
						
						deviceIDArray.push(sectorsArray[j]['device_info'][1]['value']);
					}
				}

				for(var k=0;k<sectorsArray[j].sub_station.length;k++) {
					
					var ssDataObj = sectorsArray[j].sub_station[k];
					
					// var ssMarkerIcon = base_url+"/"+ssDataObj.markerUrl;
					var ssMarkerIcon = base_url+"/"+ssDataObj.data.markerUrl;
					var ssInfo= {
						map: 'current',
						ptLat: ssDataObj.data.lat,
						ptLon:	ssDataObj.data.lon,
						technology: ssDataObj.data.technology,
						icon: ssMarkerIcon,
						oldIcon: ssMarkerIcon,
						clusterIcon: ssMarkerIcon,
						pointType: "sub_station",
						dataset: ssDataObj.data.param.sub_station,
						bhInfo: [],
						poll_info: [],
						antenna_height: ssDataObj.data.antenna_height,
						name: ssDataObj.name,
						bs_name: resultantMarkers[i].name,
						bs_sector_device: sectorsArray[j].sector_configured_on_device,
						filter_data: {"bs_name" : resultantMarkers[i].name, "sector_name" : sectorsArray[j].sector_configured_on, "ss_name" : ssDataObj.name, "bs_id" : resultantMarkers[i].originalId, "sector_id" : sectorsArray[j].sector_id},
						device_name: ssDataObj.device_name,
						ss_ip: ssDataObj.data.substation_device_ip_address,
						sector_ip: sectorsArray[j].sector_configured_on,
						hasPerf: 0,
						isActive: 1,
						state: resultantMarkers[i].data.state
					};

					if(ssDataObj.data.lat && ssDataObj.data.lon) {
						// Create SS placemark.
						var ss_marker = earth_self.makePlacemark(ssMarkerIcon,ssDataObj.data.lat,ssDataObj.data.lon,'ss_'+ssDataObj.id,ssInfo);

						google.earth.addEventListener(ss_marker, 'click', function(event) {
							var content = gmap_self.makeWindowContent(ss_marker);
							$("#infoWindowContainer").html('<iframe allowTransparency="true" style="position:absolute; top:0px; right:0px; width:100%; height:100%;overflow-y:auto; z-index:100;"></iframe>'+content);
							$("#infoWindowContainer").removeClass('hide');
							event.preventDefault();
						});

						markersMasterObj['SS'][String(ssDataObj.data.lat)+ ssDataObj.data.lon]= ss_marker;
					    markersMasterObj['SSNamae'][String(ssDataObj.device_name)]= ss_marker;

					    /*Add the master marker to the global master markers array*/
				    	masterMarkersObj_earth.push(ss_marker);

				    	allMarkersObject_earth['sub_station']['ss_'+ssDataObj.name] = ss_marker;

				    	allMarkersArray_earth.push(ss_marker);

					    /*Push SS marker to pollableDevices array*/
						pollableDevices.push(ss_marker)

					    /*Push All SS Lat & Lon*/
			    	    ssLatArray.push(ssDataObj.data.lat);
						ssLonArray.push(ssDataObj.data.lon);

						var ss_info = {
								"info" : ssDataObj.data.param.sub_station,
								"antenna_height" : ssDataObj.data.antenna_height
							},
							base_info = {
								"info" : resultantMarkers[i].data.param.base_station,
								"antenna_height" : resultantMarkers[i].data.antenna_height
							};

						startEndObj["nearEndLat"] = resultantMarkers[i].data.lat;
						startEndObj["nearEndLon"] = resultantMarkers[i].data.lon;

					    startEndObj["endLat"] = ssDataObj.data.lat;
			    		startEndObj["endLon"] = ssDataObj.data.lon;

			    		/*Sub station info Object*/
			    		// ss_info["info"] = ssDataObj.data.param.sub_station;
			    		// ss_info["antenna_height"] = ssDataObj.data.antenna_height;

			    		/*Link color object*/
			    		linkColor = ssDataObj.data.link_color;


						/*Push SS placemark to sector placemark array*/
						plotted_ss_earth.push(ss_marker);

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
							var linkLinePlacemark = earth_self.createLink_earth(startEndObj,linkColor,bs_info,ss_info,sect_height,sectorsArray[j].sector_configured_on,ssDataObj.name,resultantMarkers[i].name,resultantMarkers[i].id,sectorsArray[j].sector_id);
							allMarkersArray_earth.push(linkLinePlacemark);
							plottedLinks_earth.push(linkLinePlacemark);

							ssLinkArray.push(linkLinePlacemark);
				    		ssLinkArray_filtered = ssLinkArray;

				    		allMarkersObject_earth['path']['line_'+ssDataObj.name] = linkLinePlacemark;

						}
					}
				}
    		}

    		if(i=== resultantMarkers.length-1) {
    				/*Hide The loading Icon*/
					$("#loadingIcon").hide();

					/*Enable the refresh button*/
					$("#resetFilters").button("complete");
    		}
		}/*End of devices list for loop.*/

		if(isCallCompleted == 1) {

			if(isFirstTime == 1) {
				/*Load data for basic filters*/
				var basic_filter_data = prepare_data_for_filter();
				networkMapInstance.getBasicFilters(basic_filter_data);
			}

		
		}
	};

	/**
	 * This function create a placemark on given lat lon
	 * @method makePlacemark.
	 * @param iconHref {String}, It contains the url of placemark icon.
	 * @param latitude {Nuber}, It contains the lattitude point for placemark.
	 * @param longitude {Nuber}, It contains the longitude point for placemark.
	 * @param placemarkId {String}, It contains the unique id for placemark.
	 * @param description {object}, It contains the content which shown on click of placemark.
	 */
	this.makePlacemark = function(iconHref, latitude, longitude, placemarkId, description) {

		marker_count++;

		placemark = "";
		placemark = ge.createPlacemark(placemarkId+"_"+marker_count);
		// placemark.setDescription(description);
		icon = ge.createIcon('');
		(function(iconUrl) {
			icon.setHref(iconUrl);
		}(iconHref));
		
		
		var style = ge.createStyle(''); //create a new style
		style.getIconStyle().setIcon(icon); //apply the icon to the style
		// style.getIconStyle().setScale(0.7);
		placemark.setStyleSelector(style); //apply the style to the placemark

		var point = ge.createPoint('');
		// console.log(latitude, longitude);
		point.setLatitude(latitude);
		point.setLongitude(longitude);
		placemark.setGeometry(point);

		for(var key in description) {
			placemark[key] = description[key];
		}

		ge.getFeatures().appendChild(placemark);
		return placemark;
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
	this.createLink_earth = function(startEndObj,linkColor,bs_info,ss_info,sect_height,sector_name,ss_name,bs_name,bs_id,sector_id) {



		var  linkObject = {}, link_path_color = linkColor;
		var ss_info_obj = "", ss_height = 40;

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

        linkObject= {
        	map: 'current',
        	strokeColor: link_path_color,
        	strokeOpacity: 1.0,
        	strokeWeight: 3,
        	pointType: "path",
        	ss_info: ss_info_obj,
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
			// state: resultantMarkers[i].data.state
        };

		// 
		// Create link(line) placemark
		var lineStringPlacemark = ge.createPlacemark('');
		// Create the LineString					
		var lineString = ge.createLineString('');
		lineStringPlacemark.setGeometry(lineString);		
		// Add LineString points					
		lineString.getCoordinates().pushLatLngAlt((+startEndObj.startLat), (+startEndObj.startLon), 0);
		lineString.getCoordinates().pushLatLngAlt((+startEndObj.endLat), (+startEndObj.endLon), 0);					
		// lineStringPlacemark.setDescription(line_windowContent);					
		// Create a style and set width and color of line
		lineStringPlacemark.setStyleSelector(ge.createStyle(''));
		var lineStyle = lineStringPlacemark.getStyleSelector().getLineStyle();					
		lineStyle.setWidth(4);

		/*Color for the link line*/
		var link_color_obj = earth_self.makeRgbaObject(linkColor);

		lineStyle.getColor().setA(200);
		lineStyle.getColor().setB((+link_color_obj.b));
		lineStyle.getColor().setG((+link_color_obj.g));
		lineStyle.getColor().setR((+link_color_obj.r));

		for(var key in linkObject) {
			lineStringPlacemark[key] = linkObject[key];
		}

		google.earth.addEventListener(lineStringPlacemark, 'click', function(event) {
			event.preventDefault();
			/*Call the function to create info window content*/
			var content = gmap_self.makeWindowContent(lineStringPlacemark);
			$("#infoWindowContainer").html('<iframe allowTransparency="true" style="position:absolute; top:0px; right:0px; width:100%; height:100%;overflow-y:auto; z-index:100;"></iframe>'+content);
			$("#infoWindowContainer").removeClass('hide');
		});

		markersMasterObj['Lines'][String(startEndObj.startLat)+ startEndObj.startLon+ startEndObj.endLat+ startEndObj.endLon]= lineStringPlacemark;
		markersMasterObj['LinesName'][String(bs_name)+ ss_name]= lineStringPlacemark;

		// Add the feature to Earth
		ge.getFeatures().appendChild(lineStringPlacemark);

		return lineStringPlacemark;
	};


	/**
	 * This function show connection lines within the bounds
	 * @method showLinesInBounds
	 */
	this.showLinesInBounds = function() {
		/*Loop for polylines*/
		for(var key in allMarkersObject_earth['path']) {
			if(allMarkersObject_earth['path'].hasOwnProperty(key)) {
		    	var current_line = allMarkersObject_earth['path'][key];
		    	if(current_line) {
		    		var earthBounds = getCurrentEarthBoundPolygon();
				    var nearEndVisible = isPointInPoly(earthBounds, {lat: current_line.nearLat, lon: current_line.nearLon}),
				      	farEndVisible = isPointInPoly(earthBounds, {lat: current_line.ss_lat, lon: current_line.ss_lon}),
				      	connected_bs = allMarkersObject_earth['base_station']['bs_'+current_line.filter_data.bs_name],
				      	connected_ss = allMarkersObject_earth['sub_station']['ss_'+current_line.filter_data.ss_name];

				    if((nearEndVisible || farEndVisible) && ((connected_bs && connected_ss) && (connected_bs.isActive != 0 && connected_ss.isActive != 0))) {
				    	// If polyline not shown then show the polyline
				    	if(!current_line.map) {
				    		current_line.setVisibility(true);
				    		current_line.map = 'current';
				    	}
				    } else {
				    	// If polyline shown then hide the polyline
				    	if(current_line.map) {
				    		current_line.setVisibility(false);
				    		current_line.map = '';
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
		for(var key in allMarkersObject_earth['sub_station']) {
			if(allMarkersObject_earth['sub_station'].hasOwnProperty(key)) {
				var earthBounds = getCurrentEarthBoundPolygon();
		    	var ss_marker = allMarkersObject_earth['sub_station'][key],
		    		isMarkerExist = isPointInPoly(earthBounds, {lat: ss_marker.ptLat, lon: ss_marker.ptLon});
	    		if(isMarkerExist) {
	    			if(ss_marker.isActive && +(ss_marker.isActive) === 1) {
			    		// If SS Marker not shown then show the SS Marker
			    		if(!allMarkersObject_earth['sub_station'][key].map) {
			      			allMarkersObject_earth['sub_station'][key].setVisibility(true);
			      			allMarkersObject_earth['sub_station'][key].map = 'current';
			    		}
			    	} else {
			    		// If SS Marker shown then hide the SS Marker
			    		if(allMarkersObject_earth['sub_station'][key].map) {
			      			allMarkersObject_earth['sub_station'][key].setVisibility(false);
			      			allMarkersObject_earth['sub_station'][key].map = '';
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
		for(var key in allMarkersObject_earth['base_station']) {
			if(allMarkersObject_earth['base_station'].hasOwnProperty(key)) {
				var earthBounds = getCurrentEarthBoundPolygon();
		    	var bs_marker = allMarkersObject_earth['base_station'][key],
		      		isMarkerExist = isPointInPoly(earthBounds, {lat: bs_marker.ptLat, lon: bs_marker.ptLon});
	      		if(isMarkerExist) {
			    	if(bs_marker.isActive && +(bs_marker.isActive) === 1) {
			    		// If BS Marker not shown then show the BS Marker
			    		if(!allMarkersObject_earth['base_station'][key].map) {
			      			allMarkersObject_earth['base_station'][key].setVisibility(true);
			      			allMarkersObject_earth['base_station'][key].map = 'current';
			    		}
			        } else {
			        	// If BS Marker shown then hide the BS Marker
			        	if(allMarkersObject_earth['base_station'][key].map) {
			      			allMarkersObject_earth['base_station'][key].setVisibility(false);
			      			allMarkersObject_earth['base_station'][key].map = '';
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
		for(var key in allMarkersObject_earth['sector_device']) {
			if(allMarkersObject_earth['sector_device'].hasOwnProperty(key)) {
				var earthBounds = getCurrentEarthBoundPolygon();
		    	var sector_marker = allMarkersObject_earth['sector_device'][key],
		      		isMarkerExist = isPointInPoly(earthBounds, {lat: sector_marker.ptLat, lon: sector_marker.ptLon});
	      		if(isMarkerExist) {
			    	if(sector_marker.isActive && +(sector_marker.isActive) === 1) {
			    		// If Sector Marker not shown then show the Sector Marker
			    		if(!allMarkersObject_earth['sector_device'][key].map) {
			      			allMarkersObject_earth['sector_device'][key].setVisibility(true);
			      			allMarkersObject_earth['sector_device'][key].map = 'current';
			    		}
			    	} else {
			    		// If Sector Marker shown then hide the Sector Marker
			    		if(allMarkersObject_earth['sector_device'][key].map) {
			    			allMarkersObject_earth['sector_device'][key].setVisibility(false);
			    			allMarkersObject_earth['sector_device'][key].map = '';
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
		for(var key in allMarkersObject_earth['sector_polygon']) {
			if(allMarkersObject_earth['sector_polygon'].hasOwnProperty(key)) {
				var earthBounds = getCurrentEarthBoundPolygon();

		    	var sector_polygon = allMarkersObject_earth['sector_polygon'][key],
		    		isMarkerExist = isPointInPoly(earthBounds, {lat: sector_polygon.ptLat, lon: sector_polygon.ptLon});
	    		if(isMarkerExist) {
	    			if(sector_polygon.isActive && +(sector_polygon.isActive) === 1) {
			    		// If Polygon not shown then show the polygon
			    		if(!allMarkersObject_earth['sector_polygon'][key].map) {

			      			allMarkersObject_earth['sector_polygon'][key].setVisibility(true);
			      			allMarkersObject_earth['sector_polygon'][key].map = 'current';
			    		}
			    	} else {
			    		// If Polygon shown then hide the polygon
			    		if(allMarkersObject_earth['sector_polygon'][key].map) {
			      			allMarkersObject_earth['sector_polygon'][key].setVisibility(false);
			      			allMarkersObject_earth['sector_polygon'][key].map = '';
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
				ssLinkArray[i].setVisibility(false);
			}

		} else {
			for (var i = 0; i < current_lines.length; i++) {
				current_lines[i].setVisibility(true);
			}
		}
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
	this.plotSector_earth = function(lat,lng,pointsArray,sectorInfo,bgColor, sector_child,technology,polarisation,rad,azimuth,beam_width) {

		var sColor = "#000000",
			sWidth = 1;

		if(technology.toLowerCase() == 'pmp') {
			sColor = '#FFFFFF';
			sWidth = 2;
		}

		var halfPt = Math.floor(pointsArray.length / (+2));
		
		var startLat = pointsArray[halfPt].lat;
		var startLon = pointsArray[halfPt].lon;

		var sectorAdditionalInfo = {
			map: 'current',
			ptLat 		     : lat,
			ptLon 		     : lng,
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
			isActive 		 : 1
			// state: resultantMarkers[i].data.state
        };

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

		// infoData["technology"] = device_technology;
		// var halfPt = Math.floor(pointsArray.length / (+2));
		// Create object for Link Line Between Sector & SS
		// infoData["startLat"] = pointsArray[halfPt].lat;
		// infoData["startLon"] = pointsArray[halfPt].lon;
		// infoData["info"] = sectorInfo;

		sector_polygon.setOuterBoundary(polyPoints);
		//Create a style and set width and color of line
		sectorPolygonObj.setStyleSelector(ge.createStyle(''));
		/*Set info window content for sector*/
		// sectorPolygonObj.setDescription(sector_windowContent+"<input type='hidden' name='technology' value=' &-&-& "+JSON.stringify(infoData)+" &-&-& '/><input type='hidden' name='sub_station_data' value=' -|-|-|- "+childSS+" -|-|-|- '/>");

		for(var key in sectorAdditionalInfo) {
			sectorPolygonObj[key] = sectorAdditionalInfo[key];
		}

		allMarkersArray_earth.push(sectorPolygonObj);

		var lineStyle = sectorPolygonObj.getStyleSelector().getLineStyle();

		lineStyle.setWidth(2);
		if(technology.toLowerCase() == 'wimax') {
			lineStyle.getColor().setB(0);
			lineStyle.getColor().setG(0);
			lineStyle.getColor().setR(0);
		} else {			
			lineStyle.getColor().setB(255);
			lineStyle.getColor().setG(255);
			lineStyle.getColor().setR(255);
		}
		lineStyle.getColor().setA(600);

		// Color can also be specified by individual color components.
		var polyColor = sectorPolygonObj.getStyleSelector().getPolyStyle().getColor();
		polyColor.setA(200);
		polyColor.setR((+bgColor.r));
		polyColor.setG((+bgColor.g));
		polyColor.setB((+bgColor.b));

		// Add the placemark to Earth.
		ge.getFeatures().appendChild(sectorPolygonObj);

		google.earth.addEventListener(sectorPolygonObj, 'click', function(event) {
			var content = gmap_self.makeWindowContent(sectorPolygonObj);
			$("#infoWindowContainer").html('<iframe allowTransparency="true" style="position:absolute; top:0px; right:0px; width:100%; height:100%;overflow-y:auto; z-index:100;"></iframe>'+content);
			$("#infoWindowContainer").removeClass('hide');
			event.preventDefault();
		});
	};

	/**
	 * This function show/hide the connection line between BS & SS.
	 * @method showConnectionLines_earth
	 */
	this.showConnectionLines_earth = function() {

		var isLineChecked = $("#showConnLines:checked").length;

		var existing_lines = ssLinkArray_filtered;

		/*Unchecked case*/
		if(isLineChecked == 0) {

			for (var i = 0; i < plottedLinks_earth.length; i++) {
				plottedLinks_earth[i].setVisibility(false);
			}

		} else {
			for (var i = 0; i < plottedLinks_earth.length; i++) {
				plottedLinks_earth[i].setVisibility(true);
			}
		}
	};

	/**
     * This function initialize live polling
     * @method fetchPollingTemplate_earth
     */
    this.fetchPollingTemplate_earth = function() {
		
    	var selected_technology = $("#polling_tech").val();

    	/*Re-Initialize the polling*/
    	networkMapInstance.initLivePolling();

    	if(selected_technology != "") {
    		
    		$("#tech_send").button("loading");

    		/*ajax call for services & datasource*/
    		$.ajax({
    			url : base_url+"/"+"device/ts_templates/?technology="+selected_technology,
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

    					/*Code to draw polygon on click*/
						var polyPlacemark = gexInstance.dom.addPolygonPlacemark([], {
						    style: {
						    	poly: {color: 'black', opacity: 0},
						    	line: { width: 3, color: '#333333' }
						    }
					    });

						gexInstance.edit.drawLineString(polyPlacemark.getGeometry().getOuterBoundary(),{finishCallback : function(e) {
							
						}});

						/*Polygon Drawing End*/
    				}

    			},
    			error : function(err) {
    				console.log(err.statusText);
    			}
			});
		}
	}

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

				masterMarkersObj_earth = [];
				slaveMarkersObj = [];

				/*Populate the map with the filtered markers*/
	 			earth_self.plotDevices_earth(filteredData,"base_station");
	 			// addSubSectorMarkersToOms(filteredData);
	 		}	 		
	 	}	
	};

	this.pointToLatLon = function(lat_lon_str) {
		
		var lat = +lat_lon_str.split(",")[0],
			lng = +lat_lon_str.split(",")[1];

		// Create a new LookAt.
		var lookAt = ge.createLookAt('');

		// Set the position values.
		lookAt.setLatitude(lat);
		lookAt.setLongitude(lng);
		lookAt.setRange(85000.0); //default is 0.0

		// Update the view in Google Earth.
		ge.getView().setAbstractView(lookAt);
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

    this.showLabelElements = function() {
    	var features = ge.getFeatures();
    	// for(var key in state_wise_device_label_text) {
    	// 	state_wise_device_label_text[key].setVisibility(true);
    	// }
    }

    this.clearLabelElements = function() {
    	var features = ge.getFeatures();
    	// for(var key in state_wise_device_label_text) {
    	// 	state_wise_device_label_text[key].setVisibility(false);
    	// }
    }


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