/**
 * This events triggers when page loads. It initializes all elements
 * @for wizardNewBsLib.js
 * @event ready
 */
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
    // Initialize tooltip
    $('.tip-focus').tooltip({
        placement: 'right',
        trigger: 'focus'
    });

    // if none of the value from 'country' is selected than empty 'state' & 'city' selection too.
    // or update value of 'state' corresponding to the selected 'country'
    if ($("#id_country").val() == "") {
        $("#id_state").empty();
        $("#id_city").empty();
    } else {
        Dajaxice.inventory.update_states_after_invalid_form(Dajax.process, {
            'option': $("#id_country").val(),
            'state_id': $("#id_state").val()
        });
    }

    // if 'state' has no value than empty 'city' selection menu
    // or update 'city' corresponding to selected 'state'
    if (!$("#id_state").val()) {
        $("#id_city").empty();
    } else {
        Dajaxice.inventory.update_cities_after_invalid_form(Dajax.process, {
            'option': $("#id_state").val(),
            'city_id': $("#id_city").val()
        });
    }

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

/**
 * This event triggers when country dropdown value changes. If updates the state dropdown accordingly
 * @event change
 */
$("#id_country").change(function () {
    if ($("#id_country").val() != "") {
        Dajaxice.inventory.update_states(Dajax.process, {
            'option': $("#id_country").val()
        });
        $("#id_city").empty();
    }
    else {
        $("#id_state").select2("val","");
        $("#id_state").empty();
        $("#id_city").select2("val","");
        $("#id_city").empty();
    }
});

/**
 * This event triggers when state dropdown value changes. If updates the city dropdown accordingly
 * @event change
 */
$("#id_state").change(function () {
    $("#id_city").select2("val","");
    Dajaxice.inventory.update_cities(Dajax.process, {
        'option': $("#id_state").val()
    });
});