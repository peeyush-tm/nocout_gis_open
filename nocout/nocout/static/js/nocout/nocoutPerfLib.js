/**
 * This library is used to show performance data of particular device in charts & tables
 * @class nocout.perf.lib
 * @uses Highcharts
 * @uses jquery Datatables
 * Coded By :- Yogender Purohit
 */

/*Global Variables*/
var perf_that = "",
    allDevices = "",
    device_status = "",
    device_services = "",
    tabs_click_counter = -1,
    single_service_data = "",
    getServiceDataUrl = "",
    chart_instance = "",
    old_table = "",
    base_url = "",
    tabs_with_historical = [
        {
            "id" : "live",
            "title" : "Live",
        },
        {
            "id" : "bihourly",
            "title" : "Bi-Hourly",
        },
        {
            "id" : "hourly",
            "title" : "Hourly",
        },
        {
            "id" : "daily",
            "title" : "Daily",
        },
        {
            "id" : "weekly",
            "title" : "Weekly",
        },
        {
            "id" : "monthly",
            "title" : "Monthly",
        },
        {
            "id" : "yearly",
            "title" : "Yearly",
        }
    ],
    inventory_status_inner_inner_tabs = [
        {
            "id" : "live",
            "title" : "Live",
        },
        {
            "id" : "daily",
            "title" : "Daily",
        },
        {
            "id" : "weekly",
            "title" : "Weekly",
        },
        {
            "id" : "monthly",
            "title" : "Monthly",
        },
        {
            "id" : "yearly",
            "title" : "Yearly",
        }
    ],
    default_live_table_headers = [
        {
            'mData': 'current_value',
            'sTitle': 'Current Value',
            'sWidth': 'auto',
            'bSortable': false
        },
        {
            'mData': 'severity',
            'sTitle': 'Severity',
            'sWidth': 'auto',
            'bSortable': false
        },
        {
            'mData': 'sys_timestamp',
            'sTitle': 'Time',
            'sWidth': 'auto',
            'bSortable': false
        }
    ],
    default_hist_table_headers = [
        {
            'mData': 'current_value',
            'sTitle': 'Current Value',
            'sWidth': 'auto',
            'bSortable': false
        },
        {
            'mData': 'min_value',
            'sTitle': 'Min. Value',
            'sWidth': 'auto',
            'bSortable': false
        },
        {
            'mData': 'max_value',
            'sTitle': 'Max. Value',
            'sWidth': 'auto',
            'bSortable': false
        },
        {
            'mData': 'avg_value',
            'sTitle': 'Avg. Value',
            'sWidth': 'auto',
            'bSortable': false
        },
        {
            'mData': 'severity',
            'sTitle': 'Severity',
            'sWidth': 'auto',
            'bSortable': false
        },
        {
            'mData': 'sys_timestamp',
            'sTitle': 'Time',
            'sWidth': 'auto',
            'bSortable': false
        }
    ];

/*Set the base url of application for ajax calls*/
if(window.location.origin) {
    base_url = window.location.origin;
} else {
    base_url = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
}

$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results == null) {
        return null;
    } else {
        return results[1] || 0;
    }
};

function updateQueryStringParameter(uri, key, value) {
  var re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
  var separator = uri.indexOf('?') !== -1 ? "&" : "?";
  if (uri.match(re)) {
    return uri.replace(re, '$1' + key + "=" + value + '$2');
  }
  else {
    return uri + separator + key + "=" + value;
  }
}

var timeInterval = "";


