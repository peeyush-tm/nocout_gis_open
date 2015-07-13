/**
 * This function triggers which delete icon for any row is clicked & performs softdelete functionality
 * @method get_soft_delete_form
 * @param content {JSON Object} Contains data object sent from server
 */


// soft deletion of objects
function get_soft_delete_form(content) {
    // soft_delete_html: contains html for soft delete form
    var soft_delete_html = "";

    if (content) {
        content = content.data.objects
    } else {
        return true;
    }

    if (content.eligible.length > 0 ) {
        soft_delete_html += '<h5 class="text-danger">Please first choose future parent of this \
                             '+$.trim(content.form_title)+' from below choices:</h5> \
                             <input type="hidden" id="id_'+$.trim(content.form_type)+'" \
                             name="'+$.trim(content.form_type)+'" \
                             value="' + content.id + '" /> \
                             <select class="form-control" id="id_parent" name="parent"> \
                             <option value="">Select '+$.trim(content.form_title)+'</option>';

        for (var i = 0, l = content.eligible.length; i < l; i++){
            soft_delete_html += '<option value="' + content.eligible[i].key + '">' + content.eligible[i].value + '</option>';
        }
        soft_delete_html += '</select>';
    } else {
        var display_name = content.ip_address ? content.ip_address : content.name;
        soft_delete_html = '<span class="text-danger">This '+$.trim(content.form_title)+' \
                            (' + display_name + ') is not associated with any other \
                            '+$.trim(content.form_title)+'. <br />Click "Delete" button if you want to delete it.</span> \
                            <input type="hidden" id="id_'+$.trim(content.form_type)+'" \
                            name="'+$.trim(content.form_type)+'" value="' + content.id + '" /> \
                            <input type="hidden" id="id_parent" name="parent" value="" />'
    }

    var title = "Delete "+$.trim(content.form_title),
        upperCaseTitle = title ? title.toUpperCase() : "Device";

    bootbox.dialog({
        message: soft_delete_html,
        title: "<span class='text-danger'><i class='fa fa-times'></i> "+upperCaseTitle+"</span>",
        buttons: {
            success: {
                label: "Delete",
                className: "btn-success",
                callback: function () {
                    var soft_delete_api_url = '';
                    /*Check that from where the softdelete is called*/
                    if($.trim(content.form_type) == 'device') {
                        soft_delete_api_url = device_soft_delete_url.replace('123', $('#id_device').val());
                        if ($('#id_parent').val()) {
                            soft_delete_api_url += $('#id_parent').val() + '/'
                        }
                    } else if($.trim(content.form_type) == 'user') {

                        var parent_id = $('#id_parent').val() ? $('#id_parent').val() : 0;

                        soft_delete_api_url = user_soft_delete_url.replace('123', $('#id_user').val());
                        soft_delete_api_url = soft_delete_api_url.replace('1111111', parent_id);
                        // Dajaxice.user_profile.user_soft_delete(
                        //     show_response_message, 
                        //     {
                        //         'user_id': $('#id_user').val(),
                        //         'new_parent_id': $('#id_parent').val(),
                        //         'datatable_headers':content.datatable_headers,
                        //         'userlistingtable':'/user/userlistingtable/',
                        //         'userarchivelisting':'/user/userarchivedlistingtable/'
                        //     }
                        // );
                    }

                    if (soft_delete_api_url) {
                        // Show loading spinner
                        showSpinner();
                        // Make Ajax Call
                        $.ajax({
                            url : soft_delete_api_url,
                            type : "GET",
                            success : function(response) {
                                var result = "";
                                // Type check of response
                                if (typeof response == 'string') {
                                    result = JSON.parse(response);
                                } else {
                                    result = response;
                                }
                            },
                            error : function(err) {
                                // console.log(err.statusText);
                            },
                            complete : function() {
                                window.location.reload(true);
                            }
                        });
                    }
                }
            },
            danger: {
                label: "Cancel",
                className: "btn-danger",
                callback: function () {
                    $(".bootbox").modal("hide");
                }
            }
        }
    });
}

function add_confirmation(id) {
    bootbox.dialog({
        message: "<span class='text-green'>Are you sure want to add this user ?</span>",
        title: "<span class='text-green'><i class='fa fa-times'></i>Confirmation</span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                    var api_url = '';
                    api_url = restore_user_url.replace('123', id);
                    // Make Ajax Call
                    $.ajax({
                        url : api_url,
                        type : "GET",
                        success : function(response) {
                            var result = "";
                            // Type check of response
                            if (typeof response == 'string') {
                                result = JSON.parse(response);
                            } else {
                                result = response;
                            }
                            show_response_message(result);
                        },
                        error : function(err) {
                            // console.log(err.statusText);
                        }
                    });
                    // Dajaxice.user_profile.user_add(
                    //     show_response_message,
                    //     { 'user_id': id }
                    // )
                }
            },
            danger: {
                label: "No!",
                className: "btn-danger",
                callback: function () {
                    $(".bootbox").modal("hide");
                }
            }

        }
    })
}

function hard_delete_confirmation(id) {
    bootbox.dialog({
        message: "<span class='text-danger'>Permanently delete user from inventory. Can't roll this action back. <br />Are you sure want to add this user ?</span>",
        title: "<span class='text-danger'><i class='fa fa-times'></i> Confirmation </span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                    var api_url = '';
                    api_url = delete_user_url.replace('123', id);
                    // Make Ajax Call
                    $.ajax({
                        url : api_url,
                        type : "GET",
                        success : function(response) {
                            var result = "";
                            // Type check of response
                            if (typeof response == 'string') {
                                result = JSON.parse(response);
                            } else {
                                result = response;
                            }
                            show_response_message(result);
                        },
                        error : function(err) {
                            // console.log(err.statusText);
                        }
                    });
                    // Dajaxice.user_profile.user_hard_delete(
                    //     show_response_message,
                    //     { 'user_id': id }
                    // )
                }
            },
            danger: {
                label: "No!",
                className: "btn-danger",
                callback: function () {
                    $(".bootbox").modal("hide");
                }
            }
        }
    })
}

/**
 * This function show the response message from the server in bootbox alert box
 * @param responseResult {JSON Object} It contains the json object passed from the server
 */
// show message for soft deletion success/failure
function show_response_message(responseResult) {
    window.location.reload(true);
}

