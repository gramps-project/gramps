/*
   Copyright (c) 2006-8, Tom Carden, Steve Coast, Mikel Maron, Andrew Turner, Henri Bergius, Rob Moran
   All rights reserved.

   Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 * Neither the name of the Mapstraction nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

// Revision: $Revision$

// Use http://jsdoc.sourceforge.net/ to generate documentation

/** @mapstraction */
(function(){

////////////////////////////
//
// utility to functions, TODO namespace or remove before release
//
///////////////////////////

/**
 * $m, the dollar function, elegantising getElementById()
 * @return An HTML element or array of HTML elements
 */
function $m() {
    var elements = [];
    for (var i = 0; i < arguments.length; i++) {
        var element = arguments[i];
        if (typeof(element) == 'string') {
            element = document.getElementById(element);
        }
        if (arguments.length == 1) {
            return element;
        }
        elements.push(element);
    }
    return elements;
}

/**
 * loadScript is a JSON data fetcher
 * @param {String} src URL to JSON file
 * @param {Function} callback Callback function
 */
function loadScript(src, callback) {
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = src;
    if (callback) {
        var evl = {};
        evl.handleEvent = function(e) {
            callback();
        };
        script.addEventListener('load' ,evl ,true);
    }
    document.getElementsByTagName('head')[0].appendChild(script);
    return;
}

/**
 *
 * @param {Object} point
 * @param {Object} level
 */
function convertLatLonXY_Yahoo(point, level) { //Mercator
    var size = 1 << (26 - level);
    var pixel_per_degree = size / 360.0;
    var pixel_per_radian = size / (2 * Math.PI);
    var origin = new YCoordPoint(size / 2 , size / 2);
    var answer = new YCoordPoint();
    answer.x = Math.floor(origin.x + point.lon * pixel_per_degree);
    var sin = Math.sin(point.lat * Math.PI / 180.0);
    answer.y = Math.floor(origin.y + 0.5 * Math.log((1 + sin) / (1 - sin)) * -pixel_per_radian);
    return answer;
}

/**
 * Load a stylesheet from a remote file.
 * @param {String} href URL to the CSS file
 */
function loadStyle(href) {
    var link = document.createElement('link');
    link.type = 'text/css';
    link.rel = 'stylesheet';
    link.href = href;
    document.getElementsByTagName('head')[0].appendChild(link);
    return;
}

/**
 * getStyle provides cross-browser access to css
 * @param {Object} el HTML Element
 * @param {String} prop Style property name
 */
function getStyle(el, prop) {
    var y;
    if (el.currentStyle) {
        y = el.currentStyle[prop];
    }
    else if (window.getComputedStyle) {
        y = window.getComputedStyle( el, '').getPropertyValue(prop);
    }
    return y;
}


/**
 * Convert longitude to metres
 * http://www.uwgb.edu/dutchs/UsefulData/UTMFormulas.HTM
 * "A degree of longitude at the equator is 111.2km... For other latitudes,
 * multiply by cos(lat)"
 * assumes the earth is a sphere but good enough for our purposes
 * @param {Float} lon
 * @param {Float} lat
 */
function lonToMetres(lon, lat) {
    return lon * (111200 * Math.cos(lat * (Math.PI / 180)));
}

/**
 * Convert metres to longitude
 * @param {Object} m
 * @param {Object} lat
 */
function metresToLon(m, lat) {
    return m / (111200 * Math.cos(lat * (Math.PI / 180)));
}

/**
 * Convert kilometres to miles
 * @param {Float} km
 * @returns {Float} miles
 */
function KMToMiles(km) {
	return km / 1.609344;
}

/**
 * Convert miles to kilometres
 * @param {Float} miles
 * @returns {Float} km
 */
function milesToKM(miles) {
	return miles * 1.609344;
}

// stuff to convert google zoom levels to/from degrees
// assumes zoom 0 = 256 pixels = 360 degrees
//         zoom 1 = 256 pixels = 180 degrees
// etc.

/**
 *
 * @param {Object} pixels
 * @param {Object} zoom
 */
function getDegreesFromGoogleZoomLevel(pixels, zoom) {
    return (360 * pixels) / (Math.pow(2, zoom + 8));
}

/**
 *
 * @param {Object} pixels
 * @param {Object} degrees
 */
function getGoogleZoomLevelFromDegrees(pixels, degrees) {
    return logN((360 * pixels) / degrees, 2) - 8;
}

/**
 *
 * @param {Object} number
 * @param {Object} base
 */
function logN(number, base) {
    return Math.log(number) / Math.log(base);
}

/////////////////////////////
//
// Mapstraction proper begins here
//
/////////////////////////////

/**
 * Mapstraction instantiates a map with some API choice into the HTML element given
 * @param {String} element The HTML element to replace with a map
 * @param {String} api The API to use, one of 'google', 'yahoo', 'microsoft', 'openstreetmap', 'multimap', 'map24', 'openlayers', 'mapquest'
 * @param {Bool} debug optional parameter to turn on debug support - this uses alert panels for unsupported actions
 * @constructor
 */
function Mapstraction(element,api,debug) {
    this.api = api; // could detect this from imported scripts?
    this.maps = {};
    this.currentElement = $m(element);
    this.eventListeners = [];
    this.markers = [];
    this.layers = [];
    this.polylines = [];
    this.images = [];
    this.loaded = {};
    this.onload = {};

    // Mapstraction.writeInclude(api, "nothing");

    // optional debug support
    if (debug === true) {
        this.debug = true;
    }
    else {
        this.debug = false;
    }

    // This is so that it is easy to tell which revision of this file
    // has been copied into other projects.
    this.svn_revision_string = '$Revision$';
    this.addControlsArgs = {};

    // if (this.currentElement) {
    this.addAPI($m(element), api);
// }
}


/**
 * Change the current api on the fly
 * @param {String} api The API to swap to
 * @param element
 */
Mapstraction.prototype.swap = function(element,api) {
    if (this.api == api) {
        return;
    }

    var center = this.getCenter();
    var zoom = this.getZoom();

    this.currentElement.style.visibility = 'hidden';
    this.currentElement.style.display = 'none';


    this.currentElement = $m(element);
    this.currentElement.style.visibility = 'visible';
    this.currentElement.style.display = 'block';

    this.api = api;

    if (this.maps[this.api] === undefined) {
        this.addAPI($m(element),api);

        this.setCenterAndZoom(center,zoom);

        for (var i = 0; i < this.markers.length; i++) {
            this.addMarker(this.markers[i], true);
        }

        for (var j = 0; j < this.polylines.length; j++) {
            this.addPolyline( this.polylines[j], true);
        }
    }
    else {

        //sync the view
        this.setCenterAndZoom(center,zoom);

    //TODO synchronize the markers and polylines too
    // (any overlays created after api instantiation are not sync'd)
    }

    this.addControls(this.addControlsArgs);

};

/**
 *
 * @param {Object} element
 * @param {String} api
 */
Mapstraction.prototype.addAPI = function(element,api) {
    this.loaded[api] = false;
    this.onload[api] = [];
    var me = this;

    switch (api) {
        case 'yahoo':
            if (YMap) {
                this.maps[api] = new YMap(element);

                YEvent.Capture(this.maps[api], EventsList.MouseClick, function(event,location) {
                    me.clickHandler(location.Lat, location.Lon, location, me);
                });
                YEvent.Capture(this.maps[api], EventsList.changeZoom, function() {
                    me.moveendHandler(me);
                });
                YEvent.Capture(this.maps[api], EventsList.endPan, function() {
                    me.moveendHandler(me);
                });
                this.loaded[api] = true;
            }
            else {
                alert(api + ' map script not imported');
            }
            break;
        case 'google':
            if (GMap2) {
                if (GBrowserIsCompatible()) {
                    this.maps[api] = new GMap2(element);

                    GEvent.addListener(this.maps[api], 'click', function(marker,location) {
                        // If the user puts their own Google markers directly on the map
                        // then there is no location and this event should not fire.
                        if ( location ) {
                            me.clickHandler(location.y,location.x,location,me);
                        }
                    });

                    GEvent.addListener(this.maps[api], 'moveend', function() {
                        me.moveendHandler(me);
                    });
                    this.loaded[api] = true;
                }
                else {
                    alert('browser not compatible with Google Maps');
                }
            }
            else {
                alert(api + ' map script not imported');
            }
            break;
        case 'microsoft':
            if (VEMap) {

                element.style.position='relative';

                var msft_width = parseFloat(getStyle($m(element),'width'));
                var msft_height = parseFloat(getStyle($m(element),'height'));
                /* Hack so the VE works with FF2 */
                var ffv = 0;
                var ffn = "Firefox/";
                var ffp = navigator.userAgent.indexOf(ffn);
                if (ffp != -1) {
                    ffv = parseFloat(navigator.userAgent.substring(ffp+ffn.length));
                }
                if (ffv >= 1.5) {
                    Msn.Drawing.Graphic.CreateGraphic = function(f,b) {
                        return new Msn.Drawing.SVGGraphic(f, b);
                    };
                }

                this.maps[api] = new VEMap(element.id);
                this.maps[api].LoadMap();

                this.maps[api].AttachEvent("onclick", function(e) {
                    me.clickHandler(e.view.LatLong.Latitude, e.view.LatLong.Longitude, me);
                });
                this.maps[api].AttachEvent("onchangeview", function(e) {
                    me.moveendHandler(me);
                });

                //Source of our trouble with Mapufacture?
                this.resizeTo(msft_width, msft_height);
                this.loaded[api] = true;
            }
            else {
                alert(api + ' map script not imported');
            }
            break;
        case 'openlayers':

            this.maps[api] = new OpenLayers.Map(
                element.id,
                {
                    maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
                    maxResolution:156543,
                    numZoomLevels:18,
                    units:'meters',
                    projection: "EPSG:41001"
                }
                );

            this.layers['osmmapnik'] = new OpenLayers.Layer.TMS(
                'OSM Mapnik',
                [
                "http://a.tile.openstreetmap.org/",
                "http://b.tile.openstreetmap.org/",
                "http://c.tile.openstreetmap.org/"
                ],
                {
                    type:'png',
                    getURL: function (bounds) {
                        var res = this.map.getResolution();
                        var x = Math.round ((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
                        var y = Math.round ((this.maxExtent.top - bounds.top) / (res * this.tileSize.h));
                        var z = this.map.getZoom();
                        var limit = Math.pow(2, z);
                        if (y < 0 || y >= limit) {
                            return null;
                        } else {
                            x = ((x % limit) + limit) % limit;
                            var path = z + "/" + x + "/" + y + "." + this.type;
                            var url = this.url;
                            if (url instanceof Array) {
                                url = this.selectUrl(path, url);
                            }
                            return url + path;
                        }
                    },
                    displayOutsideMaxExtent: true
                }
                );

            this.layers['osm'] = new OpenLayers.Layer.TMS(
                'OSM',
                [
                "http://a.tah.openstreetmap.org/Tiles/tile.php/",
                "http://b.tah.openstreetmap.org/Tiles/tile.php/",
                "http://c.tah.openstreetmap.org/Tiles/tile.php/"
                ],
                {
                    type:'png',
                    getURL: function (bounds) {
                        var res = this.map.getResolution();
                        var x = Math.round ((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
                        var y = Math.round ((this.maxExtent.top - bounds.top) / (res * this.tileSize.h));
                        var z = this.map.getZoom();
                        var limit = Math.pow(2, z);
                        if (y < 0 || y >= limit) {
                            return null;
                        } else {
                            x = ((x % limit) + limit) % limit;
                            var path = z + "/" + x + "/" + y + "." + this.type;
                            var url = this.url;
                            if (url instanceof Array) {
                                url = this.selectUrl(path, url);
                            }
                            return url + path;
                        }
                    },
                    displayOutsideMaxExtent: true
                }
                );

            this.maps[api].addLayer(this.layers['osmmapnik']);
            this.maps[api].addLayer(this.layers['osm']);
            this.loaded[api] = true;
            break;
        case 'openstreetmap':
            // for now, osm is a hack on top of google
            if (GMap2) {
                if (GBrowserIsCompatible()) {
                    this.maps[api] = new GMap2(element);

                    GEvent.addListener(this.maps[api], 'click', function(marker,location) {
                        // If the user puts their own Google markers directly on the map
                        // then there is no location and this event should not fire.
                        if ( location ) {
                            me.clickHandler(location.y,location.x,location,me);
                        }
                    });

                    GEvent.addListener(this.maps[api], 'moveend', function() {
                        me.moveendHandler(me);
                    });

                    // Add OSM tiles

                    var copyright = new GCopyright(1, new GLatLngBounds(new GLatLng(-90,-180), new GLatLng(90,180)), 0, "copyleft");
                    var copyrightCollection = new GCopyrightCollection('OSM');
                    copyrightCollection.addCopyright(copyright);

                    var tilelayers = [];
                    tilelayers[0] = new GTileLayer(copyrightCollection, 1, 18);
                    tilelayers[0].getTileUrl = function (a, b) {
                        return "http://tile.openstreetmap.org/"+b+"/"+a.x+"/"+a.y+".png";
                    };
                    tilelayers[0].isPng = function() {
                        return true;
                    };
                    tilelayers[0].getOpacity = function() {
                        return 1.0;
                    };

                    var custommap = new GMapType(tilelayers, new GMercatorProjection(19), "OSM", {
                        errorMessage:"More OSM coming soon"
                    });
                    this.maps[api].addMapType(custommap);

                    // Have to tell Mapstraction that we're good so the
                    // setCenterAndZoom call below initializes the map
                    this.loaded[api] = true;

                    var myPoint = new LatLonPoint(50.6805,-1.4062505);
                    this.setCenterAndZoom(myPoint, 11);

                    this.maps[api].setMapType(custommap);
                }
                else {
                    alert('browser not compatible with Google Maps');
                }
            }
            else {
                alert(api + ' map script not imported');
            }

            break;
        case 'multimap':

            if (MultimapViewer) {

                if(this.debug){
                    // multimap calls this print_debug function to output debug info
                    window.print_debug = function(strMessage){
                        var dbg = document.getElementById('debug');
                        if(dbg){
                            dbg.innerHTML += '<p>MUlTIMAP: ' + strMessage + '</p>';
                        }
                        else {
                            alert(strMessage);
                        }
                    };
                }

                this.maps[api] = new MultimapViewer(element);

                this.maps[api].addEventHandler('click', function(eventType, eventTarget, arg1, arg2, arg3){
                    if (arg1) {
                        me.clickHandler(arg1.lat, arg1.lon, me);
                    }
                });
                this.maps[api].addEventHandler('changeZoom', function(eventType, eventTarget, arg1, arg2, arg3){
                    me.moveendHandler(me);
                });
                this.maps[api].addEventHandler('endPan', function(eventType, eventTarget, arg1, arg2, arg3){
                    me.moveendHandler(me);
                });
                this.loaded[api] = true;

            }
            else {
                alert(api + ' map script not imported');
            }

            break;
        case 'map24':
            // Copied from Google and modified
            if (Map24) {

                Map24.loadApi(["core_api","wrapper_api"] , function() {

                    Map24.MapApplication.init
                    ( {
                        NodeName: element.id,
                        MapType: "Static"
                    } );
                    me.maps[api] = Map24.MapApplication.Map;

                    Map24.MapApplication.Map.addListener('Map24.Event.MapClick',
                        function(e) {
                            me.clickHandler(e.Coordinate.Latitude/60,
                                e.Coordinate.Longitude/60,
                                me);

                            e.stop();
                        }
                        );

                    Map24.MapApplication.Map.addListener("MapPanStop",
                        function(e) {
                            me.moveendHandler(me);
                        }
                        );

                    /**/

                    var client=Map24.MapApplication.Map.MapClient['Static'];


                    /*

							 These *will* cause the specified listener to run when we stop
							 panning the map, but the default pan stop handler will be
							 cancelled. The result of this will be that when we have stopped
							 panning, we will permanently be in 'pan' mode and unable to do
							 anything else (e.g. click on the map to create a new marker).


							 var defaultOnPanStop = client.onPanStop;
							 var defaultOnZoomInStop = client.onZoomInStop;
							 var defaultOnZoomOutStop = client.onZoomOutStop;

							 client.onPanStop = function(e)
							 { me.moveendHandler(me); defaultOnPanStop(e);
							 status('DEFAULTONPANSTOP DONE');}

						// Handle zoom events - these also fire moveendHandler for the
						// other APIs in Mapstraction
						client.onZoomInStop = function(e)
						{ me.moveendHandler(me); defaultOnZoomInStop(e); }
						client.onZoomOutStop = function(e)
						{ me.moveendHandler(me); defaultOnZoomOutStop(e);  }

						 */

                    me.loaded[api] = true;
                    for (var i = 0; i < me.onload[api].length; i++) {
                        me.onload[api][i]();
                    }
                }, "2.0.1247" );

            } else {
                alert(api + ' api not loaded');
            }
            break;
        case 'mapquest':
            if (MQA.TileMap) {
                this.maps[api] = new MQA.TileMap(element);
                this.loaded[api] = true;
                MQA.EventManager.addListener(this.maps[api],"click",function(eventType, eventTarget, arg1, arg2, arg3){
                    if (arg1) {
                        me.clickHandler(arg1.lat, arg1.lon, me);
                    }
                });
                MQA.EventManager.addListener(this.maps[api],"zoomend",function() {
                    me.moveendHandler(me)
                });
                MQA.EventManager.addListener(this.maps[api],"moveend",function() {
                    me.moveendHandler(me)
                });
            }
            else {
                alert(api + ' map script not imported');
            }
            break;
        case 'freeearth':
            this.maps[api] = new FE.Map($m(element));
            this.maps[api].onLoad = function() {
                me.freeEarthLoaded = true;
                me.loaded[api] = true;
                for (var i = 0; i < me.onload[api].length; i++) {
                    me.onload[api][i]();
                }
            };
            this.maps[api].load();
            break;
        case 'openspace':
            // create the map with no controls and don't centre popup info window
            this.maps[api] = new OpenSpace.Map(element,{
                controls: [],
                centreInfoWindow: false
            });
            // note that these three controls are always there and the fact that there
            // are three resident controls is used in addControls()
            // enable map drag with mouse and keyboard
            this.maps[api].addControl(new OpenLayers.Control.Navigation());
            this.maps[api].addControl(new OpenLayers.Control.KeyboardDefaults());
            // include copyright statement
            this.maps[api].addControl(new OpenSpace.Control.CopyrightCollection());

            this.maps[api].events.register("click", this.maps[api], function(evt) {
                var point = this.getLonLatFromViewPortPx( evt.xy );
                // convert to LatLonPoint
                var llPoint = new LatLonPoint;
                llPoint.fromOpenSpace(point);
                me.clickHandler( llPoint.lat, llPoint.lon );
                return false;
            });
            this.loaded[api] = true;
            break;
        case 'viamichelin':
            if (VMMap) {
                this.maps[api] = new VMMap(element);
                this.maps[api].addEventHandler('onClick', function(eventType, eventTarget, arg1, arg2, arg3){
                    if (arg1) {
                        me.clickHandler(arg1.lat, arg1.lon, me);
                    }
                });
                this.maps[api].addEventHandler('onZoomIn', function(eventType, eventTarget, arg1, arg2, arg3){
                    me.moveendHandler(me);
                });
                this.maps[api].addEventHandler('onZoomOut', function(eventType, eventTarget, arg1, arg2, arg3){
                    me.moveendHandler(me);
                });
                this.maps[api].addEventHandler('onStopPan', function(eventType, eventTarget, arg1, arg2, arg3){
                    me.moveendHandler(me);
                });
                this.loaded[api] = true;
            }
            else {
                alert(api + ' map script not imported');
            }
            break;
        default:
            if(this.debug) {
                alert(api + ' not supported by mapstraction');
            }
    }


// this.resizeTo(getStyle($m(element),'width'), getStyle($m(element),'height'));
// the above line was called on all APIs but MSFT alters with the div size when it loads
// so you have to find the dimensions and set them again (see msft constructor).
// FIXME: test if google/yahoo etc need this resize called. Also - getStyle returns
// CSS size ('200px') not an integer, and resizeTo seems to expect ints

};

Mapstraction._getScriptLocation = function() {
    var scriptLocation = '';
    var SCRIPT_NAME = 'mapstraction.js';
    var scripts = document.getElementsByTagName('script');
    for(var i=0; i<scripts.length; i++) {
        var src = scripts[i].getAttribute('src');
        if(src) {
            var index = src.lastIndexOf(SCRIPT_NAME);
            if((index > -1) && (index + SCRIPT_NAME.length == src.length)) {
                scriptLocation=src.slice(0, -SCRIPT_NAME.length);
                break;
            }
        }
    }
    return scriptLocation;
};

Mapstraction.writeInclude = function(api, key, version) {
    var jsfiles = [];
    var allScriptTags = '';
    var host = Mapstraction._getScriptLocation() + 'lib/';
    switch(api) {
        case 'google':
            if(version === null) {
                version = '2';
            }
            jsfiles.push('http://maps.google.com/maps?file=api&v=' + version + '&key=' + key);
            break;
        case 'microsoft':
            if(version === null) {
                version = 'v3';
            }
            jsfiles.push('http://dev.virtualearth.net/mapcontrol/' + version + '/mapcontrol.js');
            break;
        case 'yahoo':
            if(version === null) {
                version = '3.8';
            }
            jsfiles.push('http://api.maps.yahoo.com/ajaxymap?v='+ version + '&appid=' + key);
            break;
        case 'openlayers':
            jsfiles.push('http://openlayers.org/api/OpenLayers.js');
            break;
        case 'multimap':
            if(version === null) {
                version = '1.2';
            }
            jsfiles.push('http://developer.multimap.com/API/maps/' + version + '/' + key);
            break;
        case 'map24':
            jsfiles.push('http://api.maptp.map24.com/ajax?appkey=' + key);
            break;
        case 'mapquest':
            // Many changes between 5.2 and 5.3
            // http://developer.mapquest.com/content/documentation/ApiDocumentation/53/JavaScript/JS_DeveloperGuide_v5.3.0.1.htm
            if(version === null) {
                version = "5.3";
            }
            jsfiles.push('http://btilelog.access.mapquest.com/tilelog/transaction?transaction=script&key=' + key + '&ipr=true&itk=true&ipkg=controls1&v=' + version);
            jsfiles.push('mapquest-js/mqcommon.js');
            jsfiles.push('mapquest-js/mqutils.js');
            jsfiles.push('mapquest-js/mqobjects.js');
            jsfiles.push('mapquest-js/mqexec.js');
            break;
        case 'freeearth':
            jsfiles.push('http://freeearth.poly9.com/api.js');
            break;
        case 'openspace':
            jsfiles.push('http://openspace.ordnancesurvey.co.uk/osmapapi/openspace.js?key=' + key);
            jsfiles.push('mapstraction-js/mapstraction-openspace.js');
            break;
        case 'viamichelin':
            jsfiles.push('http://api.viamichelin.com/apijs/js/api.js');
            //document.write('VMAPI.registerKey("' + key + '")'); // FIXME
            break;
    }

    for(var i=0; i<jsfiles.length; i++) {
        if(/MSIE/.test(navigator.userAgent) || /Safari/.test(navigator.userAgent)) {
            // var currentScriptTag="<script src='"+host+jsfiles[i]+"'></script>";
            var currentScriptTag = jsfiles[i];
            allScriptTags += currentScriptTag;
        }
        else {
            var s = document.createElement('script');
            s.src = jsfiles[i];
            s.type = 'text/javascript';
            var h = document.getElementsByTagName('head').length ? document.getElementsByTagName('head')[0] : document.body;
            h.appendChild(s);
        }
    }
    if(allScriptTags) {
        document.write(allScriptTags);
    }

};

/**
 * Returns the loaded state of a Map Provider
 * @param {String} api Optional API to query for. If not specified, returns state of the originally created API
 * @type {Boolean} The state of the map loading
 */
Mapstraction.prototype.isLoaded = function(api){
    if (api === null) {
        api = this.api;
    }
    return this.loaded[api];
};

/**
 * Set the debugging on or off - shows alert panels for functions that don't exist in Mapstraction
 * @param {Boolean} debug true to turn on debugging, false to turn it off
 * @type {Boolean} The state of debugging
 */
Mapstraction.prototype.setDebug = function(debug){
    if(debug !== null) {
        this.debug = debug;
    }
    return this.debug;
};


/**
 * Resize the current map to the specified width and height
 * (since it is actually on a child div of the mapElement passed
 * as argument to the Mapstraction constructor, the resizing of this
 * mapElement may have no effect on the size of the actual map)
 * @param {Integer} width The width the map should be.
 * @param {Integer} height The width the map should be.
 */
Mapstraction.prototype.resizeTo = function(width,height){
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.resizeTo(width,height);
        } );
        return;
    }

    switch (this.api) {
        case 'yahoo':
            this.maps[this.api].resizeTo(new YSize(width,height));
            break;
        case 'google':
        case 'openstreetmap':
            this.currentElement.style.width = width;
            this.currentElement.style.height = height;
            this.maps[this.api].checkResize();
            break;
        case 'openspace' :
            this.currentElement.style.width = width;
            this.currentElement.style.height = height;
            this.maps[this.api].updateSize();
            break;
        case 'openlayers':
            this.currentElement.style.width = width;
            this.currentElement.style.height = height;
            this.maps[this.api].updateSize();
            break;
        case 'microsoft':
            this.maps[this.api].Resize(width, height);
            break;
        case 'multimap':
            this.currentElement.style.width = width;
            this.currentElement.style.height = height;
            this.maps[this.api].resize();
            break;
        case 'mapquest':
            this.currentElement.style.width = width;
            this.currentElement.style.height = height;
            this.maps[this.api].setSize(new MQA.Size(width, height));
            break;
        case 'map24':
            Map24.MapApplication.Map.Canvas['c'].resizeTo(width,height);
            break;
        case 'viamichelin':
            this.maps[this.api].resizeTo(width, height);
            break;
    }
};

/////////////////////////
//
// Event Handling
//
// FIXME need to consolidate some of these handlers...
//
///////////////////////////

// Click handler attached to native API
Mapstraction.prototype.clickHandler = function(lat, lon, me) {
    this.callEventListeners('click', {
        location: new LatLonPoint(lat, lon)
    });
};

// Move and zoom handler attached to native API
Mapstraction.prototype.moveendHandler = function(me) {
    this.callEventListeners('moveend', {});
};

/**
 * Add a listener for an event.
 * @param {String} type Event type to attach listener to
 * @param {Function} func Callback function
 * @param {Object} caller Callback object
 */
Mapstraction.prototype.addEventListener = function() {
    var listener = {};
    listener.event_type = arguments[0];
    listener.callback_function = arguments[1];

    // added the calling object so we can retain scope of callback function
    if(arguments.length == 3) {
        listener.back_compat_mode = false;
        listener.callback_object = arguments[2];
    }
    else {
        listener.back_compat_mode = true;
        listener.callback_object = null;
    }
    this.eventListeners.push(listener);
};

/**
 * Call listeners for a particular event.
 * @param {String} sEventType Call listeners of this event type
 * @param {Object} oEventArgs Event args object to pass back to the callback
 */
Mapstraction.prototype.callEventListeners = function(sEventType, oEventArgs) {
    oEventArgs.source = this;
    for(var i = 0; i < this.eventListeners.length; i++) {
        var evLi = this.eventListeners[i];
        if(evLi.event_type == sEventType) {
            // only two cases for this, click and move
            if(evLi.back_compat_mode) {
                if(evLi.event_type == 'click') {
                    evLi.callback_function(oEventArgs.location);
                }
                else {
                    evLi.callback_function();
                }
            }
            else {
                var scope = evLi.callback_object || this;
                evLi.callback_function.call(scope, oEventArgs);
            }
        }
    }
};

/**
 * Ties a callback function to a map event
 * Currently only implemented for google maps
 * @param {String} event
 * @param {Function} callback
 * @returns {Object} handler
 */
Mapstraction.prototype.addMapListener = function(event, callback)
{
	if(this.loaded[this.api] == false)
	{
		myself = this;
		this.onload[this.api].push(function()
		{
			myself.addMapListener(event, callback);
		});
		return;
	}

	var map = this.maps[this.api];

	switch (this.api)
	{
		case 'google':
			return GEvent.addListener(map, event, callback);
			break;
		case 'yahoo':
		case 'openstreetmap':
		case 'microsoft':
		case 'openlayers':
		case 'multimap':
		case 'mapquest':
		case 'map24':
			alert(this.api + ' not supported by Mapstraction.addEvent');
			break;
	}
};

/**
 * Removes an event handler from the map
 * Currently only implemented for google maps
 * @param {Object} handler
 */
Mapstraction.prototype.removeMapListener = function(handler)
{
	if(this.loaded[this.api] == false)
	{
		myself = this;
		this.onload[this.api].push(function()
		{
			myself.removeMapListener(handler);
		});
		return;
	}

	var map = this.maps[this.api];

	switch (this.api)
	{
		case 'google':
			GEvent.removeListener(handler);
			break;
		case 'yahoo':
		case 'openstreetmap':
		case 'microsoft':
		case 'openlayers':
		case 'multimap':
		case 'mapquest':
		case 'map24':
			alert(this.api + ' not supported by Mapstraction.removeEvent');
			break;
	}
};

////////////////////
//
// map manipulation
//
/////////////////////


/**
 * addControls adds controls to the map. You specify which controls to add in
 * the associative array that is the only argument.
 * addControls can be called multiple time, with different args, to dynamically change controls.
 *
 * args = {
 *     pan:      true,
 *     zoom:     'large' || 'small',
 *     overview: true,
 *     scale:    true,
 *     map_type: true,
 * }
 *
 * @param {array} args Which controls to switch on
 */
Mapstraction.prototype.addControls = function( args ) {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.addControls(args);
        } );
        return;
    }

    var map = this.maps[this.api];

    this.addControlsArgs = args;

    switch (this.api) {

        case 'google':
        case 'openstreetmap':
            //remove old controls
            if (this.controls) {
                while ((ctl = this.controls.pop())) {
                    map.removeControl(ctl);
                }
            }
            else {
                this.controls = [];
            }
            c = this.controls;

            // Google has a combined zoom and pan control.
            if (args.zoom || args.pan) {
                if (args.zoom == 'large') {
                    c.unshift(new GLargeMapControl());
                    map.addControl(c[0]);
                } else {
                    c.unshift(new GSmallMapControl());
                    map.addControl(c[0]);
                }
            }
            if (args.scale) {
                c.unshift(new GScaleControl()); map.addControl(c[0]);
            }

            if (this.api != "openstreetmap") {
                if (args.overview) {
                    c.unshift(new GOverviewMapControl()); map.addControl(c[0]);
                }
                if (args.map_type) {
                    c.unshift(new GMapTypeControl()); map.addControl(c[0]);
                }
            }
            break;

        case 'yahoo':
            if (args.pan) {
                map.addPanControl();
            }
            else {
                map.removePanControl();
            }
            if (args.zoom == 'large') {
                map.addZoomLong();
            }
            else if ( args.zoom == 'small' ) {
                map.addZoomShort();
            }
            else {
                map.removeZoomScale();
            }
            break;

        case 'openlayers':
            // FIXME: OpenLayers has a bug removing all the controls says crschmidt
            for (var i = map.controls.length; i>1; i--) {
                map.controls[i-1].deactivate();
                map.removeControl(map.controls[i-1]);
            }
            // FIXME - can pan & zoom be separate?
            if ( args.pan             )      {
                map.addControl(new OpenLayers.Control.PanZoomBar());
            }
            else {  }
            if ( args.zoom == 'large' )      {
                map.addControl(new OpenLayers.Control.PanZoomBar());
            }
            else if ( args.zoom == 'small' ) {
                map.addControl(new OpenLayers.Control.ZoomBox());
            }
            else {
                map.addControl(new OpenLayers.Control.ZoomBox());
            }
            if ( args.overview ) {
                map.addControl(new OpenLayers.Control.OverviewMap());
            }
            if ( args.map_type ) {
                map.addControl(new OpenLayers.Control.LayerSwitcher());
            }
            break;

        case 'openspace':
            // remove existing controls but leave the basic navigation, keyboard and copyright controls in place
            // these were added in addAPI and not normally be removed
            for (var i = map.controls.length; i>3; i--) {
                map.controls[i-1].deactivate();
                map.removeControl(map.controls[i-1]);
            }
            // pan and zoom controls not available separately
            if ( args.zoom == 'large') {
                map.addControl(new OpenSpace.Control.LargeMapControl());
            }
            else if ( args.zoom == 'small' || args.pan ) {
                map.addControl(new OpenSpace.Control.SmallMapControl());
            }
            if ( args.overview ) {
                // this should work but as of OpenSpace 0.7.2 generates an error unless done before setCenterAndZoom
                var osOverviewControl = new OpenSpace.Control.OverviewMap();
                map.addControl(osOverviewControl);
                osOverviewControl.maximizeControl();
            }
            if ( args.map_type ) {
                // this is all you get with openspace, a control to switch on or off the layers and markers
                // probably not much use to anybody
                map.addControl(new OpenLayers.Control.LayerSwitcher());
            }
            break;

        case 'multimap':
            //FIXME -- removeAllWidgets();  -- can't call addControls repeatedly

            pan_zoom_widget = 'MM';
            if (args.zoom && args.zoom == "small") {
                pan_zoom_widget = pan_zoom_widget + "Small";
            }
            if (args.pan) {
                pan_zoom_widget = pan_zoom_widget + "Pan";
            }
            if (args.zoom) {
                pan_zoom_widget = pan_zoom_widget + "Zoom";
            }
            pan_zoom_widget = pan_zoom_widget + "Widget";

            if (pan_zoom_widget != "MMWidget") {
                eval(' map.addWidget( new ' + pan_zoom_widget + '() );');
            }

            if ( args.map_type ) {
                map.addWidget( new MMMapTypeWidget() );
            }
            if ( args.overview ) {
                map.addWidget( new MMOverviewWidget() );
            }
            break;

        case 'mapquest':
            //remove old controls
            if (this.controls) {
                while ( (ctl = this.controls.pop()) ) {
                    map.removeControl(ctl);
                }
            }
            else {
                this.controls = [];
            }
            c = this.controls;
            if ( args.pan ) {
                c.unshift(new MQA.PanControl());
                map.addControl(c[0], new MQA.MapCornerPlacement(MQA.MapCorner.TOP_LEFT, new MQA.Size(0,0)));
            }
            if ( args.zoom == 'large' ) {
                c.unshift(new MQA.LargeZoomControl());
                map.addControl(c[0], new MQA.MapCornerPlacement(MQA.MapCorner.TOP_LEFT, new MQA.Size(0,0)));
            }
            else if ( args.zoom == 'small' ) {
                c.unshift(new MQA.ZoomControl());
                map.addControl(c[0], new MQA.MapCornerPlacement(MQA.MapCorner.BOTTOM_LEFT, new MQA.Size(0,0)));
            }
            // TODO: Map View Control is wonky
            if ( args.map_type ) {
                c.unshift(new MQA.ViewControl());
                map.addControl(c[0], new MQA.MapCornerPlacement(MQA.MapCorner.TOP_RIGHT, new MQA.Size(0,0)));
            }
            break;

        case 'viamichelin':
            if (args.zoom == 'large') {
                map.activateZoom(true);
                map.showMapTools();
            }
            else if ( args.zoom == 'small' ) {
                map.activateMiniZoom(true);
                map.showMapTools();
            }
            else {
                map.hideMapTools();
            }
            break;
    }
};


