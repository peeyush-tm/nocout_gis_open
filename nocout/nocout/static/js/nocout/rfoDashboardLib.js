/**
 * This file contains the script to load RFO dashboard data & also maintain the filters
 * @for RFO Dashboard
 * @uses jQuery, Highcharts
 */


/**
 * This event trigger when any filter control selectbox value changed
 * @event Change
 */
$('.filter_controls').change(function(e) {
    
    // When state select then show cities of that state only
    if ($(this).attr('name').indexOf('state') > -1) {
        var selected_val = $(this).val();
        $('select[name="city_selector"] option').show();
        if (selected_val) {
            $('select[name="city_selector"]').val('');
            $('select[name="city_selector"] option:not([parent_id="'+selected_val+'"])').hide();
            $('select[parent_id="'+selected_val+'"] option').show();
        }
    }

    initRfoDashboard();
});

/**
 * This function updates given filter selectbox values as per given data
 * @method updateFiltersContent
 * @param dataset {Array}, It contains the data which has to be populate in respective selectbox
 * @param filter_name {String}, It contains the prefix name(unique) of selectbox
 * @param filter_title {String}, It contains the filter title which shown in blank value of selectbox
 */
function updateFiltersContent(dataset, filter_name, filter_title) {
    var selector_id = 'select[name="' + filter_name + '_selector"]';
    if ($(selector_id).length) {
        
        var selectbox_html = '<option value="">Select '+filter_title+'</option>';
        if (filter_name == 'month') {
            var selectbox_html = '';
        }

        for (var i=0; i<dataset.length; i++) {
            if (filter_name == 'month') {
                try {
                    var id = dataset[i]['id'],
                        timestamp_obj = new Date(Number(id));

                    var value = month_dict[timestamp_obj.getMonth()] + ' - ' + timestamp_obj.getFullYear(),
                        selected_item = '';
                    
                    if (i == dataset.length - 1) {
                        selected_item = 'SELECTED="SELECTED"';
                    }

                    selectbox_html += '<option value="' + id + '" ' + selected_item + '>' + value + '</option>';
                } catch(e) {
                    // console.error(e);
                }
            } else {
                var parent_id = '';
                if (filter_name == 'city') {
                    parent_id = dataset[i]['state_id'];
                }
                try {
                    selectbox_html += '<option parent_id="' + parent_id + '" value="' + dataset[i]['id'] + '">' + dataset[i]['value'] + '</option>';
                } catch(e) {
                    // console.error(e);
                }
            }
        }

        $(selector_id).html(selectbox_html);
    }
}

function initRfoDashboard() {
    var display_type = $('select[name="display_selector"]').val(),
        selected_month = $('select[name="month_selector"]').val(),
        selected_state = $('select[name="state_selector"]').val(),
        selected_city = $('select[name="city_selector"]').val(),
        load_table = true,
        load_chart = false;

    if (selected_month) {
        selected_month = Number(selected_month) / 1000;
    }

    if (display_type == 'both') {
        load_chart = true;
        load_table = true;
        if ($('.chart_view_container').hasClass('hide')) {
            $('.chart_view_container').removeClass('hide');
        }
        if ($('.both_view_seperator').hasClass('hide')) {
            $('.both_view_seperator').removeClass('hide');
        }
        if ($('.table_view_container').hasClass('hide')) {
            $('.table_view_container').removeClass('hide');
        }

    } else if (display_type == 'chart') {
        load_chart = true;
        load_table = false;
        if ($('.chart_view_container').hasClass('hide')) {
            $('.chart_view_container').removeClass('hide');
        }
        if (!$('.both_view_seperator').hasClass('hide')) {
            $('.both_view_seperator').addClass('hide');
        }
        if (!$('.table_view_container').hasClass('hide')) {
            $('.table_view_container').addClass('hide');
        }
    } else {
        load_chart = false;
        load_table = true;
        if (!$('.chart_view_container').hasClass('hide')) {
            $('.chart_view_container').addClass('hide');
        }
        if (!$('.both_view_seperator').hasClass('hide')) {
            $('.both_view_seperator').addClass('hide');
        }
        if ($('.table_view_container').hasClass('hide')) {
            $('.table_view_container').removeClass('hide');
        }
    }

    if (load_table) {
        // Load All data datatables
        dataTableInstance.createDataTable(
            'rfo_data_table',
            all_data_headers,
            all_data_url + '?month=' + String(selected_month)+'&state_name=' + selected_state + '&city_name='+ selected_city,
            false
        );

        // Load Summation data datatables
        dataTableInstance.createDataTable(
            'rfo_summation_table',
            summation_headers,
            summation_url + '?month=' + String(selected_month)+'&state_name=' + selected_state + '&city_name='+ selected_city,
            false
        );
    }

    if (load_chart) {
        loadRFOChart(summation_url,String(selected_month), selected_state, selected_city);
    }

    // Hide Loading Spinner
    hideSpinner();
}

