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
}

function startNextChunkCall(counter) {
    var current_chunk = JSON.parse(JSON.stringify(create_chunks[counter]));

    while(current_chunk && current_chunk.length > 0) {
        var ds_name = current_chunk.splice(0,1)[0];
        if(ds_name) {
            //Call waitAndSend function with BS Json Data and counter value
            rf_getChartData(ds_name,counter);
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
                                showInLegend: true
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