/*Global Variables*/
var advSearch_self = "",
	gmapInstance = "",
	setFilterApiUrl = "",
	earthInstance = "",
    filtersInfoArray = [],
    templateData = "",
    formElements = "",
    elementsArray = [],
    resultantObject = {},
    appliedAdvFilter = [],
    searchParameters = "",
    lastSelectedValues = [];

/**
 * This class is used to create th filter form by calling the get_filter API & the call the set_filter API with the selected filters
 * @class advanceSearchLib
 * @uses jQuery
 * @uses Select2
 * Coded By :- Yogender Purohit
 */
function advanceSearchClass() {

	/*Store the reference of current pointer in a global variable*/
	advSearch_self = this; // Name of current pointer referencing element in all files should be different otherwise conflicts occurs

	/**
	 * This function first get the filters object from the server, create the filters HTML struction & then populate the HTML in the popup
	 * @function getFilterInfo
	 * @class advanceSearchLib
	 * @param domElement "String" It is dom element.
	 * @param windowTitle "String" It is title of the popup
	 * @param buttonId "String" It is the dom selector or ID of the clicked button.
	 * @param getApiUrl "String" It is the url of the get_filter API
	 * @param setFilterApiUrl "String" It is the url of the set_filter API
	 */
	this.getFilterInfo = function(domElemet,windowTitle,buttonId,getApiUrl,setApiUrl) {

		setFilterApiUrl = setApiUrl;

		/*If any filter is applied before then save the last filter array in other variable*/
		if(appliedAdvFilter.length != 0) {
			lastSelectedValues = appliedAdvFilter;
		}

		/*Change the text of the button to "Please Wait..." & disable the button*/
		$("#"+buttonId).button("loading");
		
		/*To Enable The Cross Domain Request*/
		$.support.cors = true;

		$.ajax({
			crossDomain: true,
			url : getApiUrl,
			// url : "http://127.0.0.1:8000/gis/get_filters/",
			type : "GET",
			dataType : "json",
			/*If data fetched successful*/
			success : function(result) {

				/*Revert the button to the initial state*/
				$("#"+buttonId).button("complete");

				/*If data fetch successfully*/
				if(result.success == 1) {

					templateData = "";
					elementsArray = [];

					filtersInfoArray = result.data.objects;

					templateData += '<div class="iframe-container"><div class="content-container"><div id="'+domElemet+'" class="advanceFiltersContainer">';
					templateData += '<form id="'+domElemet+'_form"><div class="form-group form-horizontal">';

					formElements = "";
					/*Reset the appliedAdvFilter*/
					appliedAdvFilter = [];

					for(var i=0;i<filtersInfoArray.length;i++) {

						if(filtersInfoArray[i] != null) {

							formElements += '<div class="form-group"><label for="'+filtersInfoArray[i].key+'" class="col-sm-4 control-label">';
							formElements += filtersInfoArray[i].title;
							formElements += '</label><div class="col-sm-8">';

							var currentKey = $.trim(filtersInfoArray[i].key);
							var elementType = $.trim(filtersInfoArray[i].element_type);
							/*Check Element Type*/
							if(elementType == "multiselect") {

								var filterValues = filtersInfoArray[i].values;
								if(filterValues.length > 0) {

									formElements += '<select multiple class="multiSelectBox col-md-12" id="filter_'+filtersInfoArray[i].key+'">';

									/*Condition for mapped tables to pass the ID in the values else pass the value*/
									if(currentKey == "device_group" || currentKey == "device_type" || currentKey == "device_technology" || currentKey == "device_vendor") {

										for(var j=0;j<filterValues.length;j++) {

											if(($.trim(filterValues[j].id) != null && $.trim(filterValues[j].value) != null) && ($.trim(filterValues[j].id) != "" && $.trim(filterValues[j].value) != "")) {

												formElements += '<option value="'+filterValues[j].id+'">'+filterValues[j].value+'</option>';
											}
										}	
									} else {

										for(var j=0;j<filterValues.length;j++) {

											if(($.trim(filterValues[j].id) != null && $.trim(filterValues[j].value) != null) && ($.trim(filterValues[j].id) != "" && $.trim(filterValues[j].value) != "")) {

												formElements += '<option value="'+filterValues[j].value+'">'+filterValues[j].value+'</option>';
											}
										}
									}

									formElements += '</select>';
								} else {

									formElements += '<input type="text" id="filter_'+filtersInfoArray[i].key+'" name="'+filtersInfoArray[i].key+'"  class="form-control"/>';
								}
							} else if(elementType == "select") {

								var filterValues = filtersInfoArray[i].values;
								if(filterValues.length > 0) {

									formElements += '<select class="multiSelectBox col-md-12" id="filter_'+filtersInfoArray[i].key+'">';

									for(var j=0;j<filterValues.length;j++) {

										formElements += '<option value="'+filterValues[j].id+'">'+filterValues[j].value+'</option>';
									}

									formElements += '</select>';
								} else {

									formElements += '<input type="text" id="filter_'+filtersInfoArray[i].key+'" name="'+filtersInfoArray[i].key+'"  class="form-control"/>';
								}
							}
							else if(elementType == "radio") {

								var filterValues = filtersInfoArray[i].values;
								if(filterValues.length > 0) {

									for(var j=0;j<filterValues.length;j++) {

										formElements += '<label class="radio-inline"><input type="radio" id="radio_'+filterValues[j].id+'" class="radioField" value="'+filterValues[j].id+'" name="'+filtersInfoArray[i].key+'"> '+filterValues[j].value+'</label>';
									}
								} else {

									formElements += '<input type="text" id="filter_'+filtersInfoArray[i].key+'" name="'+filtersInfoArray[i].key+'"  class="form-control"/>';
								}
							} else if(elementType == "checkbox") {

								var filterValues = filtersInfoArray[i].values;
								if(filterValues.length > 0) {

									for(var j=0;j<filterValues.length;j++) {

										formElements += '<label class="checkbox-inline"><input type="checkbox" class="checkboxField" id="checkbox_'+filterValues[j].id+'" value="'+filterValues[j].id+'" name="'+filterValues[j].id+'"> '+filterValues[j].value+'</label>';
									}
								} else {

									formElements += '<input type="text" id="filter_'+filtersInfoArray[i].key+'" name="'+filtersInfoArray[i].key+'"  class="form-control"/>';
								}
							} else {

								formElements += '<input type="text" id="filter_'+filtersInfoArray[i].key+'" name="'+filtersInfoArray[i].key+'"  class="form-control"/>';
							}

							formElements += '</div></div>';
							elementsArray.push(formElements);
							formElements = "";
						}
					}

					templateData += elementsArray.join('');
					templateData += '<div class="clearfix"></div></div><div class="clearfix"></div></form>';
					templateData += '<div class="clearfix"></div></div></div><iframe class="iframeshim" frameborder="0" scrolling="no"></iframe></div><div class="clearfix"></div>';

					$("#advFilterFormContainer").html(templateData);

					if($("#advFilterContainerBlock").hasClass("hide")) {
						$("#advFilterContainerBlock").removeClass("hide");
					}
						
					/*Initialize the select2*/
					$(".advanceFiltersContainer select").select2();

					/*loop to show the last selected values*/
					for(var k=0;k<lastSelectedValues.length;k++) {

						var multiselect = $("#filter_"+lastSelectedValues[k].field),
							radio = $("#radio_"+lastSelectedValues[k].value[0]),
							checkbox = $("#checkbox_"+lastSelectedValues[k].value[0])
							multiselectClasses = "",
							radioClasses = "",
							checkboxClasses = "";

						if(multiselect.length > 0) {
							multiselectClasses = $("#filter_"+lastSelectedValues[k].field)[0].className;
						}
						if(radio.length > 0) {
							radioClasses = $("#radio_"+lastSelectedValues[k].value[0])[0].className;
						}
						if(checkbox.length > 0) {
							checkboxClasses = $("#checkbox_"+lastSelectedValues[k].value[0])[0].className;
						}

						/*Conditions for different types of feilds*/
						if(multiselectClasses.indexOf("multiSelectBox") != -1) {
						
							$("#filter_"+lastSelectedValues[k].field).select2("val",lastSelectedValues[k].value);
						
						} else if(radioClasses.indexOf("radioField") != -1) {								
							$("#radio_"+lastSelectedValues[k].value[0])[0].checked = true;

						} else if(checkboxClasses.indexOf("checkboxField") != -1) {

							for(var l=0;l<lastSelectedValues[k].value.length;l++) {

								$("#checkbox_"+lastSelectedValues[k].value[l])[0].checked = true;
							}
						}
						else {
							$("#filter_"+lastSelectedValues[k].field).val(lastSelectedValues[k].value);
						}
					}

				}
				/*If data not fetched*/
				else {

					// console.log(result.message);
					$.gritter.add({
			            // (string | mandatory) the heading of the notification
			            title: 'Advance Filters - No Records',
			            // (string | mandatory) the text inside the notification
			            text: result.message,
			            // (bool | optional) if you want it to fade out on its own or just sit there
			            sticky: true
			        });
				}

				/*Remove backdrop div & hide spinner*/
                $("#ajax_backdrop").remove();
                if(!($("#ajax_spinner").hasClass("hide"))) {
                    /*Hide ajax_spinner div*/
                    $("#ajax_spinner").addClass("hide");
                }
			},
			/*If there is a problem in calling server*/
			error : function(err) {

				$("#"+buttonId).button("complete");
				// console.log(err.statusText);
				$.gritter.add({
		            // (string | mandatory) the heading of the notification
		            title: 'Advance Filters - Error',
		            // (string | mandatory) the text inside the notification
		            text: err.statusText,
		            // (bool | optional) if you want it to fade out on its own or just sit there
		            sticky: true
		        });

		        /*Remove backdrop div & hide spinner*/
                $("#ajax_backdrop").remove();
                if(!($("#ajax_spinner").hasClass("hide"))) {
                    /*Hide ajax_spinner div*/
                    $("#ajax_spinner").addClass("hide");
                }
			}
		});		
	};

	/**
	 * This method generates get parameter for setfilter API & call setFilter function
	 * @method callSetFilter
	 */
	this.callSetFilter = function() {

		for(var j=0;j<filtersInfoArray.length;j++) {

			resultantObject = {};

			var elementType = $.trim(filtersInfoArray[j].element_type);
			var selectId = filtersInfoArray[j].key;

			/*Check Element Type*/
			if(elementType == "multiselect") {

				var val = $("#filter_"+selectId).select2("val");
				if(val.length > 0) {

					resultantObject["field"] = selectId;
					resultantObject["value"] = val;
				}
			} else if(elementType == "select") {

				var selectedVal = $("#filter_"+selectId).select2("val");
				
				if(selectedVal.length > 0) {

					resultantObject["field"] = selectId;
					resultantObject["value"] = selectedVal;
				}
			} else if(elementType == "checkbox") {

				var checkboxArray = [];

				for(var k=0;k<filtersInfoArray[j].values.length;k++) {

					if($("#checkbox_"+filtersInfoArray[j].values[k].id)[0].checked == true) {

						checkboxArray.push($("#checkbox_"+filtersInfoArray[j].values[k].id)[0].value);
					}
				}

				if(checkboxArray.length > 0) {

					resultantObject["field"] = filtersInfoArray[j].key;
					resultantObject["value"] = checkboxArray;
				}
			} else if(elementType == "radio") {

				var radioArray = [];

				for(var k=0;k<filtersInfoArray[j].values.length;k++) {

					if($("#radio_"+filtersInfoArray[j].values[k].id)[0].checked == true) {

						radioArray.push($("#radio_"+filtersInfoArray[j].values[k].id)[0].value)												
					}
				}

				if(radioArray.length > 0) {

					resultantObject["field"] = filtersInfoArray[j].key;
					resultantObject["value"] = radioArray;
				}
			} else {

				var typedText = $("#filter_"+selectId).val();
				
				if(typedText.length > 0) {

					resultantObject["field"] = selectId;
					resultantObject["value"] = typedText;
				}
			}

			if(resultantObject.field != undefined) {

				appliedAdvFilter.push(resultantObject);
			}									
		}
		/*Stringify the object array to pass it in the query parameters for in set filter API*/
		searchParameters = JSON.stringify(appliedAdvFilter);

		/*call the setFilters function with the searchparamerts & setFilters API url*/
		advSearch_self.setFilters(searchParameters,setFilterApiUrl);

		/*Call the reset function*/
		advSearch_self.resetVariables();

		$("#advFilterFormContainer").html("");

		if(!($("#advFilterContainerBlock").hasClass("hide"))) {
			$("#advFilterContainerBlock").addClass("hide");
		}

		if($("#removeFilterBtn").hasClass("hide")) {
			$("#removeFilterBtn").removeClass("hide");
		}


		/*show The loading Icon*/
		$("#loadingIcon").show();

		/*Enable the refresh button*/
		$("#resetFilters").button("loading");

	};

	/**
	 * This function call the set filter api & as the response pass the devices to the devicePlottingLib
	 * @method setFilters
	 * @param searchString "String" It is the query string passed to the API
	 * @param setFilterApi "String" It is the URL of the set filter API
	 */
	this.setFilters = function(searchString,setFilterApi) {

		/*To Enable The Cross Domain Request*/
		$.support.cors = true;

		/*Show Remove Filters button*/
		if($("#removeFilterBtn").hasClass("hide")) {
			$("#removeFilterBtn").removeClass("hide");
		}

		$.ajax({
			crossDomain: true,
			url : setFilterApi+"?filters="+searchString,
			// url : "http://127.0.0.1:8000/gis/set_filters/?filters="+searchString,
			type : "GET",
			dataType : "json",
			/*If data fetched successful*/
			success : function(result) {

				/*If data fetch successfully*/
				if(result.success == 1) {

					if(result.data.objects != null) {

				        /*Reset The basic filters dropdown*/
				        $("#technology").val($("#technology option:first").val());
				        $("#vendor").val($("#vendor option:first").val());
				        $("#state").val($("#state option:first").val());
				        $("#city").val($("#city option:first").val());

			        	if(window.location.pathname.indexOf("google_earth") == -1) {

			        		/*Create a instance of networkMapClass*/
							gmapInstance = new devicePlottingClass_gmap();

							/*Reset markers, polyline & filters*/
					        gmapInstance.clearGmapElements();

					        /*Reset Global Variables & Filters*/
					        gmapInstance.resetVariables_gmap();

					        /*If cluster icon exist then save it to global variable else make the global variable blank*/
							if(result.data.objects.data.unspiderfy_icon == undefined) {
								clusterIcon = "";
							} else {
								clusterIcon = window.location.origin+"/"+result.data.objects.data.unspiderfy_icon;
							}

					        /*Call the make network to create the BS-SS network on the google map*/
					        gmapInstance.plotDevices_gmap(result.data.objects.children,"base_station");

			        	} else {

			        		/*Create a instance of googleEarthClass*/
			        		earthInstance = new googleEarthClass();

			        		/*Clear all the elements from google earth*/
					        earthInstance.clearEarthElements();

					        /*Reset Global Variables & Filters*/
					        earthInstance.resetVariables_earth();

					        /*create the BS-SS network on the google map*/
					        earthInstance.plotDevices_earth(result.data.objects.children,"base_station");
			        	}

					}
				} else {

					$.gritter.add({
			            // (string | mandatory) the heading of the notification
			            title: 'Advance Filters - No Records',
			            // (string | mandatory) the text inside the notification
			            text: result.message,
			            // (bool | optional) if you want it to fade out on its own or just sit there
			            sticky: true
			        });

			        /*hide The loading Icon*/
					$("#loadingIcon").hide();

					/*Enable the refresh button*/
					$("#resetFilters").button("complete");

					$("#removeFilterBtn").click();
				}

				/*Remove backdrop div & hide spinner*/
                $("#ajax_backdrop").remove();
                if(!($("#ajax_spinner").hasClass("hide"))) {
                    /*Hide ajax_spinner div*/
                    $("#ajax_spinner").addClass("hide");
                }
			},
			error : function(err) {

				// console.log(err.statusText);
				$.gritter.add({
		            // (string | mandatory) the heading of the notification
		            title: 'Advance Filters - Error',
		            // (string | mandatory) the text inside the notification
		            text: err.statusText,
		            // (bool | optional) if you want it to fade out on its own or just sit there
		            sticky: true
		        });

		        /*hide The loading Icon*/
				$("#loadingIcon").hide();

				/*Enable the refresh button*/
				$("#resetFilters").button("complete");

				/*Remove backdrop div & hide spinner*/
                $("#ajax_backdrop").remove();
                if(!($("#ajax_spinner").hasClass("hide"))) {
                    /*Hide ajax_spinner div*/
                    $("#ajax_spinner").addClass("hide");
                }
			}
		});
	};

	/**
	 * This function remove the applied filter n show default or un-filtered values	 
	 * @class advanceSearchLib
	 * @method removeFilters
	 */
	this.removeFilters = function() {

		/*Reset filter data array*/
		lastSelectedValues = [];
		appliedAdvFilter = []
		
		$("#advFilterFormContainer").html("");

		if(!($("#advFilterContainerBlock").hasClass("hide"))) {
			$("#advFilterContainerBlock").addClass("hide");
		}

		/*Hide Remove Filters button*/
		if(!$("#removeFilterBtn").hasClass("hide")) {
			$("#removeFilterBtn").addClass("hide");
		}

		/*Call the resetVariables function to reset all global variables*/
		advSearch_self.resetVariables();
		
		/*Click The Refresh Button*/
		$("#resetFilters").click();		
	};

	/**
	 * This function reset all variable used in the process
	 * @class advanceSearchLib
	 * @method resetVariables
	 */
	this.resetVariables = function() {

		/*Reset the variable*/
		filtersInfoArray = [];
		templateData = "";
		formElements = "";
		elementsArray = [];
		resultantObject = {};		
		searchParameters = "";
	};
}