/**
 * addSmallControls adds a small map panning control and zoom buttons to the map
 * Supported by: yahoo, google, openstreetmap, openlayers, multimap, mapquest, openspace
 */
Mapstraction.prototype.addSmallControls = function() {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.addSmallControls();
        } );
        return;
    }

    var map = this.maps[this.api];

    switch (this.api) {
        case 'yahoo':
            map.addPanControl();
            map.addZoomShort();
            this.addControlsArgs.pan = true;
            this.addControlsArgs.zoom = 'small';
            break;
        case 'google':
        case 'openstreetmap':
            map.addControl(new GSmallMapControl());
            this.addControlsArgs.zoom = 'small';
            break;
        case 'openlayers':
            map.addControl(new OpenLayers.Control.ZoomBox());
            map.addControl(new OpenLayers.Control.LayerSwitcher({
                'ascending':false
            }));
            break;
        case 'multimap':
            smallPanzoomWidget = new MMSmallPanZoomWidget();
            map.addWidget( smallPanzoomWidget );
            this.addControlsArgs.pan = true;
            this.addControlsArgs.zoom = 'small';
            break;
        case 'mapquest':
            map.addControl(new MQA.ZoomControl(map));
            map.addControl(new MQA.PanControl(map));
            this.addControlsArgs.pan = true;
            this.addControlsArgs.zoom = 'small';
            break;
        case 'openspace':
            map.addControl(new OpenSpace.Control.SmallMapControl());
            break;
        case 'viamichelin':
            map.activateMiniZoom(true);
            this.addControlsArgs.zoom = 'small';
            map.showMapTools();
            break;
    }
};

/**
 * addLargeControls adds a large map panning control and zoom buttons to the map
 * Supported by: yahoo, google, openstreetmap, multimap, mapquest, openspace
 */