// add device to monitoring core
function add_device_form(content) {

    if (content) {
        content = content.data;
    } else {
        return true;
    }

    add_device_html = '<h5 class="">Configure ping service for device:</h5><br /> \
                       <input type="hidden" id="device_id" value="' + content.device_id + '" /> \
                       <div class=""><div class="box border red"> \
                       <div class="box-title"><h4><i class="fa fa-table"></i>Ping Parameters:</h4></div> \
                       <div class="box-body"><table class="table"> \
                       <thead><tr><th>Packets</th><th>Timeout</th><th>Normal Check Interval</th></tr></thead> \
                       <tbody><tr> \
                       <td contenteditable="true" id="packets">'+content.packets+'</td> \
                       <td contenteditable="true" id="timeout">'+content.timeout+'</td> \
                       <td contenteditable="true" id="normal_check_interval">'+content.normal_check_interval+'</td> \
                       </tr></tbody> \
                       <thead><tr><th>Data Source</th><th>Warning</th><th>Critical</th></tr></thead> \
                       <tbody> \
                       <tr><td>RTA</td><td contenteditable="true" id="rta_warning" \>'+content.rta_warning+'</td> \
                       <td contenteditable="true" id="rta_critical">'+content.rta_critical+'</td></tr> \
                       <tr><td>PL</td><td contenteditable="true" id="pl_warning">'+content.pl_warning+'</td> \
                       <td contenteditable="true" id="pl_critical">'+content.pl_critical+'</td></tr> \
                       </tbody></table></div></div></div>';

    bootbox.dialog({
        message: add_device_html,
        title: "<span class='text-danger'><i class='fa fa-plus'></i> Add device to nms core. </span>",
        buttons: {
            success: {
                label: "Add",
                className: "btn-success",
                callback: function () {
                    ping_data = {
                        "rta_warning": parseInt($("#rta_warning").text()),
                        "rta_critical": parseInt($("#rta_critical").text()),
                        "pl_warning": parseInt($("#pl_warning").text()),
                        "pl_critical": parseInt($("#pl_critical").text()),
                        "packets": parseInt($("#packets").text()),
                        "timeout": parseInt($("#timeout").text()),
                        "normal_check_interval": parseInt($("#normal_check_interval").text())
                    };

                    if (add_device_to_nms_url) {
                        var add_to_nms_url = add_device_to_nms_url.replace('123', $("#device_id").val());
                        // Make Ajax Call
                        $.ajax({
                            url : add_to_nms_url+"?ping_data="+encodeURIComponent(JSON.stringify(ping_data)),
                            type : "GET",
                            success : function(response) {
                                var result = "";
                                // Type check of response
                                if (typeof response == 'string') {
                                    result = JSON.parse(response);
                                } else {
                                    result = response;
                                }
                                device_add_message(result);
                            },
                            error : function(err) {
                                // console.log(err.statusText);
                            }
                        });

                        // Dajaxice.device.add_device_to_nms_core(
                        //     device_add_message,
                        //     {
                        //         'device_id': $("#device_id").val(),
                        //         'ping_data': ping_data
                        //     }
                        // );
                    }
                }
            },
            danger: {
                label: "Cancel",
                className: "btn-danger",
                callback: function () {
                    $(".bootbox").modal("hide");
                }
            }
        }
    });
}

// show message for device addition success/failure
function device_add_message(responseResult) {
    bootbox.alert(responseResult.message, function(){
        // reload page after clicking "OK!"
        location = window.location.origin+"/device/#NonOperationalDeviceListing";
        location.reload();
    });
}

// show message for device edit success/failure
function device_edit_message(responseResult) {
    bootbox.alert(responseResult.result.message, function(){
        // reload page after clicking "OK!"
        location = window.location.origin+"/device/#OperationalDeviceListing";
        location.reload();
    });
}

// delete device to monitoring core
function delete_device(device_id) {
    bootbox.dialog({
        message: "Disable and delete device from NMS.",
        title: "<span class='text-danger'><i class='fa fa-times'></i> Disable and delete device from NMS.</span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                    if (delete_device_from_nms_url) {
                        var updated_url = '';
                        updated_url = delete_device_from_nms_url.replace('123', device_id);

                        // Make Ajax Call
                        $.ajax({
                            url : updated_url,
                            type : "GET",
                            success : function(response) {
                                var result = "";
                                // Type check of response
                                if (typeof response == 'string') {
                                    result = JSON.parse(response);
                                } else {
                                    result = response;
                                }
                                device_delete_message(result);
                            },
                            error : function(err) {
                                // console.log(err.statusText);
                            }
                        });
                        // Dajaxice.device.delete_device_from_nms_core(
                        //     device_delete_message,
                        //     {
                        //         'device_id': device_id
                        //     }
                        // );
                    }
                }
            },
            danger: {
                label: "No!",
                className: "btn-danger",
                callback: function () {
                    $(".bootbox").modal("hide");
                }
            }
        }
    });
}

// show message for device deletion success/failure
function device_delete_message(responseResult) {
    bootbox.alert(responseResult.message, function(){
        // reload page after clicking "OK!"
        location = window.location.origin+"/device/#OperationalDeviceListing";
        location.reload();
    });
}

// modify device state (enable or disable)
function modify_device_state(device_id) {
    bootbox.dialog({
        message: "Modify device state.",
        title: "<span class='text-danger'><i class='fa fa-times'></i> Modify device state.</span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                    if (modify_device_state_url) {
                        var updated_url = '';

                        updated_url = modify_device_state_url.replace('123', device_id);
                        // Make Ajax Call
                        $.ajax({
                            url : updated_url,
                            type : "GET",
                            success : function(response) {
                                var result = "";
                                // Type check of response
                                if (typeof response == 'string') {
                                    result = JSON.parse(response);
                                } else {
                                    result = response;
                                }
                                modify_device_state_message(result);
                            },
                            error : function(err) {
                                // console.log(err.statusText);
                            }
                        });
                        // Dajaxice.device.modify_device_state(
                        //     modify_device_state_message,
                        //     {
                        //         'device_id': device_id
                        //     }
                        // );
                    }
                }
            },
            danger: {
                label: "No!",
                className: "btn-danger",
                callback: function () {
                    $(".bootbox").modal("hide");
                }
            }
        }
    });
}

// show message for device state modification success/failure
function modify_device_state_message(responseResult) {
    bootbox.alert(responseResult.message, function(){
        // reload page after clicking "OK!"
        location = window.location.origin+"/device/#DisabledDeviceListing";
        location.reload();
    });
}

