var whiteMapSettings = {
	domElement: 'wmap_container',
	/********************* Configuration for Localhost ***************************/
	// format: 'image/png',
	// geoserver_url_India: "http://i.codescape.in:887/geoserver/wms",
	// layer: "Test2:IND_adm1",
	// initial_bounds: [68.498, 7.925, 97.335, 35.501],
	/********************* END ***************************/
	/********************* Configuration for UAT(10.133.12.163) ***************************/
	format:'application/openlayers',
	geoserver_url_India: "http://10.133.12.163:5008/geoserver/cite/wms",
	layer: "cite:STATE",
	initial_bounds:[68.14339447036186,6.748584270488672,97.40963745103579,37.07349395945833],
	/********************* END ***************************/
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
	// mapCenter: [82.9165, 21.713],
	mapCenter: [79.0900, 21.1500],
	zoomLevelAtWhichStateClusterExpands: 4,
	zoomLevelAtWhichPerformanceStarts: 7
}

var clustererSettings = {
	fontSize: 10,
	fontWeight: 'bold',
	fontColor: 'black',
	fontFamily: 'Arial,sans-serif',
	clustererDistance: 100,
	threshold: 2,
	thresholdAtHighZoomLevel: 5
}