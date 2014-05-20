
function ourDataTableWidget()
{
	/**
	 * This function creates the jquery data table
	 * @class ourDataTableWidget
	 * @method createDataTable
	 * @param dataObject {JSON Object} It contains the data table configuration & data json object
	 */
	this.createDataTable = function(tableId, tableheaders, ajax_url)
	{
	    $("#"+tableId).DataTable(
            {
            bPaginate: true,
            bProcessing : true,
            bServerSide: true,
            sAjaxSource: ajax_url,
            aoColumns:tableheaders
 }
    )}
}
