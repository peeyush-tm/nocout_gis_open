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
    appliedAdvFilter_Active = [],
    searchParameters = "",
    lastSelectedValues = [];
    searchquery_data=[];
    result_plot_devices=[];
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
console.log(filtersInfoArray);
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

				/*Hide the spinner*/
                hideSpinner();
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

		        /*Hide the spinner*/
                hideSpinner();
			}
		});
	};

    this.getFilterInfofrompagedata = function( domElemet, windowTitle, buttonId){

        filtersInfoArray= prepare_data_for_filter();

        if(appliedAdvFilter_Active.length != 0) {
			lastSelectedValues = appliedAdvFilter_Active;
		}

        var templateData = "", elementsArray = [];
        templateData += '<div class="iframe-container"><div class="content-container"><div id="'+domElemet+'" class="advanceFiltersContainer">';
        templateData += '<form id="'+domElemet+'_form"><div class="form-group form-horizontal">';

        formElements = "";
        /*Reset the appliedAdvFilter*/
        appliedAdvFilter = [];
        appliedAdvFilter_Active = [];

        for(var i=0;i<filtersInfoArray.length;i++) {
console.log(lastSelectedValues);
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

                                    formElements += '<option value="'+filterValues[j].value+'">'+filterValues[j].value+'</option>';
                                }
                            }
                        } else {

                            for(var j=0;j<filterValues.length;j++) {

                                if(($.trim(filterValues[j].id) != null && $.trim(filterValues[j].value) != null) && ($.trim(filterValues[j].id) != "" && $.trim(filterValues[j].value) != "")) {

                                    formElements += '<option value="'+filterValues[j].id+'">'+filterValues[j].value+'</option>';
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
    /*Hide the spinner*/
    hideSpinner();

    };

//    this.get_device_ids_by_choice_type= function(choice, type)
//                        {
//                            choice_type_device_ids_list=[];
//                            var searchquery_data=[];
////                                main_devices_data_gmaps;
//                            for (var q=0;q<searchquery_data.length; q++)
//                                {
//                                    /*If the baststation object sector length is Zero then remove it from the searchquery_data.*/
//                                    if(searchquery_data.data.param.sector.length ==0 )
//                                        {
//                                           searchquery_data.shift();
//                                        }
//                                    else
//                                    {
//                                        for (var m =0; m<searchquery_data[q].data.param.sector.length; m++)
//                                        {
//                                            for (var n=0; n<choice.length; n++)
//                                            {
//                                                if(type=='technology')
//                                                {
//                                                    /*Removing the sectors which does not match the technology choice in searchquery_data*/
//                                                    if(choice[n] != searchquery_data[q].data.param.sector[m].technology)
//                                                        {
//                                                           searchquery_data.data.param.sector[m].pop()
//                                                        }
//                                                }
//                                                else if (type=='vendor')
//                                                {
//                                                    /*Removing the sectors which does not match the vendor choice in searchquery_data*/
//                                                    if(choice[n] != searchquery_data[q].data.param.sector[m].vendor)
//                                                        {
//                                                           searchquery_data.data.param.sector[m].pop()
//                                                        }
//                                                }
//                                                else if (type=='sector_configured_on')
//                                                {
//                                                    /*Removing the sectors which does not match the sector_configured_on choice in searchquery_data*/
//                                                    if(choice[n] != searchquery_data[q].data.param.sector[m].sector_configured_on)
//                                                        {
//                                                           searchquery_data.data.param.sector[m].pop()
//                                                        }
//                                                }
//                                                else if (type=='circuit_ids')
//                                                {
//                                                    /*Removing the sectors which does not match the circuit_ids choice in searchquery_data*/
//                                                    if(choice[n] != searchquery_data[q].data.param.sector[m].circuit_ids)
//                                                        {
//                                                           searchquery_data.data.param.sector[m].pop()
//                                                        }
//                                                }
//                                            }
//                                            /*If basestation sector length become Zero after removing the
//                                            non choice sectors then delete the basestation object in the searchquery_data*/
//                                            if(searchquery_data.data.param.sector.length ==0 )
//                                            {
//                                               searchquery_data.shift();
//                                            }
//                                        }
//                                   }
//                                }
//                                for (var n=0;n<searchquery_data.data.length; n++)
//                                {
//                                   choice_type_device_ids_list.push(searchquery_data.id)
//                                }
//                        return choice_type_device_ids_list
//                        };
	/**
	 * This method generates get parameter for setfilter API & call setFilter function
	 * @method callSetFilter
	 */
	this.callSetFilter = function() {
        appliedAdvFilter=[];
        val_final=[];
		for(var j=0;j<filtersInfoArray.length;j++) {
//			var resultantObject = {};

			var elementType = $.trim(filtersInfoArray[j].element_type);
			var selectId = filtersInfoArray[j].key;
			/*Check Element Type*/
			if(elementType == "multiselect") {
				            var val = $("#filter_"+selectId).select2("val");
                            if(val.length > 0)
                            {
                                for(var k=0; k<val.length; k++)
                                {
                                    if( val[k].indexOf(',')>=0)
                                    {
                                      appliedAdvFilter.push({'selectId':selectId, 'ids': val[k].split(',')})
                                    }
                                    else
                                    {
                                      appliedAdvFilter.push({'selectId':selectId, 'ids': val[k] })
                                    }
                                }
                            }
                    appliedAdvFilter_Active.push({ 'field':selectId, 'value':val });
		            }}
//			else if(elementType == "select") {
//
//				var selectedVal = $("#filter_"+selectId).select2("val");
//
//				if(selectedVal.length > 0) {
//
//					resultantObject["field"] = selectId;
//					resultantObject["value"] = selectedVal;
//				}
//			} else if(elementType == "checkbox") {
//
//				var checkboxArray = [];
//
//				for(var k=0;k<filtersInfoArray[j].values.length;k++) {
//
//					if($("#checkbox_"+filtersInfoArray[j].values[k].id)[0].checked == true) {
//
//						checkboxArray.push($("#checkbox_"+filtersInfoArray[j].values[k].id)[0].value);
//					}
//				}
//
//				if(checkboxArray.length > 0) {
//
//					resultantObject["field"] = filtersInfoArray[j].key;
//					resultantObject["value"] = checkboxArray;
//				}
//			} else if(elementType == "radio") {
//
//				var radioArray = [];
//
//				for(var k=0;k<filtersInfoArray[j].values.length;k++) {
//
//					if($("#radio_"+filtersInfoArray[j].values[k].id)[0].checked == true) {
//
//						radioArray.push($("#radio_"+filtersInfoArray[j].values[k].id)[0].value)
//					}
//				}
//
//				if(radioArray.length > 0) {
//
//					resultantObject["field"] = filtersInfoArray[j].key;
//					resultantObject["value"] = radioArray;
//				}
//			} else {
//
//				var typedText = $("#filter_"+selectId).val();
//
//				if(typedText.length > 0) {
//
//					resultantObject["field"] = selectId;
//					resultantObject["value"] = typedText;
//				}
//			}

//			if(resultantObject.field != undefined) {
//
//				appliedAdvFilter.push(resultantObject);
//			}
        var search_options= ['technology','vendor', 'city', 'state'];
        city_search_bs_ids =[];
        state_search_bs_ids=[];
        technology_search_bs_ids=[];
        vendor_search_bs_ids=[];
//        var direct_search_bs_ids= [];
//        var depth_search_bs_ids= [];
        for(var a=0; a<appliedAdvFilter.length; a++)
        {
            if(appliedAdvFilter[a].selectId == search_options[2])
            {
                city_search_bs_ids= city_search_bs_ids.concat(appliedAdvFilter[a].ids)
            }
            else if(appliedAdvFilter[a].selectId == search_options[3])
            {
                state_search_bs_ids= state_search_bs_ids.concat(appliedAdvFilter[a].ids)

            }else if(appliedAdvFilter[a].selectId == search_options[0])
            {
                technology_search_bs_ids= technology_search_bs_ids.concat(appliedAdvFilter[a].ids)

            }else if(appliedAdvFilter[a].selectId == search_options[1])
            {
                vendor_search_bs_ids= vendor_search_bs_ids.concat(appliedAdvFilter[a].ids)
            }
        }
        var total_ids_list=[];

        function total_ids(array_ids){
            if (array_ids.length>0){
                total_ids_list.push(array_ids)
            }
        }

        total_ids(city_search_bs_ids);
        total_ids(state_search_bs_ids);
        total_ids(technology_search_bs_ids);
        total_ids(vendor_search_bs_ids);

        /*Taking out the intersection of all the ids available from the search option.*/
        function containsAll() {
            var output = [];
            var cntObj = {};
            var array, item, cnt;
            // for each array passed as an argument to the function
            for (var i = 0; i < arguments.length; i++) {
                array = arguments[i];
                // for each element in the array
                for (
                    var j = 0; j < array.length; j++) {
                    item = "-" + array[j];
                    cnt = cntObj[item] || 0;
                    // if cnt is exactly the number of previous arrays,
                    // then increment by one so we count only one per array
                    if (cnt == i) {
                        cntObj[item] = cnt + 1;
                    }
                }
            }
            // now collect all results that are in all arrays
            for (item in cntObj) {
                if (cntObj.hasOwnProperty(item) && cntObj[item] === arguments.length) {
                    output.push(item.substring(1));
                }
            }
            return(output);
        }
        var result_ids = containsAll.apply(this, total_ids_list);

        if (technology_search_bs_ids.length>0 || vendor_search_bs_ids.length){
		    result_ids = JSON.stringify(result_ids);
		    advSearch_self.setFilters(result_ids, 'depth' );
        }else{
            result_ids = JSON.stringify(result_ids);
		    advSearch_self.setFilters(result_ids, 'direct' );
        }


//        /*Unique Direct Search Ids*/
//        direct_search_bs_ids= advSearch_self.unique_list(direct_search_bs_ids);
//        /*Unique Depth Search Ids*/
//        depth_search_bs_ids= advSearch_self.unique_list(depth_search_bs_ids);
//
//
//        /* Intersection of BS ids. The advance filters are in 'AND' condition.
//        So there by calculating intersection between two arrays */
//        /*If the direct search id is empty then the intersection between them will bw empty array.*/
//        if( direct_search_bs_ids.length>0 ){
//           depth_search_bs_ids= $(direct_search_bs_ids).filter(depth_search_bs_ids);
//        }
//
////        if (depth_search_bs_ids.length>0){
////            depth_search_bs_ids= (direct_search_bs_ids).concat(depth_search_bs_ids);
////            depth_search_bs_ids= advSearch_self.unique_list(depth_search_bs_ids);
////        }
//
////        appliedAdvFilter= advSearch_self.unique_list(appliedAdvFilter);
//		/*Stringify the object array to pass it in the query parameters for in set filter API*/
//
//		/*call the setFilters function with the search parameters & setFilters API url*/
//        if (depth_search_bs_ids.length>0){
//		    depth_search_bs_ids = JSON.stringify(depth_search_bs_ids);
//		    advSearch_self.setFilters(depth_search_bs_ids, 'depth' );
//        }else if(direct_search_bs_ids.length>0){
//            direct_search_bs_ids = JSON.stringify(direct_search_bs_ids);
//		    advSearch_self.setFilters(direct_search_bs_ids, 'direct' );
//        }




        /*Call the tp plot result of the devices to plot*/
         advSearch_self.result_plotting();
            /*Call the reset function*/

         advSearch_self.resetVariables();

         /*Hide the spinner*/
        hideSpinner();
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


    this.unique_list= function(list){
                                  var result_list = [];
                                  $.each(list, function(i, e) {
                                    if ($.inArray(e, result_list) == -1) result_list.push(e);
                                  });
                                  return result_list;
                            };

	/**
	 * This function call the set filter api & as the response pass the devices to the devicePlottingLib
	 * @method setFilters
	 * @param searchString "String" It is the query string passed to the API
	 * @param setFilterApi "String" It is the URL of the set filter API
	 */

	this.setFilters = function(searchString, search_type) {
        console.log(searchString);
		/*Show Remove Filters button*/
		if($("#removeFilterBtn").hasClass("hide")) {
			$("#removeFilterBtn").removeClass("hide");
		}
        searchString=JSON.parse(searchString);

        if (search_type=='direct'){

            loop1:
                for(var i= 0;searchString.length>i;i++){
            loop2:
                    for(var j= 0;main_devices_data_gmaps.length>j;j++){

                        if (searchString[i]== main_devices_data_gmaps[j].id){
                        result_plot_devices.push(main_devices_data_gmaps[j])
                        break loop2
                        }
                    }
                }
        }else if(search_type='depth')
        {
            var technology_choice=''
            $.each($('#s2id_filter_technology').select2('data'), function( index, value ){ technology_choice+=value.text })
            var vendor_choice= ''
            $.each($('#s2id_filter_vendor').select2('data'), function( index, value ){ vendor_choice+=value.text })
//            var sector_configured_on_choice= ''
//            $.each($('#s2id_filter_sector_configured_on').select2('data'), function( index, value ){ sector_configured_on_choice+=value.text })
//            var circuit_ids_choice= ''
//            $.each($('#s2id_filter_circuit_ids').select2('data'), function( index, value ){ circuit_ids_choice+=value.text })
            console.log(technology_choice, vendor_choice);
        loop1:
            for (var i=0; i<searchString.length; i++)
            {
            loop2:
                for(var j= 0;main_devices_data_gmaps.length>j;j++)
                {
                    if (searchString[i]== main_devices_data_gmaps[j].id)
                    {
                        /*Deep Copy of the main_devices_data_gmaps*/
                        var result_plot_data= $.extend( true, {}, main_devices_data_gmaps[j] );
                        result_plot_data.data.param.sector=[];
                    loop3:
                        for(var k=0; k<main_devices_data_gmaps[j].data.param.sector.length;k++)
                        {
                            technology_check_condition= technology_choice.length>0 ? technology_choice == main_devices_data_gmaps[j].data.param.sector[k].technology: true;
                            /*If vendor choice exist then check in the sector, if the vendor_choice is null then make it true by default to check the technology condition.*/
                            vendor_check_condition= vendor_choice.length>0 ? vendor_choice == main_devices_data_gmaps[j].data.param.sector[k].vendor: true;

                            /*And the condition when technology_check_condition and vendor_check_condition will become true and their
                            length is also zero.Then they will not appear in the depth search. */

                            /*Condition to check both the technology and vendor are present in the sector.*/
                            if( technology_check_condition && vendor_check_condition)
        //                      || sector_configured_on_choice.indexOf(main_devices_data_gmaps[i].data.param.sector[j].sector_configured_on) >=0
        //                      || circuit_ids_choice.indexOf(main_devices_data_gmaps[i].data.param.sector[j].circuit_id) >=0)
                            {
                                result_plot_data.data.param.sector= result_plot_data.data.param.sector.concat(main_devices_data_gmaps[j].data.param.sector[k])
                            }
                        }
                        /*If any relevant sector according to search condition is found then appending (BS with Sector-SS) to the result.*/
                        if(result_plot_data.data.param.sector.length !=0)
                        {
                            result_plot_devices.push(result_plot_data)
                        }

                    break loop2
                    }// if condition closed.
                }
            }
        }
        /*Reset The basic filters dropdown*/
        $("#technology").val($("#technology option:first").val());
        $("#vendor").val($("#vendor option:first").val());
        $("#state").val($("#state option:first").val());
        $("#city").val($("#city option:first").val());

//        if(window.location.pathname.indexOf("google_earth") == -1) {
//
//            /*Create a instance of networkMapClass*/
//            gmapInstance = new devicePlottingClass_gmap();
//
//            /*Reset markers, polyline & filters*/
//            gmapInstance.clearGmapElements();
//
//            /*Reset Global Variables & Filters*/
//            gmapInstance.resetVariables_gmap();
//
//            /*If cluster icon exist then save it to global variable else make the global variable blank*/
//            if(result.data.objects.data.unspiderfy_icon == undefined) {
//                clusterIcon = "";
//            } else {
//                clusterIcon = window.location.origin+"/"+result.data.objects.data.unspiderfy_icon;
//            }
//
//            /*Call the make network to create the BS-SS network on the google map*/
//            gmapInstance.plotDevices_gmap(result.data.objects.children,"base_station");
//
//        } else {

            /*Create a instance of networkMapClass*/
//            gmapInstance = new devicePlottingClass_gmap();

            /*Reset markers, polyline & filters*/
//            gmapInstance.clearGmapElements();

            /*Reset Global Variables & Filters*/
//            gmapInstance.resetVariables_gmap();

            /*If cluster icon exist then save it to global variable else make the global variable blank*/
//            if(result.data.objects.data.unspiderfy_icon == undefined) {
//                clusterIcon = "";
//            } else {
//                clusterIcon = window.location.origin+"/"+result.data.objects.data.unspiderfy_icon;
//            }

            /*Call the make network to create the BS-SS network on the google map*/
//            for( var a=0; a<result_plot_devices.length; a++){

//            gmapInstance.plotDevices_gmap(result_plot_devices,"base_station");
            //Intilaizing value to Null
//            result_plot_devices=[];
//            }
            /************** GOOGLE EARTH CODE*********************/
            /*Create a instance of googleEarthClass*/
            // earthInstance = new googleEarthClass();

            /*Clear all the elements from google earth*/
            // earthInstance.clearEarthElements();

            /*Reset Global Variables & Filters*/
            // earthInstance.resetVariables_earth();

            /*create the BS-SS network on the google map*/
            // earthInstance.plotDevices_earth(result.data.objects.children,"base_station");
//        }

//    else {
//
//        $.gritter.add({
//            // (string | mandatory) the heading of the notification
//            title: 'Advance Filters - No Records',
//            // (string | mandatory) the text inside the notification
//            text: result.message,
//            // (bool | optional) if you want it to fade out on its own or just sit there
//            sticky: true
//        });
//
//        /*hide The loading Icon*/
//        $("#loadingIcon").hide();
//
//        /*Enable the refresh button*/
//        $("#resetFilters").button("complete");
//
//        $("#removeFilterBtn").click();
//    }


    };
//			},
//			error : function(err) {
//
//				// console.log(err.statusText);
//				$.gritter.add({
//		            // (string | mandatory) the heading of the notification
//		            title: 'Advance Filters - Error',
//		            // (string | mandatory) the text inside the notification
//		            text: err.statusText,
//		            // (bool | optional) if you want it to fade out on its own or just sit there
//		            sticky: true
//		        });
//
//		        /*hide The loading Icon*/
//				$("#loadingIcon").hide();
//
//				/*Enable the refresh button*/
//				$("#resetFilters").button("complete");
//
//				/*Hide the spinner*/
//                hideSpinner();
//			}
//		});
//	};

	/**
	 * This function remove the applied filter n show default or un-filtered values
	 * @class advanceSearchLib
	 * @method removeFilters
	 */

    this.result_plotting= function(){
                    /*Create a instance of networkMapClass*/
            gmapInstance = new devicePlottingClass_gmap();

            /*Reset markers, polyline & filters*/
            gmapInstance.clearGmapElements();

            /*Reset Global Variables & Filters*/
            gmapInstance.resetVariables_gmap();

            /*If cluster icon exist then save it to global variable else make the global variable blank*/
//            if(result.data.objects.data.unspiderfy_icon == undefined) {
//                clusterIcon = "";
//            } else {
//                clusterIcon = window.location.origin+"/"+result.data.objects.data.unspiderfy_icon;
//            }

            /*Call the make network to create the BS-SS network on the google map*/
//            for( var a=0; a<result_plot_devices.length; a++){

            gmapInstance.plotDevices_gmap(result_plot_devices,"base_station");
            //Intilaizing value to Null
            result_plot_devices=[];


    }


	this.removeFilters = function() {

		/*Reset filter data array*/
		lastSelectedValues = [];
		appliedAdvFilter = [];
		appliedAdvFilter_Active = [];
        result_plot_device=[]
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
