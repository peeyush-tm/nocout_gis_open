/**
 * [GisPerformance description]
 */
function GisPerformance() {
	//Is Frozen variable
	this.isFrozen_ = 1;
	//Variable to hold GisData
	this.gisData;

	//Variable to hold Base Stations Name
	this.BSNamesArray= [];

	/*
	Here we start GisPerformance.
	Send an AJax request to get GisPerformance Data
	Store Data in gisData variable
	And start the setInterval function to updateMap every 10 secs.
	 */
	this.start= function() {
		var that= this;
		// for(var k in markersMasterObj['BSNamae']) this.BSNamesArray.push(k);
		this.BSNamesArray.push("Bagahati");
		this.BSNamesArray.push("Rakesh_Bulb_Pataudia");
		setInterval(function() {
			that.sendRequest();
		}, 10000);
	}

	this.sendRequest= function() {
		var counter= 0, that= this;
		while(counter<this.BSNamesArray.length) {
			$.ajax({
				type : 'GET',
				dataType : 'json',
				url:  window.location.origin + '/static/gisPerformance_'+this.BSNamesArray[counter]+'.json',
				async: false}).done(function(data) {
					that.gisData= data;
					that.updateMap();
			});
			counter++;
		}
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
					if(googlePolyLine) {
						googlePolyLine.setOptions({strokeColor:lineColor});
					}
					if(bsMarkerObject['child_ss'][i]["technology"]=== "WiMAX" || bsMarkerObject['child_ss'][i]["technology"]=== "PMP") {
						var sectorPoly= markersMasterObj['Poly'][bsMarkerObject['child_ss'][i]['sub_station'][j]['device_name']];
						if(sectorPoly) {
							sectorPoly.setOptions({fillColor: lineColor});
						}
					}

					var subStationIcon= this.calculatePerformanceValue("performance_icon", bsMarkerObject['child_ss'][i]["device_info"][0]["value"], bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"]);
					if(subStationIcon) {
						var subStationName= bsMarkerObject['child_ss'][i]['sub_station'][j]["device_name"];
						var subStationMarker= markersMasterObj['SSNamae'][subStationName];
						subStationMarker.setIcon(window.location.origin + '/static/img/icons/'+subStationIcon);
						subStationMarker.oldIcon= window.location.origin + '/static/img/icons/'+subStationIcon;
						subStationMarker.clusterIcon= window.location.origin + '/static/img/icons/'+subStationIcon;
					}
				}
				var deviceMarkers = sectorMarkersMasterObj[String(gisData.basestation_name)];
				for(var k=0; k< deviceMarkers.length; k++) {
					var deviceObject= this.findObjectbyDeviceName(deviceMarkers[i]["deviceInfo"][0]["value"]);
					deviceMarkers[i].oldIcon= window.location.origin + '/static/img/icons/'+deviceObject["performance_data"]["performance_icon"];
				}
			}
		}catch(exception) {
			console.log(exception);
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
			if(gisData["param"]["sector"][i]["device_name"]=== device) {
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