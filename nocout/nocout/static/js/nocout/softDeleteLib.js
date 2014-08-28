/**
 * This function triggers which delete icon for any row is clicked & performs softdelete functionality
 * @method get_soft_delete_form
 * @param content {JSON Object} Contains data object sent from server
 */


// soft deletion of objects
function get_soft_delete_form(content) {
    // soft_delete_html: contains html for soft delete form
    var soft_delete_html = "";
    if ((content.result.data.objects.eligible.length > 0 )) {
        soft_delete_html += '<h5 class="text-danger">Please first choose future parent of this '+$.trim(content.result.data.objects.form_title)+' from below choices:</h5>';
        soft_delete_html += '<input type="hidden" id="id_'+$.trim(content.result.data.objects.form_type)+'" name="'+$.trim(content.result.data.objects.form_type)+'" value="' + content.result.data.objects.id + '" />';
        soft_delete_html += '<select class="form-control" id="id_parent" name="parent">';
        soft_delete_html += '<option value="">Select '+$.trim(content.result.data.objects.form_title)+'</option>';
        for (var i = 0, l = content.result.data.objects.eligible.length; i < l; i++){
            soft_delete_html += '<option value="' + content.result.data.objects.eligible[i].key + '">' + content.result.data.objects.eligible[i].value + '</option>';
        }
        soft_delete_html += '</select>';
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

                         Dajaxice.device.device_soft_delete(show_response_message, {'device_id': $('#id_device').val(),
                        'new_parent_id': $('#id_parent').val()})

                    } else if($.trim(content.result.data.objects.form_type) == 'device_group') {

                        Dajaxice.device_group.device_group_soft_delete(show_response_message, {'device_group_id':
                            $('#id_device_group').val(),'new_parent_id': $('#id_parent').val() });

                    } else if($.trim(content.result.data.objects.form_type) == 'user_group') {

                        Dajaxice.user_group.user_group_soft_delete(show_response_message, {'user_group_id':
                            $('#id_user_group').val(),'new_parent_id': $('#id_parent').val()});

                    } else if($.trim(content.result.data.objects.form_type) == 'user') {
                        Dajaxice.user_profile.user_soft_delete(show_response_message, {
                            'user_id': $('#id_user').val(),
                            'new_parent_id': $('#id_parent').val(),
                            'datatable_headers':content.result.data.objects.datatable_headers,
                            'userlistingtable':'/user/userlistingtable/',
                            'userarchivelisting':'/user/userarchivedlistingtable/'});
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

function add_confirmation(id){
    bootbox.dialog({
      message:"Are you sure want to add this user ",
      title: "<span class='text-danger'><i class='fa fa-times'></i>Confirmation</span>",
      buttons: {
          success: {
          label: "Yes!",
                className: "btn-success",
                callback: function () {
                Dajaxice.user_profile.user_add(show_response_message, { 'user_id': id })
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

function hard_delete_confirmation(id){
    bootbox.dialog({
      message:"Are you sure want to delete this user",
      title: "<span class='text-danger'><i class='fa fa-times'></i>Confirmation</span>",
      buttons: {
          success: {
          label: "Yes!",
                className: "btn-success",
                callback: function () {
                Dajaxice.user_profile.user_hard_delete(show_response_message, { 'user_id': id })
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
    bootbox.alert(responseResult.result.message);
    location.reload(true);
//    if (typeof responseResult.result.data.objects.datatable_headers == undefined){
//        datatable_headers= responseResult.result.data.objects.datatable_headers
//        for (i=0; i< datatable_headers.length; i++){
//
//            for (var key in datatable_headers[i]){
//                var obj = datatable_headers[i][key];
//                if(obj=='False'){
//                    obj=false
//                }
//                else if (obj=='True'){
//                    obj=true
//                }
//                datatable_headers[i][key]=obj
//            }
//        }
//        var gridHeadersObj = datatable_headers
//        var ajax_url_user_listing = responseResult.result.data.objects.userlistingtable
//        var ajax_url_user_archived_listing= responseResult.result.data.objects.userarchivelisting
//        var dataTableInstance = new ourDataTableWidget();
//        dataTableInstance.createDataTable("UserArchivedListingTable", gridHeadersObj, ajax_url_user_archived_listing, destroy=true);
//        dataTableInstance.createDataTable("UserListingTable", gridHeadersObj, ajax_url_user_listing, destroy=true);
//    }
}


// add device to monitoring core
function add_device(device_id) {
    add_device_html = '<h5 class="">Configure ping service for device:</h5><br />';
    add_device_html += '<div class=""><div class="box border red"><div class="box-title"><h4><i class="fa fa-table"></i>Ping Parameters:</h4></div>';
    add_device_html += '<div class="box-body"><table class="table">';
    add_device_html += '<thead><tr><th>Packets</th><th>Timeout</th><th>Normal Check Interval</th></tr></thead>';
    add_device_html += '<tbody>';
    add_device_html += '<tr>';
    add_device_html += '<td contenteditable="true" id="packets">6</td>';
    add_device_html += '<td contenteditable="true" id="timeout">20</td>';
    add_device_html += '<td contenteditable="true" id="normal_check_interval">5</td>';
    add_device_html += '</tr>';
    add_device_html += '</tbody>';
    add_device_html += '<thead><tr><th>Data Source</th><th>Warning</th><th>Critical</th></tr></thead>';
    add_device_html += '<tbody>';
    add_device_html += '<tr><td>RTA</td><td contenteditable="true" id="rta_warning">1500</td><td contenteditable="true" id="rta_critical">3000</td></tr>';
    add_device_html += '<tr><td>PL</td><td contenteditable="true" id="pl_warning">80</td><td contenteditable="true" id="pl_critical">100</td></tr>';
    add_device_html += '</tbody>';
    add_device_html += '</table>';
    add_device_html += '</div></div></div>';

    bootbox.dialog({
        message: add_device_html,
        title: "<span class='text-danger'><i class='fa fa-plus'></i> Add device to nms core. </span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                    ping_data = {
                        "rta_warning": parseInt($("#rta_warning").text()),
                        "rta_critical": parseInt($("#rta_critical").text()),
                        "pl_warning": parseInt($("#pl_warning").text()),
                        "pl_critical": parseInt($("#pl_critical").text()),
                        "packets": parseInt($("#packets").text()),
                        "timeout": parseInt($("#timeout").text())
                    };
                    //alert(JSON.stringify(ping_data));
                    Dajaxice.device.add_device_to_nms_core(device_add_message, {'device_id': device_id, 'ping_data': ping_data});
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
function device_add_message(responseResult) {
    bootbox.alert(responseResult.result.message, function(){
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
        message: "Delete device form nms core.",
        title: "<span class='text-danger'><i class='fa fa-times'></i> Delete device form nms core.</span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                    Dajaxice.device.delete_device_from_nms_core(device_delete_message, {'device_id': device_id});
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
    bootbox.alert(responseResult.result.message, function(){
        // reload page after clicking "OK!"
        location = window.location.origin+"/device/#OperationalDeviceListing";
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
                    $(".bootbox").modal("hide");
                }
            }
        }
    });
}


// show message for device sync addition success/failure
function sync_devices_message(responseResult) {
    bootbox.alert(responseResult.result.message);
}

/*
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
                service_add_html += '<h5 class="text-warning">There are no services for device ' + '"' + content.result.data.objects.device_alias + '"to monitor. </h5>';
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
                    //if services are present on then send the call to add service else just hide the bootbox
                    if (!(typeof content.result.data.objects.services === 'undefined') && !(Object.keys(content.result.data.objects.services).length === 0)) {
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
                    else{
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

*/


// edit services on nms core
function get_service_edit_form(content) {
    var service_edit_html = "";

    if (content.result.data.objects.is_added == 1){
        if (content.result.data.objects.master_site == "master_UA") {
            if (!(typeof content.result.data.objects.services === 'undefined') && !(Object.keys(content.result.data.objects.services).length === 0)) {

                // display port select menu
                //service_edit_html += '<h5 class="text-warning">You can edit service for device ' + '"' + content.result.data.objects.device_alias + '" </h5>';
                // show service information
                service_edit_html += '<h5 class="text-warning"><b>Device Info:</b></h5>';
                service_edit_html += '<dl class="dl-horizontal">';
                service_edit_html += '<dt>Device</dt><dd>'+content.result.data.objects.device_alias+'</dd>';
                service_edit_html += '<dt>Services</dt><dd>';
                for (var i = 0, l = content.result.data.objects.services.length; i < l; i++) {
                    service_edit_html += content.result.data.objects.services[i].value+', ' ;
                }
                service_edit_html += '</dd></dl>';
                service_edit_html += '<input type="hidden" id="device_id" value="' + content.result.data.objects.device_id + '" />';

                // service display
                if (!(typeof content.result.data.objects.services === 'undefined')) {
                    service_edit_html += '<label class="control-label"><h5 class="text-warning"><b>Services:</b></h5></label>';
                    service_edit_html += '<label class="checkbox">';
                    service_edit_html += '<input class="uniform" id="ping_checkbox" type="checkbox" value="" onchange="hide_and_show_ping();">';
                    service_edit_html += '<p class="text-dark">Ping</p>';
                    service_edit_html += '</label>';
                    service_edit_html += '<div id="ping_svc" style="display: none;">';
                    service_edit_html += '<br />';
                    service_edit_html += '<h5 class="text-danger"><b>Ping configuration:</b></h5>';
                    service_edit_html += '<div class=""><div class="box border red"><div class="box-title"><h4><i class="fa fa-table"></i>Ping Parameters:</h4></div>';
                    service_edit_html += '<div class="box-body"><table class="table">';
                    service_edit_html += '<thead><tr><th>Packets</th><th>Timeout</th><th>Normal Check Interval</th></tr></thead>';
                    service_edit_html += '<tbody>';
                    service_edit_html += '<tr>';
                    service_edit_html += '<td contenteditable="true" id="packets">6</td>';
                    service_edit_html += '<td contenteditable="true" id="timeout">20</td>';
                    service_edit_html += '<td contenteditable="true" id="norm_check_interval">5</td>';
                    service_edit_html += '</tr>';
                    service_edit_html += '</tbody>';
                    service_edit_html += '<thead><tr><th>Data Source</th><th>Warning</th><th>Critical</th></tr></thead>';
                    service_edit_html += '<tbody>';
                    service_edit_html += '<tr><td>RTA</td><td contenteditable="true" id="rta_warning">1500</td><td contenteditable="true" id="rta_critical">3000</td></tr>';
                    service_edit_html += '<tr><td>PL</td><td contenteditable="true" id="pl_warning">80</td><td contenteditable="true" id="pl_critical">100</td></tr>';
                    service_edit_html += '</tbody>';
                    service_edit_html += '</table>';
                    service_edit_html += '</div></div></div>';
                    service_edit_html += '</div>';
                    $("#ping_svc").hide();
                    service_edit_html += '<hr />';
                    for (var i = 0, l = content.result.data.objects.services.length; i < l; i++) {
                        service_edit_html += '<div class="service">';
                        service_edit_html += '<label class="checkbox">';
                        service_edit_html += '<input class="uniform" id="svc_' + content.result.data.objects.services[i].key + '" type="checkbox" value="' + content.result.data.objects.services[i].key + '" onchange="show_old_configuration_for_svc_edit(' + content.result.data.objects.services[i].key + ');">';
                        service_edit_html += '<p class="text-dark">'+content.result.data.objects.services[i].value+'</p>';
                        service_edit_html += '</label>';
                        service_edit_html += '<div id="show_old_configuration_' + content.result.data.objects.services[i].key + '"></div>';
                        service_edit_html += '<div id="template_options_id_' + content.result.data.objects.services[i].key + '" onchange="show_new_configuration_for_svc_edit(' + content.result.data.objects.services[i].key + ');"></div>';
                        service_edit_html += '<div id="show_new_configuration_' + content.result.data.objects.services[i].key + '"></div>';
                        service_edit_html += '<hr />';
                        service_edit_html += '</div>';
                    }
                    service_edit_html += '</div>';
                }
            }
            else {
                service_edit_html += '<h5 class="text-danger">There are no operational services for device ' + '"' + content.result.data.objects.device_alias+'. </h5>';
            }
        }
        else{
            service_edit_html += content.result.message;
        }
    }
    else{
        service_edit_html += content.result.message;
    }

    bootbox.dialog({
        message: service_edit_html,
        title: "<span class='text-danger'><i class='fa fa-pencil'></i> Edit services from nms core.</span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                    //if services are present on then send the call to add service else just hide the bootbox
                    if (!(typeof content.result.data.objects.services === 'undefined') && !(Object.keys(content.result.data.objects.services).length === 0)) {
                        if ($("#ping_checkbox").is(":checked")) {
                            var ping_data = {
                                "rta_warning": parseInt($("#rta_warning").text()),
                                "rta_critical": parseInt($("#rta_critical").text()),
                                "pl_warning": parseInt($("#pl_warning").text()),
                                "pl_critical": parseInt($("#pl_critical").text()),
                                "packets": parseInt($("#packets").text()),
                                "timeout": parseInt($("#timeout").text()),
                                "normal_check_interval": parseInt($("#norm_check_interval").text()),
                                "device_id": parseInt($("#device_id").val())
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
                                svc = {"device_id": $("#device_id").val(), "service_id": $(this).prop("value"), "template_id": svc_val};
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
                        //alert(JSON.stringify(service_data));
                        //alert(JSON.stringify(ping_data));

                        // below is the 'service_data' we are passing through ajax
                        /*
                        [
                            {
                                "device_id": "545",
                                "service_id": "14",
                                "template_id": "2",
                                "data_source": [
                                    {
                                        "name": "odu_sn",
                                        "warning": "",
                                        "critical": ""
                                    }
                                ]
                            },
                            {
                                "device_id": "545",
                                "service_id": "10",
                                "template_id": "3",
                                "data_source": [
                                    {
                                        "name": "1",
                                        "warning": "",
                                        "critical": ""
                                    },
                                    {
                                        "name": "2",
                                        "warning": "",
                                        "critical": ""
                                    },
                                    {
                                        "name": "3",
                                        "warning": "",
                                        "critical": ""
                                    },
                                    {
                                        "name": "4",
                                        "warning": "",
                                        "critical": ""
                                    }
                                ]
                            }
                        ]
                         */
                        Dajaxice.device.edit_services(edit_services_message, {'svc_data': service_data, 'svc_ping': ping_data});
                    }
                    else{
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

// hide and show ping based on checkbox selected or not
function hide_and_show_ping() {
    if ($("#ping_checkbox").is(":checked")) {
        $("#ping_svc").show();
    }
    else {
        $("#ping_svc").hide();
    }
}

// display service templates select menu
function show_old_configuration_for_svc_edit(value) {
    id = "#svc_"+value;
    if ($(id).is(":checked")){
        //console.log($(id).prop("value"));
        Dajaxice.device.get_old_configuration_for_svc_edit(Dajax.process, {'option': value, 'service_id': $(id).prop("value"), 'device_id': $('#device_id').val()});
    }
    else {
        $("#template_options_id_"+value+"").empty();
        $("#show_old_configuration_"+value+"").empty();
        $("#show_new_configuration_"+value+"").empty();
    }
}


// display service parameters table
function show_new_configuration_for_svc_edit(value){
    service_id = value;
    template_id = $("#service_template_"+value).val();
    Dajaxice.device.get_new_configuration_for_svc_edit(Dajax.process, {'service_id': service_id, 'template_id': template_id});
}


// show message for service edit success/failure
function edit_services_message(responseResult) {
    bootbox.alert(responseResult.result.message);
}


// delete services from nms core
function get_service_delete_form(content) {
    var service_delete_html = "";

    if (content.result.data.objects.is_added == 1){
        if (content.result.data.objects.master_site == "master_UA") {
            if (!(typeof content.result.data.objects.services === 'undefined') && !(Object.keys(content.result.data.objects.services).length === 0)) {

                // display port select menu
                //service_delete_html += '<h5 class="text-warning">You can edit service for device ' + '"' + content.result.data.objects.device_alias + '" </h5>';
                // show service information
                service_delete_html += '<h5 class="text-warning"><b>Device Info:</b></h5>';
                service_delete_html += '<dl class="dl-horizontal">';
                service_delete_html += '<dt>Device</dt><dd>'+content.result.data.objects.device_alias+'</dd>';
                service_delete_html += '<dt>Services</dt><dd>';
                for (var i = 0, l = content.result.data.objects.services.length; i < l; i++) {
                    service_delete_html += content.result.data.objects.services[i].value+', ' ;
                }
                service_delete_html += '</dd></dl>';
                service_delete_html += '<input type="hidden" id="device_id" value="' + content.result.data.objects.device_id + '" />';

                // service display
                if (!(typeof content.result.data.objects.services === 'undefined')) {
                    service_delete_html += '<label class="control-label"><h5 class="text-warning"><b>Services:</b></h5></label>';
                    for (var i = 0, l = content.result.data.objects.services.length; i < l; i++) {
                        service_delete_html += '<div class="service">';
                        service_delete_html += '<label class="checkbox">';
                        service_delete_html += '<input class="uniform" id="svc_' + content.result.data.objects.services[i].key + '" type="checkbox" value="' + content.result.data.objects.services[i].key + '" onchange="show_old_configuration_for_svc_edit(' + content.result.data.objects.services[i].key + ');">';
                        service_delete_html += '<p class="text-dark">'+content.result.data.objects.services[i].value+'</p>';
                        service_delete_html += '</label>';
                        service_delete_html += '<hr />';
                        service_delete_html += '</div>';
                    }
                    service_delete_html += '</div>';
                }
            }
            else {
                service_delete_html += '<h5 class="text-warning">There are no services for device ' + '"' + content.result.data.objects.device_alias + '"to monitor. </h5>';
            }
        }
        else{
            service_delete_html += content.result.message;
        }
    }
    else{
        service_delete_html += content.result.message;
    }

    bootbox.dialog({
        message: service_delete_html,
        title: "<span class='text-danger'><i class='fa fa-minus'></i> Delete services from nms core.</span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                    //if services are present on then send the call to add service else just hide the bootbox
                    if (!(typeof content.result.data.objects.services === 'undefined') && !(Object.keys(content.result.data.objects.services).length === 0)) {
                        var service_data = [];
                        $(".service").each(function (index) {
                            var $this = $(this);
                            $this.children(".checkbox").find("input:checked").each(function () {
                                service_id = $(this).prop("value");
                                svc = {"device_id": $("#device_id").val(), "service_id": $(this).prop("value")};
                                service_data.push(svc);
                            });
                        });
                        //alert(JSON.stringify(service_data));

                        // below is the 'service_data' we are passing through ajax
                        /*
                        [
                            {
                                "device_id": "545",
                                "service_id": "1"
                            },
                            {
                                "device_id": "545",
                                "service_id": "7"
                            },
                            {
                                "device_id": "545",
                                "service_id": "14"
                            },
                            {
                                "device_id": "545",
                                "service_id": "20"
                            }
                        ]
                         */
                        Dajaxice.device.delete_services(delete_services_message, {'service_data': service_data});
                    }
                    else{
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


// show message for service deletion success/failure
function delete_services_message(responseResult) {
    bootbox.alert(responseResult.result.message);
}

// ********************************** Service Add Functions ***************************************
// add services on nms core
function get_service_add_form(content) {
    var service_add_html = "";

    if (content.result.data.objects.is_added == 1){
        if (content.result.data.objects.master_site == "master_UA") {
            if (!(typeof content.result.data.objects.services === 'undefined') && !(Object.keys(content.result.data.objects.services).length === 0)) {

                // display port select menu
                //service_add_html += '<h5 class="text-warning">You can add service for device ' + '"' + content.result.data.objects.device_alias + '" </h5>';
                // show service information
                service_add_html += '<h5 class="text-warning"><b>Device Info:</b></h5>';
                service_add_html += '<dl class="dl-horizontal">';
                service_add_html += '<dt>Device</dt><dd>'+content.result.data.objects.device_alias+'</dd>';
                service_add_html += '<dt>Services</dt><dd>';
                for (var i = 0, l = content.result.data.objects.services.length; i < l; i++) {
                    service_add_html += content.result.data.objects.services[i].value+', ' ;
                }
                service_add_html += '</dd></dl>';
                service_add_html += '<input type="hidden" id="device_id" value="' + content.result.data.objects.device_id + '" />';

                // service display
                if (!(typeof content.result.data.objects.services === 'undefined')) {
                    service_add_html += '<label class="control-label"><h5 class="text-warning"><b>Services:</b></h5></label>';
                    for (var i = 0, l = content.result.data.objects.services.length; i < l; i++) {
                        service_add_html += '<div class="service">';
                        service_add_html += '<label class="checkbox">';
                        service_add_html += '<input class="uniform" id="svc_' + content.result.data.objects.services[i].key + '" type="checkbox" value="' + content.result.data.objects.services[i].key + '" onchange="show_old_configuration_for_svc_add(' + content.result.data.objects.services[i].key + ');">';
                        service_add_html += '<p class="text-dark">'+content.result.data.objects.services[i].value+'</p>';
                        service_add_html += '</label>';
                        service_add_html += '<div id="template_options_id_' + content.result.data.objects.services[i].key + '" onchange="show_new_configuration_for_svc_add(' + content.result.data.objects.services[i].key + ');"></div>';
                        service_add_html += '<div id="show_new_configuration_' + content.result.data.objects.services[i].key + '"></div>';
                        service_add_html += '<hr />';
                        service_add_html += '</div>';
                    }
                    service_add_html += '</div>';
                }
            }
            else {
                service_add_html += '<h5 class="text-warning">All service are operational for device ' + '"' + content.result.data.objects.device_alias + '". </h5>';
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
        title: "<span class='text-danger'><i class='fa fa-plus'></i> Add services to nms core.</span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                    //if services are present on then send the call to add service else just hide the bootbox
                    if (!(typeof content.result.data.objects.services === 'undefined') && !(Object.keys(content.result.data.objects.services).length === 0)) {
                        var service_data = [];
                        $(".service").each(function (index) {
                            if ($(this).children(".checkbox").find("input:checked").prop('checked')==true) {
                                var $this = $(this);
                                var svc = {};
                                $this.children(".checkbox").find("input:checked").each(function () {
                                    service_id = $(this).prop("value");
                                    svc_val = $("#service_template_" + service_id).val();
                                    svc = {"device_id": $("#device_id").val(), "service_id": $(this).prop("value"), "template_id": svc_val};
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
                        // alert(JSON.stringify(service_data));

                        // below is the 'service_data' we are passing through ajax
                        /*
                        [
                            {
                                "device_id": "545",
                                "service_id": "14",
                                "template_id": "2",
                                "data_source": [
                                    {
                                        "name": "odu_sn",
                                        "warning": "",
                                        "critical": ""
                                    }
                                ]
                            },
                            {
                                "device_id": "545",
                                "service_id": "10",
                                "template_id": "3",
                                "data_source": [
                                    {
                                        "name": "1",
                                        "warning": "",
                                        "critical": ""
                                    },
                                    {
                                        "name": "2",
                                        "warning": "",
                                        "critical": ""
                                    },
                                    {
                                        "name": "3",
                                        "warning": "",
                                        "critical": ""
                                    },
                                    {
                                        "name": "4",
                                        "warning": "",
                                        "critical": ""
                                    }
                                ]
                            }
                        ]
                         */
                        Dajaxice.device.add_services(add_services_message, {'svc_data': service_data});
                    }
                    else{
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
    if ($(id).is(":checked")){
        //console.log($(id).prop("value"));
        Dajaxice.device.get_old_configuration_for_svc_add(Dajax.process, {'option': value, 'service_id': $(id).prop("value"), 'device_id': $('#device_id').val()});
    }
    else {
        $("#template_options_id_"+value+"").empty();
        $("#show_old_configuration_"+value+"").empty();
        $("#show_new_configuration_"+value+"").empty();
    }
}


// display service parameters table
function show_new_configuration_for_svc_add(value){
    service_id = value;
    template_id = $("#service_template_"+value).val();
    Dajaxice.device.get_new_configuration_for_svc_add(Dajax.process, {'service_id': service_id, 'template_id': template_id});
}


// show message for service add success/failure
function add_services_message(responseResult) {
    bootbox.alert(responseResult.result.message);
}


// ********************************** Service Add Functions ***************************************
// add services on nms core
function device_services_status_frame(content) {
    var services_status_html = "";
    services_status_html += '<h5 class="text-warning"><b>Device Info:</b></h5>';
    services_status_html += '<dl class="dl-horizontal">';
    services_status_html += '<dt>Device</dt><dd>'+content.result.data.objects.device_name+'</dd>';
    services_status_html += '<dt>Machine</dt><dd>'+content.result.data.objects.machine+'</dd>';
    services_status_html += '<dt>Site</dt><dd>'+content.result.data.objects.site_instance+'</dd>';
    services_status_html += '<dt>IP Address</dt><dd>'+content.result.data.objects.ip_address+'</dd>';
    services_status_html += '<dt>Device Type</dt><dd>'+content.result.data.objects.device_type+'</dd>';
    services_status_html += '</dd></dl>';
    if (!(typeof content.result.data.objects.active_services === 'undefined') && !(Object.keys(content.result.data.objects.active_services).length === 0)) {
        services_status_html += '<div class=""><div class="box border red"><div class="box-title"><h4><i class="fa fa-table"></i>Operational Services</h4></div>';
        services_status_html += '<div class="box-body"><table class="table">';
        services_status_html += '<thead><tr><th>Service</th><th>Data Sources</th></tr></thead>';
        services_status_html += '<tbody>';
        for (var i = 0, l = content.result.data.objects.active_services.length; i < l; i++) {
            services_status_html += '<tr>';
            services_status_html += '<td>'+content.result.data.objects.active_services[i].service+'</td>';
            services_status_html += '<td>'+content.result.data.objects.active_services[i].data_sources+'</td>';
            services_status_html += '</tr>';
        }
        services_status_html += '</tbody></table>';
        services_status_html += '</div></div></div>';
    }
    else{
        services_status_html += '<div class=""><div class="box border red"><div class="box-title"><h4><i class="fa fa-table"></i>Operational Services</h4></div>';
        services_status_html += '<div class="box-body"><table class="table">';
        services_status_html += '<thead><tr><th>Service</th><th>Data Sources</th></tr></thead>';
        services_status_html += '<tbody>';
        services_status_html += '<tr>';
        services_status_html += '<td align="right"><span class="text-danger">No service is operational on this device or there is no service for this device.</span></td>';
        services_status_html += '</tr>';
        services_status_html += '</tbody></table>';
        services_status_html += '</div></div></div>';
    }

    if (!(typeof content.result.data.objects.inactive_services === 'undefined') && !(Object.keys(content.result.data.objects.inactive_services).length === 0)) {
        services_status_html += '<div class=""><div class="box border orange"><div class="box-title"><h4><i class="fa fa-table"></i>Non Operational Services</h4></div>';
        services_status_html += '<div class="box-body"><table class="table">';
        services_status_html += '<thead><tr><th>Service</th><th>Data Sources</th></tr></thead>';
        services_status_html += '<tbody>';
        for (var i = 0, l = content.result.data.objects.inactive_services.length; i < l; i++) {
            services_status_html += '<tr>';
            services_status_html += '<td>'+content.result.data.objects.inactive_services[i].service+'</td>';
            services_status_html += '<td>'+content.result.data.objects.inactive_services[i].data_sources+'</td>';
            services_status_html += '</tr>';
        }
        services_status_html += '</tbody></table>';
        services_status_html += '</div></div></div>';
    }
    else{
        services_status_html += '<div class=""><div class="box border orange"><div class="box-title"><h4><i class="fa fa-table"></i>Non Operational Services</h4></div>';
        services_status_html += '<div class="box-body"><table class="table">';
        services_status_html += '<thead><tr><th>Service</th><th>Data Sources</th></tr></thead>';
        services_status_html += '<tbody>';
        services_status_html += '<tr>';
        services_status_html += '<td align="right"><span class="text-danger">All services are operational for this device or there is no service for this device.</span></td>';
        services_status_html += '</tr>';
        services_status_html += '</tbody></table>';
        services_status_html += '</div></div></div>';
    }

    bootbox.dialog({
        message: services_status_html,
        title: "<span class='text-danger'><i class='fa fa-list-alt'></i> Device Services Status</span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
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
    });
    }