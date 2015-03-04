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
       
        // ******************************* TEMPORARY CODE START *******************************//
        // By Default remove sorting from all datatables
        for(var i=0;i<tableheaders.length;i++) {
            var header = tableheaders[i];
            header['bSortable'] = false;
        }
        // ******************************* TEMPORARY CODE END *******************************//

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
                var search_btn_html = '';

                search_btn_html += '<button id="'+tableId+'_search_btn" class="btn btn-sm btn-default pull-right">';
                search_btn_html += '<i class="fa fa-search"></i></button>';

                // Add search button near search txt box
                $('#'+tableId+'_wrapper div.dataTables_filter label').append(search_btn_html);
                
                // Update search txt box & row per pages dropdown style
                $('#'+tableId+'_wrapper div.dataTables_length label select, #'+tableId+'_wrapper div.dataTables_filter label input').addClass("form-control");
                $('#'+tableId+'_wrapper div.dataTables_length label select, #'+tableId+'_wrapper div.dataTables_filter label input').addClass("input-sm");
                $('#'+tableId+'_wrapper div.dataTables_length label select, #'+tableId+'_wrapper div.dataTables_filter label input').css("max-width","150px");
            },
            aoColumns:tableheaders,
            sPaginationType: "full_numbers",
            aaSorting:[],
            bStateSave:false
 		});

        

        var dtable = $("#"+tableId).DataTable();

        // Grab the datatables input box and alter how it is bound to events
        $("#"+tableId+"_wrapper .dataTables_filter input")
            .unbind() // Unbind previous default bindings
            .bind("input", function(e) { // Bind our desired behavior
                // If the length is 3 or more characters, or the user pressed ENTER, search
                if(this.value.length >= 2 && e.keyCode == 13) {
                    // Call the API search function
                    //----------- If you want to start search on key up then uncomment the next line -----------//
                    // dtable.fnFilter(this.value);
                }
                // Ensure we clear the search if they backspace far enough
                if(this.value == "") {
                    dtable.fnFilter("");
                }
                return;
            });

        $("#page_content_div").delegate("#"+tableId+"_search_btn",'click',function() {
            var search_text = $(".dataTables_filter input").val();
            if(search_text.length >= 2) {
                dtable.fnFilter(search_text);
            }
        });

    };
}