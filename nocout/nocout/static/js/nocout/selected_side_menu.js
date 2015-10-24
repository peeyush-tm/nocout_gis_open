/**
 * This script highlights the selected menu when any page is loaded.
 * @uses jQuery.js
 * Coded By :- Yogender Purohit
 */

var currentRouterString = "",
    sideMenu = $("#sidebar ul li a"),
    routerArray = window.location.href.split("/"),
    checkValue = $.trim(routerArray[routerArray.length-2]),
    typeCheck = (+checkValue) + 1,
    isForm = false,
    technology_list = ['p2p','ptp','pmp','ptp_bh','wimax'],
    device_technology = "";

if(checkValue == "create" || checkValue == "add" || checkValue == "new" || checkValue == "update" || checkValue == "treeview" || checkValue == "edit" || checkValue == "delete") {
    if($.trim(typeCheck) != "NaN") {        
        /*Current router url text*/
        currentRouterString = $.trim(window.location.href.split("/").slice(3,routerArray.length-3));
    } else {
        /*Current router url text*/
        currentRouterString = $.trim(window.location.href.split("/").slice(3,routerArray.length-2));
    }
    isForm = true;
} else if($.trim(typeCheck) != "NaN"){
    /*Current router url text*/
    currentRouterString = $.trim(window.location.href.split("/").slice(3,routerArray.length-2));
} else {
    /*Current router url text*/
    currentRouterString = $.trim(window.location.href.split("/").slice(3,-1));
}

var currentRouter = $.trim(currentRouterString.replace(/,/g,"/")),
    router_splitted_list = currentRouter.split("/"),
    router_last_val = router_splitted_list[router_splitted_list.length - 1];

// If router's last val is any tech then remove it from url
if(technology_list.indexOf(router_last_val.toLowerCase()) > -1) {
    var new_url_splitted_list = router_splitted_list;
    new_url_splitted_list.splice(new_url_splitted_list.length-1,1);
    currentRouter = new_url_splitted_list.join("/");
}

// case of single device alert page
if(router_splitted_list.length >= 6) {
    var condition1 = router_splitted_list[router_splitted_list.length-2].indexOf('service_tab') > -1,
        condition2 = router_splitted_list[0].indexOf('alert_center') > -1;
    if(condition1 && condition2) {
        currentRouter = router_splitted_list[0]+"/"+router_splitted_list[1]+"/down/"
    }
}

// for Device Type Wizard
if(currentRouter.indexOf('wizard/device-type') > -1) {
    currentRouter = 'type';
}

/*By default all the sub-sub menu panel will be collapsed*/
$(".has-sub-sub > ul.sub-sub, .has-sub-sub > ul.sub-sub > .has-sub-sub-sub > ul.sub-sub-sub").hide();

for(var i = 0; i < sideMenu.length; i++) {

    if($.trim(sideMenu[i].href) !== 'javascript:;' && $.trim(sideMenu[i].href) != "") {
        
        /*Anchor tags hiperlink text*/
        var slashCount = sideMenu[i].href.split("/").length,
            menuLinkString = $.trim(sideMenu[i].href.split("/").slice(3,-1)),
            menuLink = $.trim(menuLinkString.replace(/,/g,"/")),
            menu_link_last_text = menuLink.split("/")[menuLink.split("/").length-1];
        /*Parent Element(li) Classname*/
        var activeClass = $.trim(sideMenu[i].parentElement.className);
        
        /*If there is active class on the parent then remove it*/
        if (activeClass === "active") {
            sideMenu[i].parentElement.className = "";
        }

        // If router's last val is any tech then remove it from url
        if(technology_list.indexOf(menu_link_last_text.toLowerCase()) > -1) {
            var new_url_splitted_list = menuLink.split("/");
            new_url_splitted_list.splice(new_url_splitted_list.length-1,1);
            menuLink = new_url_splitted_list.join("/");
        }

        if(currentRouter.indexOf(menuLink) == 0 && menuLink != "") {
            applySelectedClasses(sideMenu[i]);
        }
    }
}

