/**
 * This file contain the global reusable function for nocout platform
 * @for nocoutUtilsLib
 */


// Global Variables
var green_color = "#468847",
    orange_color = "#f0ad4e",
    red_color = "#b94a48",
    green_status_array = ['ok','success','up'],
    red_status_array = ['critical'],
    down_status_array = ['down'],
    orange_status_array = ['warning'],
    left_block_style = "border:1px solid #CCC;border-right:0px;padding: 3px 5px;background:#FFF;",
    right_block_style = "border:1px solid #CCC;padding: 3px 5px;background:#FFF;";


/**
 * This function is used to populate the latest status info for any device as per given params
 * @method populateDeviceStatus_nocout
 * @param domElement {String}, It contains the dom element ID on which the info is to be populated
 * @param info {Object}, It contains the latest status info object
 */
function populateDeviceStatus_nocout(domElement,info) {

    var fa_icon_class = "fa-circle",
        txt_color = "",
        status_html = "",
        age = info.age ? info.age : "Unknown",
        lastDownTime = info.last_down_time ? info.last_down_time : "Unknown",
        status = info.status ? info.status.toUpperCase() : "Unknown";

    if(green_status_array.indexOf($.trim(status.toLowerCase()))  > -1) {
        txt_color = green_color;
        fa_icon_class = "fa-check-circle";
    } else if(red_status_array.indexOf($.trim(status.toLowerCase()))  > -1) {
        txt_color = red_color;
        fa_icon_class = "fa-times-circle";
    } else if(orange_status_array.indexOf($.trim(status.toLowerCase()))  > -1) {
        txt_color = orange_color;
        fa_icon_class = "fa-warning";
    } else if(down_status_array.indexOf($.trim(status.toLowerCase()))  > -1) {
        txt_color = red_color;
        fa_icon_class = "fa-warning";
    } else {
        // pass
    }

    status_html = "";

    status_html += '<table id="final_status_table" class="table table-responsive table-bordered" style="background:#FFFFFF;"><tr>';
    status_html += '<td style="color:'+txt_color+';"><i title = "'+status+'" class="fa '+fa_icon_class+'" style="vertical-align: middle;"> </i> <b>Current Status</b> : '+status+'</td>';
    status_html += '<td style="color:'+txt_color+';"><b>Current Status Since</b> : '+age+'</td>';
    status_html += '<td style="color:'+txt_color+';"><b>Last Down Time</b> : '+lastDownTime+'</td>';
    status_html += '</tr></table>';

    // Update Status Block HTML as per the device status
    $("#"+domElement).html(status_html);
}

/**
 * This function is used to populate the latest status for any service as per given params
 * @method populateServiceStatus_nocout
 * @param domElement {String}, It contains the dom element ID on which the info is to be populated
 * @param info {Object}, It contains the latest status object
 */
function populateServiceStatus_nocout(domElement,info) {

    if($.trim(info.last_updated) != "" || $.trim(info.perf) != "") {
        var last_updated = info.last_updated ? info.last_updated : "N/A",
            perf = info.perf ? info.perf : "N/A",
            inner_status_html = '';
        
        inner_status_html += '<table id="perf_output_table" class="table table-responsive table-bordered" style="background:#F5F5F5;">';
        inner_status_html += '<tr>';
        inner_status_html += '<td><b>Latest Performance Output</b> : '+perf+'</td>';
        inner_status_html += '<td><b>Last Updated At</b> : '+last_updated+'</td>';
        inner_status_html += '</tr>';
        inner_status_html += '</table><div class="clearfix"></div><div class="divide-20"></div>';
        $("#"+domElement).html(inner_status_html);
    } else {
        $("#"+domElement).html("");
    }
}


/**
 * This function adds data to initialized datatable as per given params
 * @method addDataToNormalTable_nocout
 * @param table_data {Array}, It contains the data object array for table
 * @param table_headers {Array}, It contains the headers object array for table
 * @param table_id {String}, It contains the table dom element ID
 */
