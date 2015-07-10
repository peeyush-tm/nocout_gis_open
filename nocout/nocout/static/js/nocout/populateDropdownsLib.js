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