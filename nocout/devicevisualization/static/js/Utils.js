/*Map Control Click*/
OpenLayers.Control.Click = OpenLayers.Class(OpenLayers.Control, {
    defaultHandlerOptions: {
        'single': true,
        'double': false,
        'pixelTolerance': 0,
        'stopSingle': false,
        'stopDouble': false
    },

    initialize: function(options) {
        this.handlerOptions = OpenLayers.Util.extend(
            {}, this.defaultHandlerOptions
            );
        OpenLayers.Control.prototype.initialize.apply(
            this, arguments
            );
        this.handler = new OpenLayers.Handler.Click(
            this, {
                'click': this.trigger
            }, this.handlerOptions
            );
    },

    trigger: function(e) {
        whiteMapClass.mapClickEvent(e);
    }
});

Number.prototype.toRad = function() {
    return this * Math.PI / 180;
}

Number.prototype.toDeg = function() {
    return this * 180 / Math.PI;
}

/*This function gets the Points Lat lng at specific angle and radius */
function getAtXYDirection(brng, dist, lon, lat) {
    dist = dist / 6371;
    brng = brng.toRad();
    var lat1 = lat.toRad(), lon1 = lon.toRad();

    var lat2 = Math.asin(Math.sin(lat1) * Math.cos(dist) + Math.cos(lat1) * Math.sin(dist) * Math.cos(brng));
    var lon2 = lon1 + Math.atan2(Math.sin(brng) * Math.sin(dist) * Math.cos(lat1), Math.cos(dist) - Math.sin(lat1) * Math.sin(lat2));

    if (isNaN(lat2) || isNaN(lon2)) return null;

    return {lat: lat2.toDeg(), lon: lon2.toDeg()};
}

/*This function converts dms lat lon to decimal degree lat lon*/
function dmsToDegree(latLng) {

    var new_pt = NaN,degrees,minutes,seconds,hemisphere;

    degrees = Number(latLng[1]);
    minutes = typeof (latLng[2]) !== "undefined" ? Number(latLng[2]) / 60 : 0;
    seconds = typeof (latLng[3]) !== "undefined" ? Number(latLng[3]) / 3600 : 0;
    hemisphere = latLng[4] || null;
    if (hemisphere !== null && /[SW]/i.test(hemisphere)) {
        degrees = Math.abs(degrees) * -1;
    }
    if(degrees < 0) {
        new_pt = degrees - minutes - seconds;
    } else {
        new_pt = degrees + minutes + seconds;
    }

    return new_pt;
}

/*
Function to show Error Message
 */
function showErrorMessage(errormsg, response) {
    console.log(errormsg, response);
}


function displayBounds(feature, lon, lat){
    var bounds = feature.geometry.getBounds();
    var lonlat = new OpenLayers.LonLat(lon, lat);

    if ((lonlat.lon < bounds.left) || (lonlat.lat > bounds.top) || (lonlat.lat < bounds.bottom) ||(lonlat.lon > bounds.right) ) {
        return 'out';
    }
    return 'in';
}



// OpenLayers.Strategy.Cluster = OpenLayers.Class(OpenLayers.Strategy, {

//     /**
//      * APIProperty: distance
//      * {Integer} Pixel distance between features that should be considered a
//      *     single cluster.  Default is 20 pixels.
//      */
//     distance: 20,

//     /**
//      * APIProperty: threshold
//      * {Integer} Optional threshold below which original features will be
//      *     added to the layer instead of clusters.  For example, a threshold
//      *     of 3 would mean that any time there are 2 or fewer features in
//      *     a cluster, those features will be added directly to the layer instead
//      *     of a cluster representing those features.  Default is null (which is
//      *     equivalent to 1 - meaning that clusters may contain just one feature).
//      */
//     threshold: null,

//     /**
//      * Property: features
//      * {Array(<OpenLayers.Feature.Vector>)} Cached features.
//      */
//     features: null,

//     /**
//      * Property: clusters
//      * {Array(<OpenLayers.Feature.Vector>)} Calculated clusters.
//      */
//     clusters: null,

