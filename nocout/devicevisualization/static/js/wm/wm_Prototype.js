/*
This function creates a Open Layer Map and loads it in dom. Return callback when map is finished creating.
@param callback {Function} Return function when completed.
 */
WhiteMapClass.prototype.createOpenLayerMap = function(callback) {

		var format, domEl, layers= {}, that= this;

		format = whiteMapSettings.format; 
		domEl= whiteMapSettings.domElement;		

		//Options for our White Map
		var options = { controls: [
				new OpenLayers.Control.Navigation({ dragPanOptions: { enableKinetic: true } }),
				new OpenLayers.Control.PanZoomBar(),
				new OpenLayers.Control.LayerSwitcher({'ascending':false}),
				// new OpenLayers.Control.ScaleLine(), 
				new OpenLayers.Control.MousePosition(),
				new OpenLayers.Control.KeyboardDefaults()
			],
			//Bounds for our Open layer.
			maxExtent: new OpenLayers.Bounds(whiteMapSettings.initial_bounds),
			//Resolution of Open Layer
			maxResolution: whiteMapSettings.maxResolution,
			//Projection of Open Layer
			projection: whiteMapSettings.projection,
			//Unit of Open Layer
			units: whiteMapSettings.units
		};

		//Create Open Layer map on '#map' with our options
		ccpl_map = new OpenLayers.Map(domEl, options);

		//Map Zoom event of trigger mapZoomChangeEvent in events file.
		ccpl_map.events.register("moveend", ccpl_map, function(){
			that.mapZoomChangeEvent(arguments);
			return;
		});

		//Click a Click Control for OpenLayer
		var mapClick = new OpenLayers.Control.Click();
		//Add control to Map
		ccpl_map.addControl(mapClick);
		//Activate Click
		mapClick.activate();

		//Create WMS layer to load Map from our geoserver.
		layers.india_Layer = new OpenLayers.Layer.WMS(
			"india_Layer", whiteMapSettings.geoserver_url_India, {
				layers: whiteMapSettings.layer
			}, {
				isBaseLayer: true
		});

		//Add layer to Map
		ccpl_map.addLayer(layers.india_Layer);

		//Event listener of Features (Line, Sector)
		var featureEventListener = { 
			featureclick: function(e) { 
				that.onFeatureSelect(e); 
				return false; 
			}, 
			onFeatureUnselect: function(e) { 
				that.noFeatureClick(e); 
			} 
		};

		//Create a Vector Layer which will hold Sectors
		layers.sectorsLayer = new OpenLayers.Layer.Vector('Sectors Layers', {eventListeners: featureEventListener});

		//Store sectorsLayer
		this.sectorsLayer = layers.sectorsLayer;

		//Add Sectors Layer to the Map
		ccpl_map.addLayer(layers.sectorsLayer);

		//Create a Vector Layer which will hold Lines
		layers.linesLayer = new OpenLayers.Layer.Vector('Lines Layer', {eventListeners: featureEventListener});

		//Store linesLayer
		this.linesLayer= layers.linesLayer;

		//Add Lines Layer to the map
		ccpl_map.addLayer(layers.linesLayer);

		//vector Layer for Devices Marker
		layers.markerDevicesLayer = new OpenLayers.Layer.Vector("Devices Marker Layer", {visible: false, eventListeners: featureEventListener});

		//Set markerDevicesLayer
		this.markerDevicesLayer = layers.markerDevicesLayer;
		
		//Add layer to the map
		ccpl_map.addLayer(layers.markerDevicesLayer);

		var clusterStyle, styleMap, strategy;

		//Marker Clusterer Styling
		clusterStyle = new OpenLayers.Style({
			//dynamic label
			label: "${label}",
			fontSize: clustererSettings.fontSize,
			fontWeight: clustererSettings.fontWeight,
			fontColor: clustererSettings.fontColor,
			fontFamily: clustererSettings.fontFamily,
			//dynamic cursor setting
			cursor: "${cursor}",
			//dynamic external graphics
			externalGraphic: "${externalGraphic}",
			//dynamic graphic width
			graphicWidth: "${graphicWidth}",
			//dymanic graphic height
			graphicHeight: "${graphicHeight}",
		}, {
			context: {
				//Return label according to cluster length or empty
				label: function(feature) {
					return feature.cluster.length > 1 ? feature.cluster.length : "";
				},
				//Return cursor according to cluster length > 1
				cursor: function(feature) {
					return feature.cluster.length > 1 ? "pointer" : "default";
				},
				//Return Cluster Image or Original graphic of Feature
				externalGraphic: function(feature){

					/*
					 * This function returns cluster Image according to cluster Length
					*/
					function clusterImg(clusterLength) {
						var clusterImg= "";
						if(clusterLength > 1 && clusterLength <= 10) {
							clusterImg= base_url+"/"+"static/js/OpenLayers/img/m1.png"
						} else if(clusterLength > 10 && clusterLength <= 100) {
							clusterImg= base_url+"/"+"static/js/OpenLayers/img/m2.png"
						} else if(clusterLength > 100 && clusterLength <= 1000) {
							clusterImg= base_url+"/"+"static/js/OpenLayers/img/m3.png"
						} else if(clusterLength > 1000 && clusterLength <= 10000) {
							clusterImg= base_url+"/"+"static/js/OpenLayers/img/m4.png"
						} else {
							clusterImg= base_url+"/"+"static/js/OpenLayers/img/m4.png"
						}
						return clusterImg;
					}

					return feature.cluster.length > 1 ? clusterImg(feature.cluster.length) : feature.cluster[0].style.externalGraphic;
				},
				graphicWidth: function(feature) {
					return feature.cluster.length > 1 ? 55 : feature.cluster[0].style.graphicWidth;
				},
				graphicHeight: function(feature) {
					return feature.cluster.length > 1 ? 55 : feature.cluster[0].style.graphicHeight;
				}
			}
		});

		//OpenLayr Style Map for Markers Layer
		styleMap = new OpenLayers.StyleMap({
			'default': clusterStyle,
		});

		//Create a OpenLayer Strategy Cluster
		strategy= new OpenLayers.Strategy.Cluster({distance: clustererSettings.clustererDistance});

		//Create a Vector Layer for Markers with styleMap and strategy
		layers.markersLayer = new OpenLayers.Layer.Vector("Markers Layer", {styleMap  : styleMap,strategies: [strategy]});

		//Set strategy 
		this.markersLayerStrategy = strategy;

		//Set markersLayer
		this.markersLayer = layers.markersLayer;

		//Click control for Marker Layer feature to call markerClick()
		var selectCtrl = new OpenLayers.Control.SelectFeature(
			layers.markersLayer, {
				clickout: true, toggle: true, multiple: false, hover: false,
				eventListeners: {
					//on feature click
					featurehighlighted: function(feature) {that.markerClick(feature); selectCtrl.unselectAll(); return false;}
				}
			}
		);

		//Add control to the map
		ccpl_map.addControl(selectCtrl);

		//And activate it
		selectCtrl.activate();

		//Add layer to the map
		ccpl_map.addLayer(layers.markersLayer);

		//vector Layer for Live Poll Polygon, before Adding feature, remove any previous feature created.
		layers.livePollFeatureLayer= new OpenLayers.Layer.Vector("Live Poll Features Layer", {
			eventListeners: {"beforefeatureadded": function() {layers.livePollFeatureLayer.destroyFeatures();}}
		});

		//Set livePollFeatureLayer
		this.livePollFeatureLayer = layers.livePollFeatureLayer;

		//Live Poll Polygon Control
		this.livePollingPolygonControl = new OpenLayers.Control.DrawFeature(layers.livePollFeatureLayer, OpenLayers.Handler.Polygon, {eventListeners: {"featureadded": this.livePollingPolygonAdded}});

		//vector Layer for Search Icon
		layers.searchMarkerLayer = new OpenLayers.Layer.Vector("Search Markers Layer");

		layers.searchMarkerLayer.display(false);

		//Set searchMarkerLayer
		this.searchMarkerLayer = layers.searchMarkerLayer;

		//Add layer to the map
		// ccpl_map.addLayer(layers.searchMarkerLayer);

		var panel = new OpenLayers.Control.Panel();

		panel.addControls([new OpenLayers.Control.FullScreen()]);
		
		ccpl_map.addControl(panel);
		
		//Map set Extend to our bounds
		ccpl_map.zoomToExtent(new OpenLayers.Bounds(whiteMapSettings.initial_bounds));
		//return
		callback();
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
WhiteMapClass.prototype.plotLines_wmap = function(startingLon, startingLat, endingLon, endingLat, color, additionalInfo) {
	var point1 = new OpenLayers.Geometry.Point(startingLon, startingLat);
	var point2 = new OpenLayers.Geometry.Point(endingLon, endingLat);
	//creating an instance of OpenLayers.Geometry.LineString class
	var line = new OpenLayers.Geometry.LineString([point1, point2]);
	//instantiaing OpenLayers.Feature.Vector class
	var vector = new OpenLayers.Feature.Vector(line, {}, {
		strokeColor: color,
		strokeOpacity: 1,
		strokeWidth: 2,
		strokeWeight: 3
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

WhiteMapClass.prototype.plotSector_wmap = function(sectorPointsArray, additionalInfo) {

	var style = OpenLayers.Util.extend({}, OpenLayers.Feature.Vector.style['default']);
	var pointsList = [], linearRing = "", sector = "", feature= "";

	style.fillColor = additionalInfo.fillColor;
	style.strokeColor = additionalInfo.strokeColor;
	style.strokeWidth = additionalInfo.strokeWeight;
	
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
	return feature;
}