/**
 * This script highlights the selected menu when any page is loaded.
 * @uses jQuery.js
 * Coded By :- Yogender Purohit
 */

var currentRouterString = "",
    sideMenu = $("#sidebar ul li a"),
    routerArray = window.location.href.split("/"),
    checkValue = $.trim(routerArray[routerArray.length-2]),
    typeCheck = (+checkValue) + 1;

if(checkValue == "new" || checkValue == "update" || checkValue == "treeview" || checkValue == "edit" || checkValue == "delete") {
    if($.trim(typeCheck) != "NaN") {        
        /*Current router url text*/
        currentRouterString = $.trim(window.location.href.split("/").slice(3,routerArray.length-3));
    } else {
        /*Current router url text*/
        currentRouterString = $.trim(window.location.href.split("/").slice(3,routerArray.length-2));
    }    
} else if($.trim(typeCheck) != "NaN"){
    /*Current router url text*/
    currentRouterString = $.trim(window.location.href.split("/").slice(3,routerArray.length-2));
} else {
    /*Current router url text*/
    currentRouterString = $.trim(window.location.href.split("/").slice(3,-1));
}

var currentRouter = $.trim(currentRouterString.replace(/,/g,"/"));

/*By default all the sub-sub menu panel will be collapsed*/
$(".has-sub-sub > ul.sub-sub").hide();

for(var i = 0; i < sideMenu.length; i++) {

    if($.trim(sideMenu[i].href) !== 'javascript:;' && $.trim(sideMenu[i].href) != "") {
        
        /*Anchor tags hiperlink text*/
        var slashCount = sideMenu[i].href.split("/").length;
        var menuLinkString = $.trim(sideMenu[i].href.split("/").slice(3,-1));
        var menuLink = $.trim(menuLinkString.replace(/,/g,"/"));        
        /*Parent Element(li) Classname*/
        var activeClass = $.trim(sideMenu[i].parentElement.className);
        
        /*If there is active class on the parent then remove it*/
        if (activeClass === "active") {
            sideMenu[i].parentElement.className = "";
        }

        /*If the routertext matches the hiperlink text then add the active & current classes at the desired element*/
        if(currentRouter.indexOf('alert_center/customer/') > -1 && menuLink.indexOf('alert_center/customer/') > -1 && currentRouter != menuLink) {
            var sub_tag = currentRouter.split("/");
            if(menuLink.indexOf(sub_tag[sub_tag.length-1]) > -1) {
                applySelectedClasses(sideMenu[i]);
            }
        } else if(currentRouter.indexOf(menuLink) == 0 && menuLink!="") {
            applySelectedClasses(sideMenu[i]);
        }
    }
}

/*This function apply selected classes on current menu tag & its parents*/
function applySelectedClasses(menuTag) {

    var closest_has_sub = $(menuTag).closest(".has-sub");
    var closest_has_sub_sub = $(menuTag).closest(".has-sub-sub");
    var closest_li = $(menuTag).closest("li");
    var closest_sub_sub = $(menuTag).closest(".sub-sub");
    var closest_arrow = $(menuTag).closest("span.arrow");

    if(closest_has_sub.length > 0 && closest_has_sub_sub.length > 0) {
        
        closest_has_sub.addClass("active");            
        var main_child_length = closest_has_sub.children().first()[0].children.length;
        var top_arrow = closest_has_sub.children().first()[0].children[main_child_length - 1];
        top_arrow.className = top_arrow.className+" open";

        closest_has_sub_sub.addClass("active");
        var main_child_length = closest_has_sub_sub.children().first()[0].children.length;
        var top_arrow = closest_has_sub_sub.children().first()[0].children[main_child_length - 1];
        top_arrow.className = top_arrow.className+" open";

        /*Add current class to parent element*/
        closest_li.addClass("current");

    } else if(closest_has_sub.length > 0 && closest_has_sub_sub.length == 0) {
        
        closest_has_sub.addClass("active");
        var main_child_length = closest_has_sub.children().first()[0].children.length;
        var top_arrow = closest_has_sub.children().first()[0].children[main_child_length - 1];
        top_arrow.className = top_arrow.className+" open";

        /*Add current class to parent element*/
        closest_li.addClass("current");
    } else {
        /*Add current class to parent element*/
        closest_li.addClass("active");
    }

    /*Show sub menu.*/
    if(closest_sub_sub.length > 0) {
        closest_sub_sub.show();
    }
}



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

            if($("#deviceMap").length) {
                /*Remove padding & margin*/
                $("#content").addClass("zero_padding_margin");
                $(".mapContainerBlock .box-body").addClass("zero_padding_margin");

                // $("#deviceMap").height(aa-bb);
                // $("#deviceMap").height(aa);
                toggleBoxTitle();
                toggleControlButtons();

                /*Set width-height for map div in fullscreen*/
                var mapDiv = mapInstance.getDiv();
                mapDiv.style.width = "100%";
                mapDiv.style.height = screen.height+"px";
                $("#content").css("min-height","200px");

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
        } else {
            exitFullscreen();
            if($("#deviceMap").length) {
                showControlDiv= "";
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
                $("#goFullScreen").removeClass('hide');
                $("#headerToggleBtn").removeClass('hide');
                // $("#headerToggleBtn").trigger('click');
            }
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

            /*Remove padding & margin*/
            $("#content").removeClass("zero_padding_margin");
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
            $("#goFullScreen").removeClass('hide');
            $("#headerToggleBtn").removeClass('hide');
        }
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