var mapPageType = "",
    hasAdvFilter = 0,
    hasSelectDevice = 0,
    hasTools = 0,
    freezedAt = 0,
    tools_ruler= "",
    tools_line = ""
    base_url = "",
    last_selected_label = "",
    current_icon_size = "medium",
    periodic_tooltip_call = "";

/*Set the base url of application for ajax calls*/
if(window.location.origin) {
    base_url = window.location.origin;
} else {
    base_url = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
}


/*Save cookie value to variable*/
isFreeze = $.cookie("isFreezeSelected") ? $.cookie("isFreezeSelected") : 0;
freezedAt = $.cookie("freezedAt") ? $.cookie("freezedAt") : 0;
tools_ruler = $.cookie("tools_ruler") ? $.cookie("tools_ruler") : 0;        
tools_line = $.cookie("tools_line") ? $.cookie("tools_line") : 0;
last_selected_label = $.cookie("tooltipLabel") ? $.cookie("tooltipLabel") : "";
current_icon_size = $.cookie("markerIconSize") ? $.cookie("markerIconSize") : "medium";

// Select the last selected item in size dropdown 
$("select#icon_Size_Select_In_Tools").val(current_icon_size);

isPollingActive = 0;

if(isFreeze == 1 || (tools_ruler && tools_ruler != 0) || (tools_line && tools_line != 0) || ($.cookie("isLabelChecked") == true || $.cookie("isLabelChecked")=='true')) {
    $("#showToolsBtn").removeClass("btn-info");
    $("#showToolsBtn").addClass("btn-warning");
} else {
    $("#showToolsBtn").addClass("btn-info");
    $("#showToolsBtn").removeClass("btn-warning");
}

// Update "Show Labels"  checkbox as per the cookie value
if($.cookie("isLabelChecked")) {
    if($.cookie("isLabelChecked") == true || $.cookie("isLabelChecked")=='true') {
        $("#show_hide_label")[0].checked= true;
    } else {
        $("#show_hide_label")[0].checked= false;
    }
}

// Update "Show All Connection Lines"  checkbox as per the cookie value
if($.cookie("isLineChecked")) {
    if($.cookie("isLineChecked") == true || $.cookie("isLineChecked")=='true') {
        $("#showConnLines")[0].checked= true;
    } else {
        $("#showConnLines")[0].checked= false;
    }
}

// Update "Show All SS"  checkbox as per the cookie value
if($.cookie("isSSChecked")) {
    if($.cookie("isSSChecked") == true || $.cookie("isSSChecked")=='true') {
        $("#showAllSS")[0].checked= true;
    } else {
        $("#showAllSS")[0].checked= false;
    }
}

if(window.location.pathname.indexOf("white_background") > -1) {
} else {
    if(google && google.maps) {
        google.maps.event.clearListeners(mapInstance,'click');
    }
    
}

// Set globl options of highcharts after 1.5 sec of page loading
setTimeout(function() {
    if(window.Highcharts) {
        Highcharts.setOptions({
            global : {
                useUTC : false
            }
        });
    }
},1500);

/*Call get_page_status function to show the current status*/
get_page_status();

/**
 * This funciton returns the page name of currenly opened page
 * @method getPageType
 */
function getPageType() {

    if(window.location.pathname.indexOf("googleEarth") > -1) {
        mapPageType = "googleEarth";
        gmap_self = networkMapInstance;
    } else if(window.location.pathname.indexOf("white_background") > -1) {
        mapPageType = "white_background";
        networkMapInstance = gmap_self;
    } else {
        mapPageType = "gmap";
    }
}

//defining global varible for city options
city_options = []

/*This event trigger when state dropdown value is changes*/
$("#state").change(function(e) {

    getPageType();

    var state_id = $(this).val(),
        state_name= $('#state option:selected').text();

    var city_array = [];
    if(state_id == "") {
        city_array = all_cities_array;
    } else {
        city_array = state_city_obj[$.trim(state_name)];
    }

    var city_option = "<option value=''> Select City</option>";
    for(var i=0;i<city_array.length;i++) {
        if(city_array[i]) {
            city_option += "<option value='"+ i+1 +"'> "+city_array[i]+"</option>";
        }
    }

    $("#city").html(city_option);

    networkMapInstance.makeFiltersArray(mapPageType);
});

/*This event trigger when city dropdown value is changes*/
$("#city").change(function(e) {
    getPageType();
    networkMapInstance.makeFiltersArray(mapPageType);
});

/*This event trigger when vendor dropdown value is changes*/
$("#vendor").change(function(e) {
    getPageType();
    networkMapInstance.makeFiltersArray(mapPageType);
});

/*This event trigger when technology dropdown value is changes*/
$("#technology").change(function(e) {

    getPageType();
    var tech_id = $(this).val(),
        tech_value= $('#technology option:selected').text();

    var vendor_array = [];
    if(tech_id == "") {
        vendor_array = all_vendor_array;
    } else {
        vendor_array = tech_vendor_obj[$.trim(tech_value)];
    }

    var vendor_option = "<option value=''> Select Vendor</option>";
    if(vendor_array) {
        for(var i=0;i<vendor_array.length;i++) {
            if(vendor_array[i]) {
                vendor_option += "<option value='"+ i+1 +"'> "+vendor_array[i]+"</option>";
            }
        }
    }

    $("#vendor").html(vendor_option);

    networkMapInstance.makeFiltersArray(mapPageType);
});


/*This event triggers when Reset Filter button clicked*/
$("#resetFilters").click(function(e) {

    var isBasicFilterApplied = $.trim($("#technology").val()) || $.trim($("#vendor").val()) || $.trim($("#state").val()) || $.trim($("#city").val())
    
    if(isBasicFilterApplied) {

        $("#resetFilters").button("loading");

        var city_option = "";
        city_option = "<option value=''>Select City</option>";

        for(var i=all_cities_array.length;i--;) {
            city_option += "<option value='"+i+1+"'>"+all_cities_array[i]+"</option>";
        }

        $("#city").html(city_option);

        var vendor_option = "";
        vendor_option = "<option value=''>Select Vendor</option>";

        for(var i=all_vendor_array.length;i--;) {
            vendor_option += "<option value='"+i+1+"'>"+all_vendor_array[i]+"</option>";
        }

        $("#vendor").html(vendor_option);

        /*Reset The basic filters dropdown*/
        $("#technology").val($("#technology option:first").val());
        $("#vendor").val($("#vendor option:first").val());
        $("#state").val($("#state option:first").val());
        $("#city").val($("#city option:first").val());
        /*Reset search txt box*/
        $("#google_loc_search").val("");
        $("#lat_lon_search").val("");
        
        isCallCompleted = 1;/*Remove this call if server call is started on click of reset button*/

        if(window.location.pathname.indexOf("googleEarth") > -1) {

            /************************Google Earth Code***********************/

            /*Clear all the elements from google earth*/
            earth_instance.clearEarthElements();
            earth_instance.clearStateCounters();

            /*Reset Global Variables & Filters*/
            earth_instance.resetVariables_earth();

            isCallCompleted = 1;

            var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);
            lookAt.setLatitude(21.0000);
            lookAt.setLongitude(78.0000);
            lookAt.setRange(6892875.865539902);
            // lookAt.setZoom
            // Update the view in Google Earth 
            ge.getView().setAbstractView(lookAt); 
            
            // mapInstance.fitBounds(new google.maps.LatLngBounds(new google.maps.LatLng(21.1500,79.0900)));
            // mapInstance.setZoom(5);
            data_for_filters_earth = all_devices_loki_db.data;

            isApiResponse = 0;
            // Load all counters
            earth_instance.showStateWiseData_earth(all_devices_loki_db.data);
        } else if(window.location.pathname.indexOf("white_background") > -1) {
            /*Reset filter object variable*/
            appliedFilterObj_wmaps = {};

            /*Clear Existing Labels & Reset Counters*/
            whiteMapClass.clearStateCounters_wmaps();

            isApiResponse = 0;
            ccpl_map.setCenter(
                new OpenLayers.LonLat(
                    whiteMapSettings.mapCenter[0],
                    whiteMapSettings.mapCenter[1]
                ),
                1,
                true,
                true
            );
            ccpl_map.zoomTo(1);
            // Load all counters
            networkMapInstance.updateStateCounter_gmaps();
        } else {

            /*Reset filter object variable*/
            appliedFilterObj_gmaps = {};
            
            /*Clear Existing Labels & Reset Counters*/
            gmap_self.clearStateCounters();
            isApiResponse = 0;
            mapInstance.fitBounds(new google.maps.LatLngBounds(new google.maps.LatLng(21.1500,79.0900)));
            mapInstance.setZoom(5);
            // Load all counters
            // gmap_self.showStateWiseData_gmap(all_devices_loki_db.data);
            networkMapInstance.updateStateCounter_gmaps();
        }
    }

    // Reset Location Search if exists
    if($("#lat_lon_search").val()) {
        $("#lat_lon_search").val("");
    }
    if(lastSearchedPt && lastSearchedPt.map) {
        lastSearchedPt.setMap(null);
        lastSearchedPt = {};
    }

    if(window.location.pathname.indexOf("white_background") > -1) {
        try {
            var lat_lon_search_layer = ccpl_map.getLayersByName('SearchMarkers');
            if(lat_lon_search_layer && lat_lon_search_layer.length > 0) {
                lat_lon_search_layer[0].clearMarkers();
                lat_lon_search_layer[0].destroy();
            }
        } catch(e) {
            // pass
        }
    }

    if($("#google_loc_search").val()) {
        $("#google_loc_search").val("");
    }

    if(place_markers && place_markers.length > 0) {
        for(var i=0;i<place_markers.length;i++) {
            if(place_markers[i] && place_markers[i].map) {
                place_markers[i].setMap(null);
            }
        }
        place_markers = [];
    }
});

