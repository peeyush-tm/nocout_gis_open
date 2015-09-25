/**
 * This file handle the advance filtering feature for datatables.
 */
// Global Variables
var existing_pagesettings_html = '<div class="clearfix"></div>',
	string_column_options = '<option value="starts_with">Starts With</option> \
							 <option value="contains">Contains</option> \
							 <option value="not_contains">Does Not Contains</option> \
							 <option value="ends_with">Ends With</option>',
	number_column_options = '<option value="gt">Greater Than</option> \
							 <option value="gte">Greater Than Equals To</option> \
							 <option value="lt">Less Than</option> \
							 <option value="lte">Less Than Equals To</option>',
	condition_block_html = '<div class="form-group"> \
							<label class="col-sm-3 control-label">Select Condition</label> \
							<div class="col-sm-8"> \
							<select class="form-control condition_box" id="{}"> \
							<option value="equals">Is Equal To</option> \
							<option value="not_equals">Is Not Equal To</option> \
							</select></div></div>',
	excluded_columns = [
		'action', 'actions', 'nms_action', 'nms_actions', 'added_on', 'updated_on',
		'sys_timestamp', 'process_for', 'status_icon', 'is_processed', 'is_device_change',
		'file', 'logged_at', 'color_hex_value', 'icon_settings', 'user_selection',
		'range1', 'range2', 'range3', 'range4', 'range5', 'range6', 'range7', 'range8',
		'range9', 'range10'
	],
	global_variables_obj = {},
	global_table_id = '',
	global_grid_headers = '',
	global_api_url = '',
	global_destroy = '',
	global_current_table_title = '',
	global_app_name = '',
	global_header_class_name = '',
	global_data_class_name = '',
	global_header_extra_param = '',
	global_data_extra_param = '',
	global_excluded_columns = '',
	max_fields_length = 0,
	global_fields_counter = 0,
	used_columns_list = [],
	number_columns = [
		'numeric',
		'number',
		'integer'
	],
	no_filters_txt = 'No filter applied yet.',
	filter_btn_html = '<button class="btn btn-default btn-sm show_advance_filters_btn" \
					  id="{}"><i class="fa fa-filter"> </i> </button>',
	remove_filter_btn_html = '<button class="btn btn-danger btn-sm hide remove_advance_filters_btn" \
							  id="{}"><i class="fa fa-times"> </i> </button>';

/**
 * This function creates advance filters HTML as per the given headers
 * @method nocout_createAdvanceFilter
 * @param table_info_object {Object}, It contains the required info of table.
 */