//     /**
//      * Property: clustering
//      * {Boolean} The strategy is currently clustering features.
//      */
//     clustering: false,

//     /**
//      * Property: resolution
//      * {Float} The resolution (map units per pixel) of the current cluster set.
//      */
//     resolution: null,

//     /**
//      * Constructor: OpenLayers.Strategy.Cluster
//      * Create a new clustering strategy.
//      *
//      * Parameters:
//      * options - {Object} Optional object whose properties will be set on the
//      *     instance.
//      */

//     /**
//      * APIMethod: activate
//      * Activate the strategy.  Register any listeners, do appropriate setup.
//      * 
//      * Returns:
//      * {Boolean} The strategy was successfully activated.
//      */
//     activate: function() {
//         var activated = OpenLayers.Strategy.prototype.activate.call(this);
//         if(activated) {
//             this.layer.events.on({
//                 "beforefeaturesadded": this.cacheFeatures,
//                 "moveend": this.cluster,
//                 scope: this
//             });
//         }
//         return activated;
//     },

//     /**
//      * APIMethod: deactivate
//      * Deactivate the strategy.  Unregister any listeners, do appropriate
//      *     tear-down.
//      * 
//      * Returns:
//      * {Boolean} The strategy was successfully deactivated.
//      */
//     deactivate: function() {
//         var deactivated = OpenLayers.Strategy.prototype.deactivate.call(this);
//         if(deactivated) {
//             this.clearCache();
//             this.layer.events.un({
//                 "beforefeaturesadded": this.cacheFeatures,
//                 "moveend": this.cluster,
//                 scope: this
//             });
//         }
//         return deactivated;
//     },

//     /**
//      * Method: cacheFeatures
//      * Cache features before they are added to the layer.
//      *
//      * Parameters:
//      * event - {Object} The event that this was listening for.  This will come
//      *     with a batch of features to be clustered.
//      *     
//      * Returns:
//      * {Boolean} False to stop features from being added to the layer.
//      */
//     cacheFeatures: function(event) {
//         var propagate = true;
//         if(!this.clustering) {
//             this.clearCache();
//             this.features = event.features;
//             this.cluster();
//             propagate = false;
//         }
//         return propagate;
//     },

//     /**
//      * Method: clearCache
//      * Clear out the cached features.
//      */
//     clearCache: function() {
//         this.features = null;
//     },

//     /**
//      * Method: cluster
//      * Cluster features based on some threshold distance.
//      *
//      * Parameters:
//      * event - {Object} The event received when cluster is called as a
//      *     result of a moveend event.
//      */
//     cluster: function(event) {
//         if((!event || event.zoomChanged || (event && event.recluster)) && this.features) {
//             var resolution = this.layer.map.getResolution();
//             if(resolution != this.resolution || !this.clustersExist() || (event && event.recluster)) {
//                 this.resolution = resolution;
//                 var clusters = [];
//                 var feature, clustered, cluster;
//                 for(var i=0; i<this.features.length; ++i) {
//                     feature = this.features[i];
//                     if(feature.geometry) {
//                         clustered = false;
//                         for(var j=clusters.length-1; j>=0; --j) {
//                             cluster = clusters[j];
//                             if(this.shouldCluster(cluster, feature)) {
//                                 this.addToCluster(cluster, feature);
//                                 clustered = true;
//                                 break;
//                             }
//                         }
//                         if(!clustered) {
//                             clusters.push(this.createCluster(this.features[i]));
//                         }
//                     }
//                 }
//                 this.layer.removeAllFeatures();
//                 if(clusters.length > 0) {
//                     if(this.threshold > 1) {
//                         var clone = clusters.slice();
//                         clusters = [];
//                         var candidate;
//                         for(var i=0, len=clone.length; i<len; ++i) {
//                             candidate = clone[i];
//                             if(candidate.attributes.count < this.threshold) {
//                                 Array.prototype.push.apply(clusters, candidate.cluster);
//                             } else {
//                                 clusters.push(candidate);
//                             }
//                         }
//                     }
//                     this.clustering = true;
//                     // A legitimate feature addition could occur during this
//                     // addFeatures call.  For clustering to behave well, features
//                     // should be removed from a layer before requesting a new batch.
//                     this.layer.addFeatures(clusters);
//                     this.clustering = false;
//                 }
//                 this.clusters = clusters;
//             }
//         }
//     },

