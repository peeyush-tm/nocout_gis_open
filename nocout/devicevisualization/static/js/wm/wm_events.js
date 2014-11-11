/*Map Control Click*/
OpenLayers.Control.Click = OpenLayers.Class(OpenLayers.Control, {
    defaultHandlerOptions: {
        'single': true,
        'double': false,
        'pixelTolerance': 0,
        'stopSingle': false,
        'stopDouble': false
    },

    initialize: function(options) {
        this.handlerOptions = OpenLayers.Util.extend(
            {}, this.defaultHandlerOptions
            );
        OpenLayers.Control.prototype.initialize.apply(
            this, arguments
            );
        this.handler = new OpenLayers.Handler.Click(
            this, {
                'click': this.trigger
            }, this.handlerOptions
            );
    },

    trigger: function(e) {
    	whiteMapClass.unSpiderifyBsMarker();
        // console.log(e);
    }
});

/*
Event triggered for Map Idle Condition. [Whenever Map is Zoomed, Panned or something else]
 */
var isEventRepeated= true;
var lastZoomLevel = 1;
WhiteMapClass.prototype.mapIdleCondition = function() {
	isEventRepeated = true;
	/*
	This function shpws LineLayer
	@param display {boolean} Hide or show the layer
	 */
	function showLinesLayer(display) {
		$("#showConnLines").prop('checked', display);
		ccpl_map.getLayersByName("Lines")[0].setVisibility(display);
	}

	//do condition doesnt run when map is panned
	if(lastZoomLevel !== ccpl_map.getZoom()) {
		if((lastZoomLevel < whiteMapSettings.zoomLevelAfterLineAppears && ccpl_map.getZoom() >= whiteMapSettings.zoomLevelAfterLineAppears) || (lastZoomLevel >= whiteMapSettings.zoomLevelAfterLineAppears && ccpl_map.getZoom() < whiteMapSettings.zoomLevelAfterLineAppears)) {
			isEventRepeated = false;
		}

		//is event is not repeated
		if(!isEventRepeated) {
			//check if lines are to be toggled
			if(ccpl_map.getZoom() >= whiteMapSettings.zoomLevelAfterLineAppears) {
				showLinesLayer(true);
			} else {
				showLinesLayer(false);
			}

			if(ccpl_map.getZoom() >= whiteMapSettings.zoomLevelAtClusterUpdates) {
				ccpl_map.getLayersByName('Markers')[0].strategies[0].distance = 40;
				ccpl_map.getLayersByName('Markers')[0].strategies[0].threshold = 7;
			} else {
				ccpl_map.getLayersByName('Markers')[0].strategies[0].distance = 70;
				ccpl_map.getLayersByName('Markers')[0].strategies[0].threshold = "";
			}
			ccpl_map.getLayersByName('Markers')[0].strategies[0].recluster();

			// this.showFeatuesInCurrentBounds();
		}
		lastZoomLevel = ccpl_map.getZoom();		
	}

	//check if to use icons here or use stylemap

	// //gis performce calling
	// setTimeout(function() {
	// 	var bs_list = getMarkerInCurrentBound();
	// 	if(bs_list.length > 0 && isCallCompleted == 1) {
	// 		if(recallPerf != "") {
	// 			clearTimeout(recallPerf);
	// 			recallPerf = "";
	// 		}
	// 		// gisPerformanceClass.start(bs_list);
	// 	}
	// },1000);
};


/**
 * This function is triggered when Click on Layer Feature is done(Markers, Lines, Sectors). Zoom on cluster else open infowindow for it.
 * @param  {[type]} e [description]
 * @return {[type]}   [description]
 */
WhiteMapClass.prototype.layerFeatureClicked = function(e) {
	var feature = e.feature;

	/**
	 * This function shows create and display InfoWindow content for the feature.
	 * @param  {[OpenLayers Feature]} feature Feature on which Click was done
	 * @return {[type]}         ;
	 */
	function showInfoWindow(feature) {
		var infoWindowContent = gmap_self.makeWindowContent(feature);
		$("#infoWindowContainer").html(infoWindowContent);
		$("#infoWindowContainer").find('ul.list-unstyled.list-inline').remove();
		$("#infoWindowContainer").removeClass('hide');
	}

	if(feature) {
		//if cluster is present
		if(feature.cluster) {
			//if cluster of length gt 2 is there, expand the cluster
			if(feature.cluster.length >= 2) {
				var clusterPoints = [];
				for(var i = 0; i< feature.cluster.length; i++){
					clusterPoints.push(feature.cluster[i].geometry);
				}
				var lineString = new OpenLayers.Geometry.LineString(clusterPoints);
				ccpl_map.zoomToExtent(lineString.getBounds());
			//else get item at 0 index, show infowindow for it.
			} else {
				feature = feature.cluster[0].attributes;
				showInfoWindow(feature);
			}
		} else {
			//if path or sector is clicked
			if(feature.pointType === "path" || feature.pointType === "sector") {
				showInfoWindow(feature);
			//if bs or ss is clicked
			} else {
				if(feature.attributes.pointType === "base_station") {
					if(this.spiderifyMarker(feature)) {
						showInfoWindow(feature.attributes);		
					}
				} else {
					showInfoWindow(feature.attributes);
				}
			}
		}
	}
	return ;
}