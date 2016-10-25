/**
 * This event initializes select2 for advance filtering fields
 * @uses select2
 */
$(".snmp_filters").select2({
    multiple: true,
    width: "resolve",
    minimumInputLength: 3,
    query: function (query) {
        var element_type = this.element[0].id,
            entered_text = query.term,
            alarm_type = $("input[name='alarm_type']:checked").val(),
            active_tab = $.trim($('.nav-tabs li.active a').text()).toLowerCase(),
            query_string = 'search_txt=' + entered_text + '&item_type=' + element_type + "&alarm_type=" + alarm_type + "&tab_id="+ active_tab,
            ajax_url = filter_api_url + "?" + query_string,
            data = {results: []};
        // Make Ajax Call
        $.ajax({
            url : ajax_url,
            type : "GET",
            success : function(response) {

                var result = "";
                // Type check of response
                if (typeof response == 'string') {
                    result = JSON.parse(response);
                } else {
                    result = response;
                }

                data['results'] = result.data;

                query.callback(data);
            },
            error : function(err) {
                query.callback(data);
            }
        });
    }
});

/**
 * This event trigger when alarm_type radio input changed
 * @event change
 */
$('input[name="alarm_type"]').change(function(e) {
    var alarm_type = $(this).val(),
        new_get_param = 'alarm_type='+alarm_type,
        active_tab_id = $('.nav-tabs li.active a').attr('id'),
        pmp_url = $("#snmp_pmp_tab").attr("data_url"),
        rad5k_url = $("#snmp_rad5k_tab").attr("data_url"),
        headers = '',
        wimax_url = $("#snmp_wimax_tab").attr("data_url"),
        all_url = $("#snmp_all_tab").attr("data_url"),
        updated_url_pmp = "",
        updated_url_wimax = "",
        updated_url_all = "";

    show_hide_count_column();

    if (alarm_type == 'current') {
        headers = current_headers;
    } else {
        headers = clear_history_headers;
    }

    // Update PMP url
    var array1 = pmp_url.split("?"),
        array2 = array1[1].split("&");
    array2[0] = new_get_param
    array1[1] = array2.join('&');
    updated_url_pmp = array1.join('?');

    // Update Radwin5K url
    var array1 = rad5k_url.split("?"),
        array2 = array1[1].split("&");
    array2[0] = new_get_param
    array1[1] = array2.join('&');
    updated_url_rad5k = array1.join('?');

    // Update WiMAX url
    var array1 = wimax_url.split("?"),
        array2 = array1[1].split("&");
    array2[0] = new_get_param
    array1[1] = array2.join('&');
    updated_url_wimax = array1.join('?');

    // Update All url
    var array1 = all_url.split("?"),
        array2 = array1[1].split("&");
    array2[0] = new_get_param
    array1[1] = array2.join('&');
    updated_url_all = array1.join('?');

    // Update the 'data_url' attribute of all tabs
    $("#snmp_pmp_tab").attr("data_url", updated_url_pmp);
    $("#snmp_rad5k_tab").attr("data_url", updated_url_rad5k);
    $("#snmp_wimax_tab").attr("data_url", updated_url_wimax);
    $("#snmp_all_tab").attr("data_url", updated_url_all);

    $("#snmp_pmp_tab").attr("data_header", headers);
    $("#snmp_rad5k_tab").attr("data_header", headers);
    $("#snmp_wimax_tab").attr("data_header", headers);
    $("#snmp_all_tab").attr("data_header", headers);

    // Trigger click event on active tab
    $("#" + active_tab_id).trigger('click', true);
});

function show_hide_count_column() {
    if (!show_customer_count) {
        return false;
    }

    var hide_class = 'hide',
        alarm_type = $.trim($('input[name="alarm_type"]:checked').val());

    if (alarm_type == 'current') {
        hide_class = '';
    }

    var all_headers_list = JSON.parse($("#snmp_all_tab").attr("data_header")),
        pmp_headers_list = JSON.parse($("#snmp_pmp_tab").attr("data_header")),
        rad5k_headers_list = JSON.parse($("#snmp_rad5k_tab").attr("data_header")),
        wimax_headers_list = JSON.parse($("#snmp_wimax_tab").attr("data_header"));

    for (var i=0;i<all_headers_list.length;i++) {
        if (all_headers_list[i]['mData'] == 'customer_count') {
            all_headers_list[i]['sClass'] = hide_class;
        }
    }

    for (var i=0;i<pmp_headers_list.length;i++) {
        if (pmp_headers_list[i]['mData'] == 'customer_count') {
            pmp_headers_list[i]['sClass'] = hide_class;
        }
    }

    for (var i=0;i<rad5k_headers_list.length;i++) {
        if (rad5k_headers_list[i]['mData'] == 'customer_count') {
            rad5k_headers_list[i]['sClass'] = hide_class;
        }
    }    

    for (var i=0;i<wimax_headers_list.length;i++) {
        if (wimax_headers_list[i]['mData'] == 'customer_count') {
            wimax_headers_list[i]['sClass'] = hide_class;
        }
    }

    // Update headers data in tabs header attribute
    $("#snmp_all_tab").attr("data_header", JSON.stringify(all_headers_list));
    $("#snmp_pmp_tab").attr("data_header", JSON.stringify(pmp_headers_list));
    $("#snmp_rad5k_tab").attr("data_header", JSON.stringify(rad5k_headers_list));
    $("#snmp_wimax_tab").attr("data_header", JSON.stringify(wimax_headers_list));
    
    return true;

}