function loadRFOChart(ajax_url, month, selected_state, selected_city) {

    $.ajax({
        url: ajax_url + '?month='+month+'&request_for_chart=1&state_name=' + selected_state + '&city_name='+ selected_city,
        type: 'GET',
        success: function(response) {

            if (typeof(response) == 'string') {
                response = JSON.parse(response);
            }

            if (response['result'] == 'ok') {
                var current_dateobj = new Date(Number(month) * 1000),
                    month_txt = month_dict[current_dateobj.getMonth()],
                    year_txt = current_dateobj.getFullYear(),
                    year_month_str = month_txt && year_txt ? month_txt + ' ' + year_txt : '';
                var column_series_data = [],
                    categories = [];

                for (var i=0;i<response['aaData'].length;i++) {
                    categories.push(response['aaData'][i]['master_causecode'])
                    column_series_data.push({
                        'name': response['aaData'][i]['master_causecode'],
                        'type': 'column',
                        'data': [response['aaData'][i]['outage_in_minutes']]
                    })
                }

                $('#rfo_column_chart_container').highcharts({
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: 'PB TT RFO Analysis ' + year_month_str,
                        align: 'left'
                    },
                    xAxis: {
                        // categories: categories,
                        title: {
                            text: 'Master Cause Code'
                        }
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'Outage In Minutes'
                        },
                        labels: {
                            overflow: 'justify'
                        }
                    },
                    legend: {
                        itemDistance : 15,
                        itemMarginBottom : 5,
                        borderColor : "#CCCCCC",
                        borderWidth : "1",
                        borderRadius : "8",
                        itemStyle: {
                            color: '#555555',
                            fontSize : '10px'
                        },
                        layout: 'vertical',
                        align: 'right',
                        verticalAlign: 'top'
                        // width : "100%"
                    },
                    credits: {
                        enabled: false
                    },
                    plotOptions: {
                        column: {
                            pointWidth: 12,
                            groupPadding: 0
                        },
                        series: {
                            point: {
                                events: {
                                    click: function(e) {
                                        // Show Loading Spinner
                                        showSpinner();

                                        var series_name = this.series.name,
                                            series_value = this.y;
                                        
                                        // Fetch clicked point sub cause code data
                                        var sub_data_url = '';
                                        sub_data_url += all_data_url;
                                        sub_data_url += '?month='+month;
                                        sub_data_url += '&request_for_chart=1&search[value]='+series_name;
                                        sub_data_url += '&state_name=' + selected_state;
                                        sub_data_url += '&city_name='+ selected_city

                                        createFaultPieChart(sub_data_url, series_name);
                                    }
                                }
                            }
                        }
                    },
                    series: column_series_data,
                    noData: {
                        style: {
                            fontWeight: 'bold',
                            fontSize: '20px',
                            color: '#539fb8',
                        }
                    }
                });
            }
        },
        error: function(err) {
            console.log(err.statusText);
        }
    });
}

function createFaultPieChart(sub_data_url, series_name) {

    $.ajax({
        url: sub_data_url,
        type: 'GET',
        success: function(all_data_response) {
            if (typeof(all_data_response) == 'string') {
                all_data_response = JSON.parse(all_data_response);
            }

            if (all_data_response['result'] == 'ok') {
                var pie_chart_data = [],
                    pie_dict = {},
                    names_list = [];
                for(var j=0; j<all_data_response['aaData'].length; j++) {
                    var sub_causecode = all_data_response['aaData'][j]['sub_causecode'] ? all_data_response['aaData'][j]['sub_causecode'] : 'NA',
                        outage_time = all_data_response['aaData'][j]['outage_in_minutes'] ? parseFloat(all_data_response['aaData'][j]['outage_in_minutes']) : 0;

                    if (names_list.indexOf(sub_causecode) == -1) {
                        pie_dict[sub_causecode] = 0;
                        names_list.push(sub_causecode);
                    }

                    pie_dict[sub_causecode] += outage_time;
                }
                
                for(var key in pie_dict) {
                    if (pie_dict.hasOwnProperty(key)) {
                        pie_chart_data.push([key, pie_dict[key]])
                    }
                }

                var bootbox_html = '';

                bootbox_html += '<div class="pie_chart_container" align="center">\
                                    <div id="fault_pie_chart"></div>\
                                </div>';

                bootbox.dialog({
                    message: bootbox_html,
                    title: '<i class="fa fa-bar-chart">&nbsp;</i> Fault Segment - '+series_name
                });

                // Update Modal width to 90%;
                $(".modal-dialog").css("width","90%");

                $('#fault_pie_chart').highcharts({
                    chart: {
                        type: 'pie'
                    },
                    title: {
                        text: '',
                        align: 'left'
                    },
                    xAxis: {
                        // categories: categories,
                        title: {
                            text: 'Sub Cause Code'
                        }
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'Outage In Minutes'
                        },
                        labels: {
                            overflow: 'justify'
                        }
                    },
                    legend: {
                        itemDistance : 15,
                        itemMarginBottom : 5,
                        borderColor : "#CCCCCC",
                        borderWidth : "1",
                        borderRadius : "8",
                        itemStyle: {
                            color: '#555555',
                            fontSize : '10px'
                        },
                        layout: 'vertical',
                        align: 'right',
                        verticalAlign: 'top'
                        // width : "100%"
                    },
                    credits: {
                        enabled: false
                    },
                    series: [{
                        data: pie_chart_data,
                        name: series_name,
                        title: series_name
                    }],
                    noData: {
                        style: {
                            fontWeight: 'bold',
                            fontSize: '20px',
                            color: '#539fb8',
                        }
                    }
                });
                
                // Hide Loading Spinner
                hideSpinner();
            }
        },
        error: function(err) {
            // console.log(err.statusText);
            // Hide Loading Spinner
            hideSpinner();
        }
    });
}