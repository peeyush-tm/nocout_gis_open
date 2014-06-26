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

if(checkValue == "new" || checkValue == "update" || checkValue == "treeview" || checkValue == "edit") {
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
        
        if(slashCount == 5) {

            var superParentClass = $.trim(sideMenu[i].parentElement.parentElement.parentElement.className);

            if(superParentClass.indexOf("has-sub-sub") == -1 && superParentClass.indexOf("has-sub") == -1) {
                var parent = sideMenu[i].parentElement;
                parent.className = "active";
            } else {
                /*Have sub menu*/
                if(superParentClass.indexOf("has-sub-sub") == -1) {
                    /*Add open class to the arrow*/
                    var arrowClass = sideMenu[i].parentElement.parentElement.parentElement.children[0].children[2];
                    arrowClass.className = arrowClass.className + " open";

                    /*Add current class to the parent li*/
                    var parent = sideMenu[i].parentElement;
                    parent.className = "current";

                    /*Add active class to the super parent li*/
                    var superParent = sideMenu[i].parentElement.parentElement.parentElement;
                    superParent.className = superParent.className + " active";
                /*Have sub-sub menu*/
                } else {

                    /*Add open class to the arrow*/
                    var arrowClass = sideMenu[i].parentElement.parentElement.parentElement.parentElement.parentElement.children[0].children[2];
                    arrowClass.className = arrowClass.className + " open";

                    /*Add current class to the parent & parent of parent li*/
                    var parent = sideMenu[i].parentElement;
                    parent.className = parent.className+" current";

                    var parent_parent = sideMenu[i].parentElement.parentElement.parentElement;
                    parent_parent.className = parent_parent.className+" current";

                    /*Add active class to the super parent li*/
                    var superParent = sideMenu[i].parentElement.parentElement.parentElement.parentElement.parentElement;
                    superParent.className = superParent.className + " active";

                    /*Show the current sub-sub menu panel*/
                    $(sideMenu[i].parentElement.parentElement).show();
                }
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
                /*Show the current sub-sub menu panel*/
                $(sideMenu[i].parentElement.parentElement).show();

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