Mapstraction.prototype.addLargeControls = function() {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.addLargeControls();
        } );
        return;
    }

    var map = this.maps[this.api];

    switch (this.api) {
        case 'yahoo':
            map.addPanControl();
            map.addZoomLong();
            this.addControlsArgs.pan = true;  // keep the controls in case of swap
            this.addControlsArgs.zoom = 'large';
            break;
        case 'openlayers':
            map.addControl(new OpenLayers.Control.PanZoomBar());
            break;
        case 'google':
            map.addControl(new GMapTypeControl());
            map.addControl(new GOverviewMapControl()) ;
            this.addControlsArgs.overview = true;
            this.addControlsArgs.map_type = true;
        // no break statement here intentionally
        case 'openstreetmap':
            map.addControl(new GLargeMapControl());
            map.addControl(new GScaleControl()) ;
            this.addControlsArgs.pan = true;
            this.addControlsArgs.zoom = 'large';
            this.addControlsArgs.scale = true;
            break;
        case 'multimap':
            panzoomWidget = new MMPanZoomWidget();
            map.addWidget( panzoomWidget );
            this.addControlsArgs.pan = true;  // keep the controls in case of swap
            this.addControlsArgs.zoom = 'large';
            break;
        case 'mapquest':
            map.addControl(new MQA.LargeZoomControl(map));
            map.addControl(new MQA.PanControl(map));
            map.addControl(new MQA.ViewControl(map));
            this.addControlsArgs.pan = true;
            this.addControlsArgs.zoom = 'large';
            this.addControlsArgs.map_type = true;
            break;
        case 'openspace':
            map.addControl(new OpenSpace.Control.LargeMapControl());
            break;
        case 'viamichelin':
            map.activateZoom(true);
            this.addControlsArgs.zoom = 'large';
            map.showMapTools();
            break;
    }
};

/**
 * addMapTypeControls adds a map type control to the map (streets, aerial imagery etc)
 * Supported by: yahoo, google, openstreetmap, multimap, mapquest
 */
Mapstraction.prototype.addMapTypeControls = function() {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.addMapTypeControls();
        } );
        return;
    }

    var map = this.maps[this.api];

    switch (this.api) {
        case 'yahoo':
            map.addTypeControl();
            break;
        case 'google':
        case 'openstreetmap':
            map.addControl(new GMapTypeControl());
            break;
        case 'multimap':
            map.addWidget( new MMMapTypeWidget() );
            break;
        case 'mapquest':
            map.addControl(new MQA.ViewControl(map));
            break;
        case 'openlayers':
            map.addControl( new OpenLayers.Control.LayerSwitcher({
                'ascending':false
            }) );
            break;
        case 'viamichelin':
            map.activateSatelliteHybrid(true);
            break;
    }
};

/**
 * Enable/disable dragging of the map
 * Supported by: yahoo, google, openstreetmap, multimap, openspace
 * @param {Boolean} on
 */
Mapstraction.prototype.dragging = function(on) {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.dragging(on);
        } );
        return;
    }

    var map = this.maps[this.api];

    switch (this.api) {
        case 'openspace' :
            // first find the navigation control
            for (var i = 0; i<map.controls.length; i++) {
                if (map.controls[i].displayClass == "olControlNavigation") {
                    // this is it
                    if (on) {
                        map.controls[i].activate();
                    } else {
                        map.controls[i].deactivate();
                    }
                    break;
                }
            }
            break;
        case 'google':
        case 'openstreetmap':
            if (on) {
                map.enableDragging();
            } else {
                map.disableDragging();
            }
            break;
        case 'yahoo':
            if (on) {
                map.enableDragMap();
            } else {
                map.disableDragMap();
            }
            break;
        case 'multimap':
            if (on) {
                map.setOption("drag","dragmap");
            } else {
                map.setOption("drag","");
            }
            break;
        case 'mapquest':
            map.enableDragging(on);
            break;
        case 'viamichelin':
            if (on) {
                map.setMapModeNav(1);
            } else {
                map.setMapModeNav(0);
            }
            break;
    }
};

/**
 * Centers the map to some place and zoom level
 * @param {LatLonPoint} point Where the center of the map should be
 * @param {Integer} zoom The zoom level where 0 is all the way out.
 */
Mapstraction.prototype.setCenterAndZoom = function(point, zoom) {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.setCenterAndZoom(point, zoom);
        } );
        return;
    }
    var map = this.maps[this.api];

    switch (this.api) {
        case 'yahoo':
            var yzoom = 18 - zoom; // maybe?
            map.drawZoomAndCenter(point.toYahoo(),yzoom);
            break;
        case 'google':
        case 'openstreetmap':
            map.setCenter(point.toGoogle(), zoom);
            break;
        case 'microsoft':
            map.SetCenterAndZoom(point.toMicrosoft(),zoom);
            break;
        case 'openlayers':
            map.setCenter(point.toOpenLayers(), zoom);
            break;
        case 'multimap':
            map.goToPosition( new MMLatLon( point.lat, point.lng ), zoom );
            break;
        case 'map24':
            var newSettings = {};
            newSettings.Latitude = point.lat*60;
            newSettings.Longitude = point.lon*60;
            var client = map.MapClient['Static'];
            var dLon = getDegreesFromGoogleZoomLevel(client.getCanvasSize().Width, zoom);
            newSettings.MinimumWidth = lonToMetres(dLon, point.lat);
            Map24.MapApplication.center(newSettings);
            break;
        case 'mapquest':
            // MapQuest's zoom levels appear to be off by '3' from the other providers for the same bbox
            map.setCenter(new MQLatLng( point.lat, point.lng ), zoom - 3 );
            break;
        case 'freeearth':
            if (this.freeEarthLoaded) {
                map.setTargetLatLng( point.toFreeEarth() );
            }
            else {
                var me = this;
                this.freeEarthOnLoad.push( function() {
                    me.setCenterAndZoom(point);
                } );
            }
            break;
        case 'openspace':
            // adjust zoom from google to openspace equivalent
            var oszoom = zoom-6;
            if (oszoom<0) {
                oszoom = 0;
            }
            else if (oszoom>10) {
                oszoom = 10;
            }
            map.setCenter(point.toOpenSpace(), oszoom);
            break;
        case 'viamichelin':
            // [0-19] => [0-16]
            map.drawMap(new VMLonLat( point.lng, point.lat ), Math.floor(zoom / 19 * 16) );
            break;
        default:
            if (this.debug) {
                alert(this.api + ' not supported by Mapstraction.setCenterAndZoom');
            }
    }
};


/**
 * Adds a marker pin to the map
 * @param {Marker} marker The marker to add
 * @param {Boolean} old If true, doesn't add this marker to the markers array. Used by the "swap" method
 */
Mapstraction.prototype.addMarker = function(marker, old) {
    var map = this.maps[this.api];
    marker.mapstraction = this;
    marker.api = this.api;
    marker.location.api = this.api;
    marker.map = this.maps[this.api];

    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.addMarker(marker, old);
        } );
        return;
    }

    switch (this.api) {
        case 'yahoo':
            var ypin = marker.toYahoo();
            marker.setChild(ypin);
            map.addOverlay(ypin);
            if (!old) {
                this.markers.push(marker);
            }
            break;
        case 'google':
        case 'openstreetmap':
            var gpin = marker.toGoogle();
            marker.setChild(gpin);
            map.addOverlay(gpin);
            if (!old) {
                this.markers.push(marker);
            }
            break;
        case 'microsoft':
            var mpin = marker.toMicrosoft();
            marker.setChild(mpin); // FIXME: MSFT maps remove the pin by pinID so this isn't needed?
            map.AddPushpin(mpin);
            if (!old) {
                this.markers.push(marker);
            }
            break;
        case 'openlayers':
            //this.map.addPopup(new OpenLayers.Popup("chicken", new OpenLayers.LonLat(5,40), new OpenLayers.Size(200,200), "example popup"));
            if (!this.layers['markers']) {
                this.layers['markers'] = new OpenLayers.Layer.Markers('markers');
                map.addLayer(this.layers['markers']);
            }
            var olmarker = marker.toOpenLayers();
            marker.setChild(olmarker);
            this.layers['markers'].addMarker(olmarker);
            if (! old) {
                this.markers.push(marker);
            }
            break;
        case 'openspace' :
            if (!this.layers['markers']) {
                // get the default marker layer provided by OpenSpace
                this.layers['markers'] = map.getMarkerLayer();
            }
            var osmarker = marker.toOpenSpace();
            marker.setChild(osmarker);

            if(marker.infoBubble) {
                // show info window on click or hover
                if (marker.hover) {
                    osmarker.events.register('mouseover',{
                        marker:osmarker,
                        html:marker.infoBubble
                        },function(evt) {
                        this.marker.map.closeInfoWindow();
                        // this opens the window with a default size, there seems to be no way to make it automatically variable
                        this.marker.map.openInfoWindow(this.marker.icon,this.marker.lonlat,this.html/*, new OpenLayers.Size(200, 200)*/);
                        OpenLayers.Event.stop(evt);
                    });
                    osmarker.events.register('mouseout',{
                        marker:osmarker
                    },function(evt) {
                        this.marker.map.closeInfoWindow();
                        OpenLayers.Event.stop(evt);
                    });
                }
                else {
                    osmarker.events.register('mousedown',{
                        marker:osmarker,
                        html:marker.infoBubble
                        },function(evt) {
                        this.marker.map.closeInfoWindow();
                        // this opens the window with a default size, there seems to be no way to make it automatically variable
                        this.marker.map.openInfoWindow(this.marker.icon,this.marker.lonlat,this.html/*, new OpenLayers.Size(200, 200)*/);
                        OpenLayers.Event.stop(evt);
                    });
                }
            }
            this.layers['markers'].addMarker(osmarker);
            if (! old) {
                this.markers.push(marker);
            }
            break;
        case 'multimap':
            var mmpin = marker.toMultiMap();
            marker.setChild(mmpin);
            map.addOverlay(mmpin);
            if (!old) {
                this.markers.push(marker);
            }
            break;
        case 'map24':
            var m24pin = marker.toMap24();
            marker.setChild(m24pin);
            m24pin.commit();
            if (!old) {
                this.markers.push(marker);
            }
            break;
        case 'mapquest':
            var mqpin = marker.toMapQuest();
            marker.setChild(mqpin);
            map.addPoi(mqpin);
            if (!old) {
                this.markers.push(marker);
            }
            break;
        case 'freeearth':
            var fepin = marker.toFreeEarth();
            marker.setChild(fepin);
            map.addOverlay(fepin);
            if (!old) {
                this.markers.push(marker);
            }
            break;
        case 'viamichelin':
            var vmpin = marker.toViaMichelin();
            marker.setChild(vmpin);
            map.addLayer(vmpin);
            if (!old) {
                this.markers.push(marker);
            }
            break;
        default:
            if(this.debug) {
                alert(this.api + ' not supported by Mapstraction.addMarker');
            }
    }
};

/**
 * addMarkerWithData will addData to the marker, then add it to the map
 * @param {Marker} marker The marker to add
 * @param {Object} data A data has to add
 */
Mapstraction.prototype.addMarkerWithData = function(marker, data) {
    marker.addData(data);
    this.addMarker(marker);
};

/**
 * addPolylineWithData will addData to the polyline, then add it to the map
 * @param {Polyline} polyline The polyline to add
 * @param {Object} data A data has to add
 */
Mapstraction.prototype.addPolylineWithData = function(polyline, data) {
    polyline.addData(data);
    this.addPolyline(polyline);
};

/**
 * removeMarker removes a Marker from the map
 * @param {Marker} marker The marker to remove
 */
Mapstraction.prototype.removeMarker = function(marker) {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.removeMarker(marker);
        } );
        return;
    }

    var map = this.maps[this.api];

    var tmparray = [];
    while(this.markers.length > 0){
        current_marker = this.markers.pop();
        if(marker == current_marker) {
            switch (this.api) {
                case 'google':
                case 'openstreetmap':
                    map.removeOverlay(marker.proprietary_marker);
                    break;
                case 'yahoo':
                    map.removeOverlay(marker.proprietary_marker);
                    break;
                case 'microsoft':
                    map.DeletePushpin(marker.pinID);
                    break;
                case 'multimap':
                    map.removeOverlay(marker.proprietary_marker);
                    break;
                case 'mapquest':
                    map.removeShape(marker.proprietary_marker);
                    break;
                case 'map24':
                    marker.proprietary_marker.remove();
                    break;
                case 'openlayers':
                case 'openspace' :
                    this.layers['markers'].removeMarker(marker.proprietary_marker);
                    marker.proprietary_marker.destroy();
                    break;
                case 'viamichelin':
                    map.removeLayer(marker.proprietary_marker);
                    break;
            }
            marker.onmap = false;
            break;
        } else {
            tmparray.push(current_marker);
        }
    }
    this.markers = this.markers.concat(tmparray);
};

/**
 * removeAllMarkers removes all the Markers on a map
 */
Mapstraction.prototype.removeAllMarkers = function() {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.removeAllMarkers();
        } );
        return;
    }

    var map = this.maps[this.api];

    switch (this.api) {
        case 'yahoo':
            map.removeMarkersAll();
            break;
        case 'google':
        case 'openstreetmap':
            map.clearOverlays();
            break;
        case 'microsoft':
            map.DeleteAllPushpins();
            break;
        case 'multimap':
            map.removeAllOverlays();
            break;
        case 'mapquest':
            map.removeAllShapes();
            break;
        case 'map24':
            // don't think map24 has a specific method for this
            var current_marker;
            while(this.markers.length > 0) {
                current_marker = this.markers.pop();
                current_marker.proprietary_marker.remove();
            }
            break;
        case 'openlayers':
        case 'openspace':
            if (this.layers['markers']) this.layers['markers'].clearMarkers();
            break;
        case 'viamichelin':
            map.removeAllLayers();
            break;
        default:
            if(this.debug) {
                alert(this.api + ' not supported by Mapstraction.removeAllMarkers');
            }
    }

    this.markers = []; // clear the mapstraction list of markers too

};


/**
 * Declutter the markers on the map, group together overlapping markers.
 * @param {Object} opts Declutter options
 */
Mapstraction.prototype.declutterMarkers = function(opts) {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.declutterMarkers(opts);
        } );
        return;
    }

    var map = this.maps[this.api];

    switch(this.api)
    {
        //    case 'yahoo':
        //
        //      break;
        //    case 'google':
        //
        //      break;
        //    case 'openstreetmap':
        //
        //      break;
        //    case 'microsoft':
        //
        //      break;
        //    case 'openlayers':
        //
        //      break;
        case 'multimap':
            /*
			 * Multimap supports quite a lot of decluttering options such as whether
			 * to use an accurate of fast declutter algorithm and what icon to use to
			 * represent a cluster. Using all this would mean abstracting all the enums
			 * etc so we're only implementing the group name function at the moment.
			 */
            map.declutterGroup(opts.groupName);
            break;
        //    case 'mapquest':
        //
        //      break;
        //    case 'map24':
        //
        //      break;
        default:
            if(this.debug) {
                alert(this.api + ' not supported by Mapstraction.declutterMarkers');
            }
    }
};

/**
 * Add a polyline to the map
 * @param {Polyline} polyline The Polyline to add to the map
 * @param {Boolean} old If true replaces an existing Polyline
 */
Mapstraction.prototype.addPolyline = function(polyline, old) {

    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.addPolyline(polyline, old);
        } );
        return;
    }

    var map = this.maps[this.api];
    polyline.api = this.api;
    polyline.map = this.maps[this.api];
    switch (this.api) {
        case 'openspace':
            ospolyline = polyline.toOpenSpace();
            polyline.setChild(ospolyline);
            // add it to the built in vector layer
            map.getVectorLayer().addFeatures([ospolyline]);
            if(!old) {
                this.polylines.push(polyline);
            }
            break;
        case 'yahoo':
            ypolyline = polyline.toYahoo();
            polyline.setChild(ypolyline);
            map.addOverlay(ypolyline);
            if(!old) {
                this.polylines.push(polyline);
            }
            break;
        case 'google':
        case 'openstreetmap':
            gpolyline = polyline.toGoogle();
            polyline.setChild(gpolyline);
            map.addOverlay(gpolyline);
            if(!old) {
                this.polylines.push(polyline);
            }
            break;
        case 'microsoft':
            mpolyline = polyline.toMicrosoft();
            polyline.setChild(mpolyline);
            map.AddPolyline(mpolyline);
            if(!old) {
                this.polylines.push(polyline);
            }
            break;
        case 'openlayers':
            if (!this.layers['polylines']) {
                this.layers['polylines'] = new OpenLayers.Layer.Vector('polylines');
                map.addLayer(this.layers['polylines']);
            }
            var olpolyline = polyline.toOpenLayers();
            polyline.setChild(olpolyline);
            this.layers['polylines'].addFeatures([olpolyline]);
            if(!old) {
                this.polylines.push(polyline);
            }
            break;
        case 'multimap':
            mmpolyline = polyline.toMultiMap();
            polyline.setChild(mmpolyline);
            map.addOverlay( mmpolyline );
            if(!old) {
                this.polylines.push(polyline);
            }
            break;
        case 'mapquest':
            mqpolyline = polyline.toMapQuest();
            polyline.setChild(mqpolyline);
            map.addOverlay( mqpolyline );
            if(!old) {
                this.polylines.push(polyline);
            }
            break;
        case 'map24':
            var m24polyline = polyline.toMap24();
            polyline.setChild(m24polyline);
            m24polyline.commit();
            if(!old) {
                this.polylines.push(polyline);
            }
            break;
        case 'viamichelin':
            var vmpolyline = polyline.toViaMichelin();
            polyline.setChild(vmpolyline);
            map.addLayer( vmpolyline );
            if(!old) {
                this.polylines.push(polyline);
            }
            break;
        default:
            if(this.debug) {
                alert(this.api + ' not supported by Mapstraction.addPolyline');
            }
    }
};

/**
 * Remove the polyline from the map
 * @param {Polyline} polyline The Polyline to remove from the map
 */
Mapstraction.prototype.removePolyline = function(polyline) {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.removePolyline(polyline);
        } );
        return;
    }

    var map = this.maps[this.api];

    var tmparray = [];
    while(this.polylines.length > 0){
        current_polyline = this.polylines.pop();
        if(polyline == current_polyline) {
            switch (this.api) {
                case 'openspace':
                    map.getVectorLayer().removeFeatures([polyline.proprietary_polyline]);
                    break;
                case 'google':
                case 'openstreetmap':
                    map.removeOverlay(polyline.proprietary_polyline);
                    break;
                case 'yahoo':
                    map.removeOverlay(polyline.proprietary_polyline);
                    break;
                case 'microsoft':
                    map.DeletePolyline(polyline.pllID);
                    break;
                case 'multimap':
                    polyline.proprietary_polyline.remove();
                    break;
                case 'mapquest':
                    map.removeOverlay(polyline.proprietary_polyline);
                    break;
                case 'map24':
                    polyline.proprietary_polyline.remove();
                    break;
                case 'openlayers':
                    this.layers['polylines'].removeFeatures([polyline.proprietary_polyline]);
                    break;
                case 'viamichelin':
                    map.removeLayer(polyline.proprietary_polyline);
                    break;
            }
            polyline.onmap = false;
            break;
        } else {
            tmparray.push(current_polyline);
        }
    }
    this.polylines = this.polylines.concat(tmparray);
};

/**
 * Removes all polylines from the map
 */
