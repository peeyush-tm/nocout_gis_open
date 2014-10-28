/*
This function creates a Open Layer Map and loads it in dom. Return callback when map is finished creating.
@param callback {Function} Return function when completed.
 */
WhiteMapClass.prototype.createOpenLayerMap = function(callback) {
		var format = whiteMapSettings.format, domEl= whiteMapSettings.domElement;

		//Bounds for our Open layer.
		var bounds = new OpenLayers.Bounds(
			whiteMapSettings.initial_bounds[0], whiteMapSettings.initial_bounds[1],
			whiteMapSettings.initial_bounds[2], whiteMapSettings.initial_bounds[3]);

		//Options for our White Map
		var options = {
				controls: [
				//Navigation true
				new OpenLayers.Control.Navigation({
					dragPanOptions: {
						enableKinetic: true
					}
				}),
				//Pan Zoom true
				new OpenLayers.Control.PanZoomBar(),
				// new OpenLayers.Control.LayerSwitcher({'ascending':false}),
				new OpenLayers.Control.ScaleLine(),
				//Enable Mouse Position
				new OpenLayers.Control.MousePosition(),
				new OpenLayers.Control.KeyboardDefaults()
			],
			maxExtent: bounds,
			maxResolution: whiteMapSettings.maxResolution,
			projection: whiteMapSettings.projection,
			units: whiteMapSettings.units,
			allOverlays: true
		};

		var linesLayer= "", markersLayer= "", sectorsLayer= "", india_Layer= "", that= this, featuresLayer= "", controls;

		//Create Open Layer map on '#map' with our options
		ccpl_map = new OpenLayers.Map(domEl, options);

		//Create WMS layer to load Map from our geoserver.
		india_Layer = new OpenLayers.Layer.WMS(
			"india_Layer", whiteMapSettings.geoserver_url_India, {
				layers: whiteMapSettings.layer
			}, {
				isBaseLayer: true
			});

		//Add layer to Map
		ccpl_map.addLayer(india_Layer);

		//Click a Click Control for OpenLayer
		var mapClick = new OpenLayers.Control.Click();
		//Add control to Map
		ccpl_map.addControl(mapClick);
		//Activate Click
		mapClick.activate();

		var layerListeners = {
			featureclick: function(e) {
				that.onFeatureSelect(e);
				return false;
			},
			onFeatureUnselect: function(e) {
				that.noFeatureClick(e);
			}
		};

		//Create a Vector Layer which will hold Sectors
		sectorsLayer = new OpenLayers.Layer.Vector('Sectors Layers', {eventListeners: layerListeners});

		//Store sectorsLayer
		this.sectorsLayer = sectorsLayer;

		//Add Sectors Layer to the Map
		ccpl_map.addLayer(sectorsLayer);

		//Create a Vector Layer which will hold Lines
		linesLayer = new OpenLayers.Layer.Vector('Lines Layer', {eventListeners: layerListeners});

		//Store linesLayer
		this.linesLayer= linesLayer;

		//Add Lines Layer to the map
		ccpl_map.addLayer(linesLayer);

		var devicesVectorLayer = new OpenLayers.Layer.Vector("Device Vector Marker Layer");
		this.devicesVectorLayer = devicesVectorLayer;

		ccpl_map.addLayer(devicesVectorLayer);		

		var pointStyle = new OpenLayers.Style({
			label: "${label}",
			fontSize: clustererSettings.fontSize,
			fontWeight: clustererSettings.fontWeight,
			fontColor: clustererSettings.fontColor,
			fontFamily: clustererSettings.fontFamily,
			cursor: "${cursor}",
			externalGraphic: "${symbol}",
			graphicWidth: "${graphicWidth}",
			graphicHeight: "${graphicHeight}",
		}, {
			context: {
				label: function(feature) {
					return feature.cluster.length > 1 ? feature.cluster.length : "";
				},
				cursor: function(feature) {
					if(feature.cluster.length > 1) {
						return "pointer";
					} else {
						return "default";
					}
				},
				symbol: function(feature){
					if (feature.cluster.length > 1){
						if(feature.cluster.length > 1 && feature.cluster.length <= 10) {
							return base_url+"/"+"static/js/OpenLayers/img/m1.png"
						} else if(feature.cluster.length > 10 && feature.cluster.length <= 100) {
							return base_url+"/"+"static/js/OpenLayers/img/m2.png"
						} else if(feature.cluster.length > 100 && feature.cluster.length <= 1000) {
							return base_url+"/"+"static/js/OpenLayers/img/m3.png"
						}
					}
					else{
						return feature.cluster[0].style.externalGraphic
					}
				},
				graphicWidth: function(feature) {
					if(feature.cluster.length > 1) {
						return 55;
					} else {
						return 29;
					}
				},
				graphicHeight: function(feature) {
					if(feature.cluster.length > 1) {
						return 55;
					} else {
						return 40;
					}
				}
			}
		})

		var styleMap = new OpenLayers.StyleMap({
			'default': pointStyle,
		});

		var markersVectorLayer = new OpenLayers.Layer.Vector("Markers Vector Layer", {styleMap  : styleMap,strategies: [new OpenLayers.Strategy.Cluster({distance: 70})]});

		this.markersVectorLayer = markersVectorLayer;

		var selectCtrl = new OpenLayers.Control.SelectFeature(
			markersVectorLayer, {
				clickout: true,
				eventListeners: {
					featurehighlighted: function(feature) {that.markerLayerFeatureClick(feature); return false;}
				}
			}
		);

		ccpl_map.addControl(selectCtrl);
		selectCtrl.activate();

		ccpl_map.addLayer(markersVectorLayer);



		featuresLayer= new OpenLayers.Layer.Vector("draw features layer", {
			eventListeners: {"beforefeatureadded": function() {featuresLayer.destroyFeatures();}}
		});

		this.featuresLayer = featuresLayer;

		controls = {
			// point: new OpenLayers.Control.DrawFeature(featuresLayer, OpenLayers.Handler.Point),
			// line: new OpenLayers.Control.DrawFeature(featuresLayer, OpenLayers.Handler.Path),
			polygon: new OpenLayers.Control.DrawFeature(featuresLayer, OpenLayers.Handler.Polygon, {
				eventListeners: {"featureadded": this.livePollingPolygonAdded}
			})
			// drag: new OpenLayers.Control.DragFeature(featuresLayer)
		};

		this.controls= controls;

		for(var key in controls) {
			ccpl_map.addControl(controls[key]);
		}
		
		//Map set Extend to our bounds
		ccpl_map.zoomToExtent(bounds);

		//return
		callback();
}


