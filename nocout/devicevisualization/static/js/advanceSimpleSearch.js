var ipStationFound= 0,
    ipStation= [],
    searchMarkers_global = [],
    search_marker_count = 0;

/*Get The Root URL*/
var base_url;
if(window.location.origin) {
    base_url = window.location.origin;
} else {
    base_url = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
}

/**
 * This class is used to Advance Search.
 * @class advanceSearchMainClass
 * @uses jQuery
 * @uses Select2
 * Coded By :- Rahul Garg
 */
function advanceSearchMainClass() {

    this.constants= {
        search_bs_icon: base_url+'/static/img/icons/bs_bounce.png',
        search_ss_icon: base_url+'/static/img/icons/ss_bounce.png',
        max_search_items: 20,
        search_limit_message: 'Too many Searched Results. Please filter again. No Markers drawn',
        statusText: "Advance Search Applied",
        maxZoomLevel: 15,
        errorText: 'No Search Result!'
    }

    this.filtersList= [];

    this.appliedSearch= [];

    this.searchMarkers= [];

    this.searchedCircuitLines= [];

    this.showNotification= function() {
        if(!$("li#gis_search_status_txt").length) {
            $("#gis_status_txt").append("<li id='gis_search_status_txt'>"+this.constants.statusText+" <button class='btn btn-sm btn-danger pull-right' style='padding:2px 5px;margin:-3px;' onclick='resetAdvanceSearch();'>Reset</button></li>");
        }
    }

    this.hideNotification= function() {
        if($("li#gis_search_status_txt").length) {
            $("li#gis_search_status_txt").remove();
        }
    }

    //We will remove all Setted Search Markers here in the Array from the map and then clear the Array.
    this.removeSearchMarkers= function() {

        if(window.location.pathname.indexOf("googleEarth") > -1) {

            var children = ge.getFeatures().getChildNodes();
            for(var i=0;i<children.getLength();i++) { 
                var child = children.item(i);
                if(child.getId().indexOf("search_") > -1) {
                    ge.getFeatures().removeChild(child);
                }
            }
        } else {
            var markers = this.searchMarkers;
            for(var i=0; i< markers.length; i++) {
                markers[i].setMap(null);
            }
        }

        this.searchMarkers= [];
        this.search_marker_count = 0
    }

    //Here we create a new Marker based on the lat, long and show it on the map.
    this.applyIconToSearchedResult = function(lat, long, iconUrl) {
        var searchMarker, searchedInputs, isOnlyStateorCityIsApplied= false;
        search_marker_count++;

        if(window.location.pathname.indexOf("googleEarth") > -1) {
            // Create BS placemark.
            var searchMarker = ge.createPlacemark('search_'+search_marker_count);
            // Define a custom icon.
            var search_icon = ge.createIcon('');
            search_icon.setHref(base_url+"/"+iconUrl);
            var search_style = ge.createStyle(''); //create a new style
            search_style.getIconStyle().setIcon(search_icon); //apply the icon to the style
            searchMarker.setStyleSelector(search_style); //apply the style to the placemark         
            
            // Set the placemark's location.
            var search_point = ge.createPoint('');
            search_point.setLatitude(lat);
            search_point.setLongitude(long);
            searchMarker.setGeometry(search_point);
            // Add the placemark to Earth.
            ge.getFeatures().appendChild(searchMarker);

            var gex = new GEarthExtensions(ge);
            gex.fx.bounce(searchMarker, {
                duration: 300,
                repeat: 0,
                dampen: 0.3
            });

        } else {

            //create a new marker
            searchMarker = new google.maps.Marker({position: new google.maps.LatLng(lat, long), zIndex: 999});

            //IF NOT FILTER APPLIED IS IN CITY OR STATE, THEN WE WILL NOT CHANGE ANY ICONS
            searchedInputs= this.getInputArray();

            if(searchedInputs['BS Name'].length || searchedInputs['Circuit Id'].length || searchedInputs['IP'].length) {
                isOnlyStateorCityIsApplied= false;
            }

            if(!isOnlyStateorCityIsApplied) {
                    if(iconUrl) {
                        //set icon from global object
                        searchMarker.setIcon(iconUrl);  
                    } else {
                        //set icon from global object
                        searchMarker.setIcon(this.constants.search_bs_icon);
                    }
                    //set animation to marker bounce
                    if(searchMarker.getAnimation() != null) {
                        searchMarker.setAnimation(null);
                    } else {
                        searchMarker.setAnimation(google.maps.Animation.BOUNCE);
                    }
                    //show the marker on map.
                    searchMarker.setMap(mapInstance);
            }

            google.maps.event.addListener(searchMarker, 'click', function() {
                if(iconUrl) {
                    google.maps.event.trigger(markersMasterObj['SS'][String(lat)+long], 'click');
                } else {
                    google.maps.event.trigger(markersMasterObj['BS'][String(lat)+long], 'click');
                }
            });
        }

        //push marker in the previouslySearchedMarkersList array
        this.searchMarkers.push(searchMarker);
        searchMarkers_global.push(searchMarker);

        return ;
    }

    this.prepareAdvanceSearchHtml= function(domElemet) {
        var templateData= "", i=0, elementsArray= [], formElement= "", j=0;
        this.filtersList= getDataForAdvanceSearch();

        templateData+= '<div class="iframe-container"><div class="content-container"><div id="'+domElemet+'" class="advanceSearchContainer">';
        templateData += '<form id="'+domElemet+'_form"><div class="form-horizontal">';
        for(i=0; i< this.filtersList.length; i++) {
            var currentItem= this.filtersList[i];
            formElement= "";
            if(currentItem) {
                formElement+= '<div class="form-group">';
                formElement+= '<label for="'+currentItem.key+'" class="col-sm-4 control-label">'+currentItem.title+'</label>';
                formElement+= '<div class="col-sm-8">';
                if($.trim(currentItem["element_type"]== "multiselect")) {
                    if(currentItem["values"].length) {
                        formElement+= '<select multiple class="multiSelectBox col-md-12" id="search_'+currentItem.key+'">';
                        for(j=0; j< currentItem["values"].length; j++) {
                            if(currentItem["key"]=== "sector_configured_on") {
                                var sector_config_val = currentItem["values"][j]["value"];
                                formElement+= '<option value="'+sector_config_val+'">'+sector_config_val+'</option>';
                            } else if(currentItem["key"]=== "name") {
                                formElement+= '<option value="'+currentItem["values"][j].value+'">'+currentItem["values"][j].alias+'</option>';
                            } else {
                                formElement+= '<option value="'+currentItem["values"][j].value+'">'+currentItem["values"][j].value+'</option>';
                            }
                        }
                        formElement+= "</select>";
                    }
                }
                formElement += '</div></div>';
                elementsArray.push(formElement);
            }
        }

        templateData += elementsArray.join('');
        templateData += '<div class="clearfix"></div></div><div class="clearfix"></div></form>';
        templateData += '<div class="clearfix"></div></div></div><iframe class="iframeshim" frameborder="0" scrolling="no"></iframe></div><div class="clearfix"></div>';

        $("#advSearchFormContainer").html(templateData);

        if($("#advSearchContainerBlock").hasClass("hide")) {
            $("#advSearchContainerBlock").removeClass("hide");
        }

        /*Initialize the select2*/
        $(".advanceSearchContainer select").select2();

        hideSpinner();

        if(this.appliedSearch.length != 0) {
            for(var z=0; z< this.appliedSearch.length; z++) {
                var currentItem= this.appliedSearch[z];
                if(currentItem["value"].length) {
                    $("#search_"+currentItem["field"]).select2("val", currentItem["value"]);
                }
            }
        }
    }

    this.findTheLineToUpdate= function(device,searchedText) {
        for(var i=0; i< device['data']['param']['sector'].length; i++) {
            for(var j=0; j< searchedText.length; j++) {
                if((String(searchedText[j]).toLowerCase())== (String(device['data']['param']['sector'][i]['circuit_id']).toLowerCase())) {                   
                    this.applyIconToSearchedResult(device['data']['param']['sector'][i]['sub_station'][0]['data']['lat'], device['data']['param']['sector'][i]['sub_station'][0]['data']['lon'], this.constants.search_ss_icon);
                    this.searchedCircuitLines.push(new google.maps.LatLng(device['data']['param']['sector'][i]['sub_station'][0]['data']['lat'], device['data']['param']['sector'][i]['sub_station'][0]['data']['lon']));
                }    
            }
        }
    }


    this.getInputArray= function() {
        var ob= {};
        var search_self= this;
        // $("form#searchInfoModal_form > div .form-group").each(function(i , formEl) {
        //     var key= $(formEl).find('label.control-label').html();

        //     var selectedValues= [];

        //     $(formEl).find('ul.select2-choices li.select2-search-choice').each(function(i, selectedli) {
        //         selectedValues.push($(selectedli).find('div').html());
        //     });

        //     ob[key]= selectedValues;

        //     var selectedSelectId= $(formEl).find('select').select2('val');

        //     var forAttr= $(formEl).find('label.control-label').attr('for');
        //     search_self.appliedSearch.push({field: forAttr, value: selectedSelectId});
        // });

        var select2_boxes = $("form#searchInfoModal_form > div .form-group");

        for(var i=0;i<select2_boxes.length;i++) {
            var label_txt = select2_boxes[i].children[0].innerHTML,
                select_box_div = select2_boxes[i].children[1].children,
                select_box_id = select_box_div[select_box_div.length-1].id,
                selected_values = $("#"+select_box_id).select2("val");
                ob[label_txt] = selected_values; 
        }

        return ob;
    }

    /**
     * This method generates get parameter for setfilter API & call setFilter function
     * @method callSetFilter
     */
    this.searchAndCenterData = function(devicesInMap) {
        ipStationFound= 0;
        ipStation= [];
        var search_self= this;
        var selectedInputs= this.getInputArray();

        function checkIfValid(deviceJson) {
            var isValid= true;

            //check for name first
            var searchedNames= selectedInputs["BS Name"];
            var isNamePresent= false;
            if(searchedNames.length && searchedNames.indexOf(deviceJson["name"]) === -1) {
                return false;
            }

            isNamePresent= true;

            //check for Ip next
            var searchedIps = selectedInputs["IP"];
            var isSearchedIpPresent= false;

            var isSsWasSearched= false, isBsWasSearched= false;

            if(searchedIps.length) {
                var deviceSectorConfiguredOn= deviceJson["sector_configured_on_devices"].split("|");
                var common = $.grep(deviceSectorConfiguredOn, function(element) {
                    return $.inArray(element, searchedIps ) !== -1;
                });
                if(common.length) {

                    for(var c=0; c< common.length; c++) {
                        var ip= common[c];
                        for(var d=0; d< deviceJson["data"]["param"]["sector"].length; d++) {
                            var currentSector= deviceJson["data"]["param"]["sector"][d];
                            if(currentSector["sector_configured_on"]== ip) {
                                if(!isBsWasSearched) {
                                    isBsWasSearched= true;
                                }
                                isSearchedIpPresent= true;            
                            }

                            for(var e=0; e< currentSector["sub_station"].length; e++) {
                                var currentSs= currentSector["sub_station"][e];
                                if(currentSs["data"]["substation_device_ip_address"]== ip) {
                                    isSearchedIpPresent= true;
                                    if(!isSsWasSearched) {
                                        isSsWasSearched= true;
                                    }
                                    extendBound(currentSs["data"]["lat"], currentSs["data"]["lon"]);
                                    search_self.applyIconToSearchedResult(currentSs["data"]["lat"], currentSs["data"]["lon"],search_self.constants.search_ss_icon);
                                }
                            }
                        }
                    }
                }
                if(!isSearchedIpPresent) {
                    return false;
                }
            }


            //check for circuit id
            var searchedCircuitIds= selectedInputs["Circuit Id"];
            var isCircuitIdPresent= false;
            if(searchedCircuitIds.length) {
                var deviceCircuidIds= deviceJson["circuit_ids"].split("|");

                var common = $.grep(deviceCircuidIds, function(element) {
                    return $.inArray(element, searchedCircuitIds ) !== -1;
                });

                if(common.length) {
                    for(var c=0; c< common.length; c++) {
                        var circuidId= common[c];
                        for(var d=0; d< deviceJson["data"]["param"]["sector"].length; d++) {
                            var currentSector= deviceJson["data"]["param"]["sector"][d];
                            for(var e=0; e< currentSector["sub_station"].length; e++) {
                                var currentSs= currentSector["sub_station"][e];
                                if($.trim(currentSs["data"]["param"]["sub_station"][3]["value"])=== circuidId) {
                                    extendBound(currentSs["data"]["lat"], currentSs["data"]["lon"]);
                                    search_self.applyIconToSearchedResult(currentSs["data"]["lat"], currentSs["data"]["lon"],search_self.constants.search_ss_icon);
                                    isCircuitIdPresent= true;
                                }
                            }
                        }
                    }
                }

                if(!isCircuitIdPresent) {
                    return false;
                }
            }

            //check for city
            var searchedCity= selectedInputs["BS City"];
            if(searchedCity.length && searchedCity.indexOf(deviceJson["data"]["city"]) === -1) {
                return false;
            }

            if(isSsWasSearched && !(searchedCircuitIds.length && isCircuitIdPresent) && !(searchedNames.length && isNamePresent) && !isBsWasSearched) {
                return 'onlySSFound';
            }

            return isValid;
        }
        //reset previous markers
        this.removeSearchMarkers();
        this.resetVariables();

        var bounds = "";
        if(window.location.pathname.indexOf("googleEarth") > -1) {
            
        } else {
            bounds= new google.maps.LatLngBounds();
        }

        function extendBound(lat, lon) {
            if(window.location.pathname.indexOf("googleEarth") > -1) {

                  var lookAt = ge.createLookAt('');
                  lookAt.setLatitude(lat);
                  lookAt.setLongitude(lon);
                  lookAt.setRange(8000);
                  ge.getView().setAbstractView(lookAt);
            } else {

                bounds.extend(new google.maps.LatLng(lat, lon));
            }
        }



        
        var searchedStations= [];
        for(var i=0; i< devicesInMap.length; i++) {
            if(checkIfValid(devicesInMap[i])) {

                searchedStations.push(devicesInMap[i]);

                if(window.location.pathname.indexOf("googleEarth") > -1) {

                } else {
                    bounds.extend(new google.maps.LatLng(devicesInMap[i]['data']['lat'], devicesInMap[i]['data']['lon']));
                }
                if(checkIfValid(devicesInMap[i])=== 'onlySSFound') {

                } else {
                    this.applyIconToSearchedResult(devicesInMap[i]['data']['lat'], devicesInMap[i]['data']['lon']);
                    
                }
            }

            if(ipStationFound) {
                bounds.extend(new google.maps.LatLng(ipStation[0], ipStation[1]));
            }
        }


        if(this.searchedCircuitLines.length) {
            for(var i=0; i< this.searchedCircuitLines.length; i++) {
                if(window.location.pathname.indexOf("googleEarth") > -1) {

                } else {
                    bounds.extend(this.searchedCircuitLines[i]);
                }
            }
        }

        if(searchedStations.length) {
            if(searchedStations.length > this.constants.max_search_items) {
                // this.searchedLinesByCircuitIDs= [];
                this.removeSearchMarkers();
            }
            if(window.location.pathname.indexOf("googleEarth") > -1) {
                
            } else {
                mapInstance.fitBounds(bounds);
                if(mapInstance.getZoom() >= this.constants.maxZoomLevel) {
                    mapInstance.setZoom(this.constants.maxZoomLevel);
                }
            }
            this.showNotification();
        } else {
            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: 'GIS : Search',
                // (string | mandatory) the text inside the notification
                text: search_self.constants.errorText,
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false
            });

            // mapInstance.setCenter(new google.maps.LatLng(21.1500,79.0900));
            // mapInstance.setZoom(5);
            this.hideNotification();
        }

        hideSpinner();
        $("#advSearchFormContainer").html("");
        if(!($("#advSearchContainerBlock").hasClass("hide"))) {
            $("#advSearchContainerBlock").addClass("hide");
        }
    }

    /**
     * This function reset all variable used in the process
     * @class advanceSearchLib
     * @method resetVariables
     */
    this.resetVariables = function() {
        this.filtersList= [];
        this.appliedSearch= [];
        this.searchMarkers= [];
        this.searchedCircuitLines= [];
        this.search_marker_count = 0;
    };
}