/**
 * This script highlights the selected menu when any page is open.
 * @uses jQuery.js
 * Coded By :- Yogender Purohit
 */

var currentRouterString = "";
/*All Sidebar anchor tags*/
var sideMenu = $("#sidebar ul li a");
var routerArray = window.location.href.split("/");
var checkValue = $.trim(routerArray[routerArray.length-2]);
if(checkValue == "new" || checkValue == "update" || checkValue == "treeview") {
    /*Current router url text*/
    currentRouterString = $.trim(window.location.href.split("/").slice(3,routerArray.length-2));
} else {
    /*Current router url text*/
    currentRouterString = $.trim(window.location.href.split("/").slice(3,-1));
}

var currentRouter = $.trim(currentRouterString.replace(/,/g,"/"));
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
        if(slashCount == 5) {

            var superParentClass = $.trim(sideMenu[i].parentElement.parentElement.parentElement.className);

            if (superParentClass.indexOf("has-sub") == -1) {
                var parent = sideMenu[i].parentElement;
                parent.className = "active";
            } else {
                /*Add open class to the arrow*/
                var arrowClass = sideMenu[i].parentElement.parentElement.parentElement.children[0].children[2];
                arrowClass.className = arrowClass.className + " open";

                /*Add current class to the parent li*/
                var parent = sideMenu[i].parentElement;
                parent.className = "current";

                /*Add active class to the super parent li*/
                var superParent = sideMenu[i].parentElement.parentElement.parentElement;
                superParent.className = superParent.className + " active";
            }

        } else if(slashCount == 6) {

            var superParentClass = $.trim(sideMenu[i].parentElement.parentElement.parentElement.className);
            var superSuperParentClass = $.trim(sideMenu[i].parentElement.parentElement.parentElement.className);

            if (superSuperParentClass.indexOf("has-sub") == -1) {
                var parent = sideMenu[i].parentElement;
                parent.className = "active";
            } else {
                sideMenu[i].parentElement.parentElement.parentElement.parentElement.className = superSuperParentClass + " active";
                /*Add open class to the arrow*/
                var arrowClass = sideMenu[i].parentElement.parentElement.parentElement.children[0].children[2];
                arrowClass.className = arrowClass.className + " open";

                /*Add current class to the parent li*/
                var parent = sideMenu[i].parentElement;
                parent.className = "current";

                /*Add active class to the super parent li*/
                var superParent = sideMenu[i].parentElement.parentElement.parentElement;
                superParent.className = superParent.className + " active";
            }
            
        } else if(slashCount == 7) {

            var superParentClass = $.trim(sideMenu[i].parentElement.parentElement.parentElement.className);
            var superSuperParentClass = $.trim(sideMenu[i].parentElement.parentElement.parentElement.parentElement.className);
            var topParentClass = $.trim(sideMenu[i].parentElement.parentElement.parentElement.parentElement.parentElement.className);
            
            if (topParentClass.indexOf("has-sub") == -1) {
                var parent = sideMenu[i].parentElement;
                parent.className = "active";
            } else {
                sideMenu[i].parentElement.parentElement.parentElement.parentElement.parentElement.className = topParentClass + " active";
                /*Add open class to the arrow*/
                var arrowClass = sideMenu[i].parentElement.parentElement.parentElement.parentElement.parentElement.children[0].children[2];
                arrowClass.className = arrowClass.className + " open";

                /*Add current class to the parent li*/
                var parent = sideMenu[i].parentElement;
                parent.className = "current";

                /*Add active class to the super parent li*/
                var superParent = sideMenu[i].parentElement.parentElement.parentElement;
                superParent.className = superParent.className + " active";
            }
        }
    }
}