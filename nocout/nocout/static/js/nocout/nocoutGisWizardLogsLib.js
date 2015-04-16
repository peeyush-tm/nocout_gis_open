/**
 * This file call API to save user logs on create & edit operation for only GIS wizard
 * @for nocoutUserLogsLib
 */

var splitted_url_list = window.location.pathname.split("/"),
    isGisWizard = splitted_url_list.indexOf('gis-wizard') > -1,
    sub_module_name = "",
    sub_module_title_key_dict = {
        "form_1" : "sector_configured_on",
        "form_2" : "sector_id",
        "form_3" : "sector_id",
        "form_4" : "device",
        "form_5" : "device",
        "form_6" : "circuit_id",
        "form_7" : "alias",
        "ss_form_1" : "device",
        "ss_form_2" : "device",
        "ss_form_3" : "device",
        "ss_form_4" : "circuit_id",
        "ss_form_5" : "alias"
    };



    
// If formContainer class present then proceed
// If gis wizard form, only then proceed
if($(".formContainer").length > 0 && isGisWizard) {

    var isNewWizardForm = window.location.href.indexOf('new') > -1,
        isCreateWizardForm = window.location.href.indexOf('create') > -1,
        isAddWizardForm = window.location.href.indexOf('add') > -1,
        wizard_edit_condition = !isNaN(splitted_url_list[splitted_url_list.length-2]),
        module_name = "",
        isWizardFormSubmit = 0;

    if(isNewWizardForm || isCreateWizardForm || isAddWizardForm) {
        
        var page_title = $(".formContainer .box .box-title h4")[0].innerHTML.toLowerCase().split(" add ");

        try {
            module_name = page_title.join(' ').split("</i>")[1].toUpperCase();
        } catch(e) {
            module_name = page_title.join(' ');
        }

        if(splitted_url_list[splitted_url_list.length-3] == 'sector' || splitted_url_list[splitted_url_list.length-5] == 'sector') {

        }

    } else if(wizard_edit_condition) {

        if(isWizardFormSubmit === 0) {
            
            var oldWizardFields = {};
            // SetTimeout is used to delay the code execution so that the all the fields will be prepared
            setTimeout(function() {
                if(splitted_url_list[splitted_url_list.length-3] == 'sector' || splitted_url_list[splitted_url_list.length-5] == 'sector') {
                    oldWizardFields = prepareWizardFormsData(true);
                } else {
                    oldWizardFields = prepareWizardFormsData(false);
                }
            },500);

        }
    } else {
        // pass
    }
}

