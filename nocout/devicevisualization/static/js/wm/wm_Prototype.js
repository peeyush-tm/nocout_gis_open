// Global Variables
var maintenance_popup = "",
	pl_rta_popup = "";

/**
 * This function creates a Open Layer Map and loads it in dom. Return callback when map is finished creating.
 * @param  {Function} callback Return function when completed.
 * @return {[undefined]}
 */
WhiteMapClass.prototype.createOpenLayerMap = function(callback) {

	var format, domEl, layers= {}, that= this;

	format = whiteMapSettings.format; 
	domEl = whiteMapSettings.domElement;

	//Options for our White Map. Add navigation, panZoombar bar and mouse position
	var wmap_options = { 
		controls: [
			new OpenLayers.Control.Navigation({ dragPanOptions: { enableKinetic: true } }),
			new OpenLayers.Control.PanZoomBar(),
			new OpenLayers.Control.MousePosition({
				prefix: whiteMapSettings.latLngPrefixLabel
			})
			// new OpenLayers.Control.LayerSwitcher()
		],
		// Center for openLayer map
		center : new OpenLayers.LonLat(whiteMapSettings.mapCenter[0], whiteMapSettings.mapCenter[1]),
		// Zoom level for openLayers map
		zoom : 1,
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

	ccpl_map.events.register("click", ccpl_map, function(e) {
		// Remove BS maintenance popup if exists
		if(maintenance_popup) {
			ccpl_map.removePopup(maintenance_popup);
			maintenance_popup = "";
		}

		// Remove SS or Sector (PL,RTA) popup if exists
		if(pl_rta_popup) {
			ccpl_map.removePopup(pl_rta_popup);
			pl_rta_popup = "";
		}

		that.unSpiderifyWmapMarker()
	});

	//Map moveend event(Used for pan & zoom both cases)
	ccpl_map.events.register("moveend", ccpl_map, function(e) {
		that.mapIdleCondition();
		return;
	});

	//Map zoomend event
	// ccpl_map.events.register("zoomend", ccpl_map, function(e){
	// 	that.mapIdleCondition();
	// 	return;
	// });

	//Create WMS layer to load Map from our geoserver.
	layers.india_Layer = new OpenLayers.Layer.WMS(
		"india_Layer", whiteMapSettings.geoserver_url_India, {
			layers: whiteMapSettings.layer
		}
	);

	//Add layer to Map
	ccpl_map.addLayer(layers.india_Layer);

	/*
	OpenLayer Vector Layer For Showing State Labels
	 */
		//State Label Default Style
		var stateLabelStyle = new OpenLayers.Style({
			externalGraphic: base_url+"/static/js/OpenLayers/img/state_cluster.png",
			fontSize: clustererSettings.fontSize,
			fontWeight: clustererSettings.fontWeight,
			fontColor: clustererSettings.fontColor,
			fontFamily: clustererSettings.fontFamily,
			//get cursor from feature attribute cursor property
			cursor: "${cursor}",
			graphicWidth: "65",
			graphicHeight: "65",
			//get title from feature attribute title property
			title: "${title}",
			//get label for feature attribute label property
			label: "${label}",
			display: "${display}"
		});


		//Create OpenLayers StyleMap. Set default to the stateLabelStyle
		var stateLayerStyleMap = new OpenLayers.StyleMap({
			'default': stateLabelStyle
		});

		//Create OpenLayer Vector Layer for States Label and set it styleMap to the one created above.
		layers.stateLabelLayer = new OpenLayers.Layer.Vector("States", {styleMap: stateLayerStyleMap});

		//Add Layer to the Map
		ccpl_map.addLayer(layers.stateLabelLayer);
	/*
	End of OpenLayer Vector Layer For Showing State Labels
	 */

	 /*
	OpenLayer Vector Layer For Showing Search Markers
	 */
		//OpenLayers Vector Layer for Search Marker
		layers.searchMarkerLayer = new OpenLayers.Layer.Vector("Search Layer", {
            styleMap: new OpenLayers.StyleMap({
                "default": new OpenLayers.Style(OpenLayers.Util.applyDefaults({
                	//dynamic external graphics
                	externalGraphic: '${icon}',
                	//dynamic graphic width
                	graphicWidth: 71,
                	//dymanic graphic height
                	graphicHeight: 77,
                	graphicYOffset: -77
                }, OpenLayers.Feature.Vector.style["default"]))
            })
        });

        ccpl_map.addLayer(layers.searchMarkerLayer);
	/*
	End of OpenLayer Vector Layer For Showing Search Markers
	 */

	 /*
	End of OpenLayer Vector Layer For Showing KML Layer
	 */
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
	/*
	End of OpenLayer Vector Layer For Showing KML Layer
	 */


	 /*
	OpenLayer Vector Layer For Showing Wimax-PMP Sectors Polygon
	 */
		//Create a Vector Layer which will hold Sectors
		layers.sectorsLayer = new OpenLayers.Layer.Vector('Sectors');

		//Add Sectors Layer to the Map
		ccpl_map.addLayer(layers.sectorsLayer);

		//Create a Vector Layer which will hold Sectors
		layers.spider_ss_lines = new OpenLayers.Layer.Vector('Spider_SS_Lines');

		//Add Sectors Layer to the Map
		ccpl_map.addLayer(layers.spider_ss_lines);
	/*
	End of OpenLayer Layer Vector For Showing Wimax-PMP Sectors Polygon
	 */
	
	 /*
	OpenLayer Vector Layer For Showing Lines
	 */
		//Create a Vector Layer which will hold Lines
		layers.linesLayer = new OpenLayers.Layer.Vector('Lines');

		//Add Lines Layer to the Map
		ccpl_map.addLayer(layers.linesLayer);

		//Create a Vector Layer which will hold Lines
		layers.red_cross = new OpenLayers.Layer.Vector('RedCross');

		//Add Red Cross Layer to the Map
		ccpl_map.addLayer(layers.red_cross);

	/*
	End of OpenLayer Layer Vector For Showing Lines
	 */
	
	 /*
	OpenLayer Vector Layer For Showing Sector Devices
	 */
		//Create a Vector Layer which will hold Sectors
		layers.markerDevicesLayer = new OpenLayers.Layer.Vector('Devices');

		//Add Devices Layer to the Map
		ccpl_map.addLayer(layers.markerDevicesLayer);
	/*
	End of OpenLayer Layer Vector For Showing Sector Devices
	 */
	
	 /*
	OpenLayer Vector Layer For Showing BS and SS
	 */
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
					var cluster_size = feature.cluster && feature.cluster.length > 1 ? feature.cluster.length : "";
					return cluster_size;
				},
				//Return cursor according to cluster length > 1
				cursor: function(feature) {
					var cluster_cursor = feature.cluster && feature.cluster.length > 1 ? "pointer" : "default";
					return cluster_cursor;
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

					var isCluster = feature.cluster ? true : false,
						cluster_icon = isCluster && feature.cluster.length > 1 ? clusterImg(feature.cluster.length) : "";

					return cluster_icon;
				},
				graphicWidth: function(feature) {
					var isCluster = feature.cluster ? true : false;
					if(isCluster && feature.cluster.length > 1) {
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
					var isCluster = feature.cluster ? true : false;
					if(isCluster && feature.cluster.length > 1) {
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
			"default": clusterStyle
		});

		//Create a OpenLayer Strategy Cluster
		strategy = new OpenLayers.Strategy.Cluster({
			"distance": clustererSettings.clustererDistance, 
			"threshold": clustererSettings.threshold,
			"autoActivate": false,
			"autoDestroy": false
		});


		//Create a Vector Layer for Markers with styleMap and strategy
		layers.markersLayer = new OpenLayers.Layer.Vector("Markers", {
			styleMap   : styleMap,
			strategies : [strategy]
		});

		//Add layer to the map
		ccpl_map.addLayer(layers.markersLayer);
	 /*
	End of OpenLayer Vector Layer For Showing BS and SS
	 */
	
	/*
	Select Control for BS, SS, Devices, Lines and Sectors Layer[Click event]
	 */
		//Hover Control for Openlayers layer
		var hoverControl = new OpenLayers.Control.SelectFeature([layers.markersLayer, layers.markerDevicesLayer], { 
			hover: false,
			click : true,
			highlightOnly: true,
			renderIndent: "temporary",
			eventListeners: {
				onfeatureselected: function(e) {
					// setTimeout(function() {
					// 	whiteMapClass.mouseOverEvent(e);
					// }, 20);
				},
				beforefeaturehighlighted: function(e) {
					whiteMapClass.mouseOutEvent();
				},
				featurehighlighted: function(e) {
					setTimeout(function() {
						whiteMapClass.mouseOverEvent(e);
					}, 20);
				},
				featureunhighlighted: function(e) {
					whiteMapClass.mouseOutEvent(e);
				}
			}
		} );

		//Select Control for Openlayers layer.
		var selectCtrl = new OpenLayers.Control.SelectFeature(
			[
				layers.stateLabelLayer,
				layers.markersLayer,
				layers.markerDevicesLayer,
				layers.linesLayer,
				layers.sectorsLayer
			],
			{
				clickout: true
			}
		);

		//Add control to the map
		ccpl_map.addControl(hoverControl);
		ccpl_map.addControl(selectCtrl);

		//Activate Control
		hoverControl.activate();
		selectCtrl.activate();

		layers.stateLabelLayer.events.on({
			featureselected: function(e) {
				var feature = e.feature;
				gmap_self.state_label_clicked(feature.attributes.state_param);
			}
		});

		layers.markersLayer.events.on({
			featureselected: function(e) {
				var feature = e.feature;
				that.layerFeatureClicked(feature);
				selectCtrl.unselectAll();
				return false;
			}
		});

		layers.markerDevicesLayer.events.on({
			featureselected: function(e) {
				var feature = e.feature;
				that.layerFeatureClicked(feature);
				selectCtrl.unselectAll();
				return false;
			}
		});

		layers.linesLayer.events.on({
			featureselected: function(e) {
				var feature = e.feature;
				that.layerFeatureClicked(feature);
				selectCtrl.unselectAll();
				return false;
			}
		});

		layers.sectorsLayer.events.on({
			featureselected: function(e) {
				var feature = e.feature;
				that.layerFeatureClicked(feature);
				selectCtrl.unselectAll();
				return false;
			}
		});
	 /*
	End of Select Control for BS, SS, Devices, Lines and Sectors Layer[Click event]
	 */

	/*
	OpenLayer Vector Layer For Creating Polygon[for Live Polling or Export Data]
	 */
		//OpenLayers Vector Layer for creating Polygons [Live POll and Export Data]
		layers.livePollFeatureLayer= new OpenLayers.Layer.Vector("Polling", {
			eventListeners: {
				//Before adding new feature
				"beforefeatureadded": function() {
					//If already a feature is present on the layer
					if(this.features.length) {
						//remove previous all features.
						this.destroyFeatures();						
					}
				}
			}
		});

		//Add layer to the map
		ccpl_map.addLayer(layers.livePollFeatureLayer);

		//Polygon Control which will be used to Draw Polygon on the map. Call livePollingPolygonAdded() when polygon is created.
		var polygonControl = new OpenLayers.Control.DrawFeature(layers.livePollFeatureLayer, OpenLayers.Handler.Polygon, {
			eventListeners: {
				"featureadded": this.livePollingPolygonAdded
			}
		});

		//set this control to a public variable
		this.livePollingPolygonControl = polygonControl;

		//add control to the map
		ccpl_map.addControl(polygonControl);
	/*
	End of OpenLayer Vector Layer For Creating Polygon[for Live Polling or Export Data]
	 */


	/**
	 * START - EXPORT DATA POLYGON LAYER BLOCK
	 */

	layers.livePollFeatureLayer= new OpenLayers.Layer.Vector("export_Polling", {
		eventListeners: {
			//Before adding new feature
			"beforefeatureadded": function() {
				//If already a feature is present on the layer
				if(this.features.length) {
					//remove previous all features.
					this.destroyFeatures();						
				}
			}
		}
	});

	//Add layer to the map
	ccpl_map.addLayer(layers.livePollFeatureLayer);

	//Polygon Control which will be used to Draw Polygon on the map. Call livePollingPolygonAdded() when polygon is created.
	var exportData_polygonControl = new OpenLayers.Control.DrawFeature(layers.livePollFeatureLayer, OpenLayers.Handler.Polygon, {
		eventListeners: {
			"featureadded": this.exportDataPolygonAdded
		}
	});

	//set this control to a public variable
	this.exportDataPolygonControl = exportData_polygonControl;

	//add control to the map
	ccpl_map.addControl(exportData_polygonControl);

	/**
	 * END - EXPORT DATA POLYGON LAYER BLOCK
	 */

	//Get Control Panels
	var panel = new OpenLayers.Control.Panel();

	//Add Full Screen Control Panel to it
	// panel.addControls([new OpenLayers.Control.FullScreen()]);
	
	//Show Panel on the map.
	ccpl_map.addControl(panel);
	
	//Map set Extend to our bounds
	ccpl_map.zoomToExtent(new OpenLayers.Bounds(whiteMapSettings.initial_bounds));

	// Bind Right click of White Map
	ccpl_map.div.oncontextmenu = function noContextMenu(e) {
		// In Case Of IE
		if(!e) {
		    var e = window.event;
		    e.returnValue = false;
		}

		// Remove BS maintenance popup if exists
		if(maintenance_popup) {
			ccpl_map.removePopup(maintenance_popup);
			maintenance_popup = "";
		}

		// Remove SS or Sector (PL,RTA) popup if exists
		if(pl_rta_popup) {
			ccpl_map.removePopup(pl_rta_popup);
			pl_rta_popup = "";
		}

		var clicked_feature = ccpl_map.getLayersByName('Markers')[0].getFeatureFromEvent(e),
			sector_feature =  ccpl_map.getLayersByName('Devices')[0].getFeatureFromEvent(e),
			clicked_point_type = clicked_feature ? clicked_feature.pointType : false;

		if(clicked_feature || sector_feature) {

			if(!clicked_point_type) {
				clicked_point_type = sector_feature.pointType;
			}

			// In case of base station continue with maintenance status functionality
			if(clicked_point_type == 'base_station') {
				gmap_self.startBsMaintenanceFunction(clicked_feature);
			} else if(clicked_point_type == 'sub_station') {
				createPLRtaLabel(clicked_feature);
			} else if(clicked_point_type == 'sector_Marker') {
				createPLRtaLabel(sector_feature);
			}
		}

		e.preventDefault()
	}

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

	var feature= "",
		point = new OpenLayers.Geometry.Point(lon, lat);

	//If size and iconUrl is present, create Vector feature using those
	if(size && iconUrl) {
		feature = new OpenLayers.Feature.Vector(
			point,
			{},
			{
				externalGraphic: iconUrl,
				graphicHeight: size.h,
				graphicWidth: size.w
			}
		);
	} else {
		feature = new OpenLayers.Feature.Vector(point, {});
	}

	//Add additional Info to the feature
	for(var key in additionalInfo) {
		if(additionalInfo.hasOwnProperty(key)) {
			//Add those keys to Marker
			feature[key] = additionalInfo[key];
		}
	}

	//return feature
	return feature;
}

/**
 * This function creates a link between Bs & SS
 * @method plotLines_wmap. 
 * @param startEndObj {Object}, It contains the start & end points json object.
 * @param linkColor {String}, It contains the color for link line.
 * @param bs_info {Object}, It contains the start point information json object.
 * @param ss_info {Object}, It contains the end point information json object.
 * @param sector_name {String}, It contains the name of sector configured device.
 * @param ss_name {String}, It contains the name of sub-station.
 * @param bs_name {String}, It contains the name of base-station.
 * @param bs_id {Number}, It contains the id of connected base-station.
 * @param sector_id {Number}, It contains the id of connected sector.
 * @return {Object} pathConnector, It contains gmaps polyline object.
 */
WhiteMapClass.prototype.plotLines_wmap = function(startEndObj,linkColor,bs_info,ss_info,sect_height,sector_name,ss_name,bs_name,bs_id,sector_id) {

	if(isDebug) {
		console.log("Create Line Function");
		console.log("Create Line Start Time :- "+ new Date().toLocaleString());
	}

	var pathDataObject = new OpenLayers.Geometry.LineString([
		new OpenLayers.Geometry.Point(startEndObj.startLon, startEndObj.startLat),
		new OpenLayers.Geometry.Point(startEndObj.endLon, startEndObj.endLat)
	]);
	var linkObject = {},
		link_path_color = linkColor;

	var ss_info_obj = "",
		ss_height = 40;

	if(ss_info != undefined || ss_info == "") {
		ss_info_obj = ss_info.info;
		ss_height = ss_info.antenna_height && ss_info.antenna_height != 'NA' ? ss_info.antenna_height : 40;
	} else {
		ss_info_obj = "";
		ss_height = 40;
	}

	var bs_info_obj = "",
		bs_height = 40;
	if(bs_info != undefined || bs_info == "") {
		bs_info_obj = bs_info.info;
		bs_height = bs_info.antenna_height && bs_info.antenna_height != 'NA' ? bs_info.antenna_height : 40;
	} else {
		bs_info_obj = "";
		bs_height = 40;
	}

    if (sect_height == undefined || sect_height == ""){
        sect_height = 47;
    }

    linkObject = {
		path 			: pathDataObject,
		strokeColor		: link_path_color,
		strokeOpacity	: 1.0,
		strokeWeight	: 3,
		pointType 		: "path",
		geodesic		: true,
		ss_info			: ss_info_obj,
		ss_lat 			: startEndObj.endLat,
		ss_lon 			: startEndObj.endLon,
		bs_height 		: ss_height,
		bs_lat 			: startEndObj.startLat,
		bs_info 		: bs_info_obj,
		bs_lon 			: startEndObj.startLon,
		ss_height 		: sect_height,
		sector_lat 		: startEndObj.sectorLat,
		sector_lon 		: startEndObj.sectorLon,
		filter_data 	: {
			"bs_name" : bs_name,
			"sector_name" : sector_name,
			"ss_name" : ss_name,
			"bs_id" : bs_id,
			"sector_id" : sector_id,
			"ss_id": ss_info.ss_id ? ss_info.ss_id : ''
		},
		nearLat 		: startEndObj.nearEndLat,
		nearLon 		: startEndObj.nearEndLon,
		sectorName 	    : sector_name,
		ssName 		    : ss_name,
		bsName 			: bs_name,
		zIndex 			: 9999,
		type 			: "line",
		isActive 		: 1,
		layerReference  : ccpl_map.getLayersByName("Lines")[0]
	};

	var pathConnector = new OpenLayers.Feature.Vector(pathDataObject, {}, {
		strokeColor: link_path_color,
		strokeWeight: 3,
		strokeOpacity: 1.0
	});

	for(var keys in linkObject) {
		if(linkObject.hasOwnProperty(keys)) {
			pathConnector[keys] = linkObject[keys];
		}
	}

	markersMasterObj['Lines'][String(startEndObj.startLat)+ startEndObj.startLon+ startEndObj.endLat+ startEndObj.endLon]= pathConnector;
	markersMasterObj['LinesName'][String(bs_name)+ ss_name]= pathConnector;
	
	if(isDebug) {
		console.log("Create Line End Time :- "+ new Date().toLocaleString());
		console.log("*******************************************");

	}

	return pathConnector;
}

/**
 * This function plot the sector for given lat-lon points
 * @method plotSector_wmap.
 * @param Lat {Number}, It contains lattitude of the point on which sector is creater i.e. BS lat-lon.
 * @param Lng {Number}, It contains longitude of the point on which sector is creater i.e. BS lat-lon.
 * @param pointsArray [Array], It contains the points lat-lon object array.
 * @param sectorInfo {JSON Object Array}, It contains the information about the sector which are shown in info window.
 * @param bgColor {String}, It contains the RGBA format color code for sector.
 * @param sector_child [JSON object Array], It contains the connected SS data.
 * @param technology {String}, It contains the technology of sector device.
 * @param polarisation {String}, It contains the polarisation(horizontal or vertical) of sector device.
 */
// WhiteMapClass.prototype.plotSector_wmap = function(sectorPointsArray, additionalInfo) {
WhiteMapClass.prototype.plotSector_wmap = function(pointsArray, sectorInfo) {
	if(isDebug) {
		console.log("Plot Sector Polygon");
		console.log("Plot Sector Polygon Start Time :- "+ new Date().toLocaleString());
	}

	var polyPathArray = [],
		halfPt = Math.floor(pointsArray.length / (+2)),
		technology = sectorInfo.technology ? sectorInfo.technology : '',
		startLat = pointsArray[halfPt].lat,
		startLon = pointsArray[halfPt].lon;

	for(var i=pointsArray.length;i--;) {
		var pt = new OpenLayers.Geometry.Point(pointsArray[i].lon, pointsArray[i].lat);
		polyPathArray.push(pt);
	}

	var sColor = "#000000",
		sWidth = 1;

	if(technology.toLowerCase() == 'pmp') {
		sColor = '#FFFFFF';
		sWidth = 2;
	}

	var linearRing = new OpenLayers.Geometry.LinearRing(polyPathArray),
		sector = new OpenLayers.Geometry.Polygon([linearRing]),
		style = OpenLayers.Util.extend({}, OpenLayers.Feature.Vector.style['default']);

	style.strokeColor = sColor;
	style.fillColor = sectorInfo.bg_color;
	style.strokeOpacity = 1;
	style.fillOpacity = 0.5;
	style.strokeWidth = sWidth;

	var poly = new OpenLayers.Feature.Vector(sector, null, style);

	var polyInfo = sectorInfo;

	polyInfo['path'] = polyPathArray;
	polyInfo['startLat'] = startLat;
	polyInfo['startLon'] = startLon;
	polyInfo['child_ss'] = polyInfo.sector_child;
	polyInfo['original_sectors'] = polyInfo.sector_child;
	polyInfo['strokeColor'] = sColor;
	polyInfo['fillColor'] = sectorInfo.bg_color;
	polyInfo['strokeOpacity'] = 1;
	polyInfo['fillOpacity'] = 0.5;
	polyInfo['strokeWeight'] = sWidth;
	polyInfo['zIndex'] = 180;
	polyInfo['geodesic'] = true;
	polyInfo['isActive'] = 1;

    for(var keys in polyInfo) {
    	if(polyInfo.hasOwnProperty(keys)) {
    		poly[keys] = polyInfo[keys];
    	}
    }

    allMarkersObject_wmap['sector_polygon']['poly_'+sectorInfo.sectorName+"_"+sectorInfo.sector_id] = poly;

	if(polyInfo.sector_child) {
		for(var i=polyInfo.sector_child.length;i--;) {
			markersMasterObj['Poly'][polyInfo.sector_child[i]["device_name"]] = poly;
		}			
	}

	if(isDebug) {
		console.log("Plot Sector Polygon End Time :- "+ new Date().toLocaleString());
		console.log("***********************************");
	}

	ccpl_map.getLayersByName("Sectors")[0].addFeatures([poly]);

	return poly;
}

var infoWindow, lastFeature;
/*
This function closes Info Window if it is showing.
 */
WhiteMapClass.prototype.closeInfoWindow = function() {
	if(infoWindow) {
		infoWindow.hide();
		infoWindow.destroy();
		if(lastFeature) {
			lastFeature.popup = "";
		}
		infoWindow= "";
		return  true;
	}
	return false;
}
/*
This function open Info Window for the Marker.
@param e {Mouse Click Event} Event Info 
@param feature {Open Layer Marker Object} Marker on which Info Window is to be open
@param infoHTML {Object} Data to show on InfoWindow
 */
WhiteMapClass.prototype.openInfoWindow = function(feature, infoHTML) {
	
	// closeInfoWindow();

	//Create a OpenLayer Popup.
	var infoWindow = new OpenLayers.Popup(feature.name,
		new OpenLayers.LonLat(feature.ptLon, feature.ptLat),
		null,
		infoHTML,
		true);

	feature.popup = infoWindow;
	//Add popup to ccpl_map
	ccpl_map.addPopup(infoWindow);
	//Update Size for InfoWindow
	infoWindow.updateSize();
	//Show InfoWndow
	infoWindow.show();
	lastFeature = feature;

	return infoWindow;
}