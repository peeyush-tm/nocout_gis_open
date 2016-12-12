/**
 * This library handle events regarding elements on map page
 * @for devicevisualization
 */

// Global Variables
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
    periodic_tooltip_call = "",
    live_poll_config = {},
    periodic_poll_process_count = 1,
    is_tooltip_polled_used = false,
    not_ss_param_labels = ['base_station_alias'],
    pointEventHandler = "",
    altZoomList = [
        30000000, 24000000, 18000000, 10000000, 4000000, 1900000, 1100000, 550000, 280000, 
        170000, 82000, 38000, 19000, 9200, 4300, 2000, 990, 570, 280, 100, 36, 12, 0
    ];

// set base url 
try {
    base_url = getBaseUrl();
} catch(e) {
    /*Set the base url of application for ajax calls*/
    if(window.location.origin) {
        base_url = window.location.origin;
    } else {
        base_url = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
    }
}


/*Save cookie value to variable*/
isFreeze = $.cookie("isFreezeSelected") ? $.cookie("isFreezeSelected") : 0;
freezedAt = $.cookie("freezedAt") ? $.cookie("freezedAt") : 0;
tools_ruler = $.cookie("tools_ruler") ? $.cookie("tools_ruler") : 0;
last_selected_label = $.cookie("tooltipLabel") ? $.cookie("tooltipLabel") : "";
current_icon_size = $.cookie("markerIconSize") ? $.cookie("markerIconSize") : "medium";

isPollingActive = 0;

// Clear click listener
if(typeof google != 'undefined' && google.maps) {
    google.maps.event.clearListeners(mapInstance,'click');
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

//defining global varible for city options
city_options = []

// Select the last selected item in size dropdown 
$("select#icon_Size_Select_In_Tools").val(current_icon_size);

if(
    isFreeze == 1
    ||
    (tools_ruler && tools_ruler != 0)
    ||
    (
        $.cookie("isLabelChecked") == true
        ||
        $.cookie("isLabelChecked")=='true'
    )
) {
    $("#showToolsBtn").removeClass("btn-default");
    $("#showToolsBtn").addClass("btn-warning");
} else {
    $("#showToolsBtn").addClass("btn-default");
    $("#showToolsBtn").removeClass("btn-warning");
}

// Update "Show Labels"  checkbox as per the cookie value
if ($("#show_hide_label").length > 0) {
    if($.cookie("isLabelChecked")) {
        if($.cookie("isLabelChecked") == true || $.cookie("isLabelChecked")=='true') {
            $("#show_hide_label")[0].checked = true;
        } else {
            $("#show_hide_label")[0].checked = false;
        }
    }
}

// Update "Show All Connection Lines"  checkbox as per the cookie value
if ($("#showConnLines").length > 0) {
    if($.cookie("isLineChecked")) {
        if($.cookie("isLineChecked") == true || $.cookie("isLineChecked")=='true') {
            $("#showConnLines")[0].checked= true;
        } else {
            $("#showConnLines")[0].checked= false;
        }
    }
}

// Update "Show All SS"  checkbox as per the cookie value
if ($("#showAllSS").length > 0) {
    if($.cookie("isSSChecked")) {
        if($.cookie("isSSChecked") == true || $.cookie("isSSChecked")=='true') {
            $("#showAllSS")[0].checked= true;
        } else {
            $("#showAllSS")[0].checked= false;
        }
    }
}

/**
 * This event trigger when state dropdown value is changes
 * @event Change
 */
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

/**
 * This event trigger when city dropdown value is changes
 * @event Change
 */
$("#city").change(function(e) {
    getPageType();
    networkMapInstance.makeFiltersArray(mapPageType);
});


/**
 * This event trigger when region dropdown value is changes
 * @event Change
 */
$("#region").change(function(e) {
    getPageType();
    networkMapInstance.makeFiltersArray(mapPageType);
});


/**
 * This event trigger when vendor dropdown value is changes
 * @event Change
 */
$("#vendor").change(function(e) {
    getPageType();
    networkMapInstance.makeFiltersArray(mapPageType);
});

/**
 * This event trigger when technology dropdown value is changes
 * @event Change
 */
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

/**
 * This event triggers when Reset Filter button clicked
 * @event Click
 */
$("#resetFilters").click(function(e) {

    var isBasicFilterApplied = $.trim($("#technology").val()) || $.trim($("#vendor").val()) || $.trim($("#state").val()) || $.trim($("#city").val())  || $.trim($("#region").val())
    
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
        $("#region").val($("#region option:first").val());
        
        isCallCompleted = 1;/*Remove this call if server call is started on click of reset button*/

        if(window.location.pathname.indexOf("gearth") > -1) {

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
            
            data_for_filters_earth = all_devices_loki_db.data;

            isApiResponse = 0;
            // Load all counters
            earth_instance.showStateWiseData_earth(all_devices_loki_db.data);
        } else if(window.location.pathname.indexOf("wmap") > -1) {
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
            networkMapInstance.updateStateCounter_gmaps();
        }
    }

    // Reset Lat Lon Search if exists
    if($("#lat_lon_search").val()) {
        searchResultData = [];
        $("#lat_lon_search").val("");
    }
    if(lastSearchedPt && lastSearchedPt.map) {
        lastSearchedPt.setMap(null);
        lastSearchedPt = {};
    }

    // Reset Location Search if exists
    if($("#google_loc_search").val()) {
        searchResultData = [];
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

    if(window.location.pathname.indexOf("wmap") > -1) {
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
});

/**
 * This event triggers when Submit button of Advance Search clicked
 * @event Click
 */
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

/**
 * This event triggers when Cancel button of Advance Search clicked
 * @event Click
 */
$("#cancelAdvSearchBtn").click(function(e) {
    if(!($("#advFilterSearchContainerBlock").hasClass("hide"))) {
        $("#advSearchContainerBlock").addClass("hide");
    }
});

/**
 * This event triggers when Reset button of Advance Search clicked
 * @event Click
 */
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

    if(window.location.pathname.indexOf("wmap") > -1) {
        ccpl_map.getLayersByName("Search Layer")[0].setVisibility(false);
    }

    // Reset Search data variable
    searchResultData = []
    search_element_bs_id = [];

    // Reset Advance Search Flag
    isAdvanceSearch = 0;


    advJustSearch.removeSearchMarkers();
    advJustSearch.resetVariables();

    if(isDebug) {
        var time_diff = (new Date().getTime() - start_date_reset_search.getTime())/1000;
        // console.log("Update State Counters Function End Time :- "+ new Date().toLocaleString());
        console.log("Reset Advance Search Function(Return Data Case) End Time :- "+ time_diff +" Seconds");
        console.log("*******************************************");
        start_date_update_counter = "";
    }

});

/**
 * This event triggers when Submit button of Advance Filters clicked
 * @event Click
 */    
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
        antena_type_filter = $("#filter_antena_type").select2('val').length > 0 ? $("#filter_antena_type").select2('val').join(',').split(',') : [],
        region_filter = $("#filter_region").select2('val').length > 0 ? $("#filter_region").select2('val').join(',').split(',') : [],
        total_selected_items = technology_filter.length + vendor_filter.length + state_filter.length + city_filter.length + frequency_filter.length + polarization_filter.length + antena_type_filter.length + region_filter.length;

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

    /*Call get_page_status function to show the current status*/
    get_page_status();

});

/**
 * This event triggers when Cancel button of Advance Filters clicked
 * @event Click
 */
$("#cancelAdvFilterBtn").click(function(e) {

    if(!($("#advFilterContainerBlock").hasClass("hide"))) {
        $("#advFilterContainerBlock").addClass("hide");
    }

    advSearch.resetVariables();
});

/**
 * This event trigers when "Create Polygon" button is clicked
 * @event Click
 */
$("#createPolygonBtn").click(function(e) {

    disableAdvanceButton();
    $("#resetFilters").button("loading");
    $("#showToolsBtn").removeAttr("disabled");

    $("#polling_tech").val($("#polling_tech option:first").val());
    $("#polling_type").val($("#polling_type option:first").val());

    if(window.location.pathname.indexOf("wmap") > -1) {
        whiteMapClass.initLivePolling();

        hasSelectDevice = 1;

        /*Call get_page_status function to show the current status*/
        get_page_status();
    } else if(window.location.pathname.indexOf("gearth") > -1) {
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

/**
 * This event trigers when "Send" button is clicked to fetch the polling templates
 * @event Click
 */
$("#tech_send").click(function(e) {

    if(window.location.pathname.indexOf("gearth") > -1) {
        earth_instance.fetchPollingTemplate_earth();
    } else if(window.location.pathname.indexOf("wmap") > -1) {
        whiteMapClass.fetchPollingTemplate_wmap();
    } else {
        networkMapInstance.fetchPollingTemplate_gmap();
    }
});

/**
 * This event triggers when Poll Now button of live polling clicked
 * @event Click
 */
$("#fetch_polling").click(function(e) {
    networkMapInstance.fetchDevicesPollingData();
});

/**
 * This event triggers when Play button of live polling clicked
 * @event Click
 */
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

        if(window.location.pathname.indexOf("gearth") > -1) {
            earth_instance.startDevicePolling_earth();
        } else if(window.location.pathname.indexOf("wmap") > -1) {
            whiteMapClass.startDevicePolling_wmap();
        } else {
            networkMapInstance.startDevicePolling_gmap();
        }

    } else {
        bootbox.alert("Please select devices & polling template first.");
    }
});

