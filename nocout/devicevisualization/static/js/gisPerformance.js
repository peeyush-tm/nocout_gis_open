//Global Variables
var recallPerf = "",
    current_bs_list = [],
    perf_fetched_devices = [],
    perf_self = "",
    hiddenIconObj = "",
    crossLabelHTML = "<i class='fa fa-times'></i>",
    crossLabelStyle = {
        background  :   "transparent",
        fontSize    :   "16px",
        color       :   "red",
    },
    crossOffsetX = -7,
    crossOffsetY = -16,
    perfLabelStyle = {
        border        : "1px solid #B0AEAE",
        background    : "white",
        textAlign     : "center",
        fontSize      : "10px",
        color         : "black",
        padding       : '2px',
        borderRadius  : "5px",
        width         : '90px'
    },
    callsInProcess = false,
    gis_perf_call_instance = "";

if(!base_url) {
    var base_url = "";
    /*Set the base url of application for ajax calls*/
    if(window.location.origin) {
        base_url = window.location.origin;
    } else {
        base_url = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
    }
}

if((window.location.pathname.indexOf("googleEarth") > -1) || (window.location.pathname.indexOf("white_background") > -1)) {
    hiddenIconObj = base_url+'/static/img/icons/1x1.png';
} else {
    hiddenIconObj = new google.maps.MarkerImage(
        base_url+'/static/img/icons/1x1.png',
        null,
        null,
        null,
        null
    );
}

/**
 * [GisPerformance description]
 */
