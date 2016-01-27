/*Script for SSH-terminal */

/*variable console_html contains gateone(SSH-terminal) html*/
var console_html =  '<div style="width: 100em; height: 40em;">\
                        <iframe src="https://127.0.0.1:8888/" id="gadget0" frameborder="0" height="800" width="1400"></iframe>\
                    </div>'

/*Enabling Click event listener on console icon*/
$(".box-body").on('click', ".ssh_terminal", function(){

    /*Call the bootbox to show the popup with SSH-Terminal*/
    bootbox.dialog({
        title: 'SSH Terminal',
        message: console_html
    });

    $(".modal-dialog").css("width","80%");

})