function showAdvSearch() {
    showSpinner();
    // advJustSearch.getFilterInfofrompagedata("searchInfoModal", "advSearchBtn");
    if(!isAdvanceFilter) {
        $("#filter_technology").select2("val","");
        $("#filter_vendor").select2("val","");
        $("#filter_state").select2("val","");
        $("#filter_city").select2("val","");
        $("#filter_frequency").select2("val","");
        $("#filter_polarization").select2("val","");

        // Reset Advance Filters Flag
        isAdvanceFilter = 0;
    }
    if(!$("#advFilterContainerBlock").hasClass("hide")) {
        $("#advFilterContainerBlock").addClass("hide");
    }

    if($("#advSearchContainerBlock").hasClass("hide")) {
        $("#advSearchContainerBlock").removeClass("hide");
    }
    hideSpinner();
    // if (window.location.pathname.indexOf("white_background") > -1) {
    //     $("#advFilterContainerBlock").hide();
    //     $("#advSearchContainerBlock").show();
    //     advJustSearch.prepareAdvanceSearchHtml("searchInfoModal");
    // } else {
    // }
}

$("#setAdvSearchBtn").click(function(e) {
    showSpinner();
    
    var selected_bs_alias = $("#search_name").select2('val').length > 0 ? $("#search_name").select2('val').join(',').split(',') : [],
        selected_ip_address = $("#search_sector_configured_on").select2('val').length > 0 ? $("#search_sector_configured_on").select2('val').join(',').split(',') : [],
        selected_circuit_id = $("#search_circuit_ids").select2('val').length > 0 ? $("#search_circuit_ids").select2('val').join(',').split(',') : [],
        selected_bs_city = $("#search_city").select2('val').length > 0 ? $("#search_city").select2('val').join(',').split(',') : [],
        isSearchApplied = selected_bs_alias.length > 0 || selected_ip_address.length > 0 || selected_circuit_id.length > 0 || selected_bs_city.length > 0;
    // If any value is selected in searcg
    if(isSearchApplied) {

        if($("#removeSearchBtn").hasClass('hide')) {
            $("#removeSearchBtn").removeClass('hide');
        } else {
            // pass
        }
        // Set Advance Search Flag
        isAdvanceSearch = 1;
        gmap_self.advanceSearchFunc();
    } else {
        // Reset Advance Search Flag
        isAdvanceSearch = 0;
        /*Hide the spinner*/
        hideSpinner();
        bootbox.alert("Please select atleast one field.");
    }
});

$("#cancelAdvSearchBtn").click(function(e) {
    
    // if(window.location.pathname.indexOf("googleEarth") > -1) {
    //     $("#advSearchContainerBlock").addClass("hide");
    // } else if (window.location.pathname.indexOf("white_background") > -1) {
    //     $("#advFilterSearchContainerBlock").html("");
    // }

    if(!($("#advFilterSearchContainerBlock").hasClass("hide"))) {
        $("#advSearchContainerBlock").addClass("hide");
    }
    // advJustSearch.resetVariables();
});

function resetAdvanceSearch() {
    $("#resetSearchForm").trigger('click');
}

$("#resetSearchForm").click(function(e) {
    
    if(isDebug) {
        console.log("Advance Search Function")
        var start_date_reset_search = new Date();
    }

    $("#search_name").select2("val","");
    $("#search_sector_configured_on").select2("val","");
    $("#search_circuit_ids").select2("val","");
    $("#search_city").select2("val","");

    if(!$("#removeSearchBtn").hasClass('hide')) {
        $("#removeSearchBtn").addClass('hide');
    }

    if(window.location.pathname.indexOf("white_background") > -1) {
        ccpl_map.getLayersByName("Search Layer")[0].setVisibility(false);
    }

    // Reset Search data variable
    searchResultData = []
    search_element_bs_id = [];

    // Reset Advance Search Flag
    isAdvanceSearch = 0;


    advJustSearch.removeSearchMarkers();
    advJustSearch.resetVariables();
    advJustSearch.hideNotification();

    if(isDebug) {
        var time_diff = (new Date().getTime() - start_date_reset_search.getTime())/1000;
        // console.log("Update State Counters Function End Time :- "+ new Date().toLocaleString());
        console.log("Reset Advance Search Function(Return Data Case) End Time :- "+ time_diff +" Seconds");
        console.log("*******************************************");
        start_date_update_counter = "";
    }

});

/**
 * This function triggers when "Advance Filters" button is pressed
 * @method showAdvFilters
 */
function showAdvFilters() {
    /*Show the spinner*/
    showSpinner();
    if(!isAdvanceSearch) {
        resetAdvanceSearch();
    }

    if(!$("#advSearchContainerBlock").hasClass("hide")) {
        $("#advSearchContainerBlock").addClass("hide");
    }

    if($("#advFilterContainerBlock").hasClass("hide")) {
        $("#advFilterContainerBlock").removeClass("hide");
    }
    hideSpinner();
}
    
/*If 'Filter' button of advance filter is clicked*/
$("#setAdvFilterBtn").click(function(e) {

    /*Show spinner*/
    showSpinner();

    /*Reset advance filter status flag*/
    hasAdvFilter = 1;
    var filtered_data = [],
        technology_filter = $("#filter_technology").select2('val').length > 0 ? $("#filter_technology").select2('val').join(',').split(',') : [],
        vendor_filter = $("#filter_vendor").select2('val').length > 0 ? $("#filter_vendor").select2('val').join(',').split(',') : [],
        city_filter = $("#filter_city").select2('val').length > 0 ? $("#filter_city").select2('val').join(',').split(',') : [],
        state_filter = $("#filter_state").select2('val').length > 0 ? $("#filter_state").select2('val').join(',').split(',') : [],
        frequency_filter = $("#filter_frequency").select2('val').length > 0 ? $("#filter_frequency").select2('val').join(',').split(',') : [],
        polarization_filter = $("#filter_polarization").select2('val').length > 0 ? $("#filter_polarization").select2('val').join(',').split(',') : [],
        total_selected_items = technology_filter.length + vendor_filter.length + state_filter.length + city_filter.length + frequency_filter.length + polarization_filter.length;

    // If any value is selected in filter
    if(total_selected_items > 0) {
        // Set Advance Filters Flag
        isAdvanceFilter = 1;

        // Call function to plot the data on map as per the applied filters
        gmap_self.applyAdvanceFilters();
    } else {
        /*Hide the spinner*/
        hideSpinner();

        // Set Advance Filters Flag
        isAdvanceFilter = 0;

        bootbox.alert("Please select any filter");
    }
    // if(window.location.pathname.indexOf("white_background") > -1) {
    //     advSearch.callSetFilter();
    // } else {
    // }

    /*Call get_page_status function to show the current status*/
    get_page_status();

});

/*If 'Cancel' button of advance filter form is clicked*/
$("#cancelAdvFilterBtn").click(function(e) {

    // if(window.location.pathname.indexOf("googleEarth") > -1) {
    //     // $("#advFilterFormContainer").html("");
    // } else if(window.location.pathname.indexOf("white_background") > -1) {
    //     $("#advFilterFormContainer").html("");
    // }

    if(!($("#advFilterContainerBlock").hasClass("hide"))) {
        $("#advFilterContainerBlock").addClass("hide");
    }

    advSearch.resetVariables();
});

