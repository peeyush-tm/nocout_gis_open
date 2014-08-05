/**
 * @class openTabContentLib
 * This library handles the tab click event & load the data as per the tab.
 */

$(".nav-tabs li a").click(function (e,isFirst) {

	var destroy = false,
		div_id = e.currentTarget.href.split("#")[1],
		table_id = $("#"+div_id).find("table")[0].id,
		ajax_url = e.currentTarget.attributes.data_url.value,
		grid_headers = JSON.parse(e.currentTarget.attributes.data_header.value),
		isTableExists = $.fn.dataTableSettings,
		isActive = $("#"+e.currentTarget.id).parent().hasClass("active");

	/*Check that the table is created before or not*/
	for ( var i=0, iLen=isTableExists.length ; i<iLen ; i++ ) {

		if ( isTableExists[i].nTable.id == table_id ){

			if(!(isActive) || isFirst) {

				/*Clear the data from existing table*/
				$("#"+table_id).html("");
				destroy = true;
			}
		}
	}

	if(!(isActive) || isFirst) {

		/*Call createDataTable function to create the data table for specified dom element with given data*/
		dataTableInstance.createDataTable(table_id, grid_headers, ajax_url, destroy);

	}

});