// sync devices with monitoring core
function sync_devices(device_id) {
    bootbox.dialog({
        message: "Sync devices for monitoring.",
        title: "<span class='text-danger'><i class='fa fa-times'></i> Sync devices with nms core. </span>",
        buttons: {
            success: {
                label: "Sync",
                className: "btn-success",
                callback: function () {
                    if (sync_device_url) {
                        update_sync_device_url = sync_device_url;
                        if (device_id) {
                            update_sync_device_url = sync_device_url.replace('123', device_id);
                        }
                        // Make Ajax Call
                        $.ajax({
                            url : update_sync_device_url,
                            type : "GET",
                            success : function(response) {
                                var result = "";
                                // Type check of response
                                if (typeof response == 'string') {
                                    result = JSON.parse(response);
                                } else {
                                    result = response;
                                }
                                sync_devices_message(result);
                            },
                            error : function(err) {
                                // console.log(err.statusText);
                            }
                        });
                    }
                    // Dajaxice.device.sync_device_with_nms_core(
                    //     sync_devices_message,
                    //     {
                    //         'device_id': device_id
                    //     }
                    // );
                }
            },
            danger: {
                label: "Cancel",
                className: "btn-danger",
                callback: function () {
                    $(".bootbox").modal("hide");
                }
            }
        }
    });
}

// show message for device sync addition success/failure
function sync_devices_message(responseResult) {
    bootbox.alert(responseResult.message);
}

// remove sync deadlock
function remove_sync_deadlock() {
    bootbox.dialog({
        message: "Remove sync deadlock.",
        title: "<span class='text-danger'><i class='fa fa-times'></i> Remove sync deadlock. </span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                    if (remove_sync_deadlock_url) {
                        var updated_url = remove_sync_deadlock_url;
                        // Make Ajax Call
                        $.ajax({
                            url : updated_url,
                            type : "GET",
                            success : function(response) {
                                var result = "";
                                // Type check of response
                                if (typeof response == 'string') {
                                    result = JSON.parse(response);
                                } else {
                                    result = response;
                                }
                                sync_deadlock_message(result);
                            },
                            error : function(err) {
                                // console.log(err.statusText);
                            }
                        });

                    }
                    // Dajaxice.device.remove_sync_deadlock(sync_deadlock_message);
                }
            },
            danger: {
                label: "No!",
                className: "btn-danger",
                callback: function () {
                    $(".bootbox").modal("hide");
                }
            }
        }
    });
}

// show message for sync deadlock removal
function sync_deadlock_message(responseResult) {
    bootbox.alert(responseResult.message, function() {
        // reload page after clicking "OK!"
        location = window.location.origin + "/device_sync_history/";
        location.reload();
    });
}

// edit services on nms core
function get_service_edit_form(content) {

    if (content) {
        content = content.data.objects
    } else {
        return true;
    }

    var service_edit_html = "<div class='service_edit_container' style='max-height: 400px; overflow: auto;'>";

    if (content.is_added == 1){
        if (content.master_site == "master_UA") {
            if (!(typeof content.services === 'undefined') && !(Object.keys(content.services).length === 0)) {

                // show service information
                service_edit_html += '<h4 class="">Device Info:</h4> \
                                      <dl class="dl-horizontal"> \
                                      <dt>Device</dt><dd>'+content.device_alias+'</dd> \
                                      <dt>Services</dt><dd>';

                for (var i = 0, l = content.services.length; i < l; i++) {
                    service_edit_html += content.services[i].value+', ' ;
                }

                service_edit_html += '</dd></dl> \
                                      <input type="hidden" id="device_id" value="' + content.device_id + '" />';

                // service display
                if (!(typeof content.services === 'undefined')) {
                    service_edit_html += '<label class="control-label"><h5 class=""><b>Services:</b></h5></label> \
                                          <label class="checkbox"> \
                                          <input class="uniform" id="ping_checkbox" type="checkbox" \
                                          value="" onchange="hide_and_show_ping();"> \
                                          <p class="text-primary"><b>ping</b></p> \
                                          </label> <div id="ping_svc" style="display: none;"></div><hr />';

                    for (var i = 0, l = content.services.length; i < l; i++) {
                        service_edit_html += '<div class="service"> \
                                              <label class="checkbox"> \
                                              <input class="uniform" id="svc_' + content.services[i].key + '" \
                                              type="checkbox" value="' + content.services[i].key + '" \
                                              onchange="show_old_configuration_for_svc_edit(' + content.services[i].key + ');"> \
                                              <p class="text-dark">'+content.services[i].value+'</p> \
                                              </label> <div id="show_old_configuration_' + content.services[i].key + '"></div> \
                                              <div id="template_options_id_' + content.services[i].key + '" \
                                              onchange="show_new_configuration_for_svc_edit(' + content.services[i].key + ');"></div> \
                                              <div id="show_new_configuration_' + content.services[i].key + '"></div><hr /></div>';
                    }
                    service_edit_html += '</div>';
                }
            } else {
                // show service information
                service_edit_html += '<h4 class="text-warning">Device Info:</h4> \
                                      <dl class="dl-horizontal"> \
                                      <dt>Device</dt><dd>'+content.device_alias+'</dd> \
                                      <dt>Services</dt><dd>Ping</dd></dl> \
                                      <input type="hidden" id="device_id" value="' + content.device_id + '" /> \
                                      <label class="control-label"><h5 class="text-warning"><b>Services:</b></h5></label> \
                                      <label class="checkbox"> \
                                      <input class="uniform" id="ping_checkbox" type="checkbox" value="" \
                                      onchange="hide_and_show_ping();"> \
                                      <p class="text-dark">Ping</p></label> \
                                      <div id="ping_svc" style="display: none;"></div>';
            }
        } else{
            service_edit_html += content.message;
        }
    } else{
        service_edit_html += content.message;
    }

    service_edit_html += '</div>'

    bootbox.dialog({
        message: service_edit_html,
        title: "<span class='text-primary'><i class='fa fa-pencil'></i> Edit services from nms core.</span>",
        buttons: {
            success: {
                label: "Update",
                className: "btn-success",
                callback: function () {
                    //if services are present on then send the call to add service else just hide the bootbox
                    if (!(typeof content.services === 'undefined') && !(Object.keys(content.services).length === 0)) {
                        if ($("#ping_checkbox").is(":checked")) {
                            var ping_data = {
                                "rta_warning": parseInt($("#rta_warning").text()),
                                "rta_critical": parseInt($("#rta_critical").text()),
                                "pl_warning": parseInt($("#pl_warning").text()),
                                "pl_critical": parseInt($("#pl_critical").text()),
                                "packets": parseInt($("#packets").text()),
                                "timeout": parseInt($("#timeout").text()),
                                "normal_check_interval": parseInt($("#normal_check_interval").text())
                            };
                        }
                        else {
                            var ping_data = {};
                        }
                        var service_data = [];
                        $(".service").each(function (index) {
                            var $this = $(this);
                            var svc = {};
                            $this.children(".checkbox").find("input:checked").each(function () {
                                service_id = $(this).prop("value");
                                svc_val = $("#service_template_" + service_id).val();
                                svc = {
                                    "service_id": $(this).prop("value"),
                                    "template_id": svc_val
                                };
                            });
                            var data_sources = [];
                            // loop through all the elements with class 'data_source_field'
                            $this.find(".data_source_field").each(function(index, obj){
                                // fetching data source values from three columns of each row
                                var $tds = $(this).find('td'),
                                    name = $tds.eq(0).text(),
                                    warning = $tds.eq(1).text(),
                                    critical = $tds.eq(2).text();
                                // create data source dictionary
                                ds = {"name": name, "warning": warning, "critical": critical};
                                // appending data source dictionary to data_sources array
                                data_sources.push(ds);
                            });
                            if (typeof data_sources !== 'undefined' && data_sources.length > 0){
                                svc['data_source'] = data_sources;
                                service_data.push(svc);
                            }
                        });

                        if (edit_service_url) {
                            updated_edit_service_url = edit_service_url.replace('123', $("#device_id").val());
                            // Make Ajax Call
                            $.ajax({
                                url : updated_edit_service_url+"?svc_data="+encodeURIComponent(JSON.stringify(service_data))+'&svc_ping='+encodeURIComponent(JSON.stringify(ping_data)),
                                type : "GET",
                                success : function(response) {
                                    var result = "";
                                    // Type check of response
                                    if (typeof response == 'string') {
                                        result = JSON.parse(response);
                                    } else {
                                        result = response;
                                    }
                                    edit_services_message(result);
                                },
                                error : function(err) {
                                    // console.log(err.statusText);
                                }
                            });
                            // Dajaxice.device.edit_services(edit_services_message, {
                            //     'svc_data': service_data,
                            //     'svc_ping': ping_data,
                            //     'device_id': parseInt($("#device_id").val())
                            // });
                        }
                    } else {
                        if ($("#ping_checkbox").is(":checked")) {
                            var ping_data = {
                                "rta_warning": parseInt($("#rta_warning").text()),
                                "rta_critical": parseInt($("#rta_critical").text()),
                                "pl_warning": parseInt($("#pl_warning").text()),
                                "pl_critical": parseInt($("#pl_critical").text()),
                                "packets": parseInt($("#packets").text()),
                                "timeout": parseInt($("#timeout").text()),
                                "normal_check_interval": parseInt($("#normal_check_interval").text()),
                            };
                        } else {
                            var ping_data = {};
                        }

                        if (edit_service_url) {
                            updated_edit_service_url = edit_service_url.replace('123', $("#device_id").val());
                            // Make Ajax Call
                            $.ajax({
                                url : updated_edit_service_url+"?svc_ping="+encodeURIComponent(JSON.stringify(ping_data))+"&svc_data=",
                                type : "GET",
                                success : function(response) {
                                    var result = "";
                                    // Type check of response
                                    if (typeof response == 'string') {
                                        result = JSON.parse(response);
                                    } else {
                                        result = response;
                                    }
                                    edit_services_message(result);
                                },
                                error : function(err) {
                                    // console.log(err.statusText);
                                }
                            });

                            // Dajaxice.device.edit_services(edit_services_message, {
                            //     'svc_data': "",
                            //     'svc_ping': ping_data,
                            //     'device_id': parseInt($("#device_id").val())
                            // });
                        }
                    }
                }
            },
            danger: {
                label: "Cancel",
                className: "btn-danger",
                callback: function () {
                    $(".bootbox").modal("hide");
                }
            }
        }
    });
}

