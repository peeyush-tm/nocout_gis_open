/*Global Variables*/
var mapInstance = "",
	that = "",
	currentDomElement = "",
	oms = "",
	pathConnector = "",
	infowindow = "",
	devicesObject = {},
	metaData = {},
	hitCounter = 1,
	showLimit = 0,
	devicesCount = 0,
	remainingDevices = 0,
	cityArray = [],
	stateArray = [],
	vendorArray = [],
	techArray = [],
	devices = [],
	masterMarkersObj = [],
	slaveMarkersObj = [],
	pathLineArray = [],
	counter = 0,
	totalCalls = 1,
	clusterIcon = "",
	masterClusterInstance = "",
	slaveClusterInstance = "",
	polygonSelectedDevices = [],
	pathArray = [],
	polygon = "",
	pointsArray = [],
	currentPolygon = {},
	drawingManager = "",
	dataArray = [],
	leftMargin = 0;

/**
 * This class is used to plot the BS & SS on the google maps & show information on click
 * @class networkMap
 * @uses jQuery
 * @uses Google Maps
 * Coded By :- Yogender Purohit
 */
function networkMapClass() {

	/*Store the reference of current pointer in a global variable*/
	that = this;

	/**
	 * This function creates the base google map with the lat long of India
	 * @function createMap
	 * @class networkMap
	 * @param domElement "String" It the the dom element on which the map is to be create
	 */
	this.createMap = function(domElement) {

		/*Store the reference of current pointer in a global variable*/
		that = this;

		/*Save the dom element in the global variable*/
		currentDomElement = domElement;

		var mapObject = {
			center    : new google.maps.LatLng(21.1500,79.0900),
			zoom      : 2
		};    
		/*Create Map Type Object*/
		mapInstance = new google.maps.Map(document.getElementById(domElement),mapObject);

		/*Create a instance of OverlappingMarkerSpiderfier*/
		oms = new OverlappingMarkerSpiderfier(mapInstance,{markersWontMove: true, markersWontHide: true});		

		/*Create a instance of google map info window*/
		infowindow = new google.maps.InfoWindow();		

		oms.addListener('click', function(marker,e) {
			
			var windowPosition = new google.maps.LatLng(marker.position.k,marker.position.A);
			/*Call the function to create info window content*/
			var content = that.makeWindowContent(marker,e);
			/*Set the content for infowindow*/
			infowindow.setContent(content);
			/*Set The Position for InfoWindow*/
			infowindow.setPosition(windowPosition);
			/*Open the info window*/
			infowindow.open(mapInstance);
		});
		/*Event when the markers cluster expands or spiderify*/
		oms.addListener('spiderfy', function(e,markers) {

			/*Change the markers icon from cluster icon to thrie own icon*/
			for(var i=0;i<e.length;i++) {
				e[i].setOptions({"icon":e[i].oldIcon});
			}

			infowindow.close();
		});
		/*Event when markers cluster is collapsed or unspiderify*/
		oms.addListener('unspiderfy', function(e,markers) {

			/*Reset the marker icon to cluster icon*/
			for(var i=0;i<e.length;i++) {
				e[i].setOptions({"icon":clusterIcon});
			}
		});
	};

	/**
	 * This function plots the BS & SS network on the created google map
	 * @function getDevicesData
	 * @class networkMap
	 */
	this.getDevicesData = function(hostIp,username) {

		/*Store the reference of current pointer in a global variable*/
		that = this;

		if(counter < totalCalls)
		{
			/*Show The loading Icon*/
			$("#loadingIcon").show();

			/*Disable the refresh button*/
			$("#resetFilters").button("loading");

			/*To Enable The Cross Domain Request*/
			$.support.cors = true;
			
			/*Ajax call to the API*/
			$.ajax({
				crossDomain: true,
				url : "//" + hostIp + "device/stats/?username="+username+"&page_number="+hitCounter+"&limit="+showLimit,
				// url : "http://127.0.0.1:8000/device/stats/?username="+username+"&page_number="+hitCounter+"&limit="+showLimit,
				type : "GET",
				dataType : "json",
				/*If data fetched successful*/
				success : function(result) {

					if(result.data.objects != null) {

						hitCounter = hitCounter + 1;
						/*First call case*/
						if(devicesObject.data == undefined) {

							/*Save the result json to the global variable for global access*/
							devicesObject = result;
							/**/
							devices = devicesObject.data.objects.children;
						} else {

							devices = devices.concat(result.data.objects.children);
						}


						/*Update the device count with the received data*/
						devicesCount = devicesObject.data.meta.total_count;

						/*Update the device count with the received data*/
						showLimit = devicesObject.data.meta.limit;

						if(remainingDevices == 0) {

							showLimit = devicesObject.data.meta.limit;
							remainingDevices = devicesCount - devicesObject.data.meta.limit;
						} else {

							remainingDevices = remainingDevices - devicesObject.data.meta.limit;
						}
						
						if(devicesObject.success == 1) {

							/*If cluster icon exist then save it to global variable else make the global variable blank*/
							if(devicesObject.data.objects.data.cluster_icon == undefined) {
								clusterIcon = "";	
							} else {
								clusterIcon = devicesObject.data.objects.data.cluster_icon;
							}

							/*Call the populateNetwork to show the markers on the map*/
							that.populateNetwork(devices);
							
							/*Call the getDevicesFilter function to seperate the filter values from the object array*/
							that.getDevicesFilter(devices);

						} else {

							that.recallServer();
						}
						/*Calculate the total number of pages from limit & total count*/
						totalCalls = Math.ceil(result.data.meta.total_count/result.data.meta.limit);
						/*Call the function after 3 sec.*/
						setTimeout(function() {
								
							that.getDevicesData(hostIp,username);
						},3000);
					} else {

						that.recallServer();
					}
				},
				/*If data not fetched*/
				error : function(err) {

					that.recallServer();
					console.log(err.statusText);
				}
			});
		} else {

			/*Recall the server after the defined time*/
			that.recallServer();
		}
		
		counter = counter + 1;
	};

	/**
     * This function is used to populate the markers on the google maps
     * @class netowrkMap
     * @method populateNetwork
     * @param resultantMarkers [JSON Objet Array] It is the devies object array
	 */
	this.populateNetwork = function(resultantMarkers) {

		/*Store the reference of current pointer in a global variable*/
		that = this;

		/*Assign the potting devices to the 'devices' global variables*/
		devices = resultantMarkers;

		for(var i=0;i<resultantMarkers.length;i++) {			

			var master_label_content = "<div class='labelContainer'><div class='topLabel'>Perf : "+resultantMarkers[i].data.perf+"</div><div class='bottomLabel'>Model : "+resultantMarkers[i].data.model+"</div></div>";
			/*Create Master Marker Object*/
			var masterMarkerObject = {
		    	position  	: new google.maps.LatLng(resultantMarkers[i].data.lat,resultantMarkers[i].data.lon),
		    	map       	: mapInstance,
		    	icon 	  	: resultantMarkers[i].data.markerUrl,//"https://chart.googleapis.com/chart?chst=d_map_pin_letter&chld=|fcfcfc|",
		    	oldIcon 	: resultantMarkers[i].data.markerUrl,
		    	title     	: resultantMarkers[i].data.alias,
		    	pointType	: "Master",
		    	pointPerf	: resultantMarkers[i].data.perf,
		    	vendor 		: resultantMarkers[i].data.vendor,
		    	technology	: resultantMarkers[i].data.technology,
		    	model 		: resultantMarkers[i].data.model,
		    	city 		: resultantMarkers[i].data.city,
		    	state 		: resultantMarkers[i].data.state,
		    	pointName   : resultantMarkers[i].name,
		    	pointAlias  : resultantMarkers[i].data.alias,
		    	deviceType  : resultantMarkers[i].data.decive_type,
		    	currentState: resultantMarkers[i].data.current_state,
		    	pointIp  	: resultantMarkers[i].data.ip,
		    	pointMac  	: resultantMarkers[i].data.mac,
		    	pointDetail : resultantMarkers[i].data.otherDetail,
		    	labelContent: master_label_content,
				labelAnchor : new google.maps.Point(0, 62),
				labelClass  : "markerLabels",
				labelStyle	: {opacity: 0.85}
			};
			/*Create Master Marker*/
		    // var masterMarker = new google.maps.Marker(masterMarkerObject);
		    var masterMarker = new MarkerWithLabel(masterMarkerObject);
		    /*Add the master marker to the global master markers array*/
		    masterMarkersObj.push(masterMarker);
		    /*Add parent markers to the OverlappingMarkerSpiderfier*/
		    oms.addMarker(masterMarker);
	    	
		    var slaveCount = resultantMarkers[i].children.length;  
		    /*Loop for the number of slave & their links with the master*/
		    for(var j=0;j<slaveCount;j++) {
		    	
		    	var slave_label_content = "<div class='labelContainer'><div class='topLabel'>Perf : "+resultantMarkers[i].children[j].data.perf+"</div><div class='bottomLabel'>Model : "+resultantMarkers[i].children[j].data.model+"</div></div>";
		    	/*Create Slave Marker Object*/
			    var slaveMarkerObject = {
			    	position  	: new google.maps.LatLng(resultantMarkers[i].children[j].data.lat,resultantMarkers[i].children[j].data.lon),
			    	map       	: mapInstance,
			    	icon 	  	: resultantMarkers[i].children[j].data.markerUrl,
			    	oldIcon 	: resultantMarkers[i].children[j].data.markerUrl,
			    	title     	: resultantMarkers[i].children[j].data.alias,
			    	pointType	: "Slave",
			    	pointPerf	: resultantMarkers[i].children[j].data.perf,
			    	vendor 		: resultantMarkers[i].children[j].data.vendor,
			    	technology	: resultantMarkers[i].children[j].data.technology,
			    	model 		: resultantMarkers[i].children[j].data.model,
			    	city 		: resultantMarkers[i].children[j].data.city,
			    	state 		: resultantMarkers[i].children[j].data.state,
			    	pointName   : resultantMarkers[i].children[j].name,
			    	pointAlias  : resultantMarkers[i].children[j].data.alias,
			    	deviceType  : resultantMarkers[i].children[j].data.device_type,
			    	currentState: resultantMarkers[i].children[j].data.current_state,
			    	pointIp  	: resultantMarkers[i].children[j].data.ip,
			    	pointMac  	: resultantMarkers[i].children[j].data.mac,
			    	pointDetail : resultantMarkers[i].children[j].data.otherDetail,
			    	labelContent: slave_label_content,
					labelAnchor : new google.maps.Point(0, 62),
					labelClass  : "markerLabels",
					labelStyle	: {opacity: 0.85}
				};
				/*Create Slave Marker*/
			    // var slaveMarker = new google.maps.Marker(slaveMarkerObject);
			    var slaveMarker = new MarkerWithLabel(slaveMarkerObject);
			    /*Add the slave marker to the global slave array*/
		    	slaveMarkersObj.push(slaveMarker);
			    /*Add child markers to the OverlappingMarkerSpiderfier*/
				oms.addMarker(slaveMarker);

				if(resultantMarkers[i].data.showLink != 1) {

					/*Create object for Link Line Between Master & Slave*/
					var pathDataObject = [
						new google.maps.LatLng(resultantMarkers[i].data.lat,resultantMarkers[i].data.lon),
						new google.maps.LatLng(resultantMarkers[i].children[j].data.lat,resultantMarkers[i].children[j].data.lon)
					];					

					pathConnector = new google.maps.Polyline({

						path 				: pathDataObject,						
						strokeColor			: resultantMarkers[i].children[j].data.linkColor,
						strokeOpacity		: 1.0,
						strokeWeight		: 2,
						pointType 			: "path",
						/*Master Information*/
						masterLat 			: resultantMarkers[i].data.lat,
						masterLong 			: resultantMarkers[i].data.lon,
						masterPerf 			: resultantMarkers[i].data.perf,
						masterVendor 		: resultantMarkers[i].data.vendor,
				    	masterTechnology	: resultantMarkers[i].data.technology,
				    	masterModel 		: resultantMarkers[i].data.model,
						masterName  		: resultantMarkers[i].name,
						masterAlias  		: resultantMarkers[i].data.alias,
						masterCity  		: resultantMarkers[i].data.city,
						masterState  		: resultantMarkers[i].data.state,
				    	masterDeviceType	: resultantMarkers[i].data.device_type,
				    	masterCurrentState  : resultantMarkers[i].data.current_state,
				    	masterIp  			: resultantMarkers[i].data.ip,
				    	masterMac  			: resultantMarkers[i].data.mac,
				    	masterDetail  		: resultantMarkers[i].data.otherDetail,
				    	/*Slave Information*/
						slaveLat 			: resultantMarkers[i].children[j].data.lat,
						slaveLong 			: resultantMarkers[i].children[j].data.lon,
						slavePerf 			: resultantMarkers[i].children[j].data.perf,
						slaveVendor 		: resultantMarkers[i].children[j].data.vendor,
				    	slaveTechnology		: resultantMarkers[i].children[j].data.technology,
				    	slaveModel 			: resultantMarkers[i].children[j].data.model,
						slaveName  			: resultantMarkers[i].children[j].name,
						slaveAlias  		: resultantMarkers[i].children[j].data.alias,
						slaveCity  			: resultantMarkers[i].children[j].data.city,
						slaveState  		: resultantMarkers[i].children[j].data.state,
				    	slaveDeviceType 	: resultantMarkers[i].children[j].data.device_type,
				    	slaveCurrentState  	: resultantMarkers[i].children[j].data.current_state,
				    	slaveIp  			: resultantMarkers[i].children[j].data.ip,
				    	slaveMac  			: resultantMarkers[i].children[j].data.mac,
				    	slaveDetail  		: resultantMarkers[i].children[j].data.otherDetail,
				    	/*Geodesic*/
				    	geodesic			: true
					});
					/*Plot the link line between master & slave*/
					pathConnector.setMap(mapInstance);

					pathLineArray.push(pathConnector);

					/*Bind Click Event on Link Path Between Master & Slave*/
					google.maps.event.addListener(pathConnector, 'click', function(e) {
						
						/*Call the function to create info window content*/
						var content = that.makeWindowContent(this,e);
						/*Set the content for infowindow*/
						infowindow.setContent(content);
						/*Set The Position for InfoWindow*/
						infowindow.setPosition(e.latLng);
						/*Open the info window*/
						infowindow.open(mapInstance);
					});					
				}
			}
		}
		
		/*Loop to change the icon for same location markers(to cluster icon)*/
		for(var k=0;k<masterMarkersObj.length;k++) {
			for(var l=0;l<slaveMarkersObj.length;l++) {
				if(masterMarkersObj[k].position.A == slaveMarkersObj[l].position.A && masterMarkersObj[k].position.k == slaveMarkersObj[l].position.k) {
					/*Set the master marker icon to cluster icon*/
					masterMarkersObj[k].setOptions({"icon" : clusterIcon});
					/*Set the slave marker icon to cluster icon*/
					slaveMarkersObj[l].setOptions({"icon" : clusterIcon});
				}
			}
		}

		/*Cluster options object*/
		var clusterOptions = {gridSize: 70, maxZoom: 8};
		/*Add the master markers to the cluster MarkerCluster object*/
		masterClusterInstance = new MarkerClusterer(mapInstance, masterMarkersObj, clusterOptions);
		/*Add the slave markers to the cluster MarkerCluster object*/
		slaveClusterInstance = new MarkerClusterer(mapInstance, slaveMarkersObj, clusterOptions);
	};

	/**
	 * This function creates the info window content for BS,SS & link path 
	 * @class networkMap
	 * @method makeWindowContent
	 * @param contentObject {JSON Object} It contains the current pointer(this) information
	 * @return windowContent "String" It contains the content to be shown on info window
	 */
	this.makeWindowContent = function(contentObject,event) {

		/*Store the reference of current pointer in a global variable*/
		that = this;

		var windowContent = "",
			infoTable =  "",
			perfContent = "",
			clickedType = $.trim(contentObject.pointType);

		/*True,if clicked on the link line*/
		if(clickedType == "path") {

			var pathPositions = pathConnector.getPath().j;

			perfContent = "";
			infoTable = "";

			infoTable += "<table class='table table-bordered'><thead><th>Master Info</th><th>Master Perf</th><th>Slave Info</th><th>Slave Perf</th></thead><tbody>";
			infoTable += "<tr>";
			/*Master Info Start*/
			infoTable += "<td>";	
			infoTable += "<table class='table table-hover innerTable'><tbody>";
			infoTable += "<tr><td>Alias Name</td><td>"+contentObject.masterAlias+"</td></tr>";
			infoTable += "<tr><td>Current State</td><td>"+contentObject.masterCurrentState+"</td></tr>";
			infoTable += "<tr><td>Model</td><td>"+contentObject.masterModel+"</td></tr>";
			infoTable += "<tr><td>Vendor</td><td>"+contentObject.masterVendor+"</td></tr>";
			infoTable += "<tr><td>Technology</td><td>"+contentObject.masterTechnology+"</td></tr>";			
			infoTable += "<tr><td>IP Address</td><td>"+contentObject.masterIp+"</td></tr>";
			infoTable += "<tr><td>MAC Address</td><td>"+contentObject.masterMac+"</td></tr>";
			infoTable += "<tr><td>Device Type</td><td>"+contentObject.masterDeviceType+"</td></tr>";
			infoTable += "<tr><td>State</td><td>"+contentObject.masterState+"</td></tr>";
			infoTable += "<tr><td>City</td><td>"+contentObject.masterCity+"</td></tr>";
			infoTable += "<tr><td>Lat, Long</td><td>"+contentObject.masterLat+", "+contentObject.masterLong+"</td></tr>";
			infoTable += "</tbody></table>";			
			infoTable += "</td>";
			/*Master Info End*/
			/*Master Performance Start*/
			infoTable += "<td style='vertical-align:middle;text-align: center;'><h1><i class='fa fa-signal'></i>  "+contentObject.masterPerf+"</h1></td>";
			/*Master Performance End*/
			/*Slave Info Start*/
			infoTable += "<td>";			
			infoTable += "<table class='table table-hover innerTable'><tbody>";
			infoTable += "<tr><td>Alias Name</td><td>"+contentObject.slaveAlias+"</td></tr>";
			infoTable += "<tr><td>Current State</td><td>"+contentObject.slaveCurrentState+"</td></tr>";
			infoTable += "<tr><td>Model</td><td>"+contentObject.slaveModel+"</td></tr>";
			infoTable += "<tr><td>Vendor</td><td>"+contentObject.slaveVendor+"</td></tr>";
			infoTable += "<tr><td>Technology</td><td>"+contentObject.slaveTechnology+"</td></tr>";			
			infoTable += "<tr><td>IP Address</td><td>"+contentObject.slaveIp+"</td></tr>";
			infoTable += "<tr><td>MAC Address</td><td>"+contentObject.slaveMac+"</td></tr>";
			infoTable += "<tr><td>Device Type</td><td>"+contentObject.slaveDeviceType+"</td></tr>";
			infoTable += "<tr><td>State</td><td>"+contentObject.slaveState+"</td></tr>";
			infoTable += "<tr><td>City</td><td>"+contentObject.slaveCity+"</td></tr>";
			infoTable += "<tr><td>Lat, Long</td><td>"+contentObject.slaveLat+", "+contentObject.slaveLong+"</td></tr>";
			infoTable += "</tbody></table>";		
			infoTable += "</td>";
			/*Slave Info End*/
			/*Slave Performance Start*/
			infoTable += "<td style='vertical-align:middle;text-align: center;'><h1><i class='fa fa-signal'></i>  "+contentObject.slavePerf+"</h1></td>";
			/*Slave Performance End*/
			infoTable += "</tr>";
			infoTable += "</tbody></table>";
			/*Final infowindow content string*/
			windowContent += "<div class='windowContainer'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>  Master-Slave Link</h4></div><div class='box-body'><div>"+infoTable+"</div><div class='clear'></div></div></div></div>";
		} else {

			perfContent = "";
			infoTable = "";

			infoTable += "<table class='table table-bordered'><tbody>";
			infoTable += "<tr><td>Alias Name</td><td>"+contentObject.pointAlias+"</td></tr>";
			infoTable += "<tr><td>Current State</td><td>"+contentObject.currentState+"</td></tr>";
			infoTable += "<tr><td>Model</td><td>"+contentObject.model+"</td></tr>";
			infoTable += "<tr><td>Vendor</td><td>"+contentObject.vendor+"</td></tr>";
			infoTable += "<tr><td>Technology</td><td>"+contentObject.technology+"</td></tr>";			
			infoTable += "<tr><td>IP Address</td><td>"+contentObject.pointIp+"</td></tr>";
			infoTable += "<tr><td>MAC Address</td><td>"+contentObject.pointMac+"</td></tr>";
			infoTable += "<tr><td>Device Type</td><td>"+contentObject.deviceType+"</td></tr>";
			infoTable += "<tr><td>State</td><td>"+contentObject.state+"</td></tr>";
			infoTable += "<tr><td>City</td><td>"+contentObject.city+"</td></tr>";
			infoTable += "<tr><td>Lat, Long</td><td>"+contentObject.position.k+", "+contentObject.position.A+"</td></tr>";
			infoTable += "</tbody></table>";

			perfContent += "<h1><i class='fa fa-signal'></i>  "+contentObject.pointPerf+"</h1>";
			/*Final infowindow content string*/
			windowContent += "<div class='windowContainer'><div class='box border'><div class='box-title'><h4><i class='fa fa-map-marker'></i>  "+contentObject.pointType+"</h4></div><div class='box-body'><div class='windowInfo'>"+infoTable+"</div><div class='perf'>"+perfContent+"</div><div class='clear'></div></div></div></div>";
		}
		/*Return the info window content*/
		return windowContent;
	};

	/**
	 * This function is used to populate the filers(City & State) dropdown with the available data
	 * @class networkMap
	 * @method populateFilters
	 * @params cityArray [String Array] Contains the available city list
	 * @params stateArray [String Array] Contains the available state list
	 * @params vendorArray [String Array] Contains the available vendor list
	 * @params technologyArray [String Array] Contains the available technology list
	 */
	this.populateFilters = function(cityArray,stateArray,vendorArray,technologyArray) {
		
		/*Store the reference of current pointer in a global variable*/
		that = this;

		var stateOptions = "<option value=''>Select State</option>",
	 		cityOptions = "<option value=''>Select City</option>",
	 		vendorOptions = "<option value=''>Select Vendor</option>",
	 		technologyOptions = "<option value=''>Select Technology</option>";


 		/*Loop for the state array*/
	 	for(var i=0;i<stateArray.length;i++) {

	 		stateOptions += '<option value="'+stateArray[i]+'">'+stateArray[i]+'</option>';
	 	}

	 	/*Loop for the city array*/
	 	for(var j=0;j<cityArray.length;j++) {

	 		cityOptions += '<option value="'+cityArray[j]+'">'+cityArray[j]+'</option>';
	 	}

	 	/*Loop for the vendor array*/
	 	for(var k=0;k<vendorArray.length;k++) {

	 		vendorOptions += '<option value="'+vendorArray[k]+'">'+vendorArray[k]+'</option>';
	 	}	 	

	 	/*Loop for the technology array*/
	 	for(var l=0;l<technologyArray.length;l++) {

	 		technologyOptions += '<option value="'+technologyArray[l]+'">'+technologyArray[l]+'</option>';
	 	}

	 	/*Append the option string to the state dropdown*/
	 	$("#state").html(stateOptions);
	 	/*Append the option string to the city dropdown*/
	 	$("#city").html(cityOptions);
	 	/*Append the option string to the vendor dropdown*/
	 	$("#vendor").html(vendorOptions);
	 	/*Append the option string to the technology dropdown*/
	 	$("#technology").html(technologyOptions);
	};

	/**
	 * This function filters the markers for the given filters
	 * @class networkMap
	 * @method applyFilter
	 * @param filtersArray [JSON Array] It is an object array of filters with keys
	 */
	this.applyFilter = function(filtersArray) {

		/*Store the reference of current pointer in a global variable*/
		that = this;

		var filterKey = [],
			filteredData = [],
			masterIds = [],
			slaveIds = [];

		/*Fetch the keys from the filter array*/
		$.each(filtersArray, function(key, value) {

		    filterKey.push(key);
		});
		
	 	if(devices.length > 0) {

	 		filteredData = [];
	 		for(var i=0;i<devices.length;i++) {

	 			/*Total Slaves Count*/
	 			var slaveLength = devices[i].children.length;
	 			/*Loop For Slaves*/
	 			for(var j=0;j<slaveLength;j++) {

	 				var master = devices[i];
		 			var slave = devices[i].children[j];
		 				
		 			/*Conditions as per the number of filters*/
		 			if(filterKey.length == 1) {

	 					if(master.data[filterKey[0]] == filtersArray[filterKey[0]] || slave.data[filterKey[0]] == filtersArray[filterKey[0]]) {

		 					/*Check For The Duplicacy*/
		 					if(masterIds.indexOf(master.id) == -1 && slaveIds.indexOf(slave.id) == -1) {

		 						/*Save the master & slave ids to array to remove duplicacy*/
		 						masterIds.push(master.id);
		 						slaveIds.push(slave.id);

		 						filteredData.push(devices[i]);
		 					}
		 				}

		 			} else if(filterKey.length == 2) {

	 					if((master.data[filterKey[0]] == filtersArray[filterKey[0]] || slave.data[filterKey[0]] == filtersArray[filterKey[0]]) && (master.data[filterKey[1]] == filtersArray[filterKey[1]] || slave.data[filterKey[1]] == filtersArray[filterKey[1]])) {

		 					/*Check For The Duplicacy*/
		 					if(masterIds.indexOf(master.id) == -1 && slaveIds.indexOf(slave.id) == -1) {

		 						/*Save the master & slave ids to array to remove duplicacy*/
		 						masterIds.push(master.id);
		 						slaveIds.push(slave.id);

		 						filteredData.push(devices[i]);
		 					}
		 				}
		 			} else if(filterKey.length == 3) {

		 				if((master.data[filterKey[0]] == filtersArray[filterKey[0]] || slave.data[filterKey[0]] == filtersArray[filterKey[0]]) && (master.data[filterKey[1]] == filtersArray[filterKey[1]] || slave.data[filterKey[1]] == filtersArray[filterKey[1]]) && (master.data[filterKey[2]] == filtersArray[filterKey[2]] || slave.data[filterKey[2]] == filtersArray[filterKey[2]])) {

		 					/*Check For The Duplicacy*/
		 					if(masterIds.indexOf(master.id) == -1 && slaveIds.indexOf(slave.id) == -1) {

		 						/*Save the master & slave ids to array to remove duplicacy*/
		 						masterIds.push(master.id);
		 						slaveIds.push(slave.id);

		 						filteredData.push(devices[i]);
		 					}
		 				}
		 			} else if(filterKey.length == 4) {

		 				if((master.data[filterKey[0]] == filtersArray[filterKey[0]] || slave.data[filterKey[0]] == filtersArray[filterKey[0]]) && (master.data[filterKey[1]] == filtersArray[filterKey[1]] || slave.data[filterKey[1]] == filtersArray[filterKey[1]]) && (master.data[filterKey[2]] == filtersArray[filterKey[2]] || slave.data[filterKey[2]] == filtersArray[filterKey[2]]) && (master.data[filterKey[3]] == filtersArray[filterKey[3]] || slave.data[filterKey[3]] == filtersArray[filterKey[3]])) {

		 					/*Check For The Duplicacy*/
		 					if(masterIds.indexOf(master.id) == -1 && slaveIds.indexOf(slave.id) == -1) {

		 						/*Save the master & slave ids to array to remove duplicacy*/
		 						masterIds.push(master.id);
		 						slaveIds.push(slave.id);

		 						filteredData.push(devices[i]);
		 					}
		 				}
		 			}
	 			}
	 		}
	 		/*Check that after applying filters any data exist or not*/
	 		if(filteredData.length === 0) {

	 			bootbox.alert("User Don't Have Any Devies For Selected Filters");

	 		} else {

				/*Reset the markers, polyline & filters*/
	 			that.clearMapElements();

				masterMarkersObj = [];
				slaveMarkersObj = [];

				/*Populate the map with the filtered markers*/
	 			that.populateNetwork(filteredData);
	 		}	 		
	 	}	
	};

	/**
	 * This function calls the populateNetwork function to load the fetched devices in case of no filters
	 * @class devicePlottingLib
	 * @method loadExistingDevices
	 */
	this.loadExistingDevices = function() {

		/*Store the reference of current pointer in a global variable*/
		that = this;

		that.populateNetwork(devices);
	};

	/**
     * This function makes an array from the selected filters
     * @function makeFiltersArray
     * @return selectedArray [JSON Array] It is an object array of the selected filters with the keys
     */
    this.makeFiltersArray = function() {

    	/*Store the reference of current pointer in a global variable*/
		that = this;

        var selectedTechnology = $("#technology").val(),
            selectedvendor = $("#vendor").val(),
            selectedState = $("#state").val(),
            selectedCity = $("#city").val(),
            selectedArray = {};

        if(selectedTechnology != "") {

            selectedArray["technology"] = selectedTechnology;
        }

        if(selectedvendor != "") {

            selectedArray["vendor"] = selectedvendor;
        }

        if(selectedState != "") {

            selectedArray["state"] = selectedState;
        }

        if(selectedCity != "") {

            selectedArray["city"] = selectedCity;
        }
        /*Get The Length Of Filter Array*/
        var filtersLength = Object.keys(selectedArray).length;

        /*If any filter is applied then filter the data*/
        if(filtersLength > 0) {

            that.applyFilter(selectedArray);
        }
        /*If no filter is applied the load all the devices*/
        else {

            that.loadExistingDevices();
        }
    };
		
	/**
	 * This function get the filters values from divices array object & then call other function to populate the filters dropdown
	 * @class devicePlottingLib
	 * @method getDevicesFilter
	 * @param devices [Object Array] It is the fetched devices array object
	 */
	this.getDevicesFilter = function(devices) {

		/*Store the reference of current pointer in a global variable*/
		that = this;

		/*Make an array of master & slave cities as well as states*/
		for(var i=0;i<devices.length;i++) {

			/*Total number of slave for particular master*/
			var slaveCount = devices[i].children.length;

			/*Loop for the slaves*/
			for(var j=0;j<slaveCount;j++) {

				/*Push master city in cityArray array*/
				if(cityArray.indexOf($.trim(devices[i].data.city)) == -1) {

					cityArray.push($.trim(devices[i].data.city));
				}
				/*Push slave city in cityArray array*/
				if(cityArray.indexOf($.trim(devices[i].children[j].data.city)) == -1) {

					cityArray.push($.trim(devices[i].children[j].data.city));
				}

				/*Push master states in stateArray array*/
				if(stateArray.indexOf($.trim(devices[i].data.state)) == -1) {

					stateArray.push($.trim(devices[i].data.state));
				}
				/*Push slave states in stateArray array*/
				if(stateArray.indexOf($.trim(devices[i].children[j].data.state)) == -1) {

					stateArray.push($.trim(devices[i].children[j].data.state));
				}

				/*Push master vendors in masterVendorArray array*/
				if(vendorArray.indexOf($.trim(devices[i].data.vendor)) == -1) {

					vendorArray.push($.trim(devices[i].data.vendor));
				}
				/*Push slave vendors in slaveVendorArray array*/
				if(vendorArray.indexOf($.trim(devices[i].children[j].data.vendor)) == -1) {

					vendorArray.push($.trim(devices[i].children[j].data.vendor));
				}

				/*Push master technology in techArray array*/
				if(techArray.indexOf($.trim(devices[i].data.technology)) == -1) {

					techArray.push($.trim(devices[i].data.technology));
				}
				/*Push slave technology in techArray array*/
				if(techArray.indexOf($.trim(devices[i].children[j].data.technology)) == -1) {

					techArray.push($.trim(devices[i].children[j].data.technology));
				}
			}
		}
		
		/*Populate the city & state dropdown filters*/
		that.populateFilters(cityArray,stateArray,vendorArray,techArray);
	};

	/**
	 * This function creates enable the polygon drawing tool & draw the polygon
	 * @class devicePlottingLib
	 * @method createPolygon
	 */

	this.createPolygon = function() {

		/*Store the reference of current pointer in a global variable*/
    	that = this;
    	
    	selectedCount = polygonSelectedDevices.length;

    	if(selectedCount == 0) {

    		drawingManager = new google.maps.drawing.DrawingManager({
				drawingMode: google.maps.drawing.OverlayType.POLYGON,
				drawingControl: false,
				drawingControlOptions: {
					position: google.maps.ControlPosition.TOP_CENTER,
					drawingModes: [
						google.maps.drawing.OverlayType.POLYGON,
					]
				},
				map : mapInstance
			});
			
			drawingManager.setMap(mapInstance);

			google.maps.event.addListener(drawingManager, 'overlaycomplete', function(e) {

				pathArray = e.overlay.getPath().getArray();
				polygon = new google.maps.Polygon({"path" : pathArray});
				pointsArray = masterMarkersObj.concat(slaveMarkersObj);
				currentPolygon = e.overlay;
				currentPolygon.type = e.type;
				
				for(var k=0;k<pointsArray.length;k++) {
					
					var point = pointsArray[k].position;

					if (google.maps.geometry.poly.containsLocation(point, polygon)) {
						polygonSelectedDevices.push(pointsArray[k]);
					}
				}
				selectedCount = polygonSelectedDevices.length;
				if(selectedCount == 0) {
					
					bootbox.alert("No devices are under the selected area.Please re-select");
					/*Remove current polygon from map*/
					that.clearPolygon();

				} else if(selectedCount > 200) {
					
					bootbox.alert("Max. limit for selecting devices is 200.Please re-select");
					/*Remove current polygon from map*/
					that.clearPolygon();

				} else {

					var devicesTemplate = "";
					
					devicesTemplate = "<div class='deviceWellContainer'>";
					for(var i=0;i<selectedCount;i++) {

						devicesTemplate += '<div class="well well-sm"><h5>'+polygonSelectedDevices[i].title+'('+polygonSelectedDevices[i].pointIp+')</h5><ul class="list-unstyled list-inline">';
						devicesTemplate += '<li><button id="play_'+i+'" onClick="that.startMonitoring('+i+')" class="btn btn-default btn-xs"><i class="fa fa-play"></i></button></li>';
						devicesTemplate += '<li><button id="pause_'+i+'" onClick="that.pauseMonitoring('+i+')" class="btn btn-default btn-xs"><i class="fa fa-pause"></i></button></li>';
						devicesTemplate += '<li><button id="stop_'+i+'" onClick="that.stopMonitoring('+i+')" class="btn btn-default btn-xs"><i class="fa fa-stop"></i></button></li>';
						devicesTemplate += '</ul><div class="sparklineContainer"><span class="sparkline" id="sparkline_'+i+'">Loading...</span></div></div>';
					}
					devicesTemplate += "</div>";

					$("#sideInfo > .panel-body").html(devicesTemplate);					

					if($("#sideInfoContainer").hasClass("hide")) {
						$("#sideInfoContainer").removeClass("hide");
					}
					if(!$("#createPolygonBtn").hasClass("hide")) {
						$("#createPolygonBtn").addClass("hide");
					}

					if($("#clearPolygonBtn").hasClass("hide")) {
						$("#clearPolygonBtn").removeClass("hide");
					}

					drawingManager.setDrawingMode(null);
				}

				$("#createPolygonBtn").button("complete");
				$("#advFilterBtn").button("complete");
				$("#resetFilters").button("complete");
			});
    	} else {

    		bootbox.alert("Please clear the current selection.");
    		$("#clearPolygonBtn").removeClass("hide");
    		$("#createPolygonBtn").button("complete");
			$("#advFilterBtn").button("complete");
			$("#resetFilters").button("complete");
    	}
	};

	/**
	 * This function clear the polygon selection from the map
	 * @class devicePlottingLib
	 * @method clearPolygon
	 */
	this.clearPolygon = function() {

		/*Update the html of accordian body*/
		$("#sideInfo > .panel-body").html("No device selected.");
		/*Collapse the selected devices accordian*/
		if(!$("#sideInfoContainer").hasClass("hide")) {
			$("#sideInfoContainer").addClass("hide");
		}		
		/*Show Select Devices button*/
		if($("#createPolygonBtn").hasClass("hide")) {
			$("#createPolygonBtn").removeClass("hide");
		}
		/*Hide the clear selection button*/
		if(!$("#clearPolygonBtn").hasClass("hide")) {
			$("#clearPolygonBtn").addClass("hide");
		}
		/*Remove the current polygon from the map*/
		currentPolygon.setMap(null);
		/*Reset the variables*/
		polygonSelectedDevices = [];		
		pathArray = [];
		polygon = "";
		pointsArray = [];
		// currentPolygon = {};
	};

	/**
	 * This function creates the line chart for the monitoring of selected devices
	 * @class devicePlottingLib
	 * @method makeMonitoringChart
	 * @param id 'Integer'
	 */
	this.makeMonitoringChart = function(id) {

		var startClassNames = $("#play_"+id)[0].className;
		var stopClassNames = $("#stop_"+id)[0].className;

		if(startClassNames.indexOf("active") != -1) {
			
			var num = Math.floor((Math.random() * 20) + 1)
			var oldLength = dataArray.length;
			for(var i=0;i<num;i++) {

				dataArray.push(Math.floor(Math.random() * 80));
			}

			var margin = oldLength * 5;
			
			$("#sparkline_"+id).sparkline(dataArray, {
		        type: "line",
		        lineColor: "blue",
		        spotColor : "orange",
		        defaultPixelsPerValue : 5
		    });

		    setTimeout(function() {
				$("#sparkline_"+id).css("margin-left","-"+leftMargin+"px");
				/*Decrement the margin-left value*/
				leftMargin = margin;
				/*Recursive calling*/
				that.makeMonitoringChart(id);
			},1500);

		} else if(stopClassNames.indexOf("active") != -1) {

				$("#sparkline_"+id).sparkline("", {
			        type: "line",
			        lineColor: "blue",
			        spotColor : "orange",
			        zeroAxis: false
			    });
		}
	};

	this.startMonitoring = function(id) {

		$("#play_"+id).addClass("active");
        if($("#pause_"+id).hasClass("active")) {
            $("#pause_"+id).removeClass("active");
        }
        if($("#stop_"+id).hasClass("active")) {
            $("#stop_"+id).removeClass("active");
        }

        that.makeMonitoringChart(id);
	};

	this.pauseMonitoring = function(id) {
		
		$("#pause_"+id).addClass("active");
        if($("#play_"+id).hasClass("active")) {
            $("#play_"+id).removeClass("active");
        }
        if($("#stop_"+id).hasClass("active")) {
            $("#stop_"+id).removeClass("active");
        }
        that.makeMonitoringChart(id);
	};

	this.stopMonitoring = function(id) {
		
		$("#stop_"+id).addClass("active");
        if($("#play_"+id).hasClass("active")) {
            $("#play_"+id).removeClass("active");
        }
        if($("#pause_"+id).hasClass("active")) {
            $("#pause_"+id).removeClass("active");
        }
        that.makeMonitoringChart(id);
	};
	
    /**
     * This function resets the global variables & again call the api calling function after given timeout
     * @class devicePlottingLib
     * @method recallServer
     */
    this.recallServer = function() {

    	/*Store the reference of current pointer in a global variable*/
    	that = this;

    	/*Hide The loading Icon*/
		$("#loadingIcon").hide();

		/*Enable the refresh button*/
		$("#resetFilters").button("complete");
		

    	setTimeout(function() {
			
			/*Hide The loading Icon*/
			$("#loadingIcon").show();

			/*Enable the refresh button*/
			$("#resetFilters").button("loading");

			/*Reset markers & polyline*/
			that.clearMapElements();

			/*Reset Global Variables & Filters*/
			that.resetVariables();	
			
			/*Recall the API*/
			that.getDevicesData(hostIp,username);

		},120000);
    };

    /**
	 * This function removes all the elements from the map
	 * @class devicePlottingLib
	 * @method clearMapElements
	 */
	this.clearMapElements = function() {

		/*Store the reference of current pointer in a global variable*/
		that = this;

		/*Clear the marker array of OverlappingMarkerSpiderfier*/
		oms.clearMarkers();

		/*Clear master marker cluster objects*/
		if(masterClusterInstance != "") {
			masterClusterInstance.clearMarkers();
		}
		
		/*Clear slave marker cluster objects*/
		if(slaveClusterInstance != "") {
			slaveClusterInstance.clearMarkers();
		}

		/*Hide The loading Icon*/
		$("#loadingIcon").hide();

		/*Enable the refresh button*/
		$("#resetFilters").button("complete");		

		/*If any master devices exists*/
		if(masterMarkersObj.length > 0) {

			/*Remove All Master Markers*/
			for(var i=0;i<masterMarkersObj.length;i++) {

				masterMarkersObj[i].setMap(null);
			}
		}

		/*If any slave devices exists*/
		if(slaveMarkersObj.length > 0) {

			/*Remove All Slave Markers*/
			for(var j=0;j<slaveMarkersObj.length;j++) {

				slaveMarkersObj[j].setMap(null);
			}
		}

		/*If any link between devices exists*/
		if(pathLineArray.length > 0) {

			/*Remove all link line between devices*/
			for(var j=0;j<pathLineArray.length;j++) {

				pathLineArray[j].setMap(null);
			}
		}		
	};

	/**
	 * This function reset all global variable used in the process
	 * @class devicePlottingLib
	 * @method resetVariables
	 */
	this.resetVariables = function() {

		/*Store the reference of current pointer in a global variable*/
		that = this;

		$("#technology").html("<option value=''>Select Technology</option>");
		$("#vendor").html("<option value=''>Select Vendor</option>");
		$("#state").html("<option value=''>Select State</option>");
		$("#city").html("<option value=''>Select City</option>");
		/*Reset All The Variables*/
		hitCounter = 1;
		showLimit = 0;
		remainingDevices = 0;
		counter = 0;
		totalCalls = 1;
		devicesObject = {};
		devices = [];
		cityArray = [];
		stateArray = [];
		vendorArray = [];
		techArray = [];
		masterMarkersObj = [];
		slaveMarkersObj = [];
		clusterIcon = "";
	};
}