function addDataToNormalTable_nocout(table_data, table_headers, table_id) {

    for (var j = 0; j < table_data.length; j++) {
        var row_val = [];
        for (var i = 0; i < table_headers.length; i++) {
            var insert_val = table_data[j][table_headers[i]] ? table_data[j][table_headers[i]] : "";
            row_val.push(insert_val);
        }
        $('#' + table_id).dataTable().fnAddData(row_val);
    }
}

/**
 * This function creates blank data table as per given params
 * @method initNormalDataTable_nocout
 * @param table_id {String}, It contains the table dom element ID
 * @param headers {Array}, It contains the headers object array for table
 * @param service_id {String}, It contains the service dom id in which the table is to be populate.
 */
function initNormalDataTable_nocout(table_id, headers, service_id) {

    var table_string = "",
        grid_headers = headers,
        excel_columns = [];

    if($('#'+table_id).length > 0) {
        $("#"+table_id).dataTable().fnDestroy();
        $("#"+table_id).remove();
    }

    table_string += '<table id="' + table_id + '" class="datatable table table-striped table-bordered table-hover table-responsive"><thead>';
    /*Table header creation start*/
    for (var i = 0; i < grid_headers.length; i++) {
        table_string += '<td><b>' + grid_headers[i].toUpperCase() + '</b></td>';
        excel_columns.push(i);
    }
    table_string += '</thead></table>';
    /*Table header creation end*/


    if(service_id) {
        $('#'+service_id+'_chart').html(table_string);
    }

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

/**
 * This function creates blank data table for chart data as per given params
 * @method initChartDataTable_nocout
 * @param table_id {String}, It contains the table dom element ID
 * @param headers {Array}, It contains the headers object array for table
 * @param service_id {String}, It contains the service dom id in which the table is to be populate.
 */
function initChartDataTable_nocout(table_id, headers, service_id) {

    var excel_columns = [];

    if($('#'+table_id).length > 0) {
        $("#"+table_id).dataTable().fnDestroy();
        $("#"+table_id).remove();
    }

    var data_in_table = "<table id='"+table_id+"' class='datatable table table-striped table-bordered table-hover table-responsive'><thead><tr>";
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
    if(service_id) {
        $('#'+service_id+'_bottom_table').html(data_in_table);
    }

    $("#"+table_id).DataTable({
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

/**
 * This function adds data to initialized datatable as per given params
 * @method addDataToChartTable_nocout
 * @param table_obj {Array}, It contains the chart data object array
 * @param table_id {String}, It contains the table dom element ID
 */
function addDataToChartTable_nocout(table_obj, table_id) {

    var data = table_obj[0].data,
        total_columns = table_obj.length * 2;

    for(var i = 0; i < data.length; i++) {
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
            $('#'+table_id).dataTable().fnAddData(row_val);
        } else {
            $('#'+table_id).dataTable().fnAddData(row_val);
        }
    }
}

/**
 * This function adds data to created highchart
 * @method addPointsToChart_nocout
 * @param pointArray {Array}, It contains the chart data object array
 * @param dom_id {String}, It contains the chart dom element ID
 */
function addPointsToChart_nocout(pointArray, dom_id) {

    var highChartSeries = $('#'+dom_id+'_chart').highcharts().series;

    for (var i = 0; i < highChartSeries.length; i++) {
        for (var j = 0; j < pointArray[i].data.length; j++) {
            $('#'+dom_id+'_chart').highcharts().series[i].addPoint(pointArray[i].data[j], false, false, false);
        }
    }
}

/**
 * This function creates highchart for device performance
 * @method createHighChart_nocout
 * @param chartConfig {Array}, It contains configuration & data to initialize highcharts
 * @param dom_id {String}, It contains the chart dom element ID
 */
function createHighChart_nocout(chartConfig,dom_id,text_color) {

    // Is the y axis should be reversed or not
    var is_y_inverted = chartConfig["is_inverted"] ? chartConfig["is_inverted"] : false,
        legends_color = text_color ? text_color : "#FFF";

    var chart_instance = $('#'+dom_id+'_chart').highcharts({
        chart: {
            zoomType: 'x',
            type: chartConfig.type
        },
        title: {
            // text: chartConfig.name
            text: ""
        },
        credits: {
            enabled: false
        },
        legend:{
            itemDistance : 15,
            itemMarginBottom : 5,
            borderColor : legends_color,
            borderWidth : "1",
            borderRadius : "8",
            itemStyle: {
                color: legends_color,
                fontSize : '12px'
            }
        },
        tooltip: {
            headerFormat: '{point.x:%e/%m/%Y (%b)  %l:%M %p}<br>',
            pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b><br/>',
            shared: true,
            crosshairs: true,
            useHTML: true,
            valueSuffix: chartConfig.valuesuffix
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
                text : chartConfig.valuetext
            },
            reversed : is_y_inverted
        },
        series: chartConfig.chart_data
    });
}

/**
 * This function creates & returns table structur(with data) html
 * @method createTableHtml_nocout
 * @param dom_id {String}, It contains the table dom element ID
 * @param table_headers {Array}, It contains the headers object array for table
 * @param table_data {Array}, It contains the data object array for table
 */
function createTableHtml_nocout(dom_id, table_headers, table_data) {

    var table_string = "",
        grid_headers = table_headers,
        table_id = dom_id ? dom_id : "table1";

    if($("#"+table_id).length > 0) {
        $("#"+table_id).dataTable().fnDestroy();
        $("#"+table_id).remove();
    }

    table_string += '<table id="' + table_id + '" class="datatable table table-striped table-bordered table-hover table-responsive"><thead>';
    /*Table header creation start*/
    for (var i = 0; i < grid_headers.length; i++) {
        table_string += '<td><b>' + grid_headers[i].toUpperCase() + '</b></td>';
    }

    table_string += '</thead><tbody>';
    /*Table header creation end*/

    /*Table data creation start*/
    for (var j = 0; j < table_data.length; j++) {
        table_string += '<tr>';
        for (var i = 0; i < grid_headers.length; i++) {
            table_string += '<td>'+table_data[j][grid_headers[i]]+'</td>';
        }
        table_string += '</tr>';
    }
    /*Table data creation End*/

    table_string += '</tbody></table>';

    // return tbale string
    return table_string;
}

/**
 * This function creates & returns table structur(with data) html
 * @method createTableHtml_nocout
 * @param dom_id {String}, It contains the table dom element ID.
 * @param chartObj {Array}, It contains the chart data info object array.
 */
function createChartDataTableHtml_nocout(dom_id, chartObj) {

    var table_id = dom_id ? dom_id : "table1";

    if($("#"+table_id).length > 0) {
        $("#"+table_id).dataTable().fnDestroy();
        $("#"+table_id).remove();
    }

    var data_in_table = "<table id='" + table_id + "' class='datatable table table-striped table-bordered table-hover table-responsive'><thead><tr>";

    /*Make table headers*/
    for (var i = 0; i < chartObj.length; i++) {
        data_in_table += '<td colspan="2" align="center"><b>' + chartObj[i].name + '</b></td>';
    }
    data_in_table += '</tr><tr>';

    for (var i = 0; i < chartObj.length; i++) {
        data_in_table += '<td><em>Time</em></td><td><em>Value</em></td>';
    }

    data_in_table += '</tr></thead><tbody>';
    /*Table header creation end*/

    var data = chartObj[0].data;

    for (var j = 0; j < data.length; j++) {
        data_in_table += '<tr>';
        for (var i = 0; i < chartObj.length; i++) {
            var inner_data = chartObj[i].data[j],
                time_val = "",
                val = "";
            if (inner_data instanceof Array) {
                time_val = new Date(inner_data[0]).toLocaleString();
                val = inner_data[1];
            } else {
                time_val = new Date(inner_data.x).toLocaleString();
                val = inner_data.y;
            }
            data_in_table += '<td>'+time_val+'</td><td>'+val+'</td>';
        }
        data_in_table += '</tr>';
    }

    data_in_table += '</tbody>';
    data_in_table += '</table>';

    return data_in_table;
}