/**
 * This file contains the script to load RFO dashboard data & also maintain the filters
 * @for RFO Dashboard
 * @uses jQuery, Highcharts
 */

var chart_colors_list = [
        '#7cb5ec', '#90ed7d', '#f7a35c', '#528969', '#A47D7C', 
        '#f15c80', '#e4d354', '#2b908f', '#f45b5b', '#91e8e1',
        '#2f7ed8', '#0d233a', '#8bbc21', '#910000', '#1aadce', 
        '#492970', '#f28f43', '#77a1e5', '#c42525', '#a6c96a',
        '#4572A7', '#AA4643', '#89A54E', '#80699B', '#e58e7c',
        '#DB843D', '#92A8CD', '#A47D7C', '#B5CA92', '#d69e9f',
        '#1c3066', '#0a3c5d', '#2f6494', '#2f70a6', '#2c5d8a',
        '#2a5a85', '#1f21f2', '#1f5a78', '#1d4263', '#1c3f5e',
        '#001fb7', '#0d31ff', '#0b2536', '#0000ff', '#f04f2d',
        '#36939e', '#9e466b', '#453e5b', '#ffceb4', '#3D96AE',
        '#23c5e3', '#c5e323', '#a8f2c3', '#6fd6a5', '#ffceb4',
        '#e1ac96', '#3c2e28', '#53856d', '#b24747', '#a5e79b',
        '#77e180', '#488864', '#8e92a2', '#ff0033', '#9bc7ae',
        '#ffdeed', '#b296a2'
    ],
    middle_legends = {
        itemDistance : 15,
        itemMarginBottom : 5,
        borderColor : "#CCCCCC",
        borderWidth : "1",
        borderRadius : "8",
        itemStyle: {
            color: '#555555',
            fontSize : '10px'
        }
    },
    side_legends = {
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
        verticalAlign: 'middle'
    },
    common_param = "'download_excel': 'yes'";

/**
 * This function initializes RFO dashboard. It calls function to poplates charts/tables.
 * @method initRfoDashboard
 */
function initRfoDashboard() {
    var display_type = $('select[name="display_selector"]').val(),
        selected_month = $('select[name="month_selector"]').val(),
        selected_state = $('select[name="state_selector"]').val(),
        selected_city = $('select[name="city_selector"]').val(),
        is_rfo_trend_page = window.location.pathname.indexOf('/rfo_trends/') > -1,
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

    var table_title = 'PB TT RFO Analysis',
        header_class = 'RFOAnalysisView',
        all_data_class = 'RFOAnalysisList',
        selected_severity = '',
        summation_data_class = 'RFOAnalysisSummationList',
        all_data_api_url = all_data_url + '?month=' + String(selected_month)+'&state_name=' + selected_state + '&city_name='+ selected_city,
        summation_api_url = summation_url + '?month=' + String(selected_month)+'&state_name=' + selected_state + '&city_name='+ selected_city;

    if (is_rfo_trend_page) {
        selected_severity = $('select[name="severity_selector"]').val();

        all_data_api_url += '&severity='+ selected_severity;
        summation_api_url += '&severity='+ selected_severity;

        table_title = 'RFO Trends';
        header_class = 'RFOTrendsView';
        all_data_class = 'RFOTrendsList';
        summation_data_class = 'RFOTrendsSummationList'
    }

    if (load_table) {
        // Load All data datatables
        dataTableInstance.createDataTable(
            'rfo_data_table',
            all_data_headers,
            all_data_api_url,
            false,
            table_title,
            'dashboard',
            header_class,
            all_data_class,
            "{'headers_data_key': 'all_data_headers', "+common_param+"}",
            "{'severity': '"+selected_severity+"', 'month': '"+selected_month+"', 'report_title': '"+table_title+"', 'state_name': '"+selected_state+"', 'city_name': '"+selected_city+"', "+common_param+"}"
        );

        // Load Summation data datatables
        dataTableInstance.createDataTable(
            'rfo_summation_table',
            summation_headers,
            summation_api_url,
            false,
            table_title,
            'dashboard',
            header_class,
            summation_data_class,
            "{'headers_data_key': 'summation_headers', "+common_param+"}",
            "{'severity': '"+selected_severity+"', 'month': '"+selected_month+"', 'report_title': '"+table_title+"', 'state_name': '"+selected_state+"', 'city_name': '"+selected_city+"', "+common_param+"}"
        );
    }

    if (load_chart) {
        if (is_rfo_trend_page) {
            loadRFOTrendsChart(summation_api_url, {
                'is_normal': true
            });
        } else {
            loadRFOColumnChart(summation_url,String(selected_month), selected_state, selected_city);
        }
    }
}

/**
 * This function initializes MTTR Summary dashboard. It calls function to poplates charts/tables.
 * @method initMTTRDashboard
 */
function initMTTRDashboard() {

    var selected_month = $('select[name="month_selector"]').val(),
        selected_state = $('select[name="state_selector"]').val(),
        selected_city = $('select[name="city_selector"]').val();

    if (selected_month) {
        selected_month = Number(selected_month) / 1000;
    }

    loadMTTRSummaryChart(mttr_summary_url,String(selected_month), selected_state, selected_city, {'is_normal': true});
}

/**
 * This function initializes INC Ticket dashboard. It calls function to poplates charts/tables.
 * @method initINCTicketDashboard
 */