// hide and show ping based on checkbox selected or not
function hide_and_show_ping() {

    if ($("#ping_checkbox").is(":checked")) {
        if($('#ping_svc').is(':empty')) {
            if (svc_edit_ping_conf_url) {
                var updated_url = svc_edit_ping_conf_url.replace('123', $('#device_id').val());

                // Make Ajax Call
                $.ajax({
                    url : updated_url,
                    type : "GET",
                    success : function(response) {
                        var result = "";
                        // Type check of response
                        if (typeof response == 'string') {
                            result = JSON.parse(response);
                        } else {
                            result = response;
                        }
                        var block_html = '',
                            packets = result.data.packets ? result.data.packets : "",
                            pl_critical = result.data.pl_critical ? result.data.pl_critical : "",
                            pl_warning = result.data.pl_warning ? result.data.pl_warning : "",
                            rta_critical = result.data.rta_critical ? result.data.rta_critical : "",
                            rta_warning = result.data.rta_warning ? result.data.rta_warning : "",
                            timeout_time = result.data.timeout ? result.data.timeout : "",
                            normal_check_interval = result.data.normal_check_interval ? result.data.normal_check_interval : "";

                        block_html += '<div class="divide-20"></div> \
                                       <h4 class="text-danger">Ping configuration:</h4> \
                                       <div class=""><div class="box border red"><div class="box-title"><h4> \
                                       <i class="fa fa-table"></i>Ping Parameters:</h4></div> \
                                       <div class="box-body"><table class="table"> \
                                       <thead><tr><th>Packets</th><th>Timeout</th><th>Normal Check Interval</th></tr></thead> \
                                       <tbody><tr> \
                                       <td contenteditable="true" id="packets">' + packets + '</td> \
                                       <td contenteditable="true" id="timeout">' + timeout_time + '</td> \
                                       <td contenteditable="true" id="normal_check_interval">' + normal_check_interval + '</td> \
                                       </tr></tbody> \
                                       <thead><tr><th>Data Source</th><th>Warning</th><th>Critical</th></tr></thead> \
                                       <tbody> \
                                       <tr><td>RTA</td><td contenteditable="true" id="rta_warning">' + rta_warning + '</td>\
                                       <td contenteditable="true" id="rta_critical">' + rta_critical + '</td></tr> \
                                       <tr><td>PL</td><td contenteditable="true" id="pl_warning">' + pl_warning + '</td> \
                                       <td contenteditable="true" id="pl_critical">' + pl_critical + '</td></tr> \
                                       </tbody></table></div></div></div>'


                        $('#ping_svc').html(block_html);

                    },
                    error : function(err) {
                        // console.log(err.statusText);
                    }
                });
                // Dajaxice.device.get_ping_configuration_for_svc_edit(
                //     Dajax.process,
                //     {
                //         'device_id': $('#device_id').val()
                //     }
                // );
            }
            $("#ping_svc").show();
        } else{
            $("#ping_svc").show();
        }
    }
    else {
        $("#ping_svc").hide();
    }
}

