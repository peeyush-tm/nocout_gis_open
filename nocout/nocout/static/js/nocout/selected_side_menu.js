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
    }

    /*Toggle Page Header*/
    $("#page_header_container").slideToggle();
});


/*This event full screen page widget*/
$("#goFullScreen").click(function() {

    if (
        document.fullscreenEnabled ||
        document.webkitFullscreenEnabled ||
        document.mozFullScreenEnabled ||
        document.msFullscreenEnabled
    ) {
        if($("#goFullScreen").html()!== '<i class="fa fa-compress"></i> Exit Full Screen') {
            /*If page header is showing, hide it.*/
            if($.trim($("#headerToggleBtn").html()) !== '<i class="fa fa-eye"></i> Show Page Header') {
                $("#headerToggleBtn").click();
            }
            
            launchFullscreen(document.getElementById('page_content_div'));
        } else {
            exitFullscreen();
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