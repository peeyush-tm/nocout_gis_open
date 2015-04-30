/**
 * This file handle the page fullscreen featur
 * @for nocoutFullScreenLib
 */
var isMapsPage = false;

/*This event show/hide page header*/
$("#headerToggleBtn").click(function(e) {

    if($(this).hasClass('show_ctrl')) {
        // Change the icon
        $(this).html('<i class="fa fa-eye-slash"></i>');
        // remove 'btn-info' class and add 'btn-danger' class
        $(this).removeClass('btn-info').addClass('btn-danger');
        // Update the button title
        $(this).attr('title','Hide Page Controls');
        // remove 'show_ctrl' class
        $(this).removeClass('show_ctrl');
    } else {
        // Change the icon
        $(this).html('<i class="fa fa-eye"></i>');
        // remove 'btn-danger' class and // add 'btn-info' class
        $(this).removeClass('btn-danger').addClass('btn-info');
        // Update the button title
        $(this).attr('title','Show Page Controls');
        // Add 'show_ctrl' class
        $(this).addClass('show_ctrl');
        // Hide the page control block
        $("#page_content_div .box-title").removeClass('hide');
    }

    /*Toggle Page Header*/
    $("#page_header_container").slideToggle();
});

/**
 * This adds a  Page Control control to the map
 * @constructor
 */
function ShowControl(controlDiv) {
  
    controlDiv.style.padding = '5px';
    // Set CSS for the control border
    var controlUI = document.createElement('div');
    controlUI.style.backgroundColor = 'white';
    controlUI.style.borderStyle = 'solid';
    controlUI.style.borderWidth = '1px';
    controlUI.style.borderColor = '#717b87';
    controlUI.style.cursor = 'pointer';
    controlUI.style.textAlign = 'center';

    controlUI.title = 'Click to see Page Controls';
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
    controlText.innerHTML = '<b>Show Page Controls</b>';
    controlUI.appendChild(controlText);

    // Setup the click event listeners: simply set the map to
    google.maps.event.addDomListener(controlUI, 'click', function() {
        $("#headerToggleBtn").trigger('click');
        if($(this).find('b').html() === "Show Page Controls") {
            $("#page_content_div .box-title").removeClass('hide');
            $(this).find('b').html("Hide Page Controls");
        } else {
            $("#page_content_div .box-title").addClass('hide');
            $(this).find('b').html("Show Page Controls");
        }
    });
}

function toggleControlButtons() {
    if($("#goFullScreen").hasClass('hide')) {
        $("#goFullScreen").removeClass('hide');
        $("#headerToggleBtn").removeClass('hide');
    } else {
        $("#goFullScreen").addClass('hide');
        $("#headerToggleBtn").addClass('hide');
    }
}

function toggleBoxTitle() {
    if($(".mapContainerBlock .box-title").hasClass('hide')) {
        $(".mapContainerBlock .box-title").removeClass('hide');
    } else {
        $(".mapContainerBlock .box-title").addClass('hide');
    }
}

var showControlDiv= "";
var fullScreenControlDiv= "";
/*This event full screen page widget*/
$("#goFullScreen").click(function() {

    if (
        document.fullscreenEnabled ||
        document.webkitFullscreenEnabled ||
        document.mozFullScreenEnabled ||
        document.msFullscreenEnabled
    ) {

        if($(this).hasClass('normal_screen')) {
            // Hide page controls if shown
            if(!$("#headerToggleBtn").hasClass('show_ctrl')) {
                $("#headerToggleBtn").trigger('click');
            }
            // Go to fullscreen view
            launchFullscreen(document.getElementById('page_content_div'));
            
            var screen_height = screen.height,
                box_title_height = $("#page_content_div .box-title").height(),
                header_height = $("#page_header_container").height();

            if(isMapsPage) {
                goMapsFullScreen();
            } else {
                /*Add padding & margin*/
                $("#content").addClass("zero_padding_margin");
                $(".mapContainerBlock .box-body").addClass("zero_padding_margin");

                $("#content").css("min-height","200px");
            }

            // update the button title
            $(this).attr("title","Exit Fullscreen");
            // Add 'normal_screen' class
            $(this).removeClass('normal_screen');
        } else {
            // update the button title
            $(this).attr("title","Go Fullscreen");
            // Remove 'normal_screen' class
            $(this).addClass('normal_screen');
            //  call 'exitFullscreen' method
            exitFullscreen();

            if(isMapsPage) {
                exitMapsFullScreen();
            }

            $("#content").removeClass("zero_padding_margin");
            $("#goFullScreen").removeClass('hide');
            $("#headerToggleBtn").removeClass('hide');
        }
    } else {
        bootbox.alert("Fullscreen facility not supported by your browser.Please update.")
    }
});