Mapstraction.prototype.removeAllPolylines = function() {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.removeAllPolylines();
        } );
        return;
    }

    var map = this.maps[this.api];

    switch (this.api) {
        case 'openspace':
            for(var i = 0, length = this.polylines.length; i < length; i++){
                map.getVectorLayer().removeFeatures([this.polylines[i].proprietary_polyline]);
            }
            break;
        case 'yahoo':
            for(var i = 0, length = this.polylines.length; i < length; i++){
                map.removeOverlay(this.polylines[i].proprietary_polyline);
            }
            break;
        case 'google':
        case 'openstreetmap':
            for(var i = 0, length = this.polylines.length; i < length; i++){
                map.removeOverlay(this.polylines[i].proprietary_polyline);
            }
            break;
        case 'microsoft':
            map.DeleteAllPolylines();
            break;
        case 'multimap':
            for(var i = 0, length = this.polylines.length; i < length; i++){
                this.polylines[i].proprietary_polyline.remove();
            }
            break;
        case 'mapquest':
            map.removeAllShapes();
            break;
        case 'map24':
            // don't think map24 has a specific method for this
            var current_polyline;
            while(this.polylines.length > 0) {
                current_polyline = this.polylines.pop();
                current_polyline.proprietary_polyline.remove();
            }
            break;
        case 'openlayers':
            var olpolylines = [];
            for(var i = 0, length = this.polylines.length; i < length; i++){
                olpolylines.push(this.polylines[i].proprietary_polyline);
            }
            if (this.layers['polylines']) this.layers['polylines'].removeFeatures(olpolylines);
            break;
        case 'viamichelin':
            for(var i = 0, length = this.polylines.length; i < length; i++){
                map.removeLayer(this.polylines[i].proprietary_polyline);
            }
            break;
        default:
            if(this.debug) {
                alert(this.api + ' not supported by Mapstraction.removeAllPolylines');
            }
    }
    this.polylines = [];
};

/**
 * getCenter gets the central point of the map
 * @type {LatLonPoint} The center point of the map
 */
Mapstraction.prototype.getCenter = function() {
    if(this.loaded[this.api] === false) {
        return null;
    }

    var map = this.maps[this.api];

    var point = undefined;
    var pt;
    switch (this.api) {
        case 'openspace' :
            pt = map.getCenter(); // an OpenSpace.MapPoint, UK National Grid
            point = new LatLonPoint();
            point.fromOpenSpace(pt);  // convert to LatLonPoint
            break;
        case 'yahoo':
            pt = map.getCenterLatLon();
            point = new LatLonPoint(pt.Lat,pt.Lon);
            break;
        case 'google':
        case 'openstreetmap':
            pt = map.getCenter();
            point = new LatLonPoint(pt.lat(),pt.lng());
            break;
        case 'openlayers':
            pt = map.getCenter();
            point = new LatLonPoint(pt.lat, pt.lon);
            break;
        case 'microsoft':
            pt = map.GetCenter();
            point = new LatLonPoint(pt.Latitude,pt.Longitude);
            break;
        case 'multimap':
            pt = map.getMapBounds().getCenter();
            point = new LatLonPoint(pt.lat, pt.lon);
            break;
        case 'mapquest':
            pt = map.getCenter();
            point = new LatLonPoint(pt.getLatitude(), pt.getLongitude());
            break;
        case 'map24':
            pt = map.MapClient['Static'].getCurrentMapView().getCenter();
            point = new LatLonPoint(pt.Y/60,pt.X/60);
            break;
        case 'viamichelin':
            pt = map.GetCenter();
            point = new LatLonPoint(pt.lat, pt.lon);
            break;
        default:
            if(this.debug) {
                alert(this.api + ' not supported by Mapstraction.getCenter');
            }
    }
    return point;
};

/**
 * setCenter sets the central point of the map
 * @param {LatLonPoint} point The point at which to center the map
 * @options {hash} optional parameters, such as {pan:true}
 */
Mapstraction.prototype.setCenter = function(point, options) {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.setCenter(point, options);
        } );
        return;
    }

    var map = this.maps[this.api];

    switch (this.api) {
        case 'openspace' :
            map.setCenter(point.toOpenSpace());
            break;
        case 'yahoo':
            map.panToLatLon(point.toYahoo());
            break;
        case 'google':
        case 'openstreetmap':
          if(options != null && options['pan']) { map.panTo(point.toGoogle()); }
          else { map.setCenter(point.toGoogle()); }
          break;
        case 'openlayers':
            map.setCenter(point.toOpenLayers());
            break;
        case 'microsoft':
          if(options != null && options['pan']) { map.PanToLatLong(point.toMicrosoft()); }
          else { map.SetCenter(point.toMicrosoft()); }
          break;
        case 'multimap':
            map.goToPosition(point.toMultiMap());
            break;
        case 'mapquest':
            map.setCenter(point.toMapQuest());
            break;
        case 'freeearth':
            if (this.freeEarthLoaded) {
                map.setTargetLatLng( point.toFreeEarth() );
            }
            else {
                var me = this;
                this.freeEarthOnLoad.push( function(){
                    me.setCenterAndZoom(point);
                } );
            }
            break;
        case 'map24':
            // Since center changes the zoom level to default
            // we have to get the original metre width and pass it back in when
            // centering.
            var mv = map.MapClient['Static'].getCurrentMapView();
            var newSettings = {};
            newSettings.MinimumWidth = lonToMetres
            (mv.LowerRight.Longitude - mv.TopLeft.Longitude,
                (mv.LowerRight.Latitude+mv.TopLeft.Latitude)/2);
            newSettings.Latitude =  point.lat*60;
            newSettings.Longitude = point.lon*60;
            Map24.MapApplication.center(newSettings);
            break;
        case 'viamichelin':
            map.panTo(point.toViaMichelin());
            break;
        default:
            if(this.debug) {
                alert(this.api + ' not supported by Mapstraction.setCenter');
            }
    }
};


/**
 * setZoom sets the zoom level for the map
 * MS doesn't seem to do zoom=0, and Gg's sat goes closer than it's maps, and MS's sat goes closer than Y!'s
 * TODO: Mapstraction.prototype.getZoomLevels or something.
 * @param {int} zoom The (native to the map) level zoom the map to.
 */
Mapstraction.prototype.setZoom = function(zoom) {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.setZoom(zoom);
        } );
        return;
    }

    var map = this.maps[this.api];

    switch (this.api) {
        case 'openspace' :
            // convert to openspace equivalent
            var oszoom = zoom-6;
            if (oszoom<0) {
                oszoom = 0;
            }
            else if (oszoom>10) {
                oszoom = 10;
            }
            map.zoomTo(oszoom);
            break;
        case 'yahoo':
            var yzoom = 18 - zoom; // maybe?
            map.setZoomLevel(yzoom);
            break;
        case 'google':
        case 'openstreetmap':
            map.setZoom(zoom);
            break;
        case 'openlayers':
            map.zoomTo(zoom);
            break;
        case 'microsoft':
            map.SetZoomLevel(zoom);
            break;
        case 'multimap':
            map.setZoomFactor(zoom);
            break;
        case 'mapquest':
            map.setZoomLevel(zoom - 3); // MapQuest seems off by 3
            break;
        case 'map24':
            // get the current centre than calculate the settings based on this
            var point = this.getCenter();
            var newSettings = {};
            newSettings.Latitude = point.lat*60;
            newSettings.Longitude = point.lon*60;
            var client = map.MapClient['Static'];
            var dLon = getDegreesFromGoogleZoomLevel(client.getCanvasSize().Width, zoom);
            newSettings.MinimumWidth = lonToMetres(dLon, point.lat);
            Map24.MapApplication.center(newSettings);
            break;
        case 'viamichelin':
            // [0-19] => [0-16]
            map.changeMapScale(Math.floor(zoom / 19 * 16));
            break;
        default:
            if(this.debug) {
                alert(this.api + ' not supported by Mapstraction.setZoom');
            }
    }
};

/**
 * autoCenterAndZoom sets the center and zoom of the map to the smallest bounding box
 * containing all markers
 */
Mapstraction.prototype.autoCenterAndZoom = function() {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.autoCenterAndZoom();
        } );
        return;
    }

    var lat_max = -90;
    var lat_min = 90;
    var lon_max = -180;
    var lon_min = 180;

    for (var i=0; i<this.markers.length; i++) {
        lat = this.markers[i].location.lat;
        lon = this.markers[i].location.lon;
        if (lat > lat_max) {
            lat_max = lat;
        }
        if (lat < lat_min) {
            lat_min = lat;
        }
        if (lon > lon_max) {
            lon_max = lon;
        }
        if (lon < lon_min) {
            lon_min = lon;
        }
    }
    for (var i=0; i<this.polylines.length; i++) {
        for (var j=0; j<this.polylines[i].points.length; j++) {
            lat = this.polylines[i].points[j].lat;
            lon = this.polylines[i].points[j].lon;
            if (lat > lat_max) {
                lat_max = lat;
            }
            if (lat < lat_min) {
                lat_min = lat;
            }
            if (lon > lon_max) {
                lon_max = lon;
            }
            if (lon < lon_min) {
                lon_min = lon;
            }
        }
    }
    this.setBounds( new BoundingBox(lat_min, lon_min, lat_max, lon_max) );
};

/**
 * centerAndZoomOnPoints sets the center and zoom of the map from an array of points
 *
 * This is useful if you don't want to have to add markers to the map
 */
Mapstraction.prototype.centerAndZoomOnPoints = function(points) {
    var bounds = new BoundingBox(points[0].lat,points[0].lon,points[0].lat,points[0].lon);

    for (var i=1, len = points.length ; i<len; i++) {
        bounds.extend(points[i]);
    }

    this.setBounds(bounds);
};

/**
 * Sets the center and zoom of the map to the smallest bounding box
 * containing all visible markers and polylines
 * will only include markers and polylines with an attribute of "visible"
 */
Mapstraction.prototype.visibleCenterAndZoom = function()
{
	if(this.loaded[this.api] == false)
	{
		myself = this;
		this.onload[this.api].push(function()
		{
			myself.autoCenterAndZoom();
		});
		return;
	}

	var lat_max = -90;
	var lat_min = 90;
	var lon_max = -180;
	var lon_min = 180;

	for (var i=0; i<this.markers.length; i++)
	{
		if (this.markers[i].getAttribute("visible"))
		{
			lat = this.markers[i].location.lat;
			lon = this.markers[i].location.lon;

			if (lat > lat_max) lat_max = lat;
			if (lat < lat_min) lat_min = lat;
			if (lon > lon_max) lon_max = lon;
			if (lon < lon_min) lon_min = lon;
		}
	}

	for (i=0; i<this.polylines.length; i++)
	{
		if (this.polylines[i].getAttribute("visible"))
		{
			for (j=0; j<this.polylines[i].points.length; j++)
			{
				lat = this.polylines[i].points[j].lat;
				lon = this.polylines[i].points[j].lon;

				if (lat > lat_max) lat_max = lat;
				if (lat < lat_min) lat_min = lat;
				if (lon > lon_max) lon_max = lon;
				if (lon < lon_min) lon_min = lon;
			}
		}
	}

	this.setBounds(new BoundingBox(lat_min, lon_min, lat_max, lon_max));
};

/**
 * Automatically sets center and zoom level to show all polylines
 * Takes into account radius of polyline
 * @param {Int} radius
 */
Mapstraction.prototype.polylineCenterAndZoom = function(radius)
{
	if(this.loaded[this.api] == false)
	{
		myself = this;
		this.onload[this.api].push(function()
		{
			myself.polylineCenterAndZoom();
		});
		return;
	}

	radius = (radius == null) ? 0 : radius;
	
	var lat_max = -90;
	var lat_min = 90;
	var lon_max = -180;
	var lon_min = 180;

	for (i=0; i < mapstraction.polylines.length; i++)
	{
		for (j=0; j<mapstraction.polylines[i].points.length; j++)
		{
			lat = mapstraction.polylines[i].points[j].lat;
			lon = mapstraction.polylines[i].points[j].lon;

			latConv = lonConv = radius;

			if (radius > 0)
			{
				latConv = (radius / mapstraction.polylines[i].points[j].latConv());
				lonConv = (radius / mapstraction.polylines[i].points[j].lonConv());
			}

			if ((lat + latConv) > lat_max) lat_max = (lat + latConv);
			if ((lat - latConv) < lat_min) lat_min = (lat - latConv);
			if ((lon + lonConv) > lon_max) lon_max = (lon + lonConv);
			if ((lon - lonConv) < lon_min) lon_min = (lon - lonConv);
		}
	}

	this.setBounds(new BoundingBox(lat_min, lon_min, lat_max, lon_max));
};

/**
 * getZoom returns the zoom level of the map
 * @type {Integer} The zoom level of the map
 */
Mapstraction.prototype.getZoom = function() {
    if(this.loaded[this.api] === false) {
        var me = this;
        return -1;
    }

    var map = this.maps[this.api];

    switch (this.api) {
        case 'openspace' :
            return map.zoom + 6;  // convert to equivalent google zoom
        case 'yahoo':
            return 18 - map.getZoomLevel(); // maybe?
        case 'google':
        case 'openstreetmap':
            return map.getZoom();
        case 'openlayers':
            return map.zoom;
        case 'microsoft':
            return map.GetZoomLevel();
        case 'multimap':
            return map.getZoomFactor();
        case 'mapquest':
            return map.getZoomLevel() + 3; // Mapquest seems off by 3?
        case 'map24':
            // since map24 doesn't use a Google-style set of zoom levels, we have
            // to round to the nearest zoom
            var mv = map.MapClient['Static'].getCurrentMapView();
            var dLon = (mv.LowerRight.Longitude - mv.TopLeft.Longitude) / 60;
            var width = map.MapClient['Static'].getCanvasSize().Width;
            var zoom = getGoogleZoomLevelFromDegrees (width,dLon);
            return Math.round(zoom);
        case 'viamichelin':
            // [0-16] => [0-19]
            return Math.floor(map.getMapScale() / 16 * 19);
            break;
        default:
            if(this.debug) {
                alert(this.api + ' not supported by Mapstraction.getZoom');
            }
    }
};

/**
 * getZoomLevelForBoundingBox returns the best zoom level for bounds given
 * @param boundingBox the bounds to fit
 * @type {Integer} The closest zoom level that contains the bounding box
 */
Mapstraction.prototype.getZoomLevelForBoundingBox = function( bbox ) {
    if(this.loaded[this.api] === false) {
        var me = this;
        return -1;
    }

    var map = this.maps[this.api];

    // NE and SW points from the bounding box.
    var ne = bbox.getNorthEast();
    var sw = bbox.getSouthWest();
    var zoom;

    switch (this.api) {
        case 'openspace' :
            var obounds = new OpenSpace.MapBounds();
            obounds.extend(new LatLonPoint(sw.lat,sw.lon).toOpenSpace());
            obounds.extend(new LatLonPoint(ne.lat,ne.lon).toOpenSpace());
            zoom = map.getZoomForExtent(obounds) + 6; // get it and adjust to equivalent google zoom
            return zoom
        case 'google':
        // no break statement here intentionally
        case 'openstreetmap':
            var gbox = new GLatLngBounds( sw.toGoogle(), ne.toGoogle() );
            zoom = map.getBoundsZoomLevel( gbox );
            return zoom;
        case 'openlayers':
            //  FIXME: BoundingBox.toOpenLayers is missing
            // var olbox = bbox.toOpenLayers();
            // zoom = map.getZoomForExtent(olbox);
            return zoom;
        case 'multimap':
            var mmlocation = map.getAutoScaleLocation( [sw.toMultiMap(), ne.toMultiMap()] );
            zoom = mmlocation.zoom_factor;
            return zoom;
        case 'map24':
            // since map24 doesn't use a Google-style set of zoom levels, we work
            // out what zoom level will show the given longitude difference within
            // the current map pixel width
            var dLon = ne.lon - sw.lon;
            var width = map.MapClient['Static'].getCanvasSize().Width;
            zoom = getGoogleZoomLevelFromDegrees (width,dLon);
            return Math.round(zoom);
        case 'viamichelin':
            map.drawMapFromLayers();
            return map.getMapScale();
        default:
            if(this.debug) {
                alert(this.api + ' not supported by Mapstraction.getZoomLevelForBoundingBox' );
            }
    }
};


// any use this being a bitmask? Should HYBRID = ROAD | SATELLITE?
Mapstraction.ROAD = 1;
Mapstraction.SATELLITE = 2;
Mapstraction.HYBRID = 3;




/**
 * setMapType sets the imagery type for the map.
 * The type can be one of:
 * Mapstraction.ROAD
 * Mapstraction.SATELLITE
 * Mapstraction.HYBRID
 * @param {int} type The (native to the map) level zoom the map to.
 */
Mapstraction.prototype.setMapType = function(type) {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.setMapType(type);
        } );
        return;
    }

    var map = this.maps[this.api];

    switch (this.api) {
        case 'yahoo':
            switch(type) {
                case Mapstraction.ROAD:
                    map.setMapType(YAHOO_MAP_REG);
                    break;
                case Mapstraction.SATELLITE:
                    map.setMapType(YAHOO_MAP_SAT);
                    break;
                case Mapstraction.HYBRID:
                    map.setMapType(YAHOO_MAP_HYB);
                    break;
                default:
                    map.setMapType(YAHOO_MAP_REG);
            }
            break;
        case 'google':
        case 'openstreetmap':
            switch(type) {
                case Mapstraction.ROAD:
                    map.setMapType(G_NORMAL_MAP);
                    break;
                case Mapstraction.SATELLITE:
                    map.setMapType(G_SATELLITE_MAP);
                    break;
                case Mapstraction.HYBRID:
                    map.setMapType(G_HYBRID_MAP);
                    break;
                default:
                    map.setMapType(G_NORMAL_MAP);
            }
            break;
        case 'microsoft':
            // TODO: oblique?
            switch(type) {
                case Mapstraction.ROAD:
                    map.SetMapStyle(Msn.VE.MapStyle.Road);
                    break;
                case Mapstraction.SATELLITE:
                    map.SetMapStyle(Msn.VE.MapStyle.Aerial);
                    break;
                case Mapstraction.HYBRID:
                    map.SetMapStyle(Msn.VE.MapStyle.Hybrid);
                    break;
                default:
                    map.SetMapStyle(Msn.VE.MapStyle.Road);
            }
            break;
        case 'multimap':
            maptypes = map.getAvailableMapTypes();
            maptype = -1;
            for (var i = 0; i < maptypes.length; i++) {
                switch (maptypes[i]) {
                    case MM_WORLD_MAP:
                        if (type == Mapstraction.ROAD) {
                            maptype = maptypes[i];
                        }
                        default_type = maptypes[i];
                        break;
                    case MM_WORLD_AERIAL:
                        if (type == Mapstraction.SATELLITE) {
                            maptype = maptypes[i];
                        }
                        break;
                    case MM_WORLD_HYBRID:
                        if (type == Mapstraction.HYBRID) {
                            maptype = maptypes[i];
                        }
                        break;
                }
            }
            if (maptype == -1) {
                maptype = default_type;
            }
            map.setMapType(maptype);
            break;
        case 'mapquest':
            switch (type) {
                case Mapstraction.ROAD:
                    map.setMapType("map");
                    break;
                case Mapstraction.SATELLITE:
                    map.setMapType("sat");
                    break;
                case Mapstraction.HYBRID:
                    map.setMapType("hyb");
                    break;
            }
            break;
        case 'viamichelin':
            map.activateSatelliteHybrid(true);
            break;
        default:
            if(this.debug){
                alert(this.api + ' not supported by Mapstraction.setMapType');
            }
    }
};


