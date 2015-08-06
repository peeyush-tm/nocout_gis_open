/**
 * This file handle the advance filtering feature for datatables.
 */
// Global Variables
var existing_pagesettings_html = '<div class="clearfix"></div>',
	non_filtering_columns = [
		'action',
		'actions',
		'nms_action',
		'nms_actions'
	],
	add_filter_btn_html = '<div class="form-group add_filter_btn_contianer"> \
						   <div class="col-md-12 pull-right" align="right"> \
						   <a href="javascript:;" title="Add Filter Block" onclick="addNewFilters();"> \
						   <i class="fa fa-plus"></i></a></div></div>',
	condition_block_html = '<div class="filters_remove_container"> \
							<h4 title="Remove Filter Block" pk="<1>"><i class="fa fa-times text-danger"></i></h4> \
							</div><hr/><div class="form-group"> \
							<label class="col-sm-3 control-label">Select Condition</label> \
							<div class="col-sm-8"> \
							<select class="form-control condition_box" id="{}"> \
							<option value="and">AND</option> \
							<option value="or">OR</option> \
							</select></div></div><hr/>',
	timestamp_columns = [
		'added_on',
		'updated_on',
		'sys_timestamp'
	],
	global_table_id = '',
	global_grid_headers = '',
	max_fields_length = 0,
	global_fields_counter = 0,
	suggestions_api_url = '/advance_filters_auto_suggestions/?app_name={0}&class_name={1}&column={2}&get_params={3}&search_txt={4}';

/**
 * This function creates advance filters HTML as per the given headers
 * @method nocout_createAdvanceFilter
 * @param headers {Array}, It contains the listing headers array.
 */