//     /**
//      * Method: recluster
//      * User-callable function to recluster features
//      * Useful for instances where a clustering attribute (distance, threshold, ...)
//      *     has changed
//      */
//     recluster: function(){
//         var event={"recluster":true};
//         this.cluster(event);
//     },

//     /**
//      * Method: clustersExist
//      * Determine whether calculated clusters are already on the layer.
//      *
//      * Returns:
//      * {Boolean} The calculated clusters are already on the layer.
//      */
//     clustersExist: function() {
//         var exist = false;
//         if(this.clusters && this.clusters.length > 0 &&
//            this.clusters.length == this.layer.features.length) {
//             exist = true;
//             for(var i=0; i<this.clusters.length; ++i) {
//                 if(this.clusters[i] != this.layer.features[i]) {
//                     exist = false;
//                     break;
//                 }
//             }
//         }
//         return exist;
//     },

//     /**
//      * Method: shouldCluster
//      * Determine whether to include a feature in a given cluster.
//      *
//      * Parameters:
//      * cluster - {<OpenLayers.Feature.Vector>} A cluster.
//      * feature - {<OpenLayers.Feature.Vector>} A feature.
//      *
//      * Returns:
//      * {Boolean} The feature should be included in the cluster.
//      */
//     shouldCluster: function(cluster, feature) {
//         var cc = cluster.geometry.getBounds().getCenterLonLat();
//         var fc = feature.geometry.getBounds().getCenterLonLat();
//         var distance = (
//             Math.sqrt(
//                 Math.pow((cc.lon - fc.lon), 2) + Math.pow((cc.lat - fc.lat), 2)
//             ) / this.resolution
//         );
//         return (distance <= this.distance);
//     },

//     /**
//      * Method: addToCluster
//      * Add a feature to a cluster.
//      *
//      * Parameters:
//      * cluster - {<OpenLayers.Feature.Vector>} A cluster.
//      * feature - {<OpenLayers.Feature.Vector>} A feature.
//      */
//     addToCluster: function(cluster, feature) {
//         cluster.cluster.push(feature);
//         cluster.attributes.count += 1;
//     },

//     /**
//      * Method: createCluster
//      * Given a feature, create a cluster.
//      *
//      * Parameters:
//      * feature - {<OpenLayers.Feature.Vector>}
//      *
//      * Returns:
//      * {<OpenLayers.Feature.Vector>} A cluster.
//      */
//     createCluster: function(feature) {
//         var center = feature.geometry.getBounds().getCenterLonLat();
//         var cluster = new OpenLayers.Feature.Vector(
//             new OpenLayers.Geometry.Point(center.lon, center.lat),
//             {count: 1}
//         );
//         cluster.cluster = [feature];
//         return cluster;
//     },

//     CLASS_NAME: "OpenLayers.Strategy.Cluster" 
// });