function nocout_createAdvanceFilter (
	tableId,
    tableheaders,
    ajax_url,
    destroy,
    current_table_title,
    app_name,
    header_class_name,
    data_class_name,
    header_extra_param,
    data_extra_param,
    excluded_columns,
    advance_filter
) {
	// set table info in global variables
	global_table_id = tableId ? tableId : "";
	global_grid_headers = tableheaders ? tableheaders : "";
	global_api_url = ajax_url ? ajax_url : "";
	global_destroy = destroy ? destroy : "";
	global_current_table_title = current_table_title ? current_table_title : "";
	global_app_name = app_name ? app_name : "";
	global_header_class_name = header_class_name ? header_class_name : "";
	global_data_class_name = data_class_name ? data_class_name : "";
	global_header_extra_param = header_extra_param ? header_extra_param : "";
	global_data_extra_param = data_extra_param ? data_extra_param : "";
	global_excluded_columns = excluded_columns ? excluded_columns : "";

	var btn_html = filter_btn_html,
		remove_btn_html = remove_filter_btn_html;

	btn_html = btn_html.replace('{}', global_table_id+'_advance_filter_btn')
	remove_btn_html = remove_btn_html.replace('{}', global_table_id+'_remove_filter_btn')

	// Remove the existing button
	if ($('.show_advance_filters_btn').length > 0) {
		$('.show_advance_filters_btn').parent().remove();
	}

	// Add Advance Filter Button on GUI
	$('.control_btn_countainer').prepend('<li>'+btn_html+remove_btn_html+'</li>');

	$('.advance_filters_container').hide();

	if (global_variables_obj[global_table_id] && global_variables_obj[global_table_id]['is_filter_applied']) {
		$('#' + global_table_id + '_remove_filter_btn').removeClass('hide');
	}

	if (!global_grid_headers || $('#' + global_table_id + '_advance_filter').length > 0) {
		return true;
	}

	if (!global_variables_obj.hasOwnProperty(global_table_id)) {

		global_variables_obj[global_table_id] = {
			'max_fields_length' : 0,
			'global_fields_counter' : 0,
			'used_columns_list' : [],
			'is_filter_applied' : false
		};

		var filter_container_id = global_table_id + '_advance_filter',
			form_block_id = filter_container_id + '_form',
			filter_block_html = '';
		// set global_fields_counter to 1
		global_variables_obj[global_table_id]['global_fields_counter'] = 1;

		filter_block_html += '<div id="' + filter_container_id + '" class="advance_filters_container" style="display: none;">';
		filter_block_html += '<h4><i class="fa fa-arrow-circle-o-right"> </i> Advance Filter</h4>';
		filter_block_html += '<div id="' + form_block_id + '" class="advance_filters_wrapper">';
		filter_block_html += '<div class="form-group filters_form_container form-horizontal col-md-7">';
		filter_block_html += createFilterFieldsHtml(global_variables_obj[global_table_id]['global_fields_counter']);
		filter_block_html += '</div>';
		filter_block_html += '<div class="col-md-5">';
		filter_block_html += '<div class="applied_filter_container">';
		filter_block_html += '<h4>' + no_filters_txt + '</h4>';
		filter_block_html += '<table class="selected_filters_list hide table table-bordered">\
							  <thead><tr><th>Field</th> \
							  <th>Condition</th><th>Value</th> \
							  <th>Action</th></tr></thead> \
							  <tbody></tbody></table></div>';
		filter_block_html += '<div class="filter_btn_container">';
        filter_block_html += '<button type="button" class="pull-right btn btn-xs btn-danger filter_cancel_btn" \
        					  id="' + filter_container_id + '_cancel"> Cancel </button>';
        filter_block_html += '<button type="button" class="pull-right btn btn-xs btn-success hide \
        					  filter_submit_btn" onclick="applyDatatableAdvanceFilter(this);" \
        					  id="' + filter_container_id + '_submit"> Filter </button>';
		filter_block_html += '</div><div class="clearfix"></div></div><div class="clearfix"></div></div>';
		filter_block_html += '<div class="divide-20"></div></div>';

		$(filter_block_html).insertBefore($('#' + global_table_id).closest('.box')[0]);
		// Fade in the form
		$('#' + form_block_id + ' .form-horizontal .filter_container:last-child').fadeIn('slow');
	}
}


/**
 * This function add new selectbox & input for filtering option
 * @method addNewFilters
 */
function addNewFilters() {

	var form_id = global_table_id + '_advance_filter_form',
		select_id_prefix = global_table_id + '_advance_filter_select_',
		input_id_prefix = global_table_id + '_advance_filter_input_',
		select_boxes = $('#' + form_id + ' select[id*="' + select_id_prefix + '"]'),
		last_selectbox = $('#' + form_id + ' .form-horizontal select[id^="' + select_id_prefix + '"]').last(),
		last_id_counter_val = global_variables_obj[global_table_id]['global_fields_counter'],
		prev_selectbox_val = $.trim($('#' + select_id_prefix +''+last_id_counter_val).val()),
		prev_inputbox_val = $.trim($('#' + input_id_prefix +''+last_id_counter_val).val());

	if (prev_selectbox_val && prev_inputbox_val) {
		// Add used column to global list
		global_variables_obj[global_table_id]['used_columns_list'].push($('#' + select_id_prefix +''+last_id_counter_val).val());
		var field_html = createFilterFieldsHtml(global_variables_obj[global_table_id]['global_fields_counter'] += 1),
			nth_selector_txt = '';

		if ($('#' + form_id + ' .form-horizontal .filter_container').length > 1) {
			nth_selector_txt = ':last-child';
		}

		$('#' + form_id + ' .form-horizontal .filter_container'+ nth_selector_txt).fadeOut('slow', function() {
			var base_selector = '#' + form_id + ' .form-horizontal .filter_container'+ nth_selector_txt,
				selectbox_val = $(base_selector + ' select[id*="_select_"]').val(),
				selectbox_text = $(base_selector + ' select[id*="_select_"] option:selected').text(),
				conditionbox_val = $(base_selector + ' select[id*="_condition_"]').val(),
				conditionbox_text = $(base_selector + ' select[id*="_condition_"] option:selected').text(),
				search_val = $(base_selector + ' input[id*="_input_"]').val(),
				selected_filter = '<tr class="text-primary" data-column="' + selectbox_val + '" \
								  data-condition="' + conditionbox_val + '" data-searchval="' + search_val + '"\
								  > <td> ' + selectbox_text + ' </td><td>\
								  ' + conditionbox_text + '</td>' + '<td>' + search_val + '</td> \
								  <td><i class="fa fa-times text-danger single_filter_remove_btn" \
								  title="Remove Filter"></i></td></tr>';

			// hide h4
			if(!$('#' + form_id + ' .applied_filter_container h4').hasClass('hide')) {
				$('#' + form_id + ' .applied_filter_container h4').addClass('hide');
			}
			
			$('#' + form_id + ' .applied_filter_container table.selected_filters_list tbody').append(selected_filter);

			if($('#' + form_id + ' .applied_filter_container table.selected_filters_list').hasClass('hide')) {
				$('#' + form_id + ' .applied_filter_container table.selected_filters_list').removeClass('hide');
			}

			if ($('#' + form_id + ' .filter_btn_container button.btn-success').hasClass('hide')) {
				$('#' + form_id + ' .filter_btn_container button.btn-success').removeClass('hide');
			}

			if (global_variables_obj[global_table_id]['used_columns_list'].length < global_variables_obj[global_table_id]['max_fields_length']) {
				if ($('#' + global_table_id + '_advance_filter_select_' + global_variables_obj[global_table_id]['global_fields_counter']).length == 0) {
					$('#' + form_id + ' .form-horizontal').append(field_html);
					$('#' + form_id + ' .form-horizontal .filter_container:last-child').fadeIn('slow');
				}
			}
		});

	} else {
		bootbox.alert('Please select the search criteria for the preceding field first.');
	}
}


