/**
 * This function triggers which delete icon for any row is clicked & performs softdelete functionality
 * @method get_soft_delete_form
 * @param content {JSON Object} Contains data object sent from server
 */

function get_soft_delete_form(content) {
    // soft_delete_html: contains html for soft delete form
    var soft_delete_html = "";

    if (!(typeof content.result.data.objects.childs === 'undefined') && !(Object.keys(content.result.data.objects.childs).length === 0)) {
        soft_delete_html = '<h5 class="text-warning">This '+$.trim(content.result.data.objects.form_title)+' (' + content.result.data.objects.name + ') is parent of following '+$.trim(content.result.data.objects.form_title)+'s :</h5>';
        for (var i = 0, l = content.result.data.objects.childs.length; i < l; i++) {
            soft_delete_html += '<span class="text-warning">' + (i + 1) + ' : ' + content.result.data.objects.childs[i].value + ' </span><br />';
        }
        if (!(typeof content.result.data.objects.eligible === 'undefined')) {
            soft_delete_html += '<h5 class="text-danger">Please first choose future parent of these '+$.trim(content.result.data.objects.form_title)+' from below choices:</h5>';
            soft_delete_html += '<input type="hidden" id="id_'+$.trim(content.result.data.objects.form_type)+'" name="'+$.trim(content.result.data.objects.form_type)+'" value="' + content.result.data.objects.id + '" />';
            soft_delete_html += '<select class="form-control" id="id_parent" name="parent">';
            soft_delete_html += '<option value="">Select '+$.trim(content.result.data.objects.form_title)+'</option>';
            for (var i = 0, l = content.result.data.objects.eligible.length; i < l; i++) {
                soft_delete_html += '<option value="' + content.result.data.objects.eligible[i].key + '">' + content.result.data.objects.eligible[i].value + '</option>';
            }
            soft_delete_html += '</select>';
        }
    }
    else {
        soft_delete_html = '<h5 class="text-warning">This '+$.trim(content.result.data.objects.form_title)+' (' + content.result.data.objects.name + ') is not associated with any other '+$.trim(content.result.data.objects.form_title)+'. So click on Yes! if you want to delete it.</h5>';
        soft_delete_html += '<input type="hidden" id="id_'+$.trim(content.result.data.objects.form_type)+'" name="'+$.trim(content.result.data.objects.form_type)+'" value="' + content.result.data.objects.id + '" />';
        soft_delete_html += '<input type="hidden" id="id_parent" name="parent" value="" />'
    }
    var title = "Delete "+$.trim(content.result.data.objects.form_title);
    var upperCaseTitle = title.toUpperCase();
    bootbox.dialog({
        message: soft_delete_html,
        title: "<span class='text-danger'><i class='fa fa-times'></i> "+upperCaseTitle+"</span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {

                    /*Check that from where the softdelete is called*/
                    if($.trim(content.result.data.objects.form_type) == 'device') {
                        
                        Dajaxice.device.device_soft_delete(show_response_message, {'device_id': $('#id_device').val(),'new_parent_id': $('#id_parent').val()});

                    } else if($.trim(content.result.data.objects.form_type) == 'device_group') {

                        Dajaxice.device_group.device_group_soft_delete(show_response_message, {'device_group_id': $('#id_device_group').val(),'new_parent_id': $('#id_parent').val()});

                    } else if($.trim(content.result.data.objects.form_type) == 'user_group') {

                        Dajaxice.user_group.user_group_soft_delete(show_response_message, {'user_group_id': $('#id_user_group').val(),'new_parent_id': $('#id_parent').val()});
                    
                    } else if($.trim(content.result.data.objects.form_type) == 'user') {

                        Dajaxice.user_profile.user_soft_delete(show_response_message, {'user_id': $('#id_user').val(),'new_parent_id': $('#id_parent').val()});
                    }
                }
            },
            danger: {
                label: "No!",
                className: "btn-danger",
                callback: function () {
                    bootbox.alert("Ok! You choose to not delete this device right now.", function () {
                        $(".bootbox").modal("hide");
                    });
                }
            }
        }
    });
}

/**
 * This function show the response message from the server in bootbox alert box
 * @param responseResult {JSON Object} It contains the json object passed from the server
 */
function show_response_message(responseResult) {

    bootbox.alert(responseResult.result.message);
}

function add_device(device_id) {
    bootbox.dialog({
        message: "Add device "+device_id+" for monitoring.",
        title: "<span class='text-danger'><i class='fa fa-times'></i> Add device to nms core. </span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                    Dajaxice.device.add_device_to_nms_core(device_add_message, {'device_id': device_id});
                }
            },
            danger: {
                label: "No!",
                className: "btn-danger",
                callback: function () {
                    bootbox.alert("Ok! You choose to not add this device right now for monitoring.", function () {
                        $(".bootbox").modal("hide");
                    });
                }
            }
        }
    });
}

function device_add_message(responseResult) {

    bootbox.alert(responseResult.result.message);
}