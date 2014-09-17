
var mapPageType = "",
    hasAdvFilter = 0,
    hasSelectDevice = 0,
    hasTools = 0,
    freezedAt = 0;

/*Set the base url of application for ajax calls*/
if(window.location.origin) {
    base_url = window.location.origin;
} else {
    base_url = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
}

/*Set cookies if not exist*/
if(!$.cookie("isFreezeSelected")) {
    $.cookie("isFreezeSelected", 0, {path: '/'});
}

if(!$.cookie("freezedAt")) {
    $.cookie("freezedAt", 0, {path: '/'});
}

/*Save cookie value to variable*/
isFreeze = $.cookie("isFreezeSelected");
freezedAt = $.cookie("freezedAt");
isPollingActive = 0;

if(isFreeze == 1) {
    $("#showToolsBtn").removeClass("btn-info");
    $("#showToolsBtn").addClass("btn-warning");
} else {
    $("#showToolsBtn").addClass("btn-info");
    $("#showToolsBtn").removeClass("btn-warning");
}



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
        $("#vendor").val(tech_id);
    }
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
    /*Reset search txt box*/
    $("#google_loc_search").val("");
    $("#lat_lon_search").val("");

    data_for_filters = main_devices_data_gmaps;    
    isCallCompleted = 1;/*Remove this call if server call is started on click of reset button*/

    if(window.location.pathname.indexOf("google_earth") > -1) {
        
        // if(isFreeze == 0) {            

            /*Reset filter object variable*/
            appliedFilterObj_gmaps = {};

            networkMapInstance.clearGmapElements();

            /*Reset Global Variables & Filters*/
            networkMapInstance.resetVariables_gmap();

            /*Call the make network to create the BS-SS network on the google map*/
            // networkMapInstance.getDevicesData_gmap();
            networkMapInstance.plotDevices_gmap(main_devices_data_gmaps,"base_station");
        // }

        /***************GOOGLE EARTH CODE*******************/
        /*Clear all the elements from google earth*/
        // earth_instance.clearEarthElements();

        /*Reset Global Variables & Filters*/
        // earth_instance.resetVariables_earth();

        /*create the BS-SS network on the google map*/
        // earth_instance.getDevicesData_earth();

    } else {
        
        // if(isFreeze == 0) {            

            /*Reset filter object variable*/
            appliedFilterObj_gmaps = {};

            /*Reset markers, polyline & filters*/
            networkMapInstance.clearGmapElements();

            /*Reset Global Variables & Filters*/
            networkMapInstance.resetVariables_gmap();            
            /*Call the make network to create the BS-SS network on the google map*/
            // networkMapInstance.getDevicesData_gmap();
            networkMapInstance.plotDevices_gmap(main_devices_data_gmaps,"base_station");
        // }
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
    advJustSearch.searchAndCenterData(data_for_filters);
});

$("#cancelAdvSearchBtn").click(function(e) {
    $("#advFilterFormContainer").html("");

    if(!($("#advFilterSearchContainerBlock").hasClass("hide"))) {
        $("#advSearchContainerBlock").addClass("hide");
    }
    // advJustSearch.resetVariables();
});

function resetAdvanceSearch() {
    $("#resetSearchForm").trigger('click');    
}

