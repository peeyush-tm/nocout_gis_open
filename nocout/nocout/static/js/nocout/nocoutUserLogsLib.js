/**
 * This file call API to save user logs on create & edit operation on any item
 * @for nocoutUserLogsLib
 */

// If formContainer class present then proceed
if($(".formContainer").length) {

    var splitted_url_list = window.location.pathname.split("/"),
        notGisWizard = splitted_url_list.indexOf('gis-wizard') < 0,
        notL2Report = splitted_url_list.indexOf('l2_reports') < 0,
        isNewForm = splitted_url_list.indexOf('new') > -1 && notGisWizard && notL2Report,
        isCreateForm = splitted_url_list.indexOf('create') > -1 && notGisWizard && notL2Report,
        isAddForm = splitted_url_list.indexOf('add') > -1 && notGisWizard && notL2Report,
        isEditForm = splitted_url_list.indexOf('edit'),
        isUpdateForm = splitted_url_list.indexOf('update'),
        isModifyForm = splitted_url_list.indexOf('modify'),
        // wizard_condition_3 = splitted_url_list.indexOf('gis-wizard') > -1,
        // isDeviceTypeWizard =  (wizard_condition_1) || (wizard_condition_2 && wizard_condition_3),
        wizard_condition_1 = window.location.href.indexOf('wizard/device-type') > -1,
        wizard_condition_2 = !isNaN(splitted_url_list[splitted_url_list.length-1]),
        isDeviceTypeWizard =  wizard_condition_1,
        page_title = "",
        module_name = "",
        isFormSubmit = 0;

    if(isCreateForm || isNewForm || isAddForm) {
        
        page_title = $(".formContainer .box .box-title h4")[0].innerHTML.toLowerCase().split(" add ");

        try {
            module_name = page_title.join(' ').split("</i>")[1].toUpperCase();
        } catch(e) {
            module_name = page_title.join(' ');
        }

    } else if(isEditForm > -1 || isUpdateForm > -1 || isModifyForm > -1 || isDeviceTypeWizard) {

        page_title = $(".formContainer .box .box-title h4")[0] ? $(".formContainer .box .box-title h4")[0].innerHTML.toLowerCase().split(" edit ") : "";
        try {
            module_name = page_title.join(' ').split("</i>")[1].toUpperCase();
        } catch(e) {
            module_name = page_title.join(' ');
        }

        if(isFormSubmit === 0) {
            var oldFieldsArray = [];
            // SetTimeout is used to delay the code execution so that the all the fields will be prepared
            setTimeout(function() {
                oldFieldsArray = prepareFormData();
            },500);
        }
    }
}

