function WmAdvanceFilter(bsData, bsMarkerObj, ssMarkerObj, masterStationsArr, linesObj, sectorsObj) {
// console.log(data.length);
	var master_Data = bsData;
	var master_Bs_Marker_Obj = bsMarkerObj;
	var master_Ss_Marker_Obj = ssMarkerObj;
	var master_Stations_Array = masterStationsArr;
	var master_Lines_Obj = linesObj;
	var master_Sectors_Obj = sectorsObj;
	var previous_Stored_Values_Obj = {technology: [], vendor: [], city: [], state: []};

	this.resetFilter= function() {
		showSpinner();
		$("#filter_technology").select2('val', '');
		$("#filter_vendor").select2('val', '');
		$("#filter_state").select2('val', '');
		$("#filter_city").select2('val', '');

		$("#resetAdvFilterBtn").addClass('hide');

		previous_Stored_Values_Obj = {technology: [], vendor: [], city: [], state: []};
		setTimeout(function() {
			$("#setAdvFilterBtn").trigger('click');
			hideSpinner();
		}, 20);
		
	}

	this.applyFilter = function() {
		var filteredBsMarkers = [];
		var filteredLines = [];
		var filteredSectors = [];
		var data_for_filters = [];

		//Values
		var technologyValue = $("#filter_technology").val(), vendorValue = $("#filter_vendor").val(), stateValue = $("#filter_state").val(), cityValue = $("#filter_city").val();
		
		previous_Stored_Values_Obj.technology = technologyValue;
		previous_Stored_Values_Obj.vendor = vendorValue;
		previous_Stored_Values_Obj.state = stateValue;
		previous_Stored_Values_Obj.city = cityValue;

		stationsLoop: for (var i = 0; i < master_Data.length; i++) {
			var markerData = master_Data[i];
			if ((technologyValue === "" || technologyValue === null) && (vendorValue === "" || vendorValue === null) && (stateValue === "" || stateValue === null) && (cityValue === "" || cityValue === null)) {
				filteredBsData = master_Data;
				
				filteredBsMarkers = master_Stations_Array;
				for(var key in master_Lines_Obj) {
					var lines= master_Lines_Obj[key];
					for(var j=0; j< lines.length; j++) {
						lines[j].filteredLine= false;
						filteredLines.push(lines[j]);
					}
					master_Lines_Obj[key]= lines;
				}
				
				for(var key in master_Sectors_Obj) {
					var sectors= master_Sectors_Obj[key];
					for(var j=0; j< sectors.length; j++) {
						filteredSectors.push(sectors[j]);
					}
					master_Sectors_Obj[key]= sectors;
				}
				break stationsLoop;
			}

			//If technology value is present
			if (technologyValue !== "" && technologyValue !== null && technologyValue.length) {
				var goodThing = false;
				var baseStationTechnology = markerData.sector_ss_technology;

				if(baseStationTechnology) {
					baseStationTechnology = $.trim(baseStationTechnology.toLowerCase());
					//check if marker satisfies the technology condition
					for (var j = 0; j < technologyValue.length; j++) {
						if (technologyValue[j] && (baseStationTechnology.indexOf($.trim(technologyValue[j].toLowerCase())) !== -1)) {
							var goodString = "";
							for(var k=0; k< markerData.data.param.sector.length; k++) {
								if(technologyValue[j]== markerData.data.param.sector[k].technology) {
									for(var l=0;l< markerData.data.param.sector[k].sub_station.length; l++) {
										// console.log(markerData.data.param.sector[k].sub_station[l].name);
										goodString+= " "+markerData.data.param.sector[k].sub_station[l].name;
									}
								}
							}

							var ss_Markers = master_Ss_Marker_Obj[markerData.name];
							if(ss_Markers) {
								for(var m=0; m< ss_Markers.length; m++) {
									var ss_Marker_name = ss_Markers[m].attributes.name;
									// console.log(goodString+ "      " + ss_Marker_name);
									if(goodString.indexOf(ss_Marker_name) > -1) {
										ss_Markers[m].isNotFiltererd = true;
									} else {
										console.log('here');
										ss_Markers[m].isNotFiltererd = false;
									}
								}
}
							master_Ss_Marker_Obj[markerData.name] = ss_Markers;

							var line_Markers = master_Lines_Obj[markerData.name];
							// console.log(master_Lines_Obj);
							
							goodThing = true;
						}
					}
				}
				//if does not
				if (goodThing === false) {
					//continue loop
					continue stationsLoop;
				}
			}

			//If vendor value is present
			if (vendorValue !== "" && vendorValue !== null && vendorValue.length) {
				var goodThing = false;
				var baseStationVendor = markerData.sector_ss_vendor;

				if(baseStationVendor) {
					baseStationVendor = $.trim(baseStationVendor.toLowerCase());
					//check if marker satisfies the vendor condition
					for (var j = 0; j < vendorValue.length; j++) {
						var vendorVal = $.trim(vendorValue[j].toLowerCase());
						if (vendorValue[j] && baseStationVendor.indexOf(vendorVal) !== -1) {
							goodThing = true;
						}
					}
				}
				//if does not
				if (goodThing === false) {
					//continue loop
					continue stationsLoop;
				}
			}

			//If state value is present
			if (stateValue !== "" && stateValue !== null && stateValue.length) {
				var goodThing = false;
				var baseStationState = markerData.data.state;
				if(baseStationState) {
					baseStationState = $.trim(baseStationState.toLowerCase());
					//check if marker satisfies the state condition
					for (var j = 0; j < stateValue.length; j++) {
						if (stateValue[j] && baseStationState === $.trim(stateValue[j].toLowerCase())) {
							goodThing = true;
						}
					}
				}
				//if does not
				if (goodThing === false) {
					//continue loop
					continue stationsLoop;
				}
			}

			//If state value is present
			if (cityValue !== "" && cityValue !== null && cityValue.length) {
				var goodThing = false;
				var baseStationCity = markerData.data.city;
				if(baseStationCity) {
					baseStationCity = $.trim(baseStationCity.toLowerCase());
					//check if marker satisfies the state condition
					for (var j = 0; j < cityValue.length; j++) {
						if (cityValue[j] && baseStationCity === $.trim(cityValue[j].toLowerCase())) {
							goodThing = true;
						}
					}

				}
				//if does not
				if (goodThing === false) {
					//continue loop
					continue stationsLoop;
				}
			}

			data_for_filters.push(markerData);

			filteredBsMarkers.push(master_Bs_Marker_Obj[markerData.name]);
			var bsSubStationsMarkers = master_Ss_Marker_Obj[markerData.name];
			if(bsSubStationsMarkers && bsSubStationsMarkers.length) {
				for(var j=0; j< bsSubStationsMarkers.length; j++) {
					// if(bsSubStationsMarkers.isNotFiltererd) {
						filteredBsMarkers.push(bsSubStationsMarkers[j]);						
					// } 
				}
			}

			var bsLines = master_Lines_Obj[markerData.name];
			// console.log(bsLines);
			if(bsLines && bsLines.length) {
				for(var j=0; j< bsLines.length; j++) {
					bsLines[j].filteredLine= true;
					filteredLines.push(bsLines[j]);
				}
			}

			var bsSectors = master_Sectors_Obj[markerData.name];
			if(bsSectors && bsSectors.length) {
				for(var j=0; j< bsSectors.length; j++) {
					filteredSectors.push(bsSectors[j]);
				}
			}
			$("#resetAdvFilterBtn").removeClass('hide');
		}
		return {data_for_filters: data_for_filters,filtered_Features: filteredBsMarkers, line_Features: filteredLines, sector_Features: filteredSectors};
	}

	/*
	This function removes Advance Filter html markup from dom and hides it
	 */
	this.destroyAdvanceFilter = function() {
		$("#advFilterFormContainer").html('');
		if(!$("#advFilterContainerBlock").hasClass("hide")) {
			$("#advFilterContainerBlock").addClass("hide");
		}
	}

	/*
	* This function prepare HTML content which is shown on the Screen.
	 */
	this.createAdvanceFilterMarkup= function(advFilterFormData) {
		//destroy old html
		this.destroyAdvanceFilter();
		//create advance filter html with form data
		createAdvanceFilterHtml(advFilterFormData);

		//update any previous_stored technology value
		if(previous_Stored_Values_Obj.technology && previous_Stored_Values_Obj.technology.length) {
			$("#filter_technology").select2('val', previous_Stored_Values_Obj.technology);
		}
		//update any previous_stored vendor value
		if(previous_Stored_Values_Obj.vendor && previous_Stored_Values_Obj.vendor.length) {
			$("#filter_vendor").select2('val', previous_Stored_Values_Obj.vendor);
		}
		//update any previous_stored state value
		if(previous_Stored_Values_Obj.state && previous_Stored_Values_Obj.state.length) {
			$("#filter_state").select2('val', previous_Stored_Values_Obj.state);
		}
		//update any previous_stored city value
		if(previous_Stored_Values_Obj.city && previous_Stored_Values_Obj.city.length) {
			$("#filter_city").select2('val', previous_Stored_Values_Obj.city);
		}
	}
}