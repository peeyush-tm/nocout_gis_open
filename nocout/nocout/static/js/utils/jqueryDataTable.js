
function ourDataTableWidget()
{
	/**
	 * This function creates the jquery data table
	 * @class ourDataTableWidget
	 * @method createDataTable
	 * @param dataObject {JSON Object} It contains the data table configuration & data json object
	 */
	this.createDataTable = function(tableId,dataObject)
	{
	    $("#"+tableId).DataTable(
		{
			aaData: dataObject.tableData,
		    aoColumns: dataObject.tableColumn,
		    sPaginationType : dataObject.sPaginationType

		});
	}
}