/*Form Submit Event*/
$("form").submit(function(e) {

    if(notGisWizard && notL2Report) {
        // Disabel submit button
        if($("form button[type='submit']").length > 0) {
            if(!$("form button[type='submit']").hasClass("disabled")) {
                $("form button[type='submit']").addClass("disabled");
            }
        }
        /*Create case*/
        if(isCreateForm || isNewForm || isAddForm) {
            /*When first time form submitted*/
            if(isFormSubmit === 0) {

                page_title = $(".formContainer .box .box-title h4")[0].innerHTML.toLowerCase().split(" add ");
                try {
                    module_name = page_title.join(' ').split("</i>")[1].toUpperCase();
                } catch(e) {
                    module_name = page_title.join(' ');
                }

                var alias = $("form input[name*='alias']").val(),
                    shown_val = alias ? alias : $("form input[name*='name']").val();
                
                if(!shown_val) {
                    shown_val = "";
                }

                var action = "A new "+module_name.toLowerCase()+" is created - "+shown_val,
                action_response = "";

                /*Call function to save user action*/
                save_user_action(module_name,action,function(result) {
                    action_response = result;
                    if(typeof result == 'string' && result.indexOf('success') > -1) {
                        action_response = JSON.parse(result);
                    } else {
                        action_response = result;
                    }
                    isFormSubmit = 1;
                    // Enable submit button
                    if($("form button[type='submit']").length > 0) {
                        if($("form button[type='submit']").hasClass("disabled")) {
                            $("form button[type='submit']").removeClass("disabled");
                        }
                    }
                    /*Trigger Form Submit*/
                    $("form").trigger('submit');
                });
            } else {
                // Enable submit button
                if($("form button[type='submit']").length > 0) {
                    if($("form button[type='submit']").hasClass("disabled")) {
                        $("form button[type='submit']").removeClass("disabled");
                    }
                }
                return true;
            }
        /*Edit case*/
        } else if(isEditForm > -1 || isUpdateForm > -1 || isModifyForm > -1 || isDeviceTypeWizard) {
            /*When first time form submitted*/
            if(isFormSubmit === 0) {

                page_title = $(".formContainer .box .box-title h4")[0] ? $(".formContainer .box .box-title h4")[0].innerHTML.toLowerCase().split(" edit ") : "";
                try {
                    module_name = page_title.join(' ').split("</i>")[1].toUpperCase();
                } catch(e) {
                    module_name = page_title.join(' ');
                }

                var modifiedFieldsStr = "[";
                    // Prepare 'newFieldsArray'
                var newFieldsArray = prepareFormData();;


                /*Get Modified Fields*/
                for(var j=0;j<oldFieldsArray.length;j++) {
                    var old_field = oldFieldsArray[j],
                        new_field = newFieldsArray[j];

                    if(old_field && old_field.value != undefined && new_field && new_field.value != undefined) {
                        if($.trim(old_field.value) != $.trim(new_field.value) && old_field.name.indexOf('password') === -1) {
                            var new_val = new_field.value.toLowerCase() != 'select' ? new_field.value : "",
                                old_val = old_field.value.toLowerCase() != 'select' ? old_field.value : "",
                                modified_str = old_field.name+"{"+old_val+" To "+new_val+"}";
                            if($.trim(modifiedFieldsStr) != '[') {
                                modifiedFieldsStr += ","+modified_str;
                            } else {
                                modifiedFieldsStr += modified_str;
                            }
                        }
                    }
                }

                /*If any changes done then save user action else return.*/
                if($.trim(modifiedFieldsStr) != '[') {
                    
                    modifiedFieldsStr += ']';
                    /*Call function to save user action*/
                    save_user_action(module_name,modifiedFieldsStr,function(result) {
                        if(typeof result == 'string' && result.indexOf('success') > -1) {
                            action_response = JSON.parse(result);
                        } else {
                            action_response = result;
                        }

                        isFormSubmit = 1;
                        // Enable submit button
                        if($("form button[type='submit']").length > 0) {
                            if($("form button[type='submit']").hasClass("disabled")) {
                                $("form button[type='submit']").removeClass("disabled");
                            }
                        }
                        /*Trigger Form Submit*/
                        $("form").trigger('submit');
                    });
                } else {
                    // Enable submit button
                    if($("form button[type='submit']").length > 0) {
                        if($("form button[type='submit']").hasClass("disabled")) {
                            $("form button[type='submit']").removeClass("disabled");
                        }
                    }
                    return true;
                }
            } else {
                // Enable submit button
                if($("form button[type='submit']").length > 0) {
                    if($("form button[type='submit']").hasClass("disabled")) {
                        $("form button[type='submit']").removeClass("disabled");
                    }
                }
                return true;
            }
        } else {
            // Enable submit button
            if($("form button[type='submit']").length > 0) {
                if($("form button[type='submit']").hasClass("disabled")) {
                    $("form button[type='submit']").removeClass("disabled");
                }
            }
            return true;
        }
        return false;
    }
});

/**
 * This function prepares form data required for user logs
 * @method prepareFormData
 * @return form_data {Array}, It contains the complete form items data
 */
function prepareFormData() {
    var form_data = [];

    var input_boxes = $("form input:not([type='hidden']):not([type='checkbox']):not([type='password'])"),//.serializeArray(),
        select_boxes = $("form select"),
        checkbox_boxes = $("form input[type='checkbox']"),
        text_area_fields = $("form textarea");

    var input_boxes_data = prepareInputBoxesData(input_boxes),
        select_boxes_data = prepareSelectBoxesData(select_boxes),
        text_areas_data = prepareTextareaData(text_area_fields),
        checkboxes_data = prepareCheckboxesData(checkbox_boxes);

    // Concat all Data
    form_data = form_data.concat(select_boxes_data);
    form_data = form_data.concat(input_boxes_data);
    form_data = form_data.concat(text_areas_data);
    form_data = form_data.concat(checkboxes_data);

    return form_data;
}