$(document).on('webkitfullscreenchange mozfullscreenchange fullscreenchange MSFullscreenChange', function(e) {
    if (
        document.fullscreenElement ||
        document.webkitFullscreenElement ||
        document.mozFullScreenElement ||
        document.msFullscreenElement
    ) {
        
        $("#goFullScreen").html('<i class="fa fa-compress"></i>');
        $("#goFullScreen").removeClass('btn-info');
        $("#goFullScreen").addClass('btn-danger');

        // update the button title
        $("#goFullScreen").attr("title","Exit Fullscreen");

    } else {

        $("#goFullScreen").html('<i class="fa fa-arrows-alt"></i>');
        $("#goFullScreen").removeClass('btn-danger').addClass('btn-info');
        
        // update the button title
        $("#goFullScreen").attr("title","Go Fullscreen");

        if($("#deviceMap").length) {

            $(".mapContainerBlock .box-body").removeClass("zero_padding_margin");

            showControlDiv= "";

            if(mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].length === 3) {
                mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].removeAt(2);
            }
            $(mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].getAt(0)).find('b').html('Full Screen');

            toggleControlButtons();

            /*Reset width-height for map div in normal screen*/
            var mapDiv = mapInstance.getDiv();
            mapDiv.style.width = "100%";
            mapDiv.style.height = "550px";
            $("#content").removeAttr("style");
            google.maps.event.trigger(mapInstance, 'resize');
            mapInstance.setCenter(mapInstance.getCenter());

            // toggleBoxTitle();
            $(".mapContainerBlock .box-title").removeClass('hide');
        }

        /*Remove padding & margin*/
        $("#content").removeClass("zero_padding_margin");
        /*Show Full Screen & Page control buttons*/
        $("#goFullScreen").removeClass('hide');
        $("#headerToggleBtn").removeClass('hide');
    }
});

/*This function show the given element in full screen*/
function launchFullscreen(element) {
    if(element.requestFullscreen) {
        element.requestFullscreen();
    } else if(element.mozRequestFullScreen) {
        element.mozRequestFullScreen();
    } else if(element.webkitRequestFullscreen) {
        element.webkitRequestFullscreen();
    } else if(element.msRequestFullscreen) {
        element.msRequestFullscreen();
    }
}

// This function exit fullscreen mode
function exitFullscreen() {
    if(document.exitFullscreen) {
        document.exitFullscreen();
    } else if(document.mozCancelFullScreen) {
        document.mozCancelFullScreen();
    } else if(document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
    }
}

/**
 * This function show maps in full screen mode
 * @method goMapsFullScreen
 */
function goMapsFullScreen() {

    $("#content").addClass("zero_padding_margin");
    $(".mapContainerBlock .box-body").addClass("zero_padding_margin");

    $("#content").css("min-height","200px");

    var screen_height = screen.height;

    if(window.location.pathname.indexOf("googleEarth") > -1) {
        /*Set width-height for map div in fullscreen*/
        var mapDiv = $("#google_earth_container");
        mapDiv.attr('style', 'width: 100%; height:'+ screen_height+ 'px');
     
    } else if (window.location.pathname.indexOf("white_background") > -1) {
        /*Set width-height for map div in fullscreen*/
        var mapDiv = $("#wmap_container");
        mapDiv.attr('style', 'width: 100%; height:'+ screen_height+ 'px');
    } else {
        if($(".mapContainerBlock").length > 0) {
            /*Set width-height for map div in fullscreen*/
            var mapDiv = mapInstance.getDiv();
            mapDiv.style.width = "100%";
            mapDiv.style.height = screen_height+"px";

            // Trigger map resize event
            google.maps.event.trigger(mapInstance, 'resize');
            // Update map center position
            mapInstance.setCenter(mapInstance.getCenter());

            if(showControlDiv) {
                showControlDiv= "";
                mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].removeAt(1);
            }
            showControlDiv = document.createElement('div');

            var showControl = new ShowControl(showControlDiv, mapInstance);
            showControlDiv.index = 1;

            mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].push(showControlDiv);

            $(mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].getAt(0)).find('b').html('Exit Full Screen');
        }
    }
}

/**
 * This function exits maps from full screen mode
 * @method exitMapsFullScreen
 */
function exitMapsFullScreen() {

    showControlDiv= "";
    $(".mapContainerBlock .box-body").removeClass("zero_padding_margin");

    if(window.location.pathname.indexOf("googleEarth") > -1) {
        /*Reset width-height for map div in normal screen*/
        var mapDiv = $("#google_earth_container");
        mapDiv.attr('style', 'width: 100%; height: 550px');

        $("#content").removeAttr("style");
        $(".mapContainerBlock .box-title").removeClass('hide');
     
    } else if (window.location.pathname.indexOf("white_background") > -1) {
        /*Reset width-height for map div in normal screen*/
        var mapDiv = $("#wmap_container");
        mapDiv.attr('style', 'width: 100%; height: 550px');

        $("#content").removeAttr("style");
        $(".mapContainerBlock .box-title").removeClass('hide');
    } else if (window.location.pathname.indexOf("gis") > -1) {

        if(mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].length=== 3) {
            mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].removeAt(2);
        }

        $(mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].getAt(0)).find('b').html('Full Screen');

        toggleControlButtons();
        
        /*Reset width-height for map div in normal screen*/
        var mapDiv = mapInstance.getDiv();
        mapDiv.style.width = "100%";
        mapDiv.style.height = "550px";
        $("#content").removeAttr("style");

        google.maps.event.trigger(mapInstance, 'resize');
        mapInstance.setCenter(mapInstance.getCenter());

        $(".mapContainerBlock .box-title").removeClass('hide');
    }
}