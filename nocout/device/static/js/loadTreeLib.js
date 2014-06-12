/*Global Variables*/
var that = "",
	hitCounter = 1,
	showLimit = 0,
	devicesCount = 0,
	counter = -999,
	devicesObject = {},
	treeDataArray = [],
	treeDataObject = {};

/**
 * This class is used to create the tree view of devices
 * @class loadDeviceTreeLib
 * @uses jQuery
 * @uses fuelux.tree.js
 * Coded By :- Yogender Purohit
 */
function loadDeviceTreeLib() {	

	/*Store the reference of current pointer in a global variable*/
	that = this;

	/*Tree View Data Source Prototyping*/
	var DataSourceTree = function(options) {
		this._data 	= options.data;
		this._delay = options.delay;
	}

	DataSourceTree.prototype.data = function(options, callback) {
		var self = this;
		var $data = null;

		if(!("name" in options) && !("type" in options)){
			$data = this._data;//the root tree
			callback({ data: $data });
			return;
		}
		else if("type" in options && options.type == "folder") {
			if("additionalParameters" in options && "children" in options.additionalParameters)
				$data = options.additionalParameters.children;
			else $data = {}//no data
		}
		
		if($data != null)//this setTimeout is only for mimicking some random delay
			setTimeout(function(){callback({ data: $data });} , parseInt(Math.random() * 500) + 200);
	};
	/*Prototyping End*/

	/**
	 * This function is used to get the devices by calling the API
	 * @class loadDeviceTreeLib
	 * @method getDevices
	 * @param infoObject {Object} It contains the domElement,username information object
	 */
	this.getDevices = function(infoObject) {

		var username = infoObject.username;

		if(counter > 0 || counter == -999) {

			if($("#waitContainer").hasClass("hide")) {
				
				$("#waitContainer").removeClass("hide");
			}

			/*To Enable The Cross Domain Request*/
			$.support.cors = true;			
			/*Ajax call to the API*/
			$.ajax({
				crossDomain: true,
				url : "../../device/stats/?username="+username+"&page_number="+hitCounter+"&limit="+showLimit,
				// url : "http://127.0.0.1:8000/device/stats/?username="+username+"&page_number="+hitCounter+"&limit="+showLimit,
				type : "GET",
				dataType : "json",
				/*If data fetched successful*/
				success : function(result) {

					if(result.data.objects != null) {

						hitCounter = hitCounter + 1;
						/*First call case*/
						if(devicesObject.data == undefined) {

							/*Save the result json to the global variable for global access*/
							devicesObject = result;
							/**/
							devices = devicesObject.data.objects.children;
						} else {

							devices = devices.concat(result.data.objects.children);
						}


						/*Update the device count with the received data*/
						devicesCount = devicesObject.data.meta.total_count;						

						/*Update the device count with the received data*/
						showLimit = devicesObject.data.meta.limit;

						if(counter == -999) {
							counter = Math.round(devicesCount/showLimit);
						}
						
						if(devicesObject.success == 1) {
							
							/*Recursive Calling*/
							setTimeout(function() {
								that.getDevices(infoObject);
							},1500);
						}

						counter = counter - 1;
					}
				},
				error : function(err) {
					console.log(err.statusText);
				}
			});
		} else {

			that.loadDevices(devices,infoObject.domElement);
			if(!$("#waitContainer").hasClass("hide")) {

				$("#waitContainer").addClass("hide");
			}
		}		
	};

	/**
	 * This function is used to load the tree view with the devices data
	 * @class loadDeviceTreeLib
	 * @method loadDevices
	 * @param devicesData {Object} It contains the devices heirarchy object
	 * @param domElement "String" It is the DOM element selector on which the tree view is created
	 */
	this.loadDevices = function(devicesData,domElement) {

		for(var i=0;i<devicesData.length;i++) {

			if(devicesData[i].children.length > 0) {
				treeDataObject[devicesData[i].name] = {"name" : devicesData[i].data.alias+" ("+devicesData[i].name+" / "+devicesData[i].data.ip+" / "+devicesData[i].data.mac+")", "type" : "folder","additionalParameters" : {"children" : ""}};
			} else {
				treeDataObject[devicesData[i].name] = {"name" : devicesData[i].data.alias+" ("+devicesData[i].name+" / "+devicesData[i].data.ip+" / "+devicesData[i].data.mac+")", "type" : "item"};
			}

			var slaveCount = devicesData[i].children.length;
			var child  = {};			
			for(var j=0;j<slaveCount;j++) {					
				child[devicesData[i].children[j].name] = { "name" : "<a href='/network_maps/gis/"+devicesData[i].children[j].name+"'><i class='fa fa-arrow-circle-right'></i> "+devicesData[i].children[j].data.alias+" ("+devicesData[i].children[j].name+" / "+devicesData[i].children[j].data.ip+" / "+devicesData[i].children[j].data.mac+")</a>" , "type" : "item" };
				treeDataObject[devicesData[i].name]["additionalParameters"]["children"] = child;
			}
		}

		var treeDataSource = new DataSourceTree({data: treeDataObject});

		$('#'+domElement).admin_tree({
			dataSource: treeDataSource,			
			loadingHTML:'<div class="tree-loading"><i class="fa fa-spinner fa-2x fa-spin"></i> Loading...</div>',
			'open-icon' : 'fa-minus-square',
			'close-icon' : 'fa-plus-square',
			// multiSelect:true,
			// 'selectable' : true,
			'selected-icon' : null,//'fa-check',
			'unselected-icon' : null,//'fa-times'
		});
		//To add font awesome support
		$('.tree').find('[class*="fa-"]').addClass("fa");

	};

	(function (a, b) {
    a.fn.admin_tree = function (d) {
        var c = {
            "open-icon": "fa fa-folder-open",
            "close-icon": "fa fa-folder",
            selectable: true,
            "selected-icon": "fa fa-check",
            "unselected-icon": "tree-dot"
        };
        c = a.extend({}, c, d);
        this.each(function () {
            var e = a(this);
            e.html('<div class = "tree-folder" style="display:none;">				<div class="tree-folder-header">					<i class="' + c["close-icon"] + '"></i>					<div class="tree-folder-name"></div>				</div>				<div class="tree-folder-content"></div>				<div class="tree-loader" style="display:none"></div>			</div>			<div class="tree-item" style="display:none;">				' + (c["unselected-icon"] == null ? "" : '<i class="' + c["unselected-icon"] + '"></i>') + '				<div class="tree-item-name"></div>			</div>');
            e.addClass(c.selectable == true ? "tree-selectable" : "tree-unselectable");
            e.tree(c)
        });
        return this
    }
})(window.jQuery);
}