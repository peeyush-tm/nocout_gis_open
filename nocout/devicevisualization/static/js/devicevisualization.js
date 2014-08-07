var mapPageType = "";

/**
 * This funciton returns the page name of currenly opened page
 * @method getPageType
 */
function getPageType() {

    if(window.location.pathname.indexOf("google_earth") > -1) {
        mapPageType = "earth";
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
    
        /*Clear all the elements from google earth*/
        earth_instance.clearEarthElements();

        /*Reset Global Variables & Filters*/
        earth_instance.resetVariables_earth();

        /*create the BS-SS network on the google map*/
        earth_instance.getDevicesData_earth();

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

    advSearch.getFilterInfo("filterInfoModal","Advance Filters","advFilterBtn",getFilterApi,setFilterApi);
}

/**
 * This function triggers when remove filters button is clicked
 * @method removeAdvFilters
 */
function removeAdvFilters() {

    advSearch.removeFilters();
}

/*Trigers when "Create Polygon" button is clicked*/
$("#createPolygonBtn").click(function(e) {

    $("#createPolygonBtn").button("loading");
    $("#advFilterBtn").button("loading");
    $("#resetFilters").button("loading");

    networkMapInstance.createPolygon();
});

/*triggers when clear selection button is clicked*/
$("#clearPolygonBtn").click(function(e) {

    networkMapInstance.clearPolygon();
});


/**
 * This function shows tools panel to google map
 *
 */
function showToolsPanel() {

    /*Hide Tools Button*/
    $("#showToolsBtn").addClass("hide");

    /*Show Remove Button*/
    $("#removeToolsBtn").removeClass("hide");

    /*Show Tools Panel*/
    $("#toolsContainer").removeClass("hide");
}

function removetoolsPanel() {    

    /*Hide Tools Button*/
    $("#showToolsBtn").removeClass("hide");

    /*Show Remove Button*/
    $("#removeToolsBtn").addClass("hide");

    /*Show Tools Panel*/
    $("#toolsContainer").addClass("hide");

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

    networkMapInstance.clearToolsParams_gmap_gmap();
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