/*Global Variables*/
var that = "",

    hitCounter = 1,
    showLimit = 0,
    devicesCount = 0,
    counter = -999,
    devicesObject = {},
    treeDataArray = [],
    treeDataObject = {},
    isCallCompleted = 0,
    devicesCount = 0,
    devices_gmaps = [],
    main_devices_data_gmaps = [];


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
    var DataSourceTree = function (options) {
        this._data = options.data;
        this._delay = options.delay;
    }

    DataSourceTree.prototype.data = function (options, callback) {
        var self = this;
        var $data = null;

        if (!("name" in options) && !("type" in options)) {
            $data = this._data;//the root tree
            callback({ data: $data });
            return;
        }
        else if ("type" in options && options.type == "folder") {
            if ("additionalParameters" in options && "children" in options.additionalParameters)
                $data = options.additionalParameters.children;
            else $data = {}//no data
        }

        if ($data != null)//this setTimeout is only for mimicking some random delay
            setTimeout(function () {
                callback({ data: $data });
            }, parseInt(Math.random() * 500) + 200);
    };
    /*Prototyping End*/

    /**
     * This function is used to get the devices by calling the API
     * @class loadDeviceTreeLib
     * @method getDevices
     * @param infoObject {Object} It contains the domElement,username information object
     */
    this.getDevices = function (infoObject) {
        // alert();
        var this_of_this = this;

        // var username = infoObject.username;

        if (counter > 0 || counter == -999) {

            /*Ajax call not completed yet*/
            isCallCompleted = 0;
            /*To Enable The Cross Domain Request*/
            $.support.cors = true;

            /*Ajax call to the API*/
            $.ajax({
                url: "/device/stats/?total_count=" + devicesCount + "&page_number=" + hitCounter,
                type: "GET",
                dataType: "json",
                /*If data fetched successful*/
                success: function (result) {
                    if (result.success == 1) {

                        if (result.data.objects != null) {
                            hitCounter = hitCounter + 1;
                            /*First call case*/
                            if (devicesObject.data == undefined) {
                                /*Save the result json to the global variable for global access*/
                                devicesObject = result;
                                /*This will update if any filer is applied*/
                                devices_gmaps = devicesObject.data.objects.children;
                            } else {
                                devices_gmaps = devices_gmaps.concat(result.data.objects.children);
                            }
                            main_devices_data_gmaps = devices_gmaps;

                            if (devicesObject.data.objects.children.length > 0) {
                                /*Update the device count with the received data*/
                                if (devicesCount == 0) {
                                    devicesCount = devicesObject.data.meta.total_count;
                                }
                                /*Update the device count with the received data*/
                                if (devicesObject.data.meta.limit != undefined) {
                                    showLimit = devicesObject.data.meta.limit;
                                } else {
                                    showLimit = 1;
                                }

                                if (counter == -999) {
                                    counter = Math.floor(devicesCount / showLimit);
                                }

                                /*Decrement the counter*/
                                counter = counter - 1;


                                /*Call the function after 3 sec. for lazyloading*/
                                setTimeout(function () {
                                    this_of_this.getDevices();
                                }, 10);

                            } else {
                                isCallCompleted = 1;
                            }
                        } else {
                            isCallCompleted = 1;
                            this_of_this.getCityStates();
                        }
                    } else {
                        isCallCompleted = 1;
                        this_of_this.getCityStates();
                    }
                },
                /*If data not fetched*/
                error: function (err) {
                    $.gritter.add({
                        // (string | mandatory) the heading of the notification
                        title: 'GIS - Server Error',
                        // (string | mandatory) the text inside the notification
                        text: 'No connection',
                        // (bool | optional) if you want it to fade out on its own or just sit there
                        sticky: false
                    });
                }
            });
        } else {

            /*Ajax call not completed yet*/
            isCallCompleted = 1;
            this_of_this.getCityStates();
        }
    };

    this.getCityStates = function () {
        var that = this;
        var stateObject = {};
        var citiesObject = {};
        /*Ajax call for filters data*/
        $.ajax({
            url: "http://localhost:8000/" + "device/filter/",
            success: function (result) {
                var filtersData = JSON.parse(result);

                var cityData = filtersData.data.objects.city.data;
                var stateData = filtersData.data.objects.state.data;

                $.grep(stateData, function (state) {
                    // console.log(state);
                    var stateId = state["id"];
                    if (stateObject[stateId] && stateObject[stateId].length > 0) {
                        stateObject[stateId].push(state["value"]);
                    } else {
                        stateObject[stateId] = [];
                        stateObject[stateId].push(state["value"]);
                    }

                });

                $.grep(cityData, function (city) {
                    // console.log(city);
                    var cityStateId = city["state_id"];
                    if (citiesObject[cityStateId] && citiesObject[cityStateId].length > 0) {
                        citiesObject[cityStateId].push(city["value"]);
                    } else {
                        citiesObject[cityStateId] = [];
                        citiesObject[cityStateId].push(city["value"]);
                    }
                });
                that.plotTree(stateObject, citiesObject);

            },
            error: function (err) {
                $.gritter.add({
                    // (string | mandatory) the heading of the notification
                    title: 'Basic Filters - Server Error',
                    // (string | mandatory) the text inside the notification
                    text: 'No connection',
                    // (bool | optional) if you want it to fade out on its own or just sit there
                    sticky: false
                });
            }
        });
    };


    //here we have all data
    this.plotTree = function (states, cities) {
        var mainTreeObject = [];
        for (var stateId in states) {
            if (states.hasOwnProperty(stateId)) {
                var stateObject = {};
                stateObject.name = states[stateId][0];
                if (cities[stateId] && cities[stateId].length) {
                    stateObject["additionalParameters"] = {"children": []};
                    for (var i = 0; i < cities[stateId].length; i++) {
                        var cityObject = {};
                        cityObject.name = cities[stateId][i];
                        var baseStationsInCities = main_devices_data_gmaps.filter(function (v) {
                            return v["data"]["city"] == cities[stateId][i];
                        });
                        if (baseStationsInCities && baseStationsInCities.length > 0) {
                            cityObject["additionalParameters"] = {"children": []};
                            for (var j = 0; j < baseStationsInCities.length; j++) {
                                var bsObject = {};
                                bsObject.name = baseStationsInCities[j]["name"];

                                var bsSectors = baseStationsInCities[j]["data"]["param"]["sector"];
                                if (bsSectors && bsSectors.length > 0) {
                                    bsObject["additionalParameters"] = {"children": []};
                                    for (var k = 0; k < bsSectors.length; k++) {
                                        var bsSector = {};
                                        bsSector.name = bsSectors[k]["info"][0]["value"];
                                        var sectorSubStations = bsSectors[k]["sub_station"];
                                        if (sectorSubStations && sectorSubStations.length > 0) {
                                            bsSector["additionalParameters"] = {"children": []};
                                            for (var l = 0; l < sectorSubStations.length; l++) {
                                                var ssObject = {};
                                                ssObject.name = sectorSubStations[l]["name"];
                                                ssObject.type = "item";
                                                bsSector["additionalParameters"]["children"].push(ssObject);
                                            }
                                            bsSector.type = "folder";
                                        } else {
                                            bsSector.type = "item";
                                        }
                                        bsObject["additionalParameters"]["children"].push(bsSector);
                                    }
                                    bsObject.type = "folder";
                                } else {
                                    bsObject.type = "item";
                                }
                                cityObject["additionalParameters"]["children"].push(bsObject);
                            }
                            cityObject.type = "folder";
                        } else {
                            cityObject.type = "item";
                        }
                        stateObject["additionalParameters"]["children"].push(cityObject);
                    }
                    stateObject.type = "folder";
                } else {
                    stateObject.type = "item";
                }
                mainTreeObject.push(stateObject);
            }
        }
        var treeDataSource = new DataSourceTree({data: mainTreeObject});
        $("#waitContainer").hide();
        $('#devicesTree').admin_tree({
            dataSource: treeDataSource,
            loadingHTML: '<div class="tree-loading"><i class="fa fa-spinner fa-2x fa-spin"></i> Loading...</div>',
            'open-icon': 'fa-minus-square',
            'close-icon': 'fa-plus-square',
            // multiSelect:true,
            // 'selectable' : true,
            'selected-icon': null,//'fa-check',
            'unselected-icon': null,//'fa-times'
        });
        $('.tree').find('[class*="fa-"]').addClass("fa");
    }

    /**
     * This function is used to load the tree view with the devices data
     * @class loadDeviceTreeLib
     * @method loadDevices
     * @param devicesData {Object} It contains the devices heirarchy object
     * @param domElement "String" It is the DOM element selector on which the tree view is created
     */
    this.loadDevices = function (devicesData, domElement) {

        for (var i = 0; i < devicesData.length; i++) {

            if (devicesData[i].children.length > 0) {
                treeDataObject[devicesData[i].name] = {"name": devicesData[i].data.alias + " (" + devicesData[i].name + " / " + devicesData[i].data.ip + " / " + devicesData[i].data.mac + ")", "type": "folder", "additionalParameters": {"children": ""}};
            } else {
                treeDataObject[devicesData[i].name] = {"name": devicesData[i].data.alias + " (" + devicesData[i].name + " / " + devicesData[i].data.ip + " / " + devicesData[i].data.mac + ")", "type": "item"};
            }

            var slaveCount = devicesData[i].children.length;
            var child = {};
            for (var j = 0; j < slaveCount; j++) {
                child[devicesData[i].children[j].name] = { "name": "<a href='/network_maps/gis/" + devicesData[i].children[j].name + "'><i class='fa fa-arrow-circle-right'></i> " + devicesData[i].children[j].data.alias + " (" + devicesData[i].children[j].name + " / " + devicesData[i].children[j].data.ip + " / " + devicesData[i].children[j].data.mac + ")</a>", "type": "item" };
                treeDataObject[devicesData[i].name]["additionalParameters"]["children"] = child;
            }
        }

        var treeDataSource = new DataSourceTree({data: treeDataObject});

        $('#' + domElement).admin_tree({
            dataSource: treeDataSource,
            loadingHTML: '<div class="tree-loading"><i class="fa fa-spinner fa-2x fa-spin"></i> Loading...</div>',
            'open-icon': 'fa-minus-square',
            'close-icon': 'fa-plus-square',
            // multiSelect:true,
            // 'selectable' : true,
            'selected-icon': null,//'fa-check',
            'unselected-icon': null,//'fa-times'
        });
        //To add font awesome support
        $('.tree').find('[class*="fa-"]').addClass("fa");

    };