function GisPerformance() {
    //Is Frozen variable.. Get value from isFreeze Global Variable defined.
    this.isFrozen_ = 0;
    //Variable to hold GisData
    this.gisData = "";

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

        if(isPollingActive == 0  && isPerfCallStopped == 0) {
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
                callsInProcess = true;
                //Call waitAndSend function with BS Json Data and counter value
                perf_self.waitAndSend(perf_self.bsNamesList[counter], counter);
            } else {
                callsInProcess = false;
                //1 Minutes Timeout
                recallPerf = setTimeout(function () {
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

        if(gis_perf_call_instance) {
            try {
                gis_perf_call_instance.abort()
                gis_perf_call_instance = "";
            } catch(e) {
                // pass
            }
        }

        //Ajax Request
        gis_perf_call_instance = $.ajax({
            url: base_url + '/network_maps/perf_data/?base_stations=['+bs_id+']&ts='+selected_thematics+'&freeze_time=' + freezedAt,
            // url: base_url + '/static/new_perf_ptp.json',
            type: 'GET',
            dataType: 'json',
            //In success
            success: function (response) {

                var result = "";
                // Type check of response
                if(typeof response == 'string') {
                    result = JSON.parse(response);
                } else {
                    result = response;
                }

                var data = result.length ? result[0] : result;
                //If data is there
                if(data) {
                    //Store data in gisData
                    if(data.bs_id) {
                        if(window.location.pathname.indexOf("white_background") > -1) {
                            //Update Map with the data
                            perf_self.updateMap(data,function(response) {
                                //Send Request for the next counter
                                perf_self.sendRequest(counter);
                            });
                        } else if(window.location.pathname.indexOf("googleEarth") > -1) {
                            //Update Map with the data
                            perf_self.updateMap(data,function(response) {
                                //Send Request for the next counter
                                perf_self.sendRequest(counter);
                            });
                        } else {
                            var current_bs_in_bound = getMarkerInCurrentBound();
                            // If map Zoom level is greater than 11 then proceed.
                            if(mapInstance.getZoom() > 11) {
                                /*Check that the bsname is present in current bounds or not*/
                                if (current_bs_in_bound.indexOf(data.bs_id) > -1) {
                                    //Update Map with the data
                                    perf_self.updateMap(data,function(response) {
                                        //Send Request for the next counter
                                        perf_self.sendRequest(counter);
                                    });
                                } else {
                                    //Send Request for the next counter
                                    perf_self.sendRequest(counter);
                                }
                            }
                        }
                    } else {
                        if(window.location.pathname.indexOf("white_background") > -1 || window.location.pathname.indexOf("googleEarth") > -1) {
                            //Send Request for the next counter
                            perf_self.sendRequest(counter);
                        } else {
                            // If map Zoom level is greater than 11 then proceed.
                            if(mapInstance && mapInstance.getZoom() > 11) {
                                //Send Request for the next counter
                                perf_self.sendRequest(counter);
                            }
                        }
                    }
                }

            },
            //On Error, do nothing
            error: function (err) {
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
    this.updateMap = function (data,callback) {

        if(data) {
            //Step no. 1 => Find BS Station First
            var apiResponse = data,
                sectorArray = apiResponse.param.sector ? apiResponse.param.sector : [],
                bs_name = apiResponse.bs_name ? apiResponse.bs_name : "",
                perf_bh_info = apiResponse.bh_info ? apiResponse.bh_info : [],
                perf_bh_severity = apiResponse.bhSeverity ? apiResponse.bhSeverity : "",
                bs_marker = "",
                show_ss_len = $("#showAllSS:checked").length;

            if(window.location.pathname.indexOf("googleEarth") > -1) {
                bs_marker = allMarkersObject_earth['base_station']['bs_'+bs_name];
            } else if (window.location.pathname.indexOf("white_background") > -1) {
                bs_marker = allMarkersObject_wmap['base_station']['bs_'+bs_name];
            } else {
                bs_marker = allMarkersObject_gmap['base_station']['bs_'+bs_name];
            }

            // Update BH polled info to bs marker tooltip.
            if(bs_marker) {
                try {
                    bs_marker['bhInfo_polled'] = perf_bh_info;
                    bs_marker['bhSeverity'] = perf_bh_severity;
                } catch(e) {
                    // console.log(e);
                }
            }

            // BH info addition ended.

            var bs_loki_obj = all_devices_loki_db.where(function(obj) {
                    return obj.originalId == apiResponse.bs_id
                }),
                bs_object = bs_loki_obj.length > 0 ? JSON.parse(JSON.stringify(bs_loki_obj[0])) : [],
                connected_sectors = bs_object.data.param.sector,
                new_plotted_ss = [],
                bs_lat = bs_object.data.lat,
                bs_lon = bs_object.data.lon;

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
                    sector_tech = "",
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
                    sector_tech = sector_marker['technology'] ? sector_marker['technology'] : "";
                    var sector_pl = perf_self.getKeyValue(sector_perf_info,"pl",true),
                        sector_rta = perf_self.getKeyValue(sector_perf_info,"rta",true);
                    if(sector_icon) {
                        perf_self.updateMarkerIcon(sector_marker,sector_icon);
                    }

                    // Update the pl & rta values in sector marker object
                    try {
                        sector_marker['poll_info'] = sector_perf_info;
                        sector_marker['pl'] = sector_pl;
                        sector_marker['rta'] = sector_rta;
                    } catch(e) {
                        // console.log(e);
                    }
                    
                    // Save start position of line in global object
                    startEndObj["startLat"] = bs_lat;
                    startEndObj["startLon"] = bs_lon;

                    startEndObj["sectorLat"] = bs_lat;
                    startEndObj["sectorLon"] = bs_lon;

                } else if(sector_polygon) {

                    sector_tech = sector_polygon['technology'] ? sector_polygon['technology'] : "";

                    var azimuth_angle = current_sector.azimuth_angle && current_sector.azimuth_angle != 'NA' ? current_sector.azimuth_angle : 10,
                        beam_width = current_sector.beam_width && current_sector.beam_width != 'NA' ? current_sector.beam_width : 10,
                        radius = current_sector.radius && current_sector.radius != 'NA' ? current_sector.radius : 0.5,
                        sector_color = current_sector.color && current_sector.color != 'NA' ? current_sector.color : 'rgba(74,72,94,0.58)',
                        orientation = current_sector.polarization ? current_sector.polarization : sector_polygon.polarisation;

                    gmap_self.createSectorData(bs_lat,bs_lon,radius,azimuth_angle,beam_width,orientation,function(pointsArray) {

                        var halfPt = Math.floor(pointsArray.length / (+2)),
                            polyStartLat = "",
                            polyStartLon = "",
                            polyPathArray = [],
                            polyPoints= "";

                        if(halfPt == 1) {
                            var latLonArray = [
                                pointsArray[0],pointsArray[1]
                            ];
                            var centerPosition = gmap_self.getMiddlePoint(latLonArray);

                            polyStartLat = centerPosition.lat * 180 / Math.PI;
                            polyStartLon = centerPosition.lon * 180 / Math.PI;
                        } else {
                            polyStartLat = pointsArray[halfPt].lat;
                            polyStartLon = pointsArray[halfPt].lon;
                        }

                        if(window.location.pathname.indexOf("googleEarth") > -1) {
                            try {

                                // Add points for poly coordinates.
                                polyPoints = ge.createLinearRing('');
                                polyPoints.setAltitudeMode(ge.ALTITUDE_RELATIVE_TO_GROUND);
                                for(var i=0;i<pointsArray.length;i++) {
                                    polyPoints.getCoordinates().pushLatLngAlt(pointsArray[i].lat, pointsArray[i].lon, 700);
                                }
                                // Set Polygon path
                                sector_polygon.setOuterBoundary(polyPoints);

                                var poly_sector_color = earth_self.makeRgbaObject(sector_color);
                                // Color can also be specified by individual color components.
                                var polyColor = sector_polygon.getStyleSelector().getPolyStyle().getColor();

                                polyColor.setA(200);
                                polyColor.setR((+poly_sector_color.r));
                                polyColor.setG((+poly_sector_color.g));
                                polyColor.setB((+poly_sector_color.b));

                                // Update Sector Info
                                sector_polygon["azimuth"] = azimuth_angle;;
                                sector_polygon["beam_width"] = beam_width;;
                                sector_polygon["polarisation"] = orientation;;
                                sector_polygon["radius"] = radius;
                            } catch(e) {
                                // console.log(e.name);
                                // console.log(e.message);
                                // console.debug(e);
                            }

                        } else if(window.location.pathname.indexOf("white_background") > -1) {
                            for(var i=0;i<pointsArray.length;i++) {
                                var pt = new OpenLayers.Geometry.Point(pointsArray[i].lon, pointsArray[i].lat);
                                polyPathArray.push(pt);
                            }
                            
                            try {
                                // Update Sector Fill Color
                                sector_polygon.style.fillColor = sector_color;
                                // Update Sector Info
                                sector_polygon["azimuth"]      =  azimuth_angle;;
                                sector_polygon["beam_width"]   =  beam_width;;
                                sector_polygon["polarisation"] =  orientation;;
                                sector_polygon["radius"]       =  radius;
                                // Destroy Previous Geometry
                                sector_polygon["path"] = polyPathArray;
                                sector_polygon.geometry.components[0].components = polyPathArray;

                            } catch(e) {
                                // console.log(e);
                            }

                        } else {
                            for(var i=0;i<pointsArray.length;i++) {
                                var pt = new google.maps.LatLng(pointsArray[i].lat,pointsArray[i].lon);
                                polyPathArray.push(pt);
                            }

                            // Update sector Path, fillColor & other properties.
                            sector_polygon.setOptions({
                                path         :  polyPathArray,
                                fillColor    :  sector_color,
                                azimuth      :  azimuth_angle,
                                beam_width   :  beam_width,
                                polarisation :  orientation,
                                radius       :  radius
                            });
                        }

                        startEndObj["startLat"] = polyStartLat;
                        startEndObj["startLon"] = polyStartLon;

                        startEndObj["sectorLat"] = polyStartLat;
                        startEndObj["sectorLon"] = polyStartLon;
                        
                        // Add polled info to sector polygon object
                        try {
                            sector_polygon['poll_info'] = sector_perf_info;
                        } catch(e) {
                            // console.log(e);
                        }
                    });

                } else {
                    // pass
                }
                
                // If any sector marker or polygon exist then continue
                if(sector_marker || sector_polygon) {
                    // If any ss exist in response then clear old ss & their connection lines from map
                    if(sub_station.length > 0) {
                        // Loop to remove ss,line & label for current sector from map.
                        for(var xxx=0;xxx<connected_sectors.length;xxx++) {
                            if(sectorArray[i].sub_station && sectorArray[i].sub_station.length > 0) {
                                var condition1 = connected_sectors[xxx].sector_configured_on_device == sectorArray[i].device_name;
                                    condition2 = connected_sectors[xxx].sector_configured_on == sectorArray[i].ip_address;
                                    condition3 = connected_sectors[xxx].sector_id == sectorArray[i].sector_id;
                                if(condition1 && condition2 && condition3) {
                                    var connected_sub_stations = sectorArray[i].sub_station;
                                    for(var key=0; key< connected_sub_stations.length; key++) {
                                        var ss_name = connected_sub_stations[key]['name'] ? connected_sub_stations[key]['name'] : "";
                                        if(connected_sub_stations[key] && ss_name) {
                                            perf_self.removeOldSS(ss_name);
                                        }
                                    }
                                }
                            }
                        }

                        var plotSS = perf_self.isSectorDevicesPlottable(current_sector,connected_sectors);
                        // If sectors satisfied filters condition only then plot SS
                        if(plotSS) {
                            // Loop to plot new sub-stations
                            for(var j=0;j<sub_station.length;j++) {

                                var ss_marker_data = sub_station[j],
                                    ss_static_info = ss_marker_data.data.param.sub_station,
                                    ss_polled_info = ss_marker_data.data.param.polled_info,
                                    ss_tooltip_info = JSON.parse(JSON.stringify(ss_static_info)).concat(JSON.parse(JSON.stringify(ss_polled_info))),
                                    ss_pl = perf_self.getKeyValue(ss_tooltip_info,"pl",true),
                                    ss_rta = perf_self.getKeyValue(ss_tooltip_info,"rta",true),
                                    ckt_id_val = perf_self.getKeyValue(ss_tooltip_info,"cktid",true),
                                    ss_ip_address = perf_self.getKeyValue(ss_tooltip_info,"ss_ip",true),
                                    ss_perf_url = ss_marker_data.data.perf_page_url ? ss_marker_data.data.perf_page_url : "",
                                    ss_inventory_url = ss_marker_data.data.inventory_url ? ss_marker_data.data.inventory_url : "";

                                // var ss_marker_object = {};
                                var ss_marker_object = {
                                    ptLat            :  ss_marker_data.data.lat,
                                    ptLon            :  ss_marker_data.data.lon,
                                    pointType        :  "sub_station",
                                    dataset          :  ss_static_info,
                                    bhInfo           :  [],
                                    poll_info        :  ss_polled_info,
                                    pl               :  ss_pl,
                                    rta              :  ss_rta,
                                    antenna_height   :  ss_marker_data.data.antenna_height,
                                    name             :  ss_marker_data.name,
                                    technology       :  sector_tech,
                                    perf_url         :  ss_perf_url,
                                    inventory_url    :  ss_inventory_url,
                                    bs_name          :  apiResponse.bs_name,
                                    bs_sector_device :  sector_device,
                                    filter_data      :  {"bs_name" : apiResponse.bs_name, "sector_name" : sector_ip, "ss_name" : ss_marker_data.name, "bs_id" : apiResponse.bs_id, "sector_id" : sector_id},
                                    device_name      :  ss_marker_data.device_name,
                                    ss_ip            :  ss_ip_address,
                                    sector_ip        :  sector_ip,
                                    cktId            :  ckt_id_val,
                                    zIndex           :  200,
                                    optimized        :  false,
                                    isActive         :  1,
                                    windowTitle      : "Sub Station"
                                };

                                if(window.location.pathname.indexOf("googleEarth") > -1) {
                                    
                                    ss_marker_object['map'] = 'current';
                                    ss_marker_object['icon'] = base_url+"/"+ss_marker_data.data.markerUrl;
                                    ss_marker_object['oldIcon'] = base_url+"/"+ss_marker_data.data.markerUrl;
                                    ss_marker_object['clusterIcon'] = base_url+"/"+ss_marker_data.data.markerUrl;

                                    var ss_marker = earth_self.makePlacemark(
                                        base_url+"/"+ss_marker_data.data.markerUrl,
                                        ss_marker_data.data.lat,
                                        ss_marker_data.data.lon,
                                        'ss_'+ss_marker_data.id,
                                        ss_marker_object
                                    );

                                    // If show SS checkbox is unchecked then hide SS
                                    try {
                                        if(show_ss_len <= 0) {
                                            if(ss_marker.getVisibility()) {
                                                ss_marker['map'] = '';
                                                ss_marker.setVisibility(false);
                                            }
                                        }
                                    } catch(e) {
                                        // console.log(e);
                                    }

                                    (function(ss_marker) {
                                        google.earth.addEventListener(ss_marker, 'click', function(event) {
                                            // Clicked button 0 in case of left click n 2 in case of right click
                                            var clicked_button = 0;
                                            try {
                                                clicked_button = event.getButton();
                                            } catch(e) {
                                                // console.log(e);
                                            }

                                            if(clicked_button == 0) {
                                                var content = gmap_self.makeWindowContent(ss_marker);
                                                $("#google_earth_container").after('<iframe allowTransparency="true" style="position:absolute; top:35px; right:10px; overflow: auto; padding:0px; height:100%; max-height: 550px; overflow:auto; z-index:100;" class="windowIFrame col-md-4 col-md-offset-8"></iframe>');
                                                $("#infoWindowContainer").html(content);
                                                $("#infoWindowContainer").removeClass('hide');
                                            } else {
                                                var condition1 = ($.trim(this.pl) && $.trim(this.pl) != 'N/A'),
                                                    condition2 = ($.trim(this.rta) && $.trim(this.rta) != 'N/A');

                                                if(condition1 || condition2) {
                                                    var pl = $.trim(this.pl) ? this.pl : "N/A",
                                                        rta = $.trim(this.rta) ? this.rta : "N/A",
                                                        info_html = '';

                                                    // Create hover infowindow html content
                                                    info_html += '<table class="table table-responsive table-bordered table-hover">';
                                                    info_html += '<tr><td>Packet Drop</td><td>'+pl+'</td></tr>';
                                                    info_html += '<tr><td>Latency</td><td>'+rta+'</td></tr>';
                                                    info_html += '</table>';

                                                    setTimeout(function() {
                                                        openGoogleEarthBaloon(info_html, ss_marker);
                                                    }, 20);
                                                }
                                            }

                                            event.preventDefault();
                                        });
                                    }(ss_marker));
                                    
                                    allMarkersObject_earth['sub_station']['ss_'+ss_marker.name] = ss_marker;
                                    allMarkersArray_earth.push(ss_marker);

                                } else if (window.location.pathname.indexOf("white_background") > -1) {

                                    var iconImageObj = base_url+"/"+ss_marker_data.data.markerUrl,
                                        ss_marker_icon = ss_marker_data.data.markerUrl ? iconImageObj : "";

                                    /*Create SS Marker Object*/
                                    ss_marker_object['position'] = new OpenLayers.LonLat(ss_marker_data.data.lon, ss_marker_data.data.lat);
                                    ss_marker_object['map'] = 'current';
                                    ss_marker_object['icon'] = ss_marker_icon;
                                    ss_marker_object['oldIcon'] = ss_marker_icon;
                                    ss_marker_object['clusterIcon'] = ss_marker_icon;
                                    ss_marker_object['layerReference'] = ccpl_map.getLayersByName("Markers")[0];

                                    var other_size_obj = whiteMapClass.getMarkerSize_wmap(false),
                                        other_width = other_size_obj.width ? other_size_obj.width : whiteMapSettings.devices_size.medium.width,
                                        other_height = other_size_obj.height ? other_size_obj.height : whiteMapSettings.devices_size.medium.height;

                                    var size = new OpenLayers.Size(other_width, other_height);
                                    /*Create SS Marker*/
                                    var ss_marker = whiteMapClass.createOpenLayerVectorMarker(
                                        size,
                                        ss_marker_icon,
                                        ss_marker_data.data.lon,
                                        ss_marker_data.data.lat,
                                        ss_marker_object
                                    );
                                    
                                    // If show SS checkbox is unchecked then hide SS
                                    if(show_ss_len <= 0) {
                                        hideOpenLayerFeature(ss_marker);
                                    }

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
                                                labelHtml += "("+$.trim(ss_marker.dataset[z]['value'])+")";
                                            }
                                        }
                                        // If any html created then show label on ss
                                        if(labelHtml) {
                                            var toolTip_infobox = new OpenLayers.Popup('ss_'+ss_marker.name,
                                                new OpenLayers.LonLat(ss_marker.ptLon,ss_marker.ptLat),
                                                new OpenLayers.Size(110,25),
                                                labelHtml,
                                                false
                                            );
                                            ccpl_map.addPopup(toolTip_infobox);

                                            tooltipInfoLabel['ss_'+ss_marker.name] = toolTip_infobox;

                                            if($("#ss_"+ss_marker.name).length > 0) {
                                                // Shift label to left side of markers
                                                var current_left = $("#ss_"+ss_marker.name).position().left;
                                                current_left = current_left - 125;
                                                $("#ss_"+ss_marker.name).css("left",current_left+"px");
                                            }

                                            // If show/hide checkbox is unchecked then hide label
                                            if(hide_flag) {
                                                toolTip_infobox.hide();
                                            }
                                        }
                                    }
                                } else {

                                    var ss_icon_obj = gmap_self.getMarkerImageBySize(base_url+"/"+ss_marker_data.data.markerUrl,"other");

                                    ss_marker_object['position'] = new google.maps.LatLng(ss_marker_data.data.lat,ss_marker_data.data.lon);
                                    ss_marker_object['map'] = null;
                                    ss_marker_object['icon'] = ss_icon_obj;
                                    ss_marker_object['oldIcon'] = ss_icon_obj;
                                    ss_marker_object['clusterIcon'] = ss_icon_obj;
                                    
                                    if(show_ss_len > 0) {
                                        ss_marker_object['map'] = mapInstance;
                                    }

                                    /*Create SS Marker*/
                                    var ss_marker = new google.maps.Marker(ss_marker_object);
                                    
                                    /*Add SS Marker To Cluster*/
                                    masterClusterInstance.addMarkers([ss_marker],true);

                                    markersMasterObj['SS'][String(ss_marker_data.data.lat)+ ss_marker_data.data.lon]= ss_marker;
                                    markersMasterObj['SSNamae'][String(ss_marker_data.device_name)]= ss_marker;

                                    /*Add the master marker to the global master markers array*/
                                    masterMarkersObj.push(ss_marker);

                                    // If still marker exist then first remove it from object then add
                                    if(allMarkersObject_gmap['sub_station']['ss_'+ss_marker.name]) {
                                        // if map
                                        if(allMarkersObject_gmap['sub_station']['ss_'+ss_marker.name].map) {
                                            allMarkersObject_gmap['sub_station']['ss_'+ss_marker.name].setMap(null);
                                        }
                                        allMarkersObject_gmap['sub_station']['ss_'+ss_marker.name] = "";
                                    }

                                    allMarkersObject_gmap['sub_station']['ss_'+ss_marker.name] = ss_marker;
                                    // allMarkersArray_gmap.push(ss_marker);

                                    /*Add parent markers to the OverlappingMarkerSpiderfier*/
                                    oms_ss.addMarker(ss_marker);

                                    /*Push SS marker to pollableDevices array*/
                                    pollableDevices.push(ss_marker);

                                    var hide_flag = !$("#show_hide_label")[0].checked;

                                    if(last_selected_label) {
                                        var ss_actual_data = rearrangeTooltipArray(ss_toolTip_static,ss_marker.dataset),
                                            labelInfoObject = perf_self.getKeyValue(ss_actual_data,last_selected_label,false),
                                            labelHtml = "";

                                        if(labelInfoObject) {
                                            var shownVal = labelInfoObject['value'] ? $.trim(labelInfoObject['value']) : "NA";
                                            labelHtml += shownVal;
                                        }
                                        // If any html created then show label on ss
                                        if(labelHtml) {
                                            var toolTip_infobox = perf_self.createInfoboxLabel(
                                                labelHtml,
                                                ssParamLabelStyle,
                                                -120,
                                                -10,
                                                ss_marker.getPosition(),
                                                hide_flag
                                            );
                                            toolTip_infobox.open(mapInstance, ss_marker);
                                            tooltipInfoLabel['ss_'+ss_marker_data.name] = toolTip_infobox;
                                        }
                                    }

                                    // Right click event on sub-station marker
                                    google.maps.event.addListener(ss_marker, 'rightclick', function(e) {
                                        var condition1 = ($.trim(this.pl) && $.trim(this.pl) != 'N/A'),
                                            condition2 = ($.trim(this.rta) && $.trim(this.rta) != 'N/A');

                                        if(condition1 || condition2) {
                                            var pl = $.trim(this.pl) ? this.pl : "N/A",
                                                rta = $.trim(this.rta) ? this.rta : "N/A",
                                                info_html = '';

                                            // Create hover infowindow html content
                                            info_html += '<table class="table table-responsive table-bordered table-hover">';
                                            info_html += '<tr><td>Packet Drop</td><td>'+pl+'</td></tr>';
                                            info_html += '<tr><td>Latency</td><td>'+rta+'</td></tr>';
                                            info_html += '</table>';

                                            if(infowindow) {
                                                /*Set the content for infowindow*/
                                                infowindow.setContent(info_html);
                                                /*Shift the window little up*/
                                                infowindow.setOptions({pixelOffset: new google.maps.Size(0, -20)});
                                                /*Set The Position for InfoWindow*/
                                                infowindow.setPosition(new google.maps.LatLng(e.latLng.lat(),e.latLng.lng()));
                                                /*Open the info window*/
                                                infowindow.open(mapInstance);
                                            }
                                        }
                                    });

                                    // Mouseout event on sub-station marker
                                    // google.maps.event.addListener(ss_marker, 'mouseout', function() {
                                    //     var condition1 = ($.trim(this.pl) && $.trim(this.pl) != 'N/A'),
                                    //         condition2 = ($.trim(this.rta) && $.trim(this.rta) != 'N/A');

                                    //     if(condition1 || condition2) {
                                    //         if(infowindow) {
                                    //             infowindow.close();
                                    //         }
                                    //     }
                                    // });
                                }

                                var ss_info = {
                                        "info" : ss_marker_data.data.param.sub_station ? ss_marker_data.data.param.sub_station : [],
                                        "antenna_height" : ss_marker_data.data.antenna_height
                                    },
                                    base_info = {
                                        "info" : bs_object.data.param.base_station ? bs_object.data.param.base_station : [],
                                        "antenna_height" : bs_object.data.antenna_height
                                    },
                                    sect_height = sector_marker ? sector_marker.antenna_height : sector_polygon.antenna_height;


                                startEndObj["nearEndLat"] = bs_lat;
                                startEndObj["nearEndLon"] = bs_lon;

                                startEndObj["endLat"] = ss_marker_data.data.lat;
                                startEndObj["endLon"] = ss_marker_data.data.lon;

                                startEndObj["windowTitle"] = "BS-SS";
                                startEndObj["startTitle"] = "BS Info";
                                startEndObj["endTitle"] = "SS Info";

                                /*Link color object*/
                                var line_color = ss_marker_data.data.link_color;
                                linkColor = line_color && line_color != 'NA' ? line_color : 'rgba(74,72,94,0.58)';

                                var isLineChecked = $("#showConnLines:checked").length;

                                if(window.location.pathname.indexOf("googleEarth") > -1) {
                                    /*Create the link between BS & SS or Sector & SS*/
                                    var ss_link_line = earth_self.createLink_earth(
                                        startEndObj,
                                        linkColor,
                                        base_info,
                                        ss_info,
                                        sect_height,
                                        sector_ip,
                                        ss_marker_data.name,
                                        bs_object.name,
                                        bs_object.originalId,
                                        sector_id
                                    );
                                    ssLinkArray.push(ss_link_line);
                                    ssLinkArray_filtered = ssLinkArray;
                                    try {
                                        if(isLineChecked > 0) {
                                            ss_link_line.setVisibility(true);
                                            ss_link_line.map = 'current';
                                        } else {
                                            ss_link_line.setVisibility(false);
                                            ss_link_line.map = '';
                                        }
                                    } catch(e) {
                                        // console.log(e);
                                    }
                                    
                                    allMarkersObject_earth['path']['line_'+ss_marker_data.name] = ss_link_line;

                                    allMarkersArray_earth.push(ss_link_line);
                                } else if (window.location.pathname.indexOf('white_background') > -1) {
                                    /*Create the link between BS & SS or Sector & SS*/
                                    var ss_link_line = whiteMapClass.plotLines_wmap(
                                        startEndObj,
                                        linkColor,
                                        base_info,
                                        ss_info,
                                        sect_height,
                                        sector_ip,
                                        ss_marker_data.name,
                                        bs_object.name,
                                        bs_object.originalId,
                                        sector_id
                                    );

                                    ccpl_map.getLayersByName("Lines")[0].addFeatures([ss_link_line]);

                                    // If show Connection Line checkbox is unchecked then hide connection Line
                                    if(!isLineChecked > 0) {
                                        hideOpenLayerFeature(ss_link_line);
                                    }

                                    
                                    ssLinkArray.push(ss_link_line);
                                    ssLinkArray_filtered = ssLinkArray;
                                    allMarkersObject_wmap['path']['line_'+ss_marker_data.name] = ss_link_line;
                                    markersMasterObj['Lines'][String(startEndObj.startLat)+ startEndObj.startLon+ startEndObj.endLat+ startEndObj.endLon]= ss_link_line;
                                    markersMasterObj['LinesName'][String(bs_object.name)+ ss_marker_data.name]= ss_link_line;
                                    allMarkersArray_wmap.push(ss_link_line);

                                    // This is to show "X"(Cross) on line if pl is 100%
                                    if(ss_marker['pl'] && (ss_marker['pl'] == '100' || ss_marker['pl'] == '100%')) {
                                        
                                        var link_path_array = ss_link_line.path.components;

                                        // Calculate the center point lat lon to plot "X"
                                        var latLonArray = [
                                            {"lat" : link_path_array[0].y, "lon" : link_path_array[0].x},
                                            {"lat" : link_path_array[1].y, "lon" : link_path_array[1].x},
                                        ];

                                        var center_obj = gmap_self.getMiddlePoint(latLonArray),
                                            center_lat = center_obj.lat * 180 / Math.PI,
                                            center_lon = center_obj.lon * 180 / Math.PI;

                                        // Close the label if exist
                                        if(cross_label_array['line_'+ss_marker_data.name]) {
                                            // Remove the cross label
                                            cross_label_array['line_'+ss_marker_data.name].destroy();
                                            // Delete cross label from global object
                                            delete cross_label_array['line_'+ss_marker_data.name];
                                        }

                                        var crossLabelPosition = new OpenLayers.Geometry.Point(center_lon,center_lat);


                                        cross_label_array['line_'+ss_marker_data.name] = cross_label;

                                        if(isLineChecked > 0) {
                                            cross_label.show();
                                        } else {
                                            cross_label.hide();
                                        }
                                    } else {
                                        try {
                                            // Close the label if exist
                                            if(cross_label_array['line_'+ss_marker_data.name]) {
                                                // Remove the cross label
                                                cross_label_array['line_'+ss_marker_data.name].close();
                                                // Delete cross label from global object
                                                delete cross_label_array['line_'+ss_marker_data.name];
                                            }
                                        } catch(e) {
                                            // console.log(e);
                                        }
                                    }

                                } else {
                                    /*Create the link between BS & SS or Sector & SS*/

                                    // Unspiderify the marker
                                    if(oms) {
                                        oms.unspiderfy();
                                    }
                                    
                                    var ss_link_line = gmap_self.createLink_gmaps(
                                        startEndObj,
                                        linkColor,
                                        base_info,
                                        ss_info,
                                        sect_height,
                                        sector_ip,
                                        ss_marker_data.name,
                                        bs_object.name,
                                        bs_object.originalId,
                                        sector_id
                                    );
                                    ssLinkArray.push(ss_link_line);
                                    ssLinkArray_filtered = ssLinkArray;

                                    if(isLineChecked > 0) {
                                        ss_link_line.setMap(mapInstance);
                                    } else {
                                        ss_link_line.setMap(null);
                                    }

                                    // This is to show "X"(Cross) on line if pl is 100%
                                    if(ss_marker['pl'] && (ss_marker['pl'] == '100' || ss_marker['pl'] == '100%')) {
                                        
                                        var link_path_array = ss_link_line.getPath().getArray();

                                        // Calculate the center point lat lon to plot "X"
                                        var latLonArray = [
                                            {"lat" : link_path_array[0].lat(), "lon" : link_path_array[0].lng()},
                                            {"lat" : link_path_array[1].lat(), "lon" : link_path_array[1].lng()},
                                        ];

                                        var center_obj = gmap_self.getMiddlePoint(latLonArray),
                                            center_lat = center_obj.lat * 180 / Math.PI,
                                            center_lon = center_obj.lon * 180 / Math.PI;

                                        // Close the label if exist
                                        if(cross_label_array['line_'+ss_marker_data.name]) {
                                            // Remove the cross label
                                            cross_label_array['line_'+ss_marker_data.name].close();
                                            // Delete cross label from global object
                                            delete cross_label_array['line_'+ss_marker_data.name];
                                        }

                                        var crossLabelPosition = new google.maps.LatLng(center_lat,center_lon),
                                            cross_label = perf_self.createInfoboxLabel(
                                                crossLabelHTML,
                                                crossLabelStyle,
                                                crossOffsetX,
                                                crossOffsetY,
                                                crossLabelPosition,
                                                false
                                            );

                                        cross_label.open(mapInstance);
                                        cross_label_array['line_'+ss_marker_data.name] = cross_label;

                                        if(isLineChecked > 0) {
                                            cross_label.show();
                                        } else {
                                            cross_label.hide();
                                        }
                                    } else {
                                        try {
                                            // Close the label if exist
                                            if(cross_label_array['line_'+ss_marker_data.name]) {
                                                // Remove the cross label
                                                cross_label_array['line_'+ss_marker_data.name].close();
                                                // Delete cross label from global object
                                                delete cross_label_array['line_'+ss_marker_data.name];
                                            }
                                        } catch(e) {
                                            // console.log(e);
                                        }
                                    }
                                    
                                    allMarkersObject_gmap['path']['line_'+ss_marker_data.name] = ss_link_line;
                                    // allMarkersArray_gmap.push(ss_link_line);
                                }

                                // if(ss_marker_data.data.perf_value || sector_perf_val) {
                                // Create Label for Perf Value
                                var existing_index = -1;
                                for (var x = 0; x < labelsArray.length; x++) {
                                    if(window.location.pathname.indexOf("googleEarth") > -1) {
                                        // pass
                                    } else if (window.location.pathname.indexOf("white_background") > -1) {
                                        if(labelsArray[x].id == "perfLabel_"+ss_marker.name) {
                                            ccpl_map.removePopup(labelsArray[x]);
                                        }
                                    } else {
                                        var move_listener_obj = labelsArray[x].moveListener_;
                                        if (move_listener_obj) {
                                            var keys_array = Object.keys(move_listener_obj);
                                            for(var z=0;z<keys_array.length;z++) {
                                                if(typeof move_listener_obj[keys_array[z]] == 'object') {
                                                   if((move_listener_obj[keys_array[z]] && move_listener_obj[keys_array[z]]["name"]) && (move_listener_obj[keys_array[z]] && move_listener_obj[keys_array[z]]["bs_name"])) {
                                                        if(($.trim(move_listener_obj[keys_array[z]]["name"]) == $.trim(ss_marker.name)) && ($.trim(move_listener_obj[keys_array[z]]["bs_name"]) == $.trim(ss_marker.bs_name))) {
                                                            existing_index = x;
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
                                
                                var ss_val = ss_marker_data.data.perf_value ? ss_marker_data.data.perf_value : "N/A",
                                    perf_val = "";

                                if(sector_marker) {
                                    if(ss_val && sector_perf_val) {
                                        perf_val = "("+ss_val+", "+sector_perf_val+")";
                                    } else if(ss_val && !sector_perf_val) {
                                        perf_val = "("+ss_val+", N/A)";
                                    } else if(!ss_val && sector_perf_val) {
                                        perf_val = "(N/A, "+sector_perf_val+")";
                                    } else {
                                        perf_val = "(N/A, N/A)";
                                    }
                                } else if(sector_polygon) {
                                    if(ss_val) {
                                        perf_val = "("+ss_val+")";
                                    }
                                }

                                if($.trim(perf_val)) {

                                    if(window.location.pathname.indexOf("googleEarth") > -1) {
                                        ss_marker_data.perf_val = perf_val;
                                        //couldn't find any option to draw Label with Google Earth, so plese check the values on mouse hover ballon
                                    } else if (window.location.pathname.indexOf("white_background") > -1) {
                                       var perfLabel_infobox = new OpenLayers.Popup("perfLabel_"+ss_marker.name,
                                            new OpenLayers.LonLat(ss_marker.ptLon,ss_marker.ptLat),
                                            new OpenLayers.Size(90,25),
                                            perf_val,
                                            false
                                        );
                                        ccpl_map.addPopup(perfLabel_infobox);

                                        if($("#perfLabel_"+ss_marker.name).length > 0) {
                                            // Left Position in PX
                                            var current_left = $("#perfLabel_"+ss_marker.name).position().left;
                                            current_left = current_left + 10;
                                            $("#perfLabel_"+ss_marker.name).css("left",current_left+"px");
                                        }

                                        // If show/hide checkbox is unchecked then hide label
                                        if(hide_flag) {
                                            perfLabel_infobox.hide();
                                        }

                                        labelsArray.push(perfLabel_infobox);
                                    } else {
                                        var perf_infobox = perf_self.createInfoboxLabel(
                                            perf_val,
                                            perfLabelStyle,
                                            10,
                                            -10,
                                            ss_marker.getPosition(),
                                            hide_flag
                                        );

                                        perf_infobox.open(mapInstance, ss_marker);
                                        labelsArray.push(perf_infobox);
                                    }
                                }
                                // }
                            }//Sub-Station Loop End
                        }// If sector child are plottable of not condition end-----
                    } else if(sector_polygon) {

                        var ss_marker_obj = "",
                            ss_name_array = [];

                        for(var xxx=0;xxx<connected_sectors.length;xxx++) {
                            if(sectorArray[i].sub_station && sectorArray[i].sub_station.length > 0) {
                                if((connected_sectors[xxx].sector_configured_on_device == sectorArray[i].device_name) && (connected_sectors[xxx].sector_configured_on == sectorArray[i].ip_address)) {
                                    var connected_sub_stations = sectorArray[i].sub_station;
                                    for(var key=0; key< connected_sub_stations.length; key++) {
                                        var ss = connected_sub_stations[key]['name'] ? connected_sub_stations[key]['name'] : "";
                                        if(connected_sub_stations[key] && ss) {
                                            if(window.location.pathname.indexOf("googleEarth") > -1) {
                                                // Remove Line from map & array
                                                if(allMarkersObject_earth['path']['line_'+ss]) {
                                                    if(startEndObj["startLat"] && startEndObj["startLon"]) {

                                                        var current_line = allMarkersObject_earth['path']['line_'+ss];

                                                        var lineString = ge.createLineString('');
                                                        current_line.setGeometry(lineString);
                                                        // Add LineString points
                                                        lineString.getCoordinates().pushLatLngAlt((+startEndObj.startLat), (+startEndObj.startLon), 0);
                                                        lineString.getCoordinates().pushLatLngAlt((+current_line.ss_lat), (+current_line.ss_lon), 0);
                                                    }
                                                }
                                            } else if (window.location.pathname.indexOf("white_background") > -1) {
                                                // Remove Line from map & array
                                                if(allMarkersObject_wmap['path']['line_'+ss]) {
                                                    if(startEndObj["startLat"] && startEndObj["startLon"]) {
                                                        var current_line = allMarkersObject_gmap['path']['line_'+ss];
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
                                                if(allMarkersObject_gmap['path']['line_'+ss]) {
                                                    if(startEndObj["startLat"] && startEndObj["startLon"]) {

                                                        var current_line = allMarkersObject_gmap['path']['line_'+ss],
                                                            new_path = [
                                                                new google.maps.LatLng(startEndObj["startLat"],startEndObj["startLon"]),
                                                                new google.maps.LatLng(current_line.ss_lat,current_line.ss_lon)
                                                            ];
                                                        // Update line path
                                                        current_line.setOptions({
                                                            path : new_path
                                                        });
                                                    }
                                                }
                                            }
                                        } else {
                                            // pass
                                        }
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
            old_sector_loop:
            for(var i=0;i<connected_sectors.length;i++) {
                var condition1 = "",
                    condition2 = "",
                    condition3 = "";
                new_sector_loop:
                for(var j=0;j<sectorArray.length;j++) {
                    if(sectorArray[j].sub_station && sectorArray[j].sub_station.length > 0) {
                        condition1 = connected_sectors[i].sector_configured_on_device == sectorArray[j].device_name;
                        condition2 = connected_sectors[i].sector_configured_on == sectorArray[j].ip_address;
                        condition3 = connected_sectors[i].sector_id == sectorArray[j].sector_id;
                        if(condition1 && condition2 && condition3) {
                            // bs_object.data.param.sector[i].sub_station = sectorArray[j].sub_station;
                            connected_sectors[i].sub_station =  sectorArray[j].sub_station;
                            break new_sector_loop;
                        }
                    }
                }
            }

            bs_object.data.param.sector = connected_sectors;
            // Update Loki Object
            all_devices_loki_db.update(bs_object);

            if(window.location.pathname.indexOf("white_background") > -1) {

                if(new_plotted_ss && new_plotted_ss.length > 0) {
                    // ccpl_map.getLayersByName("Markers")[0].addFeatures(new_plotted_ss);
                    try {
                        ccpl_map.getLayersByName("Markers")[0].addFeatures(ccpl_map.getLayersByName("Markers")[0].features.concat(new_plotted_ss));
                    } catch(e) {
                        // console.log(e);
                    }
                    ccpl_map.getLayersByName("Markers")[0].redraw();
                    
                    // ccpl_map.getLayersByName("Markers")[0].strategies[0].features = ccpl_map.getLayersByName("Markers")[0].features;
                    ccpl_map.getLayersByName("Markers")[0].strategies[0].recluster();
                }

                ccpl_map.getLayersByName("Sectors")[0].redraw();
                // ccpl_map.getLayersByName("Lines")[0].redraw();
            }
            // Reset New Plotted SS array
            new_plotted_ss = [];
            // callback
            callback(true);
        }
    };

    /**
     * This function updates the icon for given marker
     * @method updateMarkerIcon
     * @param marker {Object}, It contains the map marker object.
     * @param icon {String}, It contains the marker icon url string
     */
    this.updateMarkerIcon = function(marker,new_icon) {

        if(window.location.pathname.indexOf("googleEarth") > -1) {
            var iconUrl = base_url+"/"+new_icon,
                old_icon_obj = iconUrl;

            try {
                marker['clusterIcon'] = hiddenIconObj;
                marker['oldIcon'] = old_icon_obj;
            } catch(e) {
                // console.log(e);
            }

            updateGoogleEarthPlacemark(marker, old_icon_obj);
        } else if (window.location.pathname.indexOf("white_background") > -1) {

            var iconUrl = base_url+"/"+new_icon,
                old_icon_obj = iconUrl,
                other_size_obj = whiteMapClass.getMarkerSize_wmap(false),
                other_width = other_size_obj.width ? other_size_obj.width : whiteMapSettings.devices_size.medium.width,
                other_height = other_size_obj.height ? other_size_obj.height : whiteMapSettings.devices_size.medium.height;

            // Update sector marker icon
            marker.attributes.icon = hiddenIconObj;
            marker.attributes.clusterIcon = hiddenIconObj;
            marker.attributes.oldIcon = old_icon_obj;
            marker.oldIcon = old_icon_obj;
            marker.style['externalGraphic'] = old_icon_obj;
            marker.style['graphicWidth'] = other_width;
            marker.style['graphicHeight'] = other_height;
            var sectorMarkerLayer = marker.layer ? marker.layer : marker.layerReference;
            sectorMarkerLayer.redraw();
        } else {
            var sector_icon_obj = gmap_self.getMarkerImageBySize(base_url+"/"+new_icon,"other");
            // Update sector marker icon
            marker.setOptions({
                "icon" : hiddenIconObj,
                "clusterIcon" : hiddenIconObj,
                "oldIcon" : sector_icon_obj,
            });
        }
    };

    /**
     * This function removed ss,line & ss labels from map as per given param
     * @method removeOldSS
     * @param ss_name {String}, It contains the name of ss
     */
    this.removeOldSS = function(ss_name) {

        if(window.location.pathname.indexOf("googleEarth") > -1) {
            // Remove SS if exists
            if (allMarkersObject_earth['sub_station']['ss_'+ss_name]){
                // Remove from google map
                allMarkersObject_earth['sub_station']['ss_'+ss_name].setVisibility(false);
                deleteGoogleEarthPlacemarker(allMarkersObject_earth['sub_station']['ss_'+ss_name].getId());
                delete allMarkersObject_earth['sub_station']['ss_'+ss_name];
            }
            // Remove Line if exists
            if(allMarkersObject_earth['path']['line_'+ss_name]) {
                allMarkersObject_earth['path']['line_'+ss_name].setVisibility(false);
                deleteGoogleEarthPlacemarker(allMarkersObject_earth['path']['line_'+ss_name]);
                delete allMarkersObject_earth['path']['ss_'+ss_name];
            }
        } else if (window.location.pathname.indexOf("white_background") > -1) {
            // Remove SS if exists
            if (allMarkersObject_wmap['sub_station']['ss_'+ss_name]){
                try {
                    hideOpenLayerFeature(allMarkersObject_wmap['sub_station']['ss_'+ss_name]);
                    ccpl_map.getLayersByName("Markers")[0].removeFeatures([allMarkersObject_wmap['sub_station']['ss_'+ss_name]]);
                    allMarkersObject_wmap['sub_station']['ss_'+ss_name].destroy();
                    delete allMarkersObject_wmap['sub_station']['ss_'+ss_name];
                } catch(e) {
                    // console.log(e);
                }
            }
            // Remove line if exists
            if(allMarkersObject_wmap['path']['line_'+ss_name]) {
                try{
                    hideOpenLayerFeature(allMarkersObject_wmap['path']['line_'+ss_name]);
                    ccpl_map.getLayersByName("Lines")[0].removeFeatures([allMarkersObject_wmap['path']['line_'+ss_name]]);
                    allMarkersObject_wmap['path']['line_'+ss_name].destroy();
                    delete allMarkersObject_wmap['path']['ss_'+ss_name];
                } catch(e) {
                    // console.log(e);
                }
            }
            // Remove label if exists
            if(tooltipInfoLabel['ss_'+ss_name]) {
                // tooltipInfoLabel['ss_'+ss_name].destroy();
                ccpl_map.removePopup(tooltipInfoLabel['ss_'+ss_name]);
                // tooltipInfoLabel['ss_'+ss_name].setVisibility(false);
                delete tooltipInfoLabel['ss_'+ss_name];
            }
        } else {
            // Remove SS if exists
            if (allMarkersObject_gmap['sub_station']['ss_'+ss_name]){
                // Remove from google Map
                allMarkersObject_gmap['sub_station']['ss_'+ss_name].setMap(null);

                // Remove SS Marker from cluster
                masterClusterInstance.removeMarker_(allMarkersObject_gmap['sub_station']['ss_'+ss_name]);

                // Delete from gobal object
                delete allMarkersObject_gmap['sub_station']['ss_'+ss_name];
            }
            // Remove Line if exists
            if(allMarkersObject_gmap['path']['line_'+ss_name]) {
                allMarkersObject_gmap['path']['line_'+ss_name].setMap(null);
                delete allMarkersObject_gmap['path']['ss_'+ss_name];
            }
            // Remove Label if exists
            if(tooltipInfoLabel['ss_'+ss_name]) {
                tooltipInfoLabel['ss_'+ss_name].close();
                delete tooltipInfoLabel['ss_'+ss_name];
            }
        }
    };

    /**
     * This function returns the value of given key from given object array
     * @method getKeyValue
     * @param objItemList {Array}, It is the array object from which the key value is to be fetched
     * @param key {String}, It contains the name of key whose value is to be fetched
     * @param returnOnlyVal {boolean}, It contains the flag which means that return only value to for corresponding key or whole object
     */
    this.getKeyValue = function(objItemList,key,returnOnlyVal,item_index) {
        
        var val = "",
            objArray = gmap_self.objDeepCopy_nocout(objItemList),
            list_index = item_index > -1 ? item_index : 0;

        for(var y=objArray.length;y--;) {
            if(objArray[y]) {
                if($.trim(objArray[y].name) == key) {
                    if(returnOnlyVal) {
                        val = String(objArray[y].value).split("|")[list_index];
                    } else {
                        // Fetch Actual Value
                        var actual_val = String(objArray[y].value).split("|")[list_index];
                        // Update dict with actual value
                        objArray[y].value = actual_val;
                        val = objArray[y];
                    }
                    break;
                }
            }
        }

        return val;
    };

    /**
     * This function creates infobox label on given position
     * @method createInfoboxLabel
     * @param labelContent {String}, It contains the label html
     * @param labelStyleObj {Object}, It contains the style or CSS object for label
     * @param xOffset {Integer}, It contains X direction offset for label
     * @param yOffset {Integer}, It contains Y direction offset for label
     * @param labelPosition {Object}, It contains the gmap lat lon object for label position
     * @param hide_flag {String}, It contains the flag either to show label or not.
     */
    this.createInfoboxLabel = function(labelContent,labelStyleObj,xOffset,yOffset,labelPosition,hide_flag) {
        var toolTip_infobox = new InfoBox({
            content: labelContent,
            boxStyle: labelStyleObj,
            pixelOffset : new google.maps.Size(xOffset,yOffset),
            disableAutoPan: true,
            position: labelPosition,
            closeBoxURL: "",
            isHidden: hide_flag,
            enableEventPropagation: true,
            zIndex: 80
        });

        return toolTip_infobox;
    };

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

    /**
     * This function checks that the given SS devices is to be shown or hide as per the filters
     * @method isSectorDevicesPlottable
     * @param current_sector {Object}, It contains the sectors data whose child is to be plotted
     * @param connected_sectors {Array}, It contains all the sectors data of specific BS
     */
    this.isSectorDevicesPlottable = function(current_sector,connected_sectors) {

        var isPlottable = false,
            technology_filter = $("#filter_technology").select2('val').length > 0 ? $("#filter_technology").select2('val').join(',').toLowerCase().split(',') : [],
            vendor_filter = $("#filter_vendor").select2('val').length > 0 ? $("#filter_vendor").select2('val').join(',').toLowerCase().split(',') : [],
            frequency_filter = $("#filter_frequency").select2('val').length > 0 ? $("#filter_frequency").select2('val').join(',').toLowerCase().split(',') : [],
            polarization_filter = $("#filter_polarization").select2('val').length > 0 ? $("#filter_polarization").select2('val').join(',').toLowerCase().split(',') : [],
            isAdvanceFilterApplied = technology_filter.length > 0 || vendor_filter.length > 0 || frequency_filter.length > 0 || polarization_filter.length > 0,
            isBasicFilterApplied = $.trim($("#technology").val()).length > 0 || $.trim($("#vendor").val()).length > 0;

        // If no filters applied
        if(!isAdvanceFilterApplied && !isBasicFilterApplied) {
            isPlottable = true;
        } else {
            // Loop all bs sectors
            for(var i=0;i<connected_sectors.length;i++) {
                if(!isPlottable) {    
                    var condition1 = connected_sectors[i].sector_configured_on_device == current_sector.device_name,
                        condition2 = connected_sectors[i].sector_configured_on == current_sector.ip_address;
                    // If both condition satisfied
                    if(condition1 && condition2) {
                        var sector_tech = connected_sectors[i].technology ? $.trim(connected_sectors[i].technology.toLowerCase()) : "",
                            sector_vendor = connected_sectors[i].vendor ? $.trim(connected_sectors[i].vendor.toLowerCase()) : "",
                            sector_frequency = connected_sectors[i].planned_frequency ? $.trim(connected_sectors[i].planned_frequency) : "",
                            sector_polarization = connected_sectors[i].orientation ? $.trim(connected_sectors[i].orientation.toLowerCase()) : "";

                        if(isBasicFilterApplied) {
                            var basic_filter_technology = $.trim($("#technology").val()).length > 0 ? $.trim($("#technology option:selected").text()).toLowerCase() == sector_tech : true,
                                basic_filter_vendor = $.trim($("#vendor").val()).length > 0 ? $.trim($("#vendor option:selected").text()).toLowerCase() == sector_vendor : true;

                            // If basic filters condition satisfied
                            if(basic_filter_technology && basic_filter_vendor) {
                                isPlottable = true;
                            }

                            if(!isPlottable) {
                                if(isAdvanceFilterApplied) {
                                    var advance_filter_condition1 = technology_filter.length > 0 ? technology_filter.indexOf(sector_tech) > -1 : true,
                                        advance_filter_condition2 = vendor_filter.length > 0 ? vendor_filter.indexOf(sector_vendor) > -1 : true,
                                        advance_filter_condition3 = frequency_filter.length > 0 ? frequency_filter.indexOf(sector_frequency) > -1 : true,
                                        advance_filter_condition4 = polarization_filter.length > 0 ? polarization_filter.indexOf(sector_polarization) > -1 : true;

                                    if(advance_filter_condition1 && advance_filter_condition2 && advance_filter_condition3 && advance_filter_condition4) {
                                        isPlottable = true;
                                    }
                                }
                            }

                        } else if(isAdvanceFilterApplied) {
                            var advance_filter_condition1 = technology_filter.length > 0 ? technology_filter.indexOf(sector_tech) > -1 : true,
                                advance_filter_condition2 = vendor_filter.length > 0 ? vendor_filter.indexOf(sector_vendor) > -1 : true,
                                advance_filter_condition3 = frequency_filter.length > 0 ? frequency_filter.indexOf(sector_frequency) > -1 : true,
                                advance_filter_condition4 = polarization_filter.length > 0 ? polarization_filter.indexOf(sector_polarization) > -1 : true;

                            if(advance_filter_condition1 && advance_filter_condition2 && advance_filter_condition3 && advance_filter_condition4) {
                                isPlottable = true;
                            }
                        } else {
                            isPlottable = true;
                        }
                    }
                }
            }
        }
        return isPlottable;
    };
}
