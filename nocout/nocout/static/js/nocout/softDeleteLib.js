/**
 * This function triggers which delete icon for any row is clicked & performs softdelete functionality
 * @method get_soft_delete_form
 * @param content {JSON Object} Contains data object sent from server
 */


// soft deletion of objects
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
// show message for soft deletion success/failure
function show_response_message(responseResult) {
    bootbox.alert(responseResult.result.message);
}


// add device to monitoring core
function add_device(device_id) {
    bootbox.dialog({
        message: "Add device for monitoring.",
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


// show message for device addition success/failure
function device_add_message(responseResult) {
    bootbox.alert(responseResult.result.message);
}


// sync devices with monitoring core
function sync_devices(device_id) {
    bootbox.dialog({
        message: "Sync devices for monitoring.",
        title: "<span class='text-danger'><i class='fa fa-times'></i> Sync devices with nms core. </span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                    Dajaxice.device.sync_device_with_nms_core(sync_devices_message, {'device_id': device_id});
                }
            },
            danger: {
                label: "No!",
                className: "btn-danger",
                callback: function () {
                    bootbox.alert("Ok! You choose to not sync devices right now for monitoring.", function () {
                        $(".bootbox").modal("hide");
                    });
                }
            }
        }
    });
}


// show message for device sync addition success/failure
function sync_devices_message(responseResult) {
    bootbox.alert(responseResult.result.message);
}


// add service to nms core
function get_service_add_form(content) {
    var service_add_html = "";

    if (content.result.data.objects.is_added == 1){
        if (content.result.data.objects.master_site == "master_UA") {
            if (!(typeof content.result.data.objects.services === 'undefined') && !(Object.keys(content.result.data.objects.services).length === 0)) {

                // display port select menu
                service_add_html += '<h5 class="text-warning">You can add service for device ' + '"' + content.result.data.objects.device_alias + '" </h5>';
                service_add_html += '<input type="hidden" id="device_id" value="' + content.result.data.objects.device_id + '" />';

                // service display
                if (!(typeof content.result.data.objects.services === 'undefined')) {
                    service_add_html += '<label class="control-label"><h5 class="text-warning">Services:</h5></label>';
                    for (var i = 0, l = content.result.data.objects.services.length; i < l; i++) {
                        service_add_html += '<div class="service">';
                        service_add_html += '<label class="checkbox">';
                        service_add_html += '<input class="uniform" id="svc_' + content.result.data.objects.services[i].key + '" type="checkbox" value="' + content.result.data.objects.services[i].key + '" onchange="show_svc_templates(' + content.result.data.objects.services[i].key + ');">';
                        service_add_html += content.result.data.objects.services[i].value;
                        service_add_html += '</label>';
                        service_add_html += '<div id="svc_params_id_' + content.result.data.objects.services[i].key + '" onchange="show_param_tables(' + content.result.data.objects.services[i].key + ');"></div>';
                        service_add_html += '<div id="svc_params_table_id_' + content.result.data.objects.services[i].key + '"></div>';
                        service_add_html += '<div id="service_data_source_table_id_' + content.result.data.objects.services[i].key + '"></div>';
                        service_add_html += '</div>';
                    }
                    service_add_html += '</div>';
                }
            }
            else {
                service_add_html += '<h5 class="text-warning">There are no service for device ' + '"' + content.result.data.objects.device_alias + '"to monitor. </h5>';
            }
        }
        else{
            service_add_html += content.result.message;
        }
    }
    else{
        service_add_html += content.result.message;
    }

    bootbox.dialog({
        message: service_add_html,
        title: "<span class='text-danger'><i class='fa fa-times'></i> Add service to nms core. </span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                    var service_data = [];
                    $(".service").each(function (index) {
                        var $this = $(this);
                        //console.log($this.text());
                        $this.children(".checkbox").find("input:checked").each(function () {
                            service_temp_id = $(this).prop("value");
                            svc_val = $("#service_" + service_temp_id).val();
                            svc = {"device_id": $("#device_id").val(), "service_id": $(this).prop("value"), "template_id": svc_val};
                            service_data.push(svc);
                        });
                    });
                    Dajaxice.device.add_service(add_services_message, {'service_data': service_data});
                }
            },
            danger: {
                label: "No!",
                className: "btn-danger",
                callback: function () {
                    bootbox.alert("Ok! You choose to not to add service right now for monitoring.", function () {
                        $(".bootbox").modal("hide");
                    });
                }
            }
        }
    });
}


// show message for service addition success/failure
function add_services_message(responseResult) {
    bootbox.alert(responseResult.result.message);
}


// display data sources select menu
function on_service_change(){
    Dajaxice.device.service_data_sources_popup(Dajax.process, {'option': $('#id_services_to_monitor').val()});
}


// display service templates select menu
function show_svc_templates(value) {
    id = "#svc_"+value;
    if ($(id).is(":checked")){
        //console.log($(id).prop("value"));
        Dajaxice.device.get_service_templates(Dajax.process, {'option': value});
    }
    else {
        $("#svc_params_id_"+value+"").empty();
        $("#svc_params_table_id_"+value+"").empty();
        $("#service_data_source_table_id_"+value+"").empty();
    }
}


// display service parameters table
function show_param_tables(value){
    service_value = value;
    para_value = $("#service_"+value).val();
    Dajaxice.device.get_service_para_and_data_source_tables(Dajax.process, {'service_value': service_value, 'para_value': para_value});
}