/*
* This function create a Marker according to parameter passed and return marker.
* @param size {OpenLayer Size Object} Size of the Marker
* @param iconUrl {String} Url of the MarkerImage
* @param lon {Number} Longitude Number of Marker
* @param lat {Number} Latitude Number of Marker
* @param additionalInfo {Object} Additional Info for the Marker.
* */
WhiteMapClass.prototype.createOpenLayerMarker = function(size, iconUrl, lon, lat, additionalInfo) {

	//Set offset for the Marker
	var offset = new OpenLayers.Pixel(-(size.w / 2), -size.h);
	//Set Lon Lat for the Marker
	var lonLat = new OpenLayers.LonLat(lon, lat); 
	//Set Icon for the Marker
	var icon = new OpenLayers.Icon(iconUrl, size, offset);
	//Create Marker
	var marker = new OpenLayers.Marker(lonLat, icon);
	//Loop through key in additionInfo
	for(var key in additionalInfo) {
		if(additionalInfo.hasOwnProperty(key)) {
			//Add those keys to Marker
			marker[key] = additionalInfo[key];
		}
	}

	//return Marker
	return marker;
}

WhiteMapClass.prototype.createOpenLayerVectorMarker= function(size, iconUrl, lon, lat, additionalInfo) {
		var point = new OpenLayers.Geometry.Point(lon, lat);
		var feature = new OpenLayers.Feature.Vector(point,
			{description: 'This is description'},
			{externalGraphic: iconUrl, graphicHeight: size.h, graphicWidth: size.w, graphicXOffset:-12, graphicYOffset:-size.h});
		// feature.attributes = { icon: iconUrl, label: "myVector", importance: 10, size: size };
		for(var key in additionalInfo) {
		if(additionalInfo.hasOwnProperty(key)) {
			//Add those keys to Marker
			feature.attributes[key] = additionalInfo[key];
		}
	}
return feature;
}


var infoWindow;
/*
This function closes Info Window if it is showing.
 */
WhiteMapClass.prototype.closeInfoWindow = function() {
	if(infoWindow) {
		infoWindow.hide();
		infoWindow.destroy();
		infoWindow= "";
		return  'done';
	}
	return 'no window';
}

function openSectorInfoWindow() {
	var sector, sub_station, tableString = "";
	console.log("Open Sector Info Window");
}

