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
        // if(currentRouter.indexOf('alert_center/customer/') > -1 && menuLink.indexOf('alert_center/customer/') > -1 && currentRouter != menuLink) {
        //     var sub_tag = currentRouter.split("/");
        //     if(menuLink.indexOf(sub_tag[sub_tag.length-1]) > -1) {
        //         applySelectedClasses(sideMenu[i]);
        //     }
        // } else if(currentRouter.indexOf(menuLink) == 0 && menuLink!="") {
        //     applySelectedClasses(sideMenu[i]);
        // }
        if(currentRouter.indexOf(menuLink) == 0 && menuLink!="") {
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

            if(window.location.pathname.indexOf("googleEarth") > -1) {
             
            } else if (window.location.pathname.indexOf("white_background") > -1) {

                $("#content").addClass("zero_padding_margin");
                $(".mapContainerBlock .box-body").addClass("zero_padding_margin");

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
            if(window.location.pathname.indexOf("googleEarth") > -1) {
             
            } else if (window.location.pathname.indexOf("white_background") > -1) {
                showControlDiv= "";
                $("#content").removeClass("zero_padding_margin");
                $(".mapContainerBlock .box-body").removeClass("zero_padding_margin");
                /*Reset width-height for map div in normal screen*/
                var mapDiv = $("#wmap_container");
                mapDiv.attr('style', 'width: 100%; height: 550px');

                $("#content").removeAttr("style");
                $(".mapContainerBlock .box-title").removeClass('hide');

                $("#goFullScreen").removeClass('hide');

                $("#headerToggleBtn").removeClass('hide');
            } else {
                showControlDiv= "";

                $("#content").removeClass("zero_padding_margin");
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



/**********************************Activity Stream for add,edit & delete*************************************/
var isNewForm = window.location.href.indexOf('new'),
    isCreateForm = window.location.href.indexOf('create'),
    isAddForm = window.location.href.indexOf('add'),
    isEditForm = window.location.href.indexOf('edit'),
    isUpdateForm = window.location.href.indexOf('update'),
    isModifyForm = window.location.href.indexOf('modify'),
    page_title = "",
    module_name = "",
    isFormSubmit = 0;

if(isCreateForm > -1 || isNewForm > -1 || isAddForm > -1) {
    
    page_title = $(".formContainer .box .box-title h4")[0].innerHTML.toLowerCase().split(" add ");
    module_name = page_title.length > 1 ? page_title[1].replace(/\b[a-z]/g, function(letter) {return letter.toUpperCase()}) :  page_title[0].replace(/\b[a-z]/g, function(letter) {return letter.toUpperCase()});

} else if(isEditForm > -1 || isUpdateForm > -1 || isModifyForm > -1) {

    page_title = $(".formContainer .box .box-title h4")[0].innerHTML.toLowerCase().split(" edit ");
    module_name = page_title.length > 1 ? page_title[1].replace(/\b[a-z]/g, function(letter) {return letter.toUpperCase()}) :  page_title[0].replace(/\b[a-z]/g, function(letter) {return letter.toUpperCase()});

    if(isFormSubmit === 0) {
        var oldFieldsArray = $("form input").serializeArray(),
            select_boxes = $("select");

        setTimeout(function() {

            for(var i=0;i<select_boxes.length;i++) {
                var select_id = select_boxes[i].attributes["id"].value,
                    values_array = $("#"+select_id).select2("data"),
                    selected_values = "";
                if(values_array.length) {
                    $.grep(values_array,function(data){
                        if(selected_values.length > 0) {
                            selected_values +=  data.text ? ","+data.text : "";
                        } else {
                            selected_values += data.text ? data.text : "";
                        }
                    });
                } else {
                    selected_values = values_array ? values_array.text : "";
                }

                var data_obj = {
                    "name" : select_boxes[i].attributes["name"].value,
                    "value" : selected_values
                };
                oldFieldsArray.push(data_obj);
            }
        },500);
    } 
}

/*Form Submit Event*/
$("form").submit(function(e) {
    /*Create case*/
    if(isCreateForm > -1 || isNewForm > -1 || isAddForm > -1) {
        /*When first time form submitted*/
        if(isFormSubmit === 0) {

            var alias = $("form input[name*='alias']").val(),
                action = "A new "+module_name.toLowerCase()+" is created - "+alias,
                action_response = "";

            /*Call function to save user action*/
            save_user_action(module_name,action,function(result) {
                action_response = result;
                if(typeof result == 'string' && result.indexOf('success') > -1) {
                    action_response = JSON.parse(result);
                } else {
                    action_response = result;
                }

                isFormSubmit = 1;
                /*Trigger Form Submit*/
                $("form").trigger('submit');
            });
        } else {
            return true;
        }
    /*Edit case*/
    } else if(isEditForm > -1 || isUpdateForm > -1 || isModifyForm > -1) {
        /*When first time form submitted*/
        if(isFormSubmit === 0) {

            var newFieldsArray = $("form input").serializeArray(),
                select_boxes = $("select"),
                modifiedFieldsStr = "[";
            /*Get New Fields*/
            for(var i=0;i<select_boxes.length;i++) {
                var select_id = select_boxes[i].attributes["id"] ? select_boxes[i].attributes["id"].value : "",
                    values_array = select_id ? $("#"+select_id).select2("data") : "",
                    selected_values = "";
                if(values_array.length) {
                    $.grep(values_array,function(data){
                        if(selected_values.length > 0) {
                            selected_values += data.text ? ","+data.text : "";
                        } else {
                            selected_values += data.text ? data.text : "";
                        }
                    });
                } else {
                    selected_values = values_array ? values_array.text : "";
                }

                var data_obj = {
                    "name" : select_boxes[i].attributes["name"].value,
                    "value" : selected_values
                };

                newFieldsArray.push(data_obj);
            }

            /*Get Modified Fields*/
            for(var j=0;j<oldFieldsArray.length;j++) {
                var old_field = oldFieldsArray[j],
                    new_field = newFieldsArray[j];
                if(old_field && new_field) {
                    if($.trim(old_field.value) != $.trim(new_field.value) && old_field.name.indexOf('password') === -1) {
                        var new_val = new_field.value.toLowerCase() != 'select' ? new_field.value : "",
                            old_val = old_field.value.toLowerCase() != 'select' ? old_field.value : "",
                            modified_str = old_field.name+"{"+old_val+" To "+new_val+"}";
                        if($.trim(modifiedFieldsStr) != '[') {
                            modifiedFieldsStr += ","+modified_str;
                        } else {
                            modifiedFieldsStr += modified_str;
                        }
                    }
                }
            }
            /*If any changes done then save user action else return.*/
            if($.trim(modifiedFieldsStr) != '[') {
                
                modifiedFieldsStr += ']';
                /*Call function to save user action*/
                save_user_action(module_name,modifiedFieldsStr,function(result) {
                    if(typeof result == 'string' && result.indexOf('success') > -1) {
                        action_response = JSON.parse(result);
                    } else {
                        action_response = result;
                    }

                    isFormSubmit = 1;
                    /*Trigger Form Submit*/
                    $("form").trigger('submit');
                });
            } else {
                return true;
            }
        } else {
            return true;
        }
    } else {
        return true;
    }

    return false;
});

/**
 * This function save user action by calling respective API.
 * @method save_user_action
 */
function save_user_action(module,action,callback) {

    var csrftoken = $.cookie("csrftoken"),
        base_url = "";

    /*Set the base url of application for ajax calls*/
    if(window.location.origin) {
        base_url = window.location.origin;
    } else {
        base_url = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
    }

    $.ajax({
        url : base_url+"/logs/actions/log/", 
        type : "POST",
        dataType: "json", 
        data : {
            module : module,
            action : action,
            csrfmiddlewaretoken : csrftoken,
        },
        success : function(response) {     
            callback(response);
        },
        error : function(xhr,errmsg,err) {
            callback(xhr.status + ": " + xhr.responseText)
        }
    });
}


/*Hide hightcharts.com link from charts if exist.*/
setTimeout(function() {
    var highcharts_link = $("svg text:last-child");
    if(highcharts_link.length > 0) {
        for(var i=0;i<highcharts_link.length;i++) {
            var link_text = $("svg text:last-child")[i] ? $.trim($("svg text:last-child")[i].innerHTML.toLowerCase()) : "";
            if(link_text === 'highcharts.com') {
                $("svg text:last-child")[i].innerHTML = "";
            }
        }
    }
},500);