OpenLayers.Strategy.Cluster = OpenLayers.Class(OpenLayers.Strategy, {

    /**
     * APIProperty: distance
     * {Integer} Pixel distance between features that should be considered a
     *     single cluster.  Default is 20 pixels.
     */
    distance: 20,

    /**
     * APIProperty: threshold
     * {Integer} Optional threshold below which original features will be
     *     added to the layer instead of clusters.  For example, a threshold
     *     of 3 would mean that any time there are 2 or fewer features in
     *     a cluster, those features will be added directly to the layer instead
     *     of a cluster representing those features.  Default is null (which is
     *     equivalent to 1 - meaning that clusters may contain just one feature).
     */
    threshold: null,

    /**
     * Property: features
     * {Array(<OpenLayers.Feature.Vector>)} Cached features.
     */
    features: null,

    /**
     * Property: clusters
     * {Array(<OpenLayers.Feature.Vector>)} Calculated clusters.
     */
    clusters: null,

    /**
     * Property: clustering
     * {Boolean} The strategy is currently clustering features.
     */
    clustering: false,

    /**
     * Property: resolution
     * {Float} The resolution (map units per pixel) of the current cluster set.
     */
    resolution: null,

    /**
     * Constructor: OpenLayers.Strategy.Cluster
     * Create a new clustering strategy.
     *
     * Parameters:
     * options - {Object} Optional object whose properties will be set on the
     *     instance.
     */

    /**
     * APIMethod: activate
     * Activate the strategy.  Register any listeners, do appropriate setup.
     * 
     * Returns:
     * {Boolean} The strategy was successfully activated.
     */
    activate: function() {
        var activated = OpenLayers.Strategy.prototype.activate.call(this);
        if(activated) {
            this.layer.events.on({
                "beforefeaturesadded": this.cacheFeatures,
                "moveend": this.cluster,
                scope: this
            });
        }
        return activated;
    },

    /**
     * APIMethod: deactivate
     * Deactivate the strategy.  Unregister any listeners, do appropriate
     *     tear-down.
     * 
     * Returns:
     * {Boolean} The strategy was successfully deactivated.
     */
    deactivate: function() {
        var deactivated = OpenLayers.Strategy.prototype.deactivate.call(this);
        if(deactivated) {
            this.clearCache();
            this.layer.events.un({
                "beforefeaturesadded": this.cacheFeatures,
                "moveend": this.cluster,
                scope: this
            });
        }
        return deactivated;
    },

    /**
     * Method: cacheFeatures
     * Cache features before they are added to the layer.
     *
     * Parameters:
     * event - {Object} The event that this was listening for.  This will come
     *     with a batch of features to be clustered.
     *     
     * Returns:
     * {Boolean} False to stop features from being added to the layer.
     */
    cacheFeatures: function(event) {
        var propagate = true;
        if(!this.clustering) {
            this.clearCache();
            this.features = event.features;
            this.cluster();
            propagate = false;
        }
        return propagate;
    },

    /**
     * Method: clearCache
     * Clear out the cached features.
     */
    clearCache: function() {
        this.features = null;
    },

    /**
     * Method: cluster
     * Cluster features based on some threshold distance.
     *
     * Parameters:
     * event - {Object} The event received when cluster is called as a
     *     result of a moveend event.
     */
    cluster: function(event) {
        if((!event || event.zoomChanged || (event && event.recluster)) && this.features) {
            var resolution = this.layer.map.getResolution();
            if(resolution != this.resolution || !this.clustersExist() || (event && event.recluster)) {
                this.resolution = resolution;
                var clusters = [];
                var feature, clustered, cluster;
                for(var i=0; i<this.features.length; ++i) {
                    feature = this.features[i];
                    if(feature.geometry) {
                        clustered = false;
                        for(var j=clusters.length-1; j>=0; --j) {
                            cluster = clusters[j];
                            if(this.shouldCluster(cluster, feature)) {
                                this.addToCluster(cluster, feature);
                                clustered = true;
                                break;
                            }
                        }
                        if(!clustered) {
                            clusters.push(this.createCluster(this.features[i]));
                        }
                    }
                }
                this.layer.removeAllFeatures();
                if(clusters.length > 0) {
                    if(this.threshold > 1) {
                        var clone = clusters.slice();
                        clusters = [];
                        var candidate;
                        for(var i=0, len=clone.length; i<len; ++i) {
                            candidate = clone[i];
                            if(candidate.attributes.count < this.threshold) {
                                Array.prototype.push.apply(clusters, candidate.cluster);
                            } else {
                                clusters.push(candidate);
                            }
                        }
                    }
                    this.clustering = true;
                    // A legitimate feature addition could occur during this
                    // addFeatures call.  For clustering to behave well, features
                    // should be removed from a layer before requesting a new batch.
                    this.layer.addFeatures(clusters);
                    this.clustering = false;
                }
                this.clusters = clusters;
            }
        }
    },

    /**
     * Method: recluster
     * User-callable function to recluster features
     * Useful for instances where a clustering attribute (distance, threshold, ...)
     *     has changed
     */
    recluster: function(){
        var event={"recluster":true};
        this.cluster(event);
    },

    /**
     * Method: clustersExist
     * Determine whether calculated clusters are already on the layer.
     *
     * Returns:
     * {Boolean} The calculated clusters are already on the layer.
     */
    clustersExist: function() {
        var exist = false;
        if(this.clusters && this.clusters.length > 0 &&
           this.clusters.length == this.layer.features.length) {
            exist = true;
            for(var i=0; i<this.clusters.length; ++i) {
                if(this.clusters[i] != this.layer.features[i]) {
                    exist = false;
                    break;
                }
            }
        }
        return exist;
    },

    /**
     * Method: shouldCluster
     * Determine whether to include a feature in a given cluster.
     *
     * Parameters:
     * cluster - {<OpenLayers.Feature.Vector>} A cluster.
     * feature - {<OpenLayers.Feature.Vector>} A feature.
     *
     * Returns:
     * {Boolean} The feature should be included in the cluster.
     */
    shouldCluster: function(cluster, feature) {
        var cc = cluster.geometry.getBounds().getCenterLonLat();
        var fc = feature.geometry.getBounds().getCenterLonLat();
        var distance = (
            Math.sqrt(
                Math.pow((cc.lon - fc.lon), 2) + Math.pow((cc.lat - fc.lat), 2)
            ) / this.resolution
        );
        return (distance <= this.distance);
    },

    /**
     * Method: addToCluster
     * Add a feature to a cluster.
     *
     * Parameters:
     * cluster - {<OpenLayers.Feature.Vector>} A cluster.
     * feature - {<OpenLayers.Feature.Vector>} A feature.
     */
    addToCluster: function(cluster, feature) {
        cluster.cluster.push(feature);
        cluster.attributes.count += 1;
    },

    /**
     * Method: createCluster
     * Given a feature, create a cluster.
     *
     * Parameters:
     * feature - {<OpenLayers.Feature.Vector>}
     *
     * Returns:
     * {<OpenLayers.Feature.Vector>} A cluster.
     */
    createCluster: function(feature) {
        var center = feature.geometry.getBounds().getCenterLonLat();
        var cluster = new OpenLayers.Feature.Vector(
            new OpenLayers.Geometry.Point(center.lon, center.lat),
            {count: 1}
        );
        cluster.cluster = [feature];
        return cluster;
    },

    CLASS_NAME: "OpenLayers.Strategy.Cluster" 
});


