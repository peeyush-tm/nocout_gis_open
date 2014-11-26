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
				})
				// new OpenLayers.Control.LayerSwitcher()
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

		layers.stateLabelLayer = new OpenLayers.Layer.Vector("States", {
                styleMap: new OpenLayers.StyleMap({'default':{
                	externalGraphic: base_url+"/static/js/OpenLayers/img/state_cluster.png",
                	graphicWidth: 50,
                	graphicHeight: 50,
                    label : "${count}",
                }})
            });

		ccpl_map.addLayer(layers.stateLabelLayer);

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
		layers.livePollFeatureLayer= new OpenLayers.Layer.Vector("Polling", {
			eventListeners: {
				"beforefeatureadded": function() {
					if(this.features.length) {
						this.destroyFeatures();						
					}
				}
			}
		});

		ccpl_map.addLayer(layers.livePollFeatureLayer);

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
	var feature= "", point = new OpenLayers.Geometry.Point(lon, lat);
	//If size and iconUrl is present, create Vector feature using those
	if(size && iconUrl) {
		feature = new OpenLayers.Feature.Vector(point, {}, {externalGraphic: iconUrl, graphicHeight: size.h, graphicWidth: size.w});
	} else {
		var feature = new OpenLayers.Feature.Vector(point, {});
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
	
	closeInfoWindow();

	//Create a OpenLayer Popup.
	infoWindow = new OpenLayers.Popup(feature.name,
		feature.lonlat,
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
		new OpenLayers.Geometry.Point(startEndObj.startLat,startEndObj.startLon),
		new OpenLayers.Geometry.Point(startEndObj.endLat,startEndObj.endLon)
	]);
	var linkObject = {},
		link_path_color = linkColor;

	var ss_info_obj = "",
		ss_height = 40;

	if(ss_info != undefined || ss_info == "") {
		ss_info_obj = ss_info.info;
		ss_height = ss_info.antenna_height;
	} else {
		ss_info_obj = "";
		ss_height = 40;
	}

	var bs_info_obj = "",
		bs_height = 40;
	if(bs_info != undefined || bs_info == "") {
		bs_info_obj = bs_info.info;
		bs_height = bs_info.antenna_height;
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
		filter_data 	: {"bs_name" : bs_name, "sector_name" : sector_name, "ss_name" : ss_name, "bs_id" : bs_id, "sector_id" : sector_id},
		nearLat 		: startEndObj.nearEndLat,
		nearLon 		: startEndObj.nearEndLon,
		sectorName 	    : sector_name,
		ssName 		    : ss_name,
		bsName 			: bs_name,
		zIndex 			: 9999,
		type: "line",
		layerReference: ccpl_map.getLayersByName("Lines")[0]
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

//-----------------------------------------------------------
var lastInfoOpen = null;
//Function to bind info window to a marker

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
WhiteMapClass.prototype.plotSector_wmap = function(lat,lon,pointsArray,sectorInfo,bgColor,sector_child,technology,polarisation,rad,azimuth,beam_width) {
	if(isDebug) {
		console.log("Plot Sector Polygon");
		console.log("Plot Sector Polygon Start Time :- "+ new Date().toLocaleString());
	}

	var polyPathArray = [];
	var halfPt = Math.floor(pointsArray.length / (+2));
	
	var startLat = pointsArray[halfPt].lat;
	var startLon = pointsArray[halfPt].lon;

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

	var linearRing = new OpenLayers.Geometry.LinearRing(pointsList);

	var sector = new OpenLayers.Geometry.Polygon([linearRing]);

	var style = OpenLayers.Util.extend({}, OpenLayers.Feature.Vector.style['default']);

	style.strokeColor = sColor;
	style.fillColor = bgColor;
	style.strokeOpacity = 1;
	style.fillOpacity = 0.5;
	style.strokeWidth = sWidth;

	var poly = new OpenLayers.Feature.Vector(sector, null, style);

	var polyInfo = {
		path 		     : polyPathArray,
		ptLat 		     : lat,
		ptLon 		     : lon,
		strokeColor      : sColor,
		fillColor 	     : bgColor,
		pointType	     : "sector",
		strokeOpacity    : 1,
		fillOpacity 	 : 0.5,
		strokeWeight     : sWidth,
		poll_info 		 : [],
		radius 			 : rad,
		azimuth 		 : azimuth,
		beam_width 		 : beam_width,
		technology 		 : sectorInfo.technology,
		vendor 			 : sectorInfo.vendor,
		deviceExtraInfo  : sectorInfo.info,
		deviceInfo 		 : sectorInfo.device_info,
		startLat 	     : startLat,
		startLon 	     : startLon,
		filter_data 	 : {"bs_name" : sectorInfo.bs_name, "sector_name" : sectorInfo.sector_name},
		bhInfo 			 : [],
		child_ss 	     : sector_child,
		polarisation 	 : polarisation,
		original_sectors : sector_child,
		zIndex 			 : 180,
		geodesic		 : true,
		isActive 		 : 1
    };

    for(var keys in polyInfo) {
    	if(polyInfo.hasOwnProperty(keys)) {
    		poly[keys] = polyInfo[keys];
    	}
    }

    // poly.setMap(mapInstance);
    allMarkersArray_wmap.push(poly);

    allMarkersObject_wmap['sector_polygon']['poly_'+sectorInfo.sector_name+"_"+sectorInfo.sector_id] = poly;

	if(sector_child) {
		for(var i=sector_child.length;i--;) {
			markersMasterObj['Poly'][sector_child[i]["device_name"]]= poly;
		}			
	}
    

	if(isDebug) {
		console.log("Plot Sector Polygon End Time :- "+ new Date().toLocaleString());
		console.log("***********************************");
	}

	ccpl_map.getLayersByName("Sectors")[0].addFeatures([poly]);

	return poly;
}

/**
 * This function checks if given feature lies in bound of polygon if polygon is provided else, in map bounds.
 * @param  {Object} point   Point which is to be check. It contains Lat Lng keys.
 * @param  {OpenLayer Polygon Feature} polygon Optional Param. If passed, check inside of polygon else use mapextend
 * @return {[type]}         [description]
 */
WhiteMapClass.prototype.checkIfPointLiesInside = function(point, polygon) {
	var mapBounds = []:
	//get map extent
	var mapBoundsArray = ccpl_map.getExtent().toArray();

	for(var i=0; i< mapBoundsArray.length; i++) {
		var pointObj= {};
		if(i=== 0) {
			pointObj.lat = mapBoundsArray[1];
			pointObj.lon = mapBoundsArray[0];
		} else if (i=== 1) {
			pointObj.lat = mapBoundsArray[3];
			pointObj.lon = mapBoundsArray[0];
		} else if (i=== 2) {
			pointObj.lat = mapBoundsArray[3];
			pointObj.lon = mapBoundsArray[2];
		} else {
			pointObj.lon = mapBoundsArray[2];
			pointObj.lat = mapBoundsArray[1];
		}
		mapBounds.push(pointObj);
	}
	//check if point lies inside extend
	if(isPointInPoly(mapBounds, point)) {
		//return true if it does
		return true;
	}
	//else return false
	return false;
}

/**
 * This function shows a Feature
 * @param  {OpenLayer Feature} feature Feature which is to be shown
 * @return {[type]}         [description]
 */
function showOpenLayerFeature(feature) {
	var markerLayer = feature.layerReference;
	feature.style.display = '';
	feature.map = 'current';
	markerLayer.redraw();
}

/**
 * This function hide a Feature
 * @param  {OpenLayer Feature} feature Feature which is to be shown
 * @return {[type]}         [description]
 */
function hideOpenLayerFeature(feature) {
	var markerLayer = feature.layerReference;
	feature.style.display = 'none';
	feature.map = '';
	markerLayer.redraw();
}