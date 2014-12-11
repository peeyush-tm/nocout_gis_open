var recallPerf = "",
    current_bs_list = [],
    perf_fetched_devices = [],
    perf_self = "";

var x = 0;
/*
 This function creates a google marker with a new URL and take all other values from previous defined marker setting else set to null
 */
function createGoogleMarker(url, oldMarkerIcon) {
    var oldMarObj = {}, newMarkerImage = "";
    //Get anchor setting from oldMarkerIcon
    oldMarObj['anchor'] = oldMarkerIcon['icon']['anchor'] ? oldMarkerIcon['icon']['anchor'] : null;
    //Get origin setting from oldMarkerIcon
    oldMarObj['origin'] = oldMarkerIcon['icon']['origin'] ? oldMarkerIcon['icon']['origin'] : null;
    //Get scaledSize setting from oldMarkerIcon
    oldMarObj['scaledSize'] = oldMarkerIcon['icon']['scaledSize'] ? oldMarkerIcon['icon']['scaledSize'] : null;
    //Get size setting from oldMarkerIcon
    oldMarObj['size'] = oldMarkerIcon['icon']['size'] ? oldMarkerIcon['icon']['size'] : google.maps.Size(32, 37);
    //Create a new MarkerImage with new url, and all others value from previous defined settings
    newMarkerImage = new google.maps.MarkerImage(url, oldMarObj['size'], oldMarObj['origin'], oldMarObj['anchor'], oldMarObj['scaledSize']);
    //Return newMarker
    return newMarkerImage;
}


/**
 * [GisPerformance description]
 */
