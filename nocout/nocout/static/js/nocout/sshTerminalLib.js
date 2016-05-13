/*Script for SSH-terminal */

/*variable console_html contains SSH-terminal html structure*/

var console_html =  '<div style="width: 100em; min-height: 500px;" id="ssh_popup_container">\
                        <iframe src="{0}/?machine={3}&ip={4}&type={5}&output=embed" id="gadget0" frameborder="0" height=90% width=90%></iframe>\
                    </div>';

/*Enabling Click event listener on console icon*/
$(".box-body").on('click', ".ssh_terminal", function(){

	ssh_machine_name = this.getAttribute("data-machine-name");
	ssh_device_ip = (this.getAttribute("data-ip-address")).trim();
	ssh_device_type = this.getAttribute("data-device-type");
	try {
		var ssh_terminal_html = console_html;
		ssh_terminal_html = ssh_terminal_html.replace('{0}', ssh_url);
		ssh_terminal_html = ssh_terminal_html.replace('{3}', ssh_machine_name);
		ssh_terminal_html = ssh_terminal_html.replace('{4}', ssh_device_ip);
		ssh_terminal_html = ssh_terminal_html.replace('{5}', ssh_device_type);

	    /*Call the bootbox to show the popup with SSH-Terminal*/
	    bootbox.dialog({
	        title: 'SSH Terminal',
	        message: ssh_terminal_html
	    });

	    $(".modal-dialog").css("width","80%");

	} catch(e) {
		// console.error(e);
	}

})

$(".controls_container").on('click', "#telnet_ss_btn", function(){

	$.ajax({
		url : base_url + '/performance/get_telnet_ss/?device_id=' + current_device,
		type : 'GET',
		success : function(response){
			var ssh_machine_name = response['data'][0]['machine_name'],
				ssh_device_ip = response['data'][0]['device_ip'],
				ssh_device_type = response['data'][0]['device_type'];

			try {
				var ss_console_html = console_html;
				ss_console_html = ss_console_html.replace('{0}', ssh_url);
				ss_console_html = ss_console_html.replace('{3}', ssh_machine_name);
				ss_console_html = ss_console_html.replace('{4}', ssh_device_ip);
				ss_console_html = ss_console_html.replace('{5}', ssh_device_type);

			    /*Call the bootbox to show the popup with SSH-Terminal*/
			    bootbox.dialog({
			        title: 'SSH Terminal',
			        message: ss_console_html
			    });


			    $(".modal-dialog").css("width","80%");
			    $(".modal-dialog").css("height","80%");

			} catch(e) {
				console.error(e);
			}
		}
	})

})

$(".controls_container").on('click', "#telnet_bs_btn", function(){

	$.ajax({
		url : base_url + '/performance/get_telnet_bs/?device_id=' + sector_configured_on_id,
		type : 'GET',
		success : function(response){
			var ssh_machine_name = response['data'][0]['machine_name'],
				ssh_device_ip = response['data'][0]['device_ip'],
				ssh_device_type = response['data'][0]['device_type'];

			try {
				var bs_console_html = console_html;
				bs_console_html = bs_console_html.replace('{0}', ssh_url);
				bs_console_html = bs_console_html.replace('{3}', ssh_machine_name);
				bs_console_html = bs_console_html.replace('{4}', ssh_device_ip);
				bs_console_html = bs_console_html.replace('{5}', ssh_device_type);

			    /*Call the bootbox to show the popup with SSH-Terminal*/
			    bootbox.dialog({
			        title: 'SSH Terminal',
			        message: bs_console_html
			    });

			    $(".modal-dialog").css("width","80%");
			    $(".modal-dialog").css("height","80%");

			} catch(e) {
				// console.error(e);
			}
		}
	})

})