function nocoutPerfLib() {

    /*Save reference of current pointer to the global variable*/
    perf_that = this;

    /**
     * This function initializes daterange picker on given domElemet
     * @method initDateRangePicker
     * @param domElemet "String", It contains the dom element id on which the the date range picker is to be initialized.
     */
    this.initDateRangePicker = function(domElemet) {

        // var saved_start_date = $.cookie('filter_start_date') ? $.cookie('filter_start_date') : "",
        //     saved_end_date = $.cookie('filter_end_date') ? $.cookie('filter_end_date') : "",
        var saved_start_date = "",
            saved_end_date = "",
            oldStartDate = saved_start_date ? new Date(saved_start_date * 1000) : new Date(),
            oldENdData = saved_end_date ? new Date(saved_end_date * 1000) : new Date();

        startDate = saved_start_date ? new Date(saved_start_date * 1000) : "";
        endDate = saved_end_date ? new Date(saved_end_date * 1000) : "";

        $('#'+domElemet).daterangepicker(
                {
                    timePicker: true,
                    timePickerIncrement: 1,
                    opens: "right",
                    showDropdowns: true,
                    ranges: {
                        'Today': [moment().startOf('day'), moment()],
                        'Last 24 Hours': [moment().subtract('days', 1), moment()],
                        'Last 7 Days': [moment().subtract('days', 6), moment()],
                        'Last 30 Days': [moment().subtract('days', 29), moment()],
                        'This Month': [moment().startOf('month'), moment().endOf('month')],
                        'Last Month': [moment().subtract('month', 1).startOf('month'), moment().subtract('month', 1).endOf('month')]
                    },
                    buttonClasses: ['btn btn-default'],
                    applyClass: 'btn-small btn-primary',
                    cancelClass: 'btn-small',
                    format: "DD-MM-YYYY HH:mm:ss",
                    separator: ' to ',
                    startDate: oldStartDate,
                    endDate: oldENdData
                },
                function (start, end) {
                    startDate = start;
                    endDate = end;
                }
        );

        if (saved_start_date && saved_end_date) {
            $('#'+domElemet).val(moment(oldStartDate).format("DD-MM-YYYY HH:mm:ss") + '  to  ' + moment(oldENdData).format("DD-MM-YYYY HH:mm:ss"));
            startDate = moment(oldStartDate);
            endDate = moment(oldENdData);
        }
    };

    /**
     * This function Show/Hide tabs as per the page type
     * @method togglePerfPageElements
     * @param page_type "String", It contains the page type i.e either the page is of network, customer or other devices
     * @param technology "String", It contains current device technology
     */
    this.togglePerfPageElements = function(page_type, technology) {

        var condition_1 = page_type == 'customer' || technology.toLowerCase() == 'ptp' || technology.toLowerCase() == 'p2p',
            condition_2 = page_type == 'other';

        // Show/hide parent Tabs
        if(condition_1 || condition_2) {
            if (!$("#topology").hasClass("hide")) {
                $("#topology").addClass("hide");
            }

            if (!$("#topology_tab").hasClass("hide")) {
                $("#topology_tab").addClass("hide");
            }
        } else {
            
            if($("#topology").hasClass("hide")) {
                $("#topology").removeClass("hide");
            }

            if ($("#topology_tab").hasClass("hide")) {
                $("#topology_tab").removeClass("hide");
            }
        }

        // Show/hide live polling button & chart container
        var live_poll_condition1 = ptp_tech_list.indexOf(technology) > -1,
            live_poll_condition2 = page_type == 'customer';

        if(!live_poll_condition1 && !live_poll_condition2) {
            $(".perf_poll_now, #perf_live_poll_input, #perf_live_poll_chart").addClass("hide");
        }

    };

    /**
     * This function fetch the status of current device
     * @method getStatus
     * @param get_status_url "String", It contains the url to fetch the status of current device.
     * @param device_id "INT", It contains the ID of current device.
     */
    this.getStatus = function (get_status_url, device_id) {

        /*Ajax call to Get Devices API*/
        var get_url = get_status_url;
        $.ajax({
            url: get_url,
            type: "GET",
            dataType: "json",
            success: function (response) {

                var result = "";
                // Type check of response
                if(typeof response == 'string') {
                    result = JSON.parse(response);
                } else {
                    result = response;
                }

                if(result.success == 1) {

                    device_status = result.data.objects;
                    // If it is single device page for other devices then hide utilization tab
                    if(device_status.is_others_page) {
                        if (!$("#utilization_top").hasClass("hide")) {
                            $("#utilization_top").addClass("hide");
                        }

                        if (!$("#utilization_top_tab").hasClass("hide")) {
                            $("#utilization_top_tab").addClass("hide");
                        }
                    }

                    if(device_status.headers && device_status.headers.length > 0) {
                        /*Loop for table headers*/
                        var headers = "<tr>";
                        for(var i=0;i<device_status.headers.length;i++) {
                            var header_name = device_status.headers[i];
                            headers += '<th>' + header_name + '</th>';
                        }

                        headers += "</tr>";
                        /*Populate table headers*/
                        $("#status_table thead").html(headers);

                        /*Loop for status table data*/
                        var status_val = "";
                        if(device_status.values.length > 0) {
                            for (var i = 0; i < device_status.values.length; i++) {
                                status_val += "<tr>";

                                var device_status_data_row = device_status.values[i];

                                if(device_status_data_row[0] && device_status_data_row[0].constructor === Array) {
                                    device_status_data_row = device_status_data_row[0];
                                }

                                for (var j = 0; j < device_status_data_row.length; j++) {
                                    var val = device_status_data_row[j]["val"] ? device_status_data_row[j]["val"] : "",
                                        url = device_status_data_row[j]["url"] ? device_status_data_row[j]["url"] : "",
                                        display_txt = url ? '<a href="'+url+'" target="_blank">' + val + '</a>' : val;

                                    status_val += '<td>'+display_txt+'</td>';
                                }   
                                status_val += "</tr>";
                            }
                        } else {
                            status_val += "<tr><td colspan='"+device_status.headers.length+"' align='center'>No Info</td></tr>";
                        }
                        
                        /*Populate table data*/
                        $("#status_table tbody").html(status_val);
                    }

                } else {
                    $.gritter.add({
                        // (string | mandatory) the heading of the notification
                        title: 'Performance',
                        // (string | mandatory) the text inside the notification
                        text: result.message,
                        // (bool | optional) if you want it to fade out on its own or just sit there
                        sticky: false
                    });
                }
            },
            error: function (err) {

                $("#status_table tbody").html(err.statusText);

                $.gritter.add({
                    // (string | mandatory) the heading of the notification
                    title: 'Performance',
                    // (string | mandatory) the text inside the notification
                    text: err.statusText,
                    // (bool | optional) if you want it to fade out on its own or just sit there
                    sticky: false
                });

            }
        });
    };

    /**
     * This function make HTML for LI element of TAB
     * @method make_tab_li_html
     * @param tab_config "{Object}", It contains the configuration for creating tab html
     * @return li_html {String}, It contains the required HTML string
     */
    this.make_tab_li_html = function(tab_config) {
        var li_html = "";

        if(!tab_config || $.isEmptyObject(tab_config)) {
            return li_html;
        }

        var active_class = tab_config.active_class ? tab_config.active_class : "",
            unique_key = tab_config.unique_key ? tab_config.unique_key : "",
            content_href = unique_key ? unique_key+"_block" : "",
            id = unique_key ? unique_key+"_tab" : "",
            api_url = tab_config.api_url ? tab_config.api_url : "",
            title = tab_config.title ? tab_config.title : "",
            icon_class = tab_config.icon_class ? tab_config.icon_class : "";

        li_html = '<li class="'+active_class+'"><a href="#'+content_href+'" \
                   url="'+api_url+'" id="'+id+'" data-toggle="tab">\
                   <i class="'+icon_class+'">&nbsp;</i>'+title+'\
                   </a></li>';

        return li_html;
    };

    /**
     * This function make HTML for TAB content
     * @method make_tab_content_html
     * @param tab_content_config "{Object}", It contains the configuration for creating tab content html
     * @return content_html {String}, It contains the required HTML string
     */
    this.make_tab_content_html = function(tab_content_config) {
        var content_html = "";

        if(!tab_content_config || $.isEmptyObject(tab_content_config)) {
            return content_html;
        }

        var active_class = tab_content_config.active_class ? tab_content_config.active_class : "",
            unique_key = tab_content_config.unique_key ? tab_content_config.unique_key : "",
            id = unique_key ? unique_key+"_block" : "",
            show_last_updated = tab_content_config.show_last_updated != undefined ? tab_content_config.show_last_updated : true,
            last_updated_id = unique_key ? "last_updated_"+unique_key+"_block" : "",
            chart_id = unique_key ? unique_key+"_chart" : "",
            bottom_table_id = unique_key ? unique_key+"_bottom_table" : "";

        content_html += '<div class="tab-pane '+active_class+'" id="'+id+'">';

        if(show_last_updated) {
            content_html += '<div align="center" class="last_updated_container" id="'+last_updated_id+'">\
                            <h3 align="left"><i class="fa fa-spinner fa-spin" title="Fetching Current Status"></i></h3>\
                            </div>';
        }

        content_html += '<div class="chart_container">\
                        <div id="'+chart_id+'" style="width:100%;">\
                        <h3><i class="fa fa-spinner fa-spin"></i></h3></div>\
                        <div id="'+bottom_table_id+'"></div></div></div>';

        return content_html;
    };

    /**
     * This function fetch the list of services
     * @method getServices
     * @param get_service_url "String", It contains the url to fetch the services.
     * @param device_id "INT", It contains the ID of current device.
     */
    this.getServices = function (get_service_url, device_id) {

        /*Show the spinner*/
        // showSpinner();

        var active_tab_id = "",
            active_tab_url = "",
            active_tab_content_dom_id = "";

        /*Ajax call to Get Devices API*/
        var get_url = get_service_url;
        $.ajax({
            url: get_url,
            type: "GET",
            dataType: "json",
            success: function (response) {
                
                var result = "";
                // Type check of response
                if(typeof response == 'string') {
                    result = JSON.parse(response);
                } else {
                    result = response;
                }

                if (result.success == 1) {

                    var first_loop = 0;
                    // If any data exists
                    if(result.data.objects && !$.isEmptyObject(result.data.objects)) {
                        /*Loop to get services from object*/
                        for(service_key in result.data.objects) {

                            var tab_id = service_key.split("_tab")[0];
                            // If dom element exists
                            if($("#"+service_key).length > 0 && $("#"+tab_id).length > 0) {
                                // Reset Variables
                                device_services = "";
                                tabs_with_data = "";

                                if ($("#"+service_key).hasClass("active")) {
                                    $("#"+service_key).removeClass("active");
                                }

                                if ($("#"+tab_id).parent("li").hasClass("active")) {
                                    $("#"+tab_id).parent("li").removeClass("active");
                                }

                                device_services = result.data.objects[service_key].info;
                                if(device_services && device_services.length > 0) {
                                    var tabs_hidden_class = "";
                                    
                                    if(device_services.length == 1) {
                                        tabs_hidden_class = "hide";
                                    }

                                    var count = 0,
                                        tabs_with_data = "",
                                        service_tabs_data = '<div class="tab-content" style="overflow:auto;">',
                                        service_tabs = '<ul class="left_tabs_container nav nav-tabs '+tabs_hidden_class+'">';

                                    var is_first_tab = 0;
                                    if (result.data.objects[service_key].isActive == 1) {
                                        is_first_tab = 1;
                                        $("#"+tab_id).parent("li").addClass("active");
                                        $("#"+service_key).addClass("active");
                                    }

                                    $.each(device_services, function (key, value) {

                                        var unique_item_key = service_key+'_'+String(count)+'_'+String(i),
                                            active_class = '';

                                        if(is_first_tab == 1 && count == 0) {
                                            // Save the active tab data in global variables
                                            active_tab_id = unique_item_key;
                                            active_tab_content_dom_id = unique_item_key+'_block';
                                            active_tab_url = "/" + value.url;

                                            // add 'active' class for active i.e first tab
                                            active_class = 'active';
                                        }

                                        var tab_info_obj = {
                                                'active_class' : active_class,
                                                'unique_key' : unique_item_key,
                                                'icon_class' : 'fa fa-arrow-circle-o-right',
                                                'api_url' : value.url,
                                                'title' : value.title
                                            },
                                            content_info_obj = {
                                                'active_class' : active_class,
                                                'unique_key' : unique_item_key,
                                                'show_last_updated' : true
                                            };


                                        // Create Tab HTML
                                        service_tabs += perf_that.make_tab_li_html(tab_info_obj);

                                        var all_tabs_condition_1 = unique_item_key.indexOf('availability') == -1,
                                            all_tabs_condition_2 = unique_item_key.indexOf('topology') == -1,
                                            all_tabs_condition_3 = unique_item_key.indexOf('utilization') == -1;

                                        // Create tab content HTML
                                        if(show_historical_on_performance && all_tabs_condition_1 && all_tabs_condition_2 && all_tabs_condition_3) {

                                            service_tabs_data += '<div class="tab-pane '+active_class+'" id="'+unique_item_key+'_block">\
                                                                  <div align="center" class="last_updated_container" id="last_updated_'+unique_item_key+'_block">\
                                                                  <h3 align="left"><i class="fa fa-spinner fa-spin" title="Fetching Current Status"></i></h3>\
                                                                  </div><div class="tabbable"><ul class="nav nav-tabs inner_inner_tab">'
                                            var inner_tab_ids = [],
                                                inner_inner_tabs = tabs_with_historical;

                                            if(unique_item_key.indexOf('_status') > -1) {
                                                inner_inner_tabs = inventory_status_inner_inner_tabs;                                                
                                            }
                                            
                                            // CREATE SUB INNER TAB HTML
                                            if(inner_inner_tabs && inner_inner_tabs.length > 0) {
                                                for(var x=0;x<inner_inner_tabs.length;x++) {
                                                    var inner_active_class = '';
                                                    if(x == 0) {
                                                        inner_active_class = 'active';
                                                    }
                                                    var current_item = inner_inner_tabs[x],
                                                        id = current_item.id,
                                                        title = current_item.title,
                                                        inner_tab_info_obj = {
                                                            'active_class' : inner_active_class,
                                                            'unique_key' : id+"_"+unique_item_key,
                                                            'icon_class' : 'fa fa-caret-right',
                                                            'api_url' : value.url+"?data_for="+id,
                                                            'title' : title
                                                        };
                                                    
                                                    service_tabs_data += perf_that.make_tab_li_html(inner_tab_info_obj);
                                                    if(inner_tab_ids.indexOf(id) == -1) {
                                                        inner_tab_ids.push(id);
                                                    }
                                                }

                                            } else {
                                                var inner_tab_info_obj = {
                                                    'active_class' : 'active',
                                                    'unique_key' : "live_"+unique_item_key,
                                                    'icon_class' : 'fa fa-caret-right',
                                                    'api_url' : value.url+"?data_for=live",
                                                    'title' : "Live"
                                                };
                                                service_tabs_data += perf_that.make_tab_li_html(inner_tab_info_obj);
                                                inner_tab_ids.push('live');
                                            }
                                            service_tabs_data += '</ul><div class="divide-20"></div><div class="tab-content">';
                                            // CREATE SUB INNER TAB CONTENT HTML
                                            for(var y=0;y<inner_tab_ids.length;y++) {
                                                var current_key = inner_tab_ids[y],
                                                    inner_content_info_obj = {
                                                        'active_class' : '',
                                                        'unique_key' : current_key+"_"+unique_item_key,
                                                        'show_last_updated' : false
                                                    };
                                                if(y==0) {
                                                    inner_content_info_obj['active_class'] = 'active';
                                                }
                                                service_tabs_data += perf_that.make_tab_content_html(inner_content_info_obj);
                                            }
                                            service_tabs_data += '</div></div><div class="clearfix"></div></div>'
                                        } else {
                                            service_tabs_data += perf_that.make_tab_content_html(content_info_obj);
                                        }

                                        // Increment the counter
                                        count++;
                                    });

                                    service_tabs += '</ul>';
                                    // service_tabs_data += '</div>';
                                    tabs_with_data = service_tabs + " " + service_tabs_data;
                                } else {
                                    if(!$("#"+tab_id).hasClass("hide")) {
                                        $("#"+tab_id).addClass("hide")
                                    }
                                }

                                $("#"+service_key+" .inner_tab_container .panel-body .tabs-left").html(tabs_with_data);
                            }
                        }

                        /*Bind click event on tabs*/
                        $('.inner_tab_container > .panel-body > .tabs-left > ul.nav-tabs > li > a').click(function (e) {
                            // show loading spinner
                            // showSpinner();

                            var current_target = e.currentTarget,
                                current_attr = current_target.attributes,
                                serviceId = current_target.id.slice(0, -4),
                                splitted_local_id = current_attr.href.value.split("#"),
                                tab_content_dom_id = splitted_local_id.length > 1 ? splitted_local_id[1] : splitted_local_id[0];
                            
                            //@TODO: all the ursl must end with a / - django style
                            var service_data_url_val = current_attr.url ? $.trim(current_attr.url.value) : "";
                                serviceDataUrl = "";

                            if(service_data_url_val) {
                                if(service_data_url_val[0] != "/") {
                                    serviceDataUrl = "/"+service_data_url_val;
                                } else {
                                    serviceDataUrl = service_data_url_val;
                                }
                            }

                            if($("#last_updated_"+tab_content_dom_id).length > 0) {
                                perf_that.resetLivePolling("last_updated_"+tab_content_dom_id);
                                // get the service status for that service
                                perfInstance.getServiceStatus(serviceDataUrl,function(response_type,data_obj) {
                                    if(response_type == 'success') {
                                        // Call function to populate latest status for this service
                                        populateServiceStatus_nocout("last_updated_"+tab_content_dom_id,data_obj);
                                    } else {
                                        $("#last_updated_"+tab_content_dom_id).html("");
                                    }
                                });
                            }
                            if(
                                !show_historical_on_performance
                                ||
                                serviceId.indexOf('availability') > -1
                                ||
                                serviceId.indexOf('utilization_top') > -1
                                ||
                                serviceId.indexOf('topology') > -1
                            ) {
                                perfInstance.initGetServiceData(serviceDataUrl, serviceId, current_device);
                            }
                        });
                    }
                } else {
                    $(".inner_tab_container").html("<p>" + result.message + "</p>");
                    $.gritter.add({
                        // (string | mandatory) the heading of the notification
                        title: 'Performance',
                        // (string | mandatory) the text inside the notification
                        text: result.message,
                        // (bool | optional) if you want it to fade out on its own or just sit there
                        sticky: false
                    });
                }

                /*Hide the spinner*/
                // hideSpinner();

            },
            error: function (err) {

                $(".inner_tab_container").html(err.statusText);

                /*Hide the spinner*/
                // hideSpinner();
            },
            complete: function () {
                if(active_tab_url && active_tab_id) {
                    /*Reset Variables & counters */
                    clearTimeout(timeInterval);

                    if($("#other_perf_table").length > 0) {
                        $("#other_perf_table").dataTable().fnDestroy();
                        $("#other_perf_table").remove();
                    }

                    if($("#perf_data_table").length > 0) {
                        $("#perf_data_table").dataTable().fnDestroy();
                        $("#perf_data_table").remove();
                    }

                    perf_that.resetLivePolling("last_updated_"+active_tab_content_dom_id);

                    /*Get Last opened tab id from cookie*/
                    var parent_tab_id = $.cookie('parent_tab_id');

                    //If parent Tab id is there & parent tab element exist in the dom.
                    if(parent_tab_id && $('#'+parent_tab_id).length && $('#'+parent_tab_id)[0].className.indexOf('hide') == -1) {
                        $('#'+parent_tab_id).trigger('click');
                    } else {
                        // show loading spinner
                        // showSpinner();
                        if($("#last_updated_"+active_tab_content_dom_id).length > 0) {
                            perfInstance.getServiceStatus(active_tab_url,function(response_type,data_obj) {
                                if(response_type == 'success') {
                                    // Call function to populate latest status for this service
                                    populateServiceStatus_nocout("last_updated_"+active_tab_content_dom_id,data_obj);
                                } else {
                                    $("#last_updated_"+active_tab_content_dom_id).html("");
                                }
                            });
                        }

                        if(show_historical_on_performance) {
                            $("#live_"+active_tab_id+"_tab").trigger('click');
                        } else {
                            /*Call getServiceData function to fetch the data for currently active service*/
                            perf_that.getServiceData(active_tab_url, active_tab_id, device_id);
                        }
                    }
                }
            }
        });
    };

    /**
     * This function get the service status for given url
     * @method getServiceStatus
     * @param service_status_url "String", It contains the url to fetch the status of current device.
     * @callback Back to the called function.
     */
    this.getServiceStatus = function(service_status_url,callback) {

        var splitted_status_url = service_status_url.split("/"),
            updated_url = splitted_status_url[splitted_status_url.length -1] != "" ? service_status_url+"/" : service_status_url,
            device_id = splitted_status_url[splitted_status_url.length -1] != "" ? splitted_status_url[splitted_status_url.length -1] : splitted_status_url[splitted_status_url.length -2];

        if(updated_url.indexOf("/servicedetail/") > -1) {
            if(updated_url.indexOf("rssi") > -1) {
                updated_url = "/performance/servicestatus/rssi/service_data_source/rssi/device/"+device_id+"/";
            } else if(updated_url.indexOf("util") > -1) {
                updated_url = "/performance/servicestatus/utilization/service_data_source/utilization/device/"+device_id+"/";
            }
        } else {
            // Replace 'service' with 'servicestatus'
            updated_url = updated_url.replace("/service/","/servicestatus/");
        }

        // 
        $.ajax({
            url : base_url+""+updated_url,
            type : "GET",
            success : function(response) {
                var result = "",
                    last_updated = "",
                    perf = "";

                // Type check of response
                if(typeof response == 'string') {
                    result = JSON.parse(response);
                } else {
                    result = response;
                }
                if(result.success) {
                    if(result.data && result.data.objects) {
                        // Call function to populate latest status info
                        populateDeviceStatus_nocout("latestStatusContainer",result.data.objects);

                        last_updated = result.data.objects.last_updated ? result.data.objects.last_updated : "";
                        perf = result.data.objects.perf ? result.data.objects.perf : "";

                        var response_obj = {
                            "last_updated" : last_updated,
                            "perf" : perf
                        };

                        callback("success",response_obj);
                    } else {
                        callback("error","");
                    }
                } else {
                    callback("error","");
                }
            },
            error : function(err) {
                $.gritter.add({
                    // (string | mandatory) the heading of the notification
                    title: 'Performance - Service Status',
                    // (string | mandatory) the text inside the notification
                    text: err.statusText,
                    // (bool | optional) if you want it to fade out on its own or just sit there
                    sticky: false
                });
                callback("error","");
            }
        });
    };

    /**
     * This function fetches data regarding particular service
     * @method getServiceData
     * @param get_service_data_url "String", It contains the url to fetch the status of current device.
     * @param service_id "String", It contains unique name for service.
     * @param device_id "INT", It contains the ID of current device.
     */
    this.getServiceData = function (get_service_data_url, service_id, device_id) {

        if(!get_service_data_url) {
            return true;
        }

        if(get_service_data_url[0] != '/') {
            get_service_data_url = "/"+get_service_data_url;
        }

        var draw_type = $("input[name='item_type']:checked").val(),
            listing_ajax_url = "";

        if(!draw_type) {
            draw_type = "chart";
        }

        // Decrement the tabs click on evert click counter
        tabs_click_counter--;

        $.cookie('activeTabId', service_id+"_tab", {path: '/'});

        var start_date = "",
            end_date = "",
            get_url = "";

        showSpinner();

        get_url = base_url + "" + get_service_data_url;
        listing_ajax_url = get_service_data_url;

        start_date = "";
        end_date = "";

        var get_param_start_date = "", 
            get_param_end_date = "";

        if(startDate && endDate) {
            
            var myStartDate = startDate.toDate(),
                myEndDate = endDate.toDate();

            // start_date = new Date(myStartDate.getTime()),
            // end_date = new Date(myEndDate.getTime());

            start_date = myStartDate.getTime(),
            end_date = myEndDate.getTime();

            try {
                if($("#"+service_id+"_chart").highcharts()) {
                    var chart = $("#"+service_id+"_chart").highcharts(),
                        chart_series = chart.series;

                    if(chart_series && chart_series.length > 0) {
                        // Remove series from highchart
                        while(chart_series.length > 0) {
                            chart_series[0].remove(true);
                        }
                    }
                    // Destroy highchart
                    $("#"+service_id+"_chart").highcharts().destroy();

                }

                if($("#"+service_id+"_bottom_table").length) {
                    $("#"+service_id+"_bottom_table").html("");
                }

                get_param_start_date = getDateInEpochFormat(start_date);
                get_param_end_date = getDateInEpochFormat(end_date)

            } catch(e) {
                // console.log(e);
            }
        } else {
            start_date = '';
            end_date = '';
        }

        if(listing_ajax_url.indexOf("?") > -1) {
            listing_ajax_url = listing_ajax_url+"&start_date="+get_param_start_date+"&end_date="+get_param_end_date;
        } else {
            listing_ajax_url = listing_ajax_url+"?start_date="+get_param_start_date+"&end_date="+get_param_end_date;
        }
        
        // Send ajax call
        sendAjax(start_date, end_date);

        // This function returns date object as per given date string
        function getDate(date) {
            var dateSplittedString = date.split('-');
            return new Date(dateSplittedString[2], (parseInt(dateSplittedString[1], 10) - 1), dateSplittedString[0]);
        }

        // This function returns next date as per given date
        function getTomorrowDate(date) {
            var tomorowDate = new Date(date);
            tomorowDate.setFullYear(date.getFullYear());
            tomorowDate.setMonth(date.getMonth());
            tomorowDate.setDate(date.getDate() + 1);
            return tomorowDate;
        }

        // This function return given date in DD-mm-YYYY format
        function getDateinStringFormat(date) {
            if(date) {
                return date.getDate() + "-" + (parseInt(date.getMonth(), 10) + 1) + "-" + date.getFullYear();
            } else {
                return '';
            }
        }


        // This function convert given date, time in epoch format.
        function getDateInEpochFormat(date, time) {
            new_date = new Date(date);
            return (new_date.getTime()) / 1000;
        }

        // This function send ajax call as per given param to get device service perf info. 
        function sendAjax(ajax_start_date, ajax_end_date) {

            var urlDataStartDate = '', urlDataEndDate = '';
            if(ajax_start_date == '' && ajax_end_date == '') {  
                // Pass              
            } else {
                var end_Date = "";
                if(moment(ajax_start_date).date() == moment(ajax_end_date).date() && moment(ajax_start_date).dayOfYear() == moment(ajax_end_date).dayOfYear()) {
                    end_Date = moment(ajax_end_date).toDate();
                } else {
                    end_Date = moment(ajax_start_date).endOf('day').toDate();
                }
                urlDataStartDate = getDateInEpochFormat(ajax_start_date);
                urlDataEndDate = getDateInEpochFormat(end_Date)
            }

            $.ajax({
                url: get_url,
                data: {
                    'start_date': urlDataStartDate,
                    'end_date': urlDataEndDate
                },
                type: "GET",
                dataType: "json",
                success: function (response) {
                    // TESTING DATA JSON
                    // $.getJSON(base_url+"/static/js/nocout/dummy_data/bs_temperature.json",function(response) {
                    var result = "";
                    // Type check of response
                    if(typeof response == 'string') {
                        result = JSON.parse(response);
                    } else {
                        result = response;
                    }

                    if(result.success == 1) {

                        var grid_headers = result.data.objects.table_data_header;

                        if(grid_headers && grid_headers.length > 0) {
                            // Hide display type option from only table tabs
                            if(!$("#display_type_container").hasClass("hide")) {
                                $("#display_type_container").addClass("hide")
                            }

                            if(typeof(grid_headers[0]) == 'string') {
                                var table_data = result.data.objects.table_data ? result.data.objects.table_data : [];
                                if($("#other_perf_table").length == 0) {
                                    initNormalDataTable_nocout(
                                        'other_perf_table',
                                        grid_headers,
                                        service_id
                                    );
                                }

                                // Call addDataToNormalTable_nocout (utilities) function to add data to initialize datatable
                                addDataToNormalTable_nocout(
                                    table_data,
                                    grid_headers,
                                    'other_perf_table'
                                );
                            } else {
                                $('#'+service_id+'_chart').html("");

                                initChartDataTable_nocout(
                                    "other_perf_table",
                                    grid_headers,
                                    service_id,
                                    listing_ajax_url,
                                    true
                                );
                            }
                        } else {
                            var chart_config = result.data.objects;

                            if(
                                listing_ajax_url.indexOf('service/rf/') > -1
                                ||
                                listing_ajax_url.indexOf('servicedetail') > -1
                                ||
                                listing_ajax_url.indexOf('availability') > -1) {
                                // Show display type option from only table tabs
                                if(!$("#display_type_container").hasClass("hide")) {
                                    $("#display_type_container").addClass("hide")
                                }
                                draw_type = 'chart';
                                // Checked the chart type radio
                                $('#display_chart')[0].checked = true
                            } else {
                                // Show display type option from only table tabs
                                if($("#display_type_container").hasClass("hide")) {
                                    $("#display_type_container").removeClass("hide")
                                }
                            }

                            // If any data available then plot chart & table
                            if(chart_config.chart_data.length > 0) {
                                if(draw_type == 'chart') {

                                    if($("#perf_data_table").length > 0 && $("#perf_data_table").html()) {
                                        $("#perf_data_table").dataTable().fnDestroy();
                                        $("#perf_data_table").remove();
                                    }

                                    if(!$('#'+service_id+'_chart').highcharts()) {
                                        createHighChart_nocout(chart_config,service_id, false, false, function(status) {
                                            // 
                                        });
                                    } else {
                                        addPointsToChart_nocout(chart_config.chart_data,service_id);
                                    }

                                    // To show the table in case of utilization_top tab
                                    if(listing_ajax_url.indexOf('servicedetail') > -1) {
                                        var contentHtml = createChartDataTableHtml_nocout(
                                            "perf_data_table",
                                            chart_config.chart_data
                                        );

                                        $('#'+service_id+'_bottom_table').html(contentHtml);

                                        $("#perf_data_table").DataTable({
                                            bPaginate: true,
                                            bDestroy: true,
                                            aaSorting : [[0,'desc']],
                                            sPaginationType: "full_numbers"
                                        });
                                    }

                                } else {
                                    // Destroy highchart if exists
                                    if($('#'+service_id+'_chart').highcharts()) {
                                        $('#'+service_id+'_chart').highcharts().destroy();
                                    }
                                    // Clear CHART DIV HTML
                                    $('#'+service_id+'_chart').html("");

                                    if(listing_ajax_url.indexOf('servicedetail') == -1) {
                                        initChartDataTable_nocout(
                                            "perf_data_table",
                                            chart_config.chart_data,
                                            service_id,
                                            listing_ajax_url,
                                            false
                                        );
                                    }
                                }
                            } else {
                                if(draw_type == 'chart') {
                                    if($("#perf_data_table").length > 0 && $("#perf_data_table").html()) {
                                        $("#perf_data_table").dataTable().fnDestroy();
                                        $("#perf_data_table").remove();
                                    }

                                    if(!$.trim(ajax_start_date) && !$.trim(ajax_end_date)) {
                                        if (!$('#'+service_id+'_chart').highcharts()) {
                                            $('#'+service_id+'_chart').html(result.message);
                                        }
                                    }
                                } else {

                                    if(listing_ajax_url.indexOf('servicedetail') == -1) {
                                        $('#'+service_id+'_chart').html("");
                                        var table_headers = default_live_table_headers;

                                        if(show_historical_on_performance && listing_ajax_url.indexOf("availability")  == -1 && listing_ajax_url.split("data_for=")[1].indexOf('live') == -1) {
                                            table_headers = default_hist_table_headers;
                                        }
                                        initChartDataTable_nocout(
                                            "perf_data_table",
                                            table_headers,
                                            service_id,
                                            listing_ajax_url,
                                            true
                                        );
                                    }
                                }
                            }
                        }
                    } else {

                        if(
                            listing_ajax_url.indexOf('service/rf/') > -1
                            ||
                            listing_ajax_url.indexOf('servicedetail') > -1
                            ||
                            listing_ajax_url.indexOf('availability') > -1
                        ) {
                            // Show display type option from only table tabs
                            if(!$("#display_type_container").hasClass("hide")) {
                                $("#display_type_container").addClass("hide")
                            }

                            draw_type = 'chart';
                            // Checked the chart type radio
                            $('#display_chart')[0].checked = true
                        } else {
                            // Show display type option from only table tabs
                            if($("#display_type_container").hasClass("hide")) {
                                $("#display_type_container").removeClass("hide")
                            }
                        }

                        if(draw_type == 'chart') {
                            if($("#perf_data_table").length > 0 && $("#perf_data_table").html()) {
                                $("#perf_data_table").dataTable().fnDestroy();
                                $("#perf_data_table").remove();
                            }

                            if(!$.trim(ajax_start_date) && !$.trim(ajax_end_date)) {
                                if(!$('#'+service_id+'_chart').highcharts()) {
                                    $('#'+service_id+'_chart').html(result.message);
                                }
                            }
                        } else {
                            // Clear chart DIV HTML
                            $('#'+service_id+'_chart').html("");

                            var table_headers = default_live_table_headers;

                            if(show_historical_on_performance && listing_ajax_url.split("data_for=")[1].indexOf('live') == -1) {
                                table_headers = default_hist_table_headers;
                            }

                            initChartDataTable_nocout(
                                "perf_data_table",
                                table_headers,
                                service_id,
                                listing_ajax_url,
                                true
                            );
                        }
                    }

                    if(draw_type == 'chart') {
                        //check condition if start date and end date is defined.
                        if($.trim(ajax_start_date) && $.trim(ajax_end_date)) {
                            //if last date
                            if(moment(ajax_start_date).date() == moment(ajax_end_date).date() && moment(ajax_start_date).dayOfYear() == moment(ajax_end_date).dayOfYear()) {

                                if($('#'+service_id+'_chart').highcharts()) {
                                    $('#' + service_id + '_chart').highcharts().redraw();
                                }

                                if (!$('#'+service_id+'_chart').highcharts()) {
                                    $('#'+service_id+'_chart').html(result.message);
                                }

                                hideSpinner();
                            //Else sendAjax request for next Date
                            } else {

                                var nextDay = moment(ajax_start_date).add(1, 'd');
                                var ohayoo = nextDay.startOf('day');
                                timeInterval = setTimeout(function () {
                                    (function(ohayoo) {
                                        sendAjax(ohayoo.toDate(), ajax_end_date);
                                    })(ohayoo);
                                }, 400);
                            }
                        } else {
                            hideSpinner();
                        }
                    } else {
                        hideSpinner();
                    }

                    // });
                },
                error : function(err) {
                    // console.log(err.statusText);
                    $.gritter.add({
                        // (string | mandatory) the heading of the notification
                        title: 'Performance - Service Data',
                        // (string | mandatory) the text inside the notification
                        text: err.statusText,
                        // (bool | optional) if you want it to fade out on its own or just sit there
                        sticky: false
                    });

                    hideSpinner();
                }
            });
        }
    };
    /**
     * This function reset the live polling section
     * @method resetLivePolling
     */
    this.resetLivePolling = function(container_dom_id) {
        // Enable the "Poll Now" button
        if($("#"+container_dom_id+" .perf_poll_now").length > 0) {
            $("#"+container_dom_id+" .perf_poll_now").button("complete");
        }

        // Reset the input values
        if($("#"+container_dom_id+" #perf_live_poll_input").length > 0) {
            $("#"+container_dom_id+" #perf_live_poll_input").val("");
        }

        // Reset the Chart container
        if($("#"+container_dom_id+" #perf_live_poll_chart").length > 0) {
            $("#"+container_dom_id+" #perf_live_poll_chart").html("");
        }

        try {
            if(perf_page_live_polling_call) {
                perf_page_live_polling_call.abort();
                perf_page_live_polling_call = "";
            }
        } catch(e) {
            // console.error(e);
        }
    };

    /**
     * This function initializes
     * @method initGetServiceData
     * @param get_service_data_url "String", It contains the url to fetch the status of current device.
     * @param service_id "String", It contains unique name for service.
     * @param device_id "INT", It contains the ID of current device.
     */
    this.initGetServiceData = function(get_service_data_url, service_id, device_id) {
        /*Reset Variables & counters */
        if(timeInterval) {
            clearTimeout(timeInterval);
        }

        if($('#'+service_id+'_chart').highcharts()) {
            $('#'+service_id+'_chart').highcharts().destroy();
        }

        for(var i=0;i<Highcharts.charts.length;i++) {
            if(Highcharts.charts[i]) {
                Highcharts.charts[i].destroy();
            }
        }
        
        Highcharts.charts = [];

        /*Call getServiceData function to fetch the data for clicked service tab*/
        perfInstance.getServiceData(get_service_data_url, service_id, device_id);
    };
}


