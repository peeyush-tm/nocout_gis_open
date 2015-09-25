/**
 * This library is used to show & hide the spinner
 * @uses spin.js
 */

/*Spinner configuration object*/
var spinner_options = {
        lines: 20, // The number of lines to draw
        length: 40, // The length of each line
        width: 2, // The line thickness
        radius: 30, // The radius of the inner circle
        corners: 1, // Corner roundness (0..1)
        rotate: 0, // The rotation offset
        direction: 1, // 1: clockwise, -1: counterclockwise
        color: '#111', // #rgb or #rrggbb or array of colors
        speed: 1, // Rounds per second
        trail: 45, // Afterglow percentage
        shadow: false, // Whether to render a shadow
        hwaccel: false, // Whether to use hardware acceleration
        className: 'spinner', // The CSS class to assign to the spinner
        zIndex: 2e9, // The z-index (defaults to 2000000000)
        top: '50%', // Top position relative to parent
        left: '50%' // Left position relative to parent
    },
    backdrop_html = '<div class="modal-backdrop fade in" id="ajax_backdrop"></div>';
/*Spinner DOM Element*/
var dom_target = document.getElementById('ajax_spinner');
/*Initialize spinner object*/
var spinner = new Spinner(spinner_options).spin(dom_target);
/**
 * This funtion show the spinner
 */
function showSpinner() {
	
	if($("#ajax_spinner").hasClass("hide")) {
        /*Show ajax_spinner div*/
        $("#ajax_spinner").removeClass("hide");
        /*If ajax_backdrop div not exist then appent it to body */
        if($("#ajax_backdrop").length == 0) {
            $("#page_content_div").append(backdrop_html);
        }            
    }
}

/**
 * This funtion hide the spinner
 */
function hideSpinner() {
	
	/*Remove backdrop div & hide spinner*/
    $("#ajax_backdrop").remove();
    if(!($("#ajax_spinner").hasClass("hide"))) {
        /*Hide ajax_spinner div*/
        $("#ajax_spinner").addClass("hide");
    }
}


function createPaginateTabs() {
    if($('.top_perf_tabs').length) {
        // console.log($('.top_perf_tabs li'));
        // console.log($('.top_perf_tabs li').length);
    }
}


// Add fa-ellipsis-v icon before every tab text
var page_tabs_obj = $('.nav-tabs li a');
for (var i=0;i <page_tabs_obj.length;i++) {
    var anchor_html = $(page_tabs_obj[i]).html();
    if (anchor_html.indexOf('</i>') == -1) {
        $(page_tabs_obj[i]).prepend('<i class="fa fa-ellipsis-v">&nbsp;</i>');
    }
}

var tab_elem = 'ul.top_perf_tabs',
    child_tag_name = 'li';


/**
 * This function show/hide paging functionality of tabs if they exceed from parent's width
 * @method createTabsPaging
 * @param elem {String}, It contains the element dom selector
 * @param child_tag {String}, It contains the child tag name
 */
function createTabsPaging(elem, child_tag) {
    tab_elem = elem;
    child_tag_name = child_tag;
    var width_object = getParentChildWidth(elem, child_tag);

    if (width_object.self_width > width_object.parent_width) {
        if($('.paging_arrow').hasClass('hide')) {
            $('.paging_arrow').removeClass('hide');
        }
    } else {
        $(elem).parent('.header-tabs').attr('style', 'width:100%;')
    }
}

/**
 * This function return given element with as per its child & its parent n super parent width
 * @method getParentChildWidth
 * @param elem {String}, It contains the element dom selector
 * @param child_tag {String}, It contains the child tag name
 */
function getParentChildWidth(elem, child_tag) {
    var self_width = 0;
    
    for (var i=0;i<$(elem + ' ' + child_tag).length;i++) {
        self_width += $($(elem + ' ' + child_tag)[i]).width();
    }

    var width_obj = {
            'self_width' : self_width,
            'parent_width' : $(elem).parent().width(),
            'super_parent_width' : $(elem).parent().parent().width()
        };

    return width_obj;
}

/**
 * This event triggers when mouse over/out from tab paging arrows
 * @event hover
 */
$('.paging_arrow').hover(
    function() {
        is_mouse_out = false;
        paginateTab(this);
    },
    function() {
        is_mouse_out = true;
    }
);

/**
 * This function moves tabs in 'right' or 'left' direction as per the given param
 * @method paginateTab
 * @param self {Object}, It contains the current object of hover event
 */
function paginateTab(self) {
    var width_object = getParentChildWidth(tab_elem, child_tag_name);

    if (tab_elem.indexOf('alert_detail_tabs') > -1) {
        extra_spacing = 50;
    } else {
        extra_spacing = 20;
    }

    var width_diff = (width_object.self_width - width_object.parent_width) + (width_object.super_parent_width - width_object.parent_width) + extra_spacing,
        margin_left = $.trim($(tab_elem)[0].style.marginLeft);
    
    if (margin_left.indexOf('px') > -1) {
        margin_left = Number(margin_left.split('px')[0]);
    }

    if ($(self).hasClass('right_arrow')) {
        var m_left = margin_left;
        if (!isNaN(Number(String(margin_left).split('-')[1]))) {
            m_left = Number(String(margin_left).split('-')[1]);
        }
        if (m_left < width_diff) {
            $(tab_elem).css('margin-left', margin_left -10);
        }
    } else {
        if (margin_left < width_diff && margin_left != 0) {
            $(tab_elem).css('margin-left', margin_left + 10);
        }
    }

    setTimeout(function() {
        if (!is_mouse_out) {
            paginateTab(self);
        }
    }, 100);
}