function createAdvanceFilterHtml(formEl) {
    var templateData= "", formElements= "";
    var elementsArray = [];
    templateData += '<div class="iframe-container"><div class="content-container"><div id="whiteMapAdvanceFilter" class="advanceFiltersContainer">';
    templateData += '<form id="white_map_filter_form"><div class="form-group form-horizontal">';
    for(var i=0;i<formEl.length;i++) {
        if(formEl[i] != null) {
            formElements += '<div class="form-group"><label for="'+formEl[i].key+'" class="col-sm-4 control-label">';
            formElements += formEl[i].title;
            formElements += '</label><div class="col-sm-8">';

            var currentKey = $.trim(formEl[i].key);
            var elementType = $.trim(formEl[i].element_type);

            /*Check Element Type*/
            if(elementType == "multiselect") {

                var filterValues = formEl[i].values;
                if(filterValues.length > 0) {
                    formElements += '<select multiple class="multiSelectBox col-md-12" id="filter_'+formEl[i].key+'">';
                    for(var j=0;j<filterValues.length;j++) {
                        formElements += '<option value="'+filterValues[j]+'">'+filterValues[j]+'</option>';
                    }
                    formElements += '</select>';
                } else {
                    formElements += '<input type="text" id="filter_'+formEl[i].key+'" name="'+formEl[i].key+'"  class="form-control"/>';
                }
            }
            formElements += '</div></div>';
            elementsArray.push(formElements);
            formElements = "";
        }
    }
    templateData += elementsArray.join('');
    templateData += '<div class="clearfix"></div></div><div class="clearfix"></div></form>';
    templateData += '<div class="clearfix"></div></div></div><iframe class="iframeshim" frameborder="0" scrolling="no"></iframe></div><div class="clearfix"></div>';

    $("#advFilterFormContainer").html(templateData);

    if($("#advFilterContainerBlock").hasClass("hide")) {
        $("#advFilterContainerBlock").removeClass("hide");
    }

    /*Initialize the select2*/
    $(".advanceFiltersContainer select").select2();
}