/**
 * getMapType gets the imagery type for the map.
 * The type can be one of:
 * Mapstraction.ROAD
 * Mapstraction.SATELLITE
 * Mapstraction.HYBRID
 */
Mapstraction.prototype.getMapType = function() {
    if(this.loaded[this.api] === false) {
        var me = this;
        return -1;
    }

    var map = this.maps[this.api];

    var type;
    switch (this.api) {
        case 'yahoo':
            type = map.getCurrentMapType();
            switch(type) {
                case YAHOO_MAP_REG:
                    return Mapstraction.ROAD;
                case YAHOO_MAP_SAT:
                    return Mapstraction.SATELLITE;
                case YAHOO_MAP_HYB:
                    return Mapstraction.HYBRID;
                default:
                    return null;
            }
            break;
        case 'google':
        case 'openstreetmap':
            type = map.getCurrentMapType();
            switch(type) {
                case G_NORMAL_MAP:
                    return Mapstraction.ROAD;
                case G_SATELLITE_MAP:
                    return Mapstraction.SATELLITE;
                case G_HYBRID_MAP:
                    return Mapstraction.HYBRID;
                default:
                    return null;
            }
            break;
        case 'microsoft':
            // TODO: oblique?
            type = map.GetMapStyle();
            switch(type) {
                case Msn.VE.MapStyle.Road:
                    return Mapstraction.ROAD;
                case Msn.VE.MapStyle.Aerial:
                    return Mapstraction.SATELLITE;
                case Msn.VE.MapStyle.Hybrid:
                    return Mapstraction.HYBRID;
                default:
                    return null;
            }
            break;
        case 'multimap':
            maptypes = map.getAvailableMapTypes();
            type = map.getMapType();
            switch(type) {
                case MM_WORLD_MAP:
                    return Mapstraction.ROAD;
                case MM_WORLD_AERIAL:
                    return Mapstraction.SATELLITE;
                case MM_WORLD_HYBRID:
                    return Mapstraction.HYBRID;
                default:
                    return null;
            }
            break;
        case 'mapquest':
            type = map.getMapType();
            switch(type) {
                case "map":
                    return Mapstraction.ROAD;
                case "sat":
                    return Mapstraction.SATELLITE;
                case "hyb":
                    return Mapstraction.HYBRID;
                default:
                    return null;
            }
            break;
        case 'viamichelin': // TODO
        default:
            if(this.debug) {
                alert(this.api + ' not supported by Mapstraction.getMapType');
            }
    }
};

/**
 * getBounds gets the BoundingBox of the map
 * @returns the bounding box for the current map state
 * @type BoundingBox
 */
Mapstraction.prototype.getBounds = function () {
    if(this.loaded[this.api] === false) {
        return null;
    }

    var map = this.maps[this.api];
    var ne, sw, nw, se;
    switch (this.api) {
        case 'openspace':
            var olbox = map.calculateBounds().toArray(); // array of openspace coords, left, bottom, right, top
            var ossw = new OpenSpace.MapPoint( olbox[0], olbox[1] );
            var osne = new OpenSpace.MapPoint( olbox[2], olbox[3] );
            // convert to LatLonPoints
            sw = new LatLonPoint;
            sw.fromOpenSpace(ossw);
            ne = new LatLonPoint;
            ne.fromOpenSpace(osne);
            return new BoundingBox(sw.lat, sw.lon, ne.lat, ne.lon);
        case 'google':
        case 'openstreetmap':
            var gbox = map.getBounds();
            sw = gbox.getSouthWest();
            ne = gbox.getNorthEast();
            return new BoundingBox(sw.lat(), sw.lng(), ne.lat(), ne.lng());
        case 'openlayers':
            var olbox = map.calculateBounds();
            return new BoundingBox(olbox.bottom, olbox.left, olbox.top, olbox.right);
        case 'yahoo':
            var ybox = map.getBoundsLatLon();
            return new BoundingBox(ybox.LatMin, ybox.LonMin, ybox.LatMax, ybox.LonMax);
        case 'microsoft':
            var mbox = map.GetMapView();
            nw = mbox.TopLeftLatLong;
            se = mbox.BottomRightLatLong;
            return new BoundingBox(se.Latitude,nw.Longitude,nw.Latitude,se.Longitude);
        case 'multimap':
            var mmbox = map.getMapBounds();
            sw = mmbox.getSouthWest();
            ne = mmbox.getNorthEast();
            return new BoundingBox(sw.lat, sw.lon, ne.lat, ne.lon);
        case 'mapquest':
            var mqbox = map.getMapBounds(); // MQRectLL
            se = mqbox.getLowerRightLatLng();
            nw = mqbox.getUpperLeftLatLng();

            // NW is this correct ???
            // return new BoundingBox(se.lat, se.lon, nw.lat, nw.lon);

            // should be this instead
            return new MQA.BoundingBox(se.lat, nw.lon, nw.lat, se.lon);
        case 'map24':
            var mv = map.MapClient['Static'].getCurrentMapView();
            se = mv.LowerRight;
            nw = mv.TopLeft;
            return new BoundingBox (se.Latitude/60, nw.Longitude/60,
                nw.Latitude/60, se.Longitude/60 );
        case 'viamichelin': // TODO
        default:
            if(this.debug) {
                alert(this.api + ' not supported by Mapstraction.getBounds');
            }
    }
};

/**
 * setBounds sets the map to the appropriate location and zoom for a given BoundingBox
 * @param {BoundingBox} the bounding box you want the map to show
 */
Mapstraction.prototype.setBounds = function(bounds){
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.setBounds(bounds);
        } );
        return;
    }

    var map = this.maps[this.api];

    var sw = bounds.getSouthWest();
    var ne = bounds.getNorthEast();
    switch (this.api) {
        case 'openspace':
            var obounds = new OpenSpace.MapBounds();
            obounds.extend(new LatLonPoint(sw.lat,sw.lon).toOpenSpace());
            obounds.extend(new LatLonPoint(ne.lat,ne.lon).toOpenSpace());
            map.zoomToExtent(obounds);
            break;
        case 'google':
        case 'openstreetmap':
            var gbounds = new GLatLngBounds(new GLatLng(sw.lat,sw.lon),new GLatLng(ne.lat,ne.lon));
            map.setCenter(gbounds.getCenter(), map.getBoundsZoomLevel(gbounds));
            break;

        case 'openlayers':
            var obounds = new OpenLayers.Bounds();
            obounds.extend(new LatLonPoint(sw.lat,sw.lon).toOpenLayers());
            obounds.extend(new LatLonPoint(ne.lat,ne.lon).toOpenLayers());
            map.zoomToExtent(obounds);
            break;
        case 'yahoo':
            if(sw.lon > ne.lon) {
                sw.lon -= 360;
            }
            var center = new YGeoPoint((sw.lat + ne.lat)/2, (ne.lon + sw.lon)/2);

            var container = map.getContainerSize();
            for(var zoom = 1 ; zoom <= 17 ; zoom++){
                var sw_pix = convertLatLonXY_Yahoo(sw,zoom);
                var ne_pix = convertLatLonXY_Yahoo(ne,zoom);
                if(sw_pix.x > ne_pix.x) {
                    sw_pix.x -= (1 << (26 - zoom)); //earth circumference in pixel
                }
                if(Math.abs(ne_pix.x - sw_pix.x) <= container.width
                    && Math.abs(ne_pix.y - sw_pix.y) <= container.height){
                    map.drawZoomAndCenter(center, zoom); //Call drawZoomAndCenter here: OK if called multiple times anyway
                    break;
                }
            }
            break;
        case 'microsoft':
            map.SetMapView([new VELatLong(sw.lat,sw.lon),new VELatLong(ne.lat,ne.lon)]);
            break;
        case 'multimap':
            var mmlocation = map.getAutoScaleLocation([sw.toMultiMap(), ne.toMultiMap()]);
            map.goToPosition(mmlocation.coords, mmlocation.zoom_factor);
            break;
        case 'mapquest':
            var mqcenter = new LatLonPoint((sw.lat + ne.lat)/2, (ne.lon + sw.lon)/2);
            var dLon = ne.lon - sw.lon;
            var mqsize = map.getSize();
            var zoom = getGoogleZoomLevelFromDegrees(mqsize.getWidth(), dLon);
            this.setCenterAndZoom(mqcenter, Math.floor(zoom));
            break;
        case 'freeearth':
            var center = new LatLonPoint((sw.lat + ne.lat)/2, (ne.lon + sw.lon)/2);
            this.setCenter(center);
            break;
        case 'map24':
            var settings = {};
            settings.Latitude = ((sw.lat+ne.lat) / 2) * 60;
            settings.Longitude = ((sw.lon+ne.lon) / 2) * 60;
            // need to convert lat/lon to metres
            settings.MinimumWidth = lonToMetres(ne.lon-sw.lon, (ne.lat+sw.lat)/2);
            settings.MinimumWidth *= 2.4; // zoom out needed for a better view
            Map24.MapApplication.center(settings);
            break;
        case 'viamichelin':
            // add a dummy polyline
            var vmpoints = new Array(new LatLonPoint(sw.lat,sw.lon), new LatLonPoint(ne.lat,ne.lon));
            var vmpoly = new VMPolyLine(vmpoints);
            map.addLayer(vmpoly);
            // then call native function to center and zoom
            map.drawMapFromLayers();
            break;
        default:
            if(this.debug) {
                alert(this.api + ' not supported by Mapstraction.setBounds');
            }
    }
};

/**
 * addImageOverlay layers an georeferenced image over the map
 * @param {id} unique DOM identifier
 * @param {src} url of image
 * @param {opacity} opacity 0-100
 * @param {west} west boundary
 * @param {south} south boundary
 * @param {east} east boundary
 * @param {north} north boundary
 */
Mapstraction.prototype.addImageOverlay = function(id, src, opacity, west, south, east, north) {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.addImageOverlay(id, src, opacity, west, south, east, north);
        } );
        return;
    }

    var map = this.maps[this.api];

    var b = document.createElement("img");
    b.style.display = 'block';
    b.setAttribute('id',id);
    b.setAttribute('src',src);
    b.style.position = 'absolute';
    b.style.zIndex = 1;
    b.setAttribute('west',west);
    b.setAttribute('south',south);
    b.setAttribute('east',east);
    b.setAttribute('north',north);

    switch (this.api) {
        case 'google':
        case 'openstreetmap':
            map.getPane(G_MAP_MAP_PANE).appendChild(b);
            this.setImageOpacity(id, opacity);
            this.setImagePosition(id);
            GEvent.bind(map, "zoomend", this, function() {
                this.setImagePosition(id);
            });
            GEvent.bind(map, "moveend", this, function() {
                this.setImagePosition(id);
            });
            break;

        case 'multimap':
            map.getContainer().appendChild(b);
            this.setImageOpacity(id, opacity);
            this.setImagePosition(id);
            me = this;
            map.addEventHandler( 'changeZoom', function(eventType, eventTarget, arg1, arg2, arg3) {
                me.setImagePosition(id);
            });
            map.addEventHandler( 'drag', function(eventType, eventTarget, arg1, arg2, arg3) {
                me.setImagePosition(id);
            });
            map.addEventHandler( 'endPan', function(eventType, eventTarget, arg1, arg2, arg3) {
                me.setImagePosition(id);
            });
            break;

        case 'viamichelin': // TODO
        default:
            b.style.display = 'none';
            if (this.debug) {
                alert(this.api + "not supported by Mapstraction.addImageOverlay not supported");
            }
            break;
    }
};

Mapstraction.prototype.setImageOpacity = function(id, opacity) {
    if (opacity < 0) {
        opacity = 0;
    }
    if (opacity >= 100) {
        opacity = 100;
    }
    var c = opacity / 100;
    var d = document.getElementById(id);
    if(typeof(d.style.filter)=='string'){
        d.style.filter='alpha(opacity:'+opacity+')';
    }
    if(typeof(d.style.KHTMLOpacity)=='string'){
        d.style.KHTMLOpacity=c;
    }
    if(typeof(d.style.MozOpacity)=='string'){
        d.style.MozOpacity=c;
    }
    if(typeof(d.style.opacity)=='string'){
        d.style.opacity=c;
    }
};

Mapstraction.prototype.setImagePosition = function(id) {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.setImagePosition(id);
        } );
        return;
    }

    var map = this.maps[this.api];
    var x = document.getElementById(id);
    var d; var e;

    switch (this.api) {
        case 'google':
        case 'openstreetmap':
            d = map.fromLatLngToDivPixel(new GLatLng(x.getAttribute('north'), x.getAttribute('west')));
            e = map.fromLatLngToDivPixel(new GLatLng(x.getAttribute('south'), x.getAttribute('east')));
            break;
        case 'multimap':
            d = map.geoPosToContainerPixels(new MMLatLon(x.getAttribute('north'), x.getAttribute('west')));
            e = map.geoPosToContainerPixels(new MMLatLon(x.getAttribute('south'), x.getAttribute('east')));
            break;
        case 'viamichelin': // TODO
    }

    x.style.top = d.y.toString() + 'px';
    x.style.left = d.x.toString() + 'px';
    x.style.width = (e.x - d.x).toString() + 'px';
    x.style.height = (e.y - d.y).toString() + 'px';
};

/**
 * addOverlay adds a GeoRSS or KML overlay to the map
 *  some flavors of GeoRSS and KML are not supported by some of the Map providers
 * @param{url} GeoRSS or KML feed URL
 * @param{autoCenterAndZoom} set true to auto center and zoom after the feed is loaded
 */
Mapstraction.prototype.addOverlay = function(url, autoCenterAndZoom) {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.addOverlay(georssURL);
        } );
        return;
    }
    if(autoCenterAndZoom == null)
        autoCenterAndZoom = false;

    var map = this.maps[this.api];
    switch (this.api) {
        case 'yahoo':
            map.addOverlay(new YGeoRSS(url));
            break;
        case 'openstreetmap': // OSM uses the google interface, so allow cascade
        case 'google':
            var geoXML = new GGeoXml(url);
            map.addOverlay(geoXML, function() {
                if(autoCenterAndZoom) {
                    geoXML.gotoDefaultViewport(map);
                }
            });
            break;
        case 'microsoft':
            var shapeLayer = new VEShapeLayer();
            var shapeSpec = new VEShapeSourceSpecification(VEDataType.ImportXML,url,shapeLayer);
            map.ImportShapeLayerData(shapeSpec, function(feed){ }, autoCenterAndZoom);
            break;
        // case 'openlayers':
        //     map.addLayer(new OpenLayers.Layer.GeoRSS("GeoRSS Layer", url));
        // break;
        case 'multimap':
            break;
        case 'freeearth':
            if (this.freeEarthLoaded) {
                var ferss = new FE.GeoRSS(url);
                map.addOverlay(ferss);
            }
            else {
                var me = this;
                this.freeEarthOnLoad.push( function() {
                    me.addOverlay(url);
                } );
            }
            break;
        case 'viamichelin': // TODO
        default:
            if(this.debug) {
                alert(this.api + ' not supported by Mapstraction.addOverlay');
            }
    }

};

Mapstraction.prototype.addJSON = function(json) {
    var features;
    if (typeof(json) == "string") {
        features = eval('(' + json + ')');
    } else {
        features = json;
    }
    features = features.features;
    var map = this.maps[this.api];
    var html = "";
    var item;
    var polyline;
    var marker;
    var markers = [];

    if(features.type == "FeatureCollection") {
        this.addJSON(features.features);
    }

    for (var i = 0; i < features.length; i++) {
        item = features[i];
        switch(item.geometry.type) {
            case "Point":
                html = "<strong>" + item.title + "</strong><p>" + item.description + "</p>";
                marker = new Marker(new LatLonPoint(item.geometry.coordinates[1],item.geometry.coordinates[0]));
                markers.push(marker);
                this.addMarkerWithData(marker,{
                    infoBubble : html,
                    label : item.title,
                    date : "new Date(\""+item.date+"\")",
                    iconShadow : item.icon_shadow,
                    marker : item.id,
                    date : "new Date(\""+item.date+"\")",
                    iconShadowSize : item.icon_shadow_size,
                    icon : "http://boston.openguides.org/markers/AQUA.png",
                    iconSize : item.icon_size,
                    category : item.source_id,
                    draggable : false,
                    hover : false
                });
                break;
            case "Polygon":
                var points = [];
                polyline = new Polyline(points);
                mapstraction.addPolylineWithData(polyline,{
                    fillColor : item.poly_color,
                    date : "new Date(\""+item.date+"\")",
                    category : item.source_id,
                    width : item.line_width,
                    opacity : item.line_opacity,
                    color : item.line_color,
                    polygon : true
                });
                markers.push(polyline);
            default:
        // console.log("Geometry: " + features.items[i].geometry.type);
        }
    }
    return markers;
};

/**
 * Adds a Tile Layer to the map
 *
 * Requires providing a parameterized tile url. Use {Z}, {X}, and {Y} to specify where the parameters
 *  should go in the URL.
 *
 * For example, the OpenStreetMap tiles are:
 *  http://tile.openstreetmap.org/{Z}/{X}/{Y}.png
 *
 * @param {tile_url} template url of the tiles.
 * @param {opacity} opacity of the tile layer - 0 is transparent, 1 is opaque. (default=0.6)
 * @param {copyright_text} copyright text to use for the tile layer. (default=Mapstraction)
 * @param {min_zoom} Minimum (furtherest out) zoom level that tiles are available (default=1)
 * @param {max_zoom} Maximum (closest) zoom level that the tiles are available (default=18)
 */
Mapstraction.prototype.addTileLayer = function(tile_url, opacity, copyright_text, min_zoom, max_zoom) {
    if(!tile_url) {
        return;
    }
    if(!this.tileLayers) {
        this.tileLayers = [];
    }
    if(!opacity) {
        opacity = 0.6;
    }
    if(!copyright_text) {
        copyright_text = "Mapstraction";
    }
    if(!min_zoom) {
        min_zoom = 1;
    }
    if(!max_zoom) {
        max_zoom = 18;
    }

    switch (this.api) {
        case 'google':
        case 'openstreetmap':
            var copyright = new GCopyright(1, new GLatLngBounds(new GLatLng(-90,-180), new GLatLng(90,180)), 0, "copyleft");
            var copyrightCollection = new GCopyrightCollection(copyright_text);
            copyrightCollection.addCopyright(copyright);

            var tilelayers = [];
            tilelayers[0] = new GTileLayer(copyrightCollection, min_zoom, max_zoom);
            tilelayers[0].isPng = function() {
                return true;
            };
            tilelayers[0].getOpacity = function() {
                return opacity;
            };
            tilelayers[0].getTileUrl = function (a, b) {
                url = tile_url;
                url = url.replace(/\{Z\}/,b);
                url = url.replace(/\{X\}/,a.x);
                url = url.replace(/\{Y\}/,a.y);
                return url;
            };
            tileLayerOverlay = new GTileLayerOverlay(tilelayers[0]);

            this.tileLayers.push( [tile_url, tileLayerOverlay, true] );
            this.maps[this.api].addOverlay(tileLayerOverlay);
            break;

    }
    return tileLayerOverlay;
};

