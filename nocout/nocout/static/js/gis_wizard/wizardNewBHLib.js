/**
 * This events triggers when page loads. It initializes all elements
 * @for wizardNewBHLib.js
 * @event ready
 */
$(document).ready(function() {
    // Changing labels of form fields
    $("label[for=id_bh_configured_on]").html('<span class="mandatory">* </span>BH Configured On');
    $("label[for=id_bh_port_name]").text('BH Port Name');
    $("label[for=id_bh_port]").text('BH Port');
    $("label[for=id_bh_type]").text('BH Type');
    $("label[for=id_bh_switch]").text('BS Converter');
    $("label[for=id_switch_port_name]").text('BS Converter Port Name');
    $("label[for=id_switch_port]").text('BS Converter Port Number');
    $("label[for=id_pop]").text('POP Converter');
    $("label[for=id_pop_port_name]").text('POP Converter Port Name');
    $("label[for=id_pop_port]").text('POP Converter Port Number');
    $("label[for=id_aggregator]").text('Aggregation Switch');
    $("label[for=id_aggregator_port_name]").text('Aggregation Switch Port Name');
    $("label[for=id_aggregator_port]").text('Aggregation Switch Port Number');
    $("label[for=id_pe_hostname]").text('PE Hostname');
    $("label[for=id_pe_ip]").text('PE IP Address');
    $("label[for=id_bh_connectivity]").text('BH Connectivity');
    $("label[for=id_bh_circuit_id]").text('BH Circuit ID');
    $("label[for=id_bh_capacity]").text('BH Capacity');
    $("label[for=id_ttsl_circuit_id]").text('TTSL Circuit ID');
    $("label[for=id_dr_site]").text('DR Site');

    // Initialize the select2 selectbox.
    $(".select2select").select2();
    
    // Initialize tooltip
    $('.tip-focus').tooltip({
        placement: 'right',
        trigger: 'focus'
    });

    // Initialize BH Configured on select2
    $("#id_bh_configured_on").select2({
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
            var id = $(element).val() ? $.trim($(element).val()) : "";
            if(id) {
                $.ajax("/device/select2/elements/", {
                    dataType: "json",
                    data: {'obj_id': id}
                }).done(function(data) {
                    callback({id: id, device_alias: data[0]});
                });
            }
        },
        formatResult: function(device) {
            return device.device_alias;
        },
        formatSelection: function(device) {
            return device.device_alias;
        }
    });
    
    // Initialize BH Switch select2
    $("#id_bh_switch").select2({
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
            var id = $(element).val() ? $.trim($(element).val()) : "";
            if(id) {
                $.ajax("/device/select2/elements/", {
                    dataType: "json",
                    data: {'obj_id': id}
                }).done(function(data) {
                    callback({id: id, device_alias: data[0]});
                });
            }
        },
        formatResult: function(device) {
            return device.device_alias;
        },
        formatSelection: function(device) {
            return device.device_alias;
        }
    });

    // Initialize pop select2
    $("#id_pop").select2({
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
            var id = $(element).val() ? $.trim($(element).val()) : "";
            if(id) {
                $.ajax("/device/select2/elements/", {
                    dataType: "json",
                    data: {'obj_id': id}
                }).done(function(data) {
                    callback({id: id, device_alias: data[0]});
                });
            }
        },
        formatResult: function(device) {
            return device.device_alias;
        },
        formatSelection: function(device) {
            return device.device_alias;
        }
    });

    // Initialize aggregator select2
    $("#id_aggregator").select2({
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
            var id = $(element).val() ? $.trim($(element).val()) : "";
            if (id) {
                $.ajax("/device/select2/elements/", {
                    dataType: "json",
                    data: {'obj_id': id}
                }).done(function(data) {
                    callback({id: id, device_alias: data[0]});
                });
            }
        },
        formatResult: function(device) {
            return device.device_alias;
        },
        formatSelection: function(device) {
            return device.device_alias;
        }
    });
    
    $("#id_pe_ip").select2({
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
                    tech_name: 'pe'
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
            return device.device_alias;
        },
        formatSelection: function(device) {
            return device.device_alias;
        }
    });
});

/**
 * This event triggers when update & show button clicked
 * @event click
 */
$("#id_update_and_show").on("click", function(e) {
    e.preventDefault();
    $('#id_backhaul_form').attr('action', "?show=True").submit();
});

/**
 * This function triggers when delete button clicked.
   After confirmation from user if request to delete BS-BH relationship link
 * @method delete_and_show
 */
function delete_and_show() {
    if(confirm('Remove relationship of Backhaul and Base Station?')) {
        window.location.replace(delete_bh_url);
    }
}
