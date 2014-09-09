/**
 * [GisPerformance description]
 */
function GisPerformance() {
	//Is Frozen variable
	this.isFrozen_ = 0;
	//Variable to hold GisData
	this.gisData;

	//Variable to hold Base Stations Name
	this.BSNamesArray= [];
	//Base Station Length
	this.bsLength= 0;

	/*
	Here we start GisPerformance.
	Send an AJax request to get GisPerformance Data
	Store Data in gisData variable
	And start the setInterval function to updateMap every 10 secs.
	 */
	this.start= function() {
		var perf_that= this;
		for(var k in markersMasterObj['BSNamae']) { this.BSNamesArray.push(k)};
		this.bsLength= this.BSNamesArray.length;

	// Global Variable
		this._isFrozen= isFreeze;
//		this.BSNamesArray.push("Bagahati");
//		this.BSNamesArray.push("Rakesh_Bulb_Pataudia");
		perf_that.sendRequest(0);
		// setInterval(function() {
		// 	console.log("====================START==========================");
		// 	perf_that.sendRequest(0);
		// 	console.log("====================END==========================");
		// }, 60000);
	}

	this.stop= function() {
		this._isFrozen= 1;
	}

	this.restart= function() {
		this._isFrozen= 0;
		this.sendRequest(0);
	}

	this.resetVariable= function() {
		this.gisData= null;
		this.BSNamesArray= [];
		this.bsLength= 0;
		this._isFrozen= isFreeze;
	}

	this.sendRequest= function(counter) {
		// var counter= 0, perf_that= this;
		// while(counter<this.BSNamesArray.length) {
			// var getBsRequestData= this.createRequestData(this.BSNamesArray[counter]);
			// counter++;
		// }
		if(this._isFrozen== 0 && $.cookie('isFreezeSelected')== 0) {
			var perf_that = this;
			// console.log("====================PROCESSING START========================");
			perf_that.waitAndSend(this.createRequestData(this.BSNamesArray[counter]), counter);
			// console.log("====================PROCESSING END========================");	
		}
	}

	this.waitAndSend = function(getBsRequestData, counter) {
		
		var perf_that = this;
		counter++;
		//If all calls has been done, 
		if(counter> this.bsLength) {
			setTimeout(function() {
				perf_that.resetVariable();
				perf_that.start();

			}, 300000);
				
			return;
		}
		if(this._isFrozen== 0 && $.cookie('isFreezeSelected')== 0) {
			$.ajax({
					type : 'POST',
					dataType : 'json',
					data: JSON.stringify(getBsRequestData),
					url:  '/network_maps/performance_data/',//,
					//async: false
					success : function (data) {
						// console.log(JSON.stringify(data));
						perf_that.gisData= data;
						if(data) {
							perf_that.updateMap();
						}
						setTimeout(function() {
							// console.log("====================GET NEXT START========================");
							perf_that.sendRequest(counter);
							// console.log("====================GET NEXT END========================");
						}, 2000);
					},
					error : function(err){
						console.log(err);
					}
				});
		}
	}

	this.createRequestData= function(bsname) {
		var initialdata= {
			"basestation_name": "",
			"basestation_id": null,
			"param": {
				"sector": []
			}
		}
		var bsGmapMarker= markersMasterObj['BSNamae'][bsname];
		if(bsGmapMarker) {
			initialdata["basestation_name"]= bsGmapMarker["bs_name"];
			initialdata["basestation_id"]= bsGmapMarker["bsInfo"][2]["value"];
			for(var i=0; i< bsGmapMarker["child_ss"].length; i++) {
				var deviceSectorJSon= {
					"device_name": bsGmapMarker["child_ss"][i]["device_info"][0]["value"], 
					"device_id": bsGmapMarker["child_ss"][i]["device_info"][1]["value"], 
					"performance_data": {"frequency": "","pl": "","color": "","performance_parameter": "","performance_value": "","performance_icon": ""}, 
					"sub_station": []
				};
				for(var j=0; j< bsGmapMarker["child_ss"][i]["sub_station"].length; j++) {
					var deviceSsJson= {
						"device_name": bsGmapMarker["child_ss"][i]["sub_station"][j]["device_name"],
						"device_id": bsGmapMarker["child_ss"][i]["sub_station"][j]["id"],
						"performance_data": {"frequency": "","pl": "","color": "","performance_parameter": "","performance_value": "","performance_icon": ""}
					}
					deviceSectorJSon["sub_station"].push(deviceSsJson);
				}
				initialdata["param"]["sector"].push(deviceSectorJSon);
			}
		}
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
		var bsMarkerObject= markersMasterObj['BSNamae'][gisData.basestation_name];
		//Step no. 2 ==> Loop through all the SS in the BS
		try {
			for(var i=0; i< bsMarkerObject['child_ss'].length; i++) {
				for(var j=0; j< bsMarkerObject['child_ss'][i]['sub_station'].length; j++) {
					//Step no. 3 ===> Fetch PerformanceValue for various key from GisData JSon
					var lineColor= this.calculatePerformanceValue("color", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
					//Fetch googlePolyline from markersMasterObj;
					var googlePolyLine= markersMasterObj['LinesName'][String(bsMarkerObject["name"])+ bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]];
					// //Update Polyline content.
					if(googlePolyLine && lineColor) {
						googlePolyLine.setOptions({strokeColor:lineColor});
					}
					if(bsMarkerObject['child_ss'][i]["technology"]=== "WiMAX" || bsMarkerObject['child_ss'][i]["technology"]=== "PMP") {
						var sectorPoly= markersMasterObj['Poly'][bsMarkerObject['child_ss'][i]['sub_station'][j]['device_name']];
						if(sectorPoly && lineColor) {
							sectorPoly.setOptions({fillColor: lineColor});
						}
					}

					var subStationIcon= this.calculatePerformanceValue("performance_icon", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
					if(subStationIcon) {
						var subStationName= bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"];
						var subStationMarker= markersMasterObj['SSNamae'][subStationName];
						subStationMarker.setIcon(createGoogleMarker(window.location.origin + '/'+ subStationIcon, subStationMarker));l
						subStationMarker.oldIcon= (createGoogleMarker(window.location.origin + '/'+ subStationIcon, subStationMarker));
						subStationMarker.clusterIcon= (createGoogleMarker(window.location.origin + '/'+ subStationIcon, subStationMarker));
					}
				}
				var deviceMarkers = sectorMarkersMasterObj[String(gisData.basestation_name)];
				for(var k=0; k< deviceMarkers.length; k++) {
					var deviceObject= this.findObjectbyDeviceName(deviceMarkers[i]["deviceInfo"][0]["value"]);
					if(deviceObject["performance_data"]["performance_icon"]) {
						deviceMarkers[i].oldIcon= (createGoogleMarker(window.location.origin + '/'+ deviceObject["performance_data"]["performance_icon"], deviceMarkers[i]));
						
					}
				}
			}
		}catch(exception) {
			// console.log(exception);
		}
	}

	this.findObjectbyDeviceName= function(deviceName) {
		var gisData= this.gisData;
		for(var i=0; i< gisData["param"]["sector"].length; i++) {
			if(gisData["param"]["sector"][i]["device_name"]=== deviceName) {
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
	}
}

function createGoogleMarker(url, oldMarkerIcon) {
	var oldMarObj= {}, newMarkerImage= "";
	oldMarObj['anchor']= oldMarkerIcon['icon']['anchor'] ? oldMarkerIcon['icon']['anchor'] : null;
	oldMarObj['origin']= oldMarkerIcon['icon']['origin'] ? oldMarkerIcon['icon']['origin'] : null;
	oldMarObj['scaledSize']= oldMarkerIcon['icon']['scaledSize'] ? oldMarkerIcon['icon']['scaledSize'] : null;
	oldMarObj['size']= oldMarkerIcon['icon']['size'] ? oldMarkerIcon['icon']['size'] : null;
	newMarkerImage= new google.maps.MarkerImage(
        url,
        oldMarObj['size'],
        oldMarObj['origin'],
        oldMarObj['anchor'],
        oldMarObj['scaledSize']);

	return newMarkerImage;
}