/**
 * This event triggers when 'Advance Filter' button clicked & will show the filtering form
 * @event click
 */
$("#snmp_advFilterBtn").click(function(e) {
    // Show filtering form container
    $("#advFilterContainer").slideDown('slow');
});

/**
 * This event triggers when 'Remove Filter' button clicked & will show the filtering form
 * @event click
 */
$("#snmp_removeFilterBtn").click(function(e) {
    // Hide filtering form container
    $("#advFilterContainer").slideUp('slow');
    
    // Hide Remove Filter Button
    if (!$(this).hasClass('hide')) {
        $(this).addClass('hide')
    }

    // Show Advance Filter Button
    if ($("#snmp_advFilterBtn").hasClass('hide')) {
        $("#snmp_advFilterBtn").removeClass('hide')
    }

    var tab_id =  $('.nav-tabs li.active a').attr('id');

    // Call function to update URL of all tabs
    alert_updateTabsUrl('', false);

    // Call function to reset filtering form
    alert_resetFilteringForm();

    // trigger click event on active tab
    $('#' + tab_id).trigger('click', true);
});

/**
 * This event triggers 'Filter' button on Filtering form clicked
 * @event click
 */
$("#snmp_setAdvFilterBtn").click(function(e) {
    var applied_filters = alert_getAppliedFilters();

    if (applied_filters) {
        var tab_id =  $('.nav-tabs li.active a').attr('id');

        // Call function to update URL of all tabs
        alert_updateTabsUrl(applied_filters, true);

        // Hide filtering form container
        $("#advFilterContainer").slideUp('slow');

        // Show Remove Filter Button
        if ($("#snmp_removeFilterBtn").hasClass('hide')) {
            $("#snmp_removeFilterBtn").removeClass('hide')
        }

        // trigger click event on active tab
        $('#' + tab_id).trigger('click', true);
    }
});

/**
 * This event triggers when "Cancel" button on filter form clicked
 * @event click
 */
$("#snmp_cancelAdvFilterBtn").click(function(e) {
    // If remove button not shown then reset filters
    if ($("#snmp_removeFilterBtn").hasClass('hide')) {
        alert_resetFilteringForm();
    }

    // Hide filtering form container
    $("#advFilterContainer").slideUp('slow');            
});

/**
 * This function get the selected filters & return
 * @method alert_getAppliedFilters
 */