// display service templates select menu
function show_old_configuration_for_svc_edit(value) {
    var service_dom_id = "#svc_"+value;
    if ($(service_dom_id).is(":checked")){
        var old_conf_updated_url = '';
        if (svc_edit_old_conf_url) {
            old_conf_updated_url = svc_edit_old_conf_url.replace('123', value);
            old_conf_updated_url = old_conf_updated_url.replace('11111111', $('#device_id').val());

            // Make Ajax Call
            $.ajax({
                url : old_conf_updated_url,
                type : "GET",
                success : function(response) {
                    var result = "";
                    // Type check of response
                    if (typeof response == 'string') {
                        result = JSON.parse(response);
                    } else {
                        result = response;
                    }
                    var old_conf_block = '',
                        svc_block = '',
                        normal_check_interval = result.data.hasOwnProperty('normal_check_interval') ? result.data.normal_check_interval : "",
                        retry_check_interval = result.data.hasOwnProperty('retry_check_interval') ? result.data.retry_check_interval : "",
                        max_check_attempts = result.data.hasOwnProperty('max_check_attempts') ? result.data.max_check_attempts : "",
                        old_conf = result.data.hasOwnProperty('old_conf') ? result.data.old_conf : [],
                        svc_param = result.data.hasOwnProperty('svc_param') ? result.data.svc_param : [];

                    old_conf_block += "<div class='divide-20'></div> \
                                       <h4 class='text-primary'>Current configuration:</h4> \
                                       <div class=''> \
                                       <div class='box border primary'> \
                                       <div class='box-title'> \
                                       <h4><i class='fa fa-table'></i>Current Service Parameters</h4> \
                                       </div><div class='box-body'><table class='table'> \
                                       <thead><tr> \
                                       <th>Normal Check Interval</th> \
                                       <th>Retry Check Interval</th> \
                                       <th>Max Check Attemps</th> \
                                       </tr></thead> \
                                       <tbody><tr> \
                                       <td>" + normal_check_interval + "</td> \
                                       <td>" + retry_check_interval + "</td> \
                                       <td>" + max_check_attempts + "</td> \
                                       </tr></tbody> \
                                       <thead><tr> \
                                       <th>DS Name</th> \
                                       <th>Warning</th> \
                                       <th>Critical</th> \
                                       </tr></thead><tbody>";

                    for (var i=0;i<old_conf.length;i++) {
                        var ds_name = old_conf[i]['data_source'],
                            warning = old_conf[i]['warning'],
                            critical = old_conf[i]['critical'];
                        old_conf_block += "<tr> \
                                           <td class='ds_name'>" + ds_name + "</td> \
                                           <td class='ds_warning'>" + warning + "</td> \
                                           <td class='ds_critical'>" + critical + "</td> \
                                           </tr>";
                    }

                    old_conf_block += "</tbody></table></div></div></div>";
                                      
                    svc_block += "<p class='text-danger'><b>Select service template:</b></p> \
                                  <select class='form-control' id='service_template_" + value + "'>";

                    for (var i=0;i<svc_param.length;i++) {
                        var id = svc_param[i]['id'],
                            val = svc_param[i]['parameter_description'];
                        svc_block += "<option value='" + id + "'>" + val + "</option>";
                    }

                    svc_block += "</select>";

                    $('#show_old_configuration_'+value).html(old_conf_block);
                    $('#template_options_id_'+value).html(svc_block);
                },
                error : function(err) {
                    // console.log(err.statusText);
                }
            });
            // Dajaxice.device.get_old_configuration_for_svc_edit(
            //     Dajax.process,
            //     {
            //         'option': value,
            //         'service_id': value,
            //         'device_id': $('#device_id').val()
            //     }
            // );
        }
    } else {
        $("#template_options_id_"+value+"").empty();
        $("#show_old_configuration_"+value+"").empty();
        $("#show_new_configuration_"+value+"").empty();
    }
}

// display service parameters table
function show_new_configuration_for_svc_edit(service_id) {
    var template_id = $("#service_template_"+$.trim(service_id)).val(),
        updated_url = '';
    if (svc_edit_new_conf_url) {
        updated_url = svc_edit_new_conf_url.replace('123', service_id);
        updated_url = updated_url.replace('11111111', template_id);
        // Make Ajax Call
        $.ajax({
            url : updated_url,
            type : "GET",
            success : function(response) {
                var result = "";
                // Type check of response
                if (typeof response == 'string') {
                    result = JSON.parse(response);
                } else {
                    result = response;
                }
                var block_html = '',
                    normal_check_interval = result.data.hasOwnProperty('normal_check_interval') ? result.data.normal_check_interval : "",
                    retry_check_interval = result.data.hasOwnProperty('retry_check_interval') ? result.data.retry_check_interval : "",
                    max_check_attempts = result.data.hasOwnProperty('max_check_attempts') ? result.data.max_check_attempts : "",
                    data_sources = result.data.hasOwnProperty('data_sources') ? result.data.data_sources : "";

                block_html += "<div class='divide-20'></div> \
                               <h4 class='text-danger'>Modified configuration:</h4> \
                               <div class=''><div class='box border red'> \
                               <div class='box-title'> \
                               <h4><i class='fa fa-table'></i>Modified Service Parameters</h4> \
                               </div> \
                               <div class='box-body'><table class='table'> \
                               <thead><tr> \
                               <th>Normal Check Interval</th> \
                               <th>Retry Check Interval</th> \
                               <th>Max Check Attempts</th> \
                               </tr></thead><tbody><tr> \
                               <td>" + normal_check_interval + "</td> \
                               <td>" + retry_check_interval + "</td> \
                               <td>" + max_check_attempts + "</td> \
                               </tr></tbody><thead><tr> \
                               <th>DS Name</th> \
                               <th>Warning</th> \
                               <th>Critical</th> \
                               </tr></thead><tbody>";

                for(var i=0;i<data_sources.length;i++) {
                    var ds_name = data_sources[i]['ds_name'],
                        warning = data_sources[i]['warning'],
                        critical = data_sources[i]['critical'];

                    block_html += "<tr class='data_source_field'> \
                                   <td class='ds_name'>" + ds_name + "</td>\
                                   <td contenteditable='true' class='ds_warning'>" + warning + "</td>\
                                   <td contenteditable='true' class='ds_critical'>" + critical + "</td> \
                                   </tr>";
                }

                block_html += "</tbody></table></div></div></div>";

                if ($('#show_new_configuration_'+service_id).length) {
                    $('#show_new_configuration_'+service_id).html(block_html);
                }

            },
            error : function(err) {
                // console.log(err.statusText);
            }
        });        
        
        // Dajaxice.device.get_new_configuration_for_svc_edit(
        //     Dajax.process,
        //     {
        //         'service_id': service_id,
        //         'template_id': template_id
        //     }
        // );
    }

}

// show message for service edit success/failure
function edit_services_message(responseResult) {
    bootbox.alert(responseResult.message);
}

