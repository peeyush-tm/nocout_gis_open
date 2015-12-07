/**
 * This events triggers when page loads. It initializes all elements
 * @for wizardNewBsLib.js
 * @event ready
 */
// Global Variables
var parent_class = 'formContainer',
    change_event_dom_ids = [
        '#id_country',
        '#id_state'
    ],
    element_relation_dict = {
        '#id_country' : {
            "old_value" : $('#id_country').val(),
            "update" : [
                {
                    "id" : '#id_state',
                    "url_name" : fetch_state_url,
                    "existing_value" : $('#id_state').val()
                }
            ],
            "reset" : ['#id_state', '#id_city']
        },
        '#id_state' : {
            "old_value" : $('#id_state').val(),
            "update" : [
                {
                    "id" : '#id_city',
                    "url_name" : fetch_city_url,
                    "existing_value" : $('#id_city').val()
                }
            ],
            "reset" : ['#id_city']
        }
    },
    current_tech = "";

$(document).ready(function () {
    $("#id_update_and_show").on("click", function(e) {
        e.preventDefault();
        $('#id_base_station_form').attr('action', "?show=True").submit();
    });

    // Changing labels of form fields
    $("label[for=id_bs_technology]").html('<span class="mandatory">* </span>BS Technology');
    $("label[for=id_bs_site_id]").text('BS Site ID');
    $("label[for=id_bs_site_type]").text('BS Site Type');
    $("label[for=id_bs_switch]").text('BS Switch');
    $("label[for=id_bs_type]").text('BS Type');
    $("label[for=id_bh_bso]").text('BH BSO');
    $("label[for=id_hssu_used]").text('HSSU Used');
    $("label[for=id_gps_type]").text('GPS Type');

    // Initialize the select2 selectbox.
    $(".select2select").select2();

    // Loop to trigger change event on select boxes
    for (var i=0;i<change_event_dom_ids.length;i++) {
        if (element_relation_dict[change_event_dom_ids[i]]['old_value']) {
            // trigger change event
            $(change_event_dom_ids[i]).trigger('change', true);
        }
    }

    // Initialize tooltip
    $('.tip-focus').tooltip({
        placement: 'right',
        trigger: 'focus'
    });

    // Initialize BS Switch select2
    $("#id_bs_switch").select2({
        placeholder: "Search for a device.",
        minimumInputLength: 2,
        width: "resolve",
        ajax: { // instead of writing the function to execute the request we use Select2's convenient helper
            url: "/device/select2/elements/",
            dataType: 'json',
            quietMillis: 250,
            data: function (term, page) {
                var org_id = $("#id_organization").val();
                return {
                    sSearch: term, // search term
                    org: org_id,
                };
            },
            results: function (data, page) { // parse the results into the format expected by Select2.
                // since we are using custom formatting functions we do not need to alter the remote JSON data
                return { results: data.items };
            },
            cache: false
        },
        initSelection: function(element, callback) {
            // the input tag has a value attribute preloaded that points to a preselected repository's id
            // this function resolves that id attribute to an object that select2 can render
            // using its formatResult renderer - that way the repository name is shown preselected
            var id = $(element).val();
            if (id !== "") {
                $.ajax("/device/select2/elements/", {
                    dataType: "json",
                    data: {'obj_id': id}
                }).done(function(data) {
                    callback({id: id, device_alias: data[0]});
                });
            }
        },
        formatResult: function(device) {
            return device.device_alias
        },
        formatSelection: function(device) {
            return device.device_alias
        }
    });

    // Initialize Backhaul select2
    $("#id_backhaul").select2({
        placeholder: "Search for a backhaul.",
        minimumInputLength: 2,
        width: "resolve",
        ajax: { // instead of writing the function to execute the request we use Select2's convenient helper
            url: "/backhaul/select2/elements/",
            dataType: 'json',
            quietMillis: 250,
            data: function (term, page) {
                var org_id = $("#id_organization").val();
                return {
                    sSearch: term, // search term
                    org: org_id,
                };
            },
            results: function (data, page) { // parse the results into the format expected by Select2.
                // since we are using custom formatting functions we do not need to alter the remote JSON data
                return { results: data.items };
            },
            cache: false
        },
        initSelection: function(element, callback) {
            // the input tag has a value attribute preloaded that points to a preselected repository's id
            // this function resolves that id attribute to an object that select2 can render
            // using its formatResult renderer - that way the repository name is shown preselected
            var id = $(element).val() ? $.trim($(element).val()) : "";
            if (id) {
                $.ajax("/backhaul/select2/elements/", {
                    dataType: "json",
                    data: {'obj_id': id}
                }).done(function(data) {
                    callback({id: id, alias: data[0]});
                });
            }
        },
        formatResult: function(backhaul) {
            return backhaul.alias;
        },
        formatSelection: function(backhaul) {
            return backhaul.alias;
        }
    });
});//end ready