/*This function apply selected classes on current menu tag & its parents*/
function applySelectedClasses(menuTag) {
    var closest_has_sub = $(menuTag).closest(".has-sub"),
        closest_has_sub_sub = $(menuTag).closest(".has-sub-sub"),
        closest_has_sub_sub_sub = $(menuTag).closest(".has-sub-sub-sub"),
        closest_li = $(menuTag).closest("li"),
        closest_sub_sub = $(menuTag).closest(".sub-sub"),
        closest_arrow = $(menuTag).closest("span.arrow"),
        breadcrumb_txt = '<li><a href="/home/"><i class="fa fa-home"></i> Home</a></li>',
        isTab = $('.nav li.active .hidden-inline-mobile'),
        isTabCase2 = $('.nav li .hidden-inline-mobile');

    if (closest_has_sub.length > 0 && closest_has_sub_sub.length > 0 && closest_has_sub_sub_sub.length > 0) {
        
        closest_has_sub.addClass("active");
        closest_has_sub.addClass("open");
        
        closest_has_sub_sub.addClass("active");
        closest_has_sub_sub.addClass("open");

        closest_has_sub_sub_sub.addClass("active");

        var top_level_child_length = closest_has_sub.children().first()[0].children.length,
            top_level_arrow = closest_has_sub.children().first()[0].children[top_level_child_length - 1];

        top_level_arrow.className = top_level_arrow.className+" open";

        var second_level_child_length = closest_has_sub_sub.children().first()[0].children.length,
            second_level_arrow = closest_has_sub_sub.children().first()[0].children[second_level_child_length - 1];

        second_level_arrow.className = second_level_arrow.className+" open";

        var first_level_child_length = closest_has_sub_sub_sub.children().first()[0].children.length,
            first_level_arrow = closest_has_sub_sub_sub.children().first()[0].children[first_level_child_length - 1];

        first_level_arrow.className = first_level_arrow.className+" open";

        /*Add current class to parent element*/
        closest_li.addClass("current");

        $(".sidebar-menu ul li.active ul.sub .has-sub-sub.active ul.sub-sub li.has-sub-sub-sub.active ul.sub-sub-sub").show();
    } else if(closest_has_sub.length > 0 && closest_has_sub_sub.length > 0 && closest_has_sub_sub_sub.length == 0) {
        closest_has_sub.addClass("active");
        var main_child_length = closest_has_sub.children().first()[0].children.length,
            top_arrow = closest_has_sub.children().first()[0].children[main_child_length - 1];

        top_arrow.className = top_arrow.className+" open";

        closest_has_sub_sub.addClass("active");
        var main_child_length = closest_has_sub_sub.children().first()[0].children.length,
            top_arrow = closest_has_sub_sub.children().first()[0].children[main_child_length - 1];

        top_arrow.className = top_arrow.className+" open";

        /*Add current class to parent element*/
        closest_li.addClass("current");
    } else if(closest_has_sub.length > 0 && closest_has_sub_sub.length == 0 && closest_has_sub_sub_sub.length == 0) {
        
        closest_has_sub.addClass("active");
        var main_child_length = closest_has_sub.children().first()[0].children.length;
        var top_arrow = closest_has_sub.children().first()[0].children[main_child_length - 1];
        top_arrow.className = top_arrow.className+" open";
        /*Add current class to parent element*/
        closest_li.addClass("current");
        breadcrumb_txt += "<li>"+closest_has_sub[0].children[0].outerHTML+"</li>";
        breadcrumb_txt += closest_li[0].outerHTML;

        // $(".breadcrumb").html(breadcrumb_txt);

        // If any tab Exists
        if(isTab.length > 0 || isTabCase2.length > 0) {
            var tab_breadcrumb = "";
            setTimeout(function() {
                if($(".lite > .box-title > h4").text().indexOf("(") > -1) {
                    if(device_technology) {
                        // Add Device Technology to breadcrumb
                        tab_breadcrumb = '<li><a style="cursor:pointer;" url="'+currentRouter+'" class="perf_tech_breadcrumb">'+device_technology.toUpperCase()+'</a></li>';
                    }
                    // Add Device IP to breadcrumb
                    tab_breadcrumb += '<li><a href="'+window.location.href.split("#")[0]+'"><b>'+$(".lite > .box-title > h4").text().split("(")[1].split(")")[0]+'</b></a></li>';
                } else {
                    tab_breadcrumb = '<li><a href="javascript:;"><strong>'+$('.nav li.active .hidden-inline-mobile').text()+'</strong></a></li>';
                }

                // $(".breadcrumb").append(tab_breadcrumb);
            },150);
        }

        // If create/update form
        if(isForm) {
            setTimeout(function() {
                var tab_breadcrumb = '<li><a href="'+window.location.href+'"><strong>'+$('.lite > .box-title > h4').text()+'</strong></a></li>';
                // $(".breadcrumb").append(tab_breadcrumb);
            },150);
        }
    } else {
        /*Add current class to parent element*/
        closest_li.addClass("active");
        var breadcrumb_text = closest_li[0].innerHTML;

        // $(".breadcrumb").html(breadcrumb_text);
        
        // If any tab Exists
        if(isTab.length > 0 || isTabCase2.length > 0) {
            var tab_breadcrumb = "";
            setTimeout(function() {
                if($(".lite > .box-title > h4").text().indexOf("(") > -1) {
                    if(device_technology) {
                        // Add Device Technology to breadcrumb
                        tab_breadcrumb = '<li><a style="cursor:pointer;" url="'+currentRouter+'" class="perf_tech_breadcrumb">'+device_technology.toUpperCase()+'</a></li>';
                    }
                    // Add Device IP to breadcrumb
                    tab_breadcrumb += '<li><a href="'+window.location.href.split("#")[0]+'"><b>'+$(".lite > .box-title > h4").text().split("(")[1].split(")")[0]+'</b></a></li>';
                } else {
                    tab_breadcrumb = '<li><a href="javascript:;"><strong>'+$('.nav li.active .hidden-inline-mobile').text()+'</strong></a></li>';
                }
                // $(".breadcrumb").append(tab_breadcrumb);
            },150);
        }

        // If create/update form
        if(isForm) {
            setTimeout(function() {
                var tab_breadcrumb = '<li><a href="'+window.location.href+'"><strong>'+$('.lite > .box-title > h4').text()+'</strong></a></li>';
                // $(".breadcrumb").append(tab_breadcrumb);
            },150);
        }
    }

    /*Show sub menu.*/
    if(closest_sub_sub.length > 0) {
        closest_sub_sub.show();
    }
}