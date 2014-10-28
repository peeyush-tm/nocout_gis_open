// javascript function to log the user actions.

function LogUserAction(module, action) {
    var csrftoken = getCookie('csrftoken');
    $.ajax({
        url : "/logs/actions/log/", 
        type : "POST",
        dataType: "json", 
        data : {
            module : module,
            action : action,
            csrfmiddlewaretoken : csrftoken,
            },
            success : function(response) {
                console.log(response)
            },
            error : function(xhr,errmsg,err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
    });
    return false;
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