/**
 * This function triggers when remove filters button is clicked
 * @method removeAdvFilters
 */
function removeAdvFilters() {
    /*Reset advance filter status flag*/
    hasAdvFilter = 0;

    advSearch.removeFilters();

    // if(window.location.pathname.indexOf("googleEarth") > -1) {
    //     // data_for_filters_earth = main_devices_data_earth;
    // } else if(window.location.pathname.indexOf("white_background") > -1) {
    //     data_for_filters = main_devices_data_wmap;
    // } else {

    // }

    /*Call get_page_status function to show the current status*/
    get_page_status();
}

/*Trigers when "Create Polygon" button is clicked*/
$("#createPolygonBtn").click(function(e) {

    disableAdvanceButton();
    $("#resetFilters").button("loading");
    $("#showToolsBtn").removeAttr("disabled");

    // if(window.location.pathname.indexOf("googleEarth") > -1) {
    //     earth_instance.initPolling_earth();
    // }

    $("#polling_tech").val($("#polling_tech option:first").val());

    if(window.location.pathname.indexOf("white_background") > -1) {
        whiteMapClass.initLivePolling();

        hasSelectDevice = 1;

        /*Call get_page_status function to show the current status*/
        get_page_status();
    } else if(window.location.pathname.indexOf("googleEarth") > -1) {
        earth_instance.initLivePolling_earth();
        hasSelectDevice = 1;

        /*Call get_page_status function to show the current status*/
        get_page_status();
    } else {
        networkMapInstance.initLivePolling();

        hasSelectDevice = 1;

        /*Call get_page_status function to show the current status*/
        get_page_status();
    }
});

$("#tech_send").click(function(e) {

    if(window.location.pathname.indexOf("googleEarth") > -1) {
        earth_instance.fetchPollingTemplate_earth();
    } else if(window.location.pathname.indexOf("white_background") > -1) {
        whiteMapClass.fetchPollingTemplate_wmap();
    } else {
        networkMapInstance.fetchPollingTemplate_gmap();
    }
});

$("#fetch_polling").click(function(e) {

    // if(window.location.pathname.indexOf("googleEarth") > -1) {
    //     earth_instance.fetchDevicesPollingData_earth();
    // } else {
        networkMapInstance.fetchDevicesPollingData();
    // }
});

$("#play_btn").click(function(e) {
    
    if($(".play_pause_btns").hasClass("disabled")) {
        $(".play_pause_btns").removeClass("disabled");
    }

    if(polygonSelectedDevices && (polygonSelectedDevices.length > 0 && $("#lp_template_select").val() != "")) {
        if(!$("#play_btn").hasClass("disabled")) {
            $("#play_btn").addClass("disabled");
        }

        if(!($("#fetch_polling").hasClass("disabled"))) {
            $("#fetch_polling").addClass("disabled");
        }

        /*Disable poll interval & max interval dropdown*/
        $("#poll_interval").attr("disabled","disabled");
        $("#poll_maxInterval").attr("disabled","disabled");

        pollCallingTimeout = "";
        pollingInterval = $("#poll_interval").val() ? +($("#poll_interval").val()) : 10;
        pollingMaxInterval = $("#poll_maxInterval").val() ? +($("#poll_maxInterval").val()) : 1;
        remainingPollCalls = Math.floor((60*pollingMaxInterval)/pollingInterval);
        isPollingPaused = 0;

        if(window.location.pathname.indexOf("googleEarth") > -1) {
            earth_instance.startDevicePolling_earth();
        } else if(window.location.pathname.indexOf("white_background") > -1) {
            whiteMapClass.startDevicePolling_wmap();
        } else {
            networkMapInstance.startDevicePolling_gmap();
        }

    } else {
        bootbox.alert("Please select devices & polling template first.");
    }
});

$("#pause_btn").click(function(e) {
    
    if($(".play_pause_btns").hasClass("disabled")) {
        $(".play_pause_btns").removeClass("disabled");
    }

    // if(window.location.pathname.indexOf("googleEarth") > -1) {
        
    // } else if(window.location.pathname.indexOf("white_background") > -1) {
        
    // } else {
        if(polygonSelectedDevices.length > 0 && $("#lp_template_select").val() != "") {
            if(remainingPollCalls > 0) {
                if(!$("#pause_btn").hasClass("disabled")) {
                    $("#pause_btn").addClass("disabled");
                }

                //stop perf calling
                if(pollCallingTimeout) {
                    clearTimeout(pollCallingTimeout);
                    pollCallingTimeout = "";
                }
                isPollingPaused = 1;
            }
        } else {
            bootbox.alert("Please select devices & polling template first.");
        }
    // }
});

$("#stop_btn").click(function(e) {

    if($(".play_pause_btns").hasClass("disabled")) {
        $(".play_pause_btns").removeClass("disabled");
    }

    if(polygonSelectedDevices.length > 0 && $("#lp_template_select").val() != "") {
        if(remainingPollCalls > 0) {
            /*Disable poll interval & max interval dropdown*/
            $("#poll_interval").removeAttr("disabled");
            $("#poll_maxInterval").removeAttr("disabled");

            if($(".play_pause_btns").hasClass("disabled")) {
                $(".play_pause_btns").removeClass("disabled");
            }

            if($("#fetch_polling").hasClass("disabled")) {
                $("#fetch_polling").removeClass("disabled");
            }

            if(pollCallingTimeout) {
                clearTimeout(pollCallingTimeout);
                pollCallingTimeout = "";
            }

            pollingInterval = 10;
            pollingMaxInterval = 1;
            remainingPollCalls = 0;
            isPollingPaused = 0;
        }

    } else {
        bootbox.alert("Please select devices & polling template first.");
    }
});

/*Change event on polling technology dropdown*/
$("#polling_tech").change(function(e) {
    if(window.location.pathname.indexOf("white_background") > -1) {
        whiteMapClass.initLivePolling();
    } else if(window.location.pathname.indexOf("googleEarth") > -1) {
        earth_instance.initLivePolling_earth();
    } else {
        networkMapInstance.initLivePolling();
    }
});

/*When "Tabular View" button for polling widget clicked*/
$("#polling_tabular_view").click(function(e) {
    if(window.location.pathname.indexOf("white_background") > -1) {
        whiteMapClass.show_polling_datatable_wmaps();
    } else {
        networkMapInstance.show_polling_datatable();
    }
});

/*triggers when clear selection button is clicked*/
$("#clearPolygonBtn").click(function(e) {
    if(window.location.pathname.indexOf("white_background") > -1) {
        whiteMapClass.stopPolling();
        hasSelectDevice = 0;
        get_page_status();
    } else if(window.location.pathname.indexOf("googleEarth") > -1) {
        earth_instance.clearPolygon();
        hasSelectDevice = 0;
        get_page_status();
    } else {
        networkMapInstance.clearPolygon();
        hasSelectDevice = 0;

        /*Call get_page_status function to show the current status*/
        get_page_status();
    }
});



function get_page_status() {
    var status_txt = "";

    if(hasAdvFilter == 1) {
        status_txt+= '<li>Advance Filters Applied</li>';
    }

    if(hasSelectDevice == 1) {
        status_txt+= '<li>Select Devices Applied</li>';
    }

    if(hasTools == 1) {
        if(isFreeze == 1 || (tools_ruler && tools_ruler != 0) || (tools_line && tools_line != 0)) {
            status_txt+= '<li>Gmap Tools Applied<button class="btn btn-sm btn-danger pull-right" onclick="clearTools_gmap()" style="padding: 2px 5px; margin: -3px;">Reset</button><li>';
        }
    }

    if($("ul#gis_status_txt li#gis_search_status_txt").length) {
        status_txt+= $("ul#gis_status_txt li#gis_search_status_txt")[0].outerHTML;
    }

    if(status_txt == "") {
        status_txt += "<li>Default</li>";    
    }

    $("#gis_status_txt").html(status_txt);
}

//On change of Icon Size, call updateAllMarkers function in DevicePlottingLib with the value.
$("select#icon_Size_Select_In_Tools").change(function() {
    var val= $.trim($(this).val());
    defaultIconSize= val;

    current_icon_size = val;
    $.cookie("markerIconSize", val, {path: '/', secure : true});
    
    if(window.location.pathname.indexOf("white_background") > -1) {
        whiteMapClass.updateMarkersSize(val);
    } else if (window.location.pathname.indexOf("googleEarth") > -1) {
        earth_instance.updateAllMarkersWithNewIcon(val);
    } else {
        networkMapInstance.updateAllMarkersWithNewIcon_gmap(val);
        
    }
});