function GisPerformance() {
    //Is Frozen variable.. Get value from isFreeze Global Variable defined.
    this.isFrozen_ = 0;
    //Variable to hold GisData
    this.gisData;

    //Variable to hold Base Stations Name
    this.bsNamesList = [];
    //Base Station Length
    this.bsLength = 0;

    perf_self = this;

    /*
     Here we start GisPerformance.
     Send an AJax request to get GisPerformance Data
     Store Data in gisData variable
     And start the setInterval function to updateMap every 10 secs.
     */
    this.start = function (bs_list) {

        if (isPollingActive == 0  && isPerfCallStopped == 0) {
            //Reset Variable
            perf_self.resetVariable()

            isPerfCallStarted = 1;

            var uncommon_bs_list = perf_self.get_intersection_bs(current_bs_list,bs_list);

            this.bsNamesList = uncommon_bs_list;
            //Store Length of Total BS
            this.bsLength = this.bsNamesList.length;

            if(uncommon_bs_list.length == bs_list.length) {
                current_bs_list = uncommon_bs_list;
            }
            //Start Request for First BS
            perf_self.sendRequest(0);
        }
    };

    /*
     This will stop Sending Request by Setting isFrozen variable to 1
     */
    this.stop = function () {
        this._isFrozen = 1;
    }

    /*
     This will restart the Request by Setting isFrozen variable to 0 and sending Request for First BS
     */
    this.restart = function () {
        this._isFrozen = isFreeze;

        if (this.bsNamesList && this.bsNamesList.length > 0) {
            this.start(this.bsNamesList);
        }
    }

    /*
     Here we reset all variables defined.
     */
    this.resetVariable = function () {
        this.gisData = null;
        this.bsNamesList = [];
        this.bsLength = 0;
        current_bs_list = [];
        this._isFrozen = isFreeze;
        isPerfCallStarted = 0;
    }

    /*
     This function sends Request based on the counter value.
     */
    this.sendRequest = function (counter) {
        // +($.cookie('isFreezeSelected')) == 0 || +($.cookie('freezedAt')) > 0
        if (isPollingActive == 0  && isPerfCallStopped == 0) {
            if(perf_self.bsNamesList.length > 0 && perf_self.bsNamesList[counter]) {
                //Call waitAndSend function with BS Json Data and counter value
                perf_self.waitAndSend(perf_self.bsNamesList[counter], counter);
            } else {
                //1 Minutes Timeout
                setTimeout(function () {
                    //Start Performance Again
                    var bs_list = getMarkerInCurrentBound();
                    // Clear previous bs list
                    if(bs_list.length > 0 && isCallCompleted == 1) {
                        /*Reset global variable when all calls completed*/
                        current_bs_list = [];
                        /*Start calls*/
                        perf_self.start(bs_list);
                    }
                }, 60000);
            }
        }
    }

    /*
     This function sends a Ajax request based on param and counter provided. If All the calls for BS is completed, then we resetVariables and start Performance again in 5 mins.
     */
    this.waitAndSend = function (bs_id, counter) {

        counter++;

        var selected_thematics = $("input:radio[name=thematic_type]").length > 0 ? $("input:radio[name=thematic_type]:checked").val() : "normal";

        //Ajax Request
        $.ajax({
            url: base_url + '/network_maps/perf_data/?base_stations=['+bs_id+']&ts='+selected_thematics+'&freeze_time=' + freezedAt,
            // url: base_url + '/static/new_perf_ptp.json',
            type: 'GET',
            dataType: 'json',
            //In success
            success: function (result) {
                var data = result.length ? result[0] : result;
                // perf_fetched_devices.push(perf_self.bsNamesList[counter-1]);
                // perf_self.bsNamesList.splice(counter-1,0);
                //If data is there
                if(data) {
                    //Store data in gisData
                    if(data.success && data.success == 1) {
                        perf_self.gisData = data;
                        if(window.location.pathname.indexOf("white_background") > -1) {
                            //Update Map with the data
                            perf_self.updateMap(function(response) {
                                //Send Request for the next counter
                                perf_self.sendRequest(counter);
                            });
                        } else if(window.location.pathname.indexOf("googleEarth") > -1) {
                            //Update Map with the data
                            perf_self.updateMap(function(response) {
                                //Send Request for the next counter
                                perf_self.sendRequest(counter);
                            });
                        } else {
                            var current_bs_in_bound = getMarkerInCurrentBound();
                            /*Check that the bsname is present in current bounds or not*/
                            if (current_bs_in_bound.indexOf(data.bs_id) > -1) {
                                //Update Map with the data
                                perf_self.updateMap(function(response) {
                                    //Send Request for the next counter
                                perf_self.sendRequest(counter);
                                });
                            }
                        }
                    }
                }

            },
            //On Error, do nothing
            error: function (err) {
                // setTimeout(function () {
                //     //Start Performance Again
                //     if (this.bsNamesList && this.bsNamesList.length > 0) {
                //         perf_self.start(this.bsNamesList);
                //     }
                // }, 60000);
                //Send Request for the next counter
                perf_self.sendRequest(counter);
            }
        });
    }

    /*
     Here we update Google Map from gisData
     First we get BS Marker from markersMasterObj with BS Name
     Then we loop through each SS for the Base Station
     Then we fetch various google map elements like lineColor or sectorColor and update those components using values from GisPerformanceData.
     */
    this.updateMap = function (callback) {

        if(this.gisData) {
            //Step no. 1 => Find BS Station First
            var gisData = this.gisData;
                sectorArray = gisData.param.sector,
                bs_name = gisData.bs_name,
                perf_bh_info = gisData.bh_info ? gisData.bh_info : [],
                perf_bh_severity = gisData.bhSeverity ? gisData.bhSeverity : "",
                other_icons_obj = "",
                bs_marker = "";

            if(window.location.pathname.indexOf("googleEarth") > -1) {
                other_icons_obj = base_url+'/static/img/icons/1x1.png';
                bs_marker = allMarkersObject_earth['base_station']['bs_'+bs_name];
            } else if (window.location.pathname.indexOf("white_background") > -1) {
                other_icons_obj = base_url+'/static/img/icons/1x1.png';
                bs_marker = allMarkersObject_wmap['base_station']['bs_'+bs_name];
            } else {
                other_icons_obj = new google.maps.MarkerImage(
                    base_url+'/static/img/icons/1x1.png',
                    null,
                    null,
                    null,
                    null
                );
                bs_marker = allMarkersObject_gmap['base_station']['bs_'+bs_name];
            }

            // Update BH polled info to bs marker tooltip.
            if(bs_marker) {
                try {
                    bs_marker['bhInfo'] = bs_marker['bhInfo'].concat(perf_bh_info);
                    bs_marker['bhSeverity'] = perf_bh_severity;
                } catch(e) {
                    // console.log(e);
                }
            }

            // BH info addition ended.

            var bs_object = JSON.parse(JSON.stringify(all_devices_loki_db.where(function(obj){return obj.originalId == gisData.bs_id})[0])),
                connected_sectors = bs_object.data.param.sector,
                new_plotted_ss = [];

            // Loop for Sectors
            for(var i=0;i<sectorArray.length;i++) {

                var current_sector = sectorArray[i],
                    sector_ip = current_sector.ip_address,
                    sector_id = current_sector.sector_id,
                    sector_perf_info = current_sector.perf_info ? current_sector.perf_info : [],
                    sector_device = current_sector.device_name,
                    sector_icon = current_sector.icon ? current_sector.icon : "",
                    sector_perf_val = current_sector.perf_value ? current_sector.perf_value : 0,
                    sub_station = current_sector.sub_station ? current_sector.sub_station : [],
                    sector_marker = "",
                    sector_polygon = "",
                    startEndObj = {};

                if(window.location.pathname.indexOf("googleEarth") > -1) {
                    sector_marker = allMarkersObject_earth['sector_device']['sector_'+sector_ip];
                    sector_polygon = allMarkersObject_earth['sector_polygon']['poly_'+sector_ip+"_"+sector_id];
                } else if(window.location.pathname.indexOf("white_background") > -1) {
                    sector_marker = allMarkersObject_wmap['sector_device']['sector_'+sector_ip];
                    sector_polygon = allMarkersObject_wmap['sector_polygon']['poly_'+sector_ip+"_"+sector_id];
                } else {
                    sector_marker = allMarkersObject_gmap['sector_device']['sector_'+sector_ip];
                    sector_polygon = allMarkersObject_gmap['sector_polygon']['poly_'+sector_ip+"_"+sector_id];
                }

                // If sector marker exist then update it with new icon
                if(sector_marker) {
                    if(sector_icon) {
                        if(window.location.pathname.indexOf("googleEarth") > -1) {
                            var iconUrl = base_url+"/"+sector_icon,
                                old_icon_obj = iconUrl;
                            // Update sector marker icon
                            updateGoogleEarthPlacemark(sector_marker, newIcon);
                            // sector_marker.icon = other_icons_obj;
                            try {
                                sector_marker['clusterIcon'] = other_icons_obj;
                                sector_marker['oldIcon'] = old_icon_obj;
                            } catch(e) {
                                // console.log(e);
                            }

                            updateGoogleEarthPlacemark(sector_marker, old_icon_obj);
                        } else if (window.location.pathname.indexOf("white_background") > -1) {
                            var iconUrl = base_url+"/"+sector_icon,
                                old_icon_obj = iconUrl;
                            // Update sector marker icon
                            sector_marker.attributes.icon = other_icons_obj;
                            sector_marker.attributes.clusterIcon = other_icons_obj;
                            sector_marker.attributes.oldIcon = old_icon_obj;
                            sector_marker.oldIcon = old_icon_obj;
                            sector_marker.style['externalGraphic'] = old_icon_obj;
                            var sectorMarkerLayer = sector_marker.layer ? sector_marker.layer : sector_marker.layerReference;
                            sectorMarkerLayer.redraw();

                        } else {
                            var largeur= 32,
                                hauteur= 37,
                                divideBy= 1,
                                anchorX= 0,
                                iconUrl = base_url+"/"+sector_icon,
                                old_icon_obj = new google.maps.MarkerImage(
                                    iconUrl,
                                    new google.maps.Size(Math.ceil(largeur/divideBy), Math.ceil(hauteur/divideBy)),
                                    new google.maps.Point(0, 0),
                                    new google.maps.Point(Math.ceil(16-(16*anchorX)), Math.ceil(hauteur/divideBy)),
                                    new google.maps.Size(Math.ceil(largeur/divideBy), Math.ceil(hauteur/divideBy))
                                );

                            // Update sector marker icon
                            sector_marker.setOptions({
                                "icon" : other_icons_obj,
                                "clusterIcon" : other_icons_obj,
                                "oldIcon" : old_icon_obj,
                            });
                        }
                    }

                    var sector_pl = "",
                        sector_rta = "";

                    for(var x=sector_perf_info.length;x--;) {
                        if($.trim(sector_perf_info[x].name) == 'pl') {
                            sector_pl = sector_perf_info[x].value;
                        } else if($.trim(sector_perf_info[x].name) == 'rta') {
                            sector_rta = sector_perf_info[x].value;
                        }
                    }

                    if(window.location.pathname.indexOf("googleEarth") > -1 || window.location.pathname.indexOf("white_background") > -1) {
                        try {
                            sector_marker['poll_info'] = sector_perf_info;
                            sector_marker['pl'] = sector_pl;
                            sector_marker['rta'] = sector_rta;
                        } catch(e) {
                            // console.log(e);
                        }
                    } else {
                        // Set perf info for sector marker to show it on tooltip
                        sector_marker.setOptions({
                            "poll_info" : sector_perf_info,
                            "pl" : sector_pl,
                            "rta" : sector_rta
                        });
                    }
                    
                    startEndObj["startLat"] = bs_object.data.lat;
                    startEndObj["startLon"] = bs_object.data.lon;
                    
                    startEndObj["sectorLat"] = bs_object.data.lat;
                    startEndObj["sectorLon"] = bs_object.data.lon;

                } else if(sector_polygon) {

                    var azimuth_angle = current_sector.azimuth_angle ? current_sector.azimuth_angle : 10,
                        beam_width = current_sector.beam_width ? current_sector.beam_width : 10,
                        radius = current_sector.radius ? current_sector.radius : 0.5,
                        sector_color = current_sector.color ? current_sector.color : 'rgba(74,72,94,0.58)',
                        lat = bs_object.data.lat,
                        lon = bs_object.data.lon,
                        orientation = current_sector.polarization ? current_sector.polarization : "vertical";

                    gmap_self.createSectorData(lat,lon,radius,azimuth_angle,beam_width,orientation,function(pointsArray) {

                        var halfPt = Math.floor(pointsArray.length / (+2)),
                            polyPathArray = [],
                            polyPoints= "";

                        if(window.location.pathname.indexOf("googleEarth") > -1) {
                            // Add points for poly coordinates.
                            polyPoints = ge.createLinearRing('');
                            polyPoints.setAltitudeMode(ge.ALTITUDE_RELATIVE_TO_GROUND);
                            for(var i=0;i<pointsArray.length;i++) {
                                polyPoints.getCoordinates().pushLatLngAlt(pointsArray[i].lat, pointsArray[i].lon, 700);
                            }
                        } else if(window.location.pathname.indexOf("white_background") > -1) {
                            for(var i=0;i<pointsArray.length;i++) {
                                var pt = new OpenLayers.Geometry.Point(pointsArray[i].lon, pointsArray[i].lat);
                                polyPathArray.push(pt);
                            }
                            
                        } else {
                            for(var i=0;i<pointsArray.length;i++) {
                                var pt = new google.maps.LatLng(pointsArray[i].lat,pointsArray[i].lon);
                                polyPathArray.push(pt);
                            }
                        }

                        startEndObj["startLat"] = pointsArray[halfPt].lat;
                        startEndObj["startLon"] = pointsArray[halfPt].lon;

                        startEndObj["sectorLat"] = pointsArray[halfPt].lat;
                        startEndObj["sectorLon"] = pointsArray[halfPt].lon;

                        if(window.location.pathname.indexOf("googleEarth") > -1) {
                            sector_polygon.setOuterBoundary(polyPoints);

                            var poly_sector_color = earth_self.makeRgbaObject(sector_color);
                            // Color can also be specified by individual color components.
                            var polyColor = sectorPolygonObj.getStyleSelector().getPolyStyle().getColor();
                            polyColor.setA(200);
                            polyColor.setR((+poly_sector_color.r));
                            polyColor.setG((+poly_sector_color.g));
                            polyColor.setB((+poly_sector_color.b));
                        } else if(window.location.pathname.indexOf("white_background") > -1) {
                            var linearRing = new OpenLayers.Geometry.LinearRing(polyPoints);
                            var geometry = new OpenLayers.Geometry.Polygon([linearRing]);

                            sector_polygon.geometry = geometry;

                        } else {
                            // Update sector Path & color.
                            sector_polygon.setOptions({
                                path: polyPathArray,
                                fillColor: sector_color
                            });
                        }
                    });

                    if(window.location.pathname.indexOf("googleEarth") > -1 || window.location.pathname.indexOf("googleEarth") > -1) {
                        try {
                            sector_polygon['poll_info'] = sector_perf_info;
                        } catch(e) {
                            // console.log(e);
                        }
                    } else {
                        // Set perf info for sector marker to show it on tooltip
                        sector_polygon.setOptions({
                            "poll_info" : sector_perf_info
                        });
                    }
                } else {
                    // pass
                }

                // Remove sub-station from google maps - start

                // If any ss exist in response then clear old ss & their connection lines from map
                if(sub_station.length > 0) {
                    // If sub-station exist the remove old sub-station markers from google map.
                    var ss_marker_obj = {},
                        removed_key = [],
                        ss_name_array = [],
                        key = "";

                    if(window.location.pathname.indexOf("googleEarth") > -1) {
                        ss_marker_obj = allMarkersObject_earth['sub_station'];
                    } else if (window.location.pathname.indexOf("white_background") > -1) {
                        ss_marker_obj = allMarkersObject_wmap['sub_station'];
                    } else {
                        ss_marker_obj = allMarkersObject_gmap['sub_station'];
                    }

                    for(key in ss_marker_obj) {
                        if(key.indexOf("ss_") > -1) {
                            var current_old_ss = ss_marker_obj[key];
                            if(current_old_ss) {
                                var condition1 = "",
                                    condition2 = "",
                                    condition3 = "";

                                try {
                                    condition1 = current_old_ss['filter_data']['bs_id'] == gisData.bs_id,
                                    condition2 = current_old_ss['filter_data']['sector_name'] == sector_ip,
                                    condition3 = current_old_ss['filter_data']['sector_id'] == sector_id;
                                } catch(e) {
                                    // console.log(e);
                                }

                                if(condition1 && condition2 && condition3) {
                                    removed_key.push(key.split("ss_")[1]);
                                    if(window.location.pathname.indexOf("googleEarth") > -1) {
                                        try {
                                            // Remove from google map
                                            current_old_ss.setVisibility(false);
                                            current_old_ss.map = '';
                                            deleteGoogleEarthPlacemarker(current_old_ss.getId());
                                        } catch(e) {
                                            // console.log(e);
                                        }
                                    } else if (window.location.pathname.indexOf("white_background") > -1) {
                                        // hideOpenLayerFeature(current_old_ss);
                                        if(current_old_ss && current_old_ss.style) {
                                            var featureLayer = current_old_ss.layer ? current_old_ss.layer : current_old_ss.layerReference;
                                            current_old_ss.style.display = 'none';
                                            if(featureLayer) {
                                                featureLayer.redraw();
                                                
                                            }
                                        }
                                    } else {
                                        // Remove from google map
                                        current_old_ss.setMap(null);
                                    }
                                } else {
                                    // pass
                                }
                            } else {
                                // pass
                            }
                        } else {
                            // pass
                        }
                    }

                    for(var x=0;x<removed_key.length;x++) {
                        if(window.location.pathname.indexOf("googleEarth") > -1) {
                            try {
                                if(allMarkersObject_earth['sub_station']["ss_"+removed_key[x]]) {
                                    delete allMarkersObject_earth['sub_station']["ss_"+removed_key[x]];
                                } else {
                                    // pass
                                }

                                // Remove Line from map
                                if(allMarkersObject_earth['path']['line_'+removed_key[x]]) {
                                    allMarkersObject_earth['path']['line_'+removed_key[x]].setVisibility(false);
                                    // Remove Line from array object
                                    delete allMarkersObject_earth['path']['line_'+removed_key[x]];
                                } else {
                                    // pass
                                }
                            } catch(e) {
                                // console.log(e);
                            }
                        } else if (window.location.pathname.indexOf("white_background") > -1) {
                            if(allMarkersObject_wmap['sub_station']["ss_"+removed_key[x]]) {
                                delete allMarkersObject_wmap['sub_station']["ss_"+removed_key[x]];
                            } else {
                                // pass
                            }

                            // Remove Line from map
                            if(allMarkersObject_wmap['path']['line_'+removed_key[x]]) {
                                allMarkersObject_wmap['path']['line_'+removed_key[x]].style.display = "none";
                                allMarkersObject_wmap['path']['line_'+removed_key[x]].layerReference.redraw();
                                // Remove Line from array object
                                delete allMarkersObject_wmap['path']['line_'+removed_key[x]];
                            } else {
                                // pass
                            }

                        } else {
                            if(allMarkersObject_gmap['sub_station']["ss_"+removed_key[x]]) {
                                delete allMarkersObject_gmap['sub_station']["ss_"+removed_key[x]];
                            } else {
                                // pass
                            }

                            // Remove Line from map
                            if(allMarkersObject_gmap['path']['line_'+removed_key[x]]) {
                                allMarkersObject_gmap['path']['line_'+removed_key[x]].setMap(null);
                                // Remove Line from array object
                                delete allMarkersObject_gmap['path']['line_'+removed_key[x]];
                            } else {
                                // pass
                            }
                        }
                    }

                    // Get ss markers from all markers array
                    var splice_index = [],
                        allMarkersArray= [],
                        updatedAllMarkersArray = [];

                    if(window.location.pathname.indexOf("googleEarth") > -1) {
                        allMarkersArray = allMarkersArray_earth;
                    } else if (window.location.pathname.indexOf("white_background") > -1) {
                        allMarkersArray = allMarkersArray_wmap;
                    } else {
                        allMarkersArray = allMarkersArray_gmap;
                    }

                    for(var x=0;x<allMarkersArray.length;x++){
                        var condition1 = "",
                            condition2 = "",
                            condition3 = "",
                            condition4 = "";

                        try {
                            condition1 = allMarkersArray[x]['pointType'] == 'sub_station' || allMarkersArray[x]['pointType'] == 'path',
                            condition2 = allMarkersArray[x]['filter_data']['bs_id'] == gisData.bs_id,
                            condition3 = allMarkersArray[x]['filter_data']['sector_name'] == sector_ip,
                            condition4 = allMarkersArray[x]['filter_data']['sector_id'] == sector_id;
                        } catch(e) {
                            // console.log(e);
                        }

                        if(!(condition1 && condition2 && condition3 && condition4)) {
                            // splice_index.push(x);
                            updatedAllMarkersArray.push(allMarkersArray[x])
                        } else {
                            // pass
                        }
                    }

                    if(window.location.pathname.indexOf("googleEarth") > -1) {
                        allMarkersArray_earth = updatedAllMarkersArray;
                    } else if (window.location.pathname.indexOf("white_background") > -1) {
                        allMarkersArray_wmap = updatedAllMarkersArray;
                    } else {
                        allMarkersArray_gmap = updatedAllMarkersArray;
                    }

                    // Remove ss marker from all markers array
                    // for(var y=0;y<splice_index.length;y++) {
                    //     if(window.location.pathname.indexOf("googleEarth") > -1) {
                    //         allMarkersArray_earth.splice(splice_index[y],1);
                    //     } else if (window.location.pathname.indexOf("white_background") > -1) {
                    //         allMarkersArray_wmap.splice(splice_index[y],1);
                    //     } else {
                    //         allMarkersArray_gmap.splice(splice_index[y],1);
                    //     }
                    // }

                    if(window.location.pathname.indexOf("googleEarth") > -1) {
                        // Pass
                    } else if (window.location.pathname.indexOf("white_background") > -1) {
                        // Update Marker cluster
                        var new_cluster_markers = [],
                            new_lines_array = [];

                        // Update Marker cluster
                        var bs_markers_array = Object.keys(allMarkersObject_wmap['base_station']).map(function(k) { return allMarkersObject_wmap['base_station'][k] }),
                            ss_markers_array = Object.keys(allMarkersObject_wmap['sub_station']).map(function(k) { return allMarkersObject_wmap['sub_station'][k] });

                        new_cluster_markers = new_cluster_markers.concat(bs_markers_array);
                        new_cluster_markers = new_cluster_markers.concat(ss_markers_array);

                        // Update Features(BS-SS Object)
                        ccpl_map.getLayersByName('Markers')[0].strategies[0].features = new_cluster_markers;
                        ccpl_map.getLayersByName('Markers')[0].features = new_cluster_markers;

                        //recluster the strategy(Clusters)
                        ccpl_map.getLayersByName('Markers')[0].strategies[0].recluster();
                        ccpl_map.getLayersByName('Markers')[0].redraw();

                        for(key in allMarkersObject_wmap['path']) {
                            if(allMarkersObject_wmap['path'][key]) {
                                new_lines_array.push(allMarkersObject_wmap['path'][key]);
                            }
                        }

                        // Update Lines layer
                        ccpl_map.getLayersByName('Lines')[0].features = new_lines_array;
                        ccpl_map.getLayersByName('Lines')[0].redraw();

                        
                    } else {
                        // Update Marker cluster
                        var bs_markers_array = Object.keys(allMarkersObject_gmap['base_station']).map(function(k) { return allMarkersObject_gmap['base_station'][k] });
                        var ss_markers_array = Object.keys(allMarkersObject_gmap['sub_station']).map(function(k) { return allMarkersObject_gmap['sub_station'][k] });
                        masterClusterInstance.clearMarkers();
                        masterClusterInstance.addMarkers(bs_markers_array);
                        masterClusterInstance.addMarkers(ss_markers_array);
                    }

                    // Loop to plot new sub-stations
                    for(var j=0;j<sub_station.length;j++) {
                        var ss_marker_data = sub_station[j],
                            ss_perf_info = ss_marker_data.data.param.sub_station,
                            ss_pl = "",
                            ss_rta = "";

                        for(var y=ss_perf_info.length;y--;) {
                            if($.trim(ss_perf_info[y].name) == 'pl') {
                                ss_pl = ss_perf_info[y].value;
                            } else if($.trim(ss_perf_info[y].name) == 'rta') {
                                ss_rta = ss_perf_info[y].value;
                            }
                        }

                        if(window.location.pathname.indexOf("googleEarth") > -1) {
                            var ssInfo= {
                                map: 'current',
                                ptLat: ss_marker_data.data.lat,
                                ptLon:  ss_marker_data.data.lon,
                                technology: ss_marker_data.data.technology,
                                icon: base_url+"/"+ss_marker_data.data.markerUrl,
                                oldIcon: base_url+"/"+ss_marker_data.data.markerUrl,
                                clusterIcon: base_url+"/"+ss_marker_data.data.markerUrl,
                                pointType: "sub_station",
                                dataset: ss_perf_info,
                                bhInfo: [],
                                poll_info: [],
                                pl: ss_pl,
                                rta: ss_rta,
                                antenna_height: ss_marker_data.data.antenna_height,
                                name: ss_marker_data.name,
                                bs_name: gisData.bs_name,
                                bs_sector_device: sector_device,
                                filter_data: {"bs_name" : gisData.bs_name, "sector_name" : sector_ip, "ss_name" : ss_marker_data.name, "bs_id" : gisData.bs_id, "sector_id" : sector_id},
                                device_name: ss_marker_data.device_name,
                                ss_ip: ss_marker_data.data.substation_device_ip_address,
                                sector_ip: sector_ip,
                                hasPerf: 0,
                                isActive: 1
                            };

                            var ss_marker = earth_self.makePlacemark(base_url+"/"+ss_marker_data.data.markerUrl, ss_marker_data.data.lat, ss_marker_data.data.lon,'ss_'+ss_marker_data.id, ssInfo);

                            (function(ss_marker) {
                                google.earth.addEventListener(ss_marker, 'click', function(event) {
                                    var content = gmap_self.makeWindowContent(ss_marker);
                                    $("#google_earth_container").after('<iframe allowTransparency="true" style="position:absolute; top:10px; right:10px; overflow: auto; padding:0px; height:100%; max-height: 550px; overflow:auto; z-index:100;" class="windowIFrame col-md-5 col-md-offset-7"></iframe>');
                                    $("#infoWindowContainer").html(content);
                                    $("#infoWindowContainer").removeClass('hide');
                                    event.preventDefault();
                                });

                                google.earth.addEventListener(ss_marker, 'mouseover', function(event) {
                                    var condition1 = ($.trim(this.pl) && $.trim(this.pl) != 'N/A'),
                                    condition2 = ($.trim(this.rta) && $.trim(this.rta) != 'N/A');

                                    if(condition1 || condition2) {
                                        var pl = $.trim(this.pl) ? this.pl : "N/A",
                                            rta = $.trim(this.rta) ? this.rta : "N/A",
                                            info_html = '';

                                        // Create hover infowindow html content
                                        info_html += '<table class="table table-responsive table-bordered table-hover">';
                                        info_html += '<tr><td><strong>Packet Drop</strong></td><td><strong>'+pl+'</strong></td></tr>';
                                        info_html += '<tr><td><strong>Latency</strong></td><td><strong>'+rta+'</strong></td></tr>';
                                        info_html += '</table>';

                                        setTimeout(function() {
                                            openGoogleEarthBaloon(info_html, ss_marker);
                                        }, 20);
                                    }
                                });

                                google.earth.addEventListener(ss_marker, 'mouseout', function(event) {
                                    ge.setBalloon(null);
                                });
                            }(ss_marker));
                            
                            allMarkersObject_earth['sub_station']['ss_'+ss_marker.name] = ss_marker;
                            allMarkersArray_earth.push(ss_marker);

                        } else if (window.location.pathname.indexOf("white_background") > -1) {

                            var iconImageObj = base_url+"/"+ss_marker_data.data.markerUrl,
                                ss_marker_icon = ss_marker_data.data.markerUrl ? iconImageObj : "";

                            /*Create SS Marker Object*/
                            var ss_marker_object = {};
                            ss_marker_object = {
                                position         :  new OpenLayers.LonLat(ss_marker_data.data.lon, ss_marker_data.data.lat),
                                ptLat            :  ss_marker_data.data.lat,
                                ptLon            :  ss_marker_data.data.lon,
                                map              :  'current',
                                icon             :  ss_marker_icon,
                                oldIcon          :  ss_marker_icon,
                                clusterIcon      :  ss_marker_icon,
                                pointType        :  "sub_station",
                                dataset          :  ss_perf_info,
                                bhInfo           :  [],
                                poll_info        :  [],
                                pl               :  ss_pl,
                                rta              :  ss_rta,
                                antenna_height   :  ss_marker_data.data.antenna_height,
                                name             :  ss_marker_data.name,
                                technology       :  ss_marker_data.data.technology,
                                bs_name          :  gisData.bs_name,
                                bs_sector_device :  sector_device,
                                filter_data      :  {"bs_name" : gisData.bs_name, "sector_name" : sector_ip, "ss_name" : ss_marker_data.name, "bs_id" : gisData.bs_id, "sector_id" : sector_id},
                                device_name      :  ss_marker_data.device_name,
                                ss_ip            :  ss_marker_data.data.substation_device_ip_address,
                                sector_ip        :  sector_ip,
                                zIndex           :  200,
                                hasPerf          :  0,
                                optimized        :  false,
                                isActive         :  1,
                                layerReference   :  ccpl_map.getLayersByName("Markers")[0]
                            };

                            var size = new OpenLayers.Size(32, 37);
                            /*Create SS Marker*/
                            var ss_marker = whiteMapClass.createOpenLayerVectorMarker(size, ss_marker_icon, ss_marker_data.data.lon, ss_marker_data.data.lat, ss_marker_object);
                            // ccpl_map.getLayersByName("Markers")[0].addFeatures([ss_marker]);

                            new_plotted_ss.push(ss_marker);

                            bs_ss_markers.push(ss_marker);
                            markersMasterObj['SS'][String(ss_marker_data.data.lat)+ ss_marker_data.data.lon]= ss_marker;
                            markersMasterObj['SSNamae'][String(ss_marker_data.device_name)]= ss_marker;
                            allMarkersObject_wmap['sub_station']['ss_'+ss_marker_data.name] = ss_marker;
                            allMarkersArray_wmap.push(ss_marker);
                            /*Push SS marker to pollableDevices array*/
                            pollableDevices.push(ss_marker)

                            // ccpl_map.getLayersByName('Markers')[0].addFeatures([ss_marker]);

                            var hide_flag = !$("#show_hide_label")[0].checked;

                            if(last_selected_label && $.trim(last_selected_label)) {
                                var labelHtml = "";
                                for(var z=ss_marker.dataset.length;z--;) {
                                    if($.trim(ss_marker.dataset[z]['name']) == $.trim(last_selected_label)) {
                                        labelHtml += "("+$.trim(ss_marker.dataset[z]['title'])+" - "+$.trim(ss_marker.dataset[z]['value'])+")";
                                    }
                                }
                                // If any html created then show label on ss
                                if(labelHtml) {
                                    var toolTip_infobox = new OpenLayers.Popup(key,
                                        new OpenLayers.LonLat(ss_marker.ptLon,ss_marker.ptLat),
                                        null,
                                        labelHtml,
                                        false
                                    );
                                    
                                    ccpl_map.addPopup(toolTip_infobox);
                                    toolTip_infobox.updateSize();

                                    tooltipInfoLabel['ss_'+ss_marker.name] = toolTip_infobox;    
                                }
                            }
                        } else {

                            /*Create SS Marker Object*/
                            var ss_marker_object = {};
                            ss_marker_object = {
                                position         :  new google.maps.LatLng(ss_marker_data.data.lat,ss_marker_data.data.lon),
                                ptLat            :  ss_marker_data.data.lat,
                                ptLon            :  ss_marker_data.data.lon,
                                map              :  mapInstance,
                                icon             :  new google.maps.MarkerImage(base_url+"/"+ss_marker_data.data.markerUrl,null,null,null,new google.maps.Size(32,37)),
                                oldIcon          :  new google.maps.MarkerImage(base_url+"/"+ss_marker_data.data.markerUrl,null,null,null,new google.maps.Size(32,37)),
                                clusterIcon      :  new google.maps.MarkerImage(base_url+"/"+ss_marker_data.data.markerUrl,null,null,null,new google.maps.Size(32,37)),
                                pointType        :  "sub_station",
                                dataset          :  ss_perf_info,
                                bhInfo           :  [],
                                poll_info        :  [],
                                pl               :  ss_pl,
                                rta              :  ss_rta,
                                antenna_height   :  ss_marker_data.data.antenna_height,
                                name             :  ss_marker_data.name,
                                bs_name          :  gisData.bs_name,
                                bs_sector_device :  sector_device,
                                filter_data      :  {"bs_name" : gisData.bs_name, "sector_name" : sector_ip, "ss_name" : ss_marker_data.name, "bs_id" : gisData.bs_id, "sector_id" : sector_id},
                                device_name      :  ss_marker_data.device_name,
                                ss_ip            :  ss_marker_data.data.substation_device_ip_address,
                                technology       :  ss_marker_data.data.technology,
                                sector_ip        :  sector_ip,
                                zIndex           :  200,
                                hasPerf          :  0,
                                optimized        :  false,
                                isActive         :  1
                            };

                            /*Create SS Marker*/
                            var ss_marker = new google.maps.Marker(ss_marker_object);

                            new_plotted_ss.push(ss_marker);
                            
                            /*Add BS Marker To Cluster*/
                            masterClusterInstance.addMarker(ss_marker);

                            markersMasterObj['SS'][String(ss_marker_data.data.lat)+ ss_marker_data.data.lon]= ss_marker;
                            markersMasterObj['SSNamae'][String(ss_marker_data.device_name)]= ss_marker;

                            /*Add the master marker to the global master markers array*/
                            masterMarkersObj.push(ss_marker);

                            // if(window.location.pathname.indexOf("googleEarth") > -1) {
                                
                            // } else if (window.location.pathname.indexOf("white_background") > -1) {
                                
                            // } else {

                            // }

                            allMarkersObject_gmap['sub_station']['ss_'+ss_marker.name] = ss_marker;
                            allMarkersArray_gmap.push(ss_marker);
                            /*Add parent markers to the OverlappingMarkerSpiderfier*/
                            oms_ss.addMarker(ss_marker);

                            /*Push SS marker to pollableDevices array*/
                            pollableDevices.push(ss_marker)

                            var hide_flag = !$("#show_hide_label")[0].checked;

                            if(last_selected_label && $.trim(last_selected_label)) {
                                var labelHtml = "";
                                for(var z=ss_marker.dataset.length;z--;) {
                                    if($.trim(ss_marker.dataset[z]['name']) == $.trim(last_selected_label)) {
                                        labelHtml += "("+$.trim(ss_marker.dataset[z]['title'])+" - "+$.trim(ss_marker.dataset[z]['value'])+")";
                                    }
                                }
                                // If any html created then show label on ss
                                if(labelHtml) {
                                    var toolTip_infobox = new InfoBox({
                                        content: labelHtml,
                                        boxStyle: {
                                            border: "1px solid #B0AEAE",
                                            background: "white",
                                            textAlign: "center",
                                            fontSize: "10px",
                                            color: "black",
                                            padding: '2px',
                                            borderRadius: "5px",
                                            width : '110px'
                                        },
                                        pixelOffset : new google.maps.Size(-120,-10),
                                        disableAutoPan: true,
                                        position: ss_marker.getPosition(),
                                        closeBoxURL: "",
                                        isHidden: hide_flag,
                                        enableEventPropagation: true,
                                        zIndex: 80
                                    });
                                    toolTip_infobox.open(mapInstance, ss_marker);
                                    tooltipInfoLabel['ss_'+ss_marker_data.name] = toolTip_infobox;
                                }
                            }
                        }

                        var ss_info = {
                                "info" : ss_marker_data.data.param.sub_station ? ss_marker_data.data.param.sub_station : [],
                                "antenna_height" : ss_marker_data.data.antenna_height
                            },
                            base_info = {
                                "info" : bs_object.data.param.base_station ? bs_object.data.param.base_station : [],
                                "antenna_height" : bs_object.data.antenna_height
                            },
                            sect_height = sector_marker ? sector_marker.antenna_height : 0;


                        startEndObj["nearEndLat"] = bs_object.data.lat;
                        startEndObj["nearEndLon"] = bs_object.data.lon;

                        startEndObj["endLat"] = ss_marker_data.data.lat;
                        startEndObj["endLon"] = ss_marker_data.data.lon;

                        /*Link color object*/
                        linkColor = ss_marker_data.data.link_color ? ss_marker_data.data.link_color : 'rgba(74,72,94,0.58)';

                        if(window.location.pathname.indexOf("googleEarth") > -1) {
                            /*Create the link between BS & SS or Sector & SS*/
                            var ss_link_line = earth_self.createLink_earth(startEndObj,linkColor,base_info,ss_info,sect_height,sector_ip,ss_marker_data.name,bs_object.name,bs_object.id);
                            ssLinkArray.push(ss_link_line);
                            ssLinkArray_filtered = ssLinkArray;
                            try {
                                ss_link_line.setVisibility(true);
                                ss_link_line.map = 'current';
                            } catch(e) {
                                // console.log(e);
                            }
                            
                            allMarkersObject_earth['path']['line_'+ss_marker_data.name] = ss_link_line;

                            allMarkersArray_earth.push(ss_link_line);
                        } else if (window.location.pathname.indexOf('white_background') > -1) {
                            /*Create the link between BS & SS or Sector & SS*/
                            var ss_link_line = whiteMapClass.plotLines_wmap(startEndObj,linkColor,base_info,ss_info,sect_height,sector_ip,ss_marker_data.name,bs_object.name,bs_object.id);

                            ccpl_map.getLayersByName("Lines")[0].addFeatures([ss_link_line]);
                            ssLinkArray.push(ss_link_line);
                            ssLinkArray_filtered = ssLinkArray;
                            allMarkersObject_wmap['path']['line_'+ss_marker_data.name] = ss_link_line;
                            markersMasterObj['Lines'][String(startEndObj.startLat)+ startEndObj.startLon+ startEndObj.endLat+ startEndObj.endLon]= ss_link_line;
                            markersMasterObj['LinesName'][String(bs_object.name)+ ss_marker_data.name]= ss_link_line;
                            allMarkersArray_wmap.push(ss_link_line);
                        } else {
                            /*Create the link between BS & SS or Sector & SS*/
                            var ss_link_line = gmap_self.createLink_gmaps(startEndObj,linkColor,base_info,ss_info,sect_height,sector_ip,ss_marker_data.name,bs_object.name,bs_object.id);
                            ssLinkArray.push(ss_link_line);
                            ssLinkArray_filtered = ssLinkArray;
                            ss_link_line.setMap(mapInstance);
                            
                            allMarkersObject_gmap['path']['line_'+ss_marker_data.name] = ss_link_line;

                            allMarkersArray_gmap.push(ss_link_line);
                        }

                        if(ss_marker_data.data.perf_value || sector_perf_val) {

                            // Create Label for Perf Value
                            var existing_index = -1;
                            for (var x = 0; x < labelsArray.length; x++) {
                                var move_listener_obj = labelsArray[x].moveListener_;
                                if (move_listener_obj) {
                                    var keys_array = Object.keys(move_listener_obj);
                                    for(var z=0;z<keys_array.length;z++) {
                                        if(typeof move_listener_obj[keys_array[z]] == 'object') {
                                           if((move_listener_obj[keys_array[z]] && move_listener_obj[keys_array[z]]["name"]) && (move_listener_obj[keys_array[z]] && move_listener_obj[keys_array[z]]["bs_name"])) {
                                                if(($.trim(move_listener_obj[keys_array[z]]["name"]) == $.trim(ss_marker.name)) && ($.trim(move_listener_obj[keys_array[z]]["bs_name"]) == $.trim(ss_marker.bs_name))) {
                                                    existing_index = x;
                                                    if(window.location.pathname.indexOf("googleEarth") > -1) {
                                                        labelsArray[x].setVisibility(false);
                                                    } else if (window.location.pathname.indexOf("white_background") > -1) {
                                                        labelsArray[x].destroy();
                                                    } else {
                                                        labelsArray[x].close();
                                                    }
                                                }
                                           }
                                        }
                                    }
                                }
                            }
                            
                            /*Remove that label from array*/
                            if (existing_index >= 0) {
                                labelsArray.splice(existing_index, 1);
                            }
                            
                            var ss_val = ss_marker_data.data.perf_value,
                                perf_val = "";

                            if(sector_marker) {
                                if(ss_val && sector_perf_val) {
                                    perf_val = "("+ss_val+", "+sector_perf_val+")";
                                } else if(ss_val && !sector_perf_val) {
                                    perf_val = "("+ss_val+", N/A)";
                                } else if(!ss_val && sector_perf_val) {
                                    perf_val = "(N/A, "+sector_perf_val+")";
                                } else {
                                    perf_val = "";
                                }
                            } else if(sector_polygon) {
                                perf_val = "("+ss_val+")";
                            }

                            if($.trim(perf_val)) {

                                if(window.location.pathname.indexOf("googleEarth") > -1) {
                                    ss_marker_data.perf_val = perf_val;
                                    //couldn't find any option to draw Label with Google Earth, so plese check the values on mouse hover ballon
                                } else if (window.location.pathname.indexOf("white_background") > -1) {
                                   var toolTip_infobox = new OpenLayers.Popup("perfLabel_"+ss_marker.name,
                                        new OpenLayers.LonLat(ss_marker.ptLon,ss_marker.ptLat),
                                        null,
                                        perf_val,
                                        false
                                    );
                                    ccpl_map.addPopup(toolTip_infobox);
                                    toolTip_infobox.updateSize(); 
                                    labelsArray.push(toolTip_infobox);
                                } else {
                                    var perf_infobox = new InfoBox({
                                        content: perf_val,
                                        boxStyle: {
                                            border: "1px solid #B0AEAE",
                                            background: "white",
                                            textAlign: "center",
                                            fontSize: "10px",
                                            color: "black",
                                            padding: '2px',
                                            width : '90px'
                                        },
                                        pixelOffset : new google.maps.Size(10,-10),
                                        disableAutoPan: true,
                                        position: ss_marker.getPosition(),
                                        closeBoxURL: "",
                                        isHidden: hide_flag,
                                        enableEventPropagation: true,
                                        zIndex: 80
                                    });

                                    perf_infobox.open(mapInstance, ss_marker);
                                    labelsArray.push(perf_infobox);
                                }
                            }
                        }
                    }//Sub-Station Loop End

                    if (window.location.pathname.indexOf("white_background") > -1) {
                        ccpl_map.getLayersByName("Markers")[0].features = new_plotted_ss.concat(ccpl_map.getLayersByName("Markers")[0].features);
                        ccpl_map.getLayersByName("Markers")[0].strategies[0].features = new_plotted_ss.concat(ccpl_map.getLayersByName("Markers")[0].features);

                        ccpl_map.getLayersByName("Markers")[0].redraw();
                        ccpl_map.getLayersByName("Markers")[0].strategies[0].recluster();
                    }

                // Remove sub-station from google maps - end
                } else {
                    if(sector_polygon) {
                        var ss_marker_obj = "",
                            ss_name_array = [];

                        if(window.location.pathname.indexOf("googleEarth") > -1) {
                            ss_marker_obj = allMarkersObject_earth['sub_station'];
                        } else if (window.location.pathname.indexOf("white_background") > -1) {
                            ss_marker_obj = allMarkersObject_wmap['sub_station'];
                        } else {
                            ss_marker_obj = allMarkersObject_gmap['sub_station'];
                        }
                        for(key in ss_marker_obj) {
                            var current_old_ss = ss_marker_obj[key],
                                condition1 = current_old_ss.filter_data.bs_id == gisData.bs_id,
                                condition2 = current_old_ss.filter_data.sector_name == sector_ip,
                                condition3 = current_old_ss.filter_data.sector_id == sector_id;

                            if(condition1 && condition2 && condition3) {
                                ss_name_array.push(current_old_ss.name);
                            }
                        }

                        for(var x=0;x<ss_name_array.length;x++) {
                            if(window.location.pathname.indexOf("googleEarth") > -1) {
                                // Remove Line from map & array
                                if(allMarkersObject_earth['path']['line_'+ss_name_array[x]]) {
                                    if(startEndObj["startLat"] && startEndObj["startLon"]) {

                                        var current_line = allMarkersObject_earth['path']['line_'+ss_name_array[x]];

                                        var lineString = ge.createLineString('');
                                        current_line.setGeometry(lineString);
                                        // Add LineString points
                                        lineString.getCoordinates().pushLatLngAlt((+startEndObj.startLat), (+startEndObj.startLon), 0);
                                        lineString.getCoordinates().pushLatLngAlt((+current_line.ss_lat), (+current_line.ss_lon), 0);
                                    }
                                }
                            } else if (window.location.pathname.indexOf("white_background") > -1) {
                                // Remove Line from map & array
                                if(allMarkersObject_wmap['path']['line_'+ss_name_array[x]]) {
                                    if(startEndObj["startLat"] && startEndObj["startLon"]) {
                                        var current_line = allMarkersObject_gmap['path']['line_'+ss_name_array[x]];
                                        var pathDataObject = new OpenLayers.Geometry.LineString([
                                            new OpenLayers.Geometry.Point(startEndObj["startLon"], startEndObj["startLat"]),
                                            new OpenLayers.Geometry.Point(current_line.ss_lon,current_line.ss_lat)
                                        ]);
                                        current_line.geometry = pathDataObject;
                                        current_line.layer.refresh();
                                    }
                                }
                            } else {
                                // Remove Line from map & array
                                if(allMarkersObject_gmap['path']['line_'+ss_name_array[x]]) {
                                    if(startEndObj["startLat"] && startEndObj["startLon"]) {

                                        var current_line = allMarkersObject_gmap['path']['line_'+ss_name_array[x]],
                                            new_path = [
                                            new google.maps.LatLng(startEndObj["startLat"],startEndObj["startLon"]),
                                            new google.maps.LatLng(current_line.ss_lat,current_line.ss_lon)
                                        ]
                                        current_line.setOptions({
                                            path : new_path
                                        });
                                    }
                                }
                            }
                        }
                    } else {
                        // pass
                    }
                }
            }// Sectors Loop End

            // Update loki db object start
            for(var i=0;i<connected_sectors.length;i++) {
                for(var j=0;j<sectorArray.length;j++) {
                    if(sectorArray[j].sub_station && sectorArray[j].sub_station.length > 0) {
                        if((connected_sectors[i].sector_configured_on_device == sectorArray[j].device_name) && (connected_sectors[i].sector_configured_on == sectorArray[j].ip_address)) {
                            bs_object.data.param.sector[i].sub_station = sectorArray[j].sub_station;
                        }
                    }
                }
            }

            // Update Loki Object
            all_devices_loki_db.update(bs_object);

            // Update loki db object end

            
            // Show New Plotted SS Markers
            // setTimeout(function() {
            //     if(window.location.pathname.indexOf("white_background") > -1) {
            //         for (var i = 0; i < new_plotted_ss.length; i++) {
            //             showOpenLayerFeature(new_plotted_ss[i]);
            //         }
            //     } else if(window.location.pathname.indexOf("googleEarth") > -1) {
            //         for (var i = 0; i < new_plotted_ss.length; i++) {

            //         }
            //     } else {
            //         for (var i = 0; i < new_plotted_ss.length; i++) {
            //             new_plotted_ss[i].setMap(mapInstance);
            //         }
            //     }
            //     callback(true);
            // }, 200);
            callback(true);
        } else {
            callback(true);
        }
    };

    /*
     Utility function to find a specific device with name from the Ajax response data
     */
    this.findObjectbyDeviceName = function (deviceName) {
        var gisData = this.gisData;
        //Loop through the sector in performance data
        for (var i = 0; i < gisData["param"]["sector"].length; i++) {
            //If we find device_name to the given deviceName in param
            if (gisData["param"]["sector"][i]["device_name"] == deviceName) {
                //Return the sector
                return gisData["param"]["sector"][i];
            }
        }
    }

    /*
     This function calculate the Performance Value for a key from the GIS Data.
     If Substation value is defined, then we return SubStation value
     Else, we return Defualt Value from sectir configuration
     */
    this.calculatePerformanceValue = function (key, device, ssName) {
        var gisData = this.gisData;

        //Loop through GIS Sector Data
        for (var i = 0; i < gisData["param"]["sector"].length; i++) {
            //If Gis Sector Name== device
            if (gisData["param"]["sector"][i] && gisData["param"]["sector"][i]["device_name"] == device) {
                if(ssName) {
                    //Loop inside device Sub Stations
                    for(var j = 0; j < gisData["param"]["sector"][i]["sub_station"].length; j++) {
                        //If SubStation name== devinceName passed
                        if (gisData["param"]["sector"][i]["sub_station"][j]["device_name"] == ssName) {
                            //Check if value is defined in SubStation
                            if (gisData["param"]["sector"][i]["sub_station"][j]["performance_data"][key]) {
                                //return the value
                                return gisData["param"]["sector"][i]["sub_station"][j]["performance_data"][key];
                            } else {
                                //return default value
                                return gisData["param"]["sector"][i]["performance_data"][key];
                            }
                        }
                    }
                } else {
                    return gisData["param"]["sector"][i]["performance_data"][key];
                }
            }
        }
        return "";
    }

    /**
     * This function get uncommon data from 2 array
     * @method get_intersection_bs
     * @param {array} oldArray, It is the bs name array
     * @param {array} newArray, It is the bs name array
     */
    this.get_intersection_bs = function(oldArray,newArray) {

        var uncommon_bs = [];
        for(var i=0;i<newArray.length;i++) {
            var current_new_bs = newArray[i];
            if(oldArray.indexOf(current_new_bs) == -1) {
                uncommon_bs.push(current_new_bs);
            }
        }

        /*return the uncommon or different bs list*/
        return uncommon_bs;
    };
}
