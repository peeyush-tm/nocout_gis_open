// bulk upload inventory
function bulk_upload_inventory_form(technology, sheetname, uploaded_by, current_status) {
    bulk_upload_inventory = '<h5 class="">Bulk Upload inventory information:</h5><br />';
    bulk_upload_inventory += '<div class=""><div class="box border red"><div class="box-title"><h4><i class="fa fa-table"></i>Bulk Upload</h4></div>';
    bulk_upload_inventory += '<div class="box-body"><table class="table">';
    bulk_upload_inventory += '<thead><tr><th>Technology</th><th>Sheetname</th><th>Uploaded By</th><th>Current Status</th></tr></thead>';
    bulk_upload_inventory += '<tr>';
    bulk_upload_inventory += '<td contenteditable="true" id="packets">'+technology+'</td>';
    bulk_upload_inventory += '<td contenteditable="true" id="timeout">'+sheetname+'</td>';
    bulk_upload_inventory += '<td contenteditable="true" id="normal_check_interval">'+uploaded_by+'</td>';
    bulk_upload_inventory += '<td contenteditable="true" id="normal_check_interval">'+current_status+'</td>';
    bulk_upload_inventory += '</tr>';
    bulk_upload_inventory += '</tbody>';
    bulk_upload_inventory += '</table>';
    bulk_upload_inventory += '</div></div></div>';
    bootbox.dialog({
        message: bulk_upload_inventory,
        title: "<span class='text-danger'><i class='fa fa-times'></i>Bulk Upload Inventory</span>",
        buttons: {
            success: {
                label: "Yes!",
                className: "btn-success",
                callback: function () {
                    window.location.assign();
                }
            },
            danger: {
                label: "No!",
                className: "btn-danger",
                callback: function () {
                    $(".bootbox").modal("hide");
                }
            }
        }
    });
}