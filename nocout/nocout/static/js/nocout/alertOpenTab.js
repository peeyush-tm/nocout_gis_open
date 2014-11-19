/**
 * This library handles the tab click event & load the data as per the selected tab.
 * @class openTabContentLib
 * @event click
 */

var last_clicked_tab = "",
    timeOutId = "";

$(".nav-tabs li a").click(function (e, isFirst) {
    /*Initialize the timer in seconds.Right now its 1 year*/
    /*86400 is 24 hrs miliseconds*/
    var timer = 86400 * 30 * 12;
    /* 1 Year in seconds */

    /*Clear or Reset Time out*/
    clearTimeout(timeOutId);

    var anchor_id = e.currentTarget.id,
        browser_url_array = window.location.href.split("#"),
        second_condition = "";

    if (isFirst) {
        second_condition = isFirst;
    } else {
        second_condition = false;
    }

    /*Current Tab content id or anchor tab hyperlink*/
    var new_url = e.currentTarget.href;

    var destroy = false,
        div_id = e.currentTarget.href.split("#")[1],
        table_id = $("#" + div_id).find("table")[0].id,
        ajax_url = e.currentTarget.attributes.data_url.value,
        grid_headers = JSON.parse(e.currentTarget.attributes.data_header.value);

    if (last_clicked_tab != e.currentTarget.id || second_condition) {

        if (table_id.toLowerCase().indexOf("p2p") > -1 || table_id.toLowerCase().indexOf("ptp") > -1) {
            for (var i = 0; i < grid_headers.length; i++) {
                var column = grid_headers[i];
                if (column.mData.indexOf("sector_id") > -1) {
                    if (column.sClass) {
                        column.sClass = "hide";
                    } else {
                        column["sClass"] = "hide";
                    }
                }
            }
        }

        /*Call createDataTable function to create the data table for specified dom element with given data*/
        dataTableInstance.createDataTable(table_id, grid_headers, ajax_url, destroy);
    }

    /*Save the last clicked tab id in global variable for condition checks*/
    last_clicked_tab = e.currentTarget.id;

    if (window.location.pathname.search('alert_center') > -1) {
        var tab_name = "";

        if (anchor_id.indexOf('pmp') > -1) {
            tab_name = 'PMP';
        } else if (anchor_id.indexOf('wifi') > -1) {
            tab_name = 'WiMAX';
        } else {
            tab_name = 'P2P';
        }
    }

    if (!isFirst) {
        if (window.location.pathname.search('alert_center') > -1) {
            var splitted_url = window.location.pathname.split("/"),
                tab_param_index = splitted_url[splitted_url.length - 1] != "" ? splitted_url.length - 1 : splitted_url.length - 2,
                last_val = splitted_url[splitted_url.length - 1] != "" ? splitted_url[splitted_url.length - 1] : splitted_url[splitted_url.length - 2];
            if (last_val != tab_name) {
                splitted_url[tab_param_index] = tab_name;
                window.location.href = window.location.origin + splitted_url.join("/") + "#" + new_url.split("#")[1];
            }
        } else {
            window.location.href = new_url;
        }
    }

    setTimeout(function() {
        // Update Breadcrumb
        $(".breadcrumb li:last-child").html('<a href="javascript:;"><strong>'+$('.nav li.active .hidden-inline-mobile').text()+'</strong></a>');
    },150);

    /*Refresh the tab after every given timer. Right now it is 5 minutes*/
    timeOutId = setTimeout(function () {

        $("#" + anchor_id).trigger('click', true);

    }, (+(timer) + "000"));
});