// delete services from nms core
function get_service_delete_form(content) {

    if (content) {
        content = content.data.objects
    } else {
        return true;
    }

    var service_delete_html = "<div class='service_delete_container' style='max-height: 400px; overflow: auto;'>";

    if (content.is_added == 1){
        if (content.master_site == "master_UA") {
            if (!(typeof content.services === 'undefined') && !(Object.keys(content.services).length === 0)) {

                // show service information
                service_delete_html += '<h4 class="">Device Info:</h4> \
                                        <dl class="dl-horizontal"> \
                                        <dt>Device</dt><dd>'+content.device_alias+'</dd> \
                                        <dt>Services</dt><dd>';

                for (var i = 0, l = content.services.length; i < l; i++) {
                    service_delete_html += content.services[i].value+', ' ;
                }

                service_delete_html += '</dd></dl> \
                                        <input type="hidden" id="device_id" value="' + content.device_id + '" />';

                // service display
                if (!(typeof content.services === 'undefined')) {
                    service_delete_html += '<label class="control-label"><h5 class=""><b>Services:</b></h5></label>';
                    for (var i = 0, l = content.services.length; i < l; i++) {
                        service_delete_html += '<div class="service"> \
                                                <label class="checkbox"> \
                                                <input class="uniform" id="svc_' + content.services[i].key + '" \
                                                type="checkbox" value="' + content.services[i].key + '" > \
                                                <p class="text-dark">'+content.services[i].value+'</p> \
                                                </label><hr /></div>';
                    }
                    service_delete_html += '</div>';
                }
            } else {
                service_delete_html += '<h5 class="text-warning">There are no services for \
                                        device ' + '"' + content.device_alias + '"to monitor. </h5>';
            }
        } else{
            service_delete_html += content.message;
        }
    } else{
        service_delete_html += content.message;
    }

    service_delete_html += '</div>';

    bootbox.dialog({
        message: service_delete_html,
        title: "<span class='text-danger'><i class='fa fa-times'></i> Delete services from nms core.</span>",
        buttons: {
            success: {
                label: "Delete",
                className: "btn-success",
                callback: function () {
                    //if services are present on then send the call to add service else just hide the bootbox
                    if (!(typeof content.services === 'undefined') && !(Object.keys(content.services).length === 0)) {
                        var service_data = [];
                        $(".service").each(function (index) {
                            var $this = $(this);
                            $this.children(".checkbox").find("input:checked").each(function () {
                                service_id = $(this).prop("value");
                                svc = $(this).prop("value");
                                service_data.push(svc);
                            });
                        });

                        if (delete_service_url) {
                            updated_delete_service_url = delete_service_url.replace('123', $("#device_id").val());
                            // Make Ajax Call
                            $.ajax({
                                url : updated_delete_service_url+"?service_data="+encodeURIComponent(JSON.stringify(service_data)),
                                type : "GET",
                                success : function(response) {
                                    var result = "";
                                    // Type check of response
                                    if (typeof response == 'string') {
                                        result = JSON.parse(response);
                                    } else {
                                        result = response;
                                    }
                                    delete_services_message(result);
                                },
                                error : function(err) {
                                    // console.log(err.statusText);
                                }
                            });
                            // Dajaxice.device.delete_services(
                            //     delete_services_message,
                            //     {
                            //         'device_id': $("#device_id").val(),
                            //         'service_data': service_data
                            //     }
                            // );
                        }

                    } else{
                        $(".bootbox").modal("hide");
                    }
                }
            },
            danger: {
                label: "Cancel",
                className: "btn-danger",
                callback: function () {
                    $(".bootbox").modal("hide");
                }
            }
        }
    });
}

// show message for service deletion success/failure
function delete_services_message(responseResult) {
    bootbox.alert(responseResult.message);
}

// ********************************** Service Add Functions ***************************************
// add services on nms core
function get_service_add_form(content) {
    
    if (content) {
        content = content.data.objects
    } else {
        return true;
    }

    var service_add_html = "";

    if (content.is_added == 1){
        if (content.master_site == "master_UA") {
            if (!(typeof content.services === 'undefined') && !(Object.keys(content.services).length === 0)) {

                // show service information
                service_add_html += '<h5 class=""><b>Device Info:</b></h5>';
                service_add_html += '<dl class="dl-horizontal">';
                service_add_html += '<dt>Device</dt><dd>'+content.device_alias+'</dd>';
                service_add_html += '<dt>Services</dt><dd>';
                for (var i = 0, l = content.services.length; i < l; i++) {
                    service_add_html += content.services[i].value+', ' ;
                }
                service_add_html += '</dd></dl>';
                service_add_html += '<input type="hidden" id="device_id" value="' + content.device_id + '" />';

                // service display
                if (!(typeof content.services === 'undefined')) {
                    service_add_html += '<label class="control-label"><h5 class="text"><b>Services:</b></h5></label>';
                    for (var i = 0, l = content.services.length; i < l; i++) {
                        service_add_html += '<div class="service"> \
                                             <label class="checkbox"> \
                                             <input class="uniform" id="svc_' + content.services[i].key + '" \
                                             type="checkbox" value="' + content.services[i].key + '" \
                                             onchange="show_old_configuration_for_svc_add(' + content.services[i].key + ');"> \
                                             <p class="text-dark">'+content.services[i].value+'</p></label> \
                                             <div id="template_options_id_' + content.services[i].key + '" \
                                             onchange="show_new_configuration_for_svc_add(' + content.services[i].key + ');"></div> \
                                             <div id="show_new_configuration_' + content.services[i].key + '"></div> \
                                             <hr /></div>';
                    }
                    service_add_html += '</div>';
                }
            } else {
                service_add_html += '<h5 class="">All service are operational for device ' + '"' + content.device_alias + '". </h5>';
            }
        } else{
            service_add_html += content.message;
        }
    } else{
        service_add_html += content.message;
    }

    // Create bootbox dialog
    bootbox.dialog({
        message: service_add_html,
        title: "<span class='text-green'><b></b><i class='fa fa-plus'></i> Add services to nms core.</span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                    //if services are present on then send the call to add service else just hide the bootbox
                    if (!(typeof content.services === 'undefined') && !(Object.keys(content.services).length === 0)) {
                        var service_data = [];
                        $(".service").each(function (index) {
                            if ($(this).children(".checkbox").find("input:checked").prop('checked')==true) {
                                var $this = $(this);
                                var svc = {};
                                $this.children(".checkbox").find("input:checked").each(function () {
                                    service_id = $(this).prop("value");
                                    svc_val = $("#service_template_" + service_id).val();
                                    svc = {"service_id": $(this).prop("value"), "template_id": svc_val};
                                });
                                var data_sources = [];
                                // loop through all the elements with class 'data_source_field'
                                $this.find(".data_source_field").each(function(index, obj){
                                    // fetching data source values from three columns of each row
                                    var $tds = $(this).find('td'),
                                        name = $tds.eq(0).text(),
                                        warning = $tds.eq(1).text(),
                                        critical = $tds.eq(2).text();
                                    // create data source dictionary
                                    ds = {"name": name, "warning": warning, "critical": critical};
                                    // appending data source dictionary to data_sources array
                                    data_sources.push(ds);
                                });
                                if (typeof data_sources !== 'undefined' && data_sources.length > 0){
                                    svc['data_source'] = data_sources;
                                }
                                service_data.push(svc);
                            }
                        });
                        if (add_service_url) {
                            updated_add_service_url = add_service_url.replace('123', content.device_id);
                            // Make Ajax Call
                            $.ajax({
                                url : updated_add_service_url+'?svc_data='+encodeURIComponent(JSON.stringify(service_data)),
                                type : "GET",
                                success : function(response) {
                                    var result = "";
                                    // Type check of response
                                    if (typeof response == 'string') {
                                        result = JSON.parse(response);
                                    } else {
                                        result = response;
                                    }
                                    add_services_message(result);
                                },
                                error : function(err) {
                                    // console.log(err.statusText);
                                }
                            });
                            // Dajaxice.device.add_services(
                            //     add_services_message,
                            //     {
                            //         'device_id': $("#device_id").val(),
                            //         'svc_data': service_data
                            //     }
                            // );
                        }
                    } else{
                        $(".bootbox").modal("hide");
                    }
                }
            },
            danger: {
                label: "No!",
                className: "btn-danger",
                callback: function () {
                    $(".bootbox").modal("hide");
                }
            }
        }
    });
}

