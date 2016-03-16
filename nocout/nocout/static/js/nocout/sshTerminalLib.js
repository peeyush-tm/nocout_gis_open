/*Script for SSH-terminal */

/*variable console_html contains SSH-terminal html structure*/

var console_html =  '<div style="width: 100em; height: 40em;" id="ssh_popup_container">\
                        <iframe src="{0}/?u={1}&p={2}&d=10&machine={3}&ip={4}&type={5}" id="gadget0" frameborder="0" height="800" width="1400"></iframe>\
                    </div>';

/*Enabling Click event listener on console icon*/
$(".box-body").on('click', ".ssh_terminal", function(){

	ssh_machine_name = this.getAttribute("data-machine-name");
	ssh_device_ip = (this.getAttribute("data-ip-address")).trim();
	ssh_device_type = this.getAttribute("data-device-type");
	try {
		console_html = console_html.replace('{0}', ssh_url);
		console_html = console_html.replace('{1}', ssh_username);
		console_html = console_html.replace('{2}', ssh_password);
		console_html = console_html.replace('{3}', ssh_machine_name);
		console_html = console_html.replace('{4}', ssh_device_ip);
		console_html = console_html.replace('{5}', ssh_device_type);

	    /*Call the bootbox to show the popup with SSH-Terminal*/
	    bootbox.dialog({
	        title: 'SSH Terminal',
	        message: console_html
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
			// console.log('Done')
			console.log("HERE")
			var ssh_machine_name = response['data'][0]['machine_name'],
				ssh_device_ip = response['data'][0]['device_ip'],
				ssh_device_type = response['data'][0]['device_type'];

			console.log("Completed variables")

			try {
				console_html = console_html.replace('{0}', ssh_url);
				console_html = console_html.replace('{1}', ssh_username);
				console_html = console_html.replace('{2}', ssh_password);
				console_html = console_html.replace('{3}', ssh_machine_name);
				console_html = console_html.replace('{4}', ssh_device_ip);
				console_html = console_html.replace('{5}', ssh_device_type);

				console.log("console_html Completed")
			    /*Call the bootbox to show the popup with SSH-Terminal*/
			    bootbox.dialog({
			        title: 'SSH Terminal',
			        message: console_html
			    });

			    console.log("bootbox dialog finished")

			    $(".modal-dialog").css("width","80%");

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
			// console.log('Done in BS')
			var ssh_machine_name = response['data'][0]['machine_name'],
				ssh_device_ip = response['data'][0]['device_ip'],
				ssh_device_type = response['data'][0]['device_type'];

			try {
				console_html = console_html.replace('{0}', ssh_url);
				console_html = console_html.replace('{1}', ssh_username);
				console_html = console_html.replace('{2}', ssh_password);
				console_html = console_html.replace('{3}', ssh_machine_name);
				console_html = console_html.replace('{4}', ssh_device_ip);
				console_html = console_html.replace('{5}', ssh_device_type);

			    /*Call the bootbox to show the popup with SSH-Terminal*/
			    bootbox.dialog({
			        title: 'SSH Terminal',
			        message: console_html
			    });

			    $(".modal-dialog").css("width","80%");

			} catch(e) {
				// console.error(e);
			}
		}
	})

})