//    (function (a, b) {
//        a.fn.admin_tree = function (d) {
//            var c = {
//                "open-icon": "fa fa-folder-open",
//                "close-icon": "fa fa-folder",
//                selectable: true,
//                "selected-icon": "fa fa-check",
//                "unselected-icon": "tree-dot"
//            };
//            c = a.extend({}, c, d);
//            this.each(function () {
//                var e = a(this);
//                e.html('<div class = "tree-folder" style="display:none;">				<div class="tree-folder-header">					<i class="' + c["close-icon"] + '"></i>					<div class="tree-folder-name"></div>				</div>				<div class="tree-folder-content"></div>				<div class="tree-loader" style="display:none"></div>			</div>			<div class="tree-item" style="display:none;">				' + (c["unselected-icon"] == null ? "" : '<i class="' + c["unselected-icon"] + '"></i>') + '				<div class="tree-item-name"></div>			</div>');
//                e.addClass(c.selectable == true ? "tree-selectable" : "tree-unselectable");
//                e.tree(c)
//            });
//            return this
//
//        }

        DataSourceTree.prototype.data = function (options, callback) {
            var self = this;
            var $data = null;

            if (!("name" in options) && !("type" in options)) {
                $data = this._data;//the root tree
                callback({ data: $data });
                return;
            }
            else if ("type" in options && options.type == "folder") {
                if ("additionalParameters" in options && "children" in options.additionalParameters)
                    $data = options.additionalParameters.children;
                else $data = {}//no data
            }

            if ($data != null)//this setTimeout is only for mimicking some random delay
                setTimeout(function () {
                    callback({ data: $data });
                }, parseInt(Math.random() * 500) + 200);
        };
        /*Prototyping End*/

        /**
         * This function is used to get the devices by calling the API
         * @class loadDeviceTreeLib
         * @method getDevices
         * @param infoObject {Object} It contains the domElement,username information object
         */
        this.getDevices = function (infoObject) {

            var username = infoObject.username;

            if (counter > 0 || counter == -999) {

                if ($("#waitContainer").hasClass("hide")) {

                    $("#waitContainer").removeClass("hide");
                }

                /*To Enable The Cross Domain Request*/
                $.support.cors = true;
                /*Ajax call to the API*/
                $.ajax({
                    crossDomain: true,
                    url: "/device/stats/?&page_number=" + hitCounter + "&total_count=" + showLimit,
                    // url : "http://127.0.0.1:8000/device/stats/?username="+username+"&page_number="+hitCounter+"&limit="+showLimit,
                    type: "GET",
                    dataType: "json",
                    /*If data fetched successful*/
                    success: function (result) {

                        if (result.data.objects != null) {

                            hitCounter = hitCounter + 1;
                            /*First call case*/
                            if (devicesObject.data == undefined) {

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

                            if (counter == -999) {
                                counter = Math.round(devicesCount / showLimit);
                            }

                            if (devicesObject.success == 1) {

                                /*Recursive Calling*/
                                setTimeout(function () {
                                    that.getDevices(infoObject);
                                }, 1500);
                            }

                            counter = counter - 1;
                        }
                    },
                    error: function (err) {
                        console.log(err.statusText);
                    }
                });
            } else {

                that.loadDevices(devices, infoObject.domElement);
                if (!$("#waitContainer").hasClass("hide")) {

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
        this.loadDevices = function (devicesData, domElement) {

            for (var i = 0; i < devicesData.length; i++) {

                if (devicesData[i].children.length > 0) {
                    treeDataObject[devicesData[i].name] = {"name": devicesData[i].data.alias + " (" + devicesData[i].name + " / " + devicesData[i].data.ip + " / " + devicesData[i].data.mac + ")", "type": "folder", "additionalParameters": {"children": ""}};
                } else {
                    treeDataObject[devicesData[i].name] = {"name": devicesData[i].data.alias + " (" + devicesData[i].name + " / " + devicesData[i].data.ip + " / " + devicesData[i].data.mac + ")", "type": "item"};
                }

                var slaveCount = devicesData[i].children.length;
                var child = {};
                for (var j = 0; j < slaveCount; j++) {
                    child[devicesData[i].children[j].name] = { "name": "<a href='/network_maps/gis/" + devicesData[i].children[j].name + "'><i class='fa fa-arrow-circle-right'></i> " + devicesData[i].children[j].data.alias + " (" + devicesData[i].children[j].name + " / " + devicesData[i].children[j].data.ip + " / " + devicesData[i].children[j].data.mac + ")</a>", "type": "item" };
                    treeDataObject[devicesData[i].name]["additionalParameters"]["children"] = child;
                }
            }

            var treeDataSource = new DataSourceTree({data: treeDataObject});

            $('#' + domElement).admin_tree({
                dataSource: treeDataSource,
                loadingHTML: '<div class="tree-loading"><i class="fa fa-spinner fa-2x fa-spin"></i> Loading...</div>',
                'open-icon': 'fa-minus-square',
                'close-icon': 'fa-plus-square',
                // multiSelect:true,
                // 'selectable' : true,
                'selected-icon': null,//'fa-check',
                'unselected-icon': null//'fa-times'
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
                    e.tree(c);
                });
                return this
            }
        })(window.jQuery);
    }