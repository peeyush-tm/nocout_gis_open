var recallPerf = "";
/*
This function creates a google marker with a new URL and take all other values from previous defined marker setting else set to null
 */
function createGoogleMarker(url, oldMarkerIcon) {
	var oldMarObj= {}, newMarkerImage= "";
	//Get anchor setting from oldMarkerIcon
	oldMarObj['anchor']= oldMarkerIcon['icon']['anchor'] ? oldMarkerIcon['icon']['anchor'] : null;
	//Get origin setting from oldMarkerIcon
	oldMarObj['origin']= oldMarkerIcon['icon']['origin'] ? oldMarkerIcon['icon']['origin'] : null;
	//Get scaledSize setting from oldMarkerIcon
	oldMarObj['scaledSize']= oldMarkerIcon['icon']['scaledSize'] ? oldMarkerIcon['icon']['scaledSize'] : null;
	//Get size setting from oldMarkerIcon
	oldMarObj['size']= oldMarkerIcon['icon']['size'] ? oldMarkerIcon['icon']['size'] : null;
	//Create a new MarkerImage with new url, and all others value from previous defined settings
	newMarkerImage = new google.maps.MarkerImage(url,oldMarObj['size'],oldMarObj['origin'],oldMarObj['anchor'],oldMarObj['scaledSize']);
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
	this.bsNamesList= [];
	//Base Station Length
	this.bsLength= 0;

	/*
	Here we start GisPerformance.
	Send an AJax request to get GisPerformance Data
	Store Data in gisData variable
	And start the setInterval function to updateMap every 10 secs.
	 */
	this.start= function(bs_list) {

		var gisPerformance_this= this;

		//Reset Variable
		gisPerformance_this.resetVariable();
		
		//Loop through all BS Names
		// for(var k in markersMasterObj['BSNamae']) { 
		// 	//Push the name into BS Name List
		// 	this.bsNamesList.push(k)
		// };
		this.bsNamesList = bs_list;
		//Store Length of Total BS
		this.bsLength = this.bsNamesList.length;

		// Global Variable
		// this._isFrozen= isFreeze;

		//Start Request for First BS
		gisPerformance_this.sendRequest(0);
	}

	/*
	This will stop Sending Request by Setting isFrozen variable to 1
	 */
	this.stop= function() {
		this._isFrozen= 1;
	}

	/*
	This will restart the Request by Setting isFrozen variable to 0 and sending Request for First BS
	 */
	this.restart= function() {
		this._isFrozen = isFreeze;
		
		if(this.bsNamesList && this.bsNamesList.length > 0) {
			this.start(this.bsNamesList);
		}
	}

	/*
	Here we reset all variables defined.
	 */
	this.resetVariable= function() {
		this.gisData= null;
		this.bsNamesList= [];
		this.bsLength= 0;
		this._isFrozen= isFreeze;
	}

	/*
	This function sends Request based on the counter value.
	 */
	this.sendRequest = function(counter) {
		//If isFrozen is false and Cookie value for freezeSelected is also false
		if(($.cookie('isFreezeSelected') == 0 || +($.cookie('freezedAt')) > 0) && isPollingActive == 0) {
			var gisPerformance_this = this;
			//Call waitAndSend function with BS Json Data and counter value
			gisPerformance_this.waitAndSend(this.createRequestData(this.bsNamesList[counter]), counter);
		}
	}

	/*
	This function sends a Ajax request based on param and counter provided. If All the calls for BS is completed, then we resetVariables and start Performance again in 5 mins.
	 */
	this.waitAndSend = function(getBsRequestData, counter) {
		
		var gisPerformance_this = this;
		counter++;
		//If all calls has been done, 
		if(counter > this.bsLength) {
			//5 Minutes Timeout
			setTimeout(function() {
				//Start Performance Again
				if(this.bsNamesList && this.bsNamesList.length > 0) {
					gisPerformance_this.start(this.bsNamesList);
				}				
			}, 60000);
			return;
		}

		//Ajax Request
		$.ajax({
			url:  '/network_maps/performance_data/?freeze_time='+freezedAt,
			data: JSON.stringify(getBsRequestData),
			type : 'POST',
			dataType : 'json',
			//In success
			success : function (data) {
				//If data is there
				if(data) {
					//Store data in gisData
					gisPerformance_this.gisData= data;
					//Update Map with the data
					gisPerformance_this.updateMap();
				}
				//After 2 seconds timeout
				recallPerf = setTimeout(function() {
					//Send Request for the next counter
					gisPerformance_this.sendRequest(counter);
				}, 1000);
			},
			//On Error, do nothing
			error : function(err){
				setTimeout(function() {
					//Start Performance Again
					if(this.bsNamesList && this.bsNamesList.length > 0) {
						gisPerformance_this.start(this.bsNamesList);
					}				
				}, 60000);
			}
		});
	}

	/*
	This function creates Data to be sended with the Ajax Request for the Specific given BS name in parameter.
	 */
	this.createRequestData= function(bsname) {
		//Initial data for DATA
		var initialdata= {
			"basestation_name": "",
			"basestation_id": null,
			"param": {
				"sector": []
			}
		}
		//Fetch BS Gmap marker from markersMasterObj
		var bsGmapMarker= markersMasterObj['BSNamae'][bsname];
		//If Marker is found
		if(bsGmapMarker) {
			//Update BS name in DATA
			initialdata["basestation_name"]= bsGmapMarker["bs_name"];
			//Update BS id in DATA
			initialdata["basestation_id"]= bsGmapMarker["bsInfo"][2]["value"];
			//Loop through all the child_ss in BS
			for(var i=0; i< bsGmapMarker["child_ss"].length; i++) {
				//Create deviceSectorJson with device_name, device_id, empty performance_data and sub_station array
				var deviceSectorJSon= {
					"device_name": bsGmapMarker["child_ss"][i]["device_info"][0]["value"], 
					"device_id": bsGmapMarker["child_ss"][i]["device_info"][1]["value"], 
					"performance_data": {"frequency": "","pl": "","color": "","performance_parameter": "","performance_value": "","performance_icon": ""}, 
					"sub_station": []
				};
				//Loop through all the SubStations in Device
				for(var j=0; j< bsGmapMarker["child_ss"][i]["sub_station"].length; j++) {
					//Store sub_station_name, sub_station_id, and empty performance data for the substation
					var deviceSsJson= {
						"device_name": bsGmapMarker["child_ss"][i]["sub_station"][j]["device_name"],
						"device_id": bsGmapMarker["child_ss"][i]["sub_station"][j]["id"],
						"performance_data": {"frequency": "","pl": "","color": "","performance_parameter": "","performance_value": "","performance_icon": ""}
					}
					//Push it in sub_station array of deviceSectorJSon
					deviceSectorJSon["sub_station"].push(deviceSsJson);
				}
				//Push DATA sector to the deviceSectorJSon created.
				initialdata["param"]["sector"].push(deviceSectorJSon);
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
	this.updateMap= function() {
		//Step no. 1 => Find BS Station First
		var gisData= this.gisData;
		//Get BS Gmap Marker
		var bsMarkerObject= markersMasterObj['BSNamae'][gisData.basestation_name];
		//Step no. 2 ==> Loop through all the SS in the BS
		try {
			//Loop through devices
			for(var i=0; i< bsMarkerObject['child_ss'].length; i++) {
				var perf_obj = {};
				//Loop through sub_station of devices
				for(var j=0; j< bsMarkerObject['child_ss'][i]['sub_station'].length; j++) {
					//Step no. 3 ===> Fetch PerformanceValue for various key from GisData JSon
					var lineColor= this.calculatePerformanceValue("color", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
					//Fetch googlePolyline from markersMasterObj;
					var googlePolyLine= markersMasterObj['LinesName'][String(bsMarkerObject["name"])+ bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]];
					// //Update Polyline content.
					if(googlePolyLine && lineColor) {
						googlePolyLine.setOptions({strokeColor:lineColor});
					}

					//If technology is WiMAX and PMP
					if(bsMarkerObject['child_ss'][i]["technology"]=== "WiMAX" || bsMarkerObject['child_ss'][i]["technology"]=== "PMP") {
						//Get sector Polyline 
						var sectorPoly= markersMasterObj['Poly'][bsMarkerObject['child_ss'][i]['sub_station'][j]['device_name']];
						//If both sector Poly and line Color is defined
						if(sectorPoly && lineColor) {
							perf_obj["performance_paramter"] = this.calculatePerformanceValue("performance_paramter", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
							perf_obj["performance_value"] = this.calculatePerformanceValue("performance_value", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
							perf_obj["frequency"] = this.calculatePerformanceValue("frequency", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
							perf_obj["pl"] = this.calculatePerformanceValue("pl", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
							//Update color for Sector POly.
							sectorPoly.hasPerf = 1;
							sectorPoly.perf_data_obj = perf_obj;
							sectorPoly.setOptions({fillColor: lineColor});
						}
					}

					//Get substation icon from Performance
					var subStationIcon= this.calculatePerformanceValue("performance_icon", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);

					//Get subStation Name
					var subStationName = bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"];
					//Get subStation Marker
					var subStationMarker= markersMasterObj['SSNamae'][subStationName];

					perf_obj["performance_paramter"] = this.calculatePerformanceValue("performance_paramter", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
					perf_obj["performance_value"] = this.calculatePerformanceValue("performance_value", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
					perf_obj["frequency"] = this.calculatePerformanceValue("frequency", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
					perf_obj["pl"] = this.calculatePerformanceValue("pl", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);

					subStationMarker.hasPerf = 1;
					subStationMarker.perf_data_obj = perf_obj;

					//If substation icon is present
					if(subStationIcon) {
						//Update icon, oldIcon and clusterIcon for the SubStation Marker
						subStationMarker.setIcon(createGoogleMarker(base_url + '/'+ subStationIcon, subStationMarker));
						subStationMarker.oldIcon= (createGoogleMarker(base_url + '/'+ subStationIcon, subStationMarker));
						subStationMarker.clusterIcon= (createGoogleMarker(base_url + '/'+ subStationIcon, subStationMarker));
					}
				}

				//Get Device Markers for the BS.
				var deviceMarkers = sectorMarkersMasterObj[String(gisData.basestation_name)];
				//Loop through all the devices
				for(var k=0; k< deviceMarkers.length; k++) {
					if(deviceMarkers[i]) {
						//Get the Device Name from the Performance Data
						var deviceObject= this.findObjectbyDeviceName(deviceMarkers[i]["deviceInfo"][0]["value"]);
						//If Icon for the device is provided in performance data
						if(deviceObject["performance_data"]["performance_icon"]) {
							//Update oldIcon for the device to the Given Icon
							deviceMarkers[i].oldIcon= (createGoogleMarker(base_url + '/'+ deviceObject["performance_data"]["performance_icon"], deviceMarkers[i]));
						}
					}
					
				}
			}
		}catch(exception) {
			// console.log(exception);
		}
	}

	/*
	Utility function to find a specific device with name from the Ajax response data
	 */
	this.findObjectbyDeviceName= function(deviceName) {
		var gisData= this.gisData;
		//Loop through the sector in performance data
		for(var i=0; i< gisData["param"]["sector"].length; i++) {
			//If we find device_name to the given deviceName in param
			if(gisData["param"]["sector"][i]["device_name"]=== deviceName) {
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
	this.calculatePerformanceValue= function(key, device, ssName) {
		var gisData= this.gisData;
		//Loop through GIS Sector Data
		for(var i=0; i< gisData["param"]["sector"].length; i++) {
			//If Gis Sector Name=== device
			if(gisData["param"]["sector"][i] && gisData["param"]["sector"][i]["device_name"]=== device) {
				//Loop inside device Sub Stations
				for(var j=0; j< gisData["param"]["sector"][i]["sub_station"].length; i++) {
					//If SubStation name=== devinceName passed
					if(gisData["param"]["sector"][i]["sub_station"][j]["device_name"]=== ssName) {
						//Check if value is defined in SubStation
						if(gisData["param"]["sector"][i]["sub_station"][j]["performance_data"][key]) {
							//return the value
							return gisData["param"]["sector"][i]["sub_station"][j]["performance_data"][key];
						} else {
							//return default value
							return gisData["param"]["sector"][i]["performance_data"][key];
						}
					}
				}
			}
		}
		return ;
	}
}