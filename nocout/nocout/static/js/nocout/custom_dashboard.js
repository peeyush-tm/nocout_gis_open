/**
 * This library is used to show Custom Dashboard made by the user or public dashboard.
 * @for custom_dashboard.js
 */

 /**
 * This function is used to create the custom dashboard as per the data entered by the user
 * @method create_custom_dashboard
 * @param post_data {Object}, It contains the latest post object
 */      
function create_custom_dashboard(post_data) {
 // Make Ajax Call
    $.ajax({
        url : base_url+"/"+"api/get_data_source_save/",
        type: "POST",                                
        data: post_data,
        success : function(response) {
            var result = response;
            var poll_now_data_dict = {};
            if (typeof(response) == 'string') {
                result = JSON.parse(result);
            }

            if (result['success']) {
                var count = $("#custom_dashboard_container .left_tabs_container li").length ? $("#custom_dashboard_container .left_tabs_container li").length:0,
                    unique_item_key = "custom_dashboard_tab"+ '_' + String(count)+ '_' + "10",
                    fields = typeof(result['data']) == 'string' ? JSON.parse(result['data'])[0] : result['data'][0],
                    active_tab_id = unique_item_key,
                    inner_inner_tabs=[],
                    inner_tab_ids = [];

                var tab_info_obj = {
                        'active_class' : "",
                        'unique_key' : unique_item_key,
                        'icon_class' : 'fa fa-dot-circle-o ',
                        'api_url' : 'performance/custom_dashboard/'+fields['pk']+'/device/'+current_device,
                        'title' : post_data['custom_alias']
                    },
                    content_info_obj = {
                        'active_class' : "",
                        'unique_key' : "custom_dashboard_tab"+ '_' + String(count)+ '_' + "10",
                        'show_last_updated' : false,
                    };

                var custom_tabs = perfInstance.make_tab_li_html(tab_info_obj);
               
                if($("#custom_dashboard_container div").hasClass("no_custom")){                        
                    $(".no_custom").remove();
                    $('#custom_dashboard_container .left_tabs_container li:first-child').trigger('click');
                }
                if (tab_info_obj){
                    count++;                        
                }                                                
                
                $("#custom_dashboard_container .left_tabs_container").append(custom_tabs);
                
                var custom_tabs_data  = '';

                custom_tabs_data += '<div class="tab-pane ' + content_info_obj["active_class"]+ '" id="' + unique_item_key+ '_block">';
                custom_tabs_data += '<div class="tabbable"><ul class="nav nav-tabs inner_inner_tab">';
                
                if(show_historical_on_performance) {
                    // inner_inner_tabs = tabs_with_historical;
                    inner_inner_tabs = inner_inner_tabs.concat(live_data_tab);                        
                    inner_inner_tabs = inner_inner_tabs.concat(tabs_with_historical);                        
                }
                   
                if (inner_inner_tabs && inner_inner_tabs.length > 0) {
                    for(var x=0;x<inner_inner_tabs.length;x++) {
                        var inner_active_class = '';
                        // if (x == 0) {
                        //     inner_active_class = 'active';
                        // }
                        var current_item = inner_inner_tabs[x],
                            id = current_item.id,
                            title = current_item.title,
                            data_url = "";
                        if (!current_item["disabled_url"]) {
                            if (tab_info_obj["api_url"].indexOf('?') == -1) {
                                data_url = tab_info_obj["api_url"] + "?data_for=" + id        
                            } else {
                                data_url = tab_info_obj["api_url"] + "&data_for=" + id
                            }
                        }
                        var inner_tab_info_obj = {
                            'active_class' : inner_active_class,
                            'unique_key' : id + "_" + unique_item_key,
                            'icon_class' : 'fa fa-clock-o',
                            'api_url' : data_url,
                            'title' : title
                        };

                        if(!poll_now_data_dict[inner_tab_info_obj["unique_key"]]) {
                            poll_now_data_dict[inner_tab_info_obj["unique_key"]] = [];
                        }

                        custom_tabs_data += perfInstance.make_tab_li_html(inner_tab_info_obj);
                        if (inner_tab_ids.indexOf(id) == -1) {
                            inner_tab_ids.push(id);
                        }
                    }

                } else {
                    var inner_tab_info_obj = {
                        'active_class' : '',
                        'unique_key' : "live_" + unique_item_key,
                        'icon_class' : 'fa fa-caret-right',
                        'api_url' : tab_info_obj["api_url"] + "?data_for=live",
                        'title' : "Live"
                    };

                    custom_tabs_data += perfInstance.make_tab_li_html(inner_tab_info_obj);
                    inner_tab_ids.push('live');
                }
                
                custom_tabs_data += '</ul><div class="divide-20"></div><div class="tab-content">';
                // CREATE SUB INNER TAB CONTENT HTML
                for(var y=0;y<inner_tab_ids.length;y++) {
                    var current_key = inner_tab_ids[y],
                        inner_content_info_obj = {
                            'tab_id' : current_key,
                            'active_class' : '',
                            'unique_key' : current_key + "_" + unique_item_key,
                            'show_last_updated' : false
                        };
                    
                    custom_tabs_data += perfInstance.make_tab_content_html(inner_content_info_obj);
                }
                    custom_tabs_data += '</div></div><div class="clearfix"></div></div>';                     
                   
                $("#custom_dashboard_container > .tabbable > .tab-content").append(custom_tabs_data);                    
               
                bootbox.hideAll();                    
            } else {
                if (result['message'].indexOf(' title ') > -1) {
                    $("#custom_alias_error").html(result['message']);
                    $("#custom_alias_error").removeClass('hide');
                } else if (result['message'].indexOf(' name ') > -1) {
                    $("#custom_name_error").html(result['message']);
                    $("#custom_name_error").removeClass('hide');
                }
            }                                                                 
        },
        error: function (err) {
          
        },
        complete: function () {
            // Hide loading spinner
            hideSpinner();                                
        }                        
    });
}

