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

for (var i = 0; i < sideMenu.length; i++) {
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
    if (menuLink == currentRouter) {
        
        var closest_has_sub = $(sideMenu[i]).closest(".has-sub");
        var closest_has_sub_sub = $(sideMenu[i]).closest(".has-sub-sub");
        var closest_li = $(sideMenu[i]).closest("li");
        var closest_sub_sub = $(sideMenu[i]).closest(".sub-sub");
        var closest_arrow = $(sideMenu[i]).closest("span.arrow");

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
}