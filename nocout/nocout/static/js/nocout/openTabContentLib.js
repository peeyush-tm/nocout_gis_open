/**
 * This library handles the tab click event & load the data as per the selected tab.
 * @class openTabContentLib
 * @event click
 */

var last_clicked_tab = "",
	timeOutId = "";

$(".nav-tabs li a").click(function (e,isFirst) {

	/*Initialize the timer in seconds.Right now its 300 sec i.e. 5 minutes*/
	var timer = 300;

	/*Clear or Reset Time out*/
	clearTimeout(timeOutId);

	var anchor_id = e.currentTarget.id,
		browser_url_array = window.location.href.split("#"),
		second_condition = "";
	
	if(isFirst) {
		second_condition = 	isFirst;
	} else {
		second_condition = 	false;
	}	

	/*Current Tab content id or anchor tab hyperlink*/
	new_url = e.currentTarget.href;


	if(!isFirst) {
		window.location.href = new_url;
	}

	var destroy = false,
		div_id = e.currentTarget.href.split("#")[1],
		table_id = $("#"+div_id).find("table")[0].id,
		ajax_url = e.currentTarget.attributes.data_url.value,
		grid_headers = JSON.parse(e.currentTarget.attributes.data_header.value),
		isTableExists = $.fn.dataTableSettings;

	/*Check that the table is created before or not*/
	for ( var i=0, iLen=isTableExists.length ; i<iLen ; i++ ) {

		if ( isTableExists[i].nTable.id == table_id ){

			if(last_clicked_tab != e.currentTarget.id || second_condition) {

				/*Clear the data from existing table*/
				$("#"+table_id).html("");
				destroy = true;
			}
		}
	}
	
	if(last_clicked_tab != e.currentTarget.id || second_condition) {

		if(table_id.toLowerCase().indexOf("p2p") > -1 || table_id.toLowerCase().indexOf("ptp") > -1) {
			
			for(var i=0;i<grid_headers.length;i++) {
				var column = grid_headers[i];
				if(column.mData.indexOf("sector_id") > -1) {
					if(column.bVisible) {
						column.bVisible = false;
					} else {
						column["bVisible"] = false;
					}
				}
			}
		}

		/*Call createDataTable function to create the data table for specified dom element with given data*/
		dataTableInstance.createDataTable(table_id, grid_headers, ajax_url, destroy);
	}

	/*Save the last clicked tab id in global variable for condition checks*/
	last_clicked_tab = e.currentTarget.id;

	/*Refresh the tab after every given timer. Right now it is 5 minutes*/
	timeOutId = setTimeout(function() {

		$("#"+anchor_id).trigger('click',true);

	},(+(timer)+"000"));
});