/**
 * This function prepares input box(textbox) data dict array for user logs
 * @method prepareInputBoxesData
 * @param input_boxes {Array}, It contains the checkboxes object array.
 * @return inputbox_data {Array}, It contains the checkbox data in format 
   which is needed for user logs
 */
function prepareInputBoxesData(input_boxes) {

    var inputbox_data = [],
        label_count_dict = {},
        labels_array = [];

    if(!input_boxes) {
        return inputbox_data;
    }

    // Loop checkboxes
    for(var i=0;i<input_boxes.length;i++) {
        if (input_boxes[i].attributes["name"]) {
            var inputbox_name = input_boxes[i].attributes["name"].value,
                inputbox_id = input_boxes[i].attributes["id"].value,
                field_title = '';
            
            try {
                // Field Label
                field_title = $(input_boxes[i]).closest('.form-group').find('label').text();
                // Remove mandatory icon if exists
                if (field_title.indexOf('*') > -1) {
                    field_title = $.trim(field_title.replace('*',''));
                }
                if (field_title.indexOf('( null )') > -1) {
                    field_title = $.trim(field_title.replace('( null )',''));
                }

                var white_space = ' ',
                    re = new RegExp(white_space, 'g'),
                    title_key = field_title.replace(re, '');

                // Counter for same label fields
                if (label_count_dict[title_key]) {
                    label_count_dict[title_key] += 1
                } else {
                    label_count_dict[title_key] = 1
                }

                if (labels_array.indexOf(field_title) == -1) {
                    labels_array.push(field_title);
                } else {
                    field_title += ' ' + String(label_count_dict[title_key]);
                }
            } catch(e) {
                field_title = inputbox_name;
            }

            if(field_title && inputbox_id) {
                var data_obj = {
                    "name" : field_title,
                    "value" : $('#' + inputbox_id).val()
                };

                inputbox_data.push(data_obj);
            }
        }
    }

    return inputbox_data;
}

/**
 * This function prepares checkboxes data dict array for user logs
 * @method prepareCheckboxesData
 * @param checkbox_boxes {Array}, It contains the checkboxes object array.
 * @return checkbox_data {Array}, It contains the checkbox data in format 
   which is needed for user logs
 */
function prepareCheckboxesData(checkbox_boxes) {

    var checkbox_data = [],
        label_count_dict = {},
        labels_array = [];

    if(!checkbox_boxes) {
        return checkbox_data;
    }

    // Loop checkboxes
    for(var i=0;i<checkbox_boxes.length;i++) {
        var checkbox_name = checkbox_boxes[i].attributes["name"].value,
            checkbox_id = checkbox_boxes[i].attributes["id"].value,
            isChecked = $("#"+checkbox_id)[0].checked,
            checkbox_val = isChecked ? $("#"+checkbox_id).val() : "off",
            field_title = '';
        
        try {
            // Field Label
            field_title = $(checkbox_boxes[i]).closest('.form-group').find('label').text();
            // Remove mandatory icon if exists
            if (field_title.indexOf('*') > -1) {
                field_title = $.trim(field_title.replace('*',''));
            }

            var white_space = ' ',
                re = new RegExp(white_space, 'g'),
                title_key = field_title.replace(re, '');

            // Counter for same label fields
            if (label_count_dict[title_key]) {
                label_count_dict[title_key] += 1
            } else {
                label_count_dict[title_key] = 1
            }

            if (labels_array.indexOf(field_title) == -1) {
                labels_array.push(field_title);
            } else {
                field_title += ' ' + String(label_count_dict[title_key]);
            }
        } catch(e) {
            field_title = checkbox_name;
        }

        if(field_title && checkbox_id) {
            var data_obj = {
                "name" : field_title,
                "value" : checkbox_val
            };

            checkbox_data.push(data_obj);
        }
    }

    return checkbox_data;
}

/**
 * This function prepares textareas data dict array for user logs
 * @method prepareTextareaData
 * @param text_area_fields {Array}, It contains the textareas object array.
 * @return textarea_data {Array}, It contains the textarea data in format 
   which is needed for user logs
 */
