/**
 * This file handle the page fullscreen featur
 * @for nocoutFullScreenLib
 */
var isMapsPage = false,
    showControlDiv = "",
    fullScreenControlDiv = "";

function toggleControlButtons() {
    if($("#goFullScreen").hasClass('hide')) {
        $("#goFullScreen").removeClass('hide');
    } else {
        $("#goFullScreen").addClass('hide');
    }
}

function toggleBoxTitle() {
    if($(".mapContainerBlock .box-title").hasClass('hide')) {
        $(".mapContainerBlock .box-title").removeClass('hide');
    } else {
        $(".mapContainerBlock .box-title").addClass('hide');
    }
}

/*This event full screen page widget*/
$("#goFullScreen").click(function() {

    if (
        document.fullscreenEnabled ||
        document.webkitFullscreenEnabled ||
        document.mozFullScreenEnabled ||
        document.msFullscreenEnabled
    ) {

        if($(this).hasClass('normal_screen')) {
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
        $("#goFullScreen").removeClass('btn-default');
        $("#goFullScreen").addClass('btn-danger');

        // update the button title
        $("#goFullScreen").attr("title","Exit Fullscreen");

    } else {

        $("#goFullScreen").html('<i class="fa fa-arrows-alt"></i>');
        $("#goFullScreen").removeClass('btn-danger').addClass('btn-default');
        
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

    if(window.location.pathname.indexOf("gearth") > -1) {
        /*Set width-height for map div in fullscreen*/
        var mapDiv = $("#google_earth_container");
        mapDiv.attr('style', 'width: 100%; height:'+ screen_height+ 'px');
     
    } else if (window.location.pathname.indexOf("wmap") > -1) {
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

    if(window.location.pathname.indexOf("gearth") > -1) {
        /*Reset width-height for map div in normal screen*/
        var mapDiv = $("#google_earth_container");
        mapDiv.attr('style', 'width: 100%; height: 550px');

        $("#content").removeAttr("style");
        $(".mapContainerBlock .box-title").removeClass('hide');
     
    } else if (window.location.pathname.indexOf("wmap") > -1) {
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