/**
 * This function generate HTML of filter fields(select & input) html
 * @method createFilterFieldsHtml
 * @return field_block_html
 */
function createFilterFieldsHtml(counter) {

	var form_id = global_table_id + '_advance_filter_form',
		select_id_prefix = global_table_id+'_advance_filter_select_',
		total_column_selectbox = $('select[id^="'+select_id_prefix+'"]').length,
		filter_container_id = global_table_id + '_advance_filter',
		selectbox_id = filter_container_id + '_select_' + String(counter),
		inputbox_id = filter_container_id + '_input_' + String(counter),
		conditionbox_id = filter_container_id + '_condition_' + String(counter),
		field_block_html = '';

	if (global_variables_obj[global_table_id]['max_fields_length'] && global_variables_obj[global_table_id]['max_fields_length'] <= total_column_selectbox + 1) {
		$('#' + form_id + ' .add_filter_btn_container button.btn-success').addClass('hide');
	}


	field_block_html += '<div class="filter_container" style="display: none;"><div class="form-group">';
	field_block_html += '<label class="col-sm-3 control-label">Select Column</label>';
	field_block_html += '<div class="col-sm-8">';
	field_block_html += '<select class="form-control columns_selectbox" id="' + selectbox_id + '">';
	field_block_html += '<option value="">Select Column</option>';

	for (var i=0;i<global_grid_headers.length;i++) {
		var columns_name = $.trim(global_grid_headers[i]['mData']),
			columns_title = $.trim(global_grid_headers[i]['sTitle']),
			fetched_type = global_grid_headers[i]['sType'],
			columnType = 'string';

		if (fetched_type) {
			columnType = fetched_type;
		}

		// If column used in before
		if (global_variables_obj[global_table_id]['used_columns_list'].indexOf(columns_name) > -1) {
			continue;
		}

		// If columns_title is blank then set it to columns_name name
		if (!columns_title) {
			// Make columns_name to title case
			try {
				columns_title = columns_name[0].toUpperCase() + columns_name.slice(1);
			} catch(e) {
				columns_title = columns_name;
			}
		}

		// If 'columns_name' is any timestamp column then skip it
		if (excluded_columns.indexOf(columns_name) > -1 || columns_name.indexOf('time') > -1) {
			continue;
		}

		// If column contains hide class
		if (global_grid_headers[i].hasOwnProperty('sClass') && global_grid_headers[i]['sClass'].indexOf('hide') > -1) {
			continue;
		}

		// If column is not searchable
		if (global_grid_headers[i].hasOwnProperty('bSearchable') && global_grid_headers[i]['bSearchable']) {
			continue;
		}

		if (counter == 1) {
			global_variables_obj[global_table_id]['max_fields_length']++;
		}

		field_block_html += '<option value="' + columns_name + '" data-cType="' + columnType + '">' + columns_title + '</option>';
	}
	
	field_block_html += '</select></div></div>';
	var temp_var = condition_block_html;

	temp_var = temp_var.replace('{}', conditionbox_id);

	field_block_html += temp_var;
	field_block_html += '<div class="form-group">';
	field_block_html += '<label class="col-sm-3 control-label">Enter Values</label>';
	field_block_html += '<div class="col-sm-8">';
	field_block_html += '<input type="text" class="form-control" \
						 placeholder="Enter comma seperated multiple values." \
						 id="' + inputbox_id + '" name="' + inputbox_id + '"/>';
	field_block_html += '</div></div>';
	field_block_html += '<a href="javascript:;" class="add_filter_btn_container" onclick="addNewFilters();"> \
						 <i class="fa fa-arrow-circle-o-right text-success"></i></a></div>';


	return field_block_html;
}


