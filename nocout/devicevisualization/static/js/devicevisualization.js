/*This event trigger when state dropdown value is changes*/
$("#state").change(function(e) {

    networkMapInstance.makeFiltersArray();
});

/*This event trigger when city dropdown value is changes*/
$("#city").change(function(e) {

    networkMapInstance.makeFiltersArray();
});

/*This event trigger when vendor dropdown value is changes*/
$("#vendor").change(function(e) {

    networkMapInstance.makeFiltersArray();
});

/*This event trigger when technology dropdown value is changes*/
$("#technology").change(function(e) {

    networkMapInstance.makeFiltersArray();
});


/*This event triggers when Reset Filter button clicked*/
$("#resetFilters").click(function(e) {

    $("#resetFilters").button("loading");
    /*Reset markers, polyline & filters*/
    networkMapInstance.clearMapElements();

    /*Reset Global Variables & Filters*/
    networkMapInstance.resetVariables();

    /*Call the make network to create the BS-SS network on the google map*/
    networkMapInstance.getDevicesData(username);
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