function nocout_createAdvanceFilter (headers, tableId) {
	if (!headers || $('#' + tableId + '_advance_filter').length > 0) {
		return true;
	}
	var current_html = $.trim($('.page_settings_container').html());

	if (current_html == existing_pagesettings_html) {
		global_table_id = tableId;
		global_grid_headers = headers;
		var filter_container_id = global_table_id + '_advance_filter',
			form_block_id = filter_container_id + '_form',
			filter_block_html = '';
		// set global_fields_counter to 1
		global_fields_counter = 1;

		filter_block_html += '<div id="' + filter_container_id + '">';
		filter_block_html += '<h4><i class="fa fa-arrow-circle-o-right"> </i> Advance Filter</h4>';
		filter_block_html += '<div id="' + form_block_id + '" class="col-md-9 col-md-offset-1">';
		filter_block_html += '<div class="form-group form-horizontal col-md-12" style="max-height: 300px;overflow: auto;">';
		filter_block_html += add_filter_btn_html;
		filter_block_html += createFilterFieldsHtml(global_fields_counter);
		filter_block_html += '</div></div>';
		filter_block_html += '<div class="col-md-8 col-md-offset-1">';
        filter_block_html += '<button type="button" class="pull-right btn btn-sm btn-danger filter_cancel_btn" \
        					  style="margin-left:10px;" id="' + filter_container_id + '_cancel"> Cancel </button>';
        filter_block_html += '<button type="button" class="pull-right btn btn-sm btn-success \
        					  filter_submit_btn" onclick="applyDatatableAdvanceFilter(this);" \
        					  id="' + filter_container_id + '_submit"> Filter </button>';
		filter_block_html += '</div><div class="clearfix"></div></div>';
		filter_block_html += '<div class="divide-20"></div>';

		$(filter_block_html).insertBefore($('#' + tableId).closest('.box')[0]);

		// Initialize filter value select2
		initFiltersSelect2(global_fields_counter);
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
		last_id_counter_val = last_selectbox[0].id.split('_select_')[1],
		prev_selectbox_val = $.trim($('#' + select_id_prefix +''+last_id_counter_val).val()),
		prev_inputbox_val = $.trim($('#' + input_id_prefix +''+last_id_counter_val).val());

	// if (prev_selectbox_val && prev_inputbox_val) {
		var field_html = createFilterFieldsHtml(global_fields_counter += 1);
		$('#' + form_id + ' .form-horizontal').append(field_html);//.insertBefore($('.add_filter_btn_contianer'));

		// Initialize filter value select2
		initFiltersSelect2(global_fields_counter);

	// } else {
	// 	bootbox.alert('Please select the search criteria for the preceding field first.');
	// }
}


/**
 * This function generate HTML of filter fields(select & input) html
 * @method createFilterFieldsHtml
 * @return field_block_html
 */
function createFilterFieldsHtml(counter) {

	var select_id_prefix = global_table_id+'_advance_filter_select_',
		total_column_selectbox = $('select[id^="'+select_id_prefix+'"]').length,
		filter_container_id = global_table_id + '_advance_filter',
		selectbox_id = filter_container_id + '_select_' + String(counter),
		inputbox_id = filter_container_id + '_input_' + String(counter),
		field_block_html = '';

	if (max_fields_length <= total_column_selectbox + 1) {
		$('.add_filter_btn_contianer').addClass('hide');
	}

	if (counter > 1) {
		field_block_html += '<hr/>';
	}

	field_block_html += '<div class="form-group">';
	field_block_html += '<label class="col-sm-3 control-label">Select Column</label>';
	field_block_html += '<div class="col-sm-8">';
	field_block_html += '<select class="form-control" id="' + selectbox_id + '">';
	field_block_html += '<option value="">Select Column</option>';

	for (var i=0;i<global_grid_headers.length;i++) {
		var columns_name = $.trim(global_grid_headers[i]['mData']),
			columns_title = $.trim(global_grid_headers[i]['sTitle']);

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
		if (timestamp_columns.indexOf(columns_name) > -1 || columns_name.indexOf('time') > -1) {
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

		// If column exists in 'non_filtering_columns'
		if (non_filtering_columns.indexOf(columns_name.toLowerCase()) > -1) {
			continue;
		}

		if (counter == 1) {
			max_fields_length++;
		}

		field_block_html += '<option value="' + columns_name + '">' + columns_title + '</option>';
	}
	
	field_block_html += '</select></div></div>';
	field_block_html += '<div class="form-group">';
	field_block_html += '<label class="col-sm-3 control-label">Enter Value</label>';
	field_block_html += '<div class="col-sm-8">';
	field_block_html += '<input type="hidden" style="width:100%;" class="filters_select2" id="' + inputbox_id + '" name="' + inputbox_id + '"/>';
	field_block_html += '</div></div>';


	return field_block_html;
}

/**
 * This function remove the given counter filter block from dom
 * @method removeFilterFieldsHtml
 */
function removeFilterFieldsHtml(counter) {
	if (!counter) {
		return ;
	}

	var filter_container_id = global_table_id + '_advance_filter',
		selectbox_id = filter_container_id + '_select_' + String(counter),
		inputbox_id = filter_container_id + '_input_' + String(counter),
		condition_block_id = filter_container_id + '_condition_' + String(counter);

	// Remove HTML blocks
	$('#' + selectbox_id).closest('.form-group').remove();
	$('#' + inputbox_id).closest('.form-group').remove();
	$('#' + condition_block_id).closest('.form-group').prev('hr').remove();
	$('#' + condition_block_id).closest('.form-group').next('hr').remove();
	$('#' + condition_block_id).closest('.form-group').remove();
	$('h4[pk=' + counter + ']').parent('.filters_remove_container').remove();

	if($('.add_filter_btn_contianer').hasClass('hide')) {
		$('.add_filter_btn_contianer').removeClass('hide');
	}
}

/**
 * This function called when 'Filter' button of advance filters form clicked
 * @method applyDatatableAdvanceFilter
 * @param current_object {Object}, It contains current object instance
 */
function applyDatatableAdvanceFilter(current_object) {
	var button_id = current_object.id,
		common_id = button_id ? button_id.split('_submit')[0] : '';
	
	if (!common_id) {
		return;
	}

	var total_select_box = $('select[id^="' + common_id + '_select_"]'),
		total_condition_box = $('select[id^="' + common_id + '_condition_"]'),
		total_input_box = $('input[id^="' + common_id + '_input_"]'),
		current_tab_url = $('.nav-tabs li.active a').attr('data_url'),
		api_main_url = current_tab_url ? current_tab_url.split('advance_filter')[0] : '',
		filtering_obj = {};
	
	for (var i=0;i<total_select_box.length;i++) {
		var counter_val = total_select_box[i].id.split('_select_')[1],
			columns_name = total_select_box[i].value,
			columns_val = $('#' + common_id + '_input_' + String(counter_val)).val();
	}
}

/**
 * This event triggers when 'Remove Filter Block' icon clicked
 * @event delegate('click')
 */
$('body').delegate('.filters_remove_container h4', 'click', function(e) {
	var counter_val = $(this).attr('pk')
	removeFilterFieldsHtml(counter_val);
});


function initFiltersSelect2(counter) {

	var filter_container_id  = global_table_id + '_advance_filter',
		input_id_prefix = filter_container_id +'_input_';

	$('#' + input_id_prefix +counter).select2({
		multiple: true,
    	minimumInputLength: 2,
    	query: function (query) {
    		var search_txt = query.term,
    			elem_id = this.element[0].id,
    			counter_val = elem_id.split('_input_')[1],
    			selectbox_id = global_table_id +'_advance_filter_select_' + counter_val,
    			data = {results: []},
    			current_tab_id = $('.nav-tabs li.active a').attr('id');
			
			if ($('#' + selectbox_id).length) {
				if ($('#' + selectbox_id).val()) {
					var columns_name = $('#' + selectbox_id).val();
					if (tables_info[current_tab_id]) {
						var app_name = tables_info[current_tab_id].app_name,
							class_name = tables_info[current_tab_id].data_class_name,
							get_params = tables_info[current_tab_id].data_extra_param,
							api_url = suggestions_api_url;

						api_url = api_url.replace('{0}', app_name);
						api_url = api_url.replace('{1}', class_name);
						api_url = api_url.replace('{2}', columns_name);
						api_url = api_url.replace('{3}', get_params);
						api_url = api_url.replace('{4}', search_txt);

						$.ajax({
							url : api_url,
							type : 'GET',
							success : function(response) {
								data['results'] = response['data']
								query.callback(data);
							},
							error : function(err) {
								// console.log(err.statusText);
							}
						});
					}
				} else {
					bootbox.alert('Please select any column first.')
				}
			}
    		query.callback(data);
		}
	});	
}