function createAdvanceSearchHtml(formEl) {
    var templateData= "", formElements= "";
    var elementsArray = [];
    templateData += '<div class="iframe-container"><div class="content-container"><div id="whiteMapAdvanceSearch" class="advanceSearchContainer">';
    templateData += '<form id="white_map_search_form"><div class="form-group form-horizontal">';
    for(var i=0;i<formEl.length;i++) {
        if(formEl[i] != null) {
            formElements += '<div class="form-group"><label for="'+formEl[i].key+'" class="col-sm-4 control-label">';
            formElements += formEl[i].title;
            formElements += '</label><div class="col-sm-8">';

            var currentKey = $.trim(formEl[i].key);
            var elementType = $.trim(formEl[i].element_type);

            /*Check Element Type*/
            if(elementType == "multiselect") {

                var filterValues = formEl[i].values;
                if(filterValues.length > 0) {
                    formElements += '<select multiple class="multiSelectBox col-md-12" id="search_'+formEl[i].key+'">';
                    for(var j=0;j<filterValues.length;j++) {
                        formElements += '<option value="'+filterValues[j]+'">'+filterValues[j]+'</option>';
                    }
                    formElements += '</select>';
                } else {
                    formElements += '<input type="text" id="search_'+formEl[i].key+'" name="'+formEl[i].key+'"  class="form-control"/>';
                }
            }
            formElements += '</div></div>';
            elementsArray.push(formElements);
            formElements = "";
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
}

/**
 * This event triggers keypress event on lat,lon search text box
 */
function isLatLon(e) {

    var entered_key_code = (e.keyCode ? e.keyCode : e.which),
        entered_txt = $("#lat_lon_search").val();

    if(entered_key_code == 13) {
        if(entered_txt.length > 0) {
            if(entered_txt.split(",").length != 2) {
                alert("Please Enter Proper Lattitude,Longitude.");
                $("#lat_lon_search").val("");
            } else {
                
                var lat = +(entered_txt.split(",")[0]),
                    lng = +(entered_txt.split(",")[1]),
                    lat_check = (lat >= -90 && lat < 90),
                    lon_check = (lng >= -180 && lng < 180),
                    dms_pattern = /^(-?\d+(?:\.\d+)?)[°:d]?\s?(?:(\d+(?:\.\d+)?)['′:]?\s?(?:(\d+(?:\.\d+)?)["″]?)?)?\s?([NSEW])?/i;
                    dms_regex = new RegExp(dms_pattern);
                
                if((lat_check && lon_check) || (dms_regex.exec(entered_txt.split(",")[0]) && dms_regex.exec(entered_txt.split(",")[1]))) {
                    if((lat_check && lon_check)) {
                        whiteMapClass.zoomToLonLat(entered_txt);
                    } else {
                        var converted_lat = dmsToDegree(dms_regex.exec(entered_txt.split(",")[0]));
                        var converted_lng = dmsToDegree(dms_regex.exec(entered_txt.split(",")[1]));
                        whiteMapClass.zoomToLonLat(converted_lat+","+converted_lng);
                    }
                } else {
                    alert("Please Enter Proper Lattitude,Longitude.");
                    $("#lat_lon_search").val("");
                }                
            }                
        } else {
            alert("Please Enter Lattitude,Longitude.");
        }
    }
}