// display service templates select menu
function show_old_configuration_for_svc_add(value) {
    id = "#svc_"+value;
    if ($(id).is(":checked")) {
        var updated_svc_add_old_conf_url = '';
        if (svc_add_old_conf_url) {
            updated_svc_add_old_conf_url = svc_add_old_conf_url.replace('123', $('#device_id').val());
            updated_svc_add_old_conf_url = updated_svc_add_old_conf_url.replace('11111111', value);

            // Make Ajax Call
            $.ajax({
                url : updated_svc_add_old_conf_url,
                type : "GET",
                success : function(response) {
                    var result = "";
                    // Type check of response
                    if (typeof response == 'string') {
                        result = JSON.parse(response);
                    } else {
                        result = response;
                    }
                    var block_html = '',
                        svc_param = result.data.objects.svc_param,
                        option_val = result.data.objects.option;

                    block_html += "<p class='text-green'><b>Select service template:</b></p> \
                                   <select class='form-control' id='service_template_" + option_val + "'> \
                                   <option value='' selected>Select</option>";
                    for(var i=0;i<svc_param.length;i++) {
                        block_html += "<option value='" + svc_param[i]['id'] + "'>" + svc_param[i]['parameter_description'] + "</option>";
                    }
                    block_html += "</select>";

                    $('#template_options_id_'+option_val).html(block_html);
                },
                error : function(err) {
                    // console.log(err.statusText);
                }
            });

            // Dajaxice.device.get_old_configuration_for_svc_add(
            //     Dajax.process,
            //     {
            //         'option': value,
            //         'service_id': $(id).prop("value"),
            //         'device_id': $('#device_id').val()
            //     }
            // );
        }
    }
    else {
        $("#template_options_id_"+value+"").empty();
        $("#show_old_configuration_"+value+"").empty();
        $("#show_new_configuration_"+value+"").empty();
    }
}

// display service parameters table
function show_new_configuration_for_svc_add(value){
    var service_id = value,
        template_id = $("#service_template_"+value).val(),
        update_svc_add_new_conf_url = '';

    if (svc_add_new_conf_url) {
        update_svc_add_new_conf_url = svc_add_new_conf_url.replace('123', service_id);
        update_svc_add_new_conf_url = update_svc_add_new_conf_url.replace('11111111', template_id);

        // Make Ajax Call
        $.ajax({
            url : update_svc_add_new_conf_url,
            type : "GET",
            success : function(response) {
                var result = "";
                // Type check of response
                if (typeof response == 'string') {
                    result = JSON.parse(response);
                } else {
                    result = response;
                }
                var html_block = '',
                    resultset = result.data.objects,
                    normal_check_interval = resultset.hasOwnProperty('normal_check_interval') ? resultset.normal_check_interval : "",
                    retry_check_interval = resultset.hasOwnProperty('retry_check_interval') ? resultset.retry_check_interval : "",
                    max_check_attempts = resultset.hasOwnProperty('max_check_attempts') ? resultset.max_check_attempts : "",
                    data_sources = resultset.hasOwnProperty('data_sources') ? resultset.data_sources : [];

                html_block += "<div class='divide-20'></div> \
                               <h4 class='text-green'>Selected configuration:</h4> \
                               <div class=''> \
                               <div class='box border green'> \
                               <div class='box-title'> \
                               <h4><i class='fa fa-table'></i>Selected Service Parameters</h4> \
                               </div> \
                               <div class='box-body'><table class='table'> \
                               <thead><tr> \
                               <th>Normal Check Interval</th> \
                               <th>Retry Check Interval</th> \
                               <th>Max Check Attempts</th> \
                               </tr></thead><tbody><tr> \
                               <td>" + normal_check_interval + "</td> \
                               <td>" + retry_check_interval + "</td> \
                               <td>" + max_check_attempts + "</td> \
                               </tr></tbody><thead><tr> \
                               <th>DS Name</th> \
                               <th>Warning</th> \
                               <th>Critical</th> \
                               </tr></thead><tbody>";

                for (var i=0;i<data_sources.length;i++) {
                    var ds_name = data_sources[i]['name'] ? data_sources[i]['name'] : "NA",
                        warning = data_sources[i]['warning'] ? data_sources[i]['warning'] : "",
                        critical = data_sources[i]['critical'] ? data_sources[i]['critical'] : "",
                        td_title =  data_sources[i]['title'] ? data_sources[i]['title'] : "Not Editable",
                        state =  data_sources[i]['state'] ? data_sources[i]['state'] : 'false';

                    html_block += "<tr class='data_source_field'> \
                                   <td class='ds_name'>" + ds_name + "</td> \
                                   <td contenteditable='" + state + "' title='" + td_title + "' class='ds_warning'> \
                                   " + warning + "</td> \
                                   <td contenteditable='" + state + "' title='" + td_title + "' class='ds_critical'> \
                                   " + critical + "</td> \
                                   </tr>";
                }

                html_block += "</tbody></table></div></div></div>";

                $('#show_new_configuration_'+service_id).html(html_block)
            },
            error : function(err) {
                // console.log(err.statusText);
            }
        });
        // Dajaxice.device.get_new_configuration_for_svc_add(
        //     Dajax.process,
        //     {
        //         'service_id': service_id,
        //         'template_id': template_id
        //     }
        // );
    }
}

