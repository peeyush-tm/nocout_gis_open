/*Map Control Click*/
OpenLayers.Control.Click = OpenLayers.Class(OpenLayers.Control, {
    defaultHandlerOptions: {
        'single': true,
        'double': false,
        'pixelTolerance': 0,
        'stopSingle': false,
        'stopDouble': false
    },

    initialize: function(options) {
        this.handlerOptions = OpenLayers.Util.extend(
            {}, this.defaultHandlerOptions
            );
        OpenLayers.Control.prototype.initialize.apply(
            this, arguments
            );
        this.handler = new OpenLayers.Handler.Click(
            this, {
                'click': this.trigger
            }, this.handlerOptions
            );
    },

    trigger: function(e) {
    	whiteMapClass.unSpiderifyBsMarker();
        
    }
});

/*
Event triggered for Map Idle Condition. [Whenever Map is Zoomed, Panned or something else]
 */
var lastZoomLevel = 1;
WhiteMapClass.prototype.mapIdleCondition = function() {
	
	setTimeout(function() {
    	if(isDebug) {
			console.log("Google Map Idle Event");
			console.log("Google Map Idle Event Start Time :- "+ new Date().toLocaleString());
		}
		// Save current zoom value in global variable
    	current_zoom = ccpl_map.getZoom();
    	/* When zoom level is greater than 8 show lines */
    	if(ccpl_map.getZoom() >= whiteMapSettings.zoomLevelAtWhichStateClusterExpands) {
    		if(ccpl_map.getZoom() < 8 || searchResultData.length > 0) {

    			var states_with_bounds = state_lat_lon_db.where(function(obj) {
    				return whiteMapClass.checkIfPointLiesInside({lat: obj.lat, lon: obj.lon});
        		});

        		var states_array = [];

        		// Hide State Labels which are in current bounds
        		for(var i=states_with_bounds.length;i--;) {
        			if(state_wise_device_labels[states_with_bounds[i].name]) {
        				states_array.push(states_with_bounds[i].name);
        				state_wise_device_labels[states_with_bounds[i].name].attributes.display = 'none';
        				ccpl_map.getLayersByName("States")[0].redraw();
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

        		var inBoundData = [];
        		
        		// If any data exists
        		if(data_to_plot.length > 0) {

        			/**
					 * If anything searched n user is on zoom level 8 then reset 
					   currentlyPlottedDevices array for removing duplicacy.
        			 */
        			if(ccpl_map.getZoom() == 11 && searchResultData.length > 0) {
        				// Reset currentlyPlottedDevices array
        				currentlyPlottedDevices = [];
    				}

    				main_devices_data_wmap = data_to_plot;

        			if(currentlyPlottedDevices.length === 0) {
        				ccpl_map.getLayersByName('Markers')[0].strategies[0].deactivate();
	            		/*Clear all everything from map*/
						$.grep(allMarkersArray_wmap,function(marker) {
							var markerLayer = marker.layer ? marker.layer : marker.layerReference;
							marker.isActive = 0;
							marker.style.display = 'none';
							markerLayer.redraw();
						});
						ccpl_map.getLayersByName('Markers')[0].strategies[0].activate();
						// Reset Variables
						allMarkersArray_wmap = [];
						main_devices_data_wmap = [];
						currentlyPlottedDevices = [];
						allMarkersObject_wmap= {
							'base_station': {},
							'path': {},
							'sub_station': {},
							'sector_device': {},
							'sector_polygon': {}
						};
						
						inBoundData = gmap_self.getInBoundDevices(data_to_plot);
						// Assign currently plotted devices to global array.
						currentlyPlottedDevices = inBoundData;
        			} else {
        				inBoundData = gmap_self.getNewBoundsDevices();
    					// Update currently plotted devices global array.
        				currentlyPlottedDevices = currentlyPlottedDevices.concat(inBoundData);
        			}

        			// Call function to plot devices on gmap
					whiteMapClass.plotDevices_wmaps(inBoundData,"base_station");
					// ccpl_map.getLayersByName('Markers')[0].refresh({forces:true});
					// ccpl_map.getLayersByName('Markers')[0].strategies[0].recluster();

					if(searchResultData.length == 0 || ccpl_map.getZoom() === 8) {
						var polylines = allMarkersObject_wmap['path'],
							polygons = allMarkersObject_wmap['sector_polygon'];

						// Hide polylines if shown
						for(key in polylines) {
							var current_line = polylines[key];
							// If shown
							if(current_line.map) {
								hideOpenLayerFeature(current_line);
								// var markerLayer = current_line.layerReference;
								// current_line.style.display = 'none';
								// current_line.map = '';
								// markerLayer.redraw();
							}
						}
						// alert();
						// Hide polygons if shown
						for(key in polygons) {
							var current_polygons = polygons[key];
							// If shown
							if(current_polygons.map) {
								hideOpenLayerFeature(current_polygons);
								// var markerLayer = current_polygons.layerReference;
								// current_polygons.style.display = 'none';
								// current_polygons.map = '';
								// markerLayer.redraw();
							}
						}
					} else {
						if(ccpl_map.getZoom() > 11) {
							whiteMapClass.showSubStaionsInBounds();
							whiteMapClass.showBaseStaionsInBounds();
							whiteMapClass.showSectorDevicesInBounds();
							whiteMapClass.showLinesInBounds();
							whiteMapClass.showSectorPolygonInBounds();
						}
					}

        		}
        		// Show points line if exist
        		for(key in line_data_obj) {
        			if(!line_data_obj[key].map) {
        				showOpenLayerFeature(line_data_obj[key]);
        				// var markerLayer = line_data_obj[key].layerReference;
        				// line_data_obj[key].style.display = '';
        				// line_data_obj[key].map = 'current';
        				// markerLayer.redraw();
        			}
        		}

        		//Update Clusters Threshold value and recluster it
        		if(ccpl_map.getLayersByName('Markers')[0].strategies[0].threshold !== clustererSettings.threshold) {
					//Update Strategy with New Threshold and Distance Value
					ccpl_map.getLayersByName('Markers')[0].strategies[0].threshold = clustererSettings.threshold;
					ccpl_map.getLayersByName('Markers')[0].strategies[0].recluster();
				}
    		// 8 LEVEL ZOOM CONDITION
    		} else {
				whiteMapClass.showSubStaionsInBounds();
				whiteMapClass.showBaseStaionsInBounds();
				whiteMapClass.showSectorDevicesInBounds();
				whiteMapClass.showLinesInBounds();
				whiteMapClass.showSectorPolygonInBounds();

				//Update Clusters Threshold value and recluster it
				if(ccpl_map.getLayersByName('Markers')[0].strategies[0].threshold !== clustererSettings.thresholdAtHighZoomLevel) {
					//Update Strategy with New Threshold and Distance Value
					ccpl_map.getLayersByName('Markers')[0].strategies[0].threshold = clustererSettings.thresholdAtHighZoomLevel;
					ccpl_map.getLayersByName('Markers')[0].strategies[0].recluster();
				}
    		}

    		// Start performance calling after 1.5 Second
			setTimeout(function() {
				var bs_id_list = getMarkerInCurrentBound();
            	if(bs_id_list.length > 0 && isCallCompleted == 1) {
            		if(recallPerf != "") {
            			clearTimeout(recallPerf);
            			recallPerf = "";
            		}
            		// gisPerformanceClass.start(bs_id_list);
            	}
        	},500);

        } else {
        	
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
                           		labelsArray[x].destroy();
                           }
                        }
                    }
                }
            }

            // Reset labels array 
            labelsArray = [];


            /*Clear master marker cluster objects*/
            // Deactivate Marker Clustering Strategy
            ccpl_map.getLayersByName('Markers')[0].strategies[0].deactivate();

            /*Clear all everything from map*/
			$.grep(allMarkersArray_wmap,function(marker) {
				var markerLayer = marker.layer ? marker.layer : marker.layerReference;
				marker.isActive = 0;
				marker.style.display = 'none';
				markerLayer.redraw();
			});

			ccpl_map.getLayersByName('Markers')[0].destroyFeatures(ccpl_map.getLayersByName('Markers')[0].features);
			ccpl_map.getLayersByName('Markers')[0].redraw();

			// Reset Variables
			allMarkersArray_wmap = [];
			bs_ss_markers= [];
			main_devices_data_wmap = [];
			plottedBsIds = [];
			currentlyPlottedDevices = [];
			allMarkersObject_wmap= {
				'base_station': {},
				'path': {},
				'sub_station': {},
				'sector_device': {},
				'sector_polygon': {}
			};

			var states_with_bounds = state_lat_lon_db.where(function(obj) {
    			return whiteMapClass.checkIfPointLiesInside({lat: obj.lat, lon: obj.lon});
    		});

			for(var i=states_with_bounds.length;i--;) {
				if(state_wise_device_labels[states_with_bounds[i].name]) {
					state_wise_device_labels[states_with_bounds[i].name].attributes.display = '';
					ccpl_map.getLayersByName("States")[0].redraw();
				}
			}

			state_lat_lon_db.where(function(obj) {
				if(state_wise_device_labels[obj.name]) {
					state_wise_device_labels[obj.name].attributes.display = '';
					ccpl_map.getLayersByName("States")[0].redraw();
					return ;
				}
			});

			// Hide points line if exist
    		for(key in line_data_obj) {
    			if(line_data_obj[key].map) {
    				hideOpenLayerFeature(line_data_obj[key]);
    			}
    		}
        }

        // Save last Zoom Value
        lastZoomLevel = ccpl_map.getZoom();
        if(isDebug) {
			console.log("Google Map Idle Event End Time :- "+ new Date().toLocaleString());
			console.log("*************************************");
		}
	},300);
};


