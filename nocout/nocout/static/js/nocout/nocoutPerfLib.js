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
    base_url = "";

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
     * This function call the server to get all the devices data & then populate it to the dropdown
     * @class nocout.perf.lib
     * @method getAllDevices
     * @param get_device_url "String", It contains the url to fetch the devices list.
     * @param device_id "INT", It contains the ID of current device.
     */
    this.getAllDevices = function (get_device_url, device_id) {
        /*Ajax call to Get Devices API*/
        var get_url = get_device_url;
        // $.ajax({
        //     url: get_url,
        //     type: "GET",
        //     dataType: "json",
        //     success: function (response) {

        //         var result = "";
        //         // Type check of response
        //         if(typeof response == 'string') {
        //             result = JSON.parse(response);
        //         } else {
        //             result = response;
        //         }

        //         if (result.success == 1) {
        //             allDevices = result.data.objects;
        //             var devices_options = '<option value="">Select Device</option>';
        //             $.each(allDevices, function (key, value) {
        //                 if (value.id == device_id) {
        //                     devices_options += '<option value="' + value.id + '" selected>' + value.technology + ':' + value.alias + '</option>';
        //                 } else {
        //                     devices_options += '<option value="' + value.id + '">' + value.technology + ':' + value.alias + '</option>';
        //                 }
        //             });
        //             $("#device_name").html(devices_options);
        //         } else {
        //             $.gritter.add({
        //                 // (string | mandatory) the heading of the notification
        //                 title: 'Performance',
        //                 // (string | mandatory) the text inside the notification
        //                 text: result.message,
        //                 // (bool | optional) if you want it to fade out on its own or just sit there
        //                 sticky: false
        //             });
        //         }
        //     },
        //     error: function (err) {
        //         $.gritter.add({
        //             // (string | mandatory) the heading of the notification
        //             title: 'Performance',
        //             // (string | mandatory) the text inside the notification
        //             text: err.statusText,
        //             // (bool | optional) if you want it to fade out on its own or just sit there
        //             sticky: false
        //         });
        //     }
        // });
    };

    /**
     * This function fetch the status of current device
     * @class nocout.perf.lib
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

                if (result.success == 1) {

                    device_status = result.data.objects;

                    if(device_status.headers && device_status.headers.length > 0) {
                        /*Loop for table headers*/
                        var headers = "<tr>";
                        $.each(device_status.headers, function (key, value) {
                            headers += '<th>' + value + '</th>';
                        });

                        headers += "</tr>";
                        /*Populate table headers*/
                        $("#status_table thead").html(headers);

                        /*Loop for status table data*/
                        var status_val = "";
                        status_val += "<tr>";
                        for (var i = 0; i < device_status.values.length; i++) {
                            var val = device_status.values[i]["val"] ? device_status.values[i]["val"] : "",
                                url = device_status.values[i]["url"] ? device_status.values[i]["url"] : "",
                                display_txt = url ? '<a href="'+url+'" target="_blank">' + val + '</a>' : val;

                            status_val += '<td>'+display_txt+'</td>';
                        }
                        status_val += "</tr>";
                        
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
     * This function fetch the list of services
     * @class nocout.perf.lib
     * @method getServices
     * @param get_service_url "String", It contains the url to fetch the services.
     * @param device_id "INT", It contains the ID of current device.
     */
    this.getServices = function (get_service_url, device_id) {

        /*Show the spinner*/
        showSpinner();

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

                    var device_services_tab = Object.keys(result.data.objects);

                    /*Loop to get services from object*/
                    var li_style = "background: #f5f5f5; width:100%; border:1px solid #dddddd;"
                    var li_a_style = "background: none; border:none;";

                    var first_loop = 0;

                    if (device_services_tab.length > 0) {
                        for (var i = 0; i < device_services_tab.length; i++) {
                            device_services = "";
                            tabs_with_data = "";
                            var tab_id = device_services_tab[i].split("_tab")[0];

                            if ($("#" + device_services_tab[i]).hasClass("active")) {
                                $("#" + device_services_tab[i]).removeClass("active");
                            }

                            if ($("#" + tab_id).parent("li").hasClass("active")) {
                                $("#" + tab_id).parent("li").removeClass("active");
                            }

                            device_services = result.data.objects[device_services_tab[i]].info;

                            if(device_services && device_services.length > 0) {
                                var left_section_class = "col-md-3",
                                    right_section_class = "col-md-9"
                                
                                if(device_services.length == 1) {
                                    left_section_class = "hide",
                                    right_section_class = "col-md-12"
                                }

                                var tabs_with_data = "";
                                var service_tabs = '<div class="left_tabs_container '+left_section_class+'"><ul class="nav nav-tabs">';

                                var service_tabs_data = '<div class="'+right_section_class+'" style="padding:0px 0px 0px 10px;">';
                                service_tabs_data += '<div class="tab-content">';

                                var is_first_tab = 0;

                                if (result.data.objects[device_services_tab[i]].isActive == 1) {
                                    is_first_tab = 1;
                                    $("#" + tab_id).parent("li").addClass("active");
                                    $("#" + device_services_tab[i]).addClass("active");
                                }

                                var count = 0;

                                $.each(device_services, function (key, value) {

                                    if (is_first_tab == 1 && count == 0) {
                                        active_tab_id = device_services_tab[i]+'_'+String(count)+'_'+String(i);
                                        active_tab_content_dom_id = device_services_tab[i]+'_'+String(count)+'_'+String(i)+'_block';
                                        active_tab_url = "/" + value.url;

                                        service_tabs += '<li class="active" style="'+ li_style + '">';
                                        service_tabs += '<a href="#'+device_services_tab[i]+'_'+String(count)+'_'+String(i)+'_block" ';
                                        service_tabs += ' url="' + value.url + '" id="'+device_services_tab[i]+'_'+String(count)+'_'+String(i)+'_tab" data-toggle="tab" style="';
                                        service_tabs += li_a_style+'">' + value.title + '</a></li>';

                                        service_tabs_data += '<div class="tab-pane active" ';
                                        service_tabs_data += 'id="'+device_services_tab[i]+'_'+String(count)+'_'+String(i)+'_block">';
                                        service_tabs_data += '<div align="center" id="last_updated_'+device_services_tab[i]+'_'+String(count)+'_'+String(i)+'_block">';
                                        service_tabs_data += '</div><div class="chart_container"><div id="'+device_services_tab[i]+'_'+String(count)+'_'+String(i)+'_chart"';
                                        service_tabs_data += ' style="height:350px;width:100%;"></div><div class="divide-20"></div>';
                                        service_tabs_data += '<div id="'+device_services_tab[i]+'_'+String(count)+'_'+String(i)+'_bottom_table"></div></div></div>';

                                    } else {

                                        service_tabs += '<li class="" style="' + li_style + '">';
                                        service_tabs += '<a href="#'+device_services_tab[i]+'_'+String(count)+'_'+String(i)+'_block" ';
                                        service_tabs += 'url="' + value.url + '" id="'+device_services_tab[i]+'_'+String(count)+'_'+String(i)+'_tab" ';
                                        service_tabs += 'data-toggle="tab" style="' + li_a_style + '">' + value.title + '</a></li>';

                                        service_tabs_data += '<div class="tab-pane" id="'+device_services_tab[i]+'_'+String(count)+'_'+String(i)+'_block">';
                                        service_tabs_data += '<div align="center" ';
                                        service_tabs_data += 'id="last_updated_'+device_services_tab[i]+'_'+String(count)+'_'+String(i)+'_block">';
                                        service_tabs_data += '</div><div class="chart_container" style="width:100%;"><div id="'+device_services_tab[i]+'_'+String(count)+'_'+String(i)+'_chart" ';
                                        service_tabs_data += 'style="height:350px;width:100%;"></div><div class="divide-20"></div>';
                                        service_tabs_data += '<div id="'+device_services_tab[i]+'_'+String(count)+'_'+String(i)+'_bottom_table"></div></div></div>';
                                    }
                                    count++;


                                    // if (is_first_tab == 1 && count == 0) {
                                    //     active_tab_id = value.name;
                                    //     active_tab_content_dom_id = value.name + "_" + device_services_tab[i] + '_block';
                                    //     active_tab_url = "/" + value.url;
                                    //     count++;
                                    //     service_tabs += '<li class="active" style="' + li_style + '"><a href="#' + value.name + "_" + device_services_tab[i] + '_block" url="' + value.url + '" id="' + value.name + '_tab" data-toggle="tab" style="' + li_a_style + '">' + value.title + '</a></li>';
                                    //     service_tabs_data += '<div class="tab-pane active" id="' + value.name + "_" + device_services_tab[i] + '_block"><div align="center" id="last_updated_' + value.name + "_" + device_services_tab[i] + '_block"></div><div class="chart_container"><div id="' + value.name + '_chart" style="height:350px;width:100%;"></div><div class="divide-20"></div><div id="' + value.name + '_bottom_table"></div></div></div>';
                                    // } else {
                                    //     service_tabs += '<li class="" style="' + li_style + '"><a href="#' + value.name + "_" + device_services_tab[i] + '_block" url="' + value.url + '" id="' + value.name + '_tab" data-toggle="tab" style="' + li_a_style + '">' + value.title + '</a></li>';
                                    //     service_tabs_data += '<div class="tab-pane" id="' + value.name + "_" + device_services_tab[i] + '_block"><div align="center" id="last_updated_' + value.name + "_" + device_services_tab[i] + '_block"></div><div class="chart_container" style="width:100%;"><div id="' + value.name + '_chart" style="height:350px;width:100%;"></div><div class="divide-20"></div><div id="' + value.name + '_bottom_table"></div></div></div>';
                                    // }

                                });

                                service_tabs += '</ul></div>';
                                service_tabs_data += '</div>';
                                tabs_with_data = service_tabs + " " + service_tabs_data;
                            } else {
                                if(!$("#" + tab_id).hasClass("hide")) {
                                    $("#" + tab_id).addClass("hide")
                                }
                            }

                            $("#" + device_services_tab[i] + " .inner_tab_container .panel-body .tabs-left").html(tabs_with_data);
                        }

                        /*Bind click event on tabs*/
                        $('.inner_tab_container .nav-tabs li a').click(function (e) {
                            // show loading spinner
                            showSpinner();
                            var serviceId = e.currentTarget.id.slice(0, -4),
                                splitted_local_id = e.currentTarget.attributes.href.value.split("#"),
                                tab_content_dom_id = splitted_local_id.length > 1 ? splitted_local_id[1] : splitted_local_id[0];

                            //@TODO: all the ursl must end with a / - django style
                            var serviceDataUrl = "/" + $.trim(e.currentTarget.attributes.url.value);
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

                            if($('#'+serviceId+'_chart').highcharts()) {
                                $('#'+serviceId+'_chart').highcharts().destroy();
                            }

                            for(var i=0;i<Highcharts.charts.length;i++) {
                                if(Highcharts.charts[i]) {
                                    Highcharts.charts[i].destroy();
                                }
                            }
                            
                            Highcharts.charts = [];

                            // First get the service status then get the data for that service
                            perfInstance.getServiceStatus(serviceDataUrl,function(response_type,data_obj) {
                                if(response_type == 'success') {
                                    // Call function to populate latest status for this service
                                    populateServiceStatus_nocout("last_updated_"+tab_content_dom_id,data_obj);
                                } else {
                                    $("#last_updated_"+tab_content_dom_id).html("");
                                }
                                perfInstance.getServiceData(serviceDataUrl, serviceId, current_device);
                            });

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
                hideSpinner();

            },
            error: function (err) {

                $(".inner_tab_container").html(err.statusText);

                /*Hide the spinner*/
                hideSpinner();
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

                    /*Get Last opened tab id from cookie*/
                    var parent_tab_id = $.cookie('parent_tab_id');
                    //If parent Tab id is there & parent tab element exist in the dom.
                    if(parent_tab_id && $('#'+parent_tab_id).length) {
                        $('#'+parent_tab_id).trigger('click');
                    } else {
                        // show loading spinner
                        showSpinner();
                        perfInstance.getServiceStatus(active_tab_url,function(response_type,data_obj) {
                            if(response_type == 'success') {
                                // Call function to populate latest status for this service
                                populateServiceStatus_nocout("last_updated_"+active_tab_content_dom_id,data_obj);
                            } else {
                                $("#last_updated_"+active_tab_content_dom_id).html("");
                            }
                            /*Call getServiceData function to fetch the data for currently active service*/
                            perf_that.getServiceData(active_tab_url, active_tab_id, device_id, data_obj);
                        });
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

        var updated_url = service_status_url.split("/")[service_status_url.split("/").length -1] != "" ? service_status_url+"/" : service_status_url,
            device_id = service_status_url.split("/")[service_status_url.split("/").length -1] != "" ? service_status_url.split("/")[service_status_url.split("/").length -1] : service_status_url.split("/")[service_status_url.split("/").length -2];

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
            },
            error : function(err) {
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

        // Decrement the tabs click on evert click counter
        tabs_click_counter--;

        $.cookie('activeTabId', service_id+"_tab", {path: '/', secure: true});

        var start_date = "",
            end_date = "",
            get_url = "";

        showSpinner();

        window.location.href = '#' + get_service_data_url.split('/')[3] + "#" + get_service_data_url.split('/')[5];

        get_url = base_url + "" + get_service_data_url;

        start_date = $.urlParam('start_date');
        end_date = $.urlParam('end_date');

        if (start_date && end_date) {
            start_date = new Date(start_date*1000);
            end_date = new Date(end_date*1000);
            sendAjax(start_date, end_date);
        } else {
            sendAjax('', '');
        }

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

            if (!(ajax_start_date && ajax_end_date)) {
//                 hideSpinner();
                // return;
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

                    var result = "";
                    // Type check of response
                    if(typeof response == 'string') {
                        result = JSON.parse(response);
                    } else {
                        result = response;
                    }

                    if(result.success == 1) {

                        var table_headers = result.data.objects.table_data_header;

                        if(table_headers && table_headers.length > 0) {
                            var table_data = result.data.objects.table_data ? result.data.objects.table_data : [];
                            if($("#other_perf_table").length == 0) {
                                initNormalDataTable_nocout(
                                    'other_perf_table',
                                    table_headers,
                                    service_id
                                );
                            }

                            // Call addDataToNormalTable_nocout (utilities) function to add data to initialize datatable
                            addDataToNormalTable_nocout(
                                table_data,
                                table_headers,
                                'other_perf_table'
                            );
                        } else {
                            var chart_config = result.data.objects;
                            // If any data available then plot chart & table
                            if(chart_config.chart_data.length > 0) {
                                if(!$('#'+service_id+'_chart').highcharts()) {
                                    createHighChart_nocout(chart_config,service_id);
                                    initChartDataTable_nocout("perf_data_table", chart_config.chart_data,service_id);
                                } else {
                                    addPointsToChart_nocout(chart_config.chart_data,service_id);
                                }
                                if ($("#perf_data_table").length > 0) {
                                    addDataToChartTable_nocout(chart_config.chart_data, 'perf_data_table')
                                }
                            }
                        }
                    }

                    //check condition if start date and end date is defined.
                    if($.trim(ajax_start_date) && $.trim(ajax_end_date)) {

                        //if last date
                        if(moment(ajax_start_date).date() == moment(ajax_end_date).date() && moment(ajax_start_date).dayOfYear() == moment(ajax_end_date).dayOfYear()) {

                            if ($('#'+service_id+'_chart').highcharts()) {
                                $('#' + service_id + '_chart').highcharts().redraw();
                            }

                            if (!$('#'+service_id+'_chart').highcharts() && $("#other_perf_table").length == 0) {
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
                }
            });
        }
    };
}