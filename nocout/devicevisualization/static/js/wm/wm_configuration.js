var whiteMapSettings = {
	format: 'image/png',
	domElement: 'wmap_container',
	geoserver_url_India: "http://i.codescape.in:887/geoserver/wms",
	layer: "Test2:IND_adm1",
	initial_bounds: [68.498, 7.925, 97.335, 35.501],
	projection: "EPSG:4326",
	maxResolution: 0.11264453125,
	units: 'degrees',
	size: {
		medium: {width: 20, height: 40} 
	},
	devices_size: {
		medium: {width: 32, height: 37}
	},
	zoomLevelAfterLineAppears: 10,
	zoomLevelAtClusterUpdates: 10,
	latLngPrefixLabel: 'Longitude, Latitude: ',
	mapCenter: [82.9165, 21.713],
	zoomLevelAtWhichStateClusterExpands: 4,
	zoomLevelAtWhichPerformanceStarts: 7
}

var clustererSettings = {
	fontSize: 10,
	fontWeight: 'bold',
	fontColor: 'black',
	fontFamily: 'Arial,sans-serif',
	clustererDistance: 70,
	threshold: 3,
	thresholdAtHighZoomLevel: 7
}