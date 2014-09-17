var ipStationFound= 0;
var ipStation= [];

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
        maxZoomLevel: 15
    }

    this.filtersList= [];

    this.appliedSearch= [];

    this.searchMarkers= [];

    this.searchedCircuitLines= [];

    this.showNotification= function() {
        if(!$("span#gis_search_status_txt").length) {
            $("<br /><span id='gis_search_status_txt'>"+this.constants.statusText+"</span><button class='btn btn-sm btn-danger pull-right' style='padding:2px 5px;margin:-3px;' onclick='resetAdvanceSearch();'>Reset</button>").insertAfter("#gis_status_txt");
        }
    }

    this.hideNotification= function() {
        if($("span#gis_search_status_txt").length) {
            $("span#gis_search_status_txt").prev().remove();
            $("span#gis_search_status_txt").next().remove();
            $("span#gis_search_status_txt").remove();
        }
    }

    //We will remove all Setted Search Markers here in the Array from the map and then clear the Array.
    this.removeSearchMarkers= function() {
        var markers= this.searchMarkers;
        for(var i=0; i< markers.length; i++) {
            markers[i].setMap(null);
        }
        this.searchMarkers= [];
    }

    //Here we create a new Marker based on the lat, long and show it on the map.
    this.applyIconToSearchedResult= function(lat, long, iconUrl) {
        var searchMarker, searchedInputs, isOnlyStateorCityIsApplied= false;
        
        //create a new marker
        searchMarker = new google.maps.Marker({position: new google.maps.LatLng(lat, long), zIndex: 999});
        //push marker in the previouslySearchedMarkersList array
        this.searchMarkers.push(searchMarker);

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
                                var s= currentItem["values"][j]["value"];
                                s= s.substring(s.lastIndexOf("(")+1,s.lastIndexOf(")"));
                                formElement+= '<option value="'+s+'">'+s+'</option>';
                            } else {
                                formElement+= '<option value="'+currentItem["values"][j].value+'">'+currentItem["values"][j].value+'</option>';
                            }
                        }
                        if(currentItem["key"]=== "sector_configured_on") {
                            var a= markersMasterObj['SS'];
                            for(var key in a) {
                                formElement += '<option value="'+a[key]['dataset'][12]['value']+'">'+a[key]['dataset'][12]['value']+'</option>';
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
        $("form#searchInfoModal_form > div .form-group").each(function(i , formEl) {
            var key= $(formEl).find('label.control-label').html();

            var selectedValues= [];

            $(formEl).find('ul.select2-choices li.select2-search-choice').each(function(i, selectedli) {
                selectedValues.push($(selectedli).find('div').html());
            });

            ob[key]= selectedValues;

            var selectedSelectId= $(formEl).find('select').select2('val');

            var forAttr= $(formEl).find('label.control-label').attr('for');
            search_self.appliedSearch.push({field: forAttr, value: selectedSelectId});
        });
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
            if(searchedNames.length && searchedNames.indexOf(deviceJson["name"]) === -1) {
                return false;
            }

            //check for Ip next
            var searchedIps = selectedInputs["IP"];
            var isSearchedIpPresent= false;
            var isSubStationIpPresent= false;
            if(searchedIps.length) {
                var deviceSectorConfiguredOn= deviceJson["sector_configured_on_devices"].split(" ");
                var deviceIps = deviceSectorConfiguredOn.map(function(sectorConfigured) {
                    if(sectorConfigured) {
                        return sectorConfigured.substring(sectorConfigured.lastIndexOf("(")+1,sectorConfigured.lastIndexOf(")"));
                    }
                });

                var common = $.grep(deviceIps, function(element) {
                    return $.inArray(element, searchedIps ) !== -1;
                });
                if(common.length) {
                    isSearchedIpPresent= true;
                }
                for(var count0= 0; count0< searchedIps.length; count0++) {
                    for(var count= 0; count< deviceJson["data"]["param"]["sector"].length; count++) {
                        if(deviceJson["data"]["param"]["sector"][count]["sub_station"][0]) {
                            if(deviceJson["data"]["param"]["sector"][count]["sub_station"][0]["data"]["substation_device_ip_address"]== searchedIps[count0]) {
                                extendBound(deviceJson["data"]["param"]["sector"][count]["sub_station"][0]["data"]["lat"], deviceJson["data"]["param"]["sector"][count]["sub_station"][0]["data"]["lon"]);
                                search_self.applyIconToSearchedResult(deviceJson["data"]["param"]["sector"][count]["sub_station"][0]["data"]["lat"], deviceJson["data"]["param"]["sector"][count]["sub_station"][0]["data"]["lon"]);
                                isSearchedIpPresent= true;
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
                var deviceCircuidIds= deviceJson["circuit_ids"].split(" ");

                var common = $.grep(deviceCircuidIds, function(element) {
                    return $.inArray(element, searchedCircuitIds ) !== -1;
                });

                if(common.length) {
                    for(var count0= 0; count0< common.length; count0++) {
                        for(var count=0; count< deviceJson["data"]["param"]["sector"].length; count++) {
                            if(deviceJson["data"]["param"]["sector"][count]["circuit_id"]== common[count0]) {
                                extendBound(deviceJson["data"]["param"]["sector"][count]["sub_station"][0]["data"]["lat"], deviceJson["data"]["param"]["sector"][count]["sub_station"][0]["data"]["lon"]);
                                search_self.applyIconToSearchedResult(deviceJson["data"]["param"]["sector"][count]["sub_station"][0]["data"]["lat"], deviceJson["data"]["param"]["sector"][count]["sub_station"][0]["data"]["lon"],search_self.constants.search_ss_icon);
                                isCircuitIdPresent= true;
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

            return isValid;
        }
        //reset previous markers
        this.removeSearchMarkers();
        this.resetVariables();

        var bounds= new google.maps.LatLngBounds();
        function extendBound(lat, lon) {
            bounds.extend(new google.maps.LatLng(lat, lon));
        }



        
        var searchedStations= [];
        for(var i=0; i< devicesInMap.length; i++) {
            if(checkIfValid(devicesInMap[i])) {
                searchedStations.push(devicesInMap[i]);
                bounds.extend(new google.maps.LatLng(devicesInMap[i]['data']['lat'], devicesInMap[i]['data']['lon']));
                this.applyIconToSearchedResult(devicesInMap[i]['data']['lat'], devicesInMap[i]['data']['lon']);
            }

            if(ipStationFound) {
                bounds.extend(new google.maps.LatLng(ipStation[0], ipStation[1]));
            }
        }


        if(this.searchedCircuitLines.length) {
            for(var i=0; i< this.searchedCircuitLines.length; i++) {
                bounds.extend(this.searchedCircuitLines[i]);
            }
        }

        if(searchedStations.length) {
            if(searchedStations.length > this.constants.max_search_items) {
                // this.searchedLinesByCircuitIDs= [];
                this.removeSearchMarkers();
            }

            mapInstance.fitBounds(bounds);
            if(mapInstance.getZoom() >= this.constants.maxZoomLevel) {
                mapInstance.setZoom(this.constants.maxZoomLevel);
            }
            this.showNotification();
        } else {
            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: 'GIS : Search',
                // (string | mandatory) the text inside the notification
                text: 'No data found for the given Searchterm.',
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false
            });

            mapInstance.setCenter(new google.maps.LatLng(21.1500,79.0900));
            mapInstance.setZoom(5);
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
    };
}