/**
 * Turns a Tile Layer on or off
 * @param {tile_url} url of the tile layer that was created.
 */
Mapstraction.prototype.toggleTileLayer = function(tile_url) {
    switch (this.api) {
        case 'google':
        case 'openstreetmap':
            for (var f=0; f<this.tileLayers.length; f++) {
                if(this.tileLayers[f][0] == tile_url) {
                    if(this.tileLayers[f][2]) {
                        this.maps[this.api].removeOverlay(this.tileLayers[f][1]);
                        this.tileLayers[f][2] = false;
                    }
                    else {
                        this.maps[this.api].addOverlay(this.tileLayers[f][1]);
                        this.tileLayers[f][2] = true;
                    }
                }
            }
            break;
    }
};

/**
 * addFilter adds a marker filter
 * @param {field} name of attribute to filter on
 * @param {operator} presently only "ge" or "le"
 * @param {value} the value to compare against
 */
Mapstraction.prototype.addFilter = function(field, operator, value) {
    if (!this.filters) {
        this.filters = [];
    }
    this.filters.push( [field, operator, value] );
};

/**
 * Remove the specified filter
 * @param {Object} field
 * @param {Object} operator
 * @param {Object} value
 */
Mapstraction.prototype.removeFilter = function(field, operator, value) {
    if (!this.filters) {
        return;
    }

    var del;
    for (var f=0; f<this.filters.length; f++) {
        if (this.filters[f][0] == field &&
            (! operator || (this.filters[f][1] == operator && this.filters[f][2] == value))) {
            this.filters.splice(f,1);
            f--; //array size decreased
        }
    }
};

/**
 * Delete the current filter if present; otherwise add it
 * @param {Object} field
 * @param {Object} operator
 * @param {Object} value
 */
Mapstraction.prototype.toggleFilter = function(field, operator, value) {
    if (!this.filters) {
        this.filters = [];
    }

    var found = false;
    for (var f = 0; f < this.filters.length; f++) {
        if (this.filters[f][0] == field && this.filters[f][1] == operator && this.filters[f][2] == value) {
            this.filters.splice(f,1);
            f--; //array size decreased
            found = true;
        }
    }

    if (! found) {
        this.addFilter(field, operator, value);
    }
};

/**
 * removeAllFilters
 */
Mapstraction.prototype.removeAllFilters = function() {
    this.filters = [];
};

/**
 * doFilter executes all filters added since last call
 * Now supports a callback function for when a marker is shown or hidden
 * @param {Function} showCallback
 * @param {Function} hideCallback
 * @returns {Int} count of visible markers
 */
Mapstraction.prototype.doFilter = function(showCallback, hideCallback) {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.doFilter(showCallback, hideCallback);
        } );
        return;
    }

    var map = this.maps[this.api];

    var visibleCount = 0;

    if (this.filters) {
        switch (this.api) {
            case 'multimap':
                /* TODO polylines aren't filtered in multimap */
                var mmfilters = [];
                for (var f=0; f<this.filters.length; f++) {
                    mmfilters.push( new MMSearchFilter( this.filters[f][0], this.filters[f][1], this.filters[f][2] ));
                }
                map.setMarkerFilters( mmfilters );
                map.redrawMap();
                break;
            default:
                var vis;
                for (var m=0; m<this.markers.length; m++) {
                    vis = true;
                    for (var f = 0; f < this.filters.length; f++) {
                        if (! this.applyFilter(this.markers[m], this.filters[f])) {
                            vis = false;
                        }
                    }
                    if (vis) {
                        visibleCount ++;
                        if (showCallback) showCallback(this.markers[m]);
                        else this.markers[m].show();
                    } else { 
                        if (hideCallback) hideCallback(this.markers[m]);
                        else this.markers[m].hide();
                    }

                    this.markers[m].setAttribute("visible", vis);
                }

                /*
					 for (var p=0; m<this.polylines.length; p++) {
					 vis = true;
					 for (var f=0; f<this.filters.length; f++) {
					 if (! this.applyFilter(this.polylines[p], this.filters[f])) {
					 vis = false;
					 }
					 }
					 if (vis) {
					 this.polylines[p].show();
					 } else {
					 this.polylines[p].hide();
					 }
					 }
				 */
                break;
        }
    }
    return visibleCount;
};

Mapstraction.prototype.applyFilter = function(o, f) {
    var vis = true;
    switch (f[1]) {
        case 'ge':
            if (o.getAttribute( f[0] ) < f[2]) {
                vis = false;
            }
            break;
        case 'le':
            if (o.getAttribute( f[0] ) > f[2]) {
                vis = false;
            }
            break;
        case 'eq':
            if (o.getAttribute( f[0] ) == f[2]) {
                vis = false;
            }
            break;
    }

    return vis;
};

/**
 * getAttributeExtremes returns the minimum/maximum of "field" from all markers
 * @param {field} name of "field" to query
 * @returns {array} of minimum/maximum
 */
Mapstraction.prototype.getAttributeExtremes = function(field) {
    var min;
    var max;
    for (var m=0; m<this.markers.length; m++) {
        if (! min || min > this.markers[m].getAttribute(field)) {
            min = this.markers[m].getAttribute(field);
        }
        if (! max || max < this.markers[m].getAttribute(field)) {
            max = this.markers[m].getAttribute(field);
        }
    }
    for (var p=0; m<this.polylines.length; m++) {
        if (! min || min > this.polylines[p].getAttribute(field)) {
            min = this.polylines[p].getAttribute(field);
        }
        if (! max || max < this.polylines[p].getAttribute(field)) {
            max = this.polylines[p].getAttribute(field);
        }
    }

    return [min, max];
};

/**
 * Returns a ratio to turn distance into pixels based on current projection
 * @returns {Float} ratio
 */
Mapstraction.prototype.getPixelRatio = function()
{
	if(this.loaded[this.api] == false)
	{
		myself = this;
		this.onload[this.api].push(function()
		{
			myself.getPixelRatio();
		});
		return;
	}

	var map = this.maps[this.api];

	switch (this.api)
	{
		case 'google':
			var projection = G_NORMAL_MAP.getProjection();
			var centerPoint = map.getCenter();
			var zoom = map.getZoom();
			var centerPixel = projection.fromLatLngToPixel(centerPoint, zoom);
			// distance is the distance in metres for 5 pixels (3-4-5 triangle)
			var distancePoint = projection.fromPixelToLatLng(new GPoint(centerPixel.x + 3, centerPixel.y + 4), zoom);
			//*1000(km to m), /5 (pythag), *2 (radius to diameter)
			return 10000/distancePoint.distanceFrom(centerPoint);
			break;
        case 'yahoo':
		case 'openstreetmap':
		case 'microsoft':
		case 'openlayers':
		case 'multimap':
		case 'mapquest':
		case 'map24':
			alert(this.api + ' not supported by Mapstraction.getPixelRatio');
			break;
	}
};

/**
 * getMap returns the native map object that mapstraction is talking to
 * @returns the native map object mapstraction is using
 */
Mapstraction.prototype.getMap = function() {
    // FIXME in an ideal world this shouldn't exist right?
    return this.maps[this.api];
};


//////////////////////////////
//
//   LatLonPoint
//
/////////////////////////////

/**
 * LatLonPoint is a point containing a latitude and longitude with helper methods
 * @param {double} lat is the latitude
 * @param {double} lon is the longitude
 * @returns a new LatLonPoint
 * @type LatLonPoint
 */
function LatLonPoint(lat, lon) {
    // TODO error if undefined?
    //  if (lat == undefined) alert('undefined lat');
    //  if (lon == undefined) alert('undefined lon');
    this.lat = lat;
    this.lon = lon;
    this.lng = lon; // lets be lon/lng agnostic
}

/**
 * toYahoo returns a Y! maps point
 * @returns a YGeoPoint
 */
LatLonPoint.prototype.toYahoo = function() {
    return new YGeoPoint(this.lat,this.lon);
};

/**
 * toGoogle returns a Google maps point
 * @returns a GLatLng
 */
LatLonPoint.prototype.toGoogle = function() {
    return new GLatLng(this.lat,this.lon);
};

/**
 * Sets a point based on a google point
 * @param {Object} googlePoint
 */
LatLonPoint.prototype.fromGoogle = function(googlePoint)
{
	this.lat = googlePoint.lat();
	this.lon = googlePoint.lng();
};

/**
 * toOpenLayers returns an OpenLayers point
 * Does a conversion from Latitude/Longitude to projected coordinates
 * @returns a OpenLayers. LonLat
 */
LatLonPoint.prototype.toOpenLayers = function() {
    var ollon = this.lon * 20037508.34 / 180;
    var ollat = Math.log(Math.tan((90 + this.lat) * Math.PI / 360)) / (Math.PI / 180);
    ollat = ollat * 20037508.34 / 180;
    //console.log("COORD: " + this.lat + ', ' + this.lon + " OL: " + ollat + ', ' +ollon);
    return new OpenLayers.LonLat(ollon, ollat);
};

/**
 * fromOpenLayers converts an OpenLayers point to Mapstraction LatLonPoint
 * Does a conversion from projectect coordinates to Latitude/Longitude
 * @returns a LatLonPoint
 */
LatLonPoint.prototype.fromOpenLayers = function() {
    var lon = (this.lon / 20037508.34) * 180;
    var lat = (this.lat / 20037508.34) * 180;

    lat = 180/Math.PI * (2 * Math.atan(Math.exp(lat * Math.PI / 180)) - Math.PI / 2);

    this.lon = lon;
    this.lat = lat;
};

/**
 * toMicrosoft returns a VE maps point
 * @returns a VELatLong
 */
LatLonPoint.prototype.toMicrosoft = function() {
    return new VELatLong(this.lat,this.lon);
};

/**
 * toMultiMap returns a MultiMap point
 * @returns a MMLatLon
 */
LatLonPoint.prototype.toMultiMap = function() {
    return new MMLatLon(this.lat, this.lon);
};

/**
 * toMapQuest returns a MapQuest point
 * @returns a MQLatLng
 */
LatLonPoint.prototype.toMapQuest = function() {
    return new MQA.LatLng(this.lat, this.lon);
};

/**
 * toFreeEarth returns a FreeEarth point
 * @returns a FE.LatLng
 */
LatLonPoint.prototype.toFreeEarth = function() {
    return new FE.LatLng(this.lat,this.lon);
};

/**
 * toMap24 returns a Map24 point
 * @returns a Map24.Point
 */
LatLonPoint.prototype.toMap24 = function() {
    return new Map24.Point (this.lon,this.lat);
};

/**
 * toOpenSpace returns an OpenSpace point
 * @returns a OpenSpace.MapPoint
 */
LatLonPoint.prototype.toOpenSpace = function() {
    var lonlat = new OpenLayers.LonLat(this.lon, this.lat);
    // need to convert to UK national grid
    var gridProjection = new OpenSpace.GridProjection();
    return gridProjection.getMapPointFromLonLat(lonlat); // on OpenSpace.MapPoint
};

/**
 * fromOpenSpace given an OpenSpace.MapPoint returns a new Mapstraction LatLonPoint
 * @param {OpenSpace.MapPoint} point to convert
 */
LatLonPoint.prototype.fromOpenSpace = function(osPoint) {
    var gridProjection = new OpenSpace.GridProjection();
    olpt = gridProjection.getLonLatFromMapPoint(osPoint); // an OpenLayers.LonLat
    this.lon = olpt.lon;
    this.lat = olpt.lat;
};

/**
 * toViaMichelin returns a ViaMichelin point
 * @returns a VMPoint
 */
LatLonPoint.prototype.toViaMichelin = function() {
    return new VMLonLat (this.lon, this.lat);
};

/**
 * toString returns a string represntation of a point
 * @returns a string like '51.23, -0.123'
 * @type String
 */
LatLonPoint.prototype.toString = function() {
    return this.lat + ', ' + this.lon;
};

/**
 * distance returns the distance in kilometers between two points
 * @param {LatLonPoint} otherPoint The other point to measure the distance from to this one
 * @returns the distance between the points in kilometers
 * @type double
 */
LatLonPoint.prototype.distance = function(otherPoint) {
	// Uses Haversine formula from http://www.movable-type.co.uk
	var rads = Math.PI / 180;
	var diffLat = (this.lat-otherPoint.lat) * rads;
	var diffLon = (this.lon-otherPoint.lon) * rads; 
	var a = Math.sin(diffLat / 2) * Math.sin(diffLat / 2) +
        Math.cos(this.lat*rads) * Math.cos(otherPoint.lat*rads) * 
        Math.sin(diffLon/2) * Math.sin(diffLon/2); 
	return 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)) * 6371; // Earth's mean radius in km
};

/**
 * equals tests if this point is the same as some other one
 * @param {LatLonPoint} otherPoint The other point to test with
 * @returns true or false
 * @type boolean
 */
LatLonPoint.prototype.equals = function(otherPoint) {
    return this.lat == otherPoint.lat && this.lon == otherPoint.lon;
};

/**
 * Returns latitude conversion based on current projection
 * @returns {Float} conversion
 */
LatLonPoint.prototype.latConv = function()
{
	return this.distance(new LatLonPoint(this.lat + 0.1, this.lon))*10;
}

/**
 * Returns longitude conversion based on current projection
 * @returns {Float} conversion
 */
LatLonPoint.prototype.lonConv = function()
{
      return this.distance(new LatLonPoint(this.lat, this.lon + 0.1))*10;
}



//////////////////////////
//
//  BoundingBox
//
//////////////////////////

/**
 * BoundingBox creates a new bounding box object
 * @param {double} swlat the latitude of the south-west point
 * @param {double} swlon the longitude of the south-west point
 * @param {double} nelat the latitude of the north-east point
 * @param {double} nelon the longitude of the north-east point
 * @returns a new BoundingBox
 * @type BoundingBox
 * @constructor
 * @classDescription BoundingBox
 */
function BoundingBox(swlat, swlon, nelat, nelon) {
    //FIXME throw error if box bigger than world
    //alert('new bbox ' + swlat + ',' +  swlon + ',' +  nelat + ',' + nelon);
    this.sw = new LatLonPoint(swlat, swlon);
    this.ne = new LatLonPoint(nelat, nelon);
}

/**
 * getSouthWest returns a LatLonPoint of the south-west point of the bounding box
 * @returns the south-west point of the bounding box
 * @type LatLonPoint
 */
BoundingBox.prototype.getSouthWest = function() {
    return this.sw;
};

/**
 * getNorthEast returns a LatLonPoint of the north-east point of the bounding box
 * @returns the north-east point of the bounding box
 * @type LatLonPoint
 */
BoundingBox.prototype.getNorthEast = function() {
    return this.ne;
};

/**
 * isEmpty finds if this bounding box has zero area
 * @returns whether the north-east and south-west points of the bounding box are the same point
 * @type boolean
 */
BoundingBox.prototype.isEmpty = function() {
    return this.ne == this.sw; // is this right? FIXME
};

/**
 * contains finds whether a given point is within a bounding box
 * @param {LatLonPoint} point the point to test with
 * @returns whether point is within this bounding box
 * @type boolean
 */
BoundingBox.prototype.contains = function(point){
    return point.lat >= this.sw.lat && point.lat <= this.ne.lat && point.lon >= this.sw.lon && point.lon <= this.ne.lon;
};

/**
 * toSpan returns a LatLonPoint with the lat and lon as the height and width of the bounding box
 * @returns a LatLonPoint containing the height and width of this bounding box
 * @type LatLonPoint
 */
BoundingBox.prototype.toSpan = function() {
    return new LatLonPoint( Math.abs(this.sw.lat - this.ne.lat), Math.abs(this.sw.lon - this.ne.lon) );
};

/**
 * extend extends the bounding box to include the new point
 */
BoundingBox.prototype.extend = function(point) {
    if(this.sw.lat > point.lat) {
        this.sw.lat = point.lat;
    }
    if(this.sw.lon > point.lon) {
        this.sw.lon = point.lon;
    }
    if(this.ne.lat < point.lat) {
        this.ne.lat = point.lat;
    }
    if(this.ne.lon < point.lon) {
        this.ne.lon = point.lon;
    }
    return;
};

//////////////////////////////
//
//  Marker
//
///////////////////////////////

/**
 * Marker create's a new marker pin
 * @param {LatLonPoint} point the point on the map where the marker should go
 * @constructor
 */
function Marker(point) {
    this.location = point;
    this.onmap = false;
    this.proprietary_marker = false;
    this.attributes = [];
    this.pinID = "mspin-"+new Date().getTime()+'-'+(Math.floor(Math.random()*Math.pow(2,16)));
}

Marker.prototype.setChild = function(some_proprietary_marker) {
    this.proprietary_marker = some_proprietary_marker;
    this.onmap = true;
};

Marker.prototype.setLabel = function(labelText) {
    this.labelText = labelText;
};

/**
 * addData conviniently set a hash of options on a marker
 */
Marker.prototype.addData = function(options){
    for(var sOptKey in options) {
        switch(sOptKey) {
            case 'label':
                this.setLabel(options.label);
                break;
            case 'infoBubble':
                this.setInfoBubble(options.infoBubble);
                break;
            case 'icon':
                if(options.iconSize && options.iconAnchor) {
                    this.setIcon(options.icon, options.iconSize, options.iconAnchor);
                }
                else if(options.iconSize) {
                    this.setIcon(options.icon, options.iconSize);
                }
                else {
                    this.setIcon(options.icon);
                }
                break;
            case 'iconShadow':
                if(options.iconShadowSize)
                    this.setShadowIcon(options.iconShadow, new Array(options.iconShadowSize[0], options.iconShadowSize[1]));
                else
                    this.setIcon(options.iconShadow);
                break;
            case 'infoDiv':
                this.setInfoDiv(options.infoDiv[0],options.infoDiv[1]);
                break;
            case 'draggable':
                this.setDraggable(options.draggable);
                break;
            case 'hover':
                this.setHover(options.hover);
            // no break statement here intentionally
            case 'hoverIcon':
                this.setHoverIcon(options.hoverIcon);
                break;
            case 'openBubble':
                this.openBubble();
                break;
            case 'groupName':
                this.setGroupName(options.groupName);
                break;
            default:
                // don't have a specific action for this bit of
                // data so set a named attribute
                this.setAttribute(sOptKey, options[sOptKey]);
                break;
        }
    }
};

/**
 * setInfoBubble sets the html/text content for a bubble popup for a marker
 * @param {String} infoBubble the html/text you want displayed
 */
Marker.prototype.setInfoBubble = function(infoBubble) {
    this.infoBubble = infoBubble;
};

/**
 * setInfoDiv sets the text and the id of the div element where to the information
 *  useful for putting information in a div outside of the map
 * @param {String} infoDiv the html/text you want displayed
 * @param {String} div the element id to use for displaying the text/html
 */
Marker.prototype.setInfoDiv = function(infoDiv,div){
    this.infoDiv = infoDiv;
    this.div = div;
};

/**
 * setIcon sets the icon for a marker
 * @param {String} iconUrl The URL of the image you want to be the icon
 */