/*
Function is used to Disable Advance Search, Advance Filter Button when Call for data is going on.
When call is completed, we use the same function to enable Button by passing 'no' in parameter.
 */
function disableAdvanceButton(status) {
    var buttonEls= ['advSearchBtn', 'advFilterBtn', 'createPolygonBtn', 'showToolsBtn','export_data_gmap'];
    var selectBoxes= ['technology', 'vendor', 'state', 'city'];
    var textBoxes= ['google_loc_search','lat_lon_search'];
    var disablingBit = false;
    if(!status) {
        disablingBit= true;
        for(var i=0; i< buttonEls.length; i++) {
            // $('#'+buttonEls[i]).prop('disabled', disablingBit);
            $('#'+buttonEls[i]).button('loading');
        }

        for(var i=0; i< selectBoxes.length; i++) {
            document.getElementById(selectBoxes[i]).disabled = disablingBit;    
        }

        for(var i=0; i< textBoxes.length; i++) {
            var el = document.getElementById(textBoxes[i]);
            if(el) {
                document.getElementById(textBoxes[i]).disabled = disablingBit;    
            }            
        }
    } else {
        disablingBit= false;
        for(var i=0; i< buttonEls.length; i++) {
            // $('#'+buttonEls[i]).prop('disabled', disablingBit);
            $('#'+buttonEls[i]).button('complete');
        }

        for(var i=0; i< selectBoxes.length; i++) {
            document.getElementById(selectBoxes[i]).disabled = disablingBit;    
        }

        for(var i=0; i< textBoxes.length; i++) {
            var el = document.getElementById(textBoxes[i]);
            if(el) {
                document.getElementById(textBoxes[i]).disabled = disablingBit;    
            }
            // document.getElementById(textBoxes[i]).disabled = disablingBit;
        }
    }
}

/**
 * This event triggers keypress event on lat,lon search text box
 */
