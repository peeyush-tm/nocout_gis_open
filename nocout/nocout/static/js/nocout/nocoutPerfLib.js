/**
 * This library is used to show live performance of particular device & its functionality
 * @class nocout.perf.lib
 * @uses FLOT CHARTS
 * Coded By :- Yogender Purohit
 */

/*Global Variables*/
var perf_that = "",
	allDevices = "",
	device_status = "";

 function nocoutPerfLib() {

 	/*Save reference of current pointer to the global variable*/
 	perf_that = this;

 	/**
 	 * This function call the server to get all the devices data & then populate it to the dropdown
 	 * @class nocout.perf.lib
 	 * @method getAllDevices
 	 * @param get_url "String", It contains the url to fetch the devices list.
 	 * @param device_id "INT", It contains the ID of current device.
 	 */
 	this.getAllDevices = function(get_url,device_id) {

		/*Ajax call to Get Devices API*/
		// $.ajax({
		// 	crossDomain: true,
		// 	url : get_url,
		// 	type : "GET",
		// 	dataType : "json",
		// 	success : function(result) {
				if(device_data.success == 1) {
					allDevices = device_data.data.objects;
					var devices_options = '<option value="">Select Device</option>';
					$.each(allDevices,function(key,value) {
						if(value.id == device_id) {
							devices_options += '<option value="'+value.id+'" selected>'+value.alias+'</option>';
						} else {
							devices_options += '<option value="'+value.id+'">'+value.alias+'</option>';
						}
					});
					$("#device_name").html(devices_options);
				} else {
					console.log(device_data.message);
				}
		// 	},
		// 	error : function(err) {
		// 		console.log(err);
		// 	}
		// });
 	};

 	/**
 	 * This function fetch the status of current device
 	 * @class nocout.perf.lib
 	 * @method getStatus
 	 * @param get_status_url "String", It contains the url to fetch the status of current device.
 	 * @param device_id "INT", It contains the ID of current device.
 	 */
 	this.getStatus = function(get_status_url,device_id) {

 		/*Ajax call to Get Devices API*/
		// $.ajax({
		// 	crossDomain: true,
		// 	url : get_url,
		// 	type : "GET",
		// 	dataType : "json",
		// 	success : function(result) {
				if(status_data.success == 1) {
					
					device_status = status_data.data.objects;
					/*Loop for table headers*/
					var headers = "<tr>";
					$.each(device_status.header,function(key,value) {
						headers += '<th>'+value+'</th>';
					});

					headers += "</tr>";
					/*Populate table headers*/
					$("#status_table thead").html(headers);

					/*Loop for status table data*/
					var status_val = "<tr>";
					$.each(device_status.values,function(key,value) {
						status_val += '<td>'+value+'</td>';
					});

					status_val += "</tr>";
					/*Populate table data*/
					$("#status_table tbody").html(status_val);
				} else {
					console.log(device_status.message);
				}
		// 	},
		// 	error : function(err) {
		// 		console.log(err);
		// 	}
		// });
 	};
 }