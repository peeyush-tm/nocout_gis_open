var recallPerf = "",
    current_bs_list = [],
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

        var gisPerformance_this = this;

        var uncommon_bs_list = perf_self.get_intersection_bs(current_bs_list,bs_list);

        //Reset Variable
        gisPerformance_this.resetVariable();

        this.bsNamesList = uncommon_bs_list;
        //Store Length of Total BS
        this.bsLength = this.bsNamesList.length;

        if(uncommon_bs_list.length === bs_list.length) {
            current_bs_list = uncommon_bs_list;
        }
        //Start Request for First BS
        gisPerformance_this.sendRequest(0);
    }

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
        this._isFrozen = isFreeze;
    }

    /*
     This function sends Request based on the counter value.
     */
    this.sendRequest = function (counter) {
        //If isFrozen is false and Cookie value for freezeSelected is also false
        if (($.cookie('isFreezeSelected') == 0 || +($.cookie('freezedAt')) > 0) && isPollingActive == 0) {
            var gisPerformance_this = this;
            //Call waitAndSend function with BS Json Data and counter value
            gisPerformance_this.waitAndSend(this.createRequestData(this.bsNamesList[counter]), counter);
        }
    }

    /*
     This function sends a Ajax request based on param and counter provided. If All the calls for BS is completed, then we resetVariables and start Performance again in 5 mins.
     */
    this.waitAndSend = function (getBsRequestData, counter) {

        var gisPerformance_this = this;
        counter++;
        //If all calls has been done,
        if (counter > this.bsLength) {
            //1 Minutes Timeout
            setTimeout(function () {
                //Start Performance Again
                var bs_list = getMarkerInCurrentBound();
                if(bs_list.length > 0 && isCallCompleted == 1) {
                    if(recallPerf != "") {
                        clearTimeout(recallPerf);
                        recallPerf = "";
                    }
                    /*Reset global variable when all calls completed*/
                    current_bs_list = [];
                    /*Start calls*/
                    gisPerformance_this.start(bs_list);
                }
            }, 60000);
            return;
        }

        //Ajax Request
        $.ajax({
            url: base_url + '/network_maps/performance_data/?freeze_time=' + freezedAt,
            data: JSON.stringify(getBsRequestData),
            type: 'POST',
            dataType: 'json',
            //In success
            success: function (data) {
                //If data is there
                if (data) {
                    //Store data in gisData
                    gisPerformance_this.gisData = data;
                    var current_bs_list = getMarkerInCurrentBound();
                    /*Check that the bsname is present in current bounds or not*/
                    if (current_bs_list.indexOf(data.basestation_name) >= 0) {
                        //Update Map with the data
                        gisPerformance_this.updateMap();
                    }
                }
                //After 2 seconds timeout
                recallPerf = setTimeout(function () {
                    //Send Request for the next counter
                    gisPerformance_this.sendRequest(counter);
                }, 1000);
            },
            //On Error, do nothing
            error: function (err) {
                setTimeout(function () {
                    //Start Performance Again
                    if (this.bsNamesList && this.bsNamesList.length > 0) {
                        gisPerformance_this.start(this.bsNamesList);
                    }
                }, 60000);
            }
        });
    }

    /*
     This function creates Data to be sended with the Ajax Request for the Specific given BS name in parameter.
     */
    this.createRequestData = function (bsname) {
        //Initial data for DATA
        var initialdata = {
            "basestation_name": "",
            "basestation_id": null,
            "param": {
                "sector": []
            }
        }
        //Fetch BS Gmap marker from markersMasterObj
        var bsGmapMarker = markersMasterObj['BSNamae'][bsname];

        //If Marker is found
        if (bsGmapMarker) {
            //Update BS name in DATA
            initialdata["basestation_name"] = bsGmapMarker["bs_name"];
            //Update BS id in DATA
            initialdata["basestation_id"] = bsGmapMarker["bsInfo"][2]["value"];
            //Loop through all the child_ss in BS
            for (var i = 0; i < bsGmapMarker["child_ss"].length; i++) {

                var deviceSectorJSon = {};

                var sector_marker = allMarkersObject_gmap['sector_device']['sector_'+$.trim(bsGmapMarker["child_ss"][i].sector_configured_on)],
                    radius = bsGmapMarker["child_ss"][i].radius,
                    azimuth = bsGmapMarker["child_ss"][i].azimuth_angle,
                    beamWidth = bsGmapMarker["child_ss"][i].beam_width,
                    sector_poly_marker = allMarkersObject_gmap['sector_polygon']['poly_'+$.trim(bsGmapMarker["child_ss"][i].sector_configured_on)+"_"+radius+"_"+azimuth+"_"+beamWidth];

                if((sector_marker && (sector_marker.map != null && sector_marker.map != "")) || (sector_poly_marker && (sector_poly_marker.map != null && sector_poly_marker.map != ""))) {

                    //Create deviceSectorJson with device_name, device_id, empty performance_data and sub_station array
                    deviceSectorJSon = {
                        "device_name": bsGmapMarker["child_ss"][i]["device_info"][0]["value"],
                        "device_id": bsGmapMarker["child_ss"][i]["device_info"][1]["value"],
                        "performance_data": {"frequency": "", "pl": "", "color": "", "performance_parameter": "", "performance_value": "", "performance_icon": ""},
                        "sub_station": []
                    };
                    //Loop through all the SubStations in Device
                    for (var j = 0; j < bsGmapMarker["child_ss"][i]["sub_station"].length; j++) {

                        var ssMarker = allMarkersObject_gmap['sub_station']['ss_'+bsGmapMarker["child_ss"][i]["sub_station"][j].name];
                        if(ssMarker && (ssMarker.map != null && ssMarker.map != "")) {
                            //Store sub_station_name, sub_station_id, and empty performance data for the substation
                            var deviceSsJson = {
                                "device_name": bsGmapMarker["child_ss"][i]["sub_station"][j]["device_name"],
                                "device_id": bsGmapMarker["child_ss"][i]["sub_station"][j]["id"],
                                "performance_data": {"frequency": "", "pl": "", "color": "", "performance_parameter": "", "performance_value": "", "performance_icon": ""}
                            }
                            //Push it in sub_station array of deviceSectorJSon
                            deviceSectorJSon["sub_station"].push(deviceSsJson);
                        }
                    }

                    //Push DATA sector to the deviceSectorJSon created.
                    initialdata["param"]["sector"].push(deviceSectorJSon);
                }
            }
        }
        //Return initialData
        return initialdata;
    }

    /*
     Here we update Google Map from gisData
     First we get BS Marker from markersMasterObj with BS Name
     Then we loop through each SS for the Base Station
     Then we fetch various google map elements like lineColor or sectorColor and update those components using values from GisPerformanceData.
     */
    this.updateMap = function () {
        //Step no. 1 => Find BS Station First
        var gisData = this.gisData;
        //Get BS Gmap Marker
        var bsMarkerObject = markersMasterObj['BSNamae'][gisData.basestation_name];
        var condition= false;
        //Step no. 2 ==> Loop through all the SS in the BS
        try {
            //Loop through devices
            for (var i = 0; i < bsMarkerObject['child_ss'].length; i++) {
            	condition = true;
            	var sector_perf_val = "",
                    polyPathArray = [],
            	    new_line_path = [],
                    radius = bsMarkerObject["child_ss"][i].radius,
                    azimuth = bsMarkerObject["child_ss"][i].azimuth_angle,
                    beamWidth = bsMarkerObject["child_ss"][i].beam_width,
                    sector_marker = allMarkersObject_gmap['sector_device']['sector_'+$.trim(bsMarkerObject["child_ss"][i].sector_configured_on)],
                    sector_poly_marker = allMarkersObject_gmap['sector_polygon']['poly_'+$.trim(bsMarkerObject["child_ss"][i].sector_configured_on+"_"+radius+"_"+azimuth+"_"+beamWidth)];



                //Loop through sub_station of devices
                for (var j = 0; j < bsMarkerObject['child_ss'][i]['sub_station'].length; j++) {

                    if((sector_marker && (sector_marker.map != null)) || (sector_poly_marker && (sector_poly_marker.map != null))) {

                        var halfPt;
                        //Step no. 3 ===> Fetch PerformanceValue for various key from GisData JSon
                        var lineColor = this.calculatePerformanceValue("color", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
                        //Fetch googlePolyline from markersMasterObj;
                        var googlePolyLine = markersMasterObj['LinesName'][String(bsMarkerObject["name"]) + bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]];
                        // //Update Polyline content.
                        if(googlePolyLine && lineColor) {
                            googlePolyLine.setOptions({strokeColor: lineColor});
                        }

                        //If technology is WiMAX and PMP
                        if($.trim(bsMarkerObject['child_ss'][i]["technology"].toLowerCase()) != "ptp" && $.trim(bsMarkerObject['child_ss'][i]["technology"].toLowerCase()) != "p2p") {
                            //Get sector Polyline
                            var sectorPoly = allMarkersObject_gmap['sector_polygon']['poly_'+$.trim(bsMarkerObject["child_ss"][i].sector_configured_on+"_"+radius+"_"+azimuth+"_"+beamWidth)];
                            //If both sector Poly and line Color is defined
                            if (sector_poly_marker && lineColor) {
                                var sector_perf_obj = {};
                                sector_perf_obj["performance_paramter"] = this.calculatePerformanceValue("performance_paramter", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
                                sector_perf_obj["performance_value"] = this.calculatePerformanceValue("performance_value", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
                                sector_perf_obj["frequency"] = this.calculatePerformanceValue("frequency", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
                                sector_perf_obj["pl"] = this.calculatePerformanceValue("pl", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
                                //Update color for Sector POly.
                                var new_radius = this.calculatePerformanceValue("radius", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
                                var azimuth = this.calculatePerformanceValue("azimuth_angle", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
                                var beam_width = this.calculatePerformanceValue("beam_width", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
                                var polarisation = sector_poly_marker.polarisation ? sector_poly_marker.polarisation : 'vertical';

                                if((new_radius && $.trim(new_radius) != "") && (azimuth && $.trim(azimuth) != "") && (beam_width && $.trim(beam_width) != "")) {
                                    /*Check to draw sector only for first time in ss loop*/
                                    if(condition) {

                                        networkMapInstance.createSectorData(+(sector_poly_marker.ptLat),+(sector_poly_marker.ptLon),new_radius,azimuth,beam_width,polarisation,function(pointsArray) {
                                            halfPt = Math.floor(pointsArray.length / (+2));
                                            polyPointsArray = pointsArray;
                                            for(var i=0;i<pointsArray.length;i++) {
                                                var pt = new google.maps.LatLng(pointsArray[i].lat,pointsArray[i].lon);
                                                polyPathArray.push(pt);
                                            }
                                        });
                                        sector_poly_marker.setPath(polyPathArray);
                                    }
                                    new_line_path = [new google.maps.LatLng(polyPointsArray[halfPt].lat,polyPointsArray[halfPt].lon),new google.maps.LatLng(googlePolyLine.ss_lat,googlePolyLine.ss_lon)];
                                }

                                if(new_line_path.length > 0) {
                                    googlePolyLine.setOptions({"bs_lat" : polyPointsArray[halfPt].lat,"bs_lon" : polyPointsArray[halfPt].lon});
                                    googlePolyLine.setPath(new_line_path);
                                }

                                sector_poly_marker.hasPerf = 1;
                                sector_poly_marker.perf_data_obj = sector_perf_obj;
                                sector_poly_marker.setOptions({fillColor: lineColor});
                            }
                        } else {
                            if(condition) {
                                if(sector_marker) {
                                    var new_icon_sector = this.calculatePerformanceValue("performance_icon", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], false);
                                    if(new_icon_sector) {
                                        var largeur= 32,
                                            hauteur= 37,
                                            divideBy= 1,
                                            anchorX= 0,
                                            iconUrl = base_url+"/"+new_icon_sector;

                                        var old_icon_obj = new google.maps.MarkerImage(
                                            iconUrl,
                                            new google.maps.Size(Math.ceil(largeur/divideBy), Math.ceil(hauteur/divideBy)),
                                            new google.maps.Point(0, 0),
                                            new google.maps.Point(Math.ceil(16-(16*anchorX)), Math.ceil(hauteur/divideBy)),
                                            new google.maps.Size(Math.ceil(largeur/divideBy), Math.ceil(hauteur/divideBy))
                                        );
                                        var other_icons_obj = new google.maps.MarkerImage(
                                            base_url+'/static/img/icons/1x1.png',
                                            null,
                                            null,
                                            null,
                                            null
                                        );
                                        sector_marker.icon = other_icons_obj;
                                        sector_marker.clusterIcon = other_icons_obj;
                                        sector_marker.clusterIcon = old_icon_obj;
                                    }

                                    /*Create Label on Sector Marker*/
                                    sector_perf_val = this.calculatePerformanceValue("performance_value", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], false);
                                }
                            }
                        }

                        //Get substation icon from Performance
                        var subStationIcon = this.calculatePerformanceValue("performance_icon", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);

                        //Get subStation Name
                        var subStationName = bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"];
                        //Get subStation Marker
                        var subStationMarker = markersMasterObj['SSNamae'][subStationName];

                        var polled_info = this.calculatePerformanceValue("device_info", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);

                        subStationMarker.hasPerf = 1;

                        var existing_index = -1;
                        for (var x = 0; x < labelsArray.length; x++) {
                            var move_listener_obj = labelsArray[x].moveListener_;
                            if (move_listener_obj) {
                                var keys_array = Object.keys(move_listener_obj);
                                for(var z=0;z<keys_array.length;z++) {
                                    if(typeof move_listener_obj[keys_array[z]] === 'object') {
                                       if((move_listener_obj[keys_array[z]] && move_listener_obj[keys_array[z]]["name"]) && (move_listener_obj[keys_array[z]] && move_listener_obj[keys_array[z]]["bs_name"])) {
                                            if (($.trim(move_listener_obj[keys_array[z]]["name"]) == $.trim(subStationMarker.name)) && ($.trim(move_listener_obj[keys_array[z]]["bs_name"]) == $.trim(subStationMarker.bs_name))) {
                                                existing_index = x;
                                                labelsArray[x].close();
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

                        var visible_flag = false;
                        if (!$("#show_hide_label")[0].checked) {
                            visible_flag = true;
                        }
                        
                        var ss_val = this.calculatePerformanceValue("performance_value", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]),
                            perf_val = "",
                            technology_condition = $.trim(bsMarkerObject['child_ss'][i]["technology"].toLowerCase()) == "ptp" || $.trim(bsMarkerObject['child_ss'][i]["technology"].toLowerCase()) == "p2p";

                        if(technology_condition) {

                            if(ss_val && sector_perf_val) {
                                perf_val = "("+ss_val+", "+sector_perf_val+")";
                            } else if(ss_val && !sector_perf_val) {
                                perf_val = "("+ss_val+", N/A)";
                            } else if(!ss_val && sector_perf_val) {
                                perf_val = "(N/A, "+sector_perf_val+")";
                            } else {
                                perf_val = "";
                            }
                        } else {
                            perf_val = ss_val;
                        }

                        if(perf_val && $.trim(perf_val)) {
                            var perf_infobox = new InfoBox({
                                content: perf_val,
                                boxStyle: {
                                    border: "1px solid black",
                                    background: "white",
                                    textAlign: "center",
                                    fontSize: "9pt",
                                    color: "black",
                                    padding: '2px',
                                    width : '100px'
                                },
                                disableAutoPan: true,
                                position: new google.maps.LatLng(subStationMarker.ptLat, subStationMarker.ptLon),
                                closeBoxURL: "",
                                isHidden: visible_flag,
                                // visible : visible_flag,
                                enableEventPropagation: true,
                                zIndex: 80
                            });

                            perf_infobox.open(mapInstance, subStationMarker);
                            if(subStationMarker.map && (subStationMarker.map != null && subStationMarker.map != "")) {
                                labelsArray.push(perf_infobox);
                            }
                        }

                        subStationMarker["poll_info"] = polled_info;


                        //If substation icon is present
                        if (subStationIcon) {
                            //Update icon, oldIcon and clusterIcon for the SubStation Marker
                            subStationMarker.setIcon(createGoogleMarker(base_url + '/' + subStationIcon, subStationMarker));
                            subStationMarker.oldIcon = (createGoogleMarker(base_url + '/' + subStationIcon, subStationMarker));
                            subStationMarker.clusterIcon = (createGoogleMarker(base_url + '/' + subStationIcon, subStationMarker));
                        }
                        /*Reset the flag*/
                        condition= false;
                    }
                }

               //Get Device Markers for the BS.

               var deviceMarkers = sectorMarkersMasterObj[String(gisData.basestation_name)] ? sectorMarkersMasterObj[String(gisData.basestation_name)] : [];
               //Loop through all the devices
               for (var k = 0; k < deviceMarkers.length; k++) {
                   if (deviceMarkers[i] && (deviceMarkers[i].map != null && deviceMarkers[i].map != "")) {
                       //Get the Device Name from the Performance Data
                       var deviceObject = this.findObjectbyDeviceName(deviceMarkers[i]["deviceInfo"][0]["value"]);
                       //If Icon for the device is provided in performance data
                       if (deviceObject["performance_data"]["performance_icon"]) {
                           //Update oldIcon for the device to the Given Icon
                           deviceMarkers[i].oldIcon = (createGoogleMarker(base_url + '/' + deviceObject["performance_data"]["performance_icon"], deviceMarkers[i]));
                           deviceMarkers[i].poll_info = deviceObject["performance_data"]["device_info"];
                       }
                   }
               }
            }
        } catch (exception) {
            //Pass
            // console.log(exception);
        }
    }

    /*
     Utility function to find a specific device with name from the Ajax response data
     */
    this.findObjectbyDeviceName = function (deviceName) {
        var gisData = this.gisData;
        //Loop through the sector in performance data
        for (var i = 0; i < gisData["param"]["sector"].length; i++) {
            //If we find device_name to the given deviceName in param
            if (gisData["param"]["sector"][i]["device_name"] === deviceName) {
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

        // var perf_sector_array = gisData["param"]["sector"];

        // for(var i=0;i<perf_sector_array.length;i++) {

        // 	if(perf_sector_array[i].device_name && ($.trim(perf_sector_array[i].device_name) == device)) {
        // 		var perf_substation_array = perf_sector_array[i].sub_station;

        // 		for(var j=0;j<perf_substation_array.length;j++) {

        // 			if(perf_substation_array[j].device_name && ($.trim(perf_substation_array[j].device_name) == ssName)) {
        // 				return perf_substation_array[j].performance_data[key];
        // 			}
        // 		}
        // 	}
        // }

        //Loop through GIS Sector Data
        for (var i = 0; i < gisData["param"]["sector"].length; i++) {
            //If Gis Sector Name=== device
            if (gisData["param"]["sector"][i] && gisData["param"]["sector"][i]["device_name"] === device) {
                if(ssName) {
                    //Loop inside device Sub Stations
                    for(var j = 0; j < gisData["param"]["sector"][i]["sub_station"].length; j++) {
                        //If SubStation name=== devinceName passed
                        if (gisData["param"]["sector"][i]["sub_station"][j]["device_name"] === ssName) {
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