/*Form Submit Event*/
$("form").submit(function(e) {
    if(isGisWizard) {
        // Disabel submit button
        if($("form button[type='submit']").length > 0) {
            if(!$("form button[type='submit']").hasClass("disabled")) {
                $("form button[type='submit']").addClass("disabled");
            }
        }

        if(isWizardFormSubmit === 0) {
            if(isNewWizardForm || isCreateWizardForm || isAddWizardForm) {
                
                page_title = $(".formContainer .box .box-title h4")[0].innerHTML.toLowerCase().split(" add ");

                try {
                    module_name = page_title.join(' ').split("</i>")[1].toUpperCase();
                } catch(e) {
                    module_name = page_title.join(' ');
                }

                var alias = $("form input[name*='alias']").val(),
                    shown_val = alias ? alias : $("form input[name*='name']").val();
                
                if(!shown_val) {
                    try {
                        var configured_on_data = $("form input[name*='_configured_on']").select2('data');
                        shown_val = configured_on_data.text ? configured_on_data.text : configured_on_data.device_alias;
                    } catch(e) {
                        shown_val = "";
                    }
                }

                var action = "A new "+module_name.toLowerCase()+" is created - "+shown_val;
                
                /*Call function to save user action*/
                save_user_action(module_name,action,function(result) {
                    var action_response = "";
                    if(typeof result == 'string' && result.indexOf('success') > -1) {
                        action_response = JSON.parse(result);
                    } else {
                        action_response = result;
                    }
                    isWizardFormSubmit = 1;
                    // Enable submit button
                    if($("form button[type='submit']").length > 0) {
                        if($("form button[type='submit']").hasClass("disabled")) {
                            $("form button[type='submit']").removeClass("disabled");
                        }
                    }
                    /*Trigger Form Submit*/
                    $("form").trigger('submit');
                });
            } else if(wizard_edit_condition) {
                
                var form_h4 = ".formContainer .box .box-title h4",
                    page_title = $(form_h4)[0] ? $(form_h4)[0].innerHTML.toLowerCase().split(" edit ") : "",
                    modifiedFieldsStr = "[";
                try {
                    module_name = page_title.join(' ').split("</i>")[1].toUpperCase();
                } catch(e) {
                    module_name = page_title.join(' ');
                }

                if(splitted_url_list[splitted_url_list.length-3] == 'sector' || splitted_url_list[splitted_url_list.length-5] == 'sector') {

                    var newWizardFields = prepareWizardFormsData(true);

                    for(key in oldWizardFields) {
                        if(oldWizardFields.hasOwnProperty(key)) {
                            var current_old_set = oldWizardFields[key],
                                current_new_set = newWizardFields[key];

                            // Reset variable
                            modifiedFieldsStr  = '[';

                            for(var j=0;j<current_old_set.data.length;j++) {
                                var old_field = current_old_set.data[j],
                                    new_field = current_new_set.data[j];

                                if(old_field && old_field.value != undefined && new_field && new_field.value != undefined) {
                                    // GET the sub-module name
                                    if($.trim(sub_module_title_key_dict[key]) == $.trim(new_field.name)) {
                                        sub_module_name = new_field.value;
                                    }

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

                                var updated_module_name = $.trim(module_name)+" : "+current_old_set.title+" - "+sub_module_name;

                                // Save logs
                                save_user_action(updated_module_name,modifiedFieldsStr,function(result) {
                                    if(typeof result == 'string' && result.indexOf('success') > -1) {
                                        action_response = JSON.parse(result);
                                    } else {
                                        action_response = result;
                                    }

                                    isWizardFormSubmit = 1;
                                    // Enable submit button
                                    if($("form button[type='submit']").length > 0) {
                                        if($("form button[type='submit']").hasClass("disabled")) {
                                            $("form button[type='submit']").removeClass("disabled");
                                        }
                                    }
                                    /*Trigger Form Submit*/
                                    $("form").trigger('submit');
                                });
                            }
                        }
                    }
                } else {
                    var newWizardFields = prepareWizardFormsData(false);

                    /*Get Modified Fields*/
                    for(var j=0;j<oldWizardFields.length;j++) {
                        var old_field = oldWizardFields[j],
                            new_field = newWizardFields[j];

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

                            isWizardFormSubmit = 1;
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
 * This function preapred form data array for GIS wizard form
 * @method prepareWizardFormsData
 * @param isSector {Boolean}, It contains a boolean flag used to check either 
   the data requested is from sector page or other
 * @return final_data {Object/Array}, It contains the requested form data
 */
function prepareWizardFormsData(isSector) {

    if(isSector) {
        var final_data = {},
            sector_forms = $(".parent_form_group"),
            isFirst = true;

        for(var i=0;i<sector_forms.length;i++) {
            var label_text = $(sector_forms[i]).prev('.form-group').children(),
                label_id = "",
                input_items = $(sector_forms[i]).children().find(
                    "input:not([type='hidden']):not([type='checkbox'])"
                ).serializeArray(),
                select_boxes = $(sector_forms[i]).children().find("select").toArray(),
                text_area_fields = $(sector_forms[i]).children().find("textarea"),
                checkbox_boxes = $(sector_forms[i]).children().find("input[type='checkbox']"),
                ajax_loader_select = $(sector_forms[i]).children().find(
                    "input.select2-offscreen[type='hidden']"
                ).toArray(),
                data_dict = {};
            // If we have any select2 loaded with ajax data then concat it with other select boxes
            select_boxes = select_boxes.concat(ajax_loader_select);

            // If its top element then use sector label
            if(isFirst && label_text.length == 0) {
                label_text = $(sector_forms[i]).closest('form').prev('.form-group').children();
            }

            // If label exists
            if(label_text && label_text.length > 0) {
                label_id = label_text.attr('id');
                label_text = $.trim(label_text.html());
                if(label_text[label_text.length-1] == ":") {
                    label_text = label_text.slice(0,-1);
                }
            }

            if(label_id) {
                var resultant_data = []

                // Prepare useful format
                var select_boxes_data = prepareSelectBoxesData(select_boxes);
                    text_areas_data = prepareTextareaData(text_area_fields);
                    checkboxes_data = prepareCheckboxesData(checkbox_boxes);

                // Concat all Data
                resultant_data = resultant_data.concat(select_boxes_data);
                resultant_data = resultant_data.concat(text_areas_data);
                resultant_data = resultant_data.concat(checkboxes_data);
                resultant_data = resultant_data.concat(input_items);

                final_data[label_id] = {
                    "title" : label_text,
                    "data" : resultant_data
                }
            }
            // Revert the flag
            isFirst = false;
        }

        return final_data;
    } else {
        var fieldsArray = $("form input:not([type='hidden']):not([type='checkbox'])").serializeArray(),
            select_boxes = $("form select"),
            checkbox_boxes = $("form input[type='checkbox']"),
            text_area_fields = $("form textarea"),
            select_boxes_data = [], 
            text_areas_data = [],
            checkboxes_data = [],
            final_data = [];

        select_boxes_data = prepareSelectBoxesData(select_boxes);
        text_areas_data = prepareTextareaData(text_area_fields);
        checkboxes_data = prepareCheckboxesData(checkbox_boxes);
        // Reset Variable
        final_data = []
        // Concat all Data
        final_data = final_data.concat(select_boxes_data);
        final_data = final_data.concat(text_areas_data);
        final_data = final_data.concat(checkboxes_data);
        final_data = final_data.concat(fieldsArray);

        return final_data;
    }
}