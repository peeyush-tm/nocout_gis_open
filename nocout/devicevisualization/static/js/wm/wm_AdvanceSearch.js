function WmAdvanceSearch(data) {

	var master_Data = data;
	var previous_Stored_Values_Obj = {name: [], ip: [], cktId: [], city: []};

	this.showNotification= function() {
		if(!$("li#gis_search_status_txt").length) {
			$("#gis_status_txt").append("<li id='gis_search_status_txt'>Advance Search Applied<button class='btn btn-sm btn-danger pull-right' style='padding:2px 5px;margin:-3px;' onclick='whiteMapClass.resetAdvanceSearch();'>Reset</button></li>");
		}
	}

	this.hideNotification= function() {
		if($("li#gis_search_status_txt").length) {
			$("li#gis_search_status_txt").remove();
		}
	}

	this.resetAdvanceSearch = function() {
		$("#search_name").select2('val', '');
		$("#search_ip").select2('val', '');
		$("#search_cktId").select2('val', '');
		$("#search_city").select2('val', '');

		$("#resetSearchForm").addClass('hide');

		searchMarkerLayer.removeFeatures();

		previous_Stored_Values_Obj = {name: [], ip: [], cktId: [], city: []};
	}

	this.applyAdvanceSearch = function() {
		var bs_name = "", ip = "", city = "", searchCktId = "", that= this;
		var base_stations = [];

		bs_name = $("#search_name").val();
		ip = $("#search_ip").val();
		city = $("#search_city").val();
		searchCktId = $("#search_cktId").val();

		previous_Stored_Values_Obj = {name: bs_name, ip: ip, cktId: searchCktId, city: city};

		//If no value for advance search
		if ((bs_name === "" || bs_name === null) && (ip === "" || ip === null) && (city === "" || city === null) && (searchCktId === "" || searchCktId === null)) {
			searchMarkerLayer.removeFeatures();
			//do nothing
		} else {
			stationsLoop: for (var i = 0; i < master_Data.length; i++) {
				var markerData = master_Data[i];
				var isValid = false;
				var ipCondition;
				var namePresent, cktIdPresent, cityPresent;
				//If bs_name is present
				if (bs_name !== "" && bs_name !== null && bs_name.length) {

					//Check for Undefined value because of select2
					if (bs_name.length === 1 && !bs_name[0]) {} else {
						namePresent= true;
						var goodThing = false;
						var baseStationName = markerData.name;
						//Check for bs_name
						for (var j = 0; j < bs_name.length; j++) {
							if (bs_name[j] && baseStationName === bs_name[j]) {
								goodThing = true;
							}
						}
						//If bs_name fails, continue stationsLoop
						if (goodThing === false) {
							continue stationsLoop;
						}
					}
				}

				//If ip is present
				if (ip !== "" && ip !== null && ip.length) {
					//Check for Undefined value because of select2
					if (ip.length === 1 && !ip[0]) {} else {
						var goodThing = false;
						var baseStationIps = markerData.sector_configured_on_devices;
						//Check for ip name
						for (var j = 0; j < ip.length; j++) {
							if (ip[j] && baseStationIps.indexOf(ip[j]) !== -1) {
								ipCondition= true;
								goodThing = true;
							}
							for(var z=0; z< markerData.data.param.sector.length; z++) {
								var sector= markerData.data.param.sector[z];
								for(var y=0; y< sector.sub_station.length; y++) {
									var sub_station = sector.sub_station[y];
									if(sub_station.data.param.sub_station[0].value == ip[j]) {
										base_stations.push(sub_station);
										if(ipCondition === undefined) {
											ipCondition = false;
											goodThing= true;
										}
									}
								}
							}
						}
						//If ip fails, continue stationsLoop
						if (goodThing === false) {
							continue stationsLoop;
						}
					}
				}

				//If searchCktId is present
				if (searchCktId !== "" && searchCktId !== null && searchCktId.length) {
					//Check for Undefined value because of select2
					if (searchCktId.length === 1 && !searchCktId[0]) {} else {
						cktIdPresent= true;
						var goodThing = false;
						var baseStationCktId = markerData.circuit_ids;
						//Check for searchCktId name
						for (var j = 0; j < searchCktId.length; j++) {
							if (searchCktId[j] && baseStationCktId.indexOf(searchCktId[j]) !== -1) {
								for(var z=0; z< markerData.data.param.sector.length; z++) {
									var sector= markerData.data.param.sector[z];
									for(var y=0; y< sector.sub_station.length; y++) {
										var sub_station = sector.sub_station[y];
										if(sub_station.data.param.sub_station[3].value === searchCktId[j]) {
											base_stations.push(sub_station);
										}
									}
								}
								goodThing = true;
							}
						}
						//If searchCktId fails, continue stationsLoop
						if (goodThing === false) {
							continue stationsLoop;
						}
					}
				}

				//If city is present
				if (city !== "" && city !== null && city.length) {
					//Check for Undefined value because of select2
					if (city.length === 1 && !city[0]) {} else {
						cityPresent = true;
						var goodThing = false;
						var baseStationCity = markerData.data.city;
						//Check for city value
						for (var j = 0; j < city.length; j++) {
							if (city[j] && baseStationCity === city[j]) {
								goodThing = true;
							}
						}
						//If city failes, continue stationsLoop
						if (goodThing === false) {
							continue stationsLoop;
						}
					}
				}
				if((ipCondition=== undefined && ipCondition !== false) || (cityPresent || cktIdPresent || namePresent)) {
					base_stations.push(markerData);
				}
			}

			if (base_stations.length) {
				var bounds = new OpenLayers.Bounds();
				var searchmarkersList = [];
				for (var i = 0; i < base_stations.length; i++) {
					var marker = whiteMapClass.createOpenLayerVectorMarker(new OpenLayers.Size(21, 25), base_url+'/static/img/icons/bs_bounce.png', base_stations[i].data.lon, base_stations[i].data.lat, {});
					searchmarkersList.push(marker);
					// this.markersLayer.addMarker(marker);
					// search_Markers.push(marker);
					
					bounds.extend(new OpenLayers.LonLat(base_stations[i].data.lon, base_stations[i].data.lat));
					that.showNotification();
				}
				searchMarkerLayer.removeFeatures();
				searchMarkerLayer.addFeatures(searchmarkersList);
				$("#resetSearchForm").removeClass('hide');
				ccpl_map.zoomToExtent(bounds);
			} else {
				alert("NO RESULT FOUND");
			}
		}
	}

	this.destroyAdvSearchHtml = function() {
		$("#advSearchFormContainer").html('');
		if(!$("#advSearchContainerBlock").hasClass("hide")) {
			$("#advSearchContainerBlock").addClass("hide");
		}
	}
	
	this.prepareAdvSearchHtml= function(advSearchFormData) {
		this.destroyAdvSearchHtml();
		createAdvanceSearchHtml(advSearchFormData);

		if(previous_Stored_Values_Obj.name && previous_Stored_Values_Obj.name.length) {
			$("#search_name").select2('val', previous_Stored_Values_Obj.name);
		}
		if(previous_Stored_Values_Obj.ip && previous_Stored_Values_Obj.ip.length) {
			$("#search_ip").select2('val', previous_Stored_Values_Obj.ip);
		}
		if(previous_Stored_Values_Obj.cktId && previous_Stored_Values_Obj.cktId.length) {
			$("#search_cktId").select2('val', previous_Stored_Values_Obj.cktId);
		}
		if(previous_Stored_Values_Obj.city && previous_Stored_Values_Obj.city.length) {
			$("#search_city").select2('val', previous_Stored_Values_Obj.city);
		}
	}

	this.getMasterData= function() {
		return master_Data;
	}

	this.setMasterData= function(newData) {
		master_Data = newData;
	}
}