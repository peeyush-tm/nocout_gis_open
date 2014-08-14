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
        mapPageType = "gmap";
        // mapPageType = "earth";
        networkMapInstance = mapsLibInstance;
    } else {
        mapPageType = "gmap";
    }
}

/*This event trigger when state dropdown value is changes*/
$("#state").change(function(e) {

    getPageType();
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
            networkMapInstance.getDevicesData_gmap();
        }
    }
});

/**
 * This function triggers when "Advance Filters" button is pressed
 * @method showAdvFilters
 */
function showAdvFilters() {

    show_spinner();
    advSearch.getFilterInfo("filterInfoModal","Advance Filters","advFilterBtn",getFilterApi,setFilterApi);
}
    
/*If 'Filter' button of advance filter is clicked*/
$("#setAdvFilterBtn").click(function(e) {

    show_spinner();

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

    networkMapInstance.createPolygon();

    hasSelectDevice = 1;

    /*Call get_page_status function to show the current status*/
    get_page_status();
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

/**
 * This function show spinner when any ajax call is made
 */
function show_spinner() {

    /*Spinner configuration object*/
    var spinner_options = {
        lines: 17, // The number of lines to draw
        length: 33, // The length of each line
        width: 3, // The line thickness
        radius: 19, // The radius of the inner circle
        corners: 1, // Corner roundness (0..1)
        rotate: 0, // The rotation offset
        direction: 1, // 1: clockwise, -1: counterclockwise
        color: '#000', // #rgb or #rrggbb or array of colors
        speed: 0.7, // Rounds per second
        trail: 60, // Afterglow percentage
        shadow: true, // Whether to render a shadow
        hwaccel: false, // Whether to use hardware acceleration
        className: 'spinner', // The CSS class to assign to the spinner
        zIndex: 2e9, // The z-index (defaults to 2000000000)
        top: '50%', // Top position relative to parent
        left: '50%' // Left position relative to parent
    },
    /*Spinner DOM Element*/
    dom_target = document.getElementById('ajax_spinner')

    if($("#ajax_spinner").hasClass("hide")) {
        /*Show ajax_spinner div*/
        $("#ajax_spinner").removeClass("hide")
        /*Initialize spinner object*/
        var spinner = new Spinner(spinner_options).spin(dom_target);
        /*If ajax_backdrop div not exist then appent it to body */
        if($("#ajax_backdrop").length == 0) {
            $("body").append('<div class="modal-backdrop fade in" id="ajax_backdrop" style="background:#FFFFFF;"></div>');
        }
    }
}