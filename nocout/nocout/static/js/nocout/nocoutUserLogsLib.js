/**
 * This file call API to save user logs on create & edit operation on any item
 * @for nocoutUserLogsLib
 */

// If formContainer class present then proceed
if($(".formContainer").length) {

    var isNewForm = window.location.href.indexOf('new'),
        isCreateForm = window.location.href.indexOf('create'),
        isAddForm = window.location.href.indexOf('add'),
        isEditForm = window.location.href.indexOf('edit'),
        isUpdateForm = window.location.href.indexOf('update'),
        isModifyForm = window.location.href.indexOf('modify'),
        splitted_url_list = window.location.pathname.split("/"),
        wizard_condition_1 = window.location.href.indexOf('wizard/device-type') > -1,
        wizard_condition_2 = !isNaN(splitted_url_list[splitted_url_list.length-1]),
        wizard_condition_3 = splitted_url_list.indexOf('gis-wizard') > -1,
        isWizardForm =  (wizard_condition_1) || (wizard_condition_2 && wizard_condition_3),
        page_title = "",
        module_name = "",
        isFormSubmit = 0;

    if(isCreateForm > -1 || isNewForm > -1 || isAddForm > -1) {
        
        page_title = $(".formContainer .box .box-title h4")[0].innerHTML.toLowerCase().split(" add ");

        try {
            module_name = page_title.join(' ').split("</i>")[1].toUpperCase();
        } catch(e) {
            module_name = page_title.join(' ');
        }

    } else if(isEditForm > -1 || isUpdateForm > -1 || isModifyForm > -1 || isWizardForm) {

        page_title = $(".formContainer .box .box-title h4")[0] ? $(".formContainer .box .box-title h4")[0].innerHTML.toLowerCase().split(" edit ") : "";
        try {
            module_name = page_title.join(' ').split("</i>")[1].toUpperCase();
        } catch(e) {
            module_name = page_title.join(' ');
        }

        if(isFormSubmit === 0) {
            var oldFieldsArray = $("form input:not([type='hidden']):not([type='checkbox'])").serializeArray(),
                select_boxes = $("form select"),
                checkbox_boxes = $("form input[type='checkbox']"),
                text_area_fields = $("form textarea");

            setTimeout(function() {
                // Loop select boxes
                for(var i=0;i<select_boxes.length;i++) {
                    var select_id = select_boxes[i].attributes["id"].value,
                        isSelect2 = $("#"+select_id)[0].className.indexOf('select2') > -1,
                        values_array = isSelect2 ? $("#"+select_id).select2("data") : $("#"+select_id+" option:selected").text(),
                        selected_values = "";

                    if(values_array && values_array.constructor == Array) {
                        $.grep(values_array,function(data){
                            if(selected_values.length > 0) {
                                selected_values +=  data.text ? ","+data.text() : "";
                            } else {
                                selected_values += data.text ? data.text() : "";
                            }
                        });
                    } else {
                        if(typeof values_array == 'object') {
                            selected_values = values_array ? values_array.text : "";
                        } else {
                            selected_values = values_array;
                        }
                    }

                    var data_obj = {
                        "name" : select_boxes[i].attributes["name"].value,
                        "value" : selected_values
                    };
                    oldFieldsArray.push(data_obj);
                }
                // Loop Textareas
                for(var i=0;i<text_area_fields.length;i++) {
                    var textarea_name = text_area_fields[i].attributes["name"].value,
                        textarea_id = text_area_fields[i].attributes["id"].value;
                    if(textarea_name && textarea_id) {
                        var data_obj = {
                            "name" : textarea_name,
                            "value" : $("#"+textarea_id).val()
                        };

                        oldFieldsArray.push(data_obj);
                    }
                }
                // Loop checkboxes
                for(var i=0;i<checkbox_boxes.length;i++) {
                    var checkbox_name = checkbox_boxes[i].attributes["name"].value,
                        checkbox_id = checkbox_boxes[i].attributes["id"].value,
                        isChecked = $("#"+checkbox_id)[0].checked,
                        checkbox_val = isChecked ? $("#"+checkbox_id).val() : "off";

                    if(checkbox_name && checkbox_id) {
                        var data_obj = {
                            "name" : checkbox_name,
                            "value" : checkbox_val
                        };

                        oldFieldsArray.push(data_obj);
                    }
                }
            },600);
        } 
    }
}

/*Form Submit Event*/
$("form").submit(function(e) {

    // Disabel submit button
    if($("form button[type='submit']").length > 0) {
        if(!$("form button[type='submit']").hasClass("disabled")) {
            $("form button[type='submit']").addClass("disabled");
        }
    }
    /*Create case*/
    if(isCreateForm > -1 || isNewForm > -1 || isAddForm > -1) {
        /*When first time form submitted*/
        if(isFormSubmit === 0) {

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
    } else if(isEditForm > -1 || isUpdateForm > -1 || isModifyForm > -1 || isWizardForm) {
        /*When first time form submitted*/
        if(isFormSubmit === 0) {

            var newFieldsArray = $("form input:not([type='hidden']):not([type='checkbox'])").serializeArray(),
                select_boxes = $("form select"),
                checkbox_boxes = $("form input[type='checkbox']"),
                text_area_fields = $("form textarea"),
                modifiedFieldsStr = "[";
            
            // Loop new selectboxes
            for(var i=0;i<select_boxes.length;i++) {
                var select_id = select_boxes[i].attributes["id"] ? select_boxes[i].attributes["id"].value : "",
                    isSelect2 = $("#"+select_id)[0].className.indexOf('select2') > -1,
                    values_array = isSelect2 ? $("#"+select_id).select2("data") : $("#"+select_id+" option:selected").text(),
                    selected_values = "";

                if(values_array && values_array.constructor == Array) {
                    $.grep(values_array,function(data){
                        if(selected_values.length > 0) {
                            selected_values +=  data.text ? ","+data.text() : "";
                        } else {
                            selected_values += data.text ? data.text() : "";
                        }
                    });
                } else {
                    if(typeof values_array == 'object') {
                        selected_values = values_array ? values_array.text : "";
                    } else {
                        selected_values = values_array;
                    }
                }

                var data_obj = {
                    "name" : select_boxes[i].attributes["name"].value,
                    "value" : selected_values
                };

                newFieldsArray.push(data_obj);
            }
            // Loop new textarea
            for(var i=0;i<text_area_fields.length;i++) {
                var textarea_name = text_area_fields[i].attributes["name"].value,
                    textarea_id = text_area_fields[i].attributes["id"].value;
                if(textarea_name && textarea_id) {
                    var data_obj = {
                        "name" : textarea_name,
                        "value" : $("#"+textarea_id).val()
                    };

                    newFieldsArray.push(data_obj);
                }
            }
            
            // Loop new checkboxes
            for(var i=0;i<checkbox_boxes.length;i++) {
                var checkbox_name = checkbox_boxes[i].attributes["name"].value,
                    checkbox_id = checkbox_boxes[i].attributes["id"].value,
                    isChecked = $("#"+checkbox_id)[0].checked,
                    checkbox_val = isChecked ? $("#"+checkbox_id).val() : "off";

                if(checkbox_name && checkbox_id) {
                    var data_obj = {
                        "name" : checkbox_name,
                        "value" : checkbox_val
                    };

                    newFieldsArray.push(data_obj);
                }
            }


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
});

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