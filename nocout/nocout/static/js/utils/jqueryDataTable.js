/**
*/
function ourDataTableWidget()
{
	/**
	 * This function creates the jquery data table on given domElement
	 * @class ourDataTableWidget
	 * @method createDataTable
	 * @param tableId "String" It contains the dom selector of table
	 * @param tableheaders {JSON Object} It contains the grid headers object
	 * @param ajax_url "String" It contains the ajax url from which the data is to be loaded
	 */
	this.createDataTable = function(tableId, tableheaders, ajax_url, destroy)
	{
        /*Show the spinner*/
        showSpinner();

        destroy = typeof destroy !== 'undefined' ? destroy : true;
		
        $('.datatable').each(function () {
            var datatable = $(this);
            // SEARCH - Add the placeholder for Search and Turn this into in-line form control
            var search_input = datatable.closest('.dataTables_wrapper').find('div[id$=_filter] input');
            search_input.attr('placeholder', 'Search');
            search_input.addClass('form-control input-sm');
            // LENGTH - Inline-Form control
            var length_sel = datatable.closest('.dataTables_wrapper').find('div[id$=_length] select');
            length_sel.addClass('form-control input-sm');
        });
        
        if (destroy){
            $("#"+tableId).dataTable().fnDestroy();
        }
	    
        $("#"+tableId).DataTable({
            bAutoWidth: false,
            bDestroy : true,
            bPaginate: true,
            bProcessing : true,
            bServerSide: true,
            sAjaxSource: ajax_url,
            /*This is the callback funtion for data ajax call*/
            fnInitComplete: function(oSettings) {
                /*Hide the spinner*/
                hideSpinner();
            },
            aoColumns:tableheaders,
            sPaginationType: "full_numbers",
            aaSorting:[],
            bStateSave:false
 		});
    };
}