/**
 * This function called when 'Filter' button of advance filters form clicked
 * @method applyDatatableAdvanceFilter
 * @param current_object {Object}, It contains current object instance
 */
function applyDatatableAdvanceFilter(current_object) {
	var form_id = global_table_id + '_advance_filter_form',
		button_id = current_object.id,
		common_id = button_id ? button_id.split('_submit')[0] : '',
		download_btn_id = global_table_id + '_download_btn';
	
	if (!common_id) {
		return;
	}

	var total_select_box = $('select[id^="' + common_id + '_select_"]'),
		total_condition_box = $('select[id^="' + common_id + '_condition_"]'),
		total_input_box = $('input[id^="' + common_id + '_input_"]'),
		api_main_url = global_api_url ? global_api_url.split('advance_filter')[0] : '',
		filtering_obj = {},
		tr_list = $('#' + form_id + ' table.selected_filters_list tbody tr'),
		filters_list = [];

	if (tr_list.length > 0) {
		for(var i=0;i<tr_list.length;i++) {
			var filter_obj = {
				"column" : $.trim($(tr_list[i]).data("column")),
				"condition" : $.trim($(tr_list[i]).data("condition")),
				"values" : $.trim(String($(tr_list[i]).data("searchval")).toLowerCase()).split(',')

			}
			filters_list.push(filter_obj)
		}
		var updated_api_url = '',
			stringified_filters = JSON.stringify(filters_list);
		// Add advance filters criteria with API url as GET param
		if (api_main_url.indexOf('?') > -1) {
			updated_api_url = api_main_url + '&advance_filter='+stringified_filters;
		} else {
			updated_api_url = api_main_url + '?advance_filter='+stringified_filters;
		}

		// Update URL in anchor tag 'data_url' attribute(Special case handled for single performance page)
		if (typeof nocout_getPerfTabDomId != 'undefined' && typeof live_data_tab != 'undefined') {
	        var active_tab_obj = nocout_getPerfTabDomId(),
	            active_dom_id = active_tab_obj.active_dom_id;
	            
	        if ($('#' + active_dom_id + '_tab').length) {
	            $('#' + active_dom_id + '_tab').attr('data_url', updated_api_url);
	        }
	    } else {
			$('.nav-tabs li.active a').attr('data_url', updated_api_url);
	    }

		global_variables_obj[global_table_id]['is_filter_applied'] = true;

		dataTableInstance.createDataTable(
            global_table_id,
			global_grid_headers,
            updated_api_url,
            global_destroy,
		    global_current_table_title,
		    global_app_name,
		    global_header_class_name,
		    global_data_class_name,
		    global_header_extra_param,
		    global_data_extra_param,
		    global_excluded_columns,
		    stringified_filters
        );
	}
}

/**
 * This event triggers when Columns dropdown value changed
 * @event delegate('change')
 */
$('#content').delegate('.columns_selectbox', 'change', function(e) {
	var column_type = 'string',
		dom_id = $(this)[0].id,
		splitted_id = dom_id.split('_select_'),
		condition_dom_id = splitted_id.join('_condition_');

	try {
		column_type = $(this).find(":selected").data('ctype');
	} catch(e) {
		// console.error(e);
	}

	// Remove extra options from selectbox
	$('#' + condition_dom_id + ' option').not('[value*="equals"]').remove();

	var extra_columns = '';

	if (number_columns.indexOf(column_type) > -1) {
		extra_columns = number_column_options;
	} else {
		extra_columns = string_column_options;
	}

	$('#' + condition_dom_id).append(extra_columns);
});