function alert_getAppliedFilters() {
    var select2_field_ids = [
            'ip_address',
            'eventname',
            'component_id',
            'component_name'
        ],
        checkbox_field_names = ['severity'],
        radio_field_names = [],
        applied_filters = "";

    // For select2 fields
    for (var i=0;i<select2_field_ids.length;i++) {
        var element_id = select2_field_ids[i],
            selected_values = $("#" + element_id).select2('data'),
            selected_str = [];

        if (selected_values && selected_values.length > 0) {
            for (var j=0;j<selected_values.length;j++) {
                var selected_txt = selected_values[j]['text']
                if (selected_txt && selected_str.indexOf(selected_txt) == -1) {
                    selected_str.push(selected_values[j].text);
                }
            }
            var connector = '';
            if (applied_filters) {
                connector = '&';
            }

            applied_filters += connector + '' + element_id + '=' + encodeURIComponent(selected_str.join('|'));
        }
    }

    // For Daterange picker field
    if (startDate && startDate) {
        var connector = '';
        if (applied_filters) {
            connector = '&';
        }
        var start_year = startDate.year(),
            start_month = Number(startDate.month()) + 1,
            start_day = startDate.date(),
            start_hour = startDate.hour(),
            start_minute = startDate.minute(),
            start_second = startDate.second(),
            end_year = endDate.year(),
            end_month = Number(endDate.month()) + 1,
            end_day = endDate.date(),
            end_hour = endDate.hour(),
            end_minute = endDate.minute(),
            end_second = endDate.second();

        // Append 0 before (1-9) month number
        if (Number(start_month) < 10) {
            start_month = String('0').concat(String(start_month));
        }

        if (Number(end_month) < 10) {
            end_month = String('0').concat(String(end_month));
        }

        var formatted_start_date = start_year + '-' + start_month + '-' + start_day + ' ' + start_hour + ':' + start_minute + ':' + start_second,
            formatted_end_date = end_year + '-' + end_month + '-' + end_day + ' ' + end_hour + ':' + end_minute + ':' + end_second;

        applied_filters += connector + 'start_date=' + encodeURIComponent(formatted_start_date);
        applied_filters += '&end_date=' + encodeURIComponent(formatted_end_date);
    }

    // For checkbox fields
    for (var i=0;i<checkbox_field_names.length;i++) {
        var element_id = checkbox_field_names[i],
            checked_values = $("[name='" + element_id + "']:checked"),
            dataset = [];

        for (var j=0;j<checked_values.length;j++) {
            var element_data = checked_values[j].value;
            if (element_data && dataset.indexOf(element_data) == -1) {
                dataset.push(element_data);
            }
        }

        if (dataset.length > 0) {
            var connector = '';
            if (applied_filters) {
                connector = '&';
            }

            applied_filters += connector + '' + element_id + '=' + encodeURIComponent(dataset.join('|'));
        }
    }


    return applied_filters;
}

/**
 * This function returns main URL of API with only default query string params
 * @method alert_getMainUrl
 * @param data_url {String}, It contains the api url save in tab's custom attribute
 */
function alert_getMainUrl(data_url, tab_txt) {
    
    if (!data_url) {
        return data_url;
    }

    // By default use 'all' as tech_name param
    if (!tab_txt) {
        tab_txt = 'all';
    }

    // In case of converter tab pass tech_name as switch
    if (tab_txt == 'converter') {
        tab_txt = 'switch';
    }

    // Remove extra params
    var param1 = data_url.split('tech_name');
    param1[1] = '=' + tab_txt
    data_url = param1.join('tech_name');

    return data_url
}

/**
 * This function updates the URL attribute of all tabs
 * @method alert_updateTabsUrl
 * @param applied_filter_str {String}, It contains the applied filters query string
 * @param set_url {Boolean}, It contains the boolean flag either to set url or reset
 */
function alert_updateTabsUrl(applied_filter_str, set_url) {
    var tabs_list = $('.nav-tabs li a');

    for (var i=0;i<tabs_list.length;i++) {
        var existing_url = tabs_list[i].attributes.data_url.value,
            tab_txt = $.trim(tabs_list[i].text).toLowerCase(),
            main_url = alert_getMainUrl(existing_url, tab_txt),
            new_url = '';

        if (set_url) {
            // Append the filtering string with API url
            new_url = main_url + "&" + applied_filter_str + '&is_filter_applied=1';
        } else {
            new_url = main_url;
        }

        // Update the url save in tab's custom attribute
        tabs_list[i].attributes.data_url.value = new_url;
    }

    return true;
}

/**
 * This function reset filtering form fields
 * @method alert_resetFilteringForm
 */
function alert_resetFilteringForm() {
    var select2_field_ids = [
            'ip_address',
            'eventname',
            'component_id',
            'component_name'
        ],
        severity_chkbox_list = $('[name="severity"]');

    // Reset Select2 fields
    for (var i=0;i<select2_field_ids.length;i++) {
        if ($('#' + select2_field_ids).length > 0) {
            $('#' + select2_field_ids).select2('val', '');
        }
    }

    // Reset severity checkboxes
    if ($('[name="severity"]:checked').length > 0) {
        for (var i=0;i<severity_chkbox_list.length;i++) {
            severity_chkbox_list[i].checked = false;
        }
    }

    // Reset Date range picker
    if (startDate || endDate) {
        // Remove daterangepicker from DOM
        $('#filter_date').daterangepicker().remove();
        
        startDate = '';
        endDate = '';

        // Add daterangepicker to DOM
        $(".date_range_container").append(date_range_picker_html);
        // Re-initialize daterange picker
        alert_initDateRangePicker()
    }

    return true;
}

/**
 * This function initializes daterange picker for advance filters on SIA listing page
 * @method alert_initDateRangePicker
 */
function alert_initDateRangePicker() {
    $('#filter_date').daterangepicker({
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
        separator: ' to '
    }, function (start, end) {
        startDate = start;
        endDate = end;
    });
}