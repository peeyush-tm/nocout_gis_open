var mapPageType = "",
    hasAdvFilter = 0,
    hasSelectDevice = 0,
    hasTools = 0;

/*Call get_page_status function to show the current status*/
get_page_status();

/**
 * This funciton returns the page name of currenly opened page
 * @method getPageType
 */
function getPageType() {

    if(window.location.pathname.indexOf("google_earth") > -1) {
        mapPageType = "earth";
        // mapPageType = "earth";
        // networkMapInstance = mapsLibInstance;
    } else {
        mapPageType = "gmap";
    }
}

//defining global varible for city options
city_options = []

/*This event trigger when state dropdown value is changes*/
$("#state").change(function(e) {

    getPageType();

    var state_id = $(this).val();
    if (state_id != ""){
        $("#city").children().show();
        for (var j =0 ; j < city_options.length; j++){
            $("#city").append(city_options[j]);
        }
        var city_obj = $("#city").children('option:not([state_id='+state_id+'])');
//        city_obj.hide();
//        city_obj.attr('disabled', true);
        $("#city").prepend('<option value="">Select City</option>');
        city_obj.each(function(){
            city_options.push($(this));
            $(this).remove();
        });
    }
    else{
        $("#city").children().show();
        for (var j =0 ; j < city_options.length; j++){
            $("#city").append(city_options[j]);
        }
//        $("#city").children('option:not([state_id='+state_id+'])').attr('disabled', false);
    }
    networkMapInstance.makeFiltersArray(mapPageType);
});

/*This event trigger when city dropdown value is changes*/
$("#city").change(function(e) {

    getPageType();
    if ( $(this).val() != ""){
        var state_id = $("#city :selected").attr("state_id");
        $("#state").val(state_id);
    }
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
    var tech_id = $(this).val();

    if (tech_id != ""){
        // $("select#vendor > option").each(function() {
        //     if($(this).attr('tech_id')=== tech_id) {
        //         $(this).show();
        //     } else {
        //         $(this).hide();
        //     }
        // });
        $("#vendor").val(tech_id);
    }
    networkMapInstance.makeFiltersArray(mapPageType);
});


/*This event triggers when Reset Filter button clicked*/
$("#resetFilters").click(function(e) {

    if(isFreeze == 0) {
        
        $("#resetFilters").button("loading");
        /*Reset The basic filters dropdown*/
        $("#technology").val($("#technology option:first").val());
        $("#vendor").val($("#vendor option:first").val());
        $("#state").val($("#state option:first").val());
        $("#city").val($("#city option:first").val());
        isCallCompleted = 1;
    }    

    if(window.location.pathname.indexOf("google_earth") > -1) {
        
        if(isFreeze == 0) {            

            /*Reset filter object variable*/
            appliedFilterObj_gmaps = {};

            /*Reset markers, polyline & filters*/
            networkMapInstance.clearGmapElements();

            /*Reset Global Variables & Filters*/
            networkMapInstance.resetVariables_gmap();

            /*Call the make network to create the BS-SS network on the google map*/
            networkMapInstance.getDevicesData_gmap();
        }

        /***************GOOGLE EARTH CODE*******************/
        /*Clear all the elements from google earth*/
        // earth_instance.clearEarthElements();

        /*Reset Global Variables & Filters*/
        // earth_instance.resetVariables_earth();

        /*create the BS-SS network on the google map*/
        // earth_instance.getDevicesData_earth();

    } else {
        
        if(isFreeze == 0) {            

            /*Reset filter object variable*/
            appliedFilterObj_gmaps = {};

            /*Reset markers, polyline & filters*/
            networkMapInstance.clearGmapElements();

            /*Reset Global Variables & Filters*/
            networkMapInstance.resetVariables_gmap();

            /*Call the make network to create the BS-SS network on the google map*/
            // networkMapInstance.getDevicesData_gmap();
            networkMapInstance.plotDevices_gmap(main_devices_data_gmaps,"base_station");
        }
    }
});

function showAdvSearch() {
    showSpinner();
    $("#advFilterContainerBlock").hide();
    $("#advSearchContainerBlock").show();
    advJustSearch.getFilterInfofrompagedata("searchInfoModal", "Advance Search", "advSearchBtn");
}

