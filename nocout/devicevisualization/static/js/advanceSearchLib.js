/*Global Variables*/
var that = "",
	filtersInfoArray = [],
	templateData = "",
	formElements = "",
	elementsArray = [],
	resultantObject = {},
	resultantObjectArray = [];

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
	 * @param getApiUrl "String" It is the url of the get_filter API
	 * @param setApiUrl "String" It is the url of the set_filter API
	 */
	this.getFilterInfo = function(domElemet,windowTitle,getApiUrl,setApiUrl)
	{
		/*To Enable The Cross Domain Request*/
		$.support.cors = true;

		// $.getJSON(getApiUrl,function(result) {
		$.ajax({

			crossDomain: true,
			url : getApiUrl,
			type : "GET",
			dataType : "json",
			/*If data fetched successful*/
			success : function(result)
			{
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

							var elementType = $.trim(filtersInfoArray[i].element_type);
							/*Check Element Type*/
							if(elementType == "multiselect")
							{
								var filterValues = filtersInfoArray[i].values;
								if(filterValues.length > 0)
								{
									formElements += '<select multiple class="multiSelectBox col-md-12" id="'+filtersInfoArray[i].key+'">';

									for(var j=0;j<filterValues.length;j++)
									{
										formElements += '<option value="'+filterValues[j].id+'">'+filterValues[j].value+'</option>';
									}

									formElements += '</select>';
								}
								else
								{
									formElements += '<input type="text" id="'+filtersInfoArray[i].key+'" name="'+filtersInfoArray[i].key+'"  class="form-control"/>';
								}
							}
							else if(elementType == "select")
							{
								var filterValues = filtersInfoArray[i].values;
								if(filterValues.length > 0)
								{
									formElements += '<select class="multiSelectBox col-md-12" id="'+filtersInfoArray[i].key+'">';

									for(var j=0;j<filterValues.length;j++)
									{
										formElements += '<option value="'+filterValues[j].id+'">'+filterValues[j].value+'</option>';
									}

									formElements += '</select>';
								}
								else
								{
									formElements += '<input type="text" id="'+filtersInfoArray[i].key+'" name="'+filtersInfoArray[i].key+'"  class="form-control"/>';
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
									formElements += '<input type="text" id="'+filtersInfoArray[i].key+'" name="'+filtersInfoArray[i].key+'"  class="form-control"/>';
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
									formElements += '<input type="text" id="'+filtersInfoArray[i].key+'" name="'+filtersInfoArray[i].key+'"  class="form-control"/>';
								}

							}
							else
							{
								formElements += '<input type="text" id="'+filtersInfoArray[i].key+'" name="'+filtersInfoArray[i].key+'"  class="form-control"/>';
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
						title: '<i class="fa fa-search">&nbsp;</i> '+windowTitle,
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
											var val = $("#"+selectId).select2("val");
											if(val.length > 0)
											{
												resultantObject["field"] = selectId;
												resultantObject["values"] = $("#"+selectId).select2("val");
											}
										}
										else if(elementType == "select")
										{
											var selectedVal = $("#"+selectId).select2("val");
											if(selectedVal.length > 0)
											{
												resultantObject["field"] = selectId;
												resultantObject["values"] = selectedVal;
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
												resultantObject["values"] = checkboxArray;
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
												resultantObject["values"] = radioArray;
											}
										}
										else
										{
											var typedText = $("#"+selectId).val();
											if(typedText.length > 0)
											{
												resultantObject["field"] = selectId;
												resultantObject["values"] = typedText;
											}
										}

										if(resultantObject.field != undefined)
										{
											resultantObjectArray.push(resultantObject);
										}									
									}

									console.log(resultantObjectArray);
								}
							},
							danger: {
								label: "Cancel",
								className: "btn-warning",
								callback: function() {
									console.log("Cancel")
								}
							}
						}
					});

					/*Initialize the select2*/
					$(".advanceFiltersContainer select").select2();
				}
				else
				{
					console.log(result.message);
				}
			},
			/*If data not fetched*/
			error : function(err)
			{
				console.log(err.statusText);
			}
		});		
	}
}