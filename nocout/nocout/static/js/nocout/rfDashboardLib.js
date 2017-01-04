/**
 * This file contains the script to populate charts on RF performance dashboards
 * @uses Highcharts
 * @class rfDashboardLib
 */

var base_url = "",
    create_chunks = [],
    total_calls_count = 0;

/*Set the base url of application for ajax calls*/
if(window.location.origin) {
    base_url = window.location.origin;
} else {
    base_url = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
}

/**
 * This function initiates RF performance dashboard
 * @method initRfDashboard
 */
function initRfDashboard() {

    if(ds_list && ds_list.length > 0 && ajax_url) {
        create_chunks = createArrayChunks(ds_list, chunk_size);
        startNextChunkCall(0);
    } else {
        /*hide spinner*/
        hideSpinner();
    }

    try {
        if(show_rf_perf_column){
            var col_no = 12/Number(show_rf_perf_column);
            if (col_no == 2) {
                $(".tab-rf-perf .box-container:even-child").after( "<div class='clearfix'></div><hr style='margin-top:0px;width:100%;'/>" );
                $(".tab-rf-perf .box-container:even-child .custom_seperator").hide();            
            } else {
                $(".tab-rf-perf .box-container:nth-child("+col_no+"n)").after( "<div class='clearfix'></div><hr style='margin-top:0px;width:100%;'/>" );
                $(".tab-rf-perf .box-container:nth-child("+col_no+"n) .custom_seperator").hide();            
            }
        }
    } catch(e) {
        // console.error(e);
    }
}


/**
 * This function call function to make ajax call as per the given param
 * @method startNextChunkCall
 * @param counter {Number}
 */
function startNextChunkCall(counter) {
    var current_chunk = JSON.parse(JSON.stringify(create_chunks[counter]));

    while(current_chunk && current_chunk.length > 0) {
        var ds_name = current_chunk.splice(0,1)[0];
        if(ds_name) {
            //Call waitAndSend function with BS Json Data and counter value
            rf_getChartData(ds_name, counter);
        }
    }
}


/**
 * This function fetch chart data by making an ajax call & create pie chart.
 * @method rf_getChartData
 */
function rf_getChartData(ds_name, chunk_counter) {
    
    if(ds_name) {

        var data_source_title = ds_name ? ds_name.toUpperCase() : "",
            get_param = "?data_source=" + ds_name,
            tab_title = window.location.href.split("rf-performance/")[1].split("/")[0].toUpperCase();

            // Adding extra flag in case if request is from rad5 page
            if (ajax_url.indexOf('radwin5k') > -1){
                get_param += '&is_rad5=1'
            }

        $.ajax({
            url : base_url+""+ajax_url+""+get_param,
            type : "GET",
            success : function(result) {
                var response = "";
                if(typeof result == 'string') {
                    response = JSON.parse(result);
                } else {
                    response = result;
                }

                if(response.success == 1) {

                    var timestamp = response.data.objects.timestamp ? response.data.objects.timestamp : "";

                    if(timestamp) {
                        // console.log($("#"+ds_name+"_timestamp").length);
                        if($("#"+ds_name+"_timestamp").length > 0) {
                            var timestamp_html = '<small>'+timestamp+'</small>';
                            $("#"+ds_name+"_timestamp").html(timestamp_html);
                        }
                    } else {
                        if($("#"+ds_name+"_timestamp").length > 0) {
                            $("#"+ds_name+"_timestamp").html("");
                        }
                    }

                    var pie_chart = $('#' + ds_name).highcharts({
                        chart: {
                            plotBackgroundColor: null,
                            plotBorderWidth: null,
                            plotShadow: false
                        },
                        credits: {
                            enabled: false
                        },
                        title: {
                            // text: response.data.objects.chart_data[0].name
                            text: ''
                        },
                        plotOptions: {
                            pie: {
                                allowPointSelect: true,
                                cursor: 'pointer',
                                dataLabels: {
                                    enabled: false
                                },
                                showInLegend: true,
                                size: "60%"
                            }
                        },
                        legend:{
                            itemDistance : 15,
                            itemMarginBottom : 5,
                            itemWidth : 125,
                            borderColor : "#CCCCCC",
                            borderWidth : "1",
                            borderRadius : "8",
                            itemStyle: {
                                color: '#555555',
                                fontSize : '10px'
                            }
                        },
                        tooltip: {
                            formatter: function () {
                                var point_name = this.point.name ? this.point.name : "",
                                    series_name = this.point.series.name ? this.point.series.name : "",
                                    percent_val = this.point.percentage ? this.point.percentage : "",
                                    tooltip_html = "";

                                point_name = point_name.split(":")[0];

                                if(percent_val) {
                                    percent_val = percent_val.toFixed(2);
                                }

                                tooltip_html ='<ul>\
                                            <li>'+point_name+'</li><br/>\
                                            <li>Value: <b>'+this.point.y+'</b><br/></li><br/>';
                                if(percent_val) {
                                    tooltip_html += '<li>Percentage: <b>'+percent_val+'%</b><br/></li>';
                                }
                                tooltip_html += '</ul>';

                                return tooltip_html;
                            }
                        },
                        colors: response.data.objects.colors,
                        series: [{
                            type: 'pie',
                            name: response.data.objects.display_name,
                            data: response.data.objects.chart_data[0].data
                        }]
                    });
                } else {
                    $.gritter.add({
                        // (string | mandatory) the heading of the notification
                        title: 'RF Performance Dashboard - '+tab_title,
                        // (string | mandatory) the text inside the notification
                        text: data_source_title + " : " + response.message,
                        // (bool | optional) if you want it to fade out on its own or just sit there
                        sticky: false,
                        // Time in ms after which the gritter will dissappear.
                        time : 1500
                    });
                }
            },
            error : function(err) {
                $.gritter.add({
                    // (string | mandatory) the heading of the notification
                    title: 'RF Performance Dashboard - '+tab_title,
                    // (string | mandatory) the text inside the notification
                    text: data_source_title + " : " + err.statusText,
                    // (bool | optional) if you want it to fade out on its own or just sit there
                    sticky: false,
                    // Time in ms after which the gritter will dissappear.
                    time : 1500
                });
            },
            complete : function() {

                total_calls_count++;
                if(total_calls_count >= chunk_size || create_chunks[chunk_counter].length < chunk_size) {
                    // Reset Calls Completed Counter
                    chunk_counter++;
                    total_calls_count = 0;
                    if(create_chunks[chunk_counter]) {
                        //Send Request for the next counter
                        startNextChunkCall(chunk_counter);
                    } else {
                        hideSpinner();
                    }
                }
            }
        });
    }
}

