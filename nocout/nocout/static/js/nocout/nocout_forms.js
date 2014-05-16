$(document).ready(function (e) {

    var inputContainers = $(".formContainer .col-sm-9");
    for (var i = 0; i < inputContainers.length; i++) {
        var childrenCount = inputContainers[i].children.length;
        if (childrenCount == 2) {
            var errCLass = $.trim(inputContainers[i].children[1].className);
            if (errCLass == "errorlist") {
                var formGroup = inputContainers[i].parentElement;
                formGroup.className = formGroup.className + " has-error";
            }
        }
    }
});
/*It removes the error class from fields if exists*/
function resetForm() {
    var inputContainers = $(".formContainer .col-sm-9");
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
}