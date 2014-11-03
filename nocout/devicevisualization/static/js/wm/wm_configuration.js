var whiteMapSettings = {
	format: 'image/png',
	domElement: 'deviceMap',
	geoserver_url_India: "http://i.codescape.in:887/geoserver/wms",
	layer: "Test2:IND_adm1",
	initial_bounds: [68.498, 7.925, 97.335, 35.501],
	projection: "EPSG:4326",
	maxResolution: 0.11264453125,
	units: 'degrees',
	size: {
		medium: {width: 20, height: 40} 
	},
	zoomLevelAfterLineAppears: 6
}

var clustererSettings = {
	fontSize: 11,
	fontWeight: 'bold',
	fontColor: 'black',
	fontFamily: 'Arial,sans-serif',
	clustererDistance: 70
}