function openLineInfoWindow(id, lon, lat, lineRef, lineData) {
console.log("Open Line Info Windw");
return false;
	var sector = "", sub_station = "", tableString = "";
	outerLoop: for(var i=0; i< lineData.data.param.sector.length; i++) {
		sector= lineData.data.param.sector[i];
		if(sector.circuit_id=== id) {
			for(var j=0; j< sector.sub_station.length; j++) {
				sub_station = sector.sub_station[j];
				if(sub_station.name=== lineRef.ssname) {
					break outerLoop;
				}
			}
		}
	}

	var contentToShow = [
	{
		"name": "Base-Station Name",
		"value": lineData.name
	}, {
		"name": "SS IP",
		"value": sub_station.data.param.sub_station[0].value
	}, {
		"name": "BS Site Name",
		"value": lineData.data.param.base_station[0].value
	}, {
		"name": "Circuit ID",
		"value": id
	}, {
		"name": "BS Site Type",
		"value": lineData.data.param.base_station[3].value
	}, {
		"name": "QOS(BW)",
		"value": sub_station.data.param.sub_station[4].value
	}, {
		"name": "Building Height",
		"value": lineData.data.param.base_station[4].value
	}, {
		"name": "Latitude",
		"value": sub_station.data.param.sub_station[5].value
	}, {
		"name": "Tower Height",
		"value": lineData.data.param.base_station[5].value
	}, {
		"name": "Longitude",
		"value": sub_station.data.param.sub_station[6].value
	}
	];
tableString+= "<table>";
	for(var i=0; i< contentToShow.length; i=i+2) {
		tableString+= "<tr><td>"+contentToShow[i].name+"</td><td>"+contentToShow[i].value+"</td><td>"+contentToShow[i+1].name+"</td><td>"+contentToShow[i+1].value+"</td></tr>";
	}
tableString+= "</table>";
	infoWindow = new OpenLayers.Popup(id,
		new OpenLayers.LonLat(lon, lat),
		null,
		tableString,
		true);
	//Add popup to ccpl_map
	ccpl_map.addPopup(infoWindow);
	//Update Size for InfoWindow
	infoWindow.updateSize();
	//Show InfoWndow
	infoWindow.show();
}
/*
This function open Info Window for the Marker.
@param e {Mouse Click Event} Event Info 
@param marker {Open Layer Marker Object} Marker on which Info Window is to be open
@param markerData {Object} Data to show on InfoWindow
 */