$('#content').delegate('i.single_filter_remove_btn', 'click', function(e) {
	
	var form_id = global_table_id + '_advance_filter_form';

	// Remaining tr length
	var remaining_tr = $('#' + form_id + ' .applied_filter_container table.selected_filters_list tbody tr').length;

	// If not filters exists then update heading text & hide filter buttons
	if (remaining_tr - 1 == 0) {
		$('.remove_advance_filters_btn').trigger('click', true);
	} else {
		var column_name = $.trim($(this).closest('tr').data('column')),
			column_title = $.trim($($(this).closest('tr').children()[0]).html()),
			option_html = '',
			column_obj = global_grid_headers.filter(function(column) {
				return column.mData == column_name
			}),
			column_type = column_obj['sType'] ? column_obj['sType'] : 'string';

		if (column_name && column_title) {
			// Add the removed column to selectbox
			option_html = '<option value="'+column_name+'" data-ctype="'+ column_type +'">'+column_title+'</option>';		
			$('#' + form_id + ' .filter_container:last-child .columns_selectbox').append(option_html);
		}

		// pop column_name from used_columns_list list
		global_variables_obj[global_table_id]['used_columns_list'].splice(global_variables_obj[global_table_id]['used_columns_list'].indexOf(column_name), 1);
		// Remove tr
		$(this).closest('tr').remove();
	}
});


$('#content').delegate('.show_advance_filters_btn', 'click', function(e) {
	var button_id = $(this)[0].id,
		splitted_id = button_id.split('_advance_filter_btn'),
		filter_container_id = splitted_id[0] + '_advance_filter';

	$('#' + filter_container_id).slideDown('slow');
});

$('#content').delegate('.filter_cancel_btn', 'click', function(e) {
	$('.advance_filters_container').slideUp('slow');
});


$('#content').delegate('.remove_advance_filters_btn', 'click', function(e, is_single) {

	var api_main_url = global_api_url ? global_api_url.split('advance_filter')[0] : '',
		form_id = global_table_id + '_advance_filter_form',
		tr_list = $('#' + form_id + ' table.selected_filters_list tbody tr'),
		download_btn_id = global_table_id + '_download_btn';

	// Add advance filters criteria with API url as GET param
	if (api_main_url.indexOf('?') > -1) {
		updated_api_url = api_main_url + '&advance_filter=';
	} else {
		updated_api_url = api_main_url + '?advance_filter=';
	}

	for (var i=0;i<tr_list.length;i++) {
		var column_name = $.trim($(tr_list[i]).data('column')),
			column_obj = global_grid_headers.filter(function(column) {
				return column.mData == column_name;
			}),
			column_type = column_obj['sType'] ? column_obj['sType'] : 'string',
			column_title = $.trim($(tr_list[i].children[0]).html());

		if (column_name && column_title) {
			// Add the removed column to selectbox
			var option_html = '<option value="'+column_name+'" data-ctype="'+ column_type +'">'+column_title+'</option>';		
			$('#' + form_id + ' .filter_container:last-child .columns_selectbox').append(option_html);
		}
	}


	$('#' + form_id + ' table.selected_filters_list tbody').html('');

	// Update download button attribute for advance filters
	$('#' + download_btn_id).attr('advance_filter', '');

	// Update URL in anchor tag 'data_url' attribute(Special case handled for single performance page)
	if (typeof nocout_getPerfTabDomId != 'undefined' && typeof live_data_tab != 'undefined') {
        var active_tab_obj = nocout_getPerfTabDomId(),
            active_dom_id = active_tab_obj.active_dom_id;

        if ($('#' + active_dom_id + '_tab').length) {
            $('#' + active_dom_id + '_tab').attr('data_url', updated_api_url);
        }
    } else {
		$('.nav-tabs li.active a').attr('data_url', updated_api_url);
    }

	global_variables_obj[global_table_id]['used_columns_list'] = [];
	global_variables_obj[global_table_id]['is_filter_applied'] = false;

    // Update Heading txt
	$('#' + form_id + ' .applied_filter_container h4').html(no_filters_txt);

	// Show h4
	if($('#' + form_id + ' .applied_filter_container h4').hasClass('hide')) {
		$('#' + form_id + ' .applied_filter_container h4').removeClass('hide');
	}

	// Hide buttons
	if (!$('#' + form_id + ' .filter_btn_container button.btn-success').hasClass('hide')) {
		$('#' + form_id + ' .filter_btn_container button.btn-success').addClass('hide');
	}

	if(!$('#' + form_id + ' .applied_filter_container table.selected_filters_list').hasClass('hide')) {
		$('#' + form_id + ' .applied_filter_container table.selected_filters_list').addClass('hide');
	}

	dataTableInstance.createDataTable(
        global_table_id,
		global_grid_headers,
        updated_api_url,
        global_destroy,
	    global_current_table_title,
	    global_app_name,
	    global_header_class_name,
	    global_data_class_name,
	    global_header_extra_param,
	    global_data_extra_param,
	    global_excluded_columns
    );

});