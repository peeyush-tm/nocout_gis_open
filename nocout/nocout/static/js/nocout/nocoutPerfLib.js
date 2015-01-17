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
    green_color = "#468847",
    red_color = "#b94a48",
    green_status_array = ['ok','success','up'],
    red_status_array = ['warning','critical','down'],
    left_block_style = "border:1px solid #CCC;border-right:0px;padding: 3px 5px;background:#FFF;",
    right_block_style = "border:1px solid #CCC;padding: 3px 5px;background:#FFF;";

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
                    allDevices = result.data.objects;
                    var devices_options = '<option value="">Select Device</option>';
                    $.each(allDevices, function (key, value) {
                        if (value.id == device_id) {
                            devices_options += '<option value="' + value.id + '" selected>' + value.technology + ':' + value.alias + '</option>';
                        } else {
                            devices_options += '<option value="' + value.id + '">' + value.technology + ':' + value.alias + '</option>';
                        }
                    });
                    $("#device_name").html(devices_options);
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
                    for (var i = 0; i < device_status.values.length; i++) {
                        status_val += "<tr>"
                        var loop_through = device_status.values[i];
                        $.each(loop_through, function (key, value) {
                            status_val += '<td>' + value + '</td>';
                        });
                        status_val += "</tr>";
                    }

                    /*Populate table data*/
                    $("#status_table tbody").html(status_val);
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
                            var serviceId = e.currentTarget.id.slice(0, -4),
                                splitted_local_id = e.currentTarget.attributes.href.value.split("#"),
                                tab_content_dom_id = splitted_local_id.length > 1 ? splitted_local_id[1] : splitted_local_id[0];
                            //@TODO: all the ursl must end with a / - django style
                            var serviceDataUrl = "/" + $.trim(e.currentTarget.attributes.url.value);
                            /*Reset Variables & counters */
                            clearTimeout(timeInterval);
                            chart_instance = "";
                            $("#other_perf_table").remove();
                            $("#perf_data_table").remove();
                            // First get the service status then get the data for that service
                            perfInstance.getServiceStatus(serviceDataUrl,function(response_type,data_obj) {
                                if(response_type == 'success') {
                                    if($.trim(data_obj.last_updated) != "" || $.trim(data_obj.perf) != "") {
                                        var last_updated = data_obj.last_updated ? data_obj.last_updated : "N/A",
                                            perf = data_obj.perf ? data_obj.perf : "N/A",
                                            inner_status_html = '';
                                        
                                        inner_status_html += '<table id="perf_ourput_table" class="table table-responsive table-bordered" style="background:#F5F5F5;">';
                                        inner_status_html += '<tr>';
                                        inner_status_html += '<td><b>Latest Performance Output</b> : '+perf+'</td>';
                                        inner_status_html += '<td><b>Last Updated At</b> : '+last_updated+'</td>';
                                        inner_status_html += '</tr>';
                                        inner_status_html += '</table><div class="clearfix"></div><div class="divide-20"></div>';
                                        $("#last_updated_"+tab_content_dom_id).html(inner_status_html);
                                    } else {
                                        $("#last_updated_"+tab_content_dom_id).html("");
                                    }
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
                if (active_tab_url && active_tab_id) {
                    /*Call getServiceData function to fetch the data for currently active service*/
                    /*Reset Variables & counters */
                    clearTimeout(timeInterval);
                    chart_instance = "";
                    $("#other_perf_table").remove();
                    $("#perf_data_table").remove();
                    /*Get Last opened tab id from cookie*/
                    var parent_tab_id = $.cookie('parent_tab_id');
                    //If parent Tab id is there & parent tab el exist in the dom.
                    if(parent_tab_id && $('#'+parent_tab_id).length) {
                        $('#'+parent_tab_id).trigger('click');
                    } else {
                        perfInstance.getServiceStatus(active_tab_url,function(response_type,data_obj) {
                            if(response_type == 'success') {
                                if($.trim(data_obj.last_updated) != "" || $.trim(data_obj.perf) != "") {
                                    var last_updated = data_obj.last_updated ? data_obj.last_updated : "N/A",
                                        perf = data_obj.perf ? data_obj.perf : "N/A",
                                        inner_status_html = '';

                                    inner_status_html += '<table id="perf_ourput_table" class="table table-responsive table-bordered" style="background:#F5F5F5;">';
                                    inner_status_html += '<tr>';
                                    inner_status_html += '<td><b>Latest Performance Output</b> : '+perf+'</td>';
                                    inner_status_html += '<td><b>Last Updated At</b> : '+last_updated+'</td>';
                                    inner_status_html += '</tr>';
                                    inner_status_html += '</table><div class="clearfix"></div><div class="divide-20"></div>';
                                    
                                    $("#last_updated_"+active_tab_content_dom_id).html(inner_status_html);
                                } else {
                                    $("#last_updated_"+active_tab_content_dom_id).html("");
                                }
                            } else {
                                $("#last_updated_"+active_tab_content_dom_id).html("");
                            }
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

        $.ajax({
            url : base_url+""+updated_url,
            type : "GET",
            success : function(response) {
                var result = "",
                    age = "",
                    lastDownTime = "",
                    last_updated = "",
                    perf = "",
                    status = "",
                    txt_color = "",
                    status_html = "";

                // Type check of response
                if(typeof response == 'string') {
                    result = JSON.parse(response);
                } else {
                    result = response;
                }

                if(result.data && result.data.objects) {
                    age = result.data.objects.age ? result.data.objects.age : "Unknown";
                    lastDownTime = result.data.objects.last_down_time ? result.data.objects.last_down_time : "Unknown";
                    status = result.data.objects.status ? result.data.objects.status.toUpperCase() : "Unknown";
                    last_updated = result.data.objects.last_updated ? result.data.objects.last_updated : "";
                    perf = result.data.objects.perf ? result.data.objects.perf : "";

                    if(green_status_array.indexOf($.trim(status.toLowerCase()))  > -1) {
                        txt_color = green_color;
                    } else if(red_status_array.indexOf($.trim(status.toLowerCase()))  > -1) {
                        txt_color = red_color;
                    } else {
                        txt_color = "";
                    }

                    status_html = "";

                    status_html += '<table id="final_status_table" class="table table-responsive table-bordered" style="background:#FFFFFF;"><tr>';
                    status_html += '<td style="color:'+txt_color+';"><i class="fa fa-circle" style="vertical-align: middle;"> </i> <b>Current Status</b> : '+status+'</td>';
                    status_html += '<td style="color:'+txt_color+';"><b>Current Status Since</b> : '+age+'</td>';
                    status_html += '<td style="color:'+txt_color+';"><b>Last Down Time</b> : '+lastDownTime+'</td>';
                    status_html += '</tr></table>';

                    // Update Status Block HTML as per the device status
                    $("#latestStatusContainer").html(status_html);

                    var response_obj = {
                        "last_updated" : last_updated,
                        "perf" : perf
                    };

                    callback("success",response_obj);
                }
            },
            error : function(err) {
                // console.log(err.statusText);
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
        // base_url = window.location.origin ? window.location.origin : window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port : '');

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

        function getDate(date) {
            var dateSplittedString = date.split('-');
            return new Date(dateSplittedString[2], (parseInt(dateSplittedString[1], 10) - 1), dateSplittedString[0]);
        }

        function getTomorrowDate(date) {
            var tomorowDate = new Date(date);
            tomorowDate.setFullYear(date.getFullYear());
            tomorowDate.setMonth(date.getMonth());
            tomorowDate.setDate(date.getDate() + 1);
            return tomorowDate;
        }

        function getDateinStringFormat(date) {
            if (date) {
                return date.getDate() + "-" + (parseInt(date.getMonth(), 10) + 1) + "-" + date.getFullYear();
            } else {
                return '';
            }

        }


        function getDateInEpochFormat(date, time) {

            // var split_time = time.split(":");
            // var new_date = moment(date).add(split_time[0], 'h').add(split_time[1], 'm').add(split_time[2], 's');
            new_date = new Date(date);
            return (new_date.getTime()) / 1000;
        }

        function createHighChart(config) {
            // Is the y axis should be reversed or not
            var is_y_inverted = config["is_inverted"] ? config["is_inverted"] : false;

            chart_instance = $('#' + service_id + '_chart').highcharts({
                chart: {
                    events: {
                        load : function() {
                            // Hide highcharts.com link from chart when chart is loaded
                            var highcharts_link = $("#"+service_id+"_chart svg text:last-child");
                            $.grep(highcharts_link,function(val) {
                                if($.trim(val.innerHTML) == 'Highcharts.com') {
                                    val.innerHTML = "";
                                }
                            });
                        }
                    },
                    zoomType: 'x',
                    type: config.type
                },
                title: {
                    // text: config.name
                    text: ""
                },
                legend:{
                    itemDistance : 15,
                    itemMarginBottom : 5,
                    borderColor : "#FFF",
                    borderWidth : "1",
                    borderRadius : "8",
                    itemStyle: {
                        color: '#FFF',
                        fontSize : '12px'
                    }
                },
                tooltip: {
                    headerFormat: '{point.x:%e/%m/%Y (%b)  %l:%M %p}<br>',
                    pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b><br/>',
                    shared: true,
                    crosshairs: true,
                    useHTML: true,
                    valueSuffix: config.valuesuffix
                },
                xAxis: {
                    title: {
                        text: "time"
                    },
                    type: 'datetime',
                    minRange: 3600000,
                    dateTimeLabelFormats: {
                        millisecond: '%H:%M:%S.%L',
                        second: '%H:%M:%S',
                        minute: '%H:%M',
                        hour: '%H:%M',
                        day: '%e. %b',
                        week: '%e. %b',
                        month: '%b \'%y',
                        year: '%Y'
                    }
                },
                yAxis: {
                    title : {
                        text : config.valuetext
                    },
                    reversed : is_y_inverted
                },
                series: config.chart_data
            });
        }

        function addPointsToHighChart(pointArray) {
            var highChartSeries = $('#' + service_id + '_chart').highcharts().series;
            for (var i = 0; i < highChartSeries.length; i++) {
                for (var j = 0; j < pointArray[i].data.length; j++) {
                    $('#' + service_id + '_chart').highcharts().series[i].addPoint(pointArray[i].data[j], false, false, false);
                }
            }
        }

        function createDataTableForChart(table_id, headers) {
            var excel_columns = [];
            var data_in_table = "<table id='" + table_id + "' class='datatable table table-striped table-bordered table-hover table-responsive'><thead><tr>";
            /*Make table headers*/
            for (var i = 0; i < headers.length; i++) {
                data_in_table += '<td colspan="2" align="center"><b>' + headers[i].name + '</b></td>';
                excel_columns.push(i);
                if(headers.length <= i+1) {
                    excel_columns.push(i+1);
                }

            }
            data_in_table += '</tr><tr>';

            for (var i = 0; i < headers.length; i++) {
                data_in_table += '<td><em>Time</em></td><td><em>Value</em></td>';
            }

            data_in_table += '</tr></thead></table>';
            /*Table header creation end*/

            $('#' + service_id + '_bottom_table').html(data_in_table);

            $("#" + table_id).DataTable({
                sDom: 'T<"clear">lfrtip',
                oTableTools: {
                    sSwfPath: base_url + "/static/js/datatables/extras/TableTools/media/swf/copy_csv_xls.swf",
                    aButtons: [
                        {
                            sExtends: "xls",
                            sButtonText: "Download Excel",
                            sFileName: "*.xls",
                            mColumns: excel_columns
                        }
                    ]
                },
                bPaginate: true,
                bDestroy: true,
                aaSorting : [[0,'desc']],
                sPaginationType: "full_numbers"
            });
        }

        function addDataToDataTableForChart(table_obj, table_id) {
            var data = table_obj[0].data,
                total_columns = table_obj.length * 2;

            for (var i = 0; i < data.length; i++) {
                var row_val = [];
                for (var j = 0; j < table_obj.length; j++) {
                    var inner_data = table_obj[j].data[i];

                    if(inner_data) {
                        if(inner_data.constructor == Array) {
                            if(inner_data[0]) {
                                row_val.push(new Date(inner_data[0]).toLocaleString());
                                var chart_val = inner_data[1];
                                row_val.push(chart_val);
                            }
                        } else if(inner_data.constructor == Object) {
                            if(inner_data.x) {
                                row_val.push(new Date(inner_data.x).toLocaleString());
                                var chart_val = inner_data.y;
                                row_val.push(chart_val);
                            }
                        }
                    }
                }
                // If row are less than total columns then add blank fields
                if(row_val.length < total_columns) {
                    var val_diff = total_columns - row_val.length;
                    for(var x=0;x<val_diff;x++) {
                        row_val.push(" ");
                    }
                    $('#' + table_id).dataTable().fnAddData(row_val);
                } else {
                    $('#' + table_id).dataTable().fnAddData(row_val);
                }
            }
        }

        function createDataTable(table_id, headers) {

            var table_string = "",
                grid_headers = headers,
                excel_columns = [];

            table_string += '<table id="' + table_id + '" class="datatable table table-striped table-bordered table-hover table-responsive"><thead>';
            /*Table header creation start*/
            for (var i = 0; i < grid_headers.length; i++) {
                table_string += '<td><b>' + grid_headers[i].toUpperCase() + '</b></td>';
                excel_columns.push(i);
            }
            table_string += '</thead></table>';
            /*Table header creation end*/

            $('#' + service_id + '_chart').html(table_string);

            $("#" + table_id).DataTable({
                sDom: 'T<"clear">lfrtip',
                oTableTools: {
                    sSwfPath: base_url + "/static/js/datatables/extras/TableTools/media/swf/copy_csv_xls.swf",
                    aButtons: [
                        {
                            sExtends: "xls",
                            sButtonText: "Download Excel",
                            sFileName: "*.xls",
                            mColumns: excel_columns
                        }
                    ]
                },
                bPaginate: true,
                bDestroy: true,
                aaSorting : [[0,'desc']],
                sPaginationType: "full_numbers"
            });
        }

        function addDataToDataTable(table_data, table_headers, table_id) {
            for (var j = 0; j < table_data.length; j++) {
                var row_val = [];
                for (var i = 0; i < table_headers.length; i++) {
                    var insert_val = table_data[j][table_headers[i]] ? table_data[j][table_headers[i]] : "";
                    row_val.push(insert_val);
                }
                $('#' + table_id).dataTable().fnAddData(row_val);
            }
        }

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
                        if (result.data.objects.table_data_header && result.data.objects.table_data_header.length > 0) {
                            if ($("#other_perf_table").length == 0) {
                                createDataTable('other_perf_table', result.data.objects.table_data_header);
                            }
                            addDataToDataTable(result.data.objects.table_data, result.data.objects.table_data_header, 'other_perf_table');
                        } else {
                            // If any data available then plot chart & table
                            if(result.data.objects.chart_data.length > 0) {
                                if (chart_instance == "") {
                                    createHighChart(result.data.objects);
                                    createDataTableForChart("perf_data_table", result.data.objects.chart_data);
                                } else {
                                    addPointsToHighChart(result.data.objects.chart_data);
                                }
                                if ($("#perf_data_table").length > 0) {
                                    addDataToDataTableForChart(result.data.objects.chart_data, 'perf_data_table')
                                }
                            }
                        }
                    }

                    //check condition if start date and end date is defined.
                    if($.trim(ajax_start_date) && $.trim(ajax_end_date)) {

                        //if last date
                        if(moment(ajax_start_date).date() == moment(ajax_end_date).date() && moment(ajax_start_date).dayOfYear() == moment(ajax_end_date).dayOfYear()) {


                            if ($('#' + service_id + '_chart').highcharts()) {
                                $('#' + service_id + '_chart').highcharts().redraw();
                            }
                            if (chart_instance == "" && $("#other_perf_table").length == 0) {
                                $('#' + service_id + '_chart').html(result.message);
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