function isLatLon(e) {

    var entered_key_code = (e.keyCode ? e.keyCode : e.which),
        entered_txt = $("#lat_lon_search").val();

    if(entered_key_code == 13) {
        if(entered_txt.length > 0) {
            if(entered_txt.split(",").length != 2) {
                alert("Please Enter Proper Lattitude,Longitude.");
                $("#lat_lon_search").val("");
            } else {
                
                var lat = $.trim(entered_txt.split(",")[0]),
                    lng = $.trim(entered_txt.split(",")[1]),
                    lat_check = (+(lat) >= -90 && +(lat) < 90),
                    lon_check = (+(lng) >= -180 && +(lng) < 180),
                    dms_pattern = /^(-?\d+(?:\.\d+)?)[°:d]?\s?(?:(\d+(?:\.\d+)?)['':]?\s?(?:(\d+(?:\.\d+)?)["?]?)?)?\s?([NSEW])?/i;
                    dms_regex = new RegExp(dms_pattern);
                
                if((lat_check && lon_check) || (dms_regex.exec(lat) && dms_regex.exec(lng))) {
                    if((lat_check && lon_check)) {
                        if(window.location.pathname.indexOf("white_background") > -1) {
                            whiteMapClass.zoomToLonLat(entered_txt);
                        } else if(window.location.pathname.indexOf("googleEarth") > -1) {
                            earth_instance.pointToLatLon(entered_txt);
                        } else {
                            networkMapInstance.pointToLatLon(entered_txt);
                        }
                    } else {
                        var converted_lat = dmsToDegree(dms_regex.exec(lat));
                        var converted_lng = dmsToDegree(dms_regex.exec(lng));
                        
                        if(window.location.pathname.indexOf("white_background") > -1) {
                            whiteMapClass.zoomToLonLat(String(converted_lat)+","+String(converted_lng));
                        } else if(window.location.pathname.indexOf("googleEarth") > -1) {
                            earth_instance.pointToLatLon(String(converted_lat)+","+String(converted_lng));
                        } else {
                            networkMapInstance.pointToLatLon(String(converted_lat)+","+String(converted_lng));
                        }
                    }
                } else {
                    alert("Please Enter Proper Lattitude,Longitude.");
                    $("#lat_lon_search").val("");
                }                
            }                
        } else {
            alert("Please Enter Lattitude,Longitude.");
        }
    }
}

/*This function converts dms lat lon to decimal degree lat lon*/
function dmsToDegree(latLng) {

    var new_pt = NaN,degrees,minutes,seconds,hemisphere;

    degrees = Number(latLng[1]);
    minutes = typeof (latLng[2]) !== "undefined" ? Number(latLng[2]) / 60 : 0;
    seconds = typeof (latLng[3]) !== "undefined" ? Number(latLng[3]) / 3600 : 0;
    hemisphere = latLng[4] || null;
    if (hemisphere !== null && /[SW]/i.test(hemisphere)) {
        degrees = Math.abs(degrees) * -1;
    }
    if(degrees < 0) {
        new_pt = degrees - minutes - seconds;
    } else {
        new_pt = degrees + minutes + seconds;
    }

    return new_pt;
}

/*Object.key for IE*/
if (!Object.keys) {
  Object.keys = (function () {
    'use strict';
    var hasOwnProperty = Object.prototype.hasOwnProperty,
        hasDontEnumBug = !({toString: null}).propertyIsEnumerable('toString'),
        dontEnums = [
          'toString',
          'toLocaleString',
          'valueOf',
          'hasOwnProperty',
          'isPrototypeOf',
          'propertyIsEnumerable',
          'constructor'
        ],
        dontEnumsLength = dontEnums.length;

    return function (obj) {
      if (typeof obj !== 'object' && (typeof obj !== 'function' || obj == null)) {
        throw new TypeError('Object.keys called on non-object');
      }

      var result = [], prop, i;

      for (prop in obj) {
        if (hasOwnProperty.call(obj, prop)) {
          result.push(prop);
        }
      }

      if (hasDontEnumBug) {
        for (i = 0; i < dontEnumsLength; i++) {
          if (hasOwnProperty.call(obj, dontEnums[i])) {
            result.push(dontEnums[i]);
          }
        }
      }
      return result;
    };
  }());
}

/*indexOf for IE*/

if (!Array.prototype.indexOf) {
  Array.prototype.indexOf = function(searchElement, fromIndex) {

    var k;

    // 1. Let O be the result of calling ToObject passing
    //    the this value as the argument.
    if (this == null) {
      throw new TypeError('"this" is null or not defined');
    }

    var O = Object(this);

    // 2. Let lenValue be the result of calling the Get
    //    internal method of O with the argument "length".
    // 3. Let len be ToUint32(lenValue).
    var len = O.length >>> 0;

    // 4. If len is 0, return -1.
    if (len == 0) {
      return -1;
    }

    // 5. If argument fromIndex was passed let n be
    //    ToInteger(fromIndex); else let n be 0.
    var n = +fromIndex || 0;

    if (Math.abs(n) == Infinity) {
      n = 0;
    }

    // 6. If n >= len, return -1.
    if (n >= len) {
      return -1;
    }

    // 7. If n >= 0, then Let k be n.
    // 8. Else, n<0, Let k be len - abs(n).
    //    If k is less than 0, then let k be 0.
    k = Math.max(n >= 0 ? n : len - Math.abs(n), 0);

    // 9. Repeat, while k < len
    while (k < len) {
      var kValue;
      // a. Let Pk be ToString(k).
      //   This is implicit for LHS operands of the in operator
      // b. Let kPresent be the result of calling the
      //    HasProperty internal method of O with argument Pk.
      //   This step can be combined with c
      // c. If kPresent is true, then
      //    i.  Let elementK be the result of calling the Get
      //        internal method of O with the argument ToString(k).
      //   ii.  Let same be the result of applying the
      //        Strict Equality Comparison Algorithm to
      //        searchElement and elementK.
      //  iii.  If same is true, return k.
      if (k in O && O[k] == searchElement) {
        return k;
      }
      k++;
    }
    return -1;
  };
}


/**
 * This function shows tools panel to google map
 *
 */
function showToolsPanel() {
    if(isFreeze == 1) {
        $("#freeze_select").addClass("hide");
        $("#freeze_remove").removeClass("hide");
    } else {
        $("#freeze_remove").addClass("hide");
        $("#freeze_select").removeClass("hide");
    }

    if(tools_ruler && tools_ruler != 0) {
        $("#ruler_select").addClass("hide");
        $("#ruler_remove").removeClass("hide");
    } else {
        $("#ruler_select").removeClass("hide");
        $("#ruler_remove").addClass("hide");
    }

    if(tools_line && tools_line != 0) {
        $("#line_select").addClass("hide");
        $("#line_remove").removeClass("hide");
    } else {
        $("#line_remove").addClass("hide");
        $("#line_select").removeClass("hide");
    }

    $("#showToolsBtn").addClass("hide");

    $("#removeToolsBtn").removeClass("hide");

    $("#toolsContainerBlock").removeClass("hide");

    if(window.location.pathname.indexOf("googleEarth") > -1) {

    } else if(window.location.pathname.indexOf("white_background") > -1) {
    } else {
        google.maps.event.clearListeners(mapInstance, 'click');
    }
}

function removetoolsPanel() {
    pointAdded= -1;
    is_line_active= -1;
    is_ruler_active= -1;

    if(window.location.pathname.indexOf("googleEarth") > -1) {
    } else if(window.location.pathname.indexOf("white_background") > -1) {
    } else {
        google.maps.event.clearListeners(mapInstance, 'click');
    }    

    $("#showToolsBtn").removeClass("hide");

    if(isFreeze == 1 || (tools_ruler && tools_ruler != 0) || (tools_line && tools_line != 0) || ($.cookie("isLabelChecked") == true || $.cookie("isLabelChecked")=='true')) {
        $("#showToolsBtn").removeClass("btn-info").addClass("btn-warning");
    } else {
        $("#showToolsBtn").removeClass("btn-warning").addClass("btn-info");
    }

    $("#removeToolsBtn").addClass("hide");

    $("#toolsContainerBlock").addClass("hide");

    get_page_status();
}

$("#ruler_select").click(function(e) {

    // Set/Reset variables
    pointAdded= -1;
    is_ruler_active= 1;
    is_line_active= -1;

    $(this).addClass("hide");
    $("#ruler_remove").removeClass("hide");

    if(window.location.pathname.indexOf("googleEarth") > -1) {
        if(pointEventHandler) {
            google.earth.removeEventListener(ge.getGlobe(), 'mousedown', pointEventHandler);
            pointEventHandler = "";
        }
        networkMapInstance.clearRulerTool_gmap();
        earth_instance.addRulerTool_earth();
    } else if(window.location.pathname.indexOf("white_background") > -1) {

    } else {
        google.maps.event.clearListeners(mapInstance, 'click');
        networkMapInstance.clearRulerTool_gmap();
        networkMapInstance.addRulerTool_gmap();
    }
});


$("#ruler_remove").click(function(e) {
    pointAdded= -1;
    is_line_active= -1;
    is_ruler_active= -1;
    
    $(this).addClass("hide");
    $("#ruler_select").removeClass("hide");

    if(window.location.pathname.indexOf("googleEarth") > -1) {
        if(pointEventHandler) {
            google.earth.removeEventListener(ge.getGlobe(), 'mousedown', pointEventHandler);
            pointEventHandler = "";
        }
        networkMapInstance.clearRulerTool_gmap();
    } else if(window.location.pathname.indexOf("white_background") > -1) {

    } else {
        google.maps.event.clearListeners(mapInstance, 'click');
        // Change map cursor
        mapInstance.setOptions({'draggableCursor' : ''});
        networkMapInstance.clearRulerTool_gmap();
    }
});

$("#line_select").click(function(e) {
    pointAdded= -1;
    is_line_active= 1;
    is_ruler_active= -1;

    $(this).addClass("hide");
    $("#line_remove").removeClass("hide");

    if(window.location.pathname.indexOf("googleEarth") > -1) {

    } else if(window.location.pathname.indexOf("white_background") > -1) {
        
    } else {
        networkMapInstance.clearLineTool_gmap();
        google.maps.event.clearListeners(mapInstance, 'click');
        networkMapInstance.createLineTool_gmap();
    }

});

$("#line_remove").click(function(e) {
    pointAdded = -1;
    is_line_active= -1;
    is_ruler_active= -1;
    $(this).addClass("hide");
    $("#line_select").removeClass("hide");

    if(window.location.pathname.indexOf("googleEarth") > -1) {

    } else if(window.location.pathname.indexOf("white_background") > -1) {
        
    } else {
        google.maps.event.clearListeners(mapInstance, 'click');
        networkMapInstance.clearLineTool_gmap();
    }
});


var pointEventHandler = "";

$("#point_select").click(function(e) {
    pointAdded= 1;
    is_line_active= -1;
    is_ruler_active= -1;
    $(this).removeClass('btn-info').addClass('btn-warning');
    $("#point_icons_container li:first-child").trigger('click');
    $("#point_icons_container").removeClass("hide");

    if(window.location.pathname.indexOf("googleEarth") > -1) {
        if(pointEventHandler) {
            google.earth.removeEventListener(ge.getGlobe(), 'click', pointEventHandler);
            pointEventHandler = "";
        }
        networkMapInstance.addPointTool_gmap();
    } else if(window.location.pathname.indexOf("white_background") > -1) {

    } else {
        google.maps.event.clearListeners(mapInstance, 'click');
        // Change map cursor
        mapInstance.setOptions({'draggableCursor' : 'default'});
        networkMapInstance.addPointTool_gmap();
    }
});

$("#close_points_icon").click(function(e) {
    
    pointAdded= -1;
    is_line_active= -1;
    is_ruler_active= -1;
    $("#point_select").removeClass('btn-warning').addClass('btn-info');
    $("#point_icons_container").addClass("hide");
    if(window.location.pathname.indexOf("googleEarth") > -1) {
        if(pointEventHandler) {
            google.earth.removeEventListener(ge.getGlobe(), 'click', pointEventHandler);
            pointEventHandler = "";
        }
    } else if(window.location.pathname.indexOf("white_background") > -1) {

    } else {
        google.maps.event.clearListeners(mapInstance, 'click');
        // Change map cursor
        mapInstance.setOptions({'draggableCursor' : ''});
    }
});

$("#point_remove").click(function(e) {
    pointAdded= -1;
    is_line_active= -1;
    is_ruler_active= -1;
    $(this).addClass("hide");
    $("#point_icons_container").addClass("hide");

    if(window.location.pathname.indexOf("googleEarth") > -1) {
        if(pointEventHandler) {
            google.earth.removeEventListener(ge.getGlobe(), 'click', pointEventHandler);
            pointEventHandler = "";
        }
    } else if(window.location.pathname.indexOf("white_background") > -1) {

    } else {
        google.maps.event.clearListeners(mapInstance, 'click');
    }
    networkMapInstance.clearPointsTool_gmap();
});


/**
 * This event trigger when clicked on "Ruler" button
 * @event click
 */
 $("#freeze_select").click(function(e) {

    if($("#freeze_remove").hasClass("hide")) {

        $("#freeze_select").addClass("hide");
        $("#freeze_remove").removeClass("hide");
        $("#freeze_remove").show();

    }
    $("#freeze_remove").removeClass("hide");

    // $.cookie('isFreezeSelected', true);

    networkMapInstance.freezeDevices_gmap();
 });

 /**
  * This event unbind ruler click event & show the Ruler button again
  * @event click
  */
$("#freeze_remove").click(function(e) {

    if(!($("#freeze_remove").hasClass("hide"))) {
        $("#freeze_select").removeClass("hide");
        $("#freeze_remove").addClass("hide");
    }
    $("#freeze_select").removeClass("hide");

    // $.cookie('isFreezeSelected', false);

    networkMapInstance.unfreezeDevices_gmap();
});

/**
 * This function get the current status & show it on gmap/google eartg page.
 */

function clearTools_gmap() {
    google.maps.event.clearListeners(mapInstance,'click');
    networkMapInstance.clearRulerTool_gmap();
    networkMapInstance.clearLineTool_gmap();
    is_line_active = 0;
    bootbox.confirm("Do you want to reset Maintenance Points too?", function(result) {
        if(result) {
            pointAdded= -1;            
            hasTools = 0;
            networkMapInstance.clearPointsTool_gmap();
            $("#showToolsBtn").addClass("btn-info");
            $("#showToolsBtn").removeClass("btn-warning");
        }
        // get_page_status();
    });   
}


/**
 * This event show/hide perf param label from SS markers
 */

$("#show_hide_label").click(function(e) {
    $.cookie("isLabelChecked", e.currentTarget.checked, {path: '/', secure : true});

    for(var x=0;x<labelsArray_filtered.length;x++) {
        if(window.location.pathname.indexOf("googleEarth") > -1) {
            
        } else if(window.location.pathname.indexOf("white_background") > -1) {
            if(e.currentTarget.checked) {
                labelsArray_filtered[x].show();
            } else {
                labelsArray_filtered[x].hide();
            }
        } else {
            labelsArray_filtered[x].setVisible(e.currentTarget.checked);
        }
    }

    // Show/Hide perf info label
    for (var x = 0; x < labelsArray.length; x++) {

        if(window.location.pathname.indexOf("googleEarth") > -1) {
            
        } else if(window.location.pathname.indexOf("white_background") > -1) {
            if(e.currentTarget.checked) {
                labelsArray[x].show();
            } else {
                labelsArray[x].hide();
            }
        } else {
            labelsArray[x].setVisible(e.currentTarget.checked);
            // var move_listener_obj = labelsArray[x].moveListener_;
            // if(move_listener_obj) {
            //     var keys_array = Object.keys(move_listener_obj);
            //     for(var z=0;z<keys_array.length;z++) {
            //         if(typeof move_listener_obj[keys_array[z]] == 'object') {
            //            if((move_listener_obj[keys_array[z]] && move_listener_obj[keys_array[z]]["name"]) && (move_listener_obj[keys_array[z]] && move_listener_obj[keys_array[z]]["bs_name"])) {
            //                 if (move_listener_obj[keys_array[z]].map != "" && move_listener_obj[keys_array[z]].map != null) {
            //                     labelsArray[x].setVisible(e.currentTarget.checked);
            //                 }
            //            }
            //         }
            //     }
            // }
        }

    }

    // Show/Hide tooltip info label
    for (key in tooltipInfoLabel) {
        if(window.location.pathname.indexOf("googleEarth") > -1) {
            
        } else if(window.location.pathname.indexOf("white_background") > -1) {
            if(e.currentTarget.checked) {
                tooltipInfoLabel[key].show();
                // If label changed then update the size as per new content.
                tooltipInfoLabel[key].updateSize();
            } else {
                tooltipInfoLabel[key].hide();
            }
        } else {
            tooltipInfoLabel[key].setVisible(e.currentTarget.checked);
            // var move_listener_obj = tooltipInfoLabel[key].moveListener_;
            // if(move_listener_obj) {
            //     var keys_array = Object.keys(move_listener_obj);
            //     for(var z=0;z<keys_array.length;z++) {
            //         if(typeof move_listener_obj[keys_array[z]] == 'object') {
            //            if((move_listener_obj[keys_array[z]] && move_listener_obj[keys_array[z]]["name"]) && (move_listener_obj[keys_array[z]] && move_listener_obj[keys_array[z]]["bs_name"])) {
            //                 if (move_listener_obj[keys_array[z]].map != "" && move_listener_obj[keys_array[z]].map != null) {
            //                     tooltipInfoLabel[key].setVisible(e.currentTarget.checked);
            //                 }
            //            }
            //         }
            //     }
            // }
        }
    }
});

/**
 * This event trigger when previous navigation button on polling widget clicked
 */
$("#navigation_container button#previous_polling_btn").click(function(e) {
    if(window.location.pathname.indexOf("white_background") > -1) {
        whiteMapClass.show_previous_polled_icon_wmaps();
    } else if(window.location.pathname.indexOf("googleEarth") > -1) {
        earth_instance.show_previous_polled_icon_earth();
    } else {
        networkMapInstance.show_previous_polled_icon();
    }
});

/**
 * This event trigger when next navigation button on polling widget clicked
 */
$("#navigation_container button#next_polling_btn").click(function(e) {
   if(window.location.pathname.indexOf("white_background") > -1) {
        whiteMapClass.show_next_polled_icon_wmaps();
    } else if(window.location.pathname.indexOf("googleEarth") > -1) {
        earth_instance.show_next_polled_icon_earth();
    } else {
        networkMapInstance.show_next_polled_icon();
    }
});

/**
 * This event trigger when clicked on add point icons
 */
$("#point_icons_container li").click(function(e) {

    /*Remove selected class from all li*/
    $("#point_icons_container li").removeClass('selected_icon');
    
    /*Add selected class to clicked li*/
    $(this).addClass('selected_icon');
    
    /*Check that 'img' tag is present in li or not*/
    if($("#point_icons_container li.selected_icon")[0].children[0].hasAttribute('src')) {
        point_icon_url = $("#point_icons_container li.selected_icon")[0].children[0].attributes['src'].value.split("../../")[1];
    }
});

/*Close info window when close button is clicked*/
$('#infoWindowContainer').delegate('.close_info_window','click',function(e) {
    $('#infoWindowContainer').html("");
    if(!$('#infoWindowContainer').hasClass("hide")) {
        $('#infoWindowContainer').addClass("hide");
    }

    // Set actual infowindow size -- START
    if(!$("#infoWindowContainer").hasClass("col-md-4")) {
        $("#infoWindowContainer").addClass("col-md-4")
    }

    if(!$("#infoWindowContainer").hasClass("col-md-offset-8")) {
        $("#infoWindowContainer").addClass("col-md-offset-8")
    }

    if($("#infoWindowContainer").hasClass("col-md-3")) {
        $("#infoWindowContainer").removeClass("col-md-3")
    }

    if($("#infoWindowContainer").hasClass("col-md-offset-9")) {
        $("#infoWindowContainer").removeClass("col-md-offset-9")
    }
    // Set actual infowindow size -- END

    if($(".windowIFrame").length) {
        $(".windowIFrame").remove();
    }
});

$('#infoWindowContainer').delegate('.download_report_btn','click',function(e) {
    var ckt_id = e.currentTarget.attributes['ckt_id'] ? e.currentTarget.attributes['ckt_id'].value : "";
    // If ckt id exist then fetch l2 report url
    if(ckt_id) {

        $.ajax({
            url: base_url+'/network_maps/l2_report/'+encodeURIComponent(ckt_id)+'/',
            type : "GET",
            success : function(response) {

                var result = "";
                // Type check for response
                if(typeof response == 'string') {
                    result = JSON.parse(response);
                } else {
                    result = response;
                }
                if(result.success == 1) {
                    if(result['data'].length == 0) {
                        bootbox.alert("No L2 Report Found.");
                    } else {
                        var url = base_url+"/"+result['data'][0]['url'];
                        // console.log(url);
                        var win = window.open(url, '_blank');
                        win.focus();
                    }
                } else {
                    bootbox.alert("No L2 Report Found.");
                }
            },
            error : function(err) {
                // console.log(err)max-;
            }
        });
    }
});

/**
 * This event triggers when any polled param name is clicked
 * @event delegaate
 */
$('#infoWindowContainer').delegate('td.text-primary','click',function(e) {
    // Show the loader
    showSpinner();

    var api_url = e.currentTarget.attributes['url'] ? e.currentTarget.attributes['url'].value : "";
    
    // If api_url exist then fetch l2 report url
    if(api_url) {
        $.ajax({
            url: base_url+"/"+api_url,
            type: "GET",
            dataType: "json",
            success: function (response) {

                var result = "";
                // Type check of response
                if(typeof response == 'string') {
                    result = JSON.parse(response);
                } else {
                    result = response;
                }

                if (result.success == 1) {
                    
                    var contentHtml = "",
                        table_headers = result.data.objects.table_data_header ? result.data.objects.table_data_header : false;

                    contentHtml += "<div style='max-height:600px;overflow:auto;position:relative;z-index:9999;'>";

                    if(table_headers) {

                        var table_data = result.data.objects.table_data ? result.data.objects.table_data : [];
                        
                        contentHtml += createTableHtml_nocout(
                            'other_perf_table',
                            table_headers,
                            table_data,
                            false
                        );

                        contentHtml += "</div>";
                        /*Call the bootbox to show the popup with datatable*/
                        bootbox.dialog({
                            message: contentHtml,
                            title: '<i class="fa fa-dot-circle-o">&nbsp;</i> Performance    '
                        });

                        // Update Modal width to 90%;
                        $(".modal-dialog").css("width","90%");

                        $("#other_perf_table").DataTable({
                            bPaginate: true,
                            bDestroy: true,
                            aaSorting : [[0,'desc']],
                            sPaginationType: "full_numbers"
                        });

                    } else {

                        contentHtml += "<div id='perf_chart' style='width:83%;'></div>";
                        contentHtml += "<div class='divide-20'></div>";
                        contentHtml += "<div id='perf_chart_table'></div>";
                        var chartConfig = result.data.objects.chart_data;

                        contentHtml += createChartDataTableHtml_nocout(
                            "perf_data_table",
                            chartConfig
                        );

                        contentHtml += "</div>";
                        contentHtml += "</div>";

                        /*Call the bootbox to show the popup with datatable*/
                        bootbox.dialog({
                            message: contentHtml,
                            title: '<i class="fa fa-dot-circle-o">&nbsp;</i> Performance'
                        });

                        // Update Modal width to 90%;
                        $(".modal-dialog").css("width","90%");

                        $("#perf_data_table").DataTable({
                            bPaginate: true,
                            bDestroy: true,
                            aaSorting : [[0,'desc']],
                            sPaginationType: "full_numbers"
                        });
                        if(chartConfig.length > 0) {
                            // Create Chart
                            createHighChart_nocout(result.data.objects,'perf');
                        }
                    }
                }
            },
            error : function(err) {
                // console.log(err.statusText);
            },
            complete : function() {
                // hide the loader
                hideSpinner();
            }
        });
    } else {
        // hide the loader
        hideSpinner();
    }
});



/**
 * This event trigger when export data button is clicked
 * @event click
 */
$("#export_data_gmap").click(function(e) {

    if($("#clearExportDataBtn").hasClass('hide')) {
        $("#clearExportDataBtn").removeClass('hide');
    }

    if(!$("#export_data_gmap").hasClass('hide')) {
        $("#export_data_gmap").addClass('hide');
    }

    //enable the flag
    isExportDataActive = 1;

    // call function to select data to be export & then export selected data
    if(window.location.pathname.indexOf('googleEarth') > -1) {
        earth_instance.exportData_earth();
    } else if(window.location.pathname.indexOf("white_background") > -1) {
        whiteMapClass.exportData_wmap();
    } else {
        networkMapInstance.exportData_gmap();
    }
});

/**
 * This event trigger when "Cancel Selection" button of export data is clicked
 * @event click
 */
$("#clearExportDataBtn").click(function(e) {
    //disable the flag
    isExportDataActive = 0;
    // call function to select data to be export & then export selected data
    networkMapInstance.removeInventorySelection();
});

/**
 * This event trigger when "Download Inventory" button on selected devices panel is clicked
 * @event click
 */
$("#download_inventory").click(function(e) {
    //call function to download selected inventory.
    networkMapInstance.downloadInventory_gmap(); 
});


/**
 * This function checks that the given point is in given polyon of not.
 * @method isPointInPoly
 * @param poly {Array}, It is the polygon data(lat-lon) array
 * @param pt {Object}, It is point lat lon object
 */
function isPointInPoly(poly, pt) {
    if(poly && poly.length > 0) {
        for(var c = false, i = -1, l = poly.length, j = l - 1; ++i < l; j = i)
                ((poly[i].lat <= pt.lat && pt.lat < poly[j].lat) || (poly[j].lat <= pt.lat && pt.lat < poly[i].lat))
                && (pt.lon < (poly[j].lon - poly[i].lon) * (pt.lat - poly[i].lat) / (poly[j].lat - poly[i].lat) + poly[i].lon)
                && (c = !c);
            return c;
    } else {
        return false;
    }
}

/**
 * Function to bounds Google Earth
 * @param  {Array} boundsObj Array of Lat and Lon Object
 * @return {[type]}           [description]
 */
function showGoogleEarthInBounds(boundsArr, callback) {

    gexInstance.dom.clearFeatures();

    var boundPolygonArray= [];
    for(var i=0;i< boundsArr.length; i++) {
        (function(i) {
            var point = gexInstance.dom.buildPointPlacemark([boundsArr[i].lat, boundsArr[i].lon]);
            // Hide this placemark
            point.setVisibility(false);
            boundPolygonArray.push(point);
        }(i));
    }

    var folder = gexInstance.dom.addFolder(boundPolygonArray);

    // var bounds = gexInstance.dom.computeBounds(folder);
    // gexInstance.view.setToBoundsView(bounds, { aspectRatio: 1.0 });
    gexInstance.util.flyToObject(folder);
    isFromSearch = true;
    callback();
}

function objectsAreSame(x, y) {
   var objectsAreSame = true;
   for(var propertyName in x) {
      if(x[propertyName] !== y[propertyName]) {
         objectsAreSame = false;
         break;
      }
   }
   return objectsAreSame;
}


function arraysEqual(a, b) {
  if (a == b) return true;
  if (a == null || b == null) return false;
  if (a.length != b.length) return false;

  // If you don't care about the order of the elements inside
  // the array, you should sort both arrays here.

  for (var i = 0; i < a.length; ++i) {
    return objectsAreSame(a[i], b[i]);
  }
  return true;
}

function checkIfMarkerIsInState(marker, array_state_name) {
    var isMarkerPresent= false, i=0;
    var lower_array_state_name = array_state_name.map(function(x) {return x.name.toLowerCase();})
    for(i=0; i< lower_array_state_name.length; i++) {
        if(!marker.state) {
            return isMarkerPresent;
        }
        if(lower_array_state_name.indexOf(marker.state.toLowerCase()) > -1) {
            return !isMarkerPresent;
        }
    }
    return isMarkerPresent;
}

function getEarthZoomLevel() {
    var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);
    return lookAt.getRange();
}

function setEarthZoomLevel(alt) {
    var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);
    return lookAt.setRange(alt);
}

function updateGoogleEarthPlacemark(placemark, newIcon) {
    // Define a custom icon.next_polling_btn
    var icon = ge.createIcon('');
    icon.setHref(newIcon);

    var style = ge.createStyle('');
    style.getIconStyle().setIcon(icon);

    var place_mark_type = placemark["pointType"] ? placemark["pointType"] : 'other';

    var current_scale = earth_self.getPlacemarkScale_earth(place_mark_type);    
    style.getIconStyle().setScale(current_scale);

    placemark.setStyleSelector(style);
}

function updateGoogleEarthPlacedmarkNewSize(placemark, newSize) {
    // Define a custom icon.next_polling_btn
    var icon = ge.createIcon('');
    icon.setHref(placemark.icon);
    var style = ge.createStyle('');
    style.getIconStyle().setIcon(icon);
    style.getIconStyle().setScale(newSize);
    placemark.setStyleSelector(style);
}

function getCurrentEarthBoundPolygon() {
    var poly = [];
    var globeBounds = ge.getView().getViewportGlobeBounds();
    poly = [ {lat: globeBounds.getNorth(), lon: globeBounds.getWest()}, {lat: globeBounds.getNorth(), lon: globeBounds.getEast()}, {lat: globeBounds.getSouth(), lon: globeBounds.getEast()},{lat: globeBounds.getSouth(), lon: globeBounds.getWest()}, {lat: globeBounds.getNorth(), lon: globeBounds.getWest()} ];
    return poly;
}

function openGoogleEarthBaloon(innerHtml, feature) {
    var balloon = ge.createHtmlDivBalloon('');
    balloon.setFeature(feature);
    var div = document.createElement('DIV');
    div.innerHTML = innerHtml;
    balloon.setContentDiv(div);
    ge.setBalloon(balloon);
}



var altZoomList = [ // Altitude <-> Zoom level
    30000000, 24000000, 18000000, 10000000, 4000000, 1900000, 1100000, 550000, 280000,
    170000, 82000, 38000, 19000, 9200, 4300, 2000, 990, 570, 280, 100, 36, 12, 0 ];

function ZoomToAlt(zoom) {
    /// <summary>Converts a zoom level to an altitude
    /// <param name="zoom" />Zoom level
    /// <returns>Altitude in meters
    return altZoomList[zoom < 0 ? 0 : zoom > 21 ? 21 : zoom];
}

function AltToZoom(alt) {
    /// <summary>Converts an altitude to a zoom level
    /// <param name="alt" />Altitude in meters
    /// <returns>Zoom level
    for (var i = 0; i < 22; ++i) {
        if (alt > altZoomList[i] - ((altZoomList[i] - altZoomList[i+1]) / 2)) return i;
    }
    return 10;
}

function getRangeInZoom() {
    var earthRange = getEarthZoomLevel();
    return AltToZoom(earthRange);
}

function deleteGoogleEarthPlacemarker(uniqueID) {
    var children = ge.getFeatures().getChildNodes();
    for(var i = 0; i < children.getLength(); i++) { 
        var child = children.item(i);
        if(child.getType() == 'KmlPlacemark') {
            if(child.getId()==uniqueID) {
                ge.getFeatures().removeChild(child);
            }
        }
    }
}

/**
 * This event trigger when any label is selected or changed from labels dropdown.
 * @event change
 */
$("#static_label").change(function(e) {

    if(($(this).val()) && ($(this).val() != last_selected_label)) {
        if(!$("#apply_label").hasClass("btn-success")) {
            $("#apply_label").addClass("btn-success");
            $("#apply_label").html("Apply Label")
        }

        if($("#apply_label").hasClass("btn-danger")) {
            $("#apply_label").removeClass("btn-danger");
        }
    }
});

/**
 * This event trigger when 'Apply Label' button in tools section clicked.
 * @event click
 */
$("#apply_label").click(function(e) {
    var selected_val = $.trim($("#static_label").val()),
        selected_text = $.trim($("#static_label option:selected").text());

    if(last_selected_label != "" && selected_val == "" && selected_text == 'Select Label') {
        // Call Function to remove ss param label from map & updates button and dropdown
        removeSSParamLabel();

    } else {
        if((selected_val) && (selected_val != last_selected_label)) {

            if($("#apply_label").hasClass("btn-success")) {
                $("#apply_label").removeClass("btn-success");
            }

            if(!$("#apply_label").hasClass("btn-danger")) {
                $("#apply_label").addClass("btn-danger");
                $("#apply_label").html("Remove Label")
            }

            // Save selected value to global variable
            last_selected_label = selected_val;
            // Update cookie value with the selected value.
            $.cookie("tooltipLabel", last_selected_label, {path: '/', secure : true});

            if(window.location.pathname.indexOf("googleEarth") > -1) {
                // Pass
            } else if(window.location.pathname.indexOf("white_background") > -1) {
                if(ccpl_map && ccpl_map.getZoom() >= 4) {
                    networkMapInstance.updateTooltipLabel_gmap();
                } else {
                    $.gritter.add({
                        title: "SS Parameter Label",
                        text: $.trim($("#static_label option:selected").text())+" - Label Applied Successfully.",
                        sticky: false,
                        time : 1000
                    });
                }
            } else {
                // If current zoom level is greater the 7
                if(mapInstance && mapInstance.getZoom() > 7) {
                    networkMapInstance.updateTooltipLabel_gmap();
                } else {
                    $.gritter.add({
                        title: "SS Parameter Label",
                        text: $.trim($("#static_label option:selected").text())+" - Label Applied Successfully.",
                        sticky: false,
                        time : 1000
                    });
                }
            }
        } else {
            if($.trim($("#apply_label").html()) == 'Remove Label') {
                // Call Function to remove ss param label from map & updates button and dropdown
                removeSSParamLabel();
            } else {
                bootbox.alert("Please select different value.");
            }
        }
    }
});


/**
 * This function removes the ss param label & updated the button text & dropdown
 * @metho removeSSParamLabel
 */
function removeSSParamLabel() {
    $("#static_label").val($("#static_label option:first").val());
    // Save selected value to global variable
    last_selected_label = "";
    // Update cookie value with the selected value.
    $.cookie("tooltipLabel", last_selected_label, {path: '/', secure : true});

    if(window.location.pathname.indexOf("googleEarth") > -1) {
        
    } else if(window.location.pathname.indexOf("white_background") > -1) {
        // Remove tooltip info label
        for (key in tooltipInfoLabel) {
            tooltipInfoLabel[key].destroy();
        }
    } else {
        // Remove tooltip info label
        for (key in tooltipInfoLabel) {
            tooltipInfoLabel[key].close();
        }
    }
    // Reset Variables
    tooltipInfoLabel = {};

    if(!$("#apply_label").hasClass("btn-success")) {
        $("#apply_label").addClass("btn-success");
        $("#apply_label").html("Apply Label")
    }

    if($("#apply_label").hasClass("btn-danger")) {
        $("#apply_label").removeClass("btn-danger");
    }
}

// This event triggers when service type radio button is changed
$('input[type=radio][name=thematic_type]').change(function(e) {
    // Call function to restart perf calling
    networkMapInstance.restartPerfCalling();
});

// 
$("#infoWindowContainer").delegate(".nav-tabs li a",'click',function(evt) {

    var current_device_id = evt.currentTarget.attributes.device_id ? evt.currentTarget.attributes.device_id.value : "",
        point_type = evt.currentTarget.attributes.point_type ? evt.currentTarget.attributes.point_type.value : "",
        dom_id = evt.currentTarget.attributes.id ? evt.currentTarget.attributes.id.value : "",
        device_tech = evt.currentTarget.attributes.device_tech ? evt.currentTarget.attributes.device_tech.value : "",
        href_val = evt.currentTarget.attributes.href ? evt.currentTarget.attributes.href.value.split("#") : "",
        block_id = href_val.length > 1 ? href_val[1] : "",
        device_pl = evt.currentTarget.attributes.pl_value ? evt.currentTarget.attributes.pl_value.value : "";

    if(dom_id && point_type && current_device_id) {
        // Show Spinner
        if(dom_id == 'polled_tab') {
            if($("a#"+dom_id+" .fa-spinner").hasClass("hide")) {
                $("a#"+dom_id+" .fa-spinner").removeClass("hide");
            }

            if(periodic_tooltip_call) {
                periodic_tooltip_call.abort();
            }

            // Make AJAX Call
            periodic_tooltip_call = $.ajax({
                url: base_url+'/network_maps/perf_info/?device_id='+current_device_id+"&device_pl="+device_pl,
                type : "GET",
                success : function(response) {

                    var result = "",
                        polled_data_html = "";
                    // Type check for response
                    if(typeof response == 'string') {
                        result = JSON.parse(response);
                    } else {
                        result = response;
                    }

                    if(result && result.length > 0) {

                        var fetched_polled_info = result,
                            tooltip_info_dict = [];

                        if(point_type == 'sector_Marker' || point_type == 'sector') {
                            
                            if(ptp_tech_list.indexOf(device_tech) > -1) {
                                tooltip_info_dict = rearrangeTooltipArray(ptp_sector_toolTip_polled,fetched_polled_info);
                            } else if(device_tech == 'wimax') {
                                tooltip_info_dict = rearrangeTooltipArray(wimax_sector_toolTip_polled,fetched_polled_info);
                            } else if(device_tech == 'pmp') {
                                tooltip_info_dict = rearrangeTooltipArray(pmp_sector_toolTip_polled,fetched_polled_info);
                            } else {
                                // pass
                            }
                        } else if(point_type == 'sub_station') {
                            if(ptp_tech_list.indexOf(device_tech) > -1) {
                                tooltip_info_dict = rearrangeTooltipArray(ptp_ss_toolTip_polled,fetched_polled_info);
                            } else if(device_tech == 'wimax') {
                                tooltip_info_dict = rearrangeTooltipArray(wimax_ss_toolTip_polled,fetched_polled_info);
                            } else if(device_tech == 'pmp') {
                                tooltip_info_dict = rearrangeTooltipArray(pmp_ss_toolTip_polled,fetched_polled_info);
                            } else {
                                // pass
                            }
                        } else {
                            // pass
                        }

                        polled_data_html = "";
                        polled_data_html += "<table class='table table-bordered table-hover'><tbody>";

                        /*Poll Parameter Info*/
                        for(var i=0; i< tooltip_info_dict.length; i++) {
                            var url = "",
                                text_class = "";
                            if(tooltip_info_dict[i]["show"]) {
                                // Url
                                url = tooltip_info_dict[i]["url"] ? tooltip_info_dict[i]["url"] : "";
                                text_class = "text-primary";

                                polled_data_html += "<tr><td class='"+text_class+"' url='"+url+"'>"+tooltip_info_dict[i]['title']+"</td>\
                                                     <td>"+tooltip_info_dict[i]['value']+"</td></tr>";
                            }
                        }

                        polled_data_html += "</tbody></table>";

                        // Clear the polled block HTML
                        $("#"+block_id).html('<div class="divide-10"></div>');

                        // Append the polled data info
                        $("#"+block_id).append(polled_data_html);

                    } else {
                        $.gritter.add({
                            title: "Polled Info",
                            text: "Please try again later.",
                            sticky: false,
                            time : 1000
                        });
                    }
                },
                error : function(err) {

                    if(err.statusText != 'abort') {
                        $.gritter.add({
                            title: "Polled Info",
                            text: err.statusText,
                            sticky: false,
                            time : 1000
                        });
                    }
                },
                complete : function() {
                    if(!$("a#"+dom_id+" .fa-spinner").hasClass("hide")) {
                        $("a#"+dom_id+" .fa-spinner").addClass("hide");
                    }       
                }
            });

        }
    } else {
        if(periodic_tooltip_call) {
            periodic_tooltip_call.abort();
        }
        if(!$(".nav-tabs li a:last-child .fa-spinner").hasClass("hide")) {
            $(".nav-tabs li a:last-child .fa-spinner").addClass("hide");
        }
    }
});