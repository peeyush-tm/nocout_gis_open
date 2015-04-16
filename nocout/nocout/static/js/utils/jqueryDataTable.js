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
	this.createDataTable = function(
        tableId,
        tableheaders,
        ajax_url,
        destroy,
        table_title,
        app_name,
        header_class_name,
        data_class_name,
        header_extra_param,
        data_extra_param
    ) {
        /*Show the spinner*/
        showSpinner();

        destroy = typeof destroy !== 'undefined' ? destroy : true;

        var page_length_val = [[10, 25, 50, 100], [10, 25, 50, 100]];

        if(ajax_url == '/download_center/citycharter/listing/yes/') {
            page_length_val = [[5, 10, 25, 50, 100], [5, 10, 25, 50, 100]];            
        }

        var default_selected_page_length = page_length_val[0][0] ? page_length_val[0][0] : 10;

        if (destroy){
            $("#"+tableId).dataTable().fnDestroy();
        }

        $("#"+tableId).DataTable({
            bAutoWidth: false,
            bDestroy : true,
            bPaginate: true,
            bProcessing : true,
            bServerSide: true,
            aLengthMenu: page_length_val,
            iDisplayLength : default_selected_page_length,
            sAjaxSource: ajax_url,
            /*This is the callback funtion for data ajax call*/
            fnInitComplete: function(oSettings) {
                /*Hide the spinner*/
                hideSpinner();
                var search_btn_html = '';
                // If download is enabled from settings then show download button else not
                if(datatables_download_flag) {
                    if(app_name && header_class_name && data_class_name) {
                        search_btn_html += '<button id="'+tableId+'_download_btn" class="btn btn-sm btn-default pull-right" title="Download">\
                                            <i class="fa fa-download"></i></button>';
                    }
                }

                search_btn_html += '<button id="'+tableId+'_search_btn" class="btn btn-sm btn-default pull-right">\
                                    <i class="fa fa-search"></i></button>';

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
                    try {
                        dtable.fnFilter("");
                    } catch(e) {
                        // console.log(e);
                    }
                }
                return;
            });

        $("#page_content_div").delegate("#"+tableId+"_search_btn",'click',function() {
            var search_text = $(".dataTables_filter input").val();
            if(search_text.length >= 2) {
                try {
                    dtable.fnFilter(search_text);
                } catch(e) {
                    // console.log(e);
                }
            }
        });

        $("#page_content_div").delegate("#"+tableId+"_download_btn",'click',function() {

            var main_url = base_url+"/downloader/datatable/?",
                url_get_param = "app="+app_name+"&rows="+data_class_name+"&headers="+header_class_name+"&headers_data="+header_extra_param+"&rows_data="+data_extra_param,
                download_url = main_url+""+url_get_param;

            $.ajax({
                url : download_url,
                type : "GET",
                success : function(result) {

                    var response = "";
            
                    if(typeof result == 'string') {
                        response = JSON.parse(result);
                    } else {
                        response = result;
                    }

                    $.gritter.add({
                        // (string | mandatory) the heading of the notification
                        title: table_title,
                        // (string | mandatory) the text inside the notification
                        text: response.message,
                        // (bool | optional) if you want it to fade out on its own or just sit there
                        sticky: true
                    });
                },
                error : function(err) {
                    $.gritter.add({
                        // (string | mandatory) the heading of the notification
                        title: table_title,
                        // (string | mandatory) the text inside the notification
                        text: err.statusText,
                        // (bool | optional) if you want it to fade out on its own or just sit there
                        sticky: false,
                        // Time in ms after which the gritter will dissappear.
                        time : 1500
                    });
                }
            });
        });

    };
}