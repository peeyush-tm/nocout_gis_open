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
        /*Spinner configuration object*/
        var spinner_options = {
            lines: 15, // The number of lines to draw
            length: 16, // The length of each line
            width: 2, // The line thickness
            radius: 10, // The radius of the inner circle
            corners: 1, // Corner roundness (0..1)
            rotate: 0, // The rotation offset
            direction: 1, // 1: clockwise, -1: counterclockwise
            color: '#000', // #rgb or #rrggbb or array of colors
            speed: 0.8, // Rounds per second
            trail: 100, // Afterglow percentage
            shadow: false, // Whether to render a shadow
            hwaccel: false, // Whether to use hardware acceleration
            className: 'spinner', // The CSS class to assign to the spinner
            zIndex: 2e9, // The z-index (defaults to 2000000000)
            top: '50%', // Top position relative to parent
            left: '50%' // Left position relative to parent
        };
        /*Spinner DOM Element*/
        var dom_target = document.getElementById('ajax_spinner');
        
        if($("#ajax_spinner").hasClass("hide")) {
            /*Show ajax_spinner div*/
            $("#ajax_spinner").removeClass("hide")
            /*Initialize spinner object*/
            var spinner = new Spinner(spinner_options).spin(dom_target);
            /*If ajax_backdrop div not exist then appent it to body */
            if($("#ajax_backdrop").length == 0) {
                $("body").append('<div class="modal-backdrop fade in" id="ajax_backdrop"></div>');
            }            
        }
        /*Spinner Block End*/

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
            bPaginate: true,
            bProcessing : true,
            bServerSide: true,
            sAjaxSource: ajax_url,
            /*This is the callback funtion for data ajax call*/
            fnInitComplete: function(oSettings) {
                /*Remove backdrop div & hide spinner*/
                $("#ajax_backdrop").remove();
                if(!($("#ajax_spinner").hasClass("hide"))) {
                    /*Hide ajax_spinner div*/
                    $("#ajax_spinner").addClass("hide");
                }
            },
            aoColumns:tableheaders
 		});
    };
}