/**
 * This event triggers when Pause button of live polling clicked
 * @event Click
 */
$("#pause_btn").click(function(e) {
    
    if($(".play_pause_btns").hasClass("disabled")) {
        $(".play_pause_btns").removeClass("disabled");
    }

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
});

/**
 * This event triggers when Stop button of live polling clicked
 * @event Click
 */
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

/**
 * This event triggers when polling technology dropdown changed
 * @event Change
 */
$("#polling_tech").change(function(e) {
    if(window.location.pathname.indexOf("wmap") > -1) {
        whiteMapClass.initLivePolling();
    } else if(window.location.pathname.indexOf("gearth") > -1) {
        earth_instance.initLivePolling_earth();
    } else {
        networkMapInstance.initLivePolling();
    }
});

/**
 * This event triggers when "Tabular View" button for polling widget clicked
 * @event Click
 */
$("#polling_tabular_view").click(function(e) {
    if(window.location.pathname.indexOf("wmap") > -1) {
        whiteMapClass.show_polling_datatable_wmaps();
    } else {
        networkMapInstance.show_polling_datatable();
    }
});

/**
 * This event triggers when clear selection button is clicked
 * @event Click
 */
$("#clearPolygonBtn").click(function(e) {
    if(window.location.pathname.indexOf("wmap") > -1) {
        whiteMapClass.stopPolling();
        hasSelectDevice = 0;
        get_page_status();
    } else if(window.location.pathname.indexOf("gearth") > -1) {
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

/**
 * This event triggers when icon size dropdown value changed
 * @event Change
 */
$("select#icon_Size_Select_In_Tools").change(function() {
    var val= $.trim($(this).val());
    defaultIconSize= val;

    current_icon_size = val;
    $.cookie("markerIconSize", val, {path: '/', secure : true});
    
    if(window.location.pathname.indexOf("wmap") > -1) {
        whiteMapClass.updateMarkersSize(val);
    } else if (window.location.pathname.indexOf("gearth") > -1) {
        earth_instance.updateAllMarkersWithNewIcon(val);
    } else {
        networkMapInstance.updateAllMarkersWithNewIcon_gmap(val);
        
    }
});

/**
 * This event triggers when "Add Ruler" button clicked
 * @event Click
 */
$("#ruler_select").click(function(e) {

    // Set/Reset variables
    pointAdded= -1;
    is_ruler_active= 1;
    is_line_active= -1;

    $(this).addClass("hide");
    $("#ruler_remove").removeClass("hide");

    if(window.location.pathname.indexOf("gearth") > -1) {
        if(pointEventHandler) {
            google.earth.removeEventListener(ge.getGlobe(), 'mousedown', pointEventHandler);
            pointEventHandler = "";
        }
        networkMapInstance.clearRulerTool_gmap();
        earth_instance.addRulerTool_earth();
    } else if(window.location.pathname.indexOf("wmap") > -1) {

    } else {
        google.maps.event.clearListeners(mapInstance, 'click');
        networkMapInstance.clearRulerTool_gmap();
        networkMapInstance.addRulerTool_gmap();
    }
});

/**
 * This event triggers when "Remove Ruler" button clicked
 * @event Click
 */
$("#ruler_remove").click(function(e) {
    pointAdded= -1;
    is_line_active= -1;
    is_ruler_active= -1;
    
    $(this).addClass("hide");
    $("#ruler_select").removeClass("hide");

    if(window.location.pathname.indexOf("gearth") > -1) {
        if(pointEventHandler) {
            google.earth.removeEventListener(ge.getGlobe(), 'mousedown', pointEventHandler);
            pointEventHandler = "";
        }
        networkMapInstance.clearRulerTool_gmap();
    } else if(window.location.pathname.indexOf("wmap") > -1) {

    } else {
        google.maps.event.clearListeners(mapInstance, 'click');
        // Change map cursor
        mapInstance.setOptions({'draggableCursor' : ''});
        networkMapInstance.clearRulerTool_gmap();
    }
});

/**
 * This event triggers when "Add Point" button clicked
 * @event Click
 */
$("#point_select").click(function(e) {
    pointAdded= 1;
    is_line_active= -1;
    is_ruler_active= -1;
    $(this).removeClass('btn-default').addClass('btn-warning');
    $("#point_icons_container li:first-child").trigger('click');
    $("#point_icons_container").removeClass("hide");

    if(window.location.pathname.indexOf("gearth") > -1) {
        if(pointEventHandler) {
            google.earth.removeEventListener(ge.getGlobe(), 'click', pointEventHandler);
            pointEventHandler = "";
        }
        networkMapInstance.addPointTool_gmap();
    } else if(window.location.pathname.indexOf("wmap") > -1) {
        // pass
    } else {
        google.maps.event.clearListeners(mapInstance, 'click');
        // Change map cursor
        mapInstance.setOptions({'draggableCursor' : 'default'});
        networkMapInstance.addPointTool_gmap();
    }
});

/**
 * This event triggers when close icon on point icons clicked
 * @event Click
 */
$("#close_points_icon").click(function(e) {
    
    pointAdded= -1;
    is_line_active= -1;
    is_ruler_active= -1;
    $("#point_select").removeClass('btn-warning').addClass('btn-default');
    $("#point_icons_container").addClass("hide");
    if(window.location.pathname.indexOf("gearth") > -1) {
        if(pointEventHandler) {
            google.earth.removeEventListener(ge.getGlobe(), 'click', pointEventHandler);
            pointEventHandler = "";
        }
    } else if(window.location.pathname.indexOf("wmap") > -1) {

    } else {
        google.maps.event.clearListeners(mapInstance, 'click');
        // Change map cursor
        mapInstance.setOptions({'draggableCursor' : ''});
    }
});

/**
 * This event triggers when "Remove Point" button clicked
 * @event Click
 */
$("#point_remove").click(function(e) {
    pointAdded= -1;
    is_line_active= -1;
    is_ruler_active= -1;
    $(this).addClass("hide");
    $("#point_icons_container").addClass("hide");

    if(window.location.pathname.indexOf("gearth") > -1) {
        if(pointEventHandler) {
            google.earth.removeEventListener(ge.getGlobe(), 'click', pointEventHandler);
            pointEventHandler = "";
        }
    } else if(window.location.pathname.indexOf("wmap") > -1) {

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
 * This event show/hide perf param label from SS markers
 * @event Click
 */

$("#show_hide_label").click(function(e) {
    $.cookie("isLabelChecked", e.currentTarget.checked, {path: '/', secure : true});

    for(var x=0;x<labelsArray_filtered.length;x++) {
        if(window.location.pathname.indexOf("gearth") > -1) {
            
        } else if(window.location.pathname.indexOf("wmap") > -1) {
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

        if(window.location.pathname.indexOf("gearth") > -1) {
            
        } else if(window.location.pathname.indexOf("wmap") > -1) {
            if(e.currentTarget.checked) {
                labelsArray[x].show();
            } else {
                labelsArray[x].hide();
            }
        } else {
            labelsArray[x].setVisible(e.currentTarget.checked);
        }

    }
});

/**
 * This event trigger when previous navigation button on polling widget clicked
 */
$("#navigation_container button#previous_polling_btn").click(function(e) {
    if(window.location.pathname.indexOf("wmap") > -1) {
        whiteMapClass.show_previous_polled_icon_wmaps();
    } else if(window.location.pathname.indexOf("gearth") > -1) {
        earth_instance.show_previous_polled_icon_earth();
    } else {
        networkMapInstance.show_previous_polled_icon();
    }
});

/**
 * This event trigger when next navigation button on polling widget clicked
 * @event Click
 */
$("#navigation_container button#next_polling_btn").click(function(e) {
   if(window.location.pathname.indexOf("wmap") > -1) {
        whiteMapClass.show_next_polled_icon_wmaps();
    } else if(window.location.pathname.indexOf("gearth") > -1) {
        earth_instance.show_next_polled_icon_earth();
    } else {
        networkMapInstance.show_next_polled_icon();
    }
});

/**
 * This event trigger when clicked on add point icons
 * @event Click
 */
$("#point_icons_container li").click(function(e) {

    /*Remove selected class from all li*/
    $("#point_icons_container li").removeClass('selected_icon');
    
    /*Add selected class to clicked li*/
    $(this).addClass('selected_icon');
    
    /*Check that 'img' tag is present in li or not*/
    if($("#point_icons_container li.selected_icon").children()[0].hasAttribute('src')) {
        point_icon_url = $("#point_icons_container li.selected_icon").children()[0].attributes.src.value;
    }
});

/**
 * This event triggers when close button on infowindow clicked
 * @event Click(Using Delegate)
 */
$('#infoWindowContainer').delegate('.close_info_window','click',function(e) {

    var current_target_attr = e.currentTarget.attributes,
        marker_key = current_target_attr['marker_key'] ? current_target_attr['marker_key'].value : "",
        marker_type = current_target_attr['marker_type'] ? current_target_attr['marker_type'].value : "";

    if(marker_key && marker_type) {
        if(window.location.pathname.indexOf('gearth') > -1) {
            // pass
        } else if(window.location.pathname.indexOf("wmap") > -1) {
            if(is_tooltip_polled_used) {
                var closed_marker = allMarkersObject_wmap[marker_type][marker_key];
                if(closed_marker) {
                    try {
                        // Update marker with the old icon
                        closed_marker.style.externalGraphic = closed_marker.oldIcon;
                        if (marker_type == 'sub_station') {
                            ccpl_map.getLayersByName('Markers')[0].redraw();
                        } else if(marker_type == 'sector_device') {
                            ccpl_map.getLayersByName('Devices')[0].redraw();
                        }
                    } catch(e) {
                        // console.log(e);
                    }

                    is_tooltip_polled_used = false;
                }
            }
        } else {
            if(is_tooltip_polled_used) {
                var closed_marker = allMarkersObject_gmap[marker_type][marker_key];
                if(closed_marker) {
                    closed_marker.setOptions({
                        "icon" : closed_marker.oldIcon
                    });
                    is_tooltip_polled_used = false;
                }
            }
        }
    }

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

/**
 * This event triggers when Download inventory button clicked clicked
 * @event Click(Using Delegate)
 */
$('#infoWindowContainer').delegate('.download_report_btn','click',function(e) {
    var item_id = e.currentTarget.attributes['item_id'] ? e.currentTarget.attributes['item_id'].value : "",
        type_report = e.currentTarget.attributes['type'] ? e.currentTarget.attributes['type'].value : "";
    // If ckt id exist then fetch l2 report url

    if(item_id) {
        
        // Disbale Download Report Button
        $(".download_report_btn").button("loading");

        $.ajax({
            url: base_url+'/network_maps/l2_report/'+encodeURIComponent(item_id)+'/'+encodeURIComponent(type_report)+'/',
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
                        
                        try {
                            window.open(url, '_blank').focus()
                        } catch(e) {
                            // console.log(e);
                        }
                    }
                } else {
                    bootbox.alert("No L2 Report Found.");
                }
            },
            error : function(err) {
                // console.log(err)max-;
            },
            complete : function() {
                // Disbale Download Report Button
                $(".download_report_btn").button("complete");
            }
        });
    }
});

/**
 * This event triggers when any polled param name is clicked
 * @event Click(Using Delegate)
 */
$('#infoWindowContainer').delegate('td','click',function(e) {

    var currentAttr = e.currentTarget.attributes,
        api_url = currentAttr['url'] ? currentAttr['url'].value : "";
    
    // If api_url exist then fetch l2 report url
    if(api_url && $('#topo_view_tab').length == 0) {
        // Show the loader
        showSpinner();

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

                        
                        if(typeof(table_headers[0]) == 'string') {

                            var table_data = result.data.objects.table_data ? result.data.objects.table_data : [];

                            contentHtml += createTableHtml_nocout(
                                'other_perf_table',
                                table_headers,
                                table_data,
                                false
                            );

                            contentHtml += "</div>";
                        } else {

                            contentHtml += "<div id='map_bottom_table'></div><div class='clearfix'></div>"
                        }
                        // /*Call the bootbox to show the popup with datatable*/
                        bootbox.dialog({
                            message: contentHtml,
                            title: '<i class="fa fa-dot-circle-o">&nbsp;</i> Performance    '
                        });

                        // // Update Modal width to 90%;
                        $(".modal-dialog").css("width","90%");

                        if(typeof(table_headers[0]) != 'string') {
                            initChartDataTable_nocout(
                                "other_perf_table",
                                table_headers,
                                "map",
                                "/"+api_url,
                                true
                            );
                        }

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
                            createHighChart_nocout(result.data.objects,'perf', false, false, function(status) {
                                // 
                            });

                            // Add data to table
                            addDataToChartTable_nocout(chartConfig, 'perf_data_table');
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
    if(window.location.pathname.indexOf('gearth') > -1) {
        earth_instance.exportData_earth();
    } else if(window.location.pathname.indexOf("wmap") > -1) {
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
 * This event trigger when any label is selected or changed from labels dropdown.
 * @event change
 */
$("#static_label").change(function(e) {

    if(($(this).val()) && ($(this).val() != last_selected_label)) {
        if(!$("#apply_label").hasClass("btn-default")) {
            $("#apply_label").addClass("btn-default");
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
        selected_text = $.trim($("#static_label option:selected").text()),
        param_label_gritter_title = 'SS Parameter Label';

    if(not_ss_param_labels.indexOf(selected_val) > -1) {
        param_label_gritter_title = 'BS Parameter Label';
    }

    if(last_selected_label != "" && selected_val == "" && selected_text == 'Select Label') {
        // Call Function to remove ss param label from map & updates button and dropdown
        removeSSParamLabel();

    } else {
        if((selected_val) && (selected_val != last_selected_label)) {

            if($("#apply_label").hasClass("btn-default")) {
                $("#apply_label").removeClass("btn-default");
            }

            if(!$("#apply_label").hasClass("btn-danger")) {
                $("#apply_label").addClass("btn-danger");
                $("#apply_label").html("Remove Label")
            }

            // Save selected value to global variable
            last_selected_label = selected_val;

            if(window.location.pathname.indexOf("gearth") > -1) {
                // Pass
                return true;
            } else if(window.location.pathname.indexOf("wmap") > -1) {
                if(ccpl_map && ccpl_map.getZoom() >= 4) {
                    networkMapInstance.updateTooltipLabel_gmap();
                } else {
                    $.gritter.add({
                        title: param_label_gritter_title,
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
                        title: param_label_gritter_title,
                        text: $.trim($("#static_label option:selected").text())+" - Label Applied Successfully.",
                        sticky: false,
                        time : 1000
                    });
                }
            }

            // Update cookie value with the selected value.
            $.cookie("tooltipLabel", last_selected_label, {path: '/', secure : true});
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
 *  This event triggers when service type radio button is changed
 * @event change
 */
$('input[type=radio][name=thematic_type]').change(function(e) {
    // Call function to restart perf calling
    networkMapInstance.restartPerfCalling();
});

/**
 * This event triggers when Tabs on infowindow clicked(or selected) 
 * @event Click(Using Delegate)
 */
$("#infoWindowContainer").delegate(".nav-tabs li a",'click',function(evt) {

    var current_device_id = evt.currentTarget.attributes.device_id ? evt.currentTarget.attributes.device_id.value : "",
        point_type = evt.currentTarget.attributes.point_type ? evt.currentTarget.attributes.point_type.value : "",
        dom_id = evt.currentTarget.attributes.id ? evt.currentTarget.attributes.id.value : "",
        device_tech = evt.currentTarget.attributes.device_tech ? evt.currentTarget.attributes.device_tech.value : "",
        device_type = evt.currentTarget.attributes.device_type ? evt.currentTarget.attributes.device_type.value : "",
        href_attr = evt.currentTarget.attributes.href ? evt.currentTarget.attributes.href.value.split("#") : "",
        block_id = href_attr.length > 1 ? href_attr[1] : "",
        pl_attr = evt.currentTarget.attributes.pl_value,
        device_pl = pl_attr && pl_attr.value != 'N/A' ? pl_attr.value : "";

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
                            tooltip_info_dict = fetched_polled_info;

                        if(point_type == 'sector_Marker' || point_type == 'sector') {
                            
                            if(ptp_tech_list.indexOf(device_tech) > -1) {
                                tooltip_info_dict = rearrangeTooltipArray(ptp_sector_toolTip_polled,fetched_polled_info);
                            } else if(device_tech == 'wimax') {
                                tooltip_info_dict = rearrangeTooltipArray(wimax_sector_toolTip_polled,fetched_polled_info);
                            } else if(device_tech == 'pmp') {
                                if(device_type == 'radwin5kbs') {
                                    tooltip_info_dict = rearrangeTooltipArray(pmp_radwin5k_sector_toolTip_polled, fetched_polled_info);
                                } else {
                                    tooltip_info_dict = rearrangeTooltipArray(pmp_sector_toolTip_polled, fetched_polled_info);
                                }
                            } else {
                                // pass
                            }
                        } else if(point_type == 'sub_station') {
                            if(ptp_tech_list.indexOf(device_tech) > -1) {
                                tooltip_info_dict = rearrangeTooltipArray(ptp_ss_toolTip_polled,fetched_polled_info);
                            } else if(device_tech == 'wimax') {
                                tooltip_info_dict = rearrangeTooltipArray(wimax_ss_toolTip_polled,fetched_polled_info);
                            } else if(device_tech == 'pmp') {                                
                                if(device_type == 'radwin5kss') {
                                    tooltip_info_dict = rearrangeTooltipArray(pmp_radwin5k_ss_toolTip_polled, fetched_polled_info);
                                } else {
                                    tooltip_info_dict = rearrangeTooltipArray(pmp_ss_toolTip_polled, fetched_polled_info);
                                }                                
                            } else {
                                // pass
                            }
                        } else if(point_type == 'base_station') {
                            if(device_tech == 'pine') {
                                tooltip_info_dict = rearrangeTooltipArray(mrotech_bh_toolTip_polled,fetched_polled_info);
                            } else if(device_tech == 'switch') {
                                tooltip_info_dict = rearrangeTooltipArray(switch_bh_toolTip_polled,fetched_polled_info);
                            } else if(device_tech == 'rici') {
                                tooltip_info_dict = rearrangeTooltipArray(rici_bh_toolTip_polled,fetched_polled_info);
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
                                // GET text color as per the severity of device
                                var severity = tooltip_info_dict[i]["severity"],
                                    severity_obj = nocout_getSeverityColorIcon(severity),
                                    text_color = severity_obj.color ? severity_obj.color : "",
                                    cursor_css = text_color ? "cursor:pointer;" : "";

                                // Url
                                url = tooltip_info_dict[i]["url"] ? tooltip_info_dict[i]["url"] : "";
                                text_class = "text-primary";

                                polled_data_html += "<tr style='color:"+text_color+";'><td url='"+url+"' style='"+cursor_css+"'>"+tooltip_info_dict[i]['title']+"</td>\
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

/**
 * This event triggers when Live polling button in Sector & SS tooltip rows clicked
 * @event Click(Using Delegate)
 */
$('#infoWindowContainer').delegate('.perf_poll_now','click',function(e) {

    var currentTarget = e.currentTarget,
        current_target_attr = currentTarget.attributes,
        current_table_childrens = $(currentTarget).parent().parent().children(),
        last_td_container = current_table_childrens[current_table_childrens.length - 1],
        service_name = current_target_attr['service_name'] ? current_target_attr['service_name'].value : "",
        ds_name = current_target_attr['ds_name'] ? current_target_attr['ds_name'].value : "",
        device_name = current_target_attr['device_name'] ? [current_target_attr['device_name'].value] : "",
        device_type = current_target_attr['device_type'] ? current_target_attr['device_type'].value : "",
        is_radwin5 = device_type && device_type.toLowerCase().indexOf('radwin5') > -1 ? 1 : 0,
        false_param = false,
        true_param = true;

        var extra_info_obj = {
            'container_dom_id': false_param,
            'sparkline_dom_id': false_param,
            'hidden_input_dom_id': false_param,
            'polled_val_shown_dom_id': false_param,
            'show_sparkline_chart': true_param,
            'is_radwin5': is_radwin5
        };

        if(service_name && ds_name && device_name) {
            // Disable all poll now buttons
            $(currentTarget).button('loading');

            // Call function to fetch live polling data
            nocout_livePollCurrentDevice(
                service_name,
                ds_name,
                device_name,
                extra_info_obj,
                function(live_polled_dict) {
                    // Disable all poll now buttons
                    $(currentTarget).button('complete');

                    if(live_polled_dict) {
                        var live_polled_html = "";

                        live_polled_html = "<span style='display:none;'>"+val_icon+" "+live_polled_dict["val"]+"<br/>\
                                           "+time_icon+" "+live_polled_dict["time"]+"</span>";

                        $(last_td_container).html(live_polled_html);
                        $(last_td_container).children().slideDown('slow')
                    } else {
                        $(last_td_container).html("");
                    }
                });
        } else {
            $.gritter.add({
                title: "Live Polling",
                text: "Please try again later.",
                sticky: false,
                time : 1000
            });
        }

});

/**
 * This event triggers when Poll Now button on top of Sector & SS tooltip clicked
 * @event Click(Using Delegate)
 */
$('#infoWindowContainer').delegate('.themetic_poll_now_btn','click',function(e) {

    var current_target_attr = e.currentTarget.attributes,
        device_name = current_target_attr['device_name'] ? [current_target_attr['device_name'].value] : "",
        marker_key = current_target_attr['marker_key'] ? current_target_attr['marker_key'].value : "",
        marker_type = current_target_attr['marker_type'] ? current_target_attr['marker_type'].value : "",
        device_type = current_target_attr['device_type'] ? current_target_attr['device_type'].value : "",
        is_radwin5 = device_type && device_type.toLowerCase().indexOf('radwin5') > -1 ? 1 : 0;

    var themetics_radio = $("input:radio[name=thematic_type]"),
        checked_themetics_radio = $("input:radio[name=thematic_type]"),
        selected_thematics = themetics_radio.length > 0 ? $("input:radio[name=thematic_type]:checked").val() : "normal";

    if(device_name && marker_key && marker_type) {
        var selected_marker = "";
        
        if(window.location.pathname.indexOf("wmap") > -1) {
            selected_marker = allMarkersObject_wmap[marker_type][marker_key];
        } else {
            selected_marker = allMarkersObject_gmap[marker_type][marker_key];
        }
        
        if(selected_marker && selected_marker.device_name == device_name) {
            // disable the button
            $(e.currentTarget).button('loading');

            // Make Ajax Call to Fetch Live Poll Data For opened device.
            $.ajax({
                url : base_url+"/"+"device/lp_bulk_data/?devices="+JSON.stringify(device_name)+"&ts_type="+selected_thematics+"&is_radwin5="+is_radwin5,
                type : "GET",
                success : function(response) {
                    var result = "";
                    // Type check of response
                    if(typeof response == 'string') {
                        result = JSON.parse(response);
                    } else {
                        result = response;
                    }

                    if(result.success == 1) {

                        var device_data_dict = result['data']['devices'][device_name[0]],
                            fetched_icon = device_data_dict && device_data_dict['icon'] ? device_data_dict['icon'] : "",
                            fetched_val = device_data_dict && device_data_dict['value'] ? device_data_dict['value'] : "",
                            polled_data_html = "",
                            dateObj = new Date(),
                            current_time = dateObj.getHours()+":"+dateObj.getMinutes()+":"+dateObj.getSeconds();

                        if(fetched_val  && fetched_val != "NA") {

                            // If value is array then use first index val
                            if(typeof fetched_val == 'object') {
                                fetched_val = fetched_val[0];
                            }

                            if(!isNaN(Number(fetched_val))) {
                                var existing_val = $("#infoWindowContainer #sparkline_val_input").val(),
                                    new_values_list = "";

                                if(existing_val) {
                                    new_values_list = existing_val+","+fetched_val;
                                } else {
                                    new_values_list = fetched_val;
                                }
                                
                                // Update the value in input field
                                $("#infoWindowContainer #sparkline_val_input").val(new_values_list);

                                // Make array of values from "," comma seperated string
                                var new_chart_data = new_values_list.split(",");

                                /*Plot sparkline chart with the fetched polling value*/
                                $("#infoWindowContainer #sparkline_container").sparkline(new_chart_data, {
                                    type: "line",
                                    lineColor: "blue",
                                    spotColor : "orange",
                                    defaultPixelsPerValue : 10
                                });
                            }
                        }

                        polled_data_html += '<span style="display:none;">'+val_icon+' '+fetched_val;
                        polled_data_html += '<br/>'+time_icon+' '+current_time+'</span>';

                        $("#infoWindowContainer #fetched_val_container").html(polled_data_html);

                        $("#infoWindowContainer #fetched_val_container span").slideDown('slow');

                        // If has icon then update marker with fetched icon.
                        if(fetched_icon) {
                            if(window.location.pathname.indexOf("wmap") > -1) {
                                try {
                                    // Update marker object with new icon
                                    selected_marker.style.externalGraphic = base_url+"/"+fetched_icon;
                                    // Get marker layer
                                    var layer = selected_marker.layer ? selected_marker.layer : selected_marker.layerReference;
                                    // Redraw layer to reflect the changes on map
                                    layer.redraw();
                                } catch(e) {
                                    // console.log(e);
                                }
                            } else {
                                var marker_img_object = gmap_self.getMarkerImageBySize(base_url+"/"+fetched_icon,"other");

                                // Update Marker Icon
                                selected_marker.setOptions({
                                    "icon" : marker_img_object
                                });
                            }

                            is_tooltip_polled_used = true;
                        }

                    } else {
                        $.gritter.add({
                            title: "Live Polling",
                            text: result.message,
                            sticky: false,
                            time : 1000
                        });
                    }
                },
                error : function(err) {
                    $.gritter.add({
                        title: "Live Polling",
                        text: err.statusText,
                        sticky: false,
                        time : 1000
                    });
                },
                complete : function() {
                    // enable the button
                    $(e.currentTarget).button('complete');
                }
            });

        }
    }
});

/**
 * This event triggers when technology(on live polling panel) changed.
 * @event change
 */
$('select[name="polling_tech"]').change(function(e) {
    var selected_tech = $.trim($(this).val());
    var selected_tech_name = $('select[name="polling_tech"] option:selected').text().toLowerCase();
   
    if (selected_tech && typeof tech_type_api != 'undefined') {
        var api_url = tech_type_api;

        // Update the tech PK in api url
        api_url = api_url.replace('123', selected_tech);

        $.ajax({
            url : api_url,
            type : 'GET',
            success : function(response) {
                var result = response;

                if (typeof response == 'string') {
                    result = JSON.parse(response);
                }

                var dType_html = '<option value="">Select Type</option>';

                for (var i=0;i<result.length;i++) {
                    if(ptp_tech_list.indexOf(selected_tech_name) == 1){
                        var title = result[i]['alias'],
                        id = result[i]['id'];
                        dType_html += '<option value="' + id + '">' + title + '</option>'                                              
                }
                    else{
                        var title = result[i]['alias'],
                        id = result[i]['id'];                       
                       if(title.indexOf('SS') !== -1)
                        {
                            dType_html += '<option value="' + id + '">' + title + '</option>'
                        }

                    }
            }

                $('select[name="polling_type"]').html(dType_html);
            },
            error : function(err) {
                // console.log(err.statusText);
            }
        })
    }
});

/**
 * This funciton returns the page name of currenly opened page
 * @method getPageType
 */
function getPageType() {

    if(window.location.pathname.indexOf("gearth") > -1) {
        mapPageType = "gearth";
        gmap_self = networkMapInstance;
    } else if(window.location.pathname.indexOf("wmap") > -1) {
        mapPageType = "wmap";
        networkMapInstance = gmap_self;
    } else {
        mapPageType = "gmap";
    }
}

/**
 * This function display advance search form 
 * @method showAdvSearch
 */
function showAdvSearch() {
    showSpinner();
    if(!isAdvanceFilter) {
        $("#filter_technology").select2("val","");
        $("#filter_vendor").select2("val","");
        $("#filter_state").select2("val","");
        $("#filter_city").select2("val","");
        $("#filter_frequency").select2("val","");
        $("#filter_polarization").select2("val","");
        $("#filter_antena_type").select2("val","");

        // Reset Advance Filters Flag
        isAdvanceFilter = 0;
    }
    if(!$("#advFilterContainerBlock").hasClass("hide")) {
        $("#advFilterContainerBlock").addClass("hide");
    }

    if($("#advSearchContainerBlock").hasClass("hide")) {
        $("#advSearchContainerBlock").removeClass("hide");
    }
    else{
      $("#advSearchContainerBlock").addClass("hide");  
    }
    hideSpinner();
}

/**
 * This function trigger event to reset the advance search form 
 * @method resetAdvanceSearch
 */
function resetAdvanceSearch() {
    $("#resetSearchForm").trigger('click');
}

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
    else{
        $("#advFilterContainerBlock").addClass("hide");
    }
    hideSpinner();
}

/**
 * This function triggers when remove filters button is clicked
 * @method removeAdvFilters
 */
function removeAdvFilters() {
    /*Reset advance filter status flag*/
    hasAdvFilter = 0;

    advSearch.removeFilters();

    /*Call get_page_status function to show the current status*/
    get_page_status();
}

/**
 * This function set the page status as per the tools usability
 * @method get_page_status
 */
function get_page_status() {
    var status_txt = "";

    if(hasAdvFilter == 1) {
        status_txt+= '<li>Advance Filters Applied</li>';
    }

    if(hasSelectDevice == 1) {
        status_txt+= '<li>Select Devices Applied</li>';
    }

    if(hasTools == 1) {
        if(isFreeze == 1 || (tools_ruler && tools_ruler != 0)) {
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

/**
 * Function is used to Disable Advance Search, Advance Filter Button when Call for data is going on.
   When call is completed, we use the same function to enable Button by passing 'no' in parameter.
 * @method disableAdvanceButton
 * @param {String} status , It contains the info either to enable/disable buttons
 */
function disableAdvanceButton(status) {
    var buttonEls = ['advSearchBtn', 'advFilterBtn', 'createPolygonBtn', 'showToolsBtn','export_data_gmap', 'resetFilters'],
        selectBoxes = ['technology', 'vendor', 'state', 'city'],
        textBoxes = ['google_loc_search','lat_lon_search'],
        disablingBit = false;

    if(!status) {
        disablingBit= true;
        for(var i=0; i< buttonEls.length; i++) {
            try {
                $('#'+buttonEls[i]).button('loading');
            } catch(e) {
                // console.error(e);
            }
        }

        for(var i=0; i< selectBoxes.length; i++) {
            try {
                document.getElementById(selectBoxes[i]).disabled = disablingBit;
            } catch(e) {
                // console.error(e);
            }
        }

        for(var i=0; i< textBoxes.length; i++) {
            try {
                var el = document.getElementById(textBoxes[i]);
                if(el) {
                    document.getElementById(textBoxes[i]).disabled = disablingBit;    
                }
            } catch(e) {
                // console.error(e);
            }
        }
    } else {
        disablingBit= false;
        for(var i=0; i< buttonEls.length; i++) {
            try {
                $('#'+buttonEls[i]).button('complete');
            } catch(e) {
                // console.error(e);
            }
        }

        for(var i=0; i< selectBoxes.length; i++) {
            try {
                document.getElementById(selectBoxes[i]).disabled = disablingBit;    
            } catch(e) {
                // console.error(e);
            }
        }

        for(var i=0; i< textBoxes.length; i++) {
            try {
                var el = document.getElementById(textBoxes[i]);
                if(el) {
                    document.getElementById(textBoxes[i]).disabled = disablingBit;    
                }
            } catch(e) {
                // console.error(e);
            }
        }
    }
}

/**
 * This event triggers keypress event on lat,lon search text box
 * @method isLatLon
 * @param {Object} evt, It contains the event object
 */
function isLatLon(evt) {

    var entered_key_code = (evt.keyCode ? evt.keyCode : evt.which),
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
                        if(window.location.pathname.indexOf("wmap") > -1) {
                            whiteMapClass.zoomToLonLat(entered_txt);
                        } else if(window.location.pathname.indexOf("gearth") > -1) {
                            earth_instance.pointToLatLon(entered_txt);
                        } else {
                            networkMapInstance.pointToLatLon(entered_txt);
                        }
                    } else {
                        var converted_lat = dmsToDegree(dms_regex.exec(lat));
                        var converted_lng = dmsToDegree(dms_regex.exec(lng));
                        
                        if(window.location.pathname.indexOf("wmap") > -1) {
                            whiteMapClass.zoomToLonLat(String(converted_lat)+","+String(converted_lng));
                        } else if(window.location.pathname.indexOf("gearth") > -1) {
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

/**
 * This function converts dms lat lon to decimal degree lat lon
 * @method dmsToDegree
 * @param {Array} latLng, It conatains the lat-lon array
 */
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

/**
 * This function shows tools panel to google map
 * @method showToolsPanel
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

    $("#showToolsBtn").addClass("hide");

    $("#removeToolsBtn").removeClass("hide");

    $("#toolsContainerBlock").removeClass("hide");

    if(window.location.pathname.indexOf("gearth") > -1) {

    } else if(window.location.pathname.indexOf("wmap") > -1) {
    } else {
        google.maps.event.clearListeners(mapInstance, 'click');
    }
}

/**
 * This function hide the tools panel
 * @method removetoolsPanel
 */
function removetoolsPanel() {
    pointAdded= -1;
    is_line_active= -1;
    is_ruler_active= -1;

    if(window.location.pathname.indexOf("gearth") > -1) {
        // pass
    } else if(window.location.pathname.indexOf("wmap") > -1) {
        // pass
    } else {
        google.maps.event.clearListeners(mapInstance, 'click');
    }    

    $("#showToolsBtn").removeClass("hide");

    if(
        isFreeze == 1
        ||
        (tools_ruler && tools_ruler != 0)
        ||
        (
            $.cookie("isLabelChecked")
            ||
            $.cookie("isLabelChecked")=='true'
        )
    ) {
        $("#showToolsBtn").removeClass("btn-default").addClass("btn-warning");
    } else {
        $("#showToolsBtn").removeClass("btn-warning").addClass("btn-default");
    }

    $("#removeToolsBtn").addClass("hide");

    $("#toolsContainerBlock").addClass("hide");

    get_page_status();
}

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
 * This function get the current status & show it on gmap/google earth page.
 * @method clearTools_gmap
 */
function clearTools_gmap() {
    google.maps.event.clearListeners(mapInstance,'click');
    networkMapInstance.clearRulerTool_gmap();
    is_line_active = 0;
    bootbox.confirm("Do you want to reset Maintenance Points too?", function(result) {
        if(result) {
            pointAdded = -1;            
            hasTools = 0;
            networkMapInstance.clearPointsTool_gmap();
            $("#showToolsBtn").addClass("btn-default");
            $("#showToolsBtn").removeClass("btn-warning");
        }
    });   
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

    gexInstance.util.flyToObject(folder);
    isFromSearch = true;
    callback();
}

/**
 * This function checks object equality
 * @method objectsAreSame
 */
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

/**
 * This function checks array equality
 * @method arraysEqual
 */
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

/**
 * This function checks that the marker is in states or not
 * @method checkIfMarkerIsInState
 */
function checkIfMarkerIsInState(marker, array_state_name) {
    var isMarkerPresent = false,
        lower_array_state_name = array_state_name.map(function(x) {
            return x.name.toLowerCase();
        }),
        i = 0;

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

/**
 * This function returns the current zoom level
 * @method getEarthZoomLevel
 */
function getEarthZoomLevel() {
    var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);
    return lookAt.getRange();
}

/**
 * This function set the zoom level for google earth as per given altitude
 * @method setEarthZoomLevel
 * @param {Number} alt, It contains the altitude value
 */
function setEarthZoomLevel(alt) {
    var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);
    return lookAt.setRange(alt);
}

/**
 * This function updates placemark with new icon
 * @method updateGoogleEarthPlacemark
 * @param {Object} placemark, It contain the google earth placemark object
 * @param {Object} newSize, It contain new icon url
 */
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

/**
 * This function updates the size of given placemark
 * @method updateGoogleEarthPlacedmarkNewSize
 * @param {Object} placemark, It contain the google earth placemark object
 * @param {Object} newSize, It contain the scale object for new size
 */
function updateGoogleEarthPlacedmarkNewSize(placemark, newSize) {
    // Define a custom icon.next_polling_btn
    var icon = ge.createIcon('');
    icon.setHref(placemark.icon);
    var style = ge.createStyle('');
    style.getIconStyle().setIcon(icon);
    style.getIconStyle().setScale(newSize);
    placemark.setStyleSelector(style);
}

/**
 * This function return the current bound coordinates of google earth
 * @method getCurrentEarthBoundPolygon
 */
function getCurrentEarthBoundPolygon() {
    var poly = [];
    var globeBounds = ge.getView().getViewportGlobeBounds();
    poly = [ {lat: globeBounds.getNorth(), lon: globeBounds.getWest()}, {lat: globeBounds.getNorth(), lon: globeBounds.getEast()}, {lat: globeBounds.getSouth(), lon: globeBounds.getEast()},{lat: globeBounds.getSouth(), lon: globeBounds.getWest()}, {lat: globeBounds.getNorth(), lon: globeBounds.getWest()} ];
    return poly;
}

/**
 * This function shows the baloon(infowindow) on given feature
 * @method openGoogleEarthBaloon
 * @param {String} innerHtml, It contain the HTML string which has to be shown on baloon
 * @param {Object} feature, It contain the google earth feature object
 */
function openGoogleEarthBaloon(innerHtml, feature) {
    var balloon = ge.createHtmlDivBalloon('');
    balloon.setFeature(feature);
    var div = document.createElement('DIV');
    div.innerHTML = innerHtml;
    balloon.setContentDiv(div);
    ge.setBalloon(balloon);
}

/**
 * This function converts given zoom level to altitude
 * @method ZoomToAlt
 * @param {Number} zoom, It contain the zoom level value
 */
function ZoomToAlt(zoom) {
    return altZoomList[zoom < 0 ? 0 : zoom > 21 ? 21 : zoom];
}

/**
 * This function converts given altitude to zoom level
 * @method AltToZoom
 * @param {Number} alt, It contain the altitude value
 */
function AltToZoom(alt) {
    for (var i = 0; i < 22; ++i) {
        if (alt > altZoomList[i] - ((altZoomList[i] - altZoomList[i+1]) / 2)) return i;
    }
    return 10;
}

/**
 * This function returns google earth range in zoom level as per the current altitude
 * @method getRangeInZoom
 */
function getRangeInZoom() {
    var earthRange = getEarthZoomLevel();
    return AltToZoom(earthRange);
}

/**
 * This function removes specific placemark from google earth
 * @method deleteGoogleEarthPlacemarker
 */
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
 * This function removes the ss param label & updated the button text & dropdown
 * @method removeSSParamLabel
 */
function removeSSParamLabel() {
    $("#static_label").val($("#static_label option:first").val());
    // Save selected value to global variable
    last_selected_label = "";
    // Update cookie value with the selected value.
    $.cookie("tooltipLabel", last_selected_label, {path: '/', secure : true});

    if(window.location.pathname.indexOf("gearth") > -1) {
        
    } else if(window.location.pathname.indexOf("wmap") > -1) {
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

    if(!$("#apply_label").hasClass("btn-default")) {
        $("#apply_label").addClass("btn-default");
        $("#apply_label").html("Apply Label")
    }

    if($("#apply_label").hasClass("btn-danger")) {
        $("#apply_label").removeClass("btn-danger");
    }
}

/**
 * This function returns the in bound BS id's list
 * @method getMarkerInCurrentBound
 * @param only_bs_ids {Boolean}, If conatins the boolean flag, either to sent bs ids chunk or single array
 * @return {Array}, List of in bound base stations id
 */
function getMarkerInCurrentBound(only_bs_ids) {

    var bsMarkersInBound = [],
        allBSObject = {};

    if(window.location.pathname.indexOf("gearth") > -1) {
        allBSObject = allMarkersObject_earth['base_station'];
    } else if(window.location.pathname.indexOf("wmap") > -1) {
        allBSObject = allMarkersObject_wmap['base_station'];
    } else {
        allBSObject = allMarkersObject_gmap['base_station'];
    }

    // Loop Bs markers to get which are in current bounds
    for(var key in allBSObject) {
        if(allBSObject.hasOwnProperty(key)) {
            var markerVisible = "";
            if(window.location.pathname.indexOf("gearth") > -1) {
                var earthBounds = getCurrentEarthBoundPolygon();
                markerVisible =  isPointInPoly(earthBounds, {lat: allBSObject[key].ptLat, lon: allBSObject[key].ptLon});
            } else if(window.location.pathname.indexOf("wmap") > -1) {
                markerVisible =  whiteMapClass.checkIfPointLiesInside({lat: allBSObject[key].ptLat, lon: allBSObject[key].ptLon});
            } else {
                markerVisible = mapInstance.getBounds().contains(allBSObject[key].getPosition());
                // If marker is present in bounds but not visible then set markerVisible to false
                if(markerVisible && !allBSObject[key].map && !allBSObject[key].isActive) {
                    markerVisible = false;
                }
            }
            if(markerVisible) {
                bsMarkersInBound.push(allBSObject[key]['filter_data']['bs_id']);
            }
        }
    }

    if(search_element_bs_id.length > 0) {
        // Update the array sequence to sent the search item call at first
        var unsearched_bs_ids = gisPerformanceClass.get_intersection_bs(search_element_bs_id,bsMarkersInBound);
        bsMarkersInBound = search_element_bs_id;
        bsMarkersInBound = bsMarkersInBound.concat(unsearched_bs_ids);
    }

    var chunk_size = periodic_poll_process_count,
        returned_bs_array  = [];

    if(!only_bs_ids) {
        returned_bs_array = createArrayChunks(bsMarkersInBound, chunk_size);
    } else {
        returned_bs_array = bsMarkersInBound;
    }

    return returned_bs_array;
}

/**
 * This function creates chunks of given array as per given chunk size
 * @method createArrayChunks
 * @param data_array {Array}, It is the items array
 * @param chunk_size {Number}, It is the size of chunks to be created
 */
function createArrayChunks(data_array, chunk_size) {

    var chunks_array = [],
        non_null_array = convertChunksToNormalArray(data_array);

    if(non_null_array && non_null_array.length > 0) {
        while (non_null_array.length > 0) {
            chunks_array.push(non_null_array.splice(0, chunk_size));
        }
    }

    return chunks_array;
}

/**
 * This function creates non null normal array from given chunks or normal array
 * @method convertChunksToNormalArray
 * @param data_array {Array}, It is the items chunks array
 * @param chunk_size {Number}, It is the size of chunks to be created
 */
function convertChunksToNormalArray(chunks_array) {
    var simple_array = chunks_array.join(',').split(','),
        non_null_array = [];

    for(var i=0;i<simple_array.length;i++) {
        if(simple_array[i] && non_null_array.indexOf(simple_array[i]) == -1)  {
            non_null_array.push(simple_array[i]);
        }
    }

    return non_null_array;
}

/**
 * This function show the cursor coordinates on mouse move
 * @method displayCoordinates
 * @param {Object} pnt, It contains the current point object
 */
function displayCoordinates(pnt) {
    var coordsLabel = $("#cursor_lat_long"),
        lat = pnt.lat(),
        lng = pnt.lng();
        
        lat = lat.toFixed(4);
        lng = lng.toFixed(4);

        coordsLabel.html("Latitude: " + lat + "  Longitude: " + lng);
}

/**
 * This function remove sector markers from map & reset the variables
 * @method clearPreviousSectorMarkers
 */
function clearPreviousSectorMarkers() {

    for(var i=0; i< sectorMarkersInMap.length; i++) {
        sectorMarkersInMap[i].setMap(null);
    }
    for(var i=0; i< sectorOmsMarkers.length; i++) {
        oms.removeMarker(sectorOmsMarkers[i]);
    }
    sectorMarkersInMap= [];
    sectorOmsMarkers= [];
}

/**
 * This function prepares required oms(overlappingmarkerspiderfier) object
 * @method clearPreviousSectorMarkers
 */
function prepare_oms_object(oms_instance) {
    
    oms_instance.addListener('click', function(marker,e) {

        var image = base_url+'/'+point_icon_url;
        if(pointAdded === 1) {
            
            connected_end_obj = {
                "lat" : e.latLng.lat(),
                "lon" : e.latLng.lng()
            };

            if(current_point_for_line) {
                gmap_self.plot_point_line(marker);
            }

            return ;
        }

        if(is_line_active == 1) {
            is_bs_clicked = 1;
            line_pt_array.push(e.latLng);
            return ;
        }   

        var sectorMarker,
            sectorMarkerOms;
        
        if(marker.pointType === "base_station") {
            //if marker is not spiderfied, stop event and add sector markers here and in oms
            if(!marker.isMarkerSpiderfied) {
                var sectorMarkersAtThePoint = sectorMarkersMasterObj[marker.name];
                if(sectorMarkersAtThePoint && sectorMarkersAtThePoint.length) {
                    for(var j=0; j< sectorMarkersAtThePoint.length; j++) {
                        if(sectorMarkersAtThePoint[j].isActive == 1) {
                            sectorMarker = sectorMarkersAtThePoint[j].setMap(mapInstance);
                            sectorMarkersInMap.push(sectorMarker);
                            sectorMarkerOms = oms.addMarker(sectorMarkersAtThePoint[j]);
                            sectorOmsMarkers.push(sectorMarkerOms);
                        }
                    }
                }
                marker.isMarkerSpiderfied= true;
                google.maps.event.trigger(marker, 'click');
                return ;
            }
        }

        /*Call the function to create info window content*/
        gmap_self.makeWindowContent(marker, function(content) {
            /*Set the content for infowindow*/
            $("#infoWindowContainer").html(content);
            $("#infoWindowContainer").removeClass('hide');
        });
    });

    /*Event when the markers cluster expands or spiderify*/
    oms_instance.addListener('spiderfy', function(e,markers) {
        /*Change the markers icon from cluster icon to thrie own icon*/
        for(var i=0;i<e.length;i++) {

            if(isPollingActive) {
                if(e[i].icon.url.indexOf('1x1.png') == -1) {
                    /*Change the icon of marker*/
                    e[i].setOptions({"icon":e[i].icon});
                } else {
                    /*Change the icon of marker*/
                    e[i].setOptions({"icon":e[i].oldIcon});
                }
            } else {
                /*Change the icon of marker*/
                e[i].setOptions({"icon":e[i].oldIcon});
            }

            for(var j=0;j<ssLinkArray.length;j++) {

                var pt_type = $.trim(e[i].pointType);
                if(pt_type == "sub_station") {
                    if($.trim(ssLinkArray[j].ssName) == $.trim(e[i].name)) {
                        var pathArray = [];
                        pathArray.push(new google.maps.LatLng(ssLinkArray[j].bs_lat,ssLinkArray[j].bs_lon));                        
                        pathArray.push(new google.maps.LatLng(e[i].position.lat(),e[i].position.lng()));
                        ssLinkArray[j].setPath(pathArray);
                    }
                } else if(pt_type == "base_station") {
                    if($.trim(ssLinkArray[j].bsName) == $.trim(e[i].name)) {
                        var pathArray = [];

                        pathArray.push(new google.maps.LatLng(e[i].position.lat(),e[i].position.lng()));
                        pathArray.push(new google.maps.LatLng(ssLinkArray[j].ss_lat,ssLinkArray[j].ss_lon));
                        ssLinkArray[j].setPath(pathArray);
                    }
                } else if(pt_type == "sector_Marker") {
                    if($.trim(ssLinkArray[j].sectorName) == $.trim(e[i].sectorName)) {
                        var pathArray = [];
                        pathArray.push(new google.maps.LatLng(e[i].position.lat(),e[i].position.lng()));
                        pathArray.push(new google.maps.LatLng(ssLinkArray[j].ss_lat,ssLinkArray[j].ss_lon));
                        ssLinkArray[j].setPath(pathArray);
                    }
                }
            }
        }
        infowindow.close();
    });

    /*Event when markers cluster is collapsed or unspiderify*/
    oms_instance.addListener('unspiderfy', function(e,markers) {
        //un freeze the map when in normal state
        // isFreeze = 0;
        var latArray = [],
            lonArray = [];
            
        $.grep(e, function (elem) {
            latArray.push(elem.ptLat);
            lonArray.push(elem.ptLon);
        });

        /*Reset the marker icon to cluster icon*/
        for(var i=0; i< e.length; i++) {
            var latCount= $.grep(latArray, function(elem) {return elem=== e[i].ptLat;}).length;
            var lonCount = $.grep(lonArray, function (elem) {return elem === e[i].ptLon;}).length;
            if(lonCount> 1 && latCount> 1) {
                if(isPollingActive) {
                    /*Change the icon of marker*/
                    e[i].setOptions({"icon":e[i].icon});
                } else {
                    //change all to cluster icon
                    e[i].setOptions({"icon": e[i].clusterIcon});
                }
            }
            for(var j=0;j<ssLinkArray.length;j++) {
                var pt_type = $.trim(e[i].pointType);


                if(pt_type == "sub_station") {
                    if($.trim(ssLinkArray[j].ssName) == $.trim(e[i].name)) {
                        var pathArray = [];
                        pathArray.push(new google.maps.LatLng(ssLinkArray[j].bs_lat,ssLinkArray[j].bs_lon));
                        pathArray.push(new google.maps.LatLng(e[i].ptLat,e[i].ptLon));                      
                        ssLinkArray[j].setPath(pathArray);
                    }
                } else if(pt_type == "base_station") {
                    if($.trim(ssLinkArray[j].bsName) == $.trim(e[i].name)) {
                        var pathArray = [];
                        pathArray.push(new google.maps.LatLng(ssLinkArray[j].bs_lat,ssLinkArray[j].bs_lon));
                        pathArray.push(new google.maps.LatLng(ssLinkArray[j].ss_lat,ssLinkArray[j].ss_lon));
                        ssLinkArray[j].setPath(pathArray);
                    }
                } else if(pt_type == "sector_Marker") {
                    if($.trim(ssLinkArray[j].sectorName) == $.trim(e[i].sectorName)) {
                        var pathArray = [];
                        pathArray.push(new google.maps.LatLng(ssLinkArray[j].sector_lat,ssLinkArray[j].sector_lon));
                        pathArray.push(new google.maps.LatLng(ssLinkArray[j].ss_lat,ssLinkArray[j].ss_lon));
                        ssLinkArray[j].setPath(pathArray);
                    }
                }
            }
        }

        for(var i=0; i< e.length; i++) {
            if(e[i].name==="base_station") {
                clearPreviousSectorMarkers();
                e[i].isMarkerSpiderfied = false;
            }
        }
    });
}

/**
 * This function manages the gmap full screen control feature
 * @method FullScreenCustomControl
 */
function FullScreenCustomControl(controlDiv, map) {

    // Set CSS styles for the DIV containing the control
    // Setting padding to 5 px will offset the control
    // from the edge of the map
    controlDiv.style.padding = '5px';

    $(controlDiv).addClass('custom_fullscreen');

    // Set CSS for the control border
    var controlUI = document.createElement('div');
    controlUI.style.backgroundColor = 'white';
    controlUI.style.borderStyle = 'solid';
    controlUI.style.borderWidth = '1px';
    controlUI.style.borderColor = '#717b87';
    controlUI.style.cursor = 'pointer';
    controlUI.style.textAlign = 'center';
    controlUI.title = 'Click here to full screen';
    controlDiv.appendChild(controlUI);

    // Set CSS for the control interior
    var controlText = document.createElement('div');

    controlText.style.fontFamily = 'Roboto,Arial,sans-serif';
    controlText.style.fontSize = '11px';
    controlText.style.fontWeight = '400';
    controlText.style.paddingTop = '1px';
    controlText.style.paddingBottom = '1px';
    controlText.style.paddingLeft = '6px';
    controlText.style.paddingRight = '6px';
    controlText.innerHTML = '<b>Full Screen</b>';
    controlUI.appendChild(controlText);

    // Setup the click event listeners: simply set the map to
    google.maps.event.addDomListener(controlUI, 'click', function() {
        var currentMode = $(this).find('b').html();
        if(currentMode === "Full Screen") {
            $(this).find('b').html("Exit Full Screen");
        } else {
            $(this).find('b').html("Full Screen");
        }
        $("#goFullScreen").trigger('click');
    });
}

/**
 * This function fetch the static info for any element(bs or ss or sector)
 * @method getStaticInfo
 */
function getStaticInfo(clicked_obj, callback) {

    if (!clicked_obj) {
        callback(clicked_obj);
    }

    var point_type = clicked_obj.pointType ? $.trim(clicked_obj.pointType).toLowerCase() : '';

    // If static info already fetched then callback from here
    if (['sector', 'sector_marker', 'sub_station', 'base_station'].indexOf(point_type) > -1) {
        if (clicked_obj.dataset && clicked_obj.dataset.length > 0) {
            callback(clicked_obj);
        }
    } else {
        if (
            clicked_obj.bs_dataset
            &&
            clicked_obj.bs_dataset.length > 0
            &&
            clicked_obj.ss_dataset
            &&
            clicked_obj.ss_dataset.length > 0
        ) {
            callback(clicked_obj);
        }
    }

    var elem_id = '',
        child_id = '',
        elem_tech = '',
        elem_type = '',
        technology = '';

    if (point_type == 'base_station') {
        try {
            elem_id = clicked_obj.filter_data.bs_id;
            elem_tech = clicked_obj.bh_device_tech;
            elem_type = clicked_obj.bh_device_type;
        } catch(e) {

        }
    } else if (point_type == 'sub_station') {
        try {
            elem_id = clicked_obj.filter_data.id;
            elem_tech = clicked_obj.technology;
            elem_type = clicked_obj.device_type;
        } catch(e) {

        }

    } else if (point_type == 'sector_marker' || point_type == 'sector') {
        try {
            elem_id = clicked_obj.filter_data.id;
            elem_tech = clicked_obj.technology;
            elem_type = clicked_obj.device_type;
        } catch(e) {

        }

    } else if (point_type == 'path') {
        try {
            elem_id = clicked_obj.filter_data.bs_id;
            child_id = clicked_obj.filter_data.ss_id;
        } catch(e) {

        }

    } else {
        callback(clicked_obj);
    }

    if (point_type && elem_id) {

        var get_params = 'elem_type='+point_type+'&elem_id='+elem_id+'&child_id='+child_id;

        // Make Ajax Call
        $.ajax({
            url: base_url + '/network_maps/get_infowindow_content/?'+ get_params,
            type: 'GET',
            success: function(response) {
                var result = response;

                if (typeof(response) == 'string') {
                    result = JSON.parse(response);
                }

                if (result.success) {

                    if (['sector', 'sector_marker', 'sub_station'].indexOf(point_type) > -1) {
                        clicked_obj['dataset'] = result.data;
                    } else if (['base_station'].indexOf(point_type) > -1) {
                        clicked_obj['dataset'] = result.data.base_station;
                        clicked_obj['bh_dataset'] = result.data.backhaul;
                    } else {
                        clicked_obj['bs_dataset'] = result.data.base_station;
                        clicked_obj['ss_dataset'] = result.data.sub_station;
                    }
                    callback(clicked_obj);
                } else {
                    callback(clicked_obj);
                }
            },
            error: function() {
                callback(clicked_obj);
            }
        });
    } else {
        callback(clicked_obj);
    }
}


/**
 * This function returns device marker JSON info object for creating device marker
 * @method getMarkerInfoJson
 * @param info_obj {Object}, It contains the complete info for the marker required to create marker specific info object
 * @param elem_type {String}, It contains the type of element/marker it is(base_station, sector, sector_polygon or sub_station)
 * @param extra_info {Object}, It contains the extra details required for given marker
 * @return required_info {Object}, It contains the marker info json object
 */
function getMarkerInfoJson(info_obj, elem_type, extra_info) {
    var required_info = {};

    if (!info_obj || !elem_type) {
        return required_info;
    }

    if (elem_type == 'base_station') {
        var fetched_status = info_obj.maintenance_status,
            bs_maintenance_status = fetched_status ? $.trim(fetched_status) : "No",
            bs_lat = info_obj.lat,
            bs_topo_url = info_obj.topo_view_url ? info_obj.topo_view_url : "",
            bs_lon = info_obj.lon;

        required_info = {
            ptLat              : bs_lat,
            ptLon              : bs_lon,
            bh_id              : info_obj.bh_id,
            bh_device_id       : info_obj.bh_device_id,
            bh_device_type     : info_obj.bh_device_type,
            bh_device_tech     : info_obj.bh_device_tech,
            pl                 : "",
            pointType          : 'base_station',
            maintenance_status : bs_maintenance_status,
            device_name        : info_obj.device_name,
            dataset            : info_obj.dataset ? info_obj.dataset : [],
            bh_dataset         : info_obj.bh_dataset ? info_obj.bh_dataset : [],
            bhInfo_polled      : [],
            topo_url           : bs_topo_url,
            bhSeverity         : "",
            bs_name            : info_obj.name,
            alias              : info_obj.alias,
            bs_alias           : info_obj.alias,
            name               : info_obj.name,
            filter_data        : extra_info,
            markerType         : 'BS',
            isMarkerSpiderfied : false,
            isActive           : false,
            windowTitle        : "Base Station"
        };

    } else if (elem_type == 'sector' || elem_type == 'sector_polygon') {

        var sector_perf_url = info_obj.perf_page_url ? info_obj.perf_page_url : "",
            sector_inventory_url = info_obj.inventory_url ? info_obj.inventory_url : "",
            sector_topo_url = info_obj.topo_view_url ? info_obj.topo_view_url : "",
            fetched_azimuth = info_obj.azimuth_angle,
            fetched_beamWidth = info_obj.beam_width,
            rad = info_obj.radius && Number(info_obj.radius) > 0 ? info_obj.radius : 0.5,
            azimuth = fetched_azimuth && fetched_azimuth != 'NA' ? fetched_azimuth : 10,
            beam_width = fetched_beamWidth && fetched_beamWidth != 'NA' ? fetched_beamWidth : 10,
            bg_color = info_obj.color && info_obj.color != 'NA' ? info_obj.color : 'rgba(74,72,94,0.58)'
            pointType = '',
            polarisation = '';

        if(elem_type == 'sector') {
            pointType = 'sector_Marker';
        } else {
            pointType = 'sector';
        }

        required_info = {
            ptLat                 : extra_info.bs_lat,
            ptLon                 : extra_info.bs_lon,
            alias                 : info_obj.ip_address,
            pointType             : pointType,
            technology            : info_obj.technology,
            device_type           : info_obj.device_type,
            vendor                : info_obj.vendor,
            dataset               : info_obj.dataset ? info_obj.dataset : [],
            poll_info             : [],
            pl                    : "",
            rta                   : "",
            radius                : rad,
            azimuth               : azimuth,
            beam_width            : beam_width,
            polarisation          : polarisation,
            bg_color              : bg_color,
            link_status           : info_obj.link_status ? info_obj.link_status : 'NA',
            link_status_timestamp : info_obj.link_status_timestamp ? info_obj.link_status_timestamp : 'NA',
            perf_url              : sector_perf_url,
            topo_url              : sector_topo_url,
            inventory_url         : sector_inventory_url,
            sectorName            : info_obj.ip_address,
            sector_child          : info_obj.sub_stations,
            sector_id             : info_obj.sector_id,
            device_id             : info_obj.device_id ? info_obj.device_id : '',
            device_name           : info_obj.device_name,
            name                  : info_obj.device_name,
            filter_data           : extra_info.filter_info,
            sector_lat            : extra_info.startLat,
            sector_lon            : extra_info.startLon,
            cktId                 : "",
            antenna_height        : info_obj.antenna_height,
            isActive              : 1,
            windowTitle           : "Base Station Device"
        };

    } else if (elem_type == 'sub_station') {
        var ss_perf_url = info_obj.perf_page_url ? info_obj.perf_page_url : "",
            ss_inventory_url = info_obj.inventory_url ? info_obj.inventory_url : "",
            ss_topo_url = info_obj.topo_view_url ? info_obj.topo_view_url : "",
            ss_info_dict = info_obj.dataset ? info_obj.dataset : [],
            ss_pl_rta_timestamp = info_obj.pl_timestamp ? info_obj.pl_timestamp : "",
            ss_pl = info_obj.pl ? info_obj.pl : "",
            ss_rta = info_obj.rta ? info_obj.rta : "";

        required_info = {
            ptLat                 :  info_obj.lat,
            ptLon                 :  info_obj.lon,
            technology            :  extra_info.technology,
            device_type           :  info_obj.device_type,
            pointType             :  "sub_station",
            alias                 :  info_obj.circuit_id,
            dataset               :  ss_info_dict,
            bhInfo                :  [],
            poll_info             :  [],
            pl                    :  ss_pl,
            rta                   :  ss_rta,
            pl_timestamp          :  ss_pl_rta_timestamp,
            perf_url              :  ss_perf_url,
            link_status           :  info_obj.link_status ? info_obj.link_status : 'NA',
            link_status_timestamp :  info_obj.link_status_timestamp ? info_obj.link_status_timestamp : 'NA',
            inventory_url         :  ss_inventory_url,
            topo_url              :  ss_topo_url,
            antenna_height        :  info_obj.antenna_height,
            name                  :  info_obj.name,
            bs_name               :  extra_info.filter_info.bs_name,
            bs_sector_device      :  extra_info.sector_device_name,
            label_str             :  info_obj.label_str ? info_obj.label_str : '',
            filter_data           :  extra_info.filter_info,
            device_name           :  info_obj.device_name,
            ss_device_id          :  info_obj.device_id,
            ss_ip                 :  info_obj.ip_address,
            sector_ip             :  extra_info.filter_info.sector_name,
            cktId                 :  info_obj.circuit_id,
            zIndex                :  200,
            optimized             :  false,
            isActive              :  1,
            windowTitle           : "Sub Station"
        };
    
    } else {
        required_info = info_obj;
    }

    return required_info;
}


/**
 * This function binds mouseover & mouseout event on given marker
 * @method createHoverWindow
 * @param marker_obj {Object}, It contains the google marker object
 */
function createHoverWindow(marker_obj) {
    if (marker_obj) {
        google.maps.event.addListener(marker_obj, 'mouseover', function(e) {
            var link_status = this.link_status ? $.trim(this.link_status) : 'NA',
                link_status_timestamp = this.link_status_timestamp ? $.trim(this.link_status_timestamp) : 'NA',
                info_html = '';

            if (!link_status) {
                link_status = 'NA';
            }

            info_html += '<table class="table table-responsive table-bordered table-hover">\
                          <tr><td>Ethernet Status</td><td>'+link_status+'</td></tr>\
                          <tr><td>Timestamp</td><td>'+link_status_timestamp+'</td></tr>\
                          </table>';

            /*Set the content for infowindow*/
            infowindow.setContent(info_html);
            /*Shift the window little up*/
            infowindow.setOptions({pixelOffset: new google.maps.Size(0, -20)});
            /*Set The Position for InfoWindow*/
            infowindow.setPosition(new google.maps.LatLng(e.latLng.lat(),e.latLng.lng()));
            /*Open the info window*/
            infowindow.open(mapInstance);                           
        });

        google.maps.event.addListener(marker_obj, 'mouseout', function(e) {
            infowindow.close();
        });
        return true;
    } else {
        return false;
    }
}

// "Object.key" prototyping for IE
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

// "indexOf" prototyping for IE
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