/**
 * This function is triggered when Click on Layer Features is done(Statem, Markers, Lines, Sectors). Zoom on cluster if present else open infowindow for it.
 * @param  {[type]} e [description]
 * @return {[type]}   [description]
 */
WhiteMapClass.prototype.layerFeatureClicked = function(feature) {
	/**
	 * This function shows create and display InfoWindow content for the feature.
	 * @param  {[OpenLayers Feature]} feature Feature on which Click was done
	 * @return {[type]}         ;
	 */
	function showInfoWindow(feature) {
		var content = gmap_self.makeWindowContent(feature);
		$("#infoWindowContainer").html(content);
		$("#infoWindowContainer").removeClass('hide');
	}

	//Check if feature clicked was a cluster
	if(feature.cluster) {
		//If feature cluster was present
		if(feature.cluster.length >= 2) {
			var clusterPoints = [];
			//Loop through all the points in cluster
			for(var i = 0; i< feature.cluster.length; i++){
				//Add geometry to the clusterPoints array
				clusterPoints.push(feature.cluster[i].geometry);
			}
			//Create a OpenLayer Geometry with our Clusterpoint
			var lineString = new OpenLayers.Geometry.LineString(clusterPoints);
			//Set Zoom to LineString
			ccpl_map.zoomToExtent(lineString.getBounds());
		} else {
			//Show infoWindow
			showInfoWindow(feature.cluster[0]);
		}
	} else {
		//If clicked feature was not base setation
		if(feature.pointType !== "base_station") {
			//Show Info Window for it
			showInfoWindow(feature);
			//If line was clicked, hide Freshnel Zone button on the infoWindowContainer
			if(feature.pointType === 'path') {
				setTimeout(function() {
					//remove freshnel zone button
					$("#infoWindowContainer").find('ul.list-unstyled.list-inline li:first-child').addClass('hide');
				}, 10);
			}
		//Else if base station was clicked
		} else {
			//First spiderify base station is not spiderfied, else open Info Window for it.
			if(this.spiderifyMarker(feature)) {
				showInfoWindow(feature);
			}
		}
	}
	//return
	return ;
}