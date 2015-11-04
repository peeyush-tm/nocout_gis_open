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

/**
 * Event triggered for Map Idle Condition. [Whenever Map is Zoomed, Panned or something else]
 */
var lastZoomLevel = 1;
WhiteMapClass.prototype.mapIdleCondition = function() {
	
	setTimeout(function() {
    	if(isDebug) {
			console.log("White Map Idle Event");
			var start_date_idle = new Date();
		}

    	/* When zoom level is greater than 8 show lines */
    	if(ccpl_map.getZoom() >= whiteMapSettings.zoomLevelAtWhichStateClusterExpands) {

    		if(ccpl_map.getZoom() > 10) {
        		// Reset Perf calling Flag
    			isPerfCallStopped = 0;
			} else {
				// Set Perf calling Flag
    			isPerfCallStopped = 1;
    			isPerfCallStarted = 0;

    			// If any periodic polling ajax call is in process then abort it
	            try {
    				if(gis_perf_call_instance) {
		                gis_perf_call_instance.abort()
		                gis_perf_call_instance = "";
		        	}
	            } catch(e) {
	                // pass
	            }
			}

			var states_with_bounds = state_lat_lon_db.where(function(obj) {
				return whiteMapClass.checkIfPointLiesInside({lat: obj.lat, lon: obj.lon});
    		});

			if(states_with_bounds.length > 0 || ccpl_map.getZoom() < 11 || searchResultData.length > 0) {

        		var states_array = [];

        		// Hide State Labels which are in current bounds
        		for(var i=states_with_bounds.length;i--;) {
        			if(state_wise_device_labels[states_with_bounds[i].name]) {
        				states_array.push(states_with_bounds[i].name);
        				state_wise_device_labels[states_with_bounds[i].name].attributes.display = 'none';
        				ccpl_map.getLayersByName("States")[0].redraw();
        			}
        		}

        		var plottable_data =  searchResultData.length > 0 ? searchResultData : gmap_self.updateStateCounter_gmaps(true),
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

    				main_devices_data_wmap = data_to_plot;

        			/**
					 * If anything searched n user is on zoom level 8 then reset 
					   currentlyPlottedDevices array for removing duplicacy.
        			 */
        			if(ccpl_map.getZoom() == 10 && searchResultData.length > 0) {
        				// Reset currentlyPlottedDevices array
        				currentlyPlottedDevices = [];
    				}


        			if(currentlyPlottedDevices.length == 0) {
        				ccpl_map.getLayersByName('Markers')[0].strategies[0].deactivate();

        				// Clear white map features & reset variables
						removeAllOpenLayerFeature();

						ccpl_map.getLayersByName('Markers')[0].strategies[0].activate();
						
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

					if(ccpl_map.getZoom() <= 10) {
						var polylines = allMarkersObject_wmap['path'],
							polygons = allMarkersObject_wmap['sector_polygon'];

						// Hide polylines if shown
						for(key in polylines) {
							hideOpenLayerFeature(polylines[key]);
							if(cross_label_array[key] && cross_label_array[key].getVisibility()) {
								hideOpenLayerFeature(cross_label_array[key]);
							}
						}
						// Redraw Lines layer to apply updates(Hide Lines)
						ccpl_map.getLayersByName('Lines')[0].redraw();

						// Redraw Red Cross layer to apply updates(Hide Lines)
						ccpl_map.getLayersByName("RedCross")[0].redraw();

						// Hide polygons if shown
						for(key in polygons) {
							hideOpenLayerFeature(polygons[key]);
						}
						// Redraw Sectors layer to apply updates(Hide Sectors)
						ccpl_map.getLayersByName('Sectors')[0].redraw();

						var current_threshold = ccpl_map.getLayersByName("Markers")[0].strategies[0].threshold,
							current_distance = ccpl_map.getLayersByName("Markers")[0].strategies[0].distance;

						if(current_threshold == 1.5  && current_distance == -1) {
							// Remove Clusters
							ccpl_map.getLayersByName("Markers")[0].strategies[0].threshold = 2;
							ccpl_map.getLayersByName("Markers")[0].strategies[0].distance = 100;
							ccpl_map.getLayersByName("Markers")[0].strategies[0].recluster();
							// ccpl_map.getLayersByName("Markers")[0].redraw();
						}
					} else {
						var current_threshold = ccpl_map.getLayersByName("Markers")[0].strategies[0].threshold,
							current_distance = ccpl_map.getLayersByName("Markers")[0].strategies[0].distance;

						if(current_threshold > 1.5  && current_distance > -1) {
							// Remove Clusters
							ccpl_map.getLayersByName("Markers")[0].strategies[0].threshold = 1.5;
							ccpl_map.getLayersByName("Markers")[0].strategies[0].distance = -1;
							ccpl_map.getLayersByName("Markers")[0].strategies[0].recluster();
							ccpl_map.getLayersByName("Markers")[0].redraw();
						}

						// Show/Hide White Map Features
						whiteMapClass.showBaseStaionsInBounds();
						whiteMapClass.showSectorDevicesInBounds();
						whiteMapClass.showSectorPolygonInBounds();
						whiteMapClass.showLinesInBounds();
						whiteMapClass.showSubStaionsInBounds();
						
					    if(isPerfCallStopped == 0 && isPerfCallStarted == 0) {
							var bs_id_list = getMarkerInCurrentBound();
			            	if(bs_id_list.length > 0 && isCallCompleted == 1) {
			            		gisPerformanceClass.start(bs_id_list);
			            	}
	            		} else {
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
		                			// sendRequest with last_counter_val
		                			gisPerformanceClass.sendRequest(last_counter_val);
		                		}
		                	}
	            		}
					}
        		}
        		// Show points line if exist
        		for(key in line_data_obj) {
        			if(!line_data_obj[key].map) {
        				showOpenLayerFeature(line_data_obj[key]);
        			}
        		}
    		} else {
    			var current_threshold = ccpl_map.getLayersByName("Markers")[0].strategies[0].threshold,
					current_distance = ccpl_map.getLayersByName("Markers")[0].strategies[0].distance;

				if(current_threshold > 1.5  && current_distance > -1) {
					// Remove Clusters
					ccpl_map.getLayersByName("Markers")[0].strategies[0].threshold = 1.5;
					ccpl_map.getLayersByName("Markers")[0].strategies[0].distance = -1;
					ccpl_map.getLayersByName("Markers")[0].strategies[0].recluster();
					ccpl_map.getLayersByName("Markers")[0].redraw();
				}

				// Show/Hide White Map Features
				whiteMapClass.showBaseStaionsInBounds();
				whiteMapClass.showSectorDevicesInBounds();
				whiteMapClass.showSectorPolygonInBounds();
				whiteMapClass.showLinesInBounds();
				whiteMapClass.showSubStaionsInBounds();

				if(isPerfCallStopped == 0 && isPerfCallStarted == 0) {
					var bs_id_list = getMarkerInCurrentBound();
	            	if(bs_id_list.length > 0 && isCallCompleted == 1) {
	            		gisPerformanceClass.start(bs_id_list);
	            	}
        		} else {
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
                			// sendRequest with last_counter_val
                			gisPerformanceClass.sendRequest(last_counter_val);
                		}
                	}
        		}
    		}
        } else {

        	// Clear white map features & reset variables
			removeAllOpenLayerFeature();

			// Hide State Counters Label
			for(key in state_wise_device_labels) {
				if(state_wise_device_labels[key]) {
					state_wise_device_labels[key].attributes.display = 'none';
    				ccpl_map.getLayersByName("States")[0].redraw();
				}
			}

        	// If any periodic polling ajax call is in process then abort it
            try {
				if(gis_perf_call_instance) {
	                gis_perf_call_instance.abort()
	                gis_perf_call_instance = "";
	        	}
            } catch(e) {
                // pass
            }

        	if(ccpl_map.getZoom() < 1) {
        		// Hide State Labels which are in current bounds
        		var country_click_event = "onClick='gmap_self.state_label_clicked(0)'",
        			total_devices_count = gmap_self.getCountryWiseCount();

    			var country_point = new OpenLayers.Geometry.Point(77.7832, 24.2870),
    				country_counter_label = new OpenLayers.Feature.Vector(country_point);

	            country_counter_label.attributes = {
	                label 		: total_devices_count,
	                state_param : 0,
	                cursor		: "pointer",
	                title 		: "Load India Data",
	                display 	: ''
	            };
	            country_counter_label.map = 'current';
	            
	            ccpl_map.getLayersByName('States')[0].addFeatures([country_counter_label]);

		        if(country_label["india"] != "") {
		        	country_label["india"].destroy();
		        	country_label["india"] = "";
		        }

	        	country_label["india"] = country_counter_label;

    		} else {

    			if(country_label["india"] != "") {
    				country_label["india"].attributes.display = 'none';
		        	country_label["india"].destroy();
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
        }

        // Save last Zoom Value
        lastZoomLevel = ccpl_map.getZoom();
        if(isDebug) {
        	var time_diff = (new Date().getTime() - start_date_idle.getTime())/1000;
			console.log("White Map Idle Event End Time :- "+ time_diff + "Seconds");
			console.log("*************************************");
			start_date_idle = "";
		}
	},450);
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
		gmap_self.makeWindowContent(feature, function(content) {
			$("#infoWindowContainer").html(content);
			$("#infoWindowContainer").removeClass('hide');
		});
	}

	//Check if feature clicked was a cluster
	if(feature && feature.cluster) {
		//If feature cluster was present
		if(feature && feature.cluster.length >= 2) {
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
		if(feature && feature.pointType !== "base_station") {

			var lat_lon_key = String(feature.ptLat)+"_"+String(feature.ptLon);

			if(feature.pointType == 'sub_station' && overlapping_ss[lat_lon_key]) {
				// If marker is spiderified then show infowindow
				if(feature.isMarkerSpiderfied) {
					showInfoWindow(feature);
				} else {
					this.spiderifyWmapMarker(overlapping_ss[lat_lon_key]);
				}
			} else {
				//Show Info Window for it
				showInfoWindow(feature);
				//If line was clicked, hide Freshnel Zone button on the infoWindowContainer
				if(feature.pointType == 'path') {
					setTimeout(function() {
						//remove freshnel zone button
						$("#infoWindowContainer").find('ul.list-unstyled.list-inline li:first-child').addClass('hide');
					}, 10);
				}
			}

		//Else if base station was clicked
		} else {
			//First spiderify base station is not spiderfied, else open Info Window for it.
			if(feature && this.spiderifyMarker(feature)) {
				showInfoWindow(feature);
			}
		}
	}
	//return
	return ;
}