WhiteMapClass.prototype.openInfoWindow = function(e, marker, markerData, sectorData, subStationData) {
	// ccpl_map.addPopup(OpenLayers.Popup.FramedCloud(marker.name, 
	// 	ccpl_map.getLonLatFromPixel(e.xy),
	// 	null, 
	// 	"some text",
	// 	null,
	// 	false, true));
	/*
	This function creates the info content which is shown in Popup
	 */
	function createInfoContent() {
		//Get marker type
		var marker_type = marker.type;		
		//Create a table
		var tableString = "";
		//If type is base_station
		if(marker_type === "base_station") {
			//Get base station data
			var base_station_data = markerData.data.param.base_station;
			//Create table markup
			tableString+= "<table id='base_station_info_table'>";
			//Object which hold content which is shown in the Data
			var contentToShow = [{
				"name": "Base Station Name",
				"value": markerData.name
			}, {
				"name": "Base Site Name",
				"value": base_station_data[0].value
			}, {
				"name": "Bs Site Type",
				"value": base_station_data[3].value
			}, {
				"name": "Building Height",
				"value": base_station_data[4].value
			}, {
				"name" : "Tower Height",
				"value": base_station_data[5].value
			}, {
				"name": "City",
				"value": base_station_data[6].value
			}, {
				"name": "State",
				"value": base_station_data[7].value
			}, {
				"name": "Address",
				"value": base_station_data[8].value
			}
			// , {
			// 	"name": "GPS Type",
			// 	"value": base_station_data[9].value
			// }, {
			// 	"name": "BS Type",
			// 	"value": base_station_data[10].value
			// }, {
			// 	"name": "BS Switch",
			// 	"value": base_station_data[11].value
			// }
			];

			//Loop through the content, and append its table markup
			for(var i=0; i< contentToShow.length; i++) {
				tableString+= "<tr><td>"+contentToShow[i]["name"]+"</td><td>"+contentToShow[i]["value"]+"</td></tr>";
			}
			//finish table
			tableString+= "</table>";
		} else if (marker_type === "base_station_device"){
			tableString+= "<table id='base_station_device_info_table'>";
			var contentToShow = [
				{
					"name": "Device Name",
					"value": sectorData.device_info[0].value
				}, {
					"name": "Technology",
					"value": sectorData.technology
				}, {
					"name": "Vendor",
					"value": sectorData.vendor
				}, {
					"name": "Sector Name",
					"value": sectorData.info[0].value
				}, {
					"name": "Planned Frequency",
					"value": sectorData.info[1].value
				}, {
					"name": "Antenna Type",
					"value": sectorData.info[2].value
				}, {
					"name": "Antenna Tilt",
					"value": sectorData.info[3].value
				}
			];

			//Loop through the content, and append its table markup
			for(var i=0; i< contentToShow.length; i++) {
				tableString+= "<tr><td>"+contentToShow[i]["name"]+"</td><td>"+contentToShow[i]["value"]+"</td></tr>";
			}

			tableString+= "</table>"
		} else if (marker_type === "sub_station") {
			tableString+= "<table id='base_station_device_info_table'>";

			var contentToShow= [
			{
				"name": "SS IP",
				"value": subStationData.data.param.sub_station[0].value
			}, {
				"name": "Circuid ID",
				"value": subStationData.data.param.sub_station[3].value
			}, {
				"name": "QOS(BW)",
				"value": subStationData.data.param.sub_station[4].value
			}, {
				"name": "Latitude",
				"value": subStationData.data.param.sub_station[5].value
			}, {
				"name": "Longitude",
				"value": subStationData.data.param.sub_station[6].value
			}, {
				"name": "Antenna Height",
				"value": subStationData.data.param.sub_station[7].value
			}, {
				"name": "Polarization",
				"value": subStationData.data.param.sub_station[8].value
			}
			];

			//Loop through the content, and append its table markup
			for(var i=0; i< contentToShow.length; i++) {
				tableString+= "<tr><td>"+contentToShow[i]["name"]+"</td><td>"+contentToShow[i]["value"]+"</td></tr>";
			}
			tableString+= "</table>";
		}
		//return tableString
		return tableString;
	}

	//If already a info window is present, hide it
	if(infoWindow) {
		infoWindow.hide();
		// infoWindow.destroy();
	}

	//Create a OpenLayer Popup.
	infoWindow = new OpenLayers.Popup(marker.name,
		marker.lonlat,
		null,
		createInfoContent(),
		true);
	//Add popup to ccpl_map
	ccpl_map.addPopup(infoWindow);
	//Update Size for InfoWindow
	infoWindow.updateSize();
	//Show InfoWndow
	infoWindow.show();
}

//Function to draw line
WhiteMapClass.prototype.drawLine = function(startingLon, startingLat, endingLon, endingLat, color, additionalInfo) {
	var point1 = new OpenLayers.Geometry.Point(startingLon, startingLat);
	var point2 = new OpenLayers.Geometry.Point(endingLon, endingLat);
	//creating an instance of OpenLayers.Geometry.LineString class
	var line = new OpenLayers.Geometry.LineString([point1, point2]);
	//instantiaing OpenLayers.Feature.Vector class
	var vector = new OpenLayers.Feature.Vector(line, {}, {
		strokeColor: color,
		strokeOpacity: 1,
		strokeWidth: 2
	});

	vector.type = "line";
	for(var keys in additionalInfo) {
		if(additionalInfo.hasOwnProperty(keys)) {
			vector[keys] = additionalInfo[keys];
		}
	}
	return vector;
}

//-----------------------------------------------------------
var lastInfoOpen = null;
//Function to bind info window to a marker

WhiteMapClass.prototype.drawSector = function(sectorPointsArray, color, technology, additionalInfo, callback) {

	var style = OpenLayers.Util.extend({}, OpenLayers.Feature.Vector.style['default']);
style.fillColor = color;
if(technology=== "PMP") {
	style.strokeColor = '#ffffff';	
} else {
	style.strokeColor = color;
}
style.strokeWidth = 1;

	// console.log(sectorPointsArray);
	var pointsList = [], linearRing = "", sector = "", feature= "";
	$.each(sectorPointsArray, function(i, sectorPoint) {
		pointsList.push(new OpenLayers.Geometry.Point(sectorPoint.lon, sectorPoint.lat));
	});

	linearRing = new OpenLayers.Geometry.LinearRing(pointsList);

	sector = new OpenLayers.Geometry.Polygon([linearRing]);


	feature = new OpenLayers.Feature.Vector(sector, null, style);


	for(var keys in additionalInfo) {
		if(additionalInfo.hasOwnProperty(keys)) {
			feature[keys] = additionalInfo[keys];
		}
	}
	callback(feature);
}