$("#setAdvSearchBtn").click(function(e) {
    showSpinner();
    advJustSearch.showNotification();
    advJustSearch.searchAndCenterData(main_devices_data_gmaps);
});

$("#cancelAdvSearchBtn").click(function(e) {
    $("#advFilterFormContainer").html("");

    if(!($("#advFilterSearchContainerBlock").hasClass("hide"))) {
        $("#advSearchContainerBlock").addClass("hide");
    }
    // advJustSearch.resetVariables();
});

$("#resetSearchForm").click(function(e) {
    $("form#searchInfoModal_form").find('select').each(function(i, el) {
        $(el).select2("val", [])
        if(i== $("form#searchInfoModal_form").find('select').length-1) {
               if(!($("#advFilterSearchContainerBlock").hasClass("hide"))) {
                $("#advSearchContainerBlock").addClass("hide");
            } 
        }
    });
    advJustSearch.resetPreviousSearchedMarkers();
    advJustSearch.resetVariables();
    mapInstance.setCenter(new google.maps.LatLng(21.1500,79.0900));
    mapInstance.setZoom(5);
    advJustSearch.hideNotification();

});

/**
 * This function triggers when "Advance Filters" button is pressed
 * @method showAdvFilters
 */
function showAdvFilters() {
    /*Show the spinner*/
    showSpinner();
    $("#advSearchContainerBlock").hide();
    $("#advFilterContainerBlock").show();
//  advSearch.getFilterInfo("filterInfoModal","Advance Filters","advFilterBtn",getFilterApi,setFilterApi);
    advSearch.getFilterInfofrompagedata("filterInfoModal", "Advance Filters", "advFilterBtn");
}
    
/*If 'Filter' button of advance filter is clicked*/
$("#setAdvFilterBtn").click(function(e) {

    /*Show spinner*/
    showSpinner();

    /*Reset advance filter status flag*/
    hasAdvFilter = 1;
    advSearch.callSetFilter();

    /*Call get_page_status function to show the current status*/
    get_page_status();

});