Marker.prototype.setIcon = function(iconUrl, iconSize, iconAnchor) {
    this.iconUrl = iconUrl;
    if(iconSize) {
        this.iconSize = iconSize;
    }
    if(iconAnchor) {
        this.iconAnchor = iconAnchor;
    }
};

/**
 * setIconSize sets the size of the icon for a marker
 * @param {String} iconSize The array size in pixels of the marker image
 */
Marker.prototype.setIconSize = function(iconSize){
    if(iconSize) {
        this.iconSize = iconSize;
    }
};

/**
 * setIconAnchor sets the anchor point for a marker
 * @param {String} iconAnchor The array offset of the anchor point
 */
Marker.prototype.setIconAnchor = function(iconAnchor){
    if(iconAnchor) {
        this.iconAnchor = iconAnchor;
    }
};

/**
 * setShadowIcon sets the icon for a marker
 * @param {String} iconUrl The URL of the image you want to be the icon
 */
Marker.prototype.setShadowIcon = function(iconShadowUrl, iconShadowSize){
    this.iconShadowUrl = iconShadowUrl;
    if(iconShadowSize) {
        this.iconShadowSize = iconShadowSize;
    }
};

Marker.prototype.setHoverIcon = function(hoverIconUrl){
    this.hoverIconUrl = hoverIconUrl;
};

/**
 * setDraggable sets the draggable state of the marker
 * @param {Bool} draggable set to true if marker should be draggable by the user
 */
Marker.prototype.setDraggable = function(draggable) {
    this.draggable = draggable;
};

/**
 * setHover sets that the marker info is displayed on hover
 * @param {Bool} hover set to true if marker should display info on hover
 */
Marker.prototype.setHover = function(hover) {
    this.hover = hover;
};

/**
 * Markers are grouped up by this name. declutterGroup makes use of this.
 */
Marker.prototype.setGroupName = function(sGrpName) {
    this.groupName = sGrpName;
};



/**
 * toYahoo returns a Yahoo Maps compatible marker pin
 * @returns a Yahoo Maps compatible marker
 */
Marker.prototype.toYahoo = function() {
    var ymarker;
    var size;
    if(this.iconSize) {
        size = new YSize(this.iconSize[0], this.iconSize[1]);
    }
    if(this.iconUrl) {
        if(this.iconSize)
            ymarker = new YMarker(this.location.toYahoo (),new YImage(this.iconUrl, size));
        else
            ymarker = new YMarker(this.location.toYahoo (),new YImage(this.iconUrl));
    }
    else {
        if(this.iconSize)
            ymarker = new YMarker(this.location.toYahoo(),null,size);
        else
            ymarker = new YMarker(this.location.toYahoo());
    }

    if(this.labelText) {
        ymarker.addLabel(this.labelText);
    }

    if(this.infoBubble) {
        var theInfo = this.infoBubble;
        var event_action;
        if(this.hover) {
            event_action = EventsList.MouseOver;
        }
        else {
            event_action = EventsList.MouseClick;
        }
        YEvent.Capture(ymarker, event_action, function() {
            ymarker.openSmartWindow(theInfo);
        });

    }

    if(this.infoDiv) {
        var theInfo = this.infoDiv;
        var div = this.div;
        var event_div;
        if(this.hover) {
            event_action = EventsList.MouseOver;
        }
        else {
            event_action = EventsList.MouseClick;
        }
        YEvent.Capture(ymarker, event_action, function() {
            document.getElementById(div).innerHTML = theInfo;
        });
    }

    return ymarker;
};

/**
 * toGoogle returns a Google Maps compatible marker pin
 * @returns Google Maps compatible marker
 */
Marker.prototype.toGoogle = function() {
    var options = {};
    if(this.labelText){
        options.title =  this.labelText;
    }
    if(this.iconUrl){
        var icon = new GIcon(G_DEFAULT_ICON, this.iconUrl);
        icon.printImage = icon.mozPrintImage = icon.image;
        if(this.iconSize) {
            icon.iconSize = new GSize(this.iconSize[0], this.iconSize[1]);
            var anchor;
            if(this.iconAnchor) {
                anchor = new GPoint(this.iconAnchor[0], this.iconAnchor[1]);
            }
            else {
                // FIXME: hard-coding the anchor point
                anchor = new GPoint(this.iconSize[0]/2, this.iconSize[1]/2);
            }
            icon.iconAnchor = anchor;
        }
        if(this.iconShadowUrl) {
            icon.shadow = this.iconShadowUrl;
            if(this.iconShadowSize) {
                icon.shadowSize = new GSize(this.iconShadowSize[0], this.iconShadowSize[1]);
            }
        }
        options.icon = icon;
    }
    if(this.draggable){
        options.draggable = this.draggable;
    }
    var gmarker = new GMarker( this.location.toGoogle(),options);

    if(this.infoBubble){
        var theInfo = this.infoBubble;
        var event_action;
        if(this.hover) {
            event_action = "mouseover";
        }
        else {
            event_action = "click";
        }
        GEvent.addListener(gmarker, event_action, function() {
            gmarker.openInfoWindowHtml(theInfo, {
                maxWidth: 100
            });
        });
    }

    if(this.hoverIconUrl){
        GEvent.addListener(gmarker, "mouseover", function() {
            gmarker.setImage(this.hoverIconUrl);
        });
        GEvent.addListener(gmarker, "mouseout", function() {
            gmarker.setImage(this.iconUrl);
        });
    }

    if(this.infoDiv){
        var theInfo = this.infoDiv;
        var div = this.div;
        var event_action;
        if(this.hover) {
            event_action = "mouseover";
        }
        else {
            event_action = "click";
        }
        GEvent.addListener(gmarker, event_action, function() {
            document.getElementById(div).innerHTML = theInfo;
        });
    }

    return gmarker;
};

/**
 * toOpenLayers returns an OpenLayers compatible marker pin
 * @returns OpenLayers compatible marker
 */
Marker.prototype.toOpenLayers = function() {
    var size, anchor, icon;
    if(this.iconSize) {
        size = new OpenLayers.Size(this.iconSize[0], this.iconSize[1]);
    }
    else {
        size = new OpenLayers.Size(21,25);
    }

    if(this.iconAnchor) {
        anchor = new OpenLayers.Pixel(this.iconAnchor[0], this.iconAnchor[1]);
    }
    else {
        // FIXME: hard-coding the anchor point
        anchor = new OpenLayers.Pixel(-(size.w/2), -size.h);
    }

    if(this.iconUrl) {
        icon = new OpenLayers.Icon(this.iconUrl, size, anchor);
    }
    else {
        icon = new OpenLayers.Icon('http://openlayers.org/dev/img/marker-gold.png', size, anchor);
    }
    var marker = new OpenLayers.Marker(this.location.toOpenLayers(), icon);

    if(this.infoBubble) {
        var popup = new OpenLayers.Popup(null,
            this.location.toOpenLayers(),
            new OpenLayers.Size(100,100),
            this.infoBubble,
            true);
        popup.autoSize = true;
        var theMap = this.map;
        if(this.hover) {
            marker.events.register("mouseover", marker, function(event) {
                theMap.addPopup(popup);
                popup.show();
            });
            marker.events.register("mouseout", marker, function(event) {
                popup.hide();
                theMap.removePopup(popup);
            });
        }
        else {
            var shown = false;
            marker.events.register("mousedown", marker, function(event) {
                if (shown) {
                    popup.hide();
                    theMap.removePopup(popup);
                    shown = false;
                } else {
                    theMap.addPopup(popup);
                    popup.show();
                    shown = true;
                }
            });
        }
    }

    if(this.hoverIconUrl) {
    // TODO
    }

    if(this.infoDiv){
    // TODO
    }


    return marker;
};

/**
 * toOpenSpace returns an OpenSpace compatible marker pin
 * @returns OpenSpace compatible marker
 */
Marker.prototype.toOpenSpace = function() {
    var size, anchor, icon;
    if(this.iconSize) {
        size = new OpenLayers.Size(this.iconSize[0], this.iconSize[1]);
    }
    else {
        size = new OpenLayers.Size(20,25);
    }

    if(this.iconAnchor) {
        anchor = new OpenLayers.Pixel(this.iconAnchor[0], this.iconAnchor[1]);
    }
    else {
        // FIXME: hard-coding the anchor point
        anchor = new OpenLayers.Pixel(-(size.w/2), -size.h);
    }

    if(this.iconUrl) {
        icon = new OpenSpace.Icon(this.iconUrl, size, anchor);
    }
    else { // leave at default OpenSpace icon
    }

    //  This requires an OpenLayers specific hack, doesn't work when not including OpenLayers.js
    // if (this.labelText) {
    //   var marker = new OpenLayers.Marker.Label(this.location.toOpenSpace(), icon, this.labelText, {mouseOver:true,tooltipsFormat:true});
    // }
    // else {
    var marker = new OpenLayers.Marker(this.location.toOpenSpace(), icon);
    // }
    return marker;
};

/**
 * toMicrosoft returns a MSFT VE compatible marker pin
 * @returns MSFT VE compatible marker
 */
Marker.prototype.toMicrosoft = function() {
    var pin = new VEPushpin(this.pinID,this.location.toMicrosoft(),
        this.iconUrl,this.labelText,this.infoBubble);
    return pin;
};

/**
 * toMap24 returns a Map24 Location
 * @returns Map24 Location
 */
Marker.prototype.toMap24 = function() {

    var ops = {};
    ops.Longitude = this.location.lon*60;
    ops.Latitude = this.location.lat*60;
    if(this.infoBubble) {
        // not sure how map24 differentiates between tooltips and
        // info bubble content
        ops.TooltipContent =  this.infoBubble;
    }

    if(this.labelText) {
    // ????
    }

    ops.LogoURL = this.iconUrl; // ? this.iconUrl : "http://www.free-map.org.uk/images/marker.png";
    ops.SymbolId = 20947;

    ops.TooltipLayout = Map24.MapObject.LAYOUT_BUBBLE;

    if(this.hover) {
        ops.TooltipOpen = "OnMouseOver";
    //        ops.TooltipClose = "OnMouseOut";
    } else {
        ops.TooltipOpen = "OnClick";
    //        ops.TooltipClose = "OnMouseOut";
    }


    var m24Location = new Map24.Location(ops);
    return m24Location;
};

/**
 * toMultiMap returns a MultiMap compatible marker pin
 * @returns MultiMap compatible marker
 */
Marker.prototype.toMultiMap = function() {
    //prepare our markeroptions
    var mmmarkeropts = {};

    if(this.iconUrl) {
        mmmarkeropts.icon = new MMIcon(this.iconUrl);
        if(this.iconSize) {
            mmmarkeropts.icon.iconSize = new MMDimensions(this.iconSize[0], this.iconSize[1]);
        }
        else {
        //mmmarkeropts.icon.iconSize = new MMDimensions(32, 32); //how to get this?
        }

        if(this.iconAnchor) {
            mmmarkeropts.icon.iconAnchor = new MMPoint(this.iconAnchor[0], this.iconAnchor[1]);
        }

        if(this.groupName) {
            mmmarkeropts.icon.groupName = this.groupName;
        }
    }

    if(this.labelText) {
        mmmarkeropts.label = this.labelText;
    }


    var mmmarker = new MMMarkerOverlay( this.location.toMultiMap(), mmmarkeropts );

    if(this.infoBubble) {
        mmmarker.setInfoBoxContent(this.infoBubble);
    }

    if(this.infoDiv) { }

    for (var key in this.attributes) {
        mmmarker.setAttribute(key, this.attributes[key]);
    }

    return mmmarker;
};

/**
 * toMapQuest returns a MapQuest compatible marker pin
 * @returns MapQuest compatible marker
 */
Marker.prototype.toMapQuest = function() {

    var mqmarker = new MQA.Poi( this.location.toMapQuest() );

    if(this.iconUrl){
        var mqicon = new MQA.MapIcon();
        mqicon.setImage(this.iconUrl,32,32,true,false);
        // TODO: Finish MapQuest icon params - icon file location, width, height, recalc infowindow offset, is it a PNG image?
        mqmarker.setIcon(mqicon);
    // mqmarker.setLabel('Hola!');
    }

    if(this.labelText) {
        mqmarker.setInfoTitleHTML( this.labelText );
    }

    if(this.infoBubble) {
        mqmarker.setInfoContentHTML( this.infoBubble );
    }

    if(this.infoDiv){
        var theInfo = this.infoDiv;
        var div = this.div;
        MQA.EventManager.addListener(mqmarker, "click", function() {
            document.getElementById(div).innerHTML = theInfo;
        });
    }

    return mqmarker;
};

/**
 * toFreeEarth returns a FreeEarth compatible marker pin
 * @returns FreeEarth compatible marker
 */
Marker.prototype.toFreeEarth = function() {
    var feicon;

    if (this.iconUrl) {
        feicon = new FE.Icon(this.iconUrl);
    } else {
        feicon = new FE.Icon("http://freeearth.poly9.com/images/bullmarker.png");
    }
    var femarker = new FE.Pushpin( this.location.toFreeEarth(), feicon);

    if(this.infoBubble) {
        var theBubble = this.infoBubble;
        FE.Event.addListener(femarker, 'click', function() {
            femarker.openInfoWindowHtml( theBubble, 200, 100 );
        } );
    }

    if(this.infoDiv) {
        var theInfo = this.infoDiv;
        var div = this.div;
        FE.Event.addListener(femarker, 'click', function() {
            document.getElementById(div).innerHTML = theInfo;
        });
    }

    return femarker;
};

/**
 * toViaMichelin returns a ViaMichelin compatible marker pin
 * @returns ViaMichelin compatible marker
 */
Marker.prototype.toViaMichelin = function() {
    var vmicon = null;
    if (this.iconUrl) {
        if(this.iconSize)
            vmicon = new VMIcon(this.iconUrl, this.iconSize[0], this.iconSize[1]);
        else
            vmicon = new VMIcon(this.iconUrl);
    }
    var vmmarker = new VMIconLayer( this.location.toViaMichelin(), vmicon, this.infoBubble);
    return vmmarker;
};

/**
 * setAttribute: set an arbitrary key/value pair on a marker
 * @arg(String) key
 * @arg value
 */
Marker.prototype.setAttribute = function(key,value) {
    this.attributes[key] = value;
};

/**
 * getAttribute: gets the value of "key"
 * @arg(String) key
 * @returns value
 */
Marker.prototype.getAttribute = function(key) {
    return this.attributes[key];
};



/**
 * openBubble opens the infoBubble
 */
Marker.prototype.openBubble = function() {
    if(this.mapstraction.loaded[this.api] === false) {
        var my_marker = this;
        this.mapstraction.onload[this.api].push( function() {
            my_marker.openBubble();
        } );
        return;
    }

    if( this.api) {
        switch (this.api) {
            case 'yahoo':
                var ypin = this.proprietary_marker;
                ypin.openSmartWindow(this.infoBubble);
                break;
            case 'google':
            case 'openstreetmap':
                var gpin = this.proprietary_marker;
                gpin.openInfoWindowHtml(this.infoBubble);
                break;
            case 'microsoft':
                var pin = this.proprietary_marker;
                // bloody microsoft -- this is broken
                var el = $m(this.pinID + "_" + this.maps[this.api].GUID).onmouseover;
                setTimeout(el, 1000); // wait a second in case the map is booting as it cancels the event
                break;
            case 'multimap':
                this.proprietary_marker.openInfoBox();
                break;
            case 'mapquest':
                // MapQuest hack to work around bug when opening marker
                this.proprietary_marker.setRolloverEnabled(false);
                this.proprietary_marker.showInfoWindow();
                this.proprietary_marker.setRolloverEnabled(true);
                break;
        }
    } else {
        if(this.debug) {
            alert('You need to add the marker before opening it');
        }
    }
};

/**
 * closeBubble closes the infoBubble
 */
Marker.prototype.closeBubble = function() {
   if(this.mapstraction.loaded[this.api] === false) {
       var my_marker = this;
       this.mapstraction.onload[this.api].push( function() {
           my_marker.closeBubble();
       } );
       return;
   }

   if( this.api) {
       switch (this.api) {
           case 'yahoo':
               var ypin = this.proprietary_marker;
               ypin.closeSmartWindow();
               break;
           case 'google':
           case 'openstreetmap':
               var gpin = this.proprietary_marker;
               gpin.closeInfoWindow();
               break;
           case 'microsoft':
               // The following works with v6.2, but need to first update way Mapstraction adds MS markers
               var pin = this.proprietary_marker;
                               this.map.HideInfoBox();
                               break;
           case 'multimap':
               //closeInfoBox?
               break;
           case 'mapquest':
               // ???
               break;
       }
   } else {
       if(this.debug) {

       }
   }
};

/**
 * hide the marker
 */
Marker.prototype.hide = function() {
    if (this.api) {
        switch (this.api) {
            case 'google':
            case 'openstreetmap':
                this.proprietary_marker.hide();
                break;
            case 'openlayers':
            case 'openspace':
                this.proprietary_marker.display(false);
                break;
            case 'yahoo':
                this.proprietary_marker.hide();
                break;
            case 'map24':
                this.proprietary_marker.hide();
                break;
            case 'multimap':
                this.proprietary_marker.setVisibility(false);
                break;
            case 'mapquest':
                this.proprietary_marker.setVisible(false);
                break;
            case 'viamichelin': // TODO
            default:
                if(this.debug) {
                    alert(this.api + "not supported by Marker.hide");
                }
        }
    }
};

/**
 * show the marker
 */
Marker.prototype.show = function() {
    if (this.api) {
        switch (this.api) {
            case 'google':
            case 'openstreetmap':
                this.proprietary_marker.show();
                break;
            case 'openlayers':
            case 'openspace' :
                this.proprietary_marker.display(true);
                break;
            case 'map24':
                this.proprietary_marker.show();
                break;
            case 'yahoo':
                this.proprietary_marker.unhide();
                break;
            case 'multimap':
                this.proprietary_marker.setVisibility(true);
                break;
            case 'mapquest':
                this.proprietary_marker.setVisible(true);
                break;
            case 'viamichelin': // TODO
            default:
                if(this.debug) {
                    alert(this.api + "not supported by Marker.show");
                }
        }
    }
};

/**
 * Adds event listener to marker
 * Currently only implemented in Google
 * @param {String} event
 * @param {Function} callback
 * @returns {Object} handler
 */
Marker.prototype.addListener = function(event, callback) {
	if(this.mapstraction.loaded[this.api] === false) {
		var my_marker = this;
		this.mapstraction.onload[this.api].push( function() { my_marker.addListener(); } );
		return;
	}

	if( this.api) {
		switch (this.api) {
			case 'google':
			case 'openstreetmap':
				return GEvent.addListener(this.proprietary_marker, event, callback);
				break;
			default:
				if(this.debug) {
					alert(api + ' not supported by Marker.addListener');
				}
				break;
		}
	} else {
		if(this.debug) {
			alert('You need to add the marker before adding an event to it');
		}
	}
};

/**
 * Removes event listener from marker
 * Currently only implemented in Google
 * @param {string} event
 */
