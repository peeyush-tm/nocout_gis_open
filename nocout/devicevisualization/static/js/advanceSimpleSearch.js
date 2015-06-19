var ipStationFound = 0,
    ipStation = [],
    searchMarkers_global = [],
    search_marker_count = 0;

/**
 * This class is used to Advance Search.
 * @class advanceSearchMainClass
 * @uses jQuery
 * @uses Select2
 * Coded By :- Rahul Garg
 */
function advanceSearchMainClass() {

    this.constants = {
        search_bs_icon        :  base_url+'/static/img/icons/bs_bounce.png',
        search_ss_icon        :  base_url+'/static/img/icons/ss_bounce.png',
        max_search_items      :  20,
        search_limit_message  :  'Too many Searched Results. Please filter again. No Markers drawn',
        statusText            :  "Advance Search Applied",
        maxZoomLevel          :  15,
        errorText             :  'No Search Result!'
    }

    this.filtersList = [];
    this.appliedSearch = [];
    this.searchMarkers = [];
    this.searchedCircuitLines = [];
    
    /**
     * This function will remove all plotted Search Markers from the map and reset variables.
     * @method removeSearchMarkers
     */
    this.removeSearchMarkers = function() {

        if(window.location.pathname.indexOf("gearth") > -1) {

            var children = ge.getFeatures().getChildNodes();
            for(var i=0;i<children.getLength();i++) { 
                var child = children.item(i);
                if(child.getId().indexOf("search_") > -1) {
                    ge.getFeatures().removeChild(child);
                }
            }
        } else if(window.location.pathname.indexOf("wmap") > -1) {
            ccpl_map.getLayersByName("Search Layer")[0].removeAllFeatures();
            ccpl_map.getLayersByName("Search Layer")[0].setVisibility(false);
        } else {
            var markers = this.searchMarkers;
            for(var i=0; i< markers.length; i++) {
                markers[i].setMap(null);
            }
        }

        this.searchMarkers= [];
        this.search_marker_count = 0
    };

    /**
     * This function draws marker on the search result
     * @method applyIconToSearchedResult
     */
    this.applyIconToSearchedResult = function(lat, long, iconUrl) {

        var searchMarker, searchedInputs, isOnlyStateorCityIsApplied= false;
        search_marker_count++;

        if(window.location.pathname.indexOf("gearth") > -1) {

            iconUrl = iconUrl ? iconUrl : base_url+'/static/img/icons/bs_bounce.png';
            // Create the placemark.
            searchMarker = ge.createPlacemark('search_'+search_marker_count);

            // Define a custom icon.
            var icon = ge.createIcon('');
            icon.setHref(iconUrl);
            
            var style = ge.createStyle(''); //create a new style
            style.getIconStyle().setIcon(icon); //apply the icon to the style
            searchMarker.setStyleSelector(style); //apply the style to the searchMarker
            style.getIconStyle().setScale(4.0);

            // Set the searchMarker's location.  
            var point = ge.createPoint('');
            point.setLatitude(lat);
            point.setLongitude(long);
            searchMarker.setGeometry(point);

        } else if (window.location.pathname.indexOf("wmap") > -1) {
            
            ccpl_map.getLayersByName("Search Layer")[0].setVisibility(true);

            //create a new marker
            searchMarker = whiteMapClass.createOpenLayerVectorMarker(undefined, undefined, long, lat, {icon: icon});
            if(searchMarker) {
                if(iconUrl) {
                    //set icon from global object
                    searchMarker.attributes.icon = iconUrl;
                } else {
                    //set icon from global object
                    searchMarker.attributes.icon = this.constants.search_bs_icon;
                }
            }
            
            ccpl_map.getLayersByName("Search Layer")[0].addFeatures([searchMarker]);
        } else {

            //create a new marker
            searchMarker = new google.maps.Marker({position: new google.maps.LatLng(lat, long), zIndex: 999});

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
    };

    /**
     * This function reset all variable used in the process
     * @method resetVariables
     */
    this.resetVariables = function() {
        this.filtersList= [];
        this.appliedSearch= [];
        this.searchMarkers= [];
        searchMarkers_global = [];
        this.searchedCircuitLines= [];
        this.search_marker_count = 0;
    };
}