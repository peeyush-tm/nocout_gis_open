/**
 * This file handle complete functionality related to global search
 * @for globalSearchLib
 * @uses select2
 */

// Global Variables
var base_url = "";

/*Set the base url of application for ajax calls*/
if(window.location.origin) {
    base_url = window.location.origin;
} else {
    base_url = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
}

/**
 * This function initializes global search inputs & bind data fetch calls
 * @method initGlobalSearch
 */
function initGlobalSearch() {

	if($("#searchBy").length > 0) {
		// Init Search By Select box with select2	
		var search_criteria_select2 = $("#searchBy").select2({
			width: 'resolve'
		});

		// Trigger when search criteria changed
		search_criteria_select2.on("change", function(e) {
			// Remove selection
			$("#global_search_txt").select2("val","");

			// Clear Previous links
			$("#redirect_link_container").html("");

			// Reset Global Search Cookies
			$.cookie("global_search_criteria", "", {path: '/', secure : true});
        	$.cookie("global_search_val", "", {path: '/', secure : true});
		});
	}

	if($("#global_search_txt").length > 0) {
		// Init Search text box with select2
		$("#global_search_txt").select2({
			multiple: false,
			minimumInputLength: 3,
			placeholder: "Search...",
			width: 'resolve',
			query: function (query) {

				var search_by_txt = $("#searchBy").select2("val");

				if(search_by_txt) {

					var data = {
						"results" : []
					};
					
					var suggestion_api_url = "/global_search/get_auto_suggestions/"+search_by_txt+"/"+String(query.term)+"/";

					makeSearchCall_nocout(suggestion_api_url,search_by_txt,query.term,function(suggestions_data) {
						data.results = suggestions_data;
						query.callback(data);
					});
				} else {
					bootbox.alert("Please select search criteria first");
				}
			}
		}).on("select2-selecting", function(el) {
			// If any item searched before then disabled the redirection links
			if($(".global_search_container #redirect_link_container").html().length) {
				$(".global_search_container #redirect_link_container").html("");
			}
		});
	}

	if($("#searchBy").length > 0 && $("#global_search_txt").length > 0) {
		loadPreviousContent_search()
	}
}

/**
 * This function loads previously searched content from cookies
 * @method loadPreviousContent_search
 */
function loadPreviousContent_search() {

	var prev_search_by = $.cookie("global_search_criteria"),
		prev_search_text = $.cookie("global_search_val");

	if(prev_search_by && prev_search_text) {
		$("#searchBy").select2("val",prev_search_by);
		$("#global_search_txt").select2("data",JSON.parse(prev_search_text));


		$("#global_search_btn").trigger("click");
	}
}

/**
 * This function make ajax call to fetch auto suggestions data as per the types text & selected search criteria.
 * @method makeSearchCall_nocout.
 * @param searchBy {String}, It contains the search criteria text.
 * @param searchTxt {String}, It contains the text entered in searcg textbox.
 */
function makeSearchCall_nocout(api_url,searchBy,searchTxt,callback) {

	if(searchBy && searchTxt) {
		$.ajax({
			url : base_url+api_url,
			type : "GET",
			success : function(response) {
				var result = "";
				if(typeof response == 'string') {
					result = JSON.parse(response);
				} else {
					result = response;
				}

				if(result.success == 1) {
					callback(result.data);
				} else {
					callback([]);
				}
			},
			error : function(err) {
				// console.log(err.statusText);
				callback([]);
			}
		});
	} else {
		bootbox.alert("Please select search criteria first.");
	}
}

/**
 * This event triggers when global search button is clicked.
 * @event click.
 */
$("#global_search_btn").click(function(e) {
	
	var search_by = $("#searchBy").select2("val"),
		search_id = $("#global_search_txt").select2("val");
	// console.log(search_id)

	if(search_by && search_id) {
		
		var search_txt_data = $("#global_search_txt").select2("data") ? JSON.stringify($("#global_search_txt").select2("data")) : "";

		// Update Cookies with new values
		$.cookie("global_search_criteria", search_by, {path: '/'});
		$.cookie("global_search_val", search_txt_data, {path: '/'});

		// Search API url
		var search_api_url = "/global_search/get_search_data/"+search_by+"/"+String(search_id) + "/";
		
		// Call function to make ajax call to get the search result. 
		makeSearchCall_nocout(search_api_url,search_by,search_id,function(search_data) {
			// Clear Previous links
			$(".global_search_container #redirect_link_container").html("");
			
			var link_html = "",
				svp_link_html = "";

			if (search_by == 'circuit_id') {
				var ckt_id = "";
				try {
					ckt_id = $("#global_search_txt").select2("data").text;
				} catch(e) {
					ckt_id = "";
				}

				if (ckt_id) {
					var link = "http://172.31.6.73/ipservices/wirelessintegrate/integratesv.php?viznet_id";
					svp_link_html = '<a href="'+link+'='+ckt_id+'" class="btn btn-default btn-sm" title="SVP" target="_blank">SVP</a>';
				}
			}

			if(search_data["inventory_page_url"]) {
				var inventory_url = base_url+""+search_data["inventory_page_url"];
				link_html += '<a href="'+inventory_url+'" class="btn btn-default btn-sm" title="Device Inventory" target="_blank"><i class="fa fa-dropbox text-primary"></i></a>';
			}

			if(search_data["circuit_inventory_url"]) {
				var inventory_url = base_url+""+search_data["circuit_inventory_url"];
				link_html += '<a href="'+inventory_url+'" class="btn btn-default btn-sm" title="Circuit Inventory" target="_blank"><i class="fa fa-arrow-circle-o-right text-primary"></i></a>';
			}

			if(search_data["sector_inventory_url"]) {
				var inventory_url = base_url+""+search_data["sector_inventory_url"];
				link_html += '<a href="'+inventory_url+'" class="btn btn-default btn-sm" title="Sector Inventory" target="_blank"><i class="fa fa-arrow-circle-o-right text-primary"></i></a>';
			}

			if(search_data["perf_page_url"]) {
				var perf_url = base_url+""+search_data["perf_page_url"];
				link_html += '<a href="'+perf_url+'" class="btn btn-default btn-sm" title="Performance" target="_blank"><i class="fa fa-bar-chart-o text-primary"></i></a>';
			}

			if(search_data["alert_page_url"]) {
				var alert_url = base_url+""+search_data["alert_page_url"];
				link_html += '<a href="'+alert_url+'" class="btn btn-default btn-sm" title="Alerts" target="_blank"><i class="fa fa-warning text-primary"></i></a>';
			}

			if (svp_link_html) {
				link_html += svp_link_html;
			}

			if(link_html) {
				link_html += "<button class='btn btn-default btn-sm' title='Reset' id='reset_global_search'><i class='fa fa-refresh'></i></button>"
			}

			if (search_by == 'ip_address') {
				$.cookie("activeTabId", "", {path: '/', secure : true});
			}

			$(".global_search_container #redirect_link_container").html(link_html);
		});
	} else {
		bootbox.alert("Please select search criteria & search value first");
	}
});


/**
 * This event triggers when reset global search button(shown after any search) is clicked
 * @event delegate(with click)
 */
$("body").delegate("#reset_global_search","click",function(e) {
	// Reset search criteria
	$("#searchBy").select2("val","");

	// Reset search seleted item
	$("#global_search_txt").select2("val","");

	// Clear Previous links
	$("#redirect_link_container").html("");

	// Reset Global Search Cookies
	$.cookie("global_search_criteria", "", {path: '/', secure : true});
	$.cookie("global_search_val", "", {path: '/', secure : true});
});