function initINCTicketDashboard() {
    var display_type = $('select[name="display_selector"]').val(),
        selected_month = $('select[name="month_selector"]').val(),
        selected_severity = $('select[name="severity_selector"]').val(),
        selected_target = $('input[name="target_selector"]').val()
        load_table = true,
        load_chart = false;

    if (selected_month) {
        selected_month = Number(selected_month) / 1000;
    }

    if (!selected_target) {
        selected_target = 60;
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

    var api_get_params = '';
    api_get_params += '?month=' + String(selected_month);
    api_get_params += '&severity=' + selected_severity;
    api_get_params += '&current_target='+ selected_target;

    if (load_table) {
        // Load INC Ticket Rate Table
        dataTableInstance.createDataTable(
            'inc_ticket_datatable',
            inc_ticket_headers,
            inc_ticket_url + api_get_params,
            false,
            'INC Ticket Rate',
            'dashboard',
            'INCTicketRateInit',
            'INCTicketRateListing',
            "{'headers_data_key': 'inc_ticket_headers', "+common_param+"}",
            "{'month': '"+selected_month+"', 'report_title': 'INC Ticket Rate', 'severity': '"+selected_severity+"', 'current_target': '"+selected_target+"', "+common_param+"}"
        );
    }

    if (load_chart) {
        api_get_params += '&request_for_chart=1';
        selected_severity = selected_severity.split('_').join(' ');
        loadINCTicketChart(inc_ticket_url + api_get_params, selected_severity);
    }
}

/**
 * This function initializes Resolution Efficiency dashboard. It calls function to poplates charts/tables.
 * @method initResolutionEfficiencyDashboard
 */
function initResolutionEfficiencyDashboard() {
    var display_type = $('select[name="display_selector"]').val(),
        selected_month = $('select[name="month_selector"]').val(),
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

    var api_get_params = '';
    api_get_params += '?month=' + String(selected_month);

    if (load_table) {
        // Load INC Ticket Rate Table
        dataTableInstance.createDataTable(
            'resolution_efficiency_datatable',
            resolution_efficiency_headers,
            resolution_efficiency_url + api_get_params,
            false,
            'Resolution Efficiency',
            'dashboard',
            'ResolutionEfficiencyInit',
            'ResolutionEfficiencyListing',
            "{'headers_data_key': 'resolution_efficiency_headers', "+common_param+"}",
            "{'month': '"+selected_month+"', 'report_title': 'Resolution Efficiency', "+common_param+"}"
        );
    }

    if (load_chart) {
        api_get_params += '&request_for_chart=1';
        loadResolutionEfficienyChart(resolution_efficiency_url + api_get_params);
    }
}

/**
 * This function initializes Sector/Backhaul Status dashboard. It calls function to poplates charts/tables.
 * @method initCapacitySummaryDashboard
 */
function initCapacitySummaryDashboard() {
    var display_type = $('select[name="display_selector"]').val(),
        selected_month = $('select[name="month_selector"]').val(),
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

    var api_get_params = '';
    api_get_params += '?month=' + String(selected_month);

    var selected_tech = $('.nav-tabs li.active a').attr('tech'),
        table_id_prefix = $('.nav-tabs li.active a').attr('table-id-prefix');
    
    // Append technology query string as per the selected tab.
    api_get_params += '&technology=' + selected_tech;


    if (load_table) {
        var tab_txt = $.trim($('.nav-tabs li.active a').text()),
            table_title = 'Sector Summary Status - ' + tab_txt,
            headers_class = 'SectorStatusInit',
            data_class = 'SectorStatusListing';

        if (window.location.pathname.indexOf('/backhaul_status/') > -1) {
            table_title = 'Backhaul Summary Status - ' + tab_txt;
            headers_class = 'BackhaulStatusInit';
            data_class = 'BackhaulStatusListing';
        }

        // Load Sector/Backhaul summary report
        dataTableInstance.createDataTable(
            table_id_prefix+'_datatable',
            capacity_summary_headers,
            capacity_summary_url + api_get_params,
            false,
            table_title,
            'dashboard',
            headers_class,
            data_class,
            "{'headers_data_key': 'summary_headers', "+common_param+"}",
            "{'month': '"+selected_month+"', 'technology': '"+selected_tech+"', 'report_title': '"+table_title+"', "+common_param+"}"
        );
    }

    if (load_chart) {
        api_get_params += '&request_for_chart=1';
        var window_pathname = window.location.pathname,
            page_type = '';

        if (window_pathname.indexOf('/backhaul_status/') > -1) {
            page_type = 'backhaul';
        } else if (window_pathname.indexOf('/sector_status/') > -1) {
            page_type = 'sector';
        }

        loadCapacityAlertChart(capacity_summary_url + api_get_params, table_id_prefix, page_type)
    }
}

/**
 * This function initializes Network/PTP BH uptime dashboard. It calls function to poplates charts/tables.
 * @method initUptimeDashboard
 */
function initUptimeDashboard() {
    var display_type = $('select[name="display_selector"]').val(),
        selected_month = $('select[name="month_selector"]').val(),
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

    var api_get_params = '';
    api_get_params += '?month=' + String(selected_month);

    var selected_tech = $('.nav-tabs li.active a').attr('tech'),
        table_id_prefix = $('.nav-tabs li.active a').attr('table-id-prefix');

    if (window.location.pathname.indexOf('/ptpbh_uptime/') > -1) {
        selected_tech = '';
        table_id_prefix = 'ptp_bh_uptime';
    }
    
    // Append technology query string as per the selected tab.
    api_get_params += '&technology=' + selected_tech;

    if (load_table) {
        var tab_txt = $.trim($('.nav-tabs li.active a').text()),
            table_title = 'Network Uptime - ' + tab_txt,
            headers_class = 'NetworkUptimeInit',
            data_class = 'SectorStatusListing';

        if (window.location.pathname.indexOf('/ptpbh_uptime/') > -1) {
            table_title = 'PTP BH Uptime - ' + tab_txt;
            headers_class = 'PTPBHUptimeInit';
            data_class = 'BackhaulStatusListing';
        }
        // Load Sector/Backhaul summary report
        dataTableInstance.createDataTable(
            table_id_prefix+'_datatable',
            network_uptime_headers,
            network_uptime_url + api_get_params,
            false,
            table_title,
            'dashboard',
            headers_class,
            data_class,
            "{'headers_data_key': 'summary_headers', "+common_param+"}",
            "{'month': '"+selected_month+"', 'technology': '"+selected_tech+"', 'report_title': '"+table_title+"', "+common_param+"}"
        );
    }

    if (load_chart) {
        api_get_params += '&request_for_chart=1';
        var window_pathname = window.location.pathname,
            page_type = '';

        if (window_pathname.indexOf('/ptpbh_uptime/') > -1) {
            page_type = 'ptpbh';
        } else if (window_pathname.indexOf('/network_uptime/') > -1) {
            page_type = 'network';
        }

        loadUptimeChart(network_uptime_url + api_get_params, table_id_prefix, page_type)
    }
}

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
        var direct_values_filter = ['severity'];
        
        var selectbox_html = '<option value="">Select '+filter_title+'</option>',
            is_rfo_trend_page = window.location.pathname.indexOf('/rfo_trends/') > -1;

        if (direct_values_filter.indexOf(filter_name) > -1 && !is_rfo_trend_page) {
            var selectbox_html = '';
        }

        var is_inc_page = window.location.pathname.indexOf('/inc_ticket_rate/') == -1,
            is_re_page = window.location.pathname.indexOf('/resolution_efficiency/') == -1,
            is_uptime_page = window.location.pathname.indexOf('_uptime/') == -1;

        for (var i=0; i<dataset.length; i++) {
            if (filter_name == 'month') {
                try {
                    var id = dataset[i]['id'],
                        timestamp_obj = new Date(Number(id));

                    var value = month_dict[timestamp_obj.getMonth()] + ' - ' + timestamp_obj.getFullYear(),
                        selected_item = '';
                    if (is_re_page && is_inc_page && is_uptime_page) {
                        if (i == dataset.length - 1) {
                            selected_item = 'SELECTED="SELECTED"';
                        }
                    }

                    selectbox_html += '<option value="' + id + '" ' + selected_item + '>' + value + '</option>';
                } catch(e) {
                    // console.error(e);
                }
            } else {
                if (dataset[i]['value'] && dataset[i]['id']) {
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
        }

        $(selector_id).html(selectbox_html);
    }
}

/**
 * This function fetch data & loads master cause code column chart
 * @method loadRFOColumnChart
 * @param ajax_url {String}, If contains the API url to fetch master cause code data
 * @param month {Integer}, It contains epoch timestamp for selected month
 * @param selected_state {String}, If contains the selected state value(if any)
 * @param selected_city {String}, If contains the selected city value(if any)
 */
function loadRFOColumnChart(ajax_url, month, selected_state, selected_city) {

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
                var chart_title = 'PB TT RFO Analysis ' + year_month_str;
                // Initialize column chart for master cause code
                $('#rfo_column_chart_container').highcharts({
                    chart: {
                        type: 'column'
                    },
                    exporting:{
                        enabled : true,
                        allowHTML: true,
                        sourceWidth: 950,
                        sourceHeight: 375,
                        filename: chart_title
                    },
                    colors: chart_colors_list,
                    title: {
                        text: chart_title,
                        align: 'left'
                    },
                    xAxis: {
                        categories: [''],
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
                    tooltip: {
                        formatter: function () {
                            var series_name = this.series.name ? $.trim(this.series.name) : "Value",
                                tooltip_html = "";

                            tooltip_html += '<ul><li><b>Master Cause Code</b></li><br/>';
                            tooltip_html += '<li>'+series_name+' : '+this.point.y+'</li><br/></ul>';

                            return tooltip_html;
                        }
                    },
                    legend: {
                        itemDistance : 15,
                        itemMarginBottom : 5,
                        borderColor : "#CCCCCC",
                        borderWidth : "1",
                        borderRadius : "0",
                        x: -25,
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

                                        // Call "createFaultPieChart" to show pie chart in popup
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

            // hide loading spinner
            hideSpinner();
        },
        error: function(err) {
            // console.log(err.statusText);
            // hide loading spinner
            hideSpinner();
        }
    });
}

/**
 * This function fetch & load sub cause code pie chart as per the given params
 * @method createFaultPieChart
 * @param api_url {String}, It contains the url of api to fetch sub cause code data
 * @param master_causecode_name {String}, It contains name of master code for which the sub cause code data is to be drawn
 */
function createFaultPieChart(api_url, master_causecode_name) {

    $.ajax({
        url: api_url,
        type: 'GET',
        success: function(all_data_response) {
            if (typeof(all_data_response) == 'string') {
                all_data_response = JSON.parse(all_data_response);
            }

            if (all_data_response['result'] == 'ok') {
                var data_list = all_data_response['aaData'],
                    pie_chart_data = [],
                    pie_dict = {},
                    names_list = [];
                for(var j=0; j<data_list.length; j++) {
                    var sub_causecode = data_list[j]['sub_causecode'] ? data_list[j]['sub_causecode'] : 'NA',
                        outage_time = data_list[j]['outage_in_minutes'] ? parseFloat(data_list[j]['outage_in_minutes']) : 0;

                    if (names_list.indexOf(sub_causecode) == -1) {
                        pie_dict[sub_causecode] = 0;
                        names_list.push(sub_causecode);
                    }

                    pie_dict[sub_causecode] += outage_time;
                }
                
                for(var key in pie_dict) {
                    if (pie_dict.hasOwnProperty(key)) {
                        pie_chart_data.push([key, parseFloat(parseFloat(pie_dict[key]).toFixed(2))])
                    }
                }

                var bootbox_html = '';

                bootbox_html += '<div class="pie_chart_container" align="center">\
                                    <div id="fault_pie_chart"></div>\
                                </div>';

                bootbox.dialog({
                    message: bootbox_html,
                    title: '<i class="fa fa-bar-chart">&nbsp;</i> Fault Segment - '+master_causecode_name
                });

                // Update Modal width to 90%;
                $(".modal-dialog").css("width","90%");
                
                var chart_legends = middle_legends;
                // If more items in chart then show legends in right side(vertically)
                if (pie_chart_data.length > 5) {
                    chart_legends = side_legends;
                }

                $('#fault_pie_chart').highcharts({
                    chart: {
                        type: 'pie'
                    },
                    exporting:{
                        enabled : true,
                        allowHTML: true,
                        sourceWidth: 950,
                        sourceHeight: 375
                    },
                    colors: chart_colors_list,
                    title: {
                        text: ''
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
                    legend: chart_legends,
                    tooltip: {
                        formatter: function () {
                            var point_name = this.key ? $.trim(this.key) : "Value",
                                tooltip_html = "";

                            tooltip_html += '<ul><li><b>'+master_causecode_name+'</b></li><br/>';
                            tooltip_html += '<li>'+point_name+' : '+this.point.y+'</li><br/></ul>';

                            return tooltip_html;
                        }
                    },
                    credits: {
                        enabled: false
                    },
                    series: [{
                        data: pie_chart_data,
                        name: master_causecode_name,
                        title: master_causecode_name
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

/**
 * This function fetch & load MTTR Summary chart
 * @method loadMTTRSummaryChart
 */
function loadMTTRSummaryChart(ajax_url, month, selected_state, selected_city, extra_info) {
    if (ajax_url.indexOf('?') > -1) {
        ajax_url +='&month='+month+'&state_name=' + selected_state + '&city_name='+ selected_city;
    } else {
        ajax_url +='?month='+month+'&state_name=' + selected_state + '&city_name='+ selected_city;
    }
     
    $.ajax({
        url: ajax_url,
        type: 'GET',
        success: function(response) {

            if (typeof(response) == 'string') {
                response = JSON.parse(response);
            }

            if (response['success']) {
                var current_dateobj = new Date(Number(month) * 1000),
                    month_txt = month_dict[current_dateobj.getMonth()],
                    year_txt = current_dateobj.getFullYear(),
                    year_month_str = month_txt && year_txt ? month_txt + ' ' + year_txt : '',
                    column_series_data = [],
                    categories = [],
                    chart_dom_id = '';

                var chart_legends = middle_legends;

                if (extra_info['is_normal']) {
                    chart_dom_id = 'mttr_summary_chart_container';
                } else {
                    chart_dom_id = 'mttr_detail_chart_container';

                    var bootbox_html = '';

                    bootbox_html += '<div id="' + chart_dom_id + '" align="center">\
                                        <div id="fault_pie_chart"></div>\
                                    </div>';

                    bootbox.dialog({
                        message: bootbox_html,
                        title: '<i class="fa fa-bar-chart">&nbsp;</i> MTTR - ' + extra_info['series_name']
                    });

                    // Update Modal width to 90%;
                    $(".modal-dialog").css("width","90%");

                    // If more items in chart then show legends in right side(vertically)
                    if (response['data'].length > 5) {
                        chart_legends = side_legends;
                    }
                }

                // Initialize column chart for master cause code
                $('#'+ chart_dom_id).highcharts({
                    chart: {
                        type: 'pie'
                    },
                    exporting:{
                        enabled : true,
                        allowHTML: true,
                        sourceWidth: 950,
                        sourceHeight: 375
                    },
                    colors: chart_colors_list,
                    title: {
                        text: '',
                        align: 'left'
                    },
                    tooltip: {
                        formatter: function () {
                            var series_name = this.point.name ? $.trim(this.point.name) : "Value",
                                tooltip_html = "";

                            if (extra_info['is_normal']) {
                                tooltip_html += '<ul><li><b>MTTR Summary</b></li><br/>';
                            } else {
                                tooltip_html += '<ul><li><b>' + extra_info['series_name'] + '</b></li><br/>';
                            }
                            tooltip_html += '<li>'+series_name+' : '+this.point.y+'%</li><br/></ul>';

                            return tooltip_html;
                        }
                    },
                    legend: chart_legends,
                    credits: {
                        enabled: false
                    },
                    plotOptions: {
                        pie: {
                            allowPointSelect: true,
                            cursor: 'pointer',
                            dataLabels: {
                                enabled: false
                            },
                            showInLegend: true
                        },
                        series: {
                            point: {
                                events: {
                                    click: function(e) {
                                        if (extra_info['is_normal']) {
                                            // Show Loading Spinner
                                            showSpinner();
                                            var series_name = this.name;

                                            // Call "createFaultPieChart" to show pie chart in popup
                                            loadMTTRSummaryChart(
                                                detailed_mttr_data_url + '?mttr_param='+series_name,
                                                month,
                                                selected_state,
                                                selected_city,
                                                {
                                                    'series_name': series_name
                                                }
                                            );
                                        }
                                    }
                                }
                            }
                        }
                    },
                    series: [{
                        // 'name': ,
                        'data': response['data']
                    }],
                    noData: {
                        style: {
                            fontWeight: 'bold',
                            fontSize: '20px',
                            color: '#539fb8',
                        }
                    }
                });
            }

            // Hide Loading Spinner
            hideSpinner();
        },
        error: function(err) {
            // console.log(err.statusText);
            // Hide Loading Spinner
            hideSpinner();
        }
    });
}

/**
 * This function fetch & load INC ticket chart
 * @method loadINCTicketChart
 */
function loadINCTicketChart(api_url, selected_severity) {

    $.ajax({
        url: api_url,
        type: 'GET',
        success: function(all_data_response) {
            if (typeof(all_data_response) == 'string') {
                all_data_response = JSON.parse(all_data_response);
            }

            if (all_data_response['result'] == 'ok') {
                var data_list = all_data_response['aaData'],
                    target_data = [],
                    sev_data = [];
                for(var j=0; j<data_list.length; j++) {
                    var timestamp = Number(data_list[j]['timestamp']) * 1000;
                    sev_data.push([
                        timestamp,
                        data_list[j]['tt_percent']
                    ]);

                    target_data.push([
                        timestamp,
                        data_list[j]['target_percent']
                    ]);
                }
                var chart_title = 'RF Network: '+ selected_severity;
                $('#inc_line_chart_container').highcharts({
                    chart: {
                        type: 'spline'
                    },
                    exporting:{
                        enabled : true,
                        allowHTML: true,
                        sourceWidth: 950,
                        sourceHeight: 375,
                        filename: chart_title
                    },
                    colors: chart_colors_list,
                    title: {
                        text: chart_title
                    },
                    xAxis: {
                        title: {
                            text: 'Month'
                        },
                        type: 'datetime',
                        dateTimeLabelFormats: {
                            month: '%b %Y',
                            year: '%Y'
                        },
                        tickInterval: 30 * 24 * 3600 * 1000
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: '%'
                        },
                        labels: {
                            overflow: 'justify'
                        }
                    },
                    plotOptions: {
                        spline: {
                            dataLabels: {
                                enabled: false
                            },
                            showInLegend: true,
                            marker: {
                                enabled: true
                            }
                        }
                    },
                    legend: middle_legends,
                    tooltip: {
                        formatter: function (e) {
                            var tooltip_html = "";
                            tooltip_html += '<ul><li><b>'+selected_severity+' ('+getFormattedDate(this.x)+')</b></li><br/>';

                            if (this.points && this.points.length > 0) {
                                for(var i=0;i<this.points.length;i++) {
                                    var color = this.points[i].series.color;

                                    tooltip_html += '<li><br/><span style="color:' + color + '"> \
                                                    '+this.points[i].series.name+'</span>: <strong> \
                                                    ' +this.points[i].y+'%</strong></li>';
                                }
                            } else {
                                tooltip_html += '<li><br/><span style="color:' + this.point.color + '">\
                                                ' + this.point.name + '</span>: <strong>' + this.point.y + '%</strong></li>';
                            }

                            tooltip_html += '</ul>';

                            return tooltip_html;
                        },
                        crosshairs: true,
                        shared: true,
                    },
                    credits: {
                        enabled: false
                    },
                    series: [{
                        "data": sev_data,
                        "name": 'TT %',
                        "type": 'spline'
                    }, {
                        "data": target_data,
                        "name": 'Target %',
                        "type": 'spline'
                    }],
                    noData: {
                        style: {
                            fontWeight: 'bold',
                            fontSize: '20px',
                            color: '#539fb8',
                        }
                    }
                });
                
            }
            
            // Hide Loading Spinner
            hideSpinner();
        },
        error: function(err) {
            // console.log(err.statusText);
            // Hide Loading Spinner
            hideSpinner();
        }
    });
}

/**
 * This function fetch & load resolution efficieny chart
 * @method loadResolutionEfficienyChart
 */
function loadResolutionEfficienyChart(api_url) {
    
    $.ajax({
        url: api_url,
        type: 'GET',
        success: function(all_data_response) {
            if (typeof(all_data_response) == 'string') {
                all_data_response = JSON.parse(all_data_response);
            }

            if (all_data_response['result'] == 'ok') {
                var data_list = all_data_response['aaData'],
                    data_dict = {};

                for(var j=0; j<data_list.length; j++) {
                    var timestamp = Number(data_list[j]['timestamp']) * 1000;
                    for (var i=0;i<downtime_slab_key_list.length; i++) {

                        if(!data_dict[downtime_slab_key_list[i]]) {
                            data_dict[downtime_slab_key_list[i]] = {
                                'data': [],
                                'type': 'spline',
                                'name': downtime_slab_dict[downtime_slab_key_list[i]]
                            }
                        }

                        data_dict[downtime_slab_key_list[i]]['data'].push([
                            timestamp,
                            data_list[j][downtime_slab_key_list[i]]
                        ])
                    }
                }

                var resultset = [];

                for(key in data_dict) {
                    if(data_dict.hasOwnProperty(key)) {
                        resultset.push(data_dict[key]);
                    }
                }

                var chart_title = 'RE: RF Network';
                $('#inc_line_chart_container').highcharts({
                    chart: {
                        type: 'spline'
                    },
                    exporting:{
                        enabled : true,
                        allowHTML: true,
                        sourceWidth: 950,
                        sourceHeight: 375,
                        filename: chart_title
                    },
                    colors: chart_colors_list,
                    title: {
                        text: chart_title
                    },
                    xAxis: {
                        title: {
                            text: 'Month'
                        },
                        type: 'datetime',
                        dateTimeLabelFormats: {
                            month: '%b %Y',
                            year: '%Y'
                        },
                        tickInterval: 30 * 24 * 3600 * 1000
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: '%'
                        },
                        labels: {
                            overflow: 'justify'
                        }
                    },
                    plotOptions: {
                        spline: {
                            dataLabels: {
                                enabled: false
                            },
                            showInLegend: true,
                            marker: {
                                enabled: true
                            }
                        }
                    },
                    legend: middle_legends,
                    tooltip: {
                        formatter: function (e) {
                            var tooltip_html = "",
                                that = this;
                            tooltip_html += '<b>Resolution Efficiency ('+getFormattedDate(that.x)+')</b><br/>';

                            if (that.points && that.points.length > 0) {
                                for(var i=0;i<that.points.length;i++) {
                                    var color = that.points[i].series.color;
                                    tooltip_html += '<br/><span style="color:' + color + '"> '+that.points[i].series.name+'</span>: \
                                                     <b>' +that.points[i].y+'%</b>';
                                }
                            } else {
                                tooltip_html += '<br/><span style="color:' + that.point.color + '">\
                                                ' + that.point.name + '</span>: <b>' + that.point.y + '%</b>';
                            }
                            return tooltip_html;
                        },
                        crosshairs: true,
                        shared: true,
                    },
                    credits: {
                        enabled: false
                    },
                    series: resultset,
                    noData: {
                        style: {
                            fontWeight: 'bold',
                            fontSize: '20px',
                            color: '#539fb8',
                        }
                    }
                });    
            }
            
            // Hide Loading Spinner
            hideSpinner();
        },
        error: function(err) {
            // console.log(err.statusText);
            // Hide Loading Spinner
            hideSpinner();
        }
    });
}

/**
 * This function accepts datetime in epoch format & returns "Month - Year" formatted string .
 * @method getFormattedDate
 * @param input_date {Number}, It contains datetime in epoch format.
 */
function getFormattedDate(input_date) {
    var formatted_date = '';

    try {
        var fetched_datetime = new Date(input_date),
            fetched_month = fetched_datetime.getMonth(),
            fetched_year = fetched_datetime.getFullYear();

        formatted_date = month_dict[fetched_month] + '-' + fetched_year;
    } catch(e) {
        // console.error(e);
    }

    return formatted_date;
}

/**
 * This function fetch data & loads Sector/Backhaul summary status column stacked chart
 * @method loadCapacityAlertChart
 * @param ajax_url {String}, If contains the API url to fetch Sector/Backhaul summary status data
 */
function loadCapacityAlertChart(ajax_url, dom_id_prefix, page_type) {

    // If dom id not exists then return
    if ($('#'+dom_id_prefix+'_chart').length == 0) {
        return false;
    }

    var chart_title = 'Sector Summary Status',
        tooltip_suffix = '%';

    if (page_type == 'backhaul') {
        chart_title = 'Backhaul Summary Status';
        tooltip_suffix = '';
    }

    $.ajax({
        url: ajax_url,
        type: 'GET',
        success: function(response) {

            if (typeof(response) == 'string') {
                response = JSON.parse(response);
            }

            if (response['result'] == 'ok') {
                
                var column_series_data = [],
                    data_dict = {};

                for (var i=0;i<response['aaData'].length;i++) {
                    var y1_val = response['aaData'][i]['na_percent'],
                        y2_val = response['aaData'][i]['sp_percent'],
                        timestamp = response['aaData'][i]['timestamp'] * 1000;

                    if (typeof y1_val == 'undefined') {
                        y1_val = response['aaData'][i]['na_sector'];
                    }

                    if (typeof y2_val == 'undefined') {
                        y2_val = response['aaData'][i]['sp_sector'];
                    }
                    if (!data_dict['needs_augmentation']) {
                        data_dict['needs_augmentation'] = [];
                    }
                    data_dict['needs_augmentation'].push([
                        timestamp,
                        y1_val
                    ])

                    if (!data_dict['stop_provisioning']) {
                        data_dict['stop_provisioning'] = [];
                    }
                    data_dict['stop_provisioning'].push([
                        timestamp,
                        y2_val
                    ])

                }
                
                column_series_data.push({
                    'name': 'Upgrade Sector '+ tooltip_suffix,
                    'type': 'column',
                    'data': data_dict['needs_augmentation']
                }, {
                    'name': 'Stop Provisioning '+ tooltip_suffix,
                    'type': 'column',
                    'data': data_dict['stop_provisioning']
                });

                // Initialize column chart for master cause code
                $('#'+dom_id_prefix+'_chart').highcharts({
                    chart: {
                        type: 'column'
                    },
                    exporting:{
                        enabled : true,
                        allowHTML: true,
                        sourceWidth: 950,
                        sourceHeight: 375,
                        filename: chart_title
                    },
                    colors: chart_colors_list,
                    title: {
                        text: '',
                        align: 'left'
                    },
                    xAxis: {
                        title: {
                            text: 'Month'
                        },
                        type: 'datetime',
                        dateTimeLabelFormats: {
                            month: '%b %Y',
                            year: '%Y'
                        },
                        tickInterval: 30 * 24 * 3600 * 1000
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'Ageing'
                        },
                        labels: {
                            overflow: 'justify'
                        }
                    },
                    tooltip: {
                        formatter: function (e) {
                            var tooltip_html = "";
                            tooltip_html += '<ul><li><b>'+chart_title+' ('+getFormattedDate(this.x)+')</b></li><br/>';

                            if (this.points && this.points.length > 0) {
                                for(var i=0;i<this.points.length;i++) {
                                    var color = this.points[i].series.color;

                                    tooltip_html += '<li><br/><span style="color:' + color + '"> \
                                                    '+this.points[i].series.name+'</span>: <strong> \
                                                    ' +this.points[i].y+ tooltip_suffix+'</strong></li>';
                                }
                            } else {
                                tooltip_html += '<li><br/><span style="color:' + this.point.color + '">\
                                                ' + this.point.name + '</span>: <strong>' + this.point.y + '%</strong></li>';
                            }

                            tooltip_html += '</ul>';

                            return tooltip_html;
                        },
                        crosshairs: true,
                        shared: true,
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
                        layout: 'horizontal',
                        align: 'center',
                        // verticalAlign: 'top'
                    },
                    credits: {
                        enabled: false
                    },
                    plotOptions: {
                        column: {
                            pointWidth: 12,
                            groupPadding: 0,
                            stacking: 'normal'
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

            // hide loading spinner
            hideSpinner();
        },
        error: function(err) {
            // console.log(err.statusText);
            // hide loading spinner
            hideSpinner();
        }
    });
}

/**
 * This function fetch data & loads Network/PTP BH uptime line chart
 * @method loadUptimeChart
 * @param ajax_url {String}, If contains the API url to fetch Network/PTP BH uptime data
 */
function loadUptimeChart(ajax_url, dom_id_prefix, page_type) {

    // If dom id not exists then return
    if ($('#'+dom_id_prefix+'_chart').length == 0) {
        return false;
    }

    var chart_title = 'Network Uptime',
        tooltip_suffix = '%';

    if (page_type == 'ptpbh') {
        chart_title = 'PTP BH Uptime';
        // tooltip_suffix = '';
    }

    $.ajax({
        url: ajax_url,
        type: 'GET',
        success: function(response) {

            if (typeof(response) == 'string') {
                response = JSON.parse(response);
            }

            if (response['result'] == 'ok') {
                
                var line_series_data = [],
                    data_dict = {};

                for (var i=0;i<response['aaData'].length;i++) {
                    var y1_val = response['aaData'][i]['below_threshold'] ? response['aaData'][i]['below_threshold'] : 0,
                        y2_val = response['aaData'][i]['above_threshold'] ? response['aaData'][i]['above_threshold'] : 0,
                        timestamp = response['aaData'][i]['timestamp'] * 1000;

                    if (!data_dict['below_threshold']) {
                        data_dict['below_threshold'] = [];
                    }

                    data_dict['below_threshold'].push([
                        timestamp,
                        y1_val
                    ])

                    if (!data_dict['above_threshold']) {
                        data_dict['above_threshold'] = [];
                    }
                    data_dict['above_threshold'].push([
                        timestamp,
                        y2_val
                    ])
                }
                
                line_series_data.push({
                    'name': 'Greater Than 99.5'+ tooltip_suffix,
                    'type': 'line',
                    'data': data_dict['above_threshold']
                }, {
                    'name': 'Less Than 99.5'+ tooltip_suffix,
                    'type': 'line',
                    'data': data_dict['below_threshold']
                });

                // Initialize column chart for master cause code
                $('#'+dom_id_prefix+'_chart').highcharts({
                    chart: {
                        type: 'line'
                    },
                    exporting:{
                        enabled : true,
                        allowHTML: true,
                        sourceWidth: 950,
                        sourceHeight: 375,
                        filename: chart_title
                    },
                    colors: chart_colors_list,
                    title: {
                        text: '',
                        align: 'left'
                    },
                    xAxis: {
                        title: {
                            text: 'Month'
                        },
                        type: 'datetime',
                        dateTimeLabelFormats: {
                            month: '%b %Y',
                            year: '%Y'
                        },
                        tickInterval: 30 * 24 * 3600 * 1000
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'Uptime %'
                        },
                        labels: {
                            overflow: 'justify'
                        }
                    },
                    tooltip: {
                        formatter: function (e) {
                            var tooltip_html = "";
                            tooltip_html += '<ul><li><b>'+chart_title+' ('+getFormattedDate(this.x)+')</b></li><br/>';

                            if (this.points && this.points.length > 0) {
                                for(var i=0;i<this.points.length;i++) {
                                    var color = this.points[i].series.color;

                                    tooltip_html += '<li><br/><span style="color:' + color + '"> \
                                                    '+this.points[i].series.name+'</span>: <strong> \
                                                    ' +this.points[i].y+ tooltip_suffix+'</strong></li>';
                                }
                            } else {
                                tooltip_html += '<li><br/><span style="color:' + this.point.color + '">\
                                                ' + this.point.name + '</span>: <strong>' + this.point.y + '%</strong></li>';
                            }

                            tooltip_html += '</ul>';

                            return tooltip_html;
                        },
                        crosshairs: true,
                        shared: true,
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
                        layout: 'horizontal',
                        align: 'center',
                        // verticalAlign: 'top'
                    },
                    credits: {
                        enabled: false
                    },
                    plotOptions: {
                        column: {
                            pointWidth: 12,
                            groupPadding: 0,
                            stacking: 'normal'
                        }
                    },
                    series: line_series_data,
                    noData: {
                        style: {
                            fontWeight: 'bold',
                            fontSize: '20px',
                            color: '#539fb8',
                        }
                    }
                });
            }

            // hide loading spinner
            hideSpinner();
        },
        error: function(err) {
            // console.log(err.statusText);
            // hide loading spinner
            hideSpinner();
        }
    });
}

/**
 * This function fetch & load RFO trends chart
 * @method loadRFOTrendsChart
 */
function loadRFOTrendsChart(ajax_url, extra_info) {

    $.ajax({
        url: ajax_url+'&request_for_chart=1',
        type: 'GET',
        success: function(response) {

            if (typeof(response) == 'string') {
                response = JSON.parse(response);
            }

            if (response['result'] == 'ok') {
                var month = $('select[name="month_selector"]').val(),
                    current_dateobj = new Date(Number(month) * 1000),
                    month_txt = month_dict[current_dateobj.getMonth()],
                    year_txt = current_dateobj.getFullYear(),
                    year_month_str = month_txt && year_txt ? month_txt + ' ' + year_txt : '',
                    column_series_data = [],
                    categories = [],
                    chart_dom_id = '',
                    name_key = 'master_causecode',
                    dataset = response['aaData'];

                if (!extra_info['is_normal']) {
                    name_key = 'sub_causecode';
                    var sub_total_minutes = 0;
                } else {
                    var master_total_minutes = 0;
                }

                dataset = dataset.filter(function(item) {
                    item['y'] = item['actual_downtime'];
                    item['name'] = item[name_key];
                    if (extra_info['is_normal']) {
                        master_total_minutes += item['actual_downtime'];
                    } else {
                        sub_total_minutes += item['actual_downtime'];
                    }
                    return true;
                });

                var chart_legends = middle_legends;

                // If more items in chart then show legends in right side(vertically)
                if (dataset.length > 5) {
                    chart_legends = side_legends;
                }

                if (extra_info['is_normal']) {
                    chart_dom_id = 'rfo_trends_chart_container';
                } else {
                    chart_dom_id = 'rfo_trends_detail_chart_container';

                    var bootbox_html = '';

                    bootbox_html += '<div id="' + chart_dom_id + '" align="center">\
                                        <div id="fault_pie_chart"></div>\
                                    </div>';

                    bootbox.dialog({
                        message: bootbox_html,
                        title: '<i class="fa fa-bar-chart">&nbsp;</i> RFO Trends - ' + extra_info['series_name']
                    });

                    // Update Modal width to 90%;
                    $(".modal-dialog").css("width","90%");
                }

                // Initialize column chart for master cause code
                $('#'+ chart_dom_id).highcharts({
                    chart: {
                        type: 'pie'
                    },
                    exporting:{
                        enabled : true,
                        allowHTML: true,
                        sourceWidth: 950,
                        sourceHeight: 375
                    },
                    colors: chart_colors_list,
                    title: {
                        text: '',
                        align: 'left'
                    },
                    tooltip: {
                        formatter: function () {
                            var series_name = this.point.name ? $.trim(this.point.name) : "Value",
                                tooltip_html = "",
                                total_minutes = 0;

                            if (extra_info['is_normal']) {
                                tooltip_html += '<ul><li><b>RFO Trends</b></li><br/>';
                                total_minutes = master_total_minutes;
                            } else {
                                tooltip_html += '<ul><li><b>' + extra_info['series_name'] + '</b></li><br/>';
                                total_minutes = sub_total_minutes;
                            }

                            var point_percent = '';
                            try {
                                point_percent = ((this.point.y/total_minutes) * 100).toFixed(2);
                            } catch(e) {
                                // console.error(e);
                            }
                            tooltip_html += '<li>'+series_name+' : '+this.point.y+' Minutes</li><br/>';
                            if (point_percent && total_minutes) {
                                tooltip_html += '<li>'+series_name+'(%) : '+point_percent+'%</li><br/>';
                            }
                            tooltip_html += '</ul>';

                            return tooltip_html;
                        }
                    },
                    legend: chart_legends,
                    credits: {
                        enabled: false
                    },
                    plotOptions: {
                        pie: {
                            allowPointSelect: true,
                            cursor: 'pointer',
                            dataLabels: {
                                enabled: false
                            },
                            showInLegend: true
                        },
                        series: {
                            point: {
                                events: {
                                    click: function(e) {
                                        if (extra_info['is_normal']) {
                                            // Show Loading Spinner
                                            showSpinner();
                                            var series_name = this.name,
                                                all_data_api_url = all_data_url,
                                                selected_month = $('select[name="month_selector"]').val(),
                                                selected_state = $('select[name="state_selector"]').val(),
                                                selected_city = $('select[name="city_selector"]').val(),
                                                selected_severity = $('select[name="severity_selector"]').val();

                                            if (selected_month) {
                                                selected_month = Number(selected_month) / 1000;
                                            }

                                            all_data_api_url += '?month=' + String(selected_month);
                                            all_data_api_url += '&state_name=' + String(selected_state);
                                            all_data_api_url += '&city_name='+ String(selected_city);
                                            all_data_api_url += '&severity=' + String(selected_severity);
                                            all_data_api_url += '&master_causecode=' + String(series_name);
                                            all_data_api_url += '&request_for_chart=1';

                                            // Call "createFaultPieChart" to show pie chart in popup
                                            loadRFOTrendsChart(
                                                all_data_api_url,
                                                {
                                                    'series_name': series_name
                                                }
                                            );
                                        }
                                    }
                                }
                            }
                        }
                    },
                    series: [{
                        // 'name': ,
                        'data': dataset
                    }],
                    noData: {
                        style: {
                            fontWeight: 'bold',
                            fontSize: '20px',
                            color: '#539fb8',
                        }
                    }
                });
                
                if (!extra_info['is_normal']) {
                    setTimeout(function() {
                        $(window).resize();
                    }, 250);
                }
            }

            // Hide Loading Spinner
            hideSpinner();
        },
        error: function(err) {
            // console.log(err.statusText);
            // Hide Loading Spinner
            hideSpinner();
        }
    });
}

/**
 * This event trigger when any filter control selectbox value changed
 * @event Change
 */
$('.filter_controls').change(function(e) {
    
    // show loading spinner
    showSpinner();

    // When state select then show cities of that state only
    if ($(this).attr('name').indexOf('state') > -1) {
        var selected_val = $(this).val();
        $('select[name="city_selector"] option').show();
        if (selected_val) {
            $('select[name="city_selector"]').val('');
            $('select[name="city_selector"] option:not([parent_id="'+selected_val+'"])').hide();
            $('select[parent_id="'+selected_val+'"] option').show();
        } else {
            $('select[name="city_selector"]').val('');
        }
    }
    var location_pathname = window.location.pathname;
    if (location_pathname.indexOf('/mttr_summary/') > -1) {
        if ($(this).attr('name').indexOf('month') > -1) {
            $('select[name="state_selector"]').val('');
            $('select[name="city_selector"]').val('');
        }
        initMTTRDashboard()
    } else if (location_pathname.indexOf('/rfo_analysis/') > -1 || location_pathname.indexOf('/rfo_trends/') > -1) {
        if ($(this).attr('name').indexOf('month') > -1) {
            $('select[name="state_selector"]').val('');
            $('select[name="city_selector"]').val('');
            if (location_pathname.indexOf('/rfo_trends/') > -1) {
                $('select[name="severity_selector"]').val('');
            }
        }
        initRfoDashboard();
    } else if (location_pathname.indexOf('/inc_ticket_rate/') > -1) {
        initINCTicketDashboard();
    } else if (location_pathname.indexOf('/resolution_efficiency/') > -1) {
        initResolutionEfficiencyDashboard();
    } else if (location_pathname.indexOf('/backhaul_status/') > -1 || location_pathname.indexOf('/sector_status/') > -1) {
        initCapacitySummaryDashboard();
    } else if (location_pathname.indexOf('/network_uptime/') > -1 || location_pathname.indexOf('/ptpbh_uptime/') > -1) {
        initUptimeDashboard();
    } else {
        // hide loading spinner
        hideSpinner();
    }
});

/**
 * This event triggers when any tab on dashboard pages clicked
 * @event click
 */
$('.nav-tabs li a').click(function(e) {

    var location_pathname = window.location.pathname;

    $('.nav-tabs li').removeClass('active');
    $(this).parent('li').addClass('active');

    $('.tab-content .tab-pane').removeClass('active');
    $($(this).attr('href')).addClass('active');

    if (location_pathname.indexOf('/backhaul_status/') > -1 || location_pathname.indexOf('/sector_status/') > -1) {
        initCapacitySummaryDashboard();
    } else if (location_pathname.indexOf('/network_uptime/') > -1 || location_pathname.indexOf('/ptpbh_uptime/') > -1) {
        initUptimeDashboard();
    }
});

/**
 * This event triggers when any key pressed in taget input box
 * @event keyup
 */
$('input[name="target_selector"]').keyup(function(e) {
    if(e.keyCode == 13) {
        initINCTicketDashboard();
    }
});