$("#resetSearchForm").click(function(e) {
    $("form#searchInfoModal_form").find('select').each(function(i, el) {
        $(el).select2("val", [])
        if(i== $("form#searchInfoModal_form").find('select').length-1) {
            //    if(!($("#advFilterSearchContainerBlock").hasClass("hide"))) {
            //     $("#advSearchContainerBlock").addClass("hide");
            // } 
        }
    });
    advJustSearch.resetPreviousSearchedMarkers();
    advJustSearch.resetVariables();
    // mapInstance.setCenter(new google.maps.LatLng(21.1500,79.0900));
    // mapInstance.setZoom(5);
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
// addSubSectorMarkersToOms();
    /*Call get_page_status function to show the current status*/
    get_page_status();
}

/*Trigers when "Create Polygon" button is clicked*/
$("#createPolygonBtn").click(function(e) {

    if($("#selectDeviceContainerBlock").hasClass("hide")) {
        $("#selectDeviceContainerBlock").removeClass("hide");
    }

    // $("#createPolygonBtn").button("loading");
    // $("#advFilterBtn").button("loading");
    // $("#advSearchBtn").button("loading");
    // $("#resetFilters").button("loading");
    disableAdvanceButton();
    $("#resetFilters").button("loading");
    $("#showToolsBtn").removeAttr("disabled");

    $("#polling_tech").val($("#polling_tech option:first").val());

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

/*Change event on polling technology dropdown*/
$("#polling_tech").change(function(e) {

    networkMapInstance.initLivePolling();
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
    if(isFreeze == 1) {
        if($("#freeze_remove").hasClass("hide")) {
            $("#freeze_select").addClass("hide");
            $("#freeze_remove").removeClass("hide");
        }
    } else {
        if($("#freeze_select").hasClass("hide")) {
            $("#freeze_remove").addClass("hide");
            $("#freeze_select").removeClass("hide");
        }
    }

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

    if(isFreeze == 1) {
        $("#showToolsBtn").removeClass("btn-info");
        $("#showToolsBtn").addClass("btn-warning");
    } else {
        $("#showToolsBtn").addClass("btn-info");
        $("#showToolsBtn").removeClass("btn-warning");
    }

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

    if(isFreeze == 1) {
        if($("#freeze_remove").hasClass("hide")) {
            $("#freeze_select").addClass("hide");
            $("#freeze_remove").removeClass("hide");
        }
    } else {
        if($("#freeze_select").hasClass("hide")) {
            $("#freeze_remove").addClass("hide");
            $("#freeze_select").removeClass("hide");
        }
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
pointAdd= 1;
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
    pointAdd= -1;
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

//On change of Icon Size, call updateAllMarkers function in DevicePlottingLib with the value.
$("select#icon_Size_Select_In_Tools").change(function() {
    var val= $(this).val();
    defaultIconSize= val;
    networkMapInstance.updateAllMarkersWithNewIcon(val);
});


/*
Function is used to Disable Advance Search, Advance Filter Button when Call for data is going on.
When call is completed, we use the same function to enable Button by passing 'no' in parameter.
 */
function disableAdvanceButton(status) {
    var buttonEls= ['advSearchBtn', 'advFilterBtn', 'createPolygonBtn', 'showToolsBtn'];
    var selectBoxes= ['technology', 'vendor', 'state', 'city'];
    var textBoxes= ['google_loc_search','lat_lon_search'];
    var disablingBit = false;
    if(status=== undefined) {
        disablingBit= true;
        for(var i=0; i< buttonEls.length; i++) {
            // $('#'+buttonEls[i]).prop('disabled', disablingBit);
            $('#'+buttonEls[i]).button('loading');
        }

        for(var i=0; i< selectBoxes.length; i++) {
            document.getElementById(selectBoxes[i]).disabled = disablingBit;    
        }

        for(var i=0; i< textBoxes.length; i++) {
            document.getElementById(textBoxes[i]).disabled = disablingBit;
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
            document.getElementById(textBoxes[i]).disabled = disablingBit;
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
                
                var lat = +(entered_txt.split(",")[0]),
                    lng = +(entered_txt.split(",")[1]),
                    lat_check = (lat >= -90 && lat < 90),
                    lon_check = (lat >= -180 && lat < 180),
                    dms_pattern = /^(-?\d+(?:\.\d+)?)[°:d]?\s?(?:(\d+(?:\.\d+)?)['′:]?\s?(?:(\d+(?:\.\d+)?)["″]?)?)?\s?([NSEW])?/i;
                    dms_regex = new RegExp(dms_pattern);
                
                if((lat_check && lon_check) || (dms_regex.exec(entered_txt.split(",")[0]) && dms_regex.exec(entered_txt.split(",")[1]))) {
                    if((lat_check && lon_check)) {
                        networkMapInstance.pointToLatLon(entered_txt);
                    } else {
                        var converted_lat = dmsToDegree(dms_regex.exec(entered_txt.split(",")[0]));
                        var converted_lng = dmsToDegree(dms_regex.exec(entered_txt.split(",")[1]));
                        networkMapInstance.pointToLatLon(converted_lat+","+converted_lng);
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
      if (typeof obj !== 'object' && (typeof obj !== 'function' || obj === null)) {
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
    if (len === 0) {
      return -1;
    }

    // 5. If argument fromIndex was passed let n be
    //    ToInteger(fromIndex); else let n be 0.
    var n = +fromIndex || 0;

    if (Math.abs(n) === Infinity) {
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
      if (k in O && O[k] === searchElement) {
        return k;
      }
      k++;
    }
    return -1;
  };
}