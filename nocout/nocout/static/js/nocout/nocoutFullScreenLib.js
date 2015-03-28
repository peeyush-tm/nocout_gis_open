/**
 * This file handle the page fullscreen featur
 * @for nocoutFullScreenLib
 */


/*This event show/hide page header*/
$("#headerToggleBtn").click(function(e) {
    /*Get Current Style*/
    var current_style = $.trim($("#page_header_container").attr("style"));

    if($.trim($("#headerToggleBtn").html()) === '<i class="fa fa-eye"></i> Show Page Controls') {
        $("#headerToggleBtn").html('<i class="fa fa-eye-slash"></i> Hide Page Controls');
        $("#headerToggleBtn").removeClass('btn-info');
        $("#headerToggleBtn").addClass('btn-danger');
    } else {
        $("#headerToggleBtn").html('<i class="fa fa-eye"></i> Show Page Controls');
        $("#headerToggleBtn").removeClass('btn-danger');
        $("#headerToggleBtn").addClass('btn-info');
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
  // Chicago
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
        if($("#goFullScreen").html() !== '<i class="fa fa-compress"></i> Exit Full Screen') {
            /*If page header is showing, hide it.*/
            if($.trim($("#headerToggleBtn").html()) !== '<i class="fa fa-eye"></i> Show Page Controls') {
                $("#headerToggleBtn").click();
            }
            
            launchFullscreen(document.getElementById('page_content_div'));


            var aa= screen.height;
            var bb= $("#page_content_div .box-title").height();
            var cc= $("#page_header_container").height();

            if(window.location.pathname.indexOf("googleEarth") > -1) {

                $("#content").addClass("zero_padding_margin");
                $(".mapContainerBlock .box-body").addClass("zero_padding_margin");

                // toggleBoxTitle();
                /*Set width-height for map div in fullscreen*/
                var mapDiv = $("#google_earth_container");
                mapDiv.attr('style', 'width: 100%; height:'+ screen.height+ 'px');
                // mapDiv.attr('style', 'height: 100%;');
                // mapDiv.style.width = "100%";
                // mapDiv.style.height = screen.height+"px";
                $("#content").css("min-height","200px");
             
            } else if (window.location.pathname.indexOf("white_background") > -1) {

                $("#content").addClass("zero_padding_margin");
                $(".mapContainerBlock .box-body").addClass("zero_padding_margin");

                // toggleBoxTitle();
                /*Set width-height for map div in fullscreen*/
                var mapDiv = $("#wmap_container");
                mapDiv.attr('style', 'width: 100%; height:'+ screen.height+ 'px');
                // mapDiv.attr('style', 'height: 100%;');
                // mapDiv.style.width = "100%";
                // mapDiv.style.height = screen.height+"px";
                $("#content").css("min-height","200px");
            } else {
                   /*Remove padding & margin*/
                $("#content").addClass("zero_padding_margin");
                $(".mapContainerBlock .box-body").addClass("zero_padding_margin");

                // $("#deviceMap").height(aa-bb);
                // $("#deviceMap").height(aa);
                // toggleBoxTitle();
                // toggleControlButtons();

                /*Set width-height for map div in fullscreen*/
                if($(".mapContainerBlock").length > 0) {
                    var mapDiv = mapInstance.getDiv();
                    mapDiv.style.width = "100%";
                    mapDiv.style.height = screen.height+"px";
                }
                $("#content").css("min-height","200px");

                if($(".mapContainerBlock").length > 0) {
                    google.maps.event.trigger(mapInstance, 'resize');
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

            // Side info container
            if($(".sideInfoContainer").length > 0) {
                if($(".sideInfoContainer .box-body").hasClass("zero_padding_margin")) {
                    $(".sideInfoContainer .box-body").removeClass("zero_padding_margin");
                }

                if($(".sideInfoContainer .box-title").hasClass('hide')) {
                    $(".sideInfoContainer .box-title").removeClass('hide');
                }
            }

        } else {
            exitFullscreen();
            if(window.location.pathname.indexOf("googleEarth") > -1) {

                showControlDiv= "";
                $(".mapContainerBlock .box-body").removeClass("zero_padding_margin");
                /*Reset width-height for map div in normal screen*/
                var mapDiv = $("#google_earth_container");
                mapDiv.attr('style', 'width: 100%; height: 550px');

                $("#content").removeAttr("style");
                $(".mapContainerBlock .box-title").removeClass('hide');

                $("#goFullScreen").removeClass('hide');

                $("#headerToggleBtn").removeClass('hide');
             
            } else if (window.location.pathname.indexOf("white_background") > -1) {
                showControlDiv= "";
                $(".mapContainerBlock .box-body").removeClass("zero_padding_margin");
                /*Reset width-height for map div in normal screen*/
                var mapDiv = $("#wmap_container");
                mapDiv.attr('style', 'width: 100%; height: 550px');

                $("#content").removeAttr("style");
                $(".mapContainerBlock .box-title").removeClass('hide');

                $("#goFullScreen").removeClass('hide');

                $("#headerToggleBtn").removeClass('hide');
            } else if (window.location.pathname.indexOf("gis") > -1) {
                showControlDiv= "";
                $(".mapContainerBlock .box-body").removeClass("zero_padding_margin");
                if(mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].length=== 3) {
                    mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].removeAt(2);
                }
                $(mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].getAt(0)).find('b').html('Full Screen');
                // $("#deviceMap").height(550);
                // toggleBoxTitle();
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
        $("#goFullScreen").html('<i class="fa fa-compress"></i> Exit Full Screen');
        $("#goFullScreen").removeClass('btn-info');
        $("#goFullScreen").addClass('btn-danger');
    } else {
        $("#goFullScreen").html('<i class="fa fa-arrows-alt"></i> View Full Screen');
        $("#goFullScreen").removeClass('btn-danger');
        $("#goFullScreen").addClass('btn-info');
        if($("#deviceMap").length) {

            $(".mapContainerBlock .box-body").removeClass("zero_padding_margin");

            showControlDiv= "";
            if(mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].length=== 3) {
                mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].removeAt(2);
            }
            $(mapInstance.controls[google.maps.ControlPosition.TOP_RIGHT].getAt(0)).find('b').html('Full Screen');
            // $("#deviceMap").height(550);
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