/*If 'Cancel' button of advance filter form is clicked*/
$("#cancelAdvFilterBtn").click(function(e) {

    $("#advFilterFormContainer").html("");

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

    /*Call get_page_status function to show the current status*/
    get_page_status();
}

/*Trigers when "Create Polygon" button is clicked*/
$("#createPolygonBtn").click(function(e) {

    if($("#selectDeviceContainerBlock").hasClass("hide")) {
        $("#selectDeviceContainerBlock").removeClass("hide");
    }

    $("#createPolygonBtn").button("loading");
    $("#advFilterBtn").button("loading");
    $("#resetFilters").button("loading");

    networkMapInstance.initLivePolling();

    hasSelectDevice = 1;

    /*Call get_page_status function to show the current status*/
    get_page_status();
});

$("#tech_send").click(function(e) {

    networkMapInstance.fetchPollingTemplate_gmap();
});

$("#fetch_polling").click(function(e) {

    networkMapInstance.getDevicesPollingData();
});

/*triggers when clear selection button is clicked*/
$("#clearPolygonBtn").click(function(e) {

    if(!($("#selectDeviceContainerBlock").hasClass("hide"))) {
        $("#selectDeviceContainerBlock").addClass("hide");
    }

    networkMapInstance.clearPolygon();
    hasSelectDevice = 0;

    /*Call get_page_status function to show the current status*/
    get_page_status();
});


/**
 * This function shows tools panel to google map
 *
 */
function showToolsPanel() {

    hasTools = 1;

    /*Hide Tools Button*/
    $("#showToolsBtn").addClass("hide");

    /*Show Remove Button*/
    $("#removeToolsBtn").removeClass("hide");

    /*Show Tools Panel*/
    $("#toolsContainerBlock").removeClass("hide");

    /*Call get_page_status function to show the current status*/
    get_page_status();
}

function removetoolsPanel() {    

    hasTools = 0;

    /*Hide Tools Button*/
    $("#showToolsBtn").removeClass("hide");

    /*Show Remove Button*/
    $("#removeToolsBtn").addClass("hide");

    /*Show Tools Panel*/
    $("#toolsContainerBlock").addClass("hide");

    if($("#ruler_select").hasClass("hide")) {
        $("#ruler_remove").addClass("hide");
        $("#ruler_select").removeClass("hide");
    }

    if($("#point_select").hasClass("hide")) {
        $("#point_remove").addClass("hide");
        $("#point_select").removeClass("hide");
    }

    if($("#line_select").hasClass("hide")) {
        $("#line_remove").addClass("hide");
        $("#line_select").removeClass("hide");
    }

    if($("#freeze_select").hasClass("hide")) {
        $("#freeze_remove").addClass("hide");
        $("#freeze_select").removeClass("hide");
    }

    networkMapInstance.clearToolsParams_gmap();

    networkMapInstance.clearPointTool_gmap();

    /*Call get_page_status function to show the current status*/
    get_page_status();
}

/**
 * This event trigger when clicked on "Ruler" button
 * @event click
 */
 $("#ruler_select").click(function(e) {

    networkMapInstance.clearToolsParams_gmap();

    if($("#ruler_remove").hasClass("hide")) {

        $("#ruler_select").addClass("hide");
        $("#ruler_remove").removeClass("hide");
    }

    networkMapInstance.addRulerTool_gmap();
 });

 /**
  * This event unbind ruler click event & show the Ruler button again
  * @event click
  */
$("#ruler_remove").click(function(e) {    

    if(!($("#ruler_remove").hasClass("hide"))) {
        $("#ruler_select").removeClass("hide");
        $("#ruler_remove").addClass("hide");
    }

    networkMapInstance.clearToolsParams_gmap();
});


/**
 * This event trigger when clicked on "Ruler" button
 * @event click
 */
 $("#point_select").click(function(e) {

    if($("#point_remove").hasClass("hide")) {
        $("#point_select").addClass("hide");
        $("#point_remove").removeClass("hide");
    }

    networkMapInstance.addPointTool_gmap();
 });

 /**
  * This event unbind ruler click event & show the Ruler button again
  * @event click
  */
$("#point_remove").click(function(e) {

    if(!($("#point_remove").hasClass("hide"))) {
        $("#point_select").removeClass("hide");
        $("#point_remove").addClass("hide");
    }

    networkMapInstance.clearPointTool_gmap();
});

/**
 * This event trigger when clicked on "Ruler" button
 * @event click
 */
 $("#freeze_select").click(function(e) {

    if($("#freeze_remove").hasClass("hide")) {

        $("#freeze_select").addClass("hide");
        $("#freeze_remove").removeClass("hide");
    }

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

    networkMapInstance.unfreezeDevices_gmap();
});

/**
 * This function get the current status & show it on gmap/google eartg page.
 */

function get_page_status() {

    var status_txt = "";

    if(hasAdvFilter == 0 && hasSelectDevice == 0 && hasTools == 0) {
        status_txt = "Default";
    } else if(hasAdvFilter == 0 && hasSelectDevice == 0 && hasTools == 1) {
        status_txt = "Gmap Tools Applied";
    } else if(hasAdvFilter == 0 && hasSelectDevice == 1 && hasTools == 0) {
        status_txt = "Select Devices Applied";
    } else if(hasAdvFilter == 0 && hasSelectDevice == 1 && hasTools == 1) {
        status_txt = "Select Devices Applied<br/>Gmap Tools Applied";
    } else if(hasAdvFilter == 1 && hasSelectDevice == 0 && hasTools == 0) {
        status_txt = "Advance Filters Applied";
    } else if(hasAdvFilter == 1 && hasSelectDevice == 0 && hasTools == 1) {
        status_txt = "Advance Filters Applied<br/>Gmap Tools Applied";
    } else if(hasAdvFilter == 1 && hasSelectDevice == 1 && hasTools == 0) {
        status_txt = "Advance Filters Applied<br/>Select Devices Applied";
    } else if(hasAdvFilter == 1 && hasSelectDevice == 1 && hasTools == 1) {
        status_txt = "Advance Filters Applied<br/>Select Devices Applied<br/>Gmap Tools Applied";
    }

    $("#gis_status_txt").html(status_txt);
}

// function updateAllMarkers(icon) {
//     for(var i=0; i< masterMarkersObj.length; i++) {
//         console.log(i);
//     }
// }


// $("input:radio[name='sex']").change(function () {
//     var val= $(this).val();

//     if(val=='small') {
//         updateAllMarkers('11');
//     } else if (val == 'medium') {

//     } else {

//     }
// });