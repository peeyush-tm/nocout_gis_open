// get single service edit form
// add service to nms core
function get_single_service_edit_form(content) {
    // service_add_html --> contains content for bootbox
    var service_add_html = "";
    service_add_html += '<input type="hidden" id="dsc_id" value="' + content.result.data.objects.dsc_id + '" />';
    service_add_html += '<input type="hidden" id="service_id" value="' + content.result.data.objects.service_name + '" />';
    service_add_html += '<input type="hidden" id="device_id" value="' + content.result.data.objects.device_name + '" />';

    // show old service information
    service_add_html += '<h5 class="text-warning"><b>Current configuration:</b></h5>';
    service_add_html += '<dl class="dl-horizontal">';
    service_add_html += '<dt>Device</dt><dd>'+content.result.data.objects.device_alias+'</dd>';
    service_add_html += '<dt>Service</dt><dd>'+content.result.data.objects.service_name+'</dd>';
    service_add_html += '<dt>Data Source</dt><dd>'+content.result.data.objects.data_source+'</dd></dl>';
    service_add_html += '<input type="hidden" id="device_id" value="' + content.result.data.objects.device_id + '" />';
    if (!(typeof content.result.data.objects.templates === 'undefined') && !(Object.keys(content.result.data.objects.templates).length === 0)) {
        service_add_html += '<div class="box border orange"><div class="box-title"><h4><i class="fa fa-table"></i>Service & Data Source Parameters</h4></div>';
        service_add_html += '<div class="box-body"><table class="table">';
        service_add_html += '<thead><tr><th>Normal Check Interval</th><th>Retry Check Interval</th><th>Max Check Attemps</th></tr></thead>';
        service_add_html += '<tbody>';
        service_add_html += '<tr>';
        service_add_html += '<td>'+content.result.data.objects.normal_check_interval+'</td>';
        service_add_html += '<td>'+content.result.data.objects.retry_check_interval+'</td>';
        service_add_html += '<td>'+content.result.data.objects.max_check_attempts+'</td>';
        service_add_html += '</tr></tbody>';
        service_add_html += '<thead><tr><th>DS Name</th><th>Warning</th><th>Critical</th></tr></thead>';
        service_add_html += '<tbody><tr>';
        service_add_html += '<td>'+content.result.data.objects.data_source+'</td>';
        service_add_html += '<td>'+content.result.data.objects.warning+'</td>';
        service_add_html += '<td>'+content.result.data.objects.critical+'</td>';
        service_add_html += '</tr>';
        service_add_html += '</tbody></table>';
        service_add_html += '</div></div></div>';

        // shows currently selected service information
        service_add_html += '<h5 class="text-danger"><b>Modified configuration:</b></h5>';
        service_add_html += '<h6><b>Select service template:</b></h6>';
        // display error message for empty service template select menu
        service_add_html += '<div id="svc_template_error_msg" class="text-danger"></div>';
        service_add_html += '<select class="form-control" id="id_svc_templates" name="svc_templates" onchange="on_svc_template_change();">';
        service_add_html += '<option value="">Select</option>';
        for (var i = 0, l = content.result.data.objects.templates.length; i < l; i++) {
            service_add_html += '<option value="' + content.result.data.objects.templates[i].key + '">' + content.result.data.objects.templates[i].value + '</option>';
        }
        service_add_html += '</select>';
        service_add_html += '<div id="modified_info"></div>';
    }
    else{
        service_add_html += '<p class="text-danger">No templates associated with this service.<br />Service can\'t be edited due to non existence of service templates.</p>';
    }

    // display bootbox with 'service_add_html' value as content
    bootbox.dialog({
        message: service_add_html,
        title: "<span class='text-danger'><i class='fa fa-edit'></i> Edit service: "+ content.result.data.objects.service_name +"</span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                    if (!(typeof content.result.data.objects.templates === 'undefined') && !(Object.keys(content.result.data.objects.templates).length === 0)) {
                        //if services are present on then send the call to add service else just hide the bootbox
                        if ($("#id_svc_templates").val() != "") {
                            // data_sources --> array which contains data sources dictionaries
                            var data_sources = [];
                            // loop through all the elements with class 'data_source_field'
                            $('.data_source_field').each(function(index, obj){
                                // fetching data source values from three columns of each row
                                var $tds = $(this).find('td'),
                                    data_source = $tds.eq(0).text(),
                                    warning = $tds.eq(1).text(),
                                    critical = $tds.eq(2).text();
                                // create data source dictionary
                                ds = {"data_source": data_source, "warning": warning, "critical": critical};
                                // appending data source dictionary to data_sources array
                                data_sources.push(ds);
                            });
                            Dajaxice.device.edit_single_service(edit_single_service_message, {'dsc_id': $("#dsc_id").val(),
                                                                                              'svc_temp_id': $('#id_svc_templates').val(),
                                                                                              'data_sources': data_sources});
                            // return true, so that bootbox close if success call goes successfully
                            return true;
                        }
                        else {
                            // display this message if no service template is selected
                            $("#svc_template_error_msg").text("* Service template must be selected.");
                            // return false, so that bootbox doesn't close automatically
                            return false;
                        }
                    }
                    else{
                        $(".bootbox").modal("hide");
                        return true;
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

// display service parameters table on service change
function on_svc_template_change(){
    Dajaxice.device.get_service_para_table(Dajax.process, {'device_name': $('#device_id').val(),
                                                           'service_name': $('#service_id').val(),
                                                           'template_id': $('#id_svc_templates').val()});
}

// show message for service addition success/failure
function edit_single_service_message(responseResult) {
    bootbox.alert(responseResult.result.message, function(){
        // reload page after clicking "OK!"
        location = window.location.origin+"/service_history/";
        location.reload();
    });
}

function get_single_service_delete_form(content){
    // service_delete_html --> contains content for bootbox
    var service_delete_html = "";
    service_delete_html += '<input type="hidden" id="service_id" value="' + content.result.data.objects.service_name + '" />';
    service_delete_html += '<input type="hidden" id="device_id" value="' + content.result.data.objects.device_name + '" />';

    // show service information
    service_delete_html += '<h5 class="text-danger"><b>Service Delete Info:</b></h5>';
    service_delete_html += '<dl class="dl-horizontal">';
    service_delete_html += '<dt>Device</dt><dd>'+content.result.data.objects.device_alias+'</dd>';
    service_delete_html += '<dt>Service</dt><dd>'+content.result.data.objects.service_alias+'</dd>';
    service_delete_html += '<dt>Data Sources</dt>';
    for (var i = 0, l = content.result.data.objects.data_sources.length; i < l; i++) {
        service_delete_html += '<dd>'+content.result.data.objects.data_sources[i]+'</dd>';
    }
    service_delete_html += '</dl>';

    // display bootbox with 'service_delete_html' value as content
    bootbox.dialog({
        message: service_delete_html,
        title: "<span class='text-danger'><i class='fa fa-times'></i> Delete service: "+ content.result.data.objects.service_name +"</span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                        Dajaxice.device.delete_single_service(delete_single_service_message, {'device_name': $("#device_id").val(),
                                                                                              'service_name': $('#service_id').val()});
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


// show message for service deletion success/failure
function delete_single_service_message(responseResult) {
    bootbox.alert(responseResult.result.message, function(){
        // reload page after clicking "OK!"
        location = window.location.origin+"/service_history/";
        location.reload();
    });
}