/**
 * This function creates chunks of given array as per given chunk size
 * @method createArrayChunks
 * @param data_array {Array}, It is the items array
 * @param chunk_size {Number}, It is the size of chunks to be created
 */
function createArrayChunks(data_array, chunk_size) {

    var chunks_array = [];
    
    var non_null_array = convertChunksToNormalArray(data_array);

    if(non_null_array && non_null_array.length > 0) {
        while (non_null_array.length > 0) {
            chunks_array.push(non_null_array.splice(0, chunk_size));
        }
    }

    return chunks_array;
}

/**
 * This function creates non null normal array from given chunks or normal array
 * @method convertChunksToNormalArray
 * @param data_array {Array}, It is the items chunks array
 * @param chunk_size {Number}, It is the size of chunks to be created
 */
function convertChunksToNormalArray(chunks_array) {
    var simple_array = chunks_array.join(',').split(','),
        non_null_array = [];

    for(var i=0;i<simple_array.length;i++) {
        if(simple_array[i] && non_null_array.indexOf(simple_array[i]) == -1)  {
            non_null_array.push(simple_array[i]);
        }
    }

    return non_null_array;
}

/**
 * This event trigger when any trends icon is clicked
 * @event click
 */
$(".tab-content i").click(function(e) {
    
    // show the loader
    showSpinner();

    var trends_id = e.currentTarget.id ? $.trim(e.currentTarget.id) : "",
        ds_name = trends_id ? e.currentTarget.id.split("_trend")[0] : "";

    if(ds_name && trends_ajax_url) {
        var get_params = "dashboard_name="+ds_name+"&is_bh="+is_bh+"&technology="+tech_name;

        // Adding extra flag in case if request is from rad5 page
        if (is_rad5){
            get_params += '&is_rad5=1'
        }
        $.ajax({
            url : base_url+""+trends_ajax_url+"?"+get_params,
            type : "GET",
            success : function(result) {
                var response = "";
                if(typeof result == 'string') {
                    response = JSON.parse(result);
                } else {
                    response = result;
                }

                if(response.success == 1) {
                    var useful_data = response.data.objects,
                        condition = useful_data && useful_data.chart_data && useful_data.chart_data.length > 0;

                    if(condition) {

                        var popup_html = "";

                        popup_html += "<div class='trends_chart_container' align='center' style='position:relative;overflow:auto;'>";
                        popup_html += "<div id='trends_chart' style='position:relative;width:100%;'></div>";
                        popup_html += "<div class='clearfix'></div>";
                        popup_html += "</div>";

                        /*Call the bootbox to show the popup with datatable*/
                        bootbox.dialog({
                            message: popup_html,
                            title: '<i class="fa fa-line-chart">&nbsp;</i> '+ds_name.toUpperCase()+' Trends'
                        });


                        // Update Modal width to 90%;
                        $(".modal-dialog").css("width","90%");
                        
                        // Create Chart
                        createHighChart_nocout(useful_data,'trends','#333333', false, function(status) {
                            // 
                        });

                        try {
                            setTimeout(function() {
                                // Resize the window to show highchart in proper bounds
                                $(window).resize();
                            },100)
                        } catch(e) {
                            // Pass
                        }
                    }
                } else {
                    $.gritter.add({
                        title: ds_name.toUpperCase()+' Trends',
                        text: response.message,
                        sticky: false,
                        time : 1000
                    });
                }
            },
            error : function(err) {
                console.log(err.statusText);
            },
            complete : function() {
                // hide the loader
                hideSpinner();
            }
        });
    }
});