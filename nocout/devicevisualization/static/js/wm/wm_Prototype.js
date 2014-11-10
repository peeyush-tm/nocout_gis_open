/**
 * This function creates a Open Layer Map and loads it in dom. Return callback when map is finished creating.
 * @param  {Function} callback Return function when completed.
 * @return {[undefined]}
 */
WhiteMapClass.prototype.createOpenLayerMap = function(callback) {

		var format, domEl, layers= {}, that= this;

		format = whiteMapSettings.format; 
		domEl= whiteMapSettings.domElement;		

		//Options for our White Map. Add navigation, panZoombar bar and mouse position
		var wmap_options = { 
			controls: [
				new OpenLayers.Control.Navigation({ dragPanOptions: { enableKinetic: true } }),
				new OpenLayers.Control.PanZoomBar(),
				new OpenLayers.Control.MousePosition({
					prefix: whiteMapSettings.latLngPrefixLabel
				}),
				new OpenLayers.Control.LayerSwitcher()
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

		//Create Open Layer map on '#map' with our wmap_options
		ccpl_map = new OpenLayers.Map(domEl, wmap_options);

		//Click a Click Control for OpenLayer
		var mapClick = new OpenLayers.Control.Click();
		//Add control to Map
		ccpl_map.addControl(mapClick);
		//Activate Click
		mapClick.activate();

		//Map moveend event
		ccpl_map.events.register("moveend", ccpl_map, function(e){
			that.mapIdleCondition();
			return;
		});

		//Create WMS layer to load Map from our geoserver.
		layers.india_Layer = new OpenLayers.Layer.WMS(
			"india_Layer", whiteMapSettings.geoserver_url_India, {
				layers: whiteMapSettings.layer
			}
		);

		//Add layer to Map
		ccpl_map.addLayer(layers.india_Layer);

		//Create a vector Layer for Search Markers
		layers.searchMarkerLayer = new OpenLayers.Layer.Vector("Search Layer", {
            styleMap: new OpenLayers.StyleMap({
                "default": new OpenLayers.Style(OpenLayers.Util.applyDefaults({
                	//dynamic external graphics
                	externalGraphic: '${icon}',
                	//dynamic graphic width
                	graphicWidth: 71,
                	//dymanic graphic height
                	graphicHeight: 77
                }, OpenLayers.Feature.Vector.style["default"]))
            })
        });

		//Add layer to the map
		ccpl_map.addLayer(layers.searchMarkerLayer);

		layers.searchMarkerLayer.setVisibility(false);

		// KML 	FILE CODE
		 // var kmlUrl = base_url+'/static/doc.kml';
		 // var groundOverlay = new OpenLayers.Layer.Vector("KML2", {
		 // 	renderers: location.search.indexOf('Canvas') >= 0 ? ['Canvas', 'SVG', 'VML'] : ['SVG', 'VML', 'Canvas'],
		 // 	projection: ccpl_map.displayProjection,
		 // 	strategies: [new OpenLayers.Strategy.Fixed()],
		 // 	protocol: new OpenLayers.Protocol.HTTP({
		 // 		url: kmlUrl,
		 // 		format: new OpenLayers.Format.KML({
		 // 			maxDepth: 1,
		 // 			baseUrl: kmlUrl,
		 // 			extractStyles: true,
		 // 			extractAttributes: true
		 // 		})
		 // 	})
		 // });

		 // ccpl_map.addLayer(groundOverlay);
		
		// var kmlFileExample = new OpenLayers.Layer.Vector("kml layer", {
		// 	// projection: new OpenLayers.Projection("EPSG:4326"),
		// 	sphericalMercator: true,
		// 	strategies: [new OpenLayers.Strategy.Fixed()],
		// 	protocol: new OpenLayers.Protocol.HTTP({
		// 		url: base_url+'/static/doc.kml',
		// 		format: new OpenLayers.Format.KML({
		// 			extractStyles: true,
		// 			extractAttributes: true,
		// 			maxDepth: 10
		// 		})
		// 	}),
		// 	visible: true
		// });
		// kmlFileExample.setVisibility(true);
		// ccpl_map.addLayer(kmlFileExample);

		//Event listener of Features (Line, Sector, Devices)
		// var featureEventListener = {
		// 	featureclick: function(e) { 
		// 		that.onFeatureSelect(e); 
		// 		return false; 
		// 	}
		// };

		//Create a Vector Layer which will hold Sectors
		layers.sectorsLayer = new OpenLayers.Layer.Vector('Sectors');

		//Add Sectors Layer to the Map
		ccpl_map.addLayer(layers.sectorsLayer);

		//Create a Vector Layer which will hold Lines
		layers.linesLayer = new OpenLayers.Layer.Vector('Lines');

		layers.linesLayer.setVisibility(false);

		//Add Lines Layer to the map
		ccpl_map.addLayer(layers.linesLayer);

		//vector Layer for Devices Marker
		layers.markerDevicesLayer = new OpenLayers.Layer.Vector("Devices");

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
			graphicHeight: "${graphicHeight}"
			// graphicXOffset: "${graphicXOffset}",
			// graphicYOffset: "${graphicYOffset}"
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
					if(feature.cluster.length > 1) {
						return 55;
					} else {
						var currentSize = getIconSize();
						if(feature.attributes.pointType === "base_station") {
							return currentSize.bs_devices_size.graphicWidth
						} else {
							return currentSize.ss_devices_size.graphicWidth
						}
					}
				},
				graphicHeight: function(feature) {
					if(feature.cluster.length > 1) {
						return 55;
					} else {
						var currentSize = getIconSize();
						if(feature.attributes.pointType === "base_station") {
							return currentSize.bs_devices_size.graphicHeight
						} else {
							return currentSize.ss_devices_size.graphicHeight
						}
					}
				}
			}
		});

		//OpenLayr Style Map for Markers Layer
		styleMap = new OpenLayers.StyleMap({
			'default': clusterStyle
		});

		//Create a OpenLayer Strategy Cluster
		strategy= new OpenLayers.Strategy.Cluster({distance: clustererSettings.clustererDistance});

		//Create a Vector Layer for Markers with styleMap and strategy
		layers.markersLayer = new OpenLayers.Layer.Vector("Markers", {styleMap  : styleMap, strategies: [strategy]});

		//Add layer to the map
		ccpl_map.addLayer(layers.markersLayer);

		//Click control for Marker Layer feature to call markerClicked()
		var selectCtrl = new OpenLayers.Control.SelectFeature(
			[layers.markersLayer, layers.markerDevicesLayer, layers.linesLayer, layers.sectorsLayer], {
				clickout: true,
				eventListeners: {
					//on feature click
					featurehighlighted: function(feature) {
						console.log(feature);
						that.layerFeatureClicked(feature);
						selectCtrl.unselectAll();
						return false;
					}
				}
			}
		);

		//Add control to the map
		ccpl_map.addControl(selectCtrl);

		//And activate it
		selectCtrl.activate();

		//vector Layer for Live Poll Polygon, before Adding feature, remove any previous feature created.
		layers.livePollFeatureLayer= new OpenLayers.Layer.Vector("Livepolling", {
			eventListeners: {
				"beforefeatureadded": function() {
					if(this.features.length) {
						this.destroyFeatures();						
					}
				}
			}
		});

		//Live Poll Polygon Control
		var polygonControl = new OpenLayers.Control.DrawFeature(layers.livePollFeatureLayer, OpenLayers.Handler.Polygon, {
			eventListeners: {
				"featureadded": this.livePollingPolygonAdded
			}
		});

		this.livePollingPolygonControl = polygonControl;

		ccpl_map.addControl(polygonControl);
		
		var panel = new OpenLayers.Control.Panel();

		panel.addControls([new OpenLayers.Control.FullScreen()]);
		
		ccpl_map.addControl(panel);
		
		//Map set Extend to our bounds
		ccpl_map.zoomToExtent(new OpenLayers.Bounds(whiteMapSettings.initial_bounds));

		//return
		callback();
}

/**
 * This function creates Open Layer Vector Feature Marker
 * @param  {[Openlayer Size Object]} size   Size for Feature
 * @param  {String} iconUrl        Url for the Icon
 * @param  {Number} lon            Longitude of Marker
 * @param  {Number} lat            Latitude of Marker
 * @param  {Object} additionalInfo Additional Info to add in the Marker
 * @return {OpenLayer Vector}      OpenLayer Vector feature created
 */
WhiteMapClass.prototype.createOpenLayerVectorMarker= function(size, iconUrl, lon, lat, additionalInfo) {
		var point = new OpenLayers.Geometry.Point(lon, lat);
		if(size && iconUrl) {
			var feature = new OpenLayers.Feature.Vector(point,
				{description: 'This is description'},
				{externalGraphic: iconUrl, graphicHeight: size.h, graphicWidth: size.w});
			
		} else {
			var feature = new OpenLayers.Feature.Vector(point,
				{description: 'This is description'});
		}
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