Marker.prototype.removeListener = function(event) {
	if(this.mapstraction.loaded[this.api] === false) {
		var my_marker = this;
		this.mapstraction.onload[this.api].push( function() { my_marker.removeListener(); } );
		return;
	}

	if( this.api) {
		switch (this.api) {
			case 'google':
			case 'openstreetmap':
				GEvent.clearListeners(this.proprietary_marker, event);
				break;
			default:
				if(this.debug) {
					alert(api + ' not supported by Marker.removeListener');
				}
				break;
		}
	} else {
		if(this.debug) {
			alert('You need to add the marker before adding an event to it');
		}
	}
};

/**
 * Updates marker details from proprietary_marker
 * Currently only implemented in Google
 */
Marker.prototype.update = function() {
	if( this.api) {
		switch (this.api) {
			case 'google':
			case 'openstreetmap':
				point = new LatLonPoint();
				point.fromGoogle(this.proprietary_marker.getPoint());
				this.location = point;
				break;
			default:
				if(this.debug) {
					alert(api + ' not supported by Marker.updateLocation');
				}
				break;
		}
	} else {
		if(this.debug) {
			alert('You need to add the marker before updating its location');
		}
	}
};

///////////////
// Polyline ///
///////////////


function Polyline(points) {
    this.points = points;
    this.attributes = [];
    this.onmap = false;
    this.proprietary_polyline = false;
    this.pllID = "mspll-"+new Date().getTime()+'-'+(Math.floor(Math.random()*Math.pow(2,16)));
}

/**
 * addData conviniently set a hash of options on a polyline
 */
Polyline.prototype.addData = function(options){
    for(var sOpt in options) {
        switch(sOpt) {
            case 'color':
                this.setColor(options.color);
                break;
            case 'width':
                this.setWidth(options.width);
                break;
            case 'opacity':
                this.setOpacity(options.opacity);
                break;
            case 'closed':
                this.setClosed(options.closed);
                break;
            case 'fillColor':
                this.setFillColor(options.fillColor);
                break;
            default:
                this.setAttribute(sOpt, options[sOpt]);
                break;
        }
    }
};

Polyline.prototype.setChild = function(some_proprietary_polyline) {
    this.proprietary_polyline = some_proprietary_polyline;
    this.onmap = true;
};

/**
 * in the form: #RRGGBB
 * Note map24 insists on upper case, so we convert it.
 */
Polyline.prototype.setColor = function(color){
    this.color = (color.length==7 && color[0]=="#") ? color.toUpperCase() : color;
};

/**
 * Stroke width of the polyline
 * @param {Integer} width
 */
Polyline.prototype.setWidth = function(width){
    this.width = width;
};

/**
 * A float between 0.0 and 1.0
 * @param {Float} opacity
 */
Polyline.prototype.setOpacity = function(opacity){
    this.opacity = opacity;
};

/**
 * Marks the polyline as a closed polygon
 * @param {Boolean} bClosed
 */
Polyline.prototype.setClosed = function(bClosed){
    this.closed = bClosed;
};

/**
 * Fill color for a closed polyline as HTML color value e.g. #RRGGBB
 * @param {String} sFillColor HTML color value #RRGGBB
 */
Polyline.prototype.setFillColor = function(sFillColor) {
    this.fillColor = sFillColor;
};

/**
 * toOpenSpace returns an OpenLayers polyline/polygon
 * @returns a LineString/LinearRing
 */
Polyline.prototype.toOpenSpace = function() {
    var ospolyline;
    var ospoints = [];
    for (var i = 0, length = this.points.length ; i< length; i++){
        // convert each point to OpenSpace.MapPoint
        var ospoint = this.points[i].toOpenSpace();
        var olgpoint = new OpenLayers.Geometry.Point(ospoint.getEasting(), ospoint.getNorthing());
        ospoints.push(olgpoint);
    }
    if (this.closed) {
        ospolyline = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.LinearRing(ospoints), null, {
            fillColor: this.color,
            strokeColor: this.color,
            strokeOpacity: this.opacity,
            fillOpacity: this.opacity,
            strokeWidth: this.width
        });
    }
    else {
        ospolyline = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.LineString(ospoints), null, {
            fillColor: 0,
            strokeColor: this.color,
            strokeOpacity: this.opacity,
            fillOpacity: 0,
            strokeWidth: this.width
        });
    }
    return ospolyline;
};

/**
 * toYahoo returns a Yahoo polyline
 * @returns a YPolyline
 */
Polyline.prototype.toYahoo = function() {
    var ypolyline;
    var ypoints = [];
    for (var i = 0, length = this.points.length ; i< length; i++){
        ypoints.push(this.points[i].toYahoo());
    }
    // YPolygon does not exist :-(
    ypolyline = new YPolyline(ypoints,this.color,this.width,this.opacity);
    return ypolyline;
};

/**
 * toGoogle returns a Google polyline/polygon
 * @returns a GPolyline/GPolygon
 */
Polyline.prototype.toGoogle = function() {
    var gpoints = [];
    for (var i = 0,  length = this.points.length ; i< length; i++){
        gpoints.push(this.points[i].toGoogle());
    }
    if (this.closed	|| gpoints[0].equals(gpoints[length-1])) {
        var gpoly = new GPolygon(gpoints, this.color, this.width, this.opacity, this.fillColor || "#5462E3", this.opacity || "0.3");
    } else {
        var gpoly = new GPolyline(gpoints, this.color, this.width, this.opacity);
    }
    return gpoly;
};

/**
 * toMap24 returns a Map24 polyline/polygon
 * @returns a Polyline/Polygon
 */
Polyline.prototype.toMap24 = function() {
    var m24poly;
    var m24longs = "";
    var m24lats = "";
    for (var i=0, length = this.points.length; i<length; i++) {
        if(i) {
            m24longs += "|";
            m24lats += "|";
        }
        m24longs += (this.points[i].lon*60);
        m24lats += (this.points[i].lat*60);
    }
    if (this.closed	|| this.points[0].equals(this.points[length-1])) {
        m24poly = new Map24.Polygon({
            Longitudes: m24longs,
            Latitudes: m24lats,
            FillColor: [this.color || "grey", this.opacity || "0.5"],
            BorderColor: this.color
        });
    } else {
        m24poly = new Map24.Polyline({
            Longitudes: m24longs,
            Latitudes: m24lats,
            Color: this.color || "black",
            Width: this.width || 3
        });
    }
    return m24poly;
};

/**
 * toMicrosoft returns a Microsoft polyline
 * @returns a VEPolyline
 */
Polyline.prototype.toMicrosoft = function() {
    var mpolyline;
    var mpoints = [];
    for (var i = 0, length = this.points.length ; i< length; i++){
        mpoints.push(this.points[i].toMicrosoft());
    }

    var color;
    var opacity = this.opacity ||1.0;
    if(this.color){
        color = new VEColor(parseInt(this.color.substr(1,2),16),parseInt(this.color.substr(3,2),16),parseInt(this.color.substr(5,2),16), opacity);
    }else{
        color = new VEColor(0,255,0, opacity);
    }

    mpolyline = new VEPolyline(this.pllID,mpoints,color,this.width);
    return mpolyline;
};

/**
 * toMultiMap returns a MultiMap polyline
 * @returns a MMPolyLineOverlay
 */
Polyline.prototype.toMultiMap = function() {
    var mmpolyline;
    var mmpoints = [];
    for (var i = 0, length = this.points.length ; i< length; i++){
        mmpoints.push(this.points[i].toMultiMap());
    }
    mmpolyline = new MMPolyLineOverlay(mmpoints, this.color, this.opacity, this.width, this.closed, this.fillColor);
    return mmpolyline;
};

/**
 * toMapQuest returns a MapQuest polyline/polygon
 * @returns a LineOverlay/PolygonOverlay
 */
Polyline.prototype.toMapQuest = function() {
    if (this.closed	|| this.points[0].equals(this.points[this.points.length-1])) {
        var mqpoly = new MQA.PolygonOverlay();
        mqpoly.setFillColor(this.color || "#E90000");
        mqpoly.setFillColorAlpha(this.opacity || 0.3);
    }
    else {
        var mqpoly = new MQA.LineOverlay();
    }
    mqpoly.setKey("Line");
    mqpoly.setBorderWidth(this.width || 3);
    mqpoly.setColor(this.color || "#E90000");
    mqpoly.setColorAlpha(this.opacity || 0.5);

    var mqpoints = new MQA.LatLngCollection();
    for (var i = 0, length = this.points.length ; i< length; i++){
        mqpoints.add(this.points[i].toMapQuest());
    }
    mqpoly.setShapePoints(mqpoints);
    return mqpoly;
};

/**
 * toFreeEarth returns a FreeEarth polyline
 * @returns a Polyline
 */
Polyline.prototype.toFreeEarth = function() {
    var fepoints = [];

    for (var i = 0, length = this.points.length ; i< length; i++){
        fepoints.push(this.points[i].toFreeEarth());
    }

    var fepolyline = new FE.Polyline(fepoints, this.color || '0xff0000', this.width || 1, this.opacity || 1);

    return fepolyline;
};

/**
 * toOpenLayers returns an OpenLayers polyline/polygon
 * @returns a LineString/LinearRing
 */
Polyline.prototype.toOpenLayers = function() {
    var olpolyline;
    var olpoints = [];
    var ring;
    var style = {
        strokeColor: this.color || "#000000",
        strokeOpacity: this.opacity || 1,
        strokeWidth: this.width || 1,
        fillColor: this.fillColor || "#000000",
        fillOpacity: this.getAttribute('fillOpacity') || 0.2
    };

    //TODO Handle closed attribute

    for (var i = 0, length = this.points.length ; i< length; i++){
        olpoint = this.points[i].toOpenLayers();
        olpoints.push(new OpenLayers.Geometry.Point(olpoint.lon, olpoint.lat));
    }

    if (this.closed) {
        // a closed polygon
        ring = new OpenLayers.Geometry.LinearRing(olpoints);
    } else {
        // a line
        ring = new OpenLayers.Geometry.LineString(olpoints);
    }

    olpolyline = new OpenLayers.Feature.Vector(ring, null, style);

    return olpolyline;
};

/**
 * toViaMichelin returns a ViaMichelin polyline/polygon
 * @returns a VMPolyLine/VMPolygonShape
 */
Polyline.prototype.toViaMichelin = function() {
    var vmpoints = [];
    for (var i = 0, length = this.points.length ; i< length; i++){
        vmpoints.push(this.points[i].toViaMichelin());
    }
    if (this.closed	|| this.points[0].equals(this.points[length-1])) {
        var vmpoly = new VMPolygonShape(vmpoints, this.color, this.width || 5, this.fillColor, this.opacity || 0.2);
    }
    else {
        var vmpoly = new VMPolyLine(vmpoints, this.color, this.width || 5, this.opacity || 0.5);
    }
    return vmpoly;
};

/**
 * setAttribute: set an arbitrary key/value pair on a polyline
 * @arg(String) key
 * @arg value
 */
Polyline.prototype.setAttribute = function(key,value) {
    this.attributes[key] = value;
};

/**
 * getAttribute: gets the value of "key"
 * @arg(String) key
 * @returns value
 */
Polyline.prototype.getAttribute = function(key) {
    return this.attributes[key];
};

/**
 * show: not yet implemented
 */
Polyline.prototype.show = function() {
    switch (this.api) {
        case 'multimap':
            if(!this.onmap) {
                this.map.addOverlay(this.proprietary_polyline);
            }
            break;
        default:
            if(this.debug) {
                alert(api + ' not supported by Polyline.show');
            }
            break;
    }
};

/**
 * hide: not yet implemented
 */
Polyline.prototype.hide = function() {
    switch (this.api) {
        case 'multimap':
            if(this.onmap) {
                this.map.removeOverlay(this.proprietary_polyline);
                this.onmap = false;
            }
            break;
        default:
            if(this.debug) {
                alert(api + ' not supported by Polyline.hide');
            }
            break;
    }
};

/**
 * Simplifies a polyline, averaging and reducing the points
 * @param {Integer} tolerance (1.0 is a good starting point)
 */
Polyline.prototype.simplify = function(tolerance) {
	var reduced = new Array();

	// First point
	reduced[0] = this.points[0];

	var markerPoint = 0;
  var length = this.points.length;
	for (var i = 1; i < length-1; i++)
        if (this.points[i].distance(this.points[markerPoint]) >= tolerance)
		{
			reduced[reduced.length] = this.points[i];
			markerPoint = i;
        }

	// Last point
	reduced[reduced.length] = this.points[this.points.length-1];

	// Revert
	this.points = reduced;
};

// Displays the coordinates of the cursor in the HTML element
//
// @element ID of the HTML element to display the coordinates in
Mapstraction.prototype.mousePosition = function(element) {
    if(this.loaded[this.api] === false) {
        var me = this;
        this.onload[this.api].push( function() {
            me.mousePosition(element);
        } );
        return;
    }
    var locDisp = document.getElementById(element);
    if (locDisp != null) {
        var map = this.maps[this.api];
        switch (this.api) {
            case 'openlayers':
                try {
                    map.events.register('mousemove', map, function (e) {
                        var lonLat = map.getLonLatFromViewPortPx(e.xy);
                        var lon = lonLat.lon * (180.0 / 20037508.34);
                        var lat = lonLat.lat * (180.0 / 20037508.34);
                        lat = (180/Math.PI)*(2*Math.atan(Math.exp(lat*Math.PI/180))-(Math.PI/2));
                        var loc = numFormatFloat(lat,4) + ' / ' + numFormatFloat(lon,4);
                        // numFormatFloat(X,4) simply formats floating point 'X' to 4 dec places
                        locDisp.innerHTML = loc;
                    });
                    locDisp.innerHTML = '0.0000 / 0.0000';
                } catch (x) {
                //alert("Error: " + e);
                }
                break;
            case 'microsoft':
                try {
                    map.AttachEvent('onmousemove', function (e) {
                        var latLon = map.PixelToLatLong(new VEPixel(e.mapX,e.mapY));
                        var loc = numFormatFloat(latLon.Latitude,4)+' / '+numFormatFloat(latLon.Longitude,4);
                        locDisp.innerHTML = loc;
                        if (e.rightMouseButton == false) {
                            element.style.cursor = 'crosshair';
                            return false;
                        } else {
                            return true; // (should disabled drag-panning on right mouse button)
                        }
                    });
                    locDisp.innerHTML = '0.0000 / 0.0000';
                } catch (e) {
                //alert("Error: " + e);
                }
                break;
            case 'google':
                GEvent.addListener(map, 'mousemove', function (point) {
                    var loc = point.lat().toFixed(4) + ' / ' + point.lng().toFixed(4);
                    locDisp.innerHTML = loc;
                });
                locDisp.innerHTML = '0.0000 / 0.0000';
                break;
        }
    }
};

/////////////
/// Route ///
/////////////

/**
 * Enable scroll wheel zooming
 * Currently only supported by Google
 */
Mapstraction.prototype.enableScrollWheelZoom = function() {
	if(this.loaded[this.api] == false)
	{
		myself = this;
		this.onload[this.api].push(function()
		{
			myself.enableScrollWheelZoom();
		});
		return;
	}

	var map = this.maps[this.api];

	switch (this.api)
	{
	    case 'google':
		case 'openstreetmap':
			map.enableContinuousZoom();
			map.enableScrollWheelZoom();
			break;
		default:
			if(this.debug) {
				alert(api + ' not supported by Mapstration.enableScrollWheelZoom');
			}
			break;
	}
};

///////////////
// Polygons  //
///////////////

/**
 * Add a polygon to the map, based on addPolyline and accepts a polyline as the template
 * Currently only implemented in Google
 * @param {object} polygon
 */
 Mapstraction.prototype.addPolygon = function(polygon) {
   if(this.loaded[this.api] == false)
   {
     myself = this;
     this.onload[this.api].push(function()
     {
       myself.addPolygon(polygon);
     });
     return;
   }

   var map = this.maps[this.api];

   switch (this.api)
   {
     case 'google':
     case 'openstreetmap':
     var gpoints = [];

     for (var i = 0; i < polygon.points.length; i++)
     gpoints.push(polygon.points[i].toGoogle());

     gpolygon = new GPolygon(gpoints, polygon.color, 0, polygon.opacity, polygon.color, polygon.opacity);
     polygon.setChild(gpolygon);
     map.addOverlay(gpolygon);
     this.polylines.push(polygon);
     break;
     default:
     if(this.debug) {
       alert(api + ' not supported by Mapstration.addPolygon');
     }
     break;
   }
 };

///////////////
// Radius    //
///////////////

/**
 * Creates a new radius object for drawing circles around a point, does a lot of initial calculation to increase load time
 * @returns a new Radius
 * @type Radius
 * @constructor
 * @classDescription Radius
 * @param {Object} center
 * @param {quality} quality (20 is a good starting point)
 */
function Radius(center, quality) {
	this.center = center;
	var latConv = center.latConv();
	var lonConv = center.lonConv();

	// Create Radian conversion constant
	var rad = Math.PI / 180;
	this.calcs = new Array();

	for(var i = 0; i < 360; i += quality)
		this.calcs.push([Math.cos(i * rad) / latConv, Math.sin(i * rad) / lonConv]);
}

/**
 * Returns polyline of a circle around the point based on new radius
 * @param {Radius} radius
 * @param {Colour} colour
 * @returns {Polyline} Polyline
 */
Radius.prototype.getPolyline = function(radius, colour) {
	var points = Array();

	for(var i = 0; i < this.calcs.length; i++){
		var point = new LatLonPoint(
			this.center.lat + (radius * this.calcs[i][0]),
			this.center.lon + (radius * this.calcs[i][1])
		);
		points.push(point);
	}

	// Add first point
	points.push(points[0]);

	var line = new Polyline(points);
	line.setColor(colour);

	return line;
};

/*
 * Expose mapstraction through mxn namespace
 */
window.mxn = {
    'BoundingBox': BoundingBox,
    'LatLonPoint': LatLonPoint,
    'Mapstraction': Mapstraction,
    'Marker': Marker,
    'Polyline': Polyline,
    'Radius': Radius,

    /*
	 * Expose utility functions to the outside
	 */
    'fn': {
        'milesToKM' : milesToKM,
		'KMToMiles' : KMToMiles,
        'metresToLon': metresToLon,
        'lonToMetres': lonToMetres,
        'loadScript': loadScript
    },

    /**
	 * Allow spillage of classes for backward compatibility with
	 * non-namespaced versions. NOTE: Doesn't expose loose utility
	 * functions.
	 */
    activatePolluteMode: function(){
        if(
            window.BoundingBox ||
            window.LatLonPoint ||
            window.Mapstraction ||
            window.Marker ||
            window.Polyline ||
            window.Radius
            ) {
            alert('Warning: Mapstraction pollute mode naming clash.');
        }
        window['BoundingBox'] = BoundingBox;
        window['LatLonPoint'] = LatLonPoint;
        window['Mapstraction'] = Mapstraction;
        window['Marker'] = Marker;
        window['Polyline'] = Polyline;
        window['Radius'] = Radius;
    }
};

})();
mxn.activatePolluteMode();
