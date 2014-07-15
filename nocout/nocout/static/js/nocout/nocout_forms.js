/**
 * This file shows the validation error on any form
 * @uses jQuery.js
 * @uses gritter.js
 */
$(document).ready(function (e) {

    /*Initialize the variables*/
    var hasError = 0,
        inputContainers = $(".formContainer .col-md-9"),
        labelContainer = $(".formContainer label.col-sm-3");
        errorMessage = '<ul class="list-unstyled">';
    console.log(inputContainers);
    for (var i = 0; i < inputContainers.length; i++) {    	
        /*Total no. of childrens in col-sm-7 class*/
        var childrenCount = inputContainers[i].children.length;
        console.log(childrenCount);
        if (childrenCount == 3) {

            /*Error class from server side validation check*/
            var errCLass = $.trim(inputContainers[i].children[1].className);
            if (errCLass == "errorlist") {
                
                /*Field name on which error occured*/
                var fieldName = $.trim(labelContainer[i].innerHTML);

                /*Error message from server side*/
                var errMsg = $.trim(inputContainers[i].children[1].childNodes[0].innerHTML);

                /*Id of the text box*/
                var fieldId = inputContainers[i].children[0].id;
                /*Concat the error message & field name to show them in validation error gritter*/
                errorMessage += '<li><i class="fa fa-bug text-danger"></i> <a href="#'+fieldId+'">'+fieldName+' : '+errMsg+'</a></li>';
                
                /*Add has-error class to parent div to show the text field & label red.*/
                var formGroup = inputContainers[i].parentElement;
                formGroup.className = formGroup.className + " has-error";

                /*Update hasError variable by 1 f any error occured*/
                hasError = 1;
            }
        }
    }
    errorMessage += '</ul>';
    $(".errorlist").hide();

    if(hasError == 1) {
        var validationErrors = $.gritter.add({
            // (string | mandatory) the heading of the notification
            title: 'Validation Error',
            // (string | mandatory) the text inside the notification
            text: errorMessage,
            // (bool | optional) if you want it to fade out on its own or just sit there
            sticky: true
        });
    }
});

/*It removes the error class from fields if exists*/
function resetForm() {    
    var inputContainers = $(".formContainer .col-md-9");
    /*Remove the error class from all the fields.*/
    for (var i = 0; i < inputContainers.length; i++) {
        var childrenCount = inputContainers[i].children.length;
        if (childrenCount == 2) {
            var errCLass = $.trim(inputContainers[i].children[1].className);

            if (errCLass == "errorlist") {
                inputContainers[i].children[1].remove();
                inputContainers[i].parentElement.className = "form-group";
            }
        }
    }
    /*Remove the gritter popup when reset button is clicked*/
    $("#gritter-notice-wrapper").empty();
}