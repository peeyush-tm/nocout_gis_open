/*Global Variables*/
var that = "",
	filtersInfoArray = [],
	templateData = "",
	formElements = "",
	elementsArray = [],
	resultantObject = {},
	resultantObjectArray = [],
	searchParameters = "";

/**
 * This class is used to create th filter form by calling the get_filter API & the call the set_filter API with the selected filters
 * @class advanceSearchClass
 * @uses jQuery
 * Coded By :- Yogender Purohit
 */
function advanceSearchClass()
{
	/*Store the reference of current pointer in a global variable*/
	that = this;

	/**
	 * This function first get the filters object from the server, create the filters HTML struction & then populate the HTML in the popup
	 * @function getFilterInfo
	 * @class advanceSearchClass
	 * @param domElement "String" It is dom element.
	 * @param windowTitle "String" It is title of the popup
	 * @param buttonId "String" It is the dom selector or ID of the clicked button.
	 * @param getApiUrl "String" It is the url of the get_filter API
	 * @param setApiUrl "String" It is the url of the set_filter API
	 */
	this.getFilterInfo = function(domElemet,windowTitle,buttonId,getApiUrl,setApiUrl)
	{
		/*Change the text of the button to "Please Wait..." & disable the button*/
		$("#"+buttonId).button("loading");
		
		/*To Enable The Cross Domain Request*/
		$.support.cors = true;

		$.ajax({

			crossDomain: true,
			url : getApiUrl,
			// url : "http://192.168.0.19:8000/gis/get_filters/",
			type : "GET",
			dataType : "json",
			/*If data fetched successful*/
			success : function(result)
			{
				/*Revert the button to the initial state*/
				$("#"+buttonId).button("complete");

				/*If data fetch successfully*/
				if(result.success == 1)
				{
					templateData = "";
					elementsArray = [];

					filtersInfoArray = result.data.objects;

					templateData += '<div id="'+domElemet+'" class="col-md-12 advanceFiltersContainer">';
					templateData += '<form id="'+domElemet+'_form"><div class="form-group form-horizontal">';

					formElements = "";

					for(var i=0;i<filtersInfoArray.length;i++)
					{
						if(filtersInfoArray[i] != null)
						{
							formElements += '<div class="form-group"><label for="'+filtersInfoArray[i].key+'" class="col-sm-3 control-label">';
							formElements += filtersInfoArray[i].title;
							formElements += '</label><div class="col-sm-8">';

							var currentKey = $.trim(filtersInfoArray[i].key);
							var elementType = $.trim(filtersInfoArray[i].element_type);
							/*Check Element Type*/
							if(elementType == "multiselect")
							{
								var filterValues = filtersInfoArray[i].values;
								if(filterValues.length > 0)
								{
									formElements += '<select multiple class="multiSelectBox col-md-12" id="filter_'+filtersInfoArray[i].key+'">';

									/*Condition for mapped tables to pass the ID in the values else pass the value*/
									if(currentKey == "device_group" || currentKey == "device_type" || currentKey == "device_technology" || currentKey == "device_vendor")
									{
										for(var j=0;j<filterValues.length;j++)
										{
											if(($.trim(filterValues[j].id) != null && $.trim(filterValues[j].value) != null) && ($.trim(filterValues[j].id) != "" && $.trim(filterValues[j].value) != ""))
											{
												formElements += '<option value="'+filterValues[j].id+'">'+filterValues[j].value+'</option>';
											}
										}	
									}
									else
									{
										for(var j=0;j<filterValues.length;j++)
										{
											if(($.trim(filterValues[j].id) != null && $.trim(filterValues[j].value) != null) && ($.trim(filterValues[j].id) != "" && $.trim(filterValues[j].value) != ""))
											{
												formElements += '<option value="'+filterValues[j].value+'">'+filterValues[j].value+'</option>';
											}											
										}
									}

									formElements += '</select>';
								}
								else
								{
									formElements += '<input type="text" id="filter_'+filtersInfoArray[i].key+'" name="'+filtersInfoArray[i].key+'"  class="form-control"/>';
								}
							}
							else if(elementType == "select")
							{
								var filterValues = filtersInfoArray[i].values;
								if(filterValues.length > 0)
								{
									formElements += '<select class="multiSelectBox col-md-12" id="filter_'+filtersInfoArray[i].key+'">';

									for(var j=0;j<filterValues.length;j++)
									{
										formElements += '<option value="'+filterValues[j].id+'">'+filterValues[j].value+'</option>';
									}

									formElements += '</select>';
								}
								else
								{
									formElements += '<input type="text" id="filter_'+filtersInfoArray[i].key+'" name="'+filtersInfoArray[i].key+'"  class="form-control"/>';
								}
							}
							else if(elementType == "radio")
							{
								var filterValues = filtersInfoArray[i].values;
								if(filterValues.length > 0)
								{
									for(var j=0;j<filterValues.length;j++)
									{
										formElements += '<label class="radio-inline"><input type="radio" id="'+filterValues[j].id+'" value="'+filterValues[j].id+'" name="'+filtersInfoArray[i].key+'"> '+filterValues[j].value+'</label>';
									}
								}
								else
								{
									formElements += '<input type="text" id="filter_'+filtersInfoArray[i].key+'" name="'+filtersInfoArray[i].key+'"  class="form-control"/>';
								}

							}
							else if(elementType == "checkbox")
							{
								var filterValues = filtersInfoArray[i].values;
								if(filterValues.length > 0)
								{
									for(var j=0;j<filterValues.length;j++)
									{
										formElements += '<label class="checkbox-inline"><input type="checkbox" id="'+filterValues[j].id+'" value="'+filterValues[j].id+'" name="'+filterValues[j].id+'"> '+filterValues[j].value+'</label>';
									}
								}
								else
								{
									formElements += '<input type="text" id="filter_'+filtersInfoArray[i].key+'" name="'+filtersInfoArray[i].key+'"  class="form-control"/>';
								}

							}
							else
							{
								formElements += '<input type="text" id="filter_'+filtersInfoArray[i].key+'" name="'+filtersInfoArray[i].key+'"  class="form-control"/>';
							}

							formElements += '</div></div>';
							elementsArray.push(formElements);
							formElements = "";
						}
					}

					templateData += elementsArray.join('');
					templateData += '</div><div class="clearfix"></div></form>';
					templateData += '<div class="clearfix"></div></div>';

					/*Call the bootbox to show the popup with the fetched filters*/
					bootbox.dialog({
						message: templateData,
						title: '<i class="fa fa-filter">&nbsp;</i> '+windowTitle,
						buttons: {
							success: {
								label: "Search",
								className: "btn-success",
								callback: function() {
									
									for(var j=0;j<filtersInfoArray.length;j++)
									{
										resultantObject = {};

										var elementType = $.trim(filtersInfoArray[j].element_type);
										var selectId = filtersInfoArray[j].key;

										/*Check Element Type*/
										if(elementType == "multiselect")
										{
											var val = $("#filter_"+selectId).select2("val");
											if(val.length > 0)
											{
												resultantObject["field"] = selectId;
												resultantObject["value"] = val;
											}
										}
										else if(elementType == "select")
										{
											var selectedVal = $("#filter_"+selectId).select2("val");
											if(selectedVal.length > 0)
											{
												resultantObject["field"] = selectId;
												resultantObject["value"] = selectedVal;
											}
										}
										else if(elementType == "checkbox")
										{
											var checkboxArray = [];

											for(var k=0;k<filtersInfoArray[j].values.length;k++)
											{
												if($("#"+filtersInfoArray[j].values[k].id)[0].checked == true)
												{
													checkboxArray.push($("#"+filtersInfoArray[j].values[k].id)[0].value);
												}
											}

											if(checkboxArray.length > 0)
											{
												resultantObject["field"] = filtersInfoArray[j].key;
												resultantObject["value"] = checkboxArray;
											}
										}
										else if(elementType == "radio")
										{
											var radioArray = [];

											for(var k=0;k<filtersInfoArray[j].values.length;k++)
											{
												if($("#"+filtersInfoArray[j].values[k].id)[0].checked == true)
												{
													radioArray.push($("#"+filtersInfoArray[j].values[k].id)[0].value)												
												}
											}

											if(radioArray.length > 0)
											{
												resultantObject["field"] = filtersInfoArray[j].key;
												resultantObject["value"] = radioArray;
											}
										}
										else
										{
											var typedText = $("#filter_"+selectId).val();
											if(typedText.length > 0)
											{
												resultantObject["field"] = selectId;
												resultantObject["value"] = typedText;
											}
										}

										if(resultantObject.field != undefined)
										{
											resultantObjectArray.push(resultantObject);
										}									
									}
									/*Stringify the object array to pass it in the query parameters for in set filter API*/
									searchParameters = JSON.stringify(resultantObjectArray);

									that.setFilters(searchParameters,setApiUrl);

									/*Call the reset function*/
									that.resetVariables();
								}
							},
							danger: {
								label: "Cancel",
								className: "btn-warning",
								callback: function() {
									
									/*Call the reset function*/
									that.resetVariables();
								}
							}
						}
					});

					/*Initialize the select2*/
					$(".advanceFiltersContainer select").select2();
				}
				/*If data not fetched*/
				else
				{
					console.log(result.message);
				}
			},
			/*If there is a problem in calling server*/
			error : function(err)
			{
				$("#"+buttonId).button("complete");
				console.log(err.statusText);
			}
		});		
	};

	/**
	 * This function call the set filter api & as the response pass the devices to the devicePlottingLib
	 * @class advanceSearchLib
	 * @method setFilters
	 * @param searchString "String" It is the query string passed to the API
	 * @param setFilterApi "String" It is the URL of the set filter API
	 */
	this.setFilters = function(searchString,setFilterApi)
	{
		/*To Enable The Cross Domain Request*/
		$.support.cors = true;

		$.ajax({
			crossDomain: true,
			url : setFilterApi+"?search_text='"+searchString+"'",
			// url : "http://192.168.0.19:8000/gis/set_filters/?search_text='"+searchString+"'",
			type : "GET",
			dataType : "json",
			/*If data fetched successful*/
			success : function(result)
			{
				/*If data fetch successfully*/
				if(result.success == 1)
				{
					if(result.data.objects != null)
					{
						/*Create a instance of networkMapClass*/
						var networkMapInstance = new networkMapClass();

						/*Reset markers, polyline & filters*/
				        networkMapInstance.clearMapElements();

				        /*Reset Global Variables & Filters*/
				        networkMapInstance.resetVariables();

				        /*Call the getDevicesFilter function to seperate the filter values from the object array*/
						networkMapInstance.getDevicesFilter(result.data.objects.children);

				        /*Call the make network to create the BS-SS network on the google map*/
				        networkMapInstance.populateNetwork(result.data.objects.children);
					}
				}
				else
				{
					console.log(result.message);
				}
			},
			error : function(err)
			{
				console.log(err.statusText);
			}
		});
	};

	/**
	 * This function reset all variable used in the process
	 * @class advanceSearchLib
	 * @method resetVariables
	 */
	this.resetVariables = function()
	{
		/*Reset the variable*/
		filtersInfoArray = [];
		templateData = "";
		formElements = "";
		elementsArray = [];
		resultantObject = {};
		resultantObjectArray = [];
		searchParameters = "";
	}
}