/**
 * This event trigger when custom_dashboard block clicked
 * @event click
 */
$("#custom_dashboard").click(function (e) {
    var count = $("#custom_dashboard_container .left_tabs_container li").length
    if(!$('#service_view_type_btn').hasClass('hide')) {
        $('#service_view_type_btn').addClass('hide');
    }
    if(!$('#item_type_btn').hasClass('hide')) {
        $('#item_type_btn').addClass('hide');
    }
    if(is_viewer){
        $("#custom_dashboard_container .control_btn_countainer").addClass("hide")
    }                       
    if(count == 0){
        if(!$("#custom_dashboard_container div").hasClass("no_custom")){
             $("#custom_dashboard_container").append('<div class="no_custom">No Custom Dashboards added.</div>')
         }              
    }    
});

/**
 * This event trigger when addition button of custom dashboard is clicked.
 * @event click
 */
$("#add_custom_dashboard").on('click', function () {
    //Call the bootbox to show the popup          
    var popup_html = "";
   
    popup_html += " <div class='add_custom_container' style='position:relative;overflow:auto;'>\
                        <div class='form-horizontal col-md-8 col-md-offset-2' id='custom_dashboard_form'> \
                            <div class='form-group'>\
                                <label for='custom_name'>Name <span class='mandatory'>* </span> </label>\
                                <input type='text' class='multiSelectBox form-control' id='custom_name' style='width:100%;'> \
                                <div class='error_msg hide text-danger' id='custom_name_error'></div> \
                            </div>\
                            <div class='form-group'> \
                                <label for='custom_alias'>Alias <span class='mandatory'>* </span> </label>\
                                <input type='text' class='multiSelectBox form-control' id='custom_alias' style='width:100%;'>\
                                <div class='error_msg hide text-danger' id='custom_alias_error'></div> \
                            </div>\
                            <div class='form-group'> \
                                <label for='display_type'>\
                                    Display Type <span class='mandatory'>*</span>\
                                </label>\
                                <div> \
                                    <input type='radio' name='display_type' value='table' > Table &nbsp; \
                                    <input type='radio' name='display_type' value='Chart' checked='checked'> Chart \
                                </div> \
                            </div>\
                            <div class='form-group'> \
                                <label for='datasource'>\
                                    Datasources <span class='mandatory'>*</span>\
                                </label>\
                                <input type='hidden' class='multiSelectBox' id='select_datasource' style='width:100%;'> \
                                <div class='error_msg hide text-danger' id='custom_datasource_error'></div> \
                            </div>\
                            <div class='form-group'> \
                                <label for='is_public' >Is Public:</label>\
                                <input type='checkbox' class='' id='select_is_public'> \
                            </div>\
                        </div> \
                    </div>";



    var add_db_box =bootbox.dialog({
        message: popup_html,
        title: 'Create New Dashboard',
        buttons: {
            success: {
            label: "Save",
            className: "btn-default ",
                callback: function() {
                    var custom_dashboard_name = $("#custom_name").val() ? $.trim($("#custom_name").val()) : '',
                        custom_dashboard_alias = $("#custom_alias").val() ? $.trim($("#custom_alias").val()) : '',
                        selected_datasource = $("#select_datasource").select2('val'),
                        selected_type = $('input[name=display_type]:checked').val() ? $('input[name=display_type]:checked').val().toLowerCase():"";
                        is_public_dashboard = $('#select_is_public').is(':checked')? 1: 0,
                        data = {results: []};
                        // Custom Dashboard Addition Form Validation
                    if (!custom_dashboard_name || custom_dashboard_name.indexOf(' ') > -1) {
                        $("#custom_name_error").html('Please enter valid name. Name only contains alphanumeric character, underscore & hyphen.');
                        $("#custom_name_error").removeClass('hide');
                        return false;
                    } else {
                        $("#custom_name_error").html('');
                        $("#custom_name_error").addClass('hide');
                    }
                    if (!custom_dashboard_alias) {
                        $("#custom_alias_error").html('Please enter alias of Custom Dashboard. ');
                        $("#custom_alias_error").removeClass('hide');
                        return false;
                    } else {
                        $("#custom_alias_error").html('');
                        $("#custom_alias_error").addClass('hide');
                    }                            
                    if ((selected_datasource.length!=2 && selected_type == "chart")) {
                        $("#custom_datasource_error").html('Please select 2 datasources. Only 2 datasources can be selected for Chart Display.');
                        $("#custom_datasource_error").removeClass('hide');
                        return false;                       
                        } else {
                        $("#custom_datasource_error").html('');
                        $("#custom_datasource_error").addClass('hide');
                    }
                    if ((selected_datasource.length<2 && selected_type == "table")) {
                        $("#custom_datasource_error").html('Please select atleast 2 datasources.');
                        $("#custom_datasource_error").removeClass('hide');
                        return false;                       
                        } else {
                        $("#custom_datasource_error").html('');
                        $("#custom_datasource_error").addClass('hide');
                    }
                    if (!selected_datasource || selected_datasource.length < 1 ) {
                        $("#custom_datasource_error").html('Please select datasource');
                        $("#custom_datasource_error").removeClass('hide');
                        return false;
                    } else {
                        $("#custom_datasource_error").html('');
                        $("#custom_datasource_error").addClass('hide');
                    }
                    // Show loading spinner
                    showSpinner();
                    //Data entered by the user 
                    var post_data = {
                        "custom_name":  custom_dashboard_name ,
                        "custom_alias":  custom_dashboard_alias,
                        "ds_name": selected_datasource,
                        "selected_type": selected_type,
                        "is_public_dashboard": JSON.stringify(is_public_dashboard)
                    };

                    create_custom_dashboard(post_data);

                    return false;
                }
        },
        danger: {
          label: "Cancel",
          className: "btn-default",
            callback: function() {
            }
        }
    }

    

	});        

    $(".modal-dialog").css("width","60%");      

    $("#select_datasource").select2({
        multiple: true,
        minimumInputLength: 3,
        query: function (query) {
            var search_txt = query.term,
                selected_type = $('input[name=display_type]:checked').val().toLowerCase(),
                name=$('input[id=select_custom_name]').val(),
                selected_datasource =$("input[id='select_datasource']").val().split(',').length;

            
            var data = {results: []};           
            // <AJAX_CALL>
            $.ajax({                        
                url : base_url+"/"+"api/get_data_source/?display_type="+selected_type+"&search="+search_txt,
                success : function(response) {                                
                    data.results = response;
                    query.callback(data);
                },
                error: function (err) {
                    query.callback(data);
                    }                        
                });       
        }
    });
});          

