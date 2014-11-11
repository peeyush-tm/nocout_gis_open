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

            if(filtersInfoArray[i] != null) {

                formElements += '<div class="form-group"><label for="'+filtersInfoArray[i].key+'" class="col-sm-4 control-label">';
                formElements += filtersInfoArray[i].title;
                formElements += '</label><div class="col-sm-8">';

                var currentKey = $.trim(filtersInfoArray[i].key);
                var elementType = $.trim(filtersInfoArray[i].element_type);
                /*Check Element Type*/
                if(elementType == "multiselect") {

                    var filterValues = filtersInfoArray[i].values;
                    // if(filterValues.length > 0) {

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
                    // } else {

                    //     formElements += '<input type="text" id="filter_'+filtersInfoArray[i].key+'" name="'+filtersInfoArray[i].key+'"  class="form-control"/>';
                    // }
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

	/**
	 * This method generates get parameter for setfilter API & call setFilter function
	 * @method callSetFilter
	 */
	this.callSetFilter = function() {
        appliedAdvFilter=[];
        val_final=[];
		for(var j=0;j<filtersInfoArray.length;j++) {

			var elementType = $.trim(filtersInfoArray[j].element_type),
				selectId = filtersInfoArray[j].key;
			/*Check Element Type*/
			if(elementType == "multiselect") {
	            var val = $("#filter_"+selectId).select2("val");
                if(val.length > 0) {
                    for(var k=0; k<val.length; k++) {
                        if( val[k].indexOf(',')>=0) {
                          appliedAdvFilter.push({'selectId':selectId, 'ids': val[k].split(',')})
                        } else {
                          appliedAdvFilter.push({'selectId':selectId, 'ids': val[k] })
                        }
                    }
                }
                appliedAdvFilter_Active.push({ 'field':selectId, 'value':val });
            }
        }

        var search_options= ['technology','vendor', 'city', 'state'];
        city_search_bs_ids =[];
        state_search_bs_ids=[];
        technology_search_bs_ids=[];
        vendor_search_bs_ids=[];
        
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
		    if(result_ids && result_ids.length > 0) {
		    	result_ids = JSON.stringify(result_ids);
			    advSearch_self.setFilters(result_ids, 'depth' );
		    }
        }else{

        	if(result_ids && result_ids.length > 0) {
        		result_ids = JSON.stringify(result_ids);
			    advSearch_self.setFilters(result_ids, 'direct' );
        	}
        }

		/*Hide the spinner*/
        hideSpinner();

		if(result_ids && result_ids.length > 0) {

	        /*Call the tp plot result of the devices to plot*/
	        advSearch_self.result_plotting();
	        
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
		} else {
			bootbox.alert("Please select any filter");
		}

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
		/*Show Remove Filters button*/
		if($("#removeFilterBtn").hasClass("hide")) {
			$("#removeFilterBtn").removeClass("hide");
		}

		var current_data_array = [];

		if(window.location.pathname.indexOf("googleEarth") > -1) {
			current_data_array = main_devices_data_earth;
		} else if (window.location.pathname.indexOf("white_background") > -1) { 
			current_data_array = main_devices_data_wmap;
		}else {
			current_data_array = main_devices_data_gmaps;
		}

        searchString=JSON.parse(searchString);

        if (search_type=='direct'){

            loop1:
                for(var i= 0;searchString.length>i;i++){
            loop2:
                    for(var j= 0;current_data_array.length>j;j++){

                        if (searchString[i]== current_data_array[j].id) {
                        	result_plot_devices.push(current_data_array[j])
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
        loop1:
            for (var i=0; i<searchString.length; i++)
            {
            loop2:
                for(var j= 0;current_data_array.length>j;j++)
                {
                    if (searchString[i]== current_data_array[j].id)
                    {
                        /*Deep Copy of the current_data_array*/
                        var result_plot_data= $.extend( true, {}, current_data_array[j] );
                        result_plot_data.data.param.sector=[];
                    loop3:
                        for(var k=0; k<current_data_array[j].data.param.sector.length;k++)
                        {
                            technology_check_condition= technology_choice.length>0 ? technology_choice.indexOf(current_data_array[j].data.param.sector[k].technology)>=0 : true;
                            /*If vendor choice exist then check in the sector, if the vendor_choice is null then make it true by default to check the technology condition.*/
                            vendor_check_condition= vendor_choice.length>0 ? vendor_choice.indexOf(current_data_array[j].data.param.sector[k].vendor)>=0 : true;

                            /*And the condition when technology_check_condition and vendor_check_condition will become true and their
                            length is also zero.Then they will not appear in the depth search. */

                            /*Condition to check both the technology and vendor are present in the sector.*/
                            if( technology_check_condition && vendor_check_condition)
        //                      || sector_configured_on_choice.indexOf(current_data_array[i].data.param.sector[j].sector_configured_on) >=0
        //                      || circuit_ids_choice.indexOf(current_data_array[i].data.param.sector[j].circuit_id) >=0)
                            {
                                result_plot_data.data.param.sector= result_plot_data.data.param.sector.concat(current_data_array[j].data.param.sector[k])
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

//        if(window.location.pathname.indexOf("googleEarth") == -1) {
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
//                clusterIcon = base_url+"/"+result.data.objects.data.unspiderfy_icon;
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
//                clusterIcon = base_url+"/"+result.data.objects.data.unspiderfy_icon;
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

    this.result_plotting= function() {
        
        if(window.location.pathname.indexOf("googleEarth") > -1) {

        	/*Save filtered data in global variable*/
			data_for_filters_earth = result_plot_devices;

        	/*Clear all the elements from google earth*/
	        earth_instance.clearEarthElements();

	        /*Reset Global Variables & Filters*/
	        earth_instance.resetVariables_earth();

	        /*create the BS-SS network on the google earth*/
	        earth_instance.plotDevices_earth(data_for_filters_earth,"base_station");

        } else if (window.location.pathname.indexOf("white_background") > -1) { 

        		showWmapFilteredData(result_plot_devices);

        } else {

	        /*Create a instance of networkMapClass*/
	        gmapInstance = new devicePlottingClass_gmap();

	  //       /*Reset markers, polyline & filters*/
	  //       gmapInstance.clearGmapElements();

	  //       /*Reset Global Variables & Filters*/
	  //       gmapInstance.resetVariables_gmap();

			// /*Call plotDevices_gmap to plot filtered devices on google map*/
	  //       gmapInstance.plotDevices_gmap(result_plot_devices,"base_station");



	        /*Save filtered data in global variable*/
			data_for_filters = result_plot_devices;

			gmapInstance.showHideMarkers_gmap(data_for_filters);

	        /*Filter Line & label array as per filtered data*/
	        gmapInstance.getFilteredLineLabel(data_for_filters);
        }

        //Intilaizing value to Null
        result_plot_devices=[];
    }


	this.removeFilters = function() {
		
		/*Reset filter data array*/
		lastSelectedValues = [];
		appliedAdvFilter = [];
		appliedAdvFilter_Active = [];
        result_plot_device=[]

        if(!($("#advFilterContainerBlock").hasClass("hide"))) {
			$("#advFilterContainerBlock").addClass("hide");
		}

		/*Hide Remove Filters button*/
		if(!$("#removeFilterBtn").hasClass("hide")) {
			$("#removeFilterBtn").addClass("hide");
		}

        // Not to clear the html for gmap page
        if(window.location.pathname.indexOf("googleEarth") > -1) {
	        $("#advFilterFormContainer").html("");
	    } else if(window.location.pathname.indexOf("white_background") > -1) {
	        $("#advFilterFormContainer").html("");
	    } else {
	    	$("#filter_technology").select2("val","");
	    	$("#filter_vendor").select2("val","");
	    	$("#filter_state").select2("val","");
	    	$("#filter_city").select2("val","");
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