$('.inner_tab_container').delegate('ul.inner_inner_tab li a','click',function (e) {
    var current_target = e.currentTarget,
        current_attr = current_target.attributes,
        tab_service_id = current_target.id.slice(0, -4);

    var service_data_url_val = current_attr.url ? $.trim(current_attr.url.value) : "";
        serviceDataUrl = "";

    if(service_data_url_val) {
        if(service_data_url_val[0] != "/") {
            serviceDataUrl = "/"+service_data_url_val;
        } else {
            serviceDataUrl = service_data_url_val;
        }
    }

    if(show_historical_on_performance) {
        perfInstance.initGetServiceData(serviceDataUrl, tab_service_id, current_device);
    }

});

// Change event on display type radio buttons
$('input[name="item_type"]').change(function(e) {

    var top_tab_content_href = $(".top_perf_tabs > li.active a").attr("href"),
        top_tab_content_id = top_tab_content_href.split("#").length > 1 ? top_tab_content_href.split("#")[1] : top_tab_content_href.split("#")[0];
    

    if(show_historical_on_performance) {
        var left_active_tab_href = $("#"+top_tab_content_id+" .left_tabs_container li.active a").attr("href"),
            left_tab_content_id = left_active_tab_href.split("#").length > 1 ? left_active_tab_href.split("#")[1] : left_active_tab_href.split("#")[0];

        var active_inner_tab = $("#"+left_tab_content_id+" .inner_inner_tab li.active a"),
            service_id = active_inner_tab.attr("id").slice(0, -4),
            get_service_data_url = active_inner_tab.attr("url");

    } else {

        var left_active_tab_anchor = $("#"+top_tab_content_id+" .left_tabs_container li.active a"),
            active_inner_tab = $('.top_perf_tab_content div.active .inner_tab_container .nav-tabs li.active a'),
            service_id = left_active_tab_anchor.attr("id").slice(0, -4),
            get_service_data_url = left_active_tab_anchor.attr("url");
    }

    if(
        service_id.indexOf('availability') > -1
        ||
        service_id.indexOf('utilization_top') > -1
        ||
        service_id.indexOf('topology') > -1
    ) {

        var active_inner_tab = $('.top_perf_tab_content div.active .inner_tab_container .nav-tabs li.active a'),
            service_id = active_inner_tab.attr("id").slice(0, -4),
            get_service_data_url = active_inner_tab.attr("url");

    } 

    if(get_service_data_url && service_id && current_device) {

        if($("#other_perf_table").length > 0) {
            $("#other_perf_table").dataTable().fnDestroy();
            $("#other_perf_table").remove();
        }

        if($("#perf_data_table").length > 0) {
            $("#perf_data_table").dataTable().fnDestroy();
            $("#perf_data_table").remove();
        }

        perfInstance.initGetServiceData(get_service_data_url, service_id, current_device);
    }
});