/**
 * This event trigger when delete button is clicked
 * @event click
 */
$("#delete_custom_dashboard").on('click', function () {
   var count = $("#custom_dashboard_container .left_tabs_container li").length?$("#custom_dashboard_container .left_tabs_container li").length:0;
   var popup_html = "";                            

    popup_html += "<div class='delete_custom_container' style='position:relative;overflow:auto;'> \
                        <div class='form-group'> \
                            <label for='datasource'> \
                                Custom Dashboard<span class='mandatory'>*</span> \
                            </label> \
                            <select multiple='multiple' class='select2select' id='delete_customdb' style='width:100%;'> \
                            </select> \
                            <div class='error_msg hide text-danger' id='delete_customdb_error'>\
                        </div> \
                    </div>"

    //Call the bootbox to show the popup with datatable
    var delete_db_box = bootbox.dialog({
        message: popup_html,
        title: 'Delete Custom Dashboards',
        buttons: {
            success: {
                label: "Delete",
                className: "btn-default ",
                callback: function() {                            
                    var select_box= $("#delete_customdb option:selected")?$("#delete_customdb option:selected"):"";
                        selected_ids = [],
                        selected_txt = [];    
                        select_box.each(function(){
                            selected_ids.push($(this).val());
                            selected_txt.push($(this).text())
                        });

                        //Validation
                        if (!selected_ids || selected_ids.length === 0) {                                    
                            $("#delete_customdb_error").html('Please enter custom dashboard to be deleted');
                            $("#delete_customdb_error").removeClass('hide');
                            return false;
                        } else {
                            $("#delete_customdb_error").html('');
                            $("#delete_customdb_error").addClass('hide');
                        }
                        // Show loading spinner
                        showSpinner()
                         // Make Ajax Call
                        $.ajax({                                
                        url : base_url+"/"+"api/get_data_source_delete/",
                        type: "POST",                                
                        data: {
                            selected_db : selected_ids
                        },
                        success : function(data) {                                 
                        var result = "";
                       
                        
                        },
                        error: function (err) {
                          
                            },
                        complete: function () {
                            // Hide loading spinner
                            hideSpinner();                                
                            bootbox.alert("Custom Dashboard "+selected_txt+" deleted");
                            if(!selected_txt.length == 0) {
                                $.each(selected_txt, function(index, value){                                    
                                    //Append each added dashboard to the custom dashboard list
                                    var left_tab_dom = $('#custom_dashboard_container .left_tabs_container li').filter(function() {
                                            return $.trim($.text([this])) === value;
                                        }),
                                        content_dom_id = left_tab_dom.children('a').attr('href');
                                        
                                    left_tab_dom.remove();
                                    $(content_dom_id).remove();

                                    if ($('#custom_dashboard_container .left_tabs_container li').length > 0) {
                                        $('#custom_dashboard_container .left_tabs_container li:first-child').trigger('click');
                                    }
                                    else{
                                        if(!$("#custom_dashboard_container div").hasClass("no_custom")){
                                            $("#custom_dashboard_container").append('<div class="no_custom">No Custom Dashboards added.</div>')
                                        }                                
                                    
                                    }
                                });
                            }                         
                        }                        
                        });    

                    
                }
            },
            danger: {
              label: "Cancel",
              className: "btn-default",
              callback: function() {
                
              }
            }
        }    
    });

    delete_db_box.on("shown.bs.modal", function() {
         // Make Ajax Call
        $("#delete_customdb").select2();
        $.ajax({                    
                url : base_url+"/"+"api/get_data_source_list/",
                type: "GET",                            
                success : function(response) {                                
                    var result ="";                            
                    
                    if (typeof response == 'string') {
                        result = JSON.parse(response);
                        } else {
                        result = response;
                        }
                    if (result['success']){
                        var option_html = '';
                        var objects = result['data']['objects'];                           
                                              
                        $("#delete_customdb").select2('enable');
                        for (var x=0;x<objects.length;x++) {
                            var existing_keys = Object.keys(objects[x]).filter(function(items) {return items != 'id'}),
                            alias_key = existing_keys.indexOf('title') > -1 ? 'title' : existing_keys[0];                        
                            option_html += '<option value="' + objects[x].id + '" ' +  '>' + objects[x][alias_key] + '</option>';
                            $("#delete_customdb").html(option_html);                                
                        }
                    }                                           
                    else{
                        $("#delete_customdb_error").html('No Custom Dashboards to be deleted.');
                        $("#delete_customdb_error").removeClass('hide');
                        return false;
                    }                          
                try {
                    // Enable the selector                            
                    $("#delete_customdb").select2('val', selected_id);
                } catch(e) {
                    // console.error(e);
                }
            },           
        });                  
    });

    $(".modal-dialog").css("width","60%");          
        
});