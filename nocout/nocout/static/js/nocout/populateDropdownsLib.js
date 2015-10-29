/**
 * This library populate child dropdown as per the change in parent dropdown
 * @for populateDropdownsLib
 */

if (typeof parent_class == 'undefined') {
	parent_class = 'form-horizontal';
}

if (typeof change_event_dom_ids == 'undefined') {
	change_event_dom_ids = [];
}

if (typeof element_relation_dict == 'undefined') {
	element_relation_dict = {};
}


/**
 * This event triggers when dropdown for 'change_event_dom_ids' ids list changed
 * @event delegate(For change)
 */
$("." + parent_class).delegate(change_event_dom_ids.join(', '), 'change', function(e) {
    var element_id = $(this)[0].id,
        data_id = $(this).val();

    if (element_id && element_relation_dict['#' + element_id]) {

        var update_items_list = element_relation_dict['#' + element_id].update,
            reset_items_list = element_relation_dict['#' + element_id].reset;

        if (element_relation_dict['#' + element_id]['old_value']) {
            data_id = element_relation_dict['#' + element_id]['old_value'];
            element_relation_dict['#' + element_id]['old_value'] = '';
        }

        // Reset given select2 element
        for( var i=0;i<reset_items_list.length;i++) {
            try {
                $(reset_items_list[i]).select2("val","");
                $(reset_items_list[i]).empty();
            } catch(e) {
                // console.error(e);
            }
        }
        // if 'data_id' is undefined then set it to 0
        data_id = data_id && typeof data_id != 'undefined' && data_id != '' ? data_id : 0;
        // Set given select2 element
        for( var i=0;i<update_items_list.length;i++) {
            var url_name = update_items_list[i]['url_name'] ? update_items_list[i]['url_name'] : "",
                affected_element_id = update_items_list[i]['id'] ? update_items_list[i]['id'] : "",
                existing_value = update_items_list[i]['existing_value'] ? update_items_list[i]['existing_value'] : "";
            if (existing_value) {
                update_items_list[i]['existing_value'] = '';
            }
            // Remove dummy id '123' with actual id
            url_name = url_name.replace('123', data_id);
            // Call function to make ajax call & update element
            makeFormAjaxCall(url_name, affected_element_id, existing_value)
        }
    }
});

/**
 * This function makes ajax call to given url & after formatting API response return it
 * @method makeFormAjaxCall
 * @param api_url {String}, It contains the url of api from which data is to be fetched
 * @param affected_element_id {String}, It contains the dom ID of 
   element whose data is to be updated as per API reponse
 * @param existing_value {Number}, It contains the existing value of given select box
 */
function makeFormAjaxCall(api_url, affected_element_id, existing_value) {

    if (!api_url) {
        return "";
    }

    var complete_url = getCompleteUrl(api_url);

    // Disable the selector
    $(affected_element_id).select2('disable');
    
    // Make ajax call to given url
    $.ajax({
        url : complete_url,
        type : "GET",
        success : function(response) {
            var result = "";
            // Type check of response
            if (typeof response == 'string') {
                result = JSON.parse(response);
            } else {
                result = response;
            }
            var option_html = '<option value="0">Select</option>';

            for (var x=0;x<result.length;x++) {
                var existing_keys = Object.keys(result[x]).filter(function(items) {return items != 'id'}),
                    alias_key = existing_keys.indexOf('alias') > -1 ? 'alias' : existing_keys[0],
                    selected_txt = '';

                if (existing_value && existing_value == result[x].id) {
                    selected_txt = 'selected="selected"';
                }

                option_html += '<option value="' + result[x].id + '" ' + selected_txt + '>' + result[x][alias_key] + '</option>';
            }
            // Update select box HTML
            $(affected_element_id).html(option_html);
            try {
                $(affected_element_id).select2('val', existing_value);
            } catch(e) {
                // console.error(e);
            }

            return true;
        },
        error : function(err) {
            // console.log(err.statusText);
            return true;
        },
        complete : function() {
            // Enable the selector
            $(affected_element_id).select2('enable');
        }
    });
}


/**
 * This function select the given thematics for user
 * @method updateThematicSelection
 * @param tab_id {String}, It contains the dom id of listing
 * @param current_checkbox {Object}, It contains the current changed checkbox object
 * @param device_type {String}, It contains the device type of current thematics
 */
function updateThematicSelection(tab_id, current_checkbox, device_type) {


    var checked_flag = false;
    if ($(current_checkbox).prop('checked')) {
        $(current_checkbox).prop('checked', false);
        checked_flag = true;
    }

     /*Check Device Type */
    var check_device_type = $('#'+tab_id+' .check_class:checked[data-deviceType="'+device_type+'"]');

   /*More than one device type checked */
    if(check_device_type.length > 0) {
        $('#'+tab_id+' .check_class:checked[data-deviceType="'+device_type+'"]').prop('checked', false);
        $('#'+tab_id+' .check_class:checked[data-deviceType="'+device_type+'"]').removeAttr('checked');
    }

    if (checked_flag) {
        $(current_checkbox).prop('checked', true);
        checked_flag = false;
    }

    if (current_checkbox.checked) {
        $.ajax({
            url:thematic_api_url,
            data:{ 'threshold_template_id': current_checkbox.value },
            dataType:"json",
            success:function(result){
                if(result.success){
                    dialog_box_message= "Service Thematic Setting (0) is assigned to User: (1)".replace('(0)', result.data.objects.thematic_setting_name)
                    dialog_box_message= dialog_box_message.replace('(1)', result.data.objects.username);
                    bootbox.dialog({
                        message:dialog_box_message,
                        title: "<span class='text-sucess'><i class='fa fa-times'></i>Confirmation</span>",
                        buttons: {
                            success: {
                                label: "OK",
                                className: "btn-success",
                                callback: function () {
                                    $(".bootbox").modal("hide");
                                }
                            }
                        }
                    });
                }
            }
        });//ajax ends
    } else {
        bootbox.dialog({
            message:"You can not Uncheck the Selected Settings, Please Select the other setting.",
            title: "<span class='text-sucess'><i class='fa fa-times'></i>Confirmation</span>",
            buttons: {
                success: {
                    label: "OK",
                    className: "btn-success",
                    callback: function () {
                        $(".bootbox").modal("hide");
                    }
                }
            }
        });
        $(current_checkbox).prop('checked', true);
    }
}


/**
 * This function formats the permissions select2 diplay/selected contents
 * @method format_permissions_widget
 * @param result {Object}, It contains the single select2 value object
 * @return return_txt {String}, It contains the HTML formatted string
 */
function format_permissions_widget(result) {

    if (!result || !result['text']) {
        return '';
    }

    var txt_class = '',
        icon_class = '',
        return_txt = result.text;

    if (result.text.indexOf('- View') > -1) {
        txt_class = 'text-primary';
        icon_class = 'fa-eye';
    } else if (result.text.indexOf('- Edit') > -1) {
        txt_class = 'text-warning';
        icon_class = 'fa-edit';
    } else if (result.text.indexOf('- Delete') > -1) {
        txt_class = 'text-danger';
        icon_class = 'fa-times';
    } else if (result.text.indexOf('- Add') > -1) {
        txt_class = 'text-success';
        icon_class = 'fa-plus';
    } else if (result.text.indexOf('- Sync') > -1) {
        txt_class = 'text-success';
        icon_class = 'fa-refresh';
    }

    return_txt = '<i class="fa ' + icon_class +  ' ' + txt_class + '"></i> ' + result.text;

    return return_txt;
}