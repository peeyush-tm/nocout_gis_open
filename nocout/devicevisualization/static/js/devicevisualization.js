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

    $("#resetFilters").button("loading");

    /*Reset The basic filters dropdown*/
    $("#technology").val($("#technology option:first").val());
    $("#vendor").val($("#vendor option:first").val());
    $("#state").val($("#state option:first").val());
    $("#city").val($("#city option:first").val());

    if(window.location.pathname.indexOf("google_earth") > -1) {
    
        /*Clear all the elements from google earth*/
        earth_instance.clearEarthElements();

        /*Reset Global Variables & Filters*/
        earth_instance.resetVariables_earth();

        /*create the BS-SS network on the google map*/
        earth_instance.getDevicesData_earth();

    } else {
        /*Reset filter object variable*/
        appliedFilterObj_gmaps = {};

        /*Reset markers, polyline & filters*/
        networkMapInstance.clearGmapElements();

        /*Reset Global Variables & Filters*/
        networkMapInstance.resetVariables_gmap();

        /*Call the make network to create the BS-SS network on the google map*/
        networkMapInstance.getDevicesData_gmap();
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