// show message for service add success/failure
function add_services_message(responseResult) {
    bootbox.alert(responseResult.message);
}

// ********************************** Service Add Functions ***************************************
// add services on nms core
function device_services_status_frame(content) {

    if (content) {
        content = content.data.objects
    } else {
        return true;
    }

    var services_status_html = "<div class='device_status_container' style='max-height: 450px; overflow: auto;'>";
    services_status_html += '<h4 style="margin-top: 0px;">Device Info:</h4> \
                             <dl class="dl-horizontal"> \
                             <dt>Device</dt><dd>'+content.device_name+'</dd> \
                             <dt>Machine</dt><dd>'+content.machine+'</dd> \
                             <dt>Site</dt><dd>'+content.site_instance+'</dd> \
                             <dt>IP Address</dt><dd>'+content.ip_address+'</dd> \
                             <dt>Device Type</dt><dd>'+content.device_type+'</dd> \
                             </dd></dl>';

    var active_services = content.active_services,
        inactive_services = content.inactive_services;

    if (!(typeof active_services === 'undefined') && !(Object.keys(active_services).length === 0)) {
        services_status_html += '<div class=""><div class="box border green"><div class="box-title"> \
                                 <h4><i class="fa fa-table"></i>Operational Services</h4></div>  \
                                 <div class="box-body"><table class="table table-striped table-bordered table-hover"> \
                                 <thead><tr><th>Service</th><th>Data Sources</th></tr></thead> \
                                 <tbody>';

        for (var i = 0, l = active_services.length; i < l; i++) {
            services_status_html += '<tr> \
                                     <td>'+active_services[i].service+'</td> \
                                     <td>'+active_services[i].data_sources+'</td> \
                                     </tr>';
        }

        services_status_html += '</tbody></table> </div></div></div>';
    } else {
        services_status_html += '<div class=""><div class="box border green"><div class="box-title"> \
                                 <h4><i class="fa fa-table"></i>Operational Services</h4></div> \
                                 <div class="box-body"><table class="table table-striped table-bordered table-hover"> \
                                 <thead><tr><th>Service</th><th>Data Sources</th></tr></thead> \
                                 <tbody> \
                                 <tr> \
                                 <td colspan="2" style="text-align:center;"><span class="text-danger"> \
                                 No service is operational on this device.</span></td> \
                                 </tr> \
                                 </tbody></table></div></div></div>';
    }

    if (!(typeof inactive_services === 'undefined') && !(Object.keys(inactive_services).length === 0)) {
        services_status_html += '<div class=""><div class="box border red"><div class="box-title"> \
                                 <h4><i class="fa fa-table"></i>Non Operational Services</h4></div> \
                                 <div class="box-body"><table class="table table-striped table-bordered table-hover"> \
                                 <thead><tr><th>Service</th><th>Data Sources</th></tr></thead> \
                                 <tbody>';

        for (var i = 0, l = inactive_services.length; i < l; i++) {
            services_status_html += '<tr> \
                                     <td>'+inactive_services[i].service+'</td> \
                                     <td>'+inactive_services[i].data_sources+'</td> \
                                     </tr>';
        }
        services_status_html += '</tbody></table></div></div></div>';
    } else {
        services_status_html += '<div class=""><div class="box border red"><div class="box-title"> \
                                 <h4><i class="fa fa-table"></i>Non Operational Services</h4></div> \
                                 <div class="box-body"><table class="table table-striped table-bordered table-hover"> \
                                 <thead><tr><th>Service</th><th>Data Sources</th></tr></thead> \
                                 <tbody><tr> \
                                 <td colspan="2" style="text-align:center;"><span class="text-danger"> \
                                 All services are operational for this device.</span></td> \
                                 </tr></tbody></table> \
                                 </div></div></div>';
    }

    services_status_html += '</div>';

    bootbox.dialog({
        message: services_status_html,
        title: "<span class='text-green'><i class='fa fa-list-alt'></i> Device Services Status</span>",
        // buttons: {
        //     success: {
        //         label: "Yes!",
        //         className: "btn-success",
        //         callback: function () {
        //                 $(".bootbox").modal("hide");
        //         }
        //     },
        //     danger: {
        //         label: "No!",
        //         className: "btn-danger",
        //         callback: function () {
        //             $(".bootbox").modal("hide");
        //         }
        //     }
        // }
    });
    // Increase the width of modal box(bootbox)
    $(".modal-dialog").css("width","75%");
}

// ********************************** Device Restore Functions ***************************************
// restore device
function get_restore_device_form(content) {

    if (content) {
        content = content.data.objects
    } else {
        return true;
    }
    var restore_device_html = '';

    restore_device_html += '<input type="hidden" id="device_id" value="' + content.id + '" /> \
                           <h4 class="text-warning">Device Info:</h4> \
                           <dl class="dl-horizontal"> \
                           <dt>Device IP</dt><dd>' + content.ip_address + '</dd> \
                           <dt>Device Alias</dt><dd>' + content.alias + '</dd> \
                           </dd></dl>';

    bootbox.dialog({
        message: restore_device_html,
        title: "<span class='text-danger'><i class='fa fa-plus'></i> RESTORE DEVICE</span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                    if (restore_device_url) {
                        var updated_url = '';
                        updated_url = restore_device_url.replace('123', $("#device_id").val());

                        // Make Ajax Call
                        $.ajax({
                            url : updated_url,
                            type : "GET",
                            success : function(response) {
                                var result = "";
                                // Type check of response
                                if (typeof response == 'string') {
                                    result = JSON.parse(response);
                                } else {
                                    result = response;
                                }
                                device_restore_message(result);
                            },
                            error : function(err) {
                                // console.log(err.statusText);
                            }
                        });

                        // Dajaxice.device.device_restore(
                        //     device_restore_message,
                        //     {
                        //         'device_id': $("#device_id").val()
                        //     }
                        // );
                    }
                }
            },
            danger: {
                label: "No!",
                className: "btn-danger",
                callback: function () {
                    $(".bootbox").modal("hide");
                }
            }
        }
    });
}

// show message for device addition success/failure
function device_restore_message(responseResult) {
    bootbox.alert(responseResult.message, function() {
        // reload page after clicking "OK!"
        location = window.location.origin + "/device/#ArchivedDeviceListing";
        location.reload();
    });
}