/**
 * This function is called when Mouseover is done over a feature in Markers layer or Devices Layer.
 * @param  {OpenLayer Feature} e [Contains Information of Feature which is Hovered]
 * @return {[type]}   [description]
 */
var featureHovered = "";
WhiteMapClass.prototype.mouseOverEvent = function(e) {
	var feature = e.feature;
	featureHovered = feature;
	setTimeout(function() {
		var condition1 = ($.trim(feature.pl) && $.trim(feature.pl) != 'N/A'),
		condition2 = ($.trim(feature.rta) && $.trim(feature.rta) != 'N/A');

		if(condition1 || condition2) {
			var pl = $.trim(feature.pl) ? feature.pl : "N/A",
			rta = $.trim(feature.rta) ? feature.rta : "N/A",
			info_html = '';

			// Create hover infowindow html content
			info_html += '<table class="table table-responsive table-bordered table-hover">';
			info_html += '<tr><td><strong>Packet Drop</strong></td><td><strong>'+pl+'</strong></td></tr>';
			info_html += '<tr><td><strong>Latency</strong></td><td><strong>'+rta+'</strong></td></tr>';
			info_html += '</table>';

			var infoWindow = whiteMapClass.openInfoWindow(feature, info_html);
			feature.popup = infoWindow;
		}
	}, 40);
}

/**
 * This function is called when Mouseout is done over a feature in Markers layer or Devices Layer.
 * @param  {OpenLayer Feature} e [Contains Information of Feature which was unfocussed]
 * @return {[type]}   [description]
 */
WhiteMapClass.prototype.mouseOutEvent = function(e) {
	var feature = e ? e.feature : featureHovered;
	var condition1 = ($.trim(feature.pl) && $.trim(feature.pl) != 'N/A'),
		condition2 = ($.trim(feature.rta) && $.trim(feature.rta) != 'N/A');

	if(condition1 || condition2) {
		if(feature && feature.popup) {
			feature.popup.hide();
			feature.popup.destroy();
			feature.popup = "";
			featureHovered = "";
		}
	}
}