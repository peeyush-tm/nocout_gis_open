/*Global Variables*/
var mapInstance = "",
	that = "",
	currentDomElement = "",
	oms = "",
	pathConnector = "",
	infowindow = "",
	devicesObject = {},
	metaRequest = {},
	metaData = {},
	hitCounter = 0,
	devicesCount = 0,
	remainingDevices = 0,
	cityArray = [],
	stateArray = [],
	vendorArray = [],
	techArray = [],
	devices = [],
	slaveMarkersObj = {},
	masterMarkersObj = {};

/**
 * This class is used to plot the BS & SS on the google maps & show information on click
 * @class networkMap
 * @uses jQuery
 * @uses Google Maps
 * Coded By :- Yogender Purohit
 */
function networkMapClass()
{
	/*Store the reference of current pointer in a global variable*/
	that = this;
	metaData["page_number"] = 1;
	metaData["limit"] = 0;
	metaRequest["meta"] = metaData;
	/**
	 * This function creates the base google map with the lat long of India
	 * @function createMap
	 * @class networkMap
	 * @param domElement "String" It the the dom element on which the map is to be create
	 */
	this.createMap = function(domElement)
	{
		/*Save the dom element in the global variable*/
		currentDomElement = domElement;

		var mapObject = {
			center    : new google.maps.LatLng(21.0000,78.0000),
			zoom      : 3
		};    
		/*Create Map Type Object*/
		mapInstance = new google.maps.Map(document.getElementById(domElement),mapObject);

		/*Create a instance of OverlappingMarkerSpiderfier*/
		oms = new OverlappingMarkerSpiderfier(mapInstance,{markersWontMove: true, markersWontHide: true});

		/*Create a instance of google map info window*/
		infowindow = new google.maps.InfoWindow();		

		oms.addListener('click', function(marker,e) {
			
			/*Call the function to create info window content*/
			var content = that.makeWindowContent(marker,e);
			/*Set the content for infowindow*/
			infowindow.setContent(content);
			/*Set The Position for InfoWindow*/
			infowindow.setPosition(e.latLng);
			/*Open the info window*/
			infowindow.open(mapInstance);
		});
		
		oms.addListener('spiderfy', function(markers) {

			infowindow.close();
		});
	};

	/**
	 * This function plots the BS & SS network on the created google map
	 * @function getDevicesData
	 * @class networkMap
	 */
	this.getDevicesData = function(hostIp,username)
	{	
		/*Append the username in the object*/
		metaRequest["username"] = username;

		that.apiCallFunction(metaRequest,hostIp,username);
	};

	/**
     * This function is used to populate the markers on the google maps
     * @class netowrkMap
     * @method populateNetwork
     * @param resultantMarkers [JSON Objet Array] It is the devies object array
	 */
	this.populateNetwork = function(resultantMarkers)
	{
		// that.createMap(currentDomElement);

		for(var i=0;i<resultantMarkers.length;i++)
		{
			/*Create Master Marker Object*/
			var masterMarkerObject = {
		    	position  	: new google.maps.LatLng(resultantMarkers[i].data.lat,resultantMarkers[i].data.lon),
		    	map       	: mapInstance,
		    	icon 	  	: resultantMarkers[i].data.markerUrl,
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
		    	pointDetail : resultantMarkers[i].data.otherDetail
			};
			/*Create Master Marker*/
		    var masterMarker = new google.maps.Marker(masterMarkerObject);
		    /*Add the master marker to the global master markers array*/
		    masterMarkersObj.push(masterMarker);
		    /*Loop for the number of slave & their links with the master*/
		    var slaveCount = resultantMarkers[i].children.length;

		    for(var j=0;j<slaveCount;j++)
		 	{
		    	/*Create Slave Marker Object*/
			    var slaveMarkerObject = {
			    	position  	: new google.maps.LatLng(resultantMarkers[i].children[j].data.lat,resultantMarkers[i].children[j].data.lon),
			    	map       	: mapInstance,
			    	icon 	  	: resultantMarkers[i].children[j].data.markerUrl,
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
			    	pointDetail : resultantMarkers[i].children[j].data.otherDetail
				};
				/*Create Slave Marker*/
			    var slaveMarker = new google.maps.Marker(slaveMarkerObject);				    				    
			    /*Add the slave marker to the global slave array*/
		    	slaveMarkersObj.push(slaveMarker);
			    /*Add BS & SS markers to the OverlappingMarkerSpiderfier*/
			    oms.addMarker(masterMarker);
				oms.addMarker(slaveMarker);

				if(resultantMarkers[i].data.showLink == 1)
				{
					/*Create object for Link Line Between Master & Slave*/
					var pathDataObject = [
						new google.maps.LatLng(resultantMarkers[i].data.lat,resultantMarkers[i].data.lon),
						new google.maps.LatLng(resultantMarkers[i].children[j].data.lat,resultantMarkers[i].children[j].data.lon)
					];					

					pathConnector = new google.maps.Polyline({

						path 				: pathDataObject,						
						strokeColor			: resultantMarkers[i].children[j].data.linkColor,
						strokeOpacity		: 1.0,
						strokeWeight		: 4,
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

					/*Bind Click Event on Link Path Between Master & Slave*/
					google.maps.event.addListener(pathConnector, 'click', function(e) {
						
						/*Call the function to create info window content*/
						var content = that.makeWindowContent(this);
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
	};

	/**
	 * This function creates the info window content for BS,SS & link path 
	 * @class networkMap
	 * @method makeWindowContent
	 * @param contentObject {JSON Object} It contains the current pointer(this) information
	 * @return windowContent "String" It contains the content to be shown on info window
	 */
	this.makeWindowContent = function(contentObject,event)
	{
		var windowContent = "",
			infoTable =  "",
			perfContent = "",
			clickedType = $.trim(contentObject.pointType);

		/*True,if clicked on the link line*/
		if(clickedType == "path")
		{
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
		}		
		else
		{
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
			infoTable += "<tr><td>Lat, Long</td><td>"+event.latLng.k+", "+event.latLng.A+"</td></tr>";
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
		
		var stateOptions = "<option value=''>Select State</option>",
	 		cityOptions = "<option value=''>Select City</option>",
	 		vendorOptions = "<option value=''>Select Vendor</option>",
	 		technologyOptions = "<option value=''>Select Technology</option>";


 		/*Loop for the state array*/
	 	for(var i=0;i<stateArray.length;i++)
	 	{
	 		stateOptions += '<option value="'+stateArray[i]+'">'+stateArray[i]+'</option>';
	 	}

	 	/*Loop for the city array*/
	 	for(var j=0;j<cityArray.length;j++)
	 	{
	 		cityOptions += '<option value="'+cityArray[j]+'">'+cityArray[j]+'</option>';
	 	}

	 	/*Loop for the vendor array*/
	 	for(var k=0;k<vendorArray.length;k++)
	 	{
	 		vendorOptions += '<option value="'+vendorArray[k]+'">'+vendorArray[k]+'</option>';
	 	}	 	

	 	/*Loop for the technology array*/
	 	for(var l=0;l<technologyArray.length;l++)
	 	{
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

		var filterKey = [],
			filteredData = [],
			masterIds = [],
			slaveIds = [];


		/*Clear the marker array of OverlappingMarkerSpiderfier*/
		oms.clearMarkers();

		/*Fetch the keys from the filter array*/
		$.each(filtersArray, function(key, value) {

		    filterKey.push(key);
		});

	 	if(devicesObject.success == 1)
	 	{
	 		filteredData = [];
	 		for(var i=0;i<devices.length;i++)
	 		{
	 			/*Total Slaves Count*/
	 			var slaveLength = devices[i].children.length;
	 			/*Loop For Slaves*/
	 			for(var j=0;j<slaveLength;j++)
	 			{
	 				var master = devices[i];
		 			var slave = devices[i].children[j];
		 			
		 			/*Conditions as per the number of filters*/
		 			if(filterKey.length == 1)
		 			{
	 					if(master.data[filterKey[0]] == filtersArray[filterKey[0]] || slave.data[filterKey[0]] == filtersArray[filterKey[0]])
		 				{
		 					/*Check For The Duplicacy*/
		 					if(masterIds.indexOf(master.id) == -1 && slaveIds.indexOf(slave.id) == -1)
		 					{
		 						/*Save the master & slave ids to array to remove duplicacy*/
		 						masterIds.push(master.id);
		 						slaveIds.push(slave.id);

		 						filteredData.push(devices[i]);
		 					}
		 				}

		 			}
		 			else if(filterKey.length == 2)
		 			{
	 					if((master.data[filterKey[0]] == filtersArray[filterKey[0]] || slave.data[filterKey[0]] == filtersArray[filterKey[0]]) && (master.data[filterKey[1]] == filtersArray[filterKey[1]] || slave.data[filterKey[1]] == filtersArray[filterKey[1]]))
		 				{	 					
		 					/*Check For The Duplicacy*/
		 					if(masterIds.indexOf(master.id) == -1 && slaveIds.indexOf(slave.id) == -1)
		 					{
		 						/*Save the master & slave ids to array to remove duplicacy*/
		 						masterIds.push(master.id);
		 						slaveIds.push(slave.id);

		 						filteredData.push(devices[i]);
		 					}
		 				}
		 			}
		 			else if(filterKey.length == 3)
		 			{
		 				if((master.data[filterKey[0]] == filtersArray[filterKey[0]] || slave.data[filterKey[0]] == filtersArray[filterKey[0]]) && (master.data[filterKey[1]] == filtersArray[filterKey[1]] || slave.data[filterKey[1]] == filtersArray[filterKey[1]]) && (master.data[filterKey[2]] == filtersArray[filterKey[2]] || slave.data[filterKey[2]] == filtersArray[filterKey[2]]))
		 				{	 					
		 					/*Check For The Duplicacy*/
		 					if(masterIds.indexOf(master.id) == -1 && slaveIds.indexOf(slave.id) == -1)
		 					{
		 						/*Save the master & slave ids to array to remove duplicacy*/
		 						masterIds.push(master.id);
		 						slaveIds.push(slave.id);

		 						filteredData.push(devices[i]);
		 					}
		 				}
		 			}
		 			else if(filterKey.length == 4)
		 			{
		 				if((master.data[filterKey[0]] == filtersArray[filterKey[0]] || slave.data[filterKey[0]] == filtersArray[filterKey[0]]) && (master.data[filterKey[1]] == filtersArray[filterKey[1]] || slave.data[filterKey[1]] == filtersArray[filterKey[1]]) && (master.data[filterKey[2]] == filtersArray[filterKey[2]] || slave.data[filterKey[2]] == filtersArray[filterKey[2]]) && (master.data[filterKey[3]] == filtersArray[filterKey[3]] || slave.data[filterKey[3]] == filtersArray[filterKey[3]]))
		 				{	 					
		 					/*Check For The Duplicacy*/
		 					if(masterIds.indexOf(master.id) == -1 && slaveIds.indexOf(slave.id) == -1)
		 					{
		 						/*Save the master & slave ids to array to remove duplicacy*/
		 						masterIds.push(master.id);
		 						slaveIds.push(slave.id);

		 						filteredData.push(devices[i]);
		 					}
		 				}
		 			}
	 			}
	 		}
	 		if(filteredData.length === 0)
	 		{
	 			alert("User Don't Have Any Devies For Selected Filters");
	 		}
	 		
	 		/*Clear the marker array of OverlappingMarkerSpiderfier*/
			oms.clearMarkers();

	 		/*Populate the map with the filtered markers*/
	 		that.populateNetwork(filteredData);
	 	}	
	};

	/**
	 * This function calls the populateNetwork function to load the fetched devices in case of no filters
	 * @class devicePlottingLib
	 * @method loadExistingDevices
	 */
	this.loadExistingDevices = function()
	{
		that.populateNetwork(devices);
	};

	/**
	 * This function makes the ajax call for the API to get the devices
	 * @class devicePlottingLib
	 * @method apiCallFunction
	 */
	this.apiCallFunction = function(metaInfo,hostIp,username)
	{
		hitCounter = hitCounter + 1;

		/*Update the page number*/
		metaInfo.meta.page_number = hitCounter;
		console.log(metaInfo.meta.limit);
		console.log(remainingDevices);

		if((remainingDevices <= metaInfo.meta.limit) && (remainingDevices != 0) && (metaInfo.meta.limit != 0))
		{
			metaRequest.meta.page_number = 1;
			metaRequest.meta.limit = 0;
			hitCounter = 0;
			remainingDevices = 0;
			devicesObject = {};
			devices = [];
			cityArray = [];
			stateArray = [];
			vendorArray = [];
			techArray = [];
			devices = [];

			setTimeout(function() {

				if(masterMarkersObj.length > 0)
				{
					/*Remove All Master Markers*/
					for(var i=0;i<masterMarkersObj.length;i++)
					{
						masterMarkersObj[i].setMap(null);
					}
				}
				if(slaveMarkersObj.length > 0)
				{
					/*Remove All Slave Markers*/
					for(var j=0;j<slaveMarkersObj.length;j++)
					{
						slaveMarkersObj[j].setMap(null);
					}
				}
				
				that.getDevicesData(hostIp,username);

			},50000);
		}
		else
		{
			setTimeout(function(){
				
				that.getDevicesData(hostIp,username);

			},3000);
			
		}
		
		/*Clear the marker array of OverlappingMarkerSpiderfier*/
		oms.clearMarkers();

		/*To Enable The Cross Domain Request*/
		$.support.cors = true;

		/*Ajax call to the API*/
		$.ajax({
			crossDomain: true,
			// url : "http://"+hostIp+":8000/device/stats/",
			url : "http://192.168.1.37:8000/device/stats/",
			type : "POST",
			dataType : "json",
			data : JSON.stringify(metaInfo),
			/*If data fetched successful*/
			success : function(result)
			{
				console.log(result);
				/*First call case*/
				if(devicesObject.data == undefined)
				{
					/*Save the result json to the global variable for global access*/
					devicesObject = result;
					/**/
					devices = devicesObject.data.objects.children;
				}
				else
				{
					devices = devices.concat(result.data.objects.children);
				}

				/*Update the device count with the received data*/
				devicesCount = devicesObject.data.meta.total_count;
				/*Update the device count with the received data*/
				metaRequest.meta.limit = devicesObject.data.meta.limit;

				if(remainingDevices == 0)
				{
					remainingDevices = devicesCount - devicesObject.data.meta.limit;
				}
				else
				{
					remainingDevices = remainingDevices - devicesObject.data.meta.limit;
				}

				if(devicesObject.success == 1)
				{
					/*Call the populateNetwork to show the markers on the map*/
					that.populateNetwork(devices);

					/*Make an array of master & slave cities as well as states*/
					for(var i=0;i<devices.length;i++)
					{
						/*Total number of slave for particular master*/
						var slaveCount = devices[i].children.length;

						/*Loop for the slaves*/
						for(var j=0;j<slaveCount;j++)
						{
							/*Push master city in cityArray array*/
							if(cityArray.indexOf($.trim(devices[i].data.city)) == -1)
							{
								cityArray.push($.trim(devices[i].data.city));
							}
							/*Push slave city in cityArray array*/
							if(cityArray.indexOf($.trim(devices[i].children[j].data.city)) == -1)
							{
								cityArray.push($.trim(devices[i].children[j].data.city));
							}

							/*Push master states in stateArray array*/
							if(stateArray.indexOf($.trim(devices[i].data.state)) == -1)
							{
								stateArray.push($.trim(devices[i].data.state));
							}
							/*Push slave states in stateArray array*/
							if(stateArray.indexOf($.trim(devices[i].children[j].data.state)) == -1)
							{
								stateArray.push($.trim(devices[i].children[j].data.state));
							}

							/*Push master vendors in masterVendorArray array*/
							if(vendorArray.indexOf($.trim(devices[i].data.vendor)) == -1)
							{
								vendorArray.push($.trim(devices[i].data.vendor));
							}
							/*Push slave vendors in slaveVendorArray array*/
							if(vendorArray.indexOf($.trim(devices[i].children[j].data.vendor)) == -1)
							{
								vendorArray.push($.trim(devices[i].children[j].data.vendor));
							}

							/*Push master technology in techArray array*/
							if(techArray.indexOf($.trim(devices[i].data.technology)) == -1)
							{
								techArray.push($.trim(devices[i].data.technology));
							}
							/*Push slave technology in techArray array*/
							if(techArray.indexOf($.trim(devices[i].children[j].data.technology)) == -1)
							{
								techArray.push($.trim(devices[i].children[j].data.technology));
							}
						}
					}
					/*Populate the city & state dropdown filters*/
					that.populateFilters(cityArray,stateArray,vendorArray,techArray);
				}
			},
			/*If data not fetched*/
			error : function(err)
			{
				console.log(err.success());
			}
		});
	}
}