function prepareTextareaData(text_area_fields) {

    var textarea_data = [];

    if(!text_area_fields) {
        return textarea_data;
    }

    var label_count_dict = {},
        labels_array = [];

    // Loop Textareas
    for(var i=0;i<text_area_fields.length;i++) {
        var textarea_name = text_area_fields[i].attributes["name"].value,
            textarea_id = text_area_fields[i].attributes["id"].value,
            field_title = '';
        
        try {
            // Field Label
            field_title = $(text_area_fields[i]).closest('.form-group').find('label').text();
            // Remove mandatory icon if exists
            if (field_title.indexOf('*') > -1) {
                field_title = $.trim(field_title.replace('*',''));
            }

            var white_space = ' ',
                re = new RegExp(white_space, 'g'),
                title_key = field_title.replace(re, '');

            // Counter for same label fields
            if (label_count_dict[title_key]) {
                label_count_dict[title_key] += 1
            } else {
                label_count_dict[title_key] = 1
            }

            if (labels_array.indexOf(field_title) == -1) {
                labels_array.push(field_title);
            } else {
                field_title += ' ' + String(label_count_dict[title_key]);
            }
        } catch(e) {
            field_title = textarea_name;
        }

        if(field_title && textarea_id) {
            var data_obj = {
                "name" : field_title,
                "value" : $("#"+textarea_id).val()
            };

            textarea_data.push(data_obj);
        }
    }

    return textarea_data;
}


/**
 * This function prepares select boxes data dict array for user logs
 * @method prepareSelectBoxesData
 * @param select_boxes {Array}, It contains the select boxes object array.
 * @return select_boxes_data {Array}, It contains the selectbox data in format 
   which is needed for user logs
 */
function prepareSelectBoxesData(select_boxes) {
    var select_boxes_data = [];

    if(!select_boxes) {
        return select_boxes_data;
    }
    var labels_array = [],
        label_count_dict = {};
    // Loop select boxes
    for(var i=0;i<select_boxes.length;i++) {
        var select_id = select_boxes[i].attributes["id"].value,
            isSelect2 = $("#"+select_id)[0].className.indexOf('select2') > -1,
            values_array = isSelect2 ? $("#"+select_id).select2("data") : $("#"+select_id+" option:selected").text(),
            field_name = select_boxes[i].attributes["name"].value,
            selected_values = "";

        if(values_array && values_array.constructor == Array) {
            $.grep(values_array,function(data){
                if(selected_values.length > 0) {
                    selected_values +=  data.text ? ","+data.text : "";
                } else {
                    selected_values += data.text ? data.text : "";
                }
            });
        } else {
            if(typeof values_array == 'object') {
                selected_values = values_array ? values_array.text : "";
                if(values_array) {
                    // For some select2 the key is device_alias not text.
                    if(!selected_values && values_array.hasOwnProperty('device_alias')) {
                        selected_values = values_array['device_alias'];
                    }
                }
            } else {
                selected_values = values_array;
            }
        }
        var field_title = '';
        
        try {
            // Field Label
            field_title = $(select_boxes[i]).closest('.form-group').find('label').text();
            // Remove mandatory icon if exists
            if (field_title.indexOf('*') > -1) {
                field_title = $.trim(field_title.replace('*',''));
            }

            var white_space = ' ',
                re = new RegExp(white_space, 'g'),
                title_key = field_title.replace(re, '');

            // Counter for same label fields
            if (label_count_dict[title_key]) {
                label_count_dict[title_key] += 1
            } else {
                label_count_dict[title_key] = 1
            }

            if (labels_array.indexOf(field_title) == -1) {
                labels_array.push(field_title);
            } else {
                field_title += ' ' + String(label_count_dict[title_key]);
            }
        } catch(e) {
            field_title = field_name;
        }

        var data_obj = {
            "name" : field_title,
            "value" : selected_values
        };
        select_boxes_data.push(data_obj);
    }

    return select_boxes_data;
}


/**
 * This function save user action by calling respective API.
 * @method save_user_action
 */
function save_user_action(module,action,callback) {

    var csrftoken = $.cookie("csrftoken"),
        base_url = "";

    /*Set the base url of application for ajax calls*/
    if(window.location.origin) {
        base_url = window.location.origin;
    } else {
        base_url = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
    }

    $.ajax({
        url : base_url+"/logs/actions/log/", 
        type : "POST",
        dataType: "json", 
        data : {
            module : module,
            action : action,
            csrfmiddlewaretoken : csrftoken,
        },
        success : function(response) {     
            callback(response);
        },
        error : function(xhr,errmsg,err) {
            callback(xhr.status + ": " + xhr.responseText)
        }
    });
}