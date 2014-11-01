var searchMarkerLayer= "";
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
		var options = { controls: [
				new OpenLayers.Control.Navigation({ dragPanOptions: { enableKinetic: true } }),
				new OpenLayers.Control.PanZoomBar(),
				new OpenLayers.Control.LayerSwitcher({'ascending':false}),
				// new OpenLayers.Control.ScaleLine(), 
				new OpenLayers.Control.MousePosition(),
				// new OpenLayers.Control.KeyboardDefaults()
			],
			maxExtent: bounds,
			maxResolution: whiteMapSettings.maxResolution,
			projection: whiteMapSettings.projection,
			units: whiteMapSettings.units
		};

		var linesLayer= "", markersLayer= "", sectorsLayer= "", india_Layer= "", that= this, featuresLayer= "", controls;

		//Create Open Layer map on '#map' with our options
		ccpl_map = new OpenLayers.Map(domEl, options);

		ccpl_map.events.register("zoomend", ccpl_map, function(){
			if(ccpl_map.getZoom() > whiteMapSettings.zoomLevelAfterLineAppears) {
				var selectedValue = $("#showConnLines").prop('checked', true);
			} else {
				var selectedValue = $("#showConnLines").prop('checked', false);
			}
			that.toggleLines();
		});

		//Click a Click Control for OpenLayer
		var mapClick = new OpenLayers.Control.Click();
		//Add control to Map
		ccpl_map.addControl(mapClick);
		//Activate Click
		mapClick.activate();

		//Create WMS layer to load Map from our geoserver.
		india_Layer = new OpenLayers.Layer.WMS(
			"india_Layer", whiteMapSettings.geoserver_url_India, {
				layers: whiteMapSettings.layer
			}, {
				isBaseLayer: true
		});

		//Add layer to Map
		ccpl_map.addLayer(india_Layer);

		var layerEventListener = { featureclick: function(e) { that.onFeatureSelect(e); return false; }, onFeatureUnselect: function(e) { that.noFeatureClick(e); } };

		//Create a Vector Layer which will hold Sectors
		sectorsLayer = new OpenLayers.Layer.Vector('Sectors Layers', {eventListeners: layerEventListener});

		//Store sectorsLayer
		this.sectorsLayer = sectorsLayer;

		//Add Sectors Layer to the Map
		ccpl_map.addLayer(sectorsLayer);

		//Create a Vector Layer which will hold Lines
		linesLayer = new OpenLayers.Layer.Vector('Lines Layer', {eventListeners: layerEventListener});

		//Store linesLayer
		this.linesLayer= linesLayer;

		//Add Lines Layer to the map
		ccpl_map.addLayer(linesLayer);

		searchMarkerLayer = new OpenLayers.Layer.Vector("Search Marker Vector Layer");
		ccpl_map.addLayer(searchMarkerLayer);

		var devicesVectorLayer = new OpenLayers.Layer.Vector("Device Vector Marker Layer", {eventListeners: layerEventListener});
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
					if(feature.cluster && feature.cluster.length > 1) {
						return feature.cluster.length > 1 ? feature.cluster.length : "";
					} else {
						return "";
					}
				},
				cursor: function(feature) {
					if(feature.cluster && feature.cluster.length) {
						if(feature.cluster.length > 1) {
							return "pointer";
						} else {
							return "default";
						}
					} else {
						return "default";
					}
				},
				symbol: function(feature){
					if (feature.cluster && feature.cluster.length > 1){
						if(feature.cluster.length > 1 && feature.cluster.length <= 10) {
							return base_url+"/"+"static/js/OpenLayers/img/m1.png"
						} else if(feature.cluster.length > 10 && feature.cluster.length <= 100) {
							return base_url+"/"+"static/js/OpenLayers/img/m2.png"
						} else if(feature.cluster.length > 100 && feature.cluster.length <= 1000) {
							return base_url+"/"+"static/js/OpenLayers/img/m3.png"
						}
					} else{
						if(feature.cluster && feature.cluster.length) {
							return feature.cluster[0].style.externalGraphic
						} else {
							return "";
						}
					}
				},
				graphicWidth: function(feature) {
					if(feature.cluster && feature.cluster.length > 1) {
						return 55;
					} else {
						return 29;
					}
				},
				graphicHeight: function(feature) {
					if(feature.cluster && feature.cluster.length > 1) {
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

		var strategy= new OpenLayers.Strategy.Cluster({distance: clustererSettings.clustererDistance});

		var markersVectorLayer = new OpenLayers.Layer.Vector("Markers Vector Layer", {styleMap  : styleMap,strategies: [strategy]});

		this.markerLayerStrategy = strategy;

		this.markersVectorLayer = markersVectorLayer;

		var selectCtrl = new OpenLayers.Control.SelectFeature(
			markersVectorLayer, {
				clickout: true, toggle: true,
				multiple: true, hover: false,
				eventListeners: {
					featurehighlighted: function(feature) {that.markerLayerFeatureClick(feature); selectCtrl.unselectAll(); 	return false;}
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
			polygon: new OpenLayers.Control.DrawFeature(featuresLayer, OpenLayers.Handler.Polygon, {
				eventListeners: {"featureadded": this.livePollingPolygonAdded}
			})
		};

		this.controls= controls;

		for(var key in controls) {
			ccpl_map.addControl(controls[key]);
		}

		var panel = new OpenLayers.Control.Panel();
		panel.addControls([
			new OpenLayers.Control.Button({ displayClass: "helpButton", trigger: function() {alert('Full screen')}, title: 'Full Screen' })
		]);

		ccpl_map.addControl(panel);
		
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
/*
This function open Info Window for the Marker.
@param e {Mouse Click Event} Event Info 
@param marker {Open Layer Marker Object} Marker on which Info Window is to be open
@param markerData {Object} Data to show on InfoWindow
 */
WhiteMapClass.prototype.openInfoWindow = function(e, marker, markerData, sectorData, subStationData) {
	
	//If already a info window is present, hide it
	if(infoWindow) {
		infoWindow.hide();
		// infoWindow.destroy();
	}

	//Create a OpenLayer Popup.
	infoWindow = new OpenLayers.Popup(marker.name,
		marker.lonlat,
		null,
		contentString,
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