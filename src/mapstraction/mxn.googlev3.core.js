/*
Copyright (c) 2010 Tom Carden, Steve Coast, Mikel Maron, Andrew Turner, Henri Bergius, Rob Moran, Derek Fowler
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 * Neither the name of the Mapstraction nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
mxn.register('googlev3', {	

Mapstraction: {
	
	init: function(element, api){		
		var me = this;
		if ( google && google.maps ){
			// by default add road map and no controls
			var myOptions = {
				disableDefaultUI: true,
				mapTypeId: google.maps.MapTypeId.ROADMAP,
				mapTypeControl: false,
				mapTypeControlOptions: null,
				navigationControl: false,
			        navigationControlOptions: null,
				scrollwheel: false
			};

		    // find controls
		    if (!this.addControlsArgs && loadoptions.addControlsArgs) {
		    	this.addControlsArgs = loadoptions.addControlsArgs;
		    }
		    if (this.addControlsArgs) {
			    if (this.addControlsArgs.zoom) {
			    	myOptions.navigationControl = true;
			    	if (this.addControlsArgs.zoom == 'small') {
			    		myOptions.navigationControlOptions = {style: google.maps.NavigationControlStyle.SMALL};
			    	}
			    	if (this.addControlsArgs.zoom == 'large') {
			    		myOptions.navigationControlOptions = {style: google.maps.NavigationControlStyle.ZOOM_PAN};
			    	}
			    }
			    if (this.addControlsArgs.map_type) {
					myOptions.mapTypeControl = true;
					myOptions.mapTypeControlOptions = {style: google.maps.MapTypeControlStyle.DEFAULT};
			    }
		    }
		
			var map = new google.maps.Map(element, myOptions);
				
			// deal with click
			google.maps.event.addListener(map, 'click', function(location){
				me.click.fire({'location': 
					new mxn.LatLonPoint(location.latLng.lat(),location.latLng.lng())
				});
			});

			// deal with zoom change
			google.maps.event.addListener(map, 'zoom_changed', function(){
				me.changeZoom.fire();
			});
			// deal with map movement
			google.maps.event.addListener(map, 'dragend', function(){
				me.moveendHandler(me);
				me.endPan.fire();
			});
			this.maps[api] = map;
			this.loaded[api] = true;
			me.load.fire();
		}
		else {
			alert(api + ' map script not imported');
		}
	},
	
	applyOptions: function(){
		var map = this.maps[this.api];
		var myOptions = [];
		if (this.options.enableDragging) {
			myOptions.draggable = true;
		} 
		if (this.options.enableScrollWheelZoom){
			myOptions.scrollwheel = true;
		} 
		map.setOptions(myOptions);
	},

	resizeTo: function(width, height){	
		this.currentElement.style.width = width;
		this.currentElement.style.height = height;
		var map = this.maps[this.api];
		google.maps.event.trigger(map,'resize');
  	},

	addControls: function( args ) {
		var map = this.maps[this.api];	
		// remove old controls

		// Google has a combined zoom and pan control.
		if (args.zoom || args.pan) {
			if (args.zoom == 'large'){ 
				this.addLargeControls();
			} else { 
				this.addSmallControls();
			}
		}
		if (args.scale){
			var myOptions = {
				scaleControl:true,
				scaleControlOptions: {style:google.maps.ScaleControlStyle.DEFAULT}				
			};
			map.setOptions(myOptions);
			this.addControlsArgs.scale = true;
		}
		if (args.map_type){
		    this.addMapTypeControls();
		}
	},

	addSmallControls: function() {
		var map = this.maps[this.api];
		var myOptions = {
			navigationControl: true,
			navigationControlOptions: {style: google.maps.NavigationControlStyle.SMALL}
		};
		map.setOptions(myOptions);

		this.addControlsArgs.pan = false;
		this.addControlsArgs.scale = false;						
		this.addControlsArgs.zoom = 'small';
	},

	addLargeControls: function() {
		var map = this.maps[this.api];
		var myOptions = {
			navigationControl: true,
			navigationControlOptions: {style:google.maps.NavigationControlStyle.DEFAULT}
		};
		map.setOptions(myOptions);
		this.addControlsArgs.pan = true;
		this.addControlsArgs.zoom = 'large';
	},

	addMapTypeControls: function() {
		var map = this.maps[this.api];
		var myOptions = {
			mapTypeControl: true,
			mapTypeControlOptions: {style: google.maps.MapTypeControlStyle.DEFAULT}
		};
		map.setOptions(myOptions);
		this.addControlsArgs.map_type = true;
	},

	setCenterAndZoom: function(point, zoom) { 
		var map = this.maps[this.api];
		var pt = point.toProprietary(this.api);
		map.setCenter(pt);
		map.setZoom(zoom);
	},
	
	addMarker: function(marker, old) {
	   return marker.toProprietary(this.api);		
	},

	removeMarker: function(marker) {
		// doesn't really remove them, just hides them
		marker.hide();
	},
	
	declutterMarkers: function(opts) {
		var map = this.maps[this.api];
		// TODO: Add provider code
	},

	addPolyline: function(polyline, old) {
		var map = this.maps[this.api];
		var gpoly = polyline.toProprietary(this.api);
		gpoly.setMap(map);
		return gpoly;
	},

	removePolyline: function(polyline) {
		var map = this.maps[this.api];
		polyline.proprietary_polyline.setMap(null);
	},
	   
	getCenter: function() {
		var map = this.maps[this.api];
		var pt = map.getCenter();
		return new mxn.LatLonPoint(pt.lat(),pt.lng());
	},

	setCenter: function(point, options) {
		var map = this.maps[this.api];
		var pt = point.toProprietary(this.api);
		if(options && options.pan) { 
			map.panTo(pt);
		}
		else { 
			map.setCenter(pt);
		}
	},

	setZoom: function(zoom) {
		var map = this.maps[this.api];
		map.setZoom(zoom);
	},
	
	getZoom: function() {
		var map = this.maps[this.api];
		return map.getZoom();
	},

	getZoomLevelForBoundingBox: function( bbox ) {
		var map = this.maps[this.api];
		var sw = bbox.getSouthWest().toProprietary(this.api);
		var ne = bbox.getNorthEast().toProprietary(this.api);
		var gLatLngBounds = new google.maps.LatLngBounds(sw, ne);
		map.fitBounds(gLatLngBounds);
		return map.getZoom();
	},

	setMapType: function(type) {
		var map = this.maps[this.api];
		switch(type) {
			case mxn.Mapstraction.ROAD:
				map.setMapTypeId(google.maps.MapTypeId.ROADMAP);
				break;
			case mxn.Mapstraction.SATELLITE:
				map.setMapTypeId(google.maps.MapTypeId.SATELLITE);
				break;
			case mxn.Mapstraction.HYBRID:
				map.setMapTypeId(google.maps.MapTypeId.HYBRID);
				break;
			case mxn.Mapstraction.PHYSICAL:
				map.setMapTypeId(google.maps.MapTypeId.TERRAIN);
				break;
			default:
				map.setMapTypeId(google.maps.MapTypeId.ROADMAP);
		}	 
	},

	getMapType: function() {
		var map = this.maps[this.api];
		var type = map.getMapTypeId();
		switch(type) {
			case google.maps.MapTypeId.ROADMAP:
				return mxn.Mapstraction.ROAD;
			case google.maps.MapTypeId.SATELLITE:
				return mxn.Mapstraction.SATELLITE;
			case google.maps.MapTypeId.HYBRID:
				return mxn.Mapstraction.HYBRID;
			case google.maps.MapTypeId.TERRAIN:
				return mxn.Mapstraction.PHYSICAL;
			default:
				return null;
		}
	},

	getBounds: function () {
		var map = this.maps[this.api];
		var gLatLngBounds = map.getBounds();
		var sw = gLatLngBounds.getSouthWest();
		var ne = gLatLngBounds.getNorthEast();
		return new mxn.BoundingBox(sw.lat(), sw.lng(), ne.lat(), ne.lng());
	},

	setBounds: function(bounds){
		var map = this.maps[this.api];
		var sw = bounds.getSouthWest().toProprietary(this.api);
		var ne = bounds.getNorthEast().toProprietary(this.api);
		var gLatLngBounds = new google.maps.LatLngBounds(sw, ne);
		map.fitBounds(gLatLngBounds);
	},

	addImageOverlay: function(id, src, opacity, west, south, east, north, oContext) {
		var map = this.maps[this.api];
		
		// TODO: Add provider code
	},

	setImagePosition: function(id, oContext) {
		var map = this.maps[this.api];
		var topLeftPoint; var bottomRightPoint;

		// TODO: Add provider code

		//oContext.pixels.top = ...;
		//oContext.pixels.left = ...;
		//oContext.pixels.bottom = ...;
		//oContext.pixels.right = ...;
	},
	
	addOverlay: function(url, autoCenterAndZoom) {
		var map = this.maps[this.api];
		
		// TODO: Add provider code
		
	},

	addTileLayer: function(tile_url, opacity, copyright_text, min_zoom, max_zoom, map_type) {
		var map = this.maps[this.api];
		
		// TODO: Add provider code
	},

	toggleTileLayer: function(tile_url) {
		var map = this.maps[this.api];
		
		// TODO: Add provider code
	},

	getPixelRatio: function() {
		var map = this.maps[this.api];

		// TODO: Add provider code	
	},
	
	addCrosshair: function(Cross, crosshairSize, divid) {
		var map = this.maps[this.api];
                if ( map.init == true ) {
                    cross=document.getElementById("Googlev3_Control_CrossHair");
                    cross.style.visibility = 'visible';
                    return map.crosshair;
                };
		var container = map.getDiv();
		var crosshair=document.createElement("img");
                crosshair.id = "Googlev3_Control_CrossHair";
		crosshair.src=Cross;
		crosshair.style.width=crosshairSize+'px';
		crosshair.style.height=crosshairSize+'px';
		crosshair.style.border='0';
		crosshair.style.position='fixed';
                this.X = (parseInt(container.offsetWidth) / 2)+8-(crosshairSize / 2) + 'px';
                this.Y = (parseInt(container.offsetHeight) / 2)+8-(crosshairSize / 2) + 'px';
                crosshair.style.top=this.Y;
                crosshair.style.left=this.X;
		crosshair.style.zIndex='1500';
		container.appendChild(crosshair);
		map.crosshair=crosshair;
                map.init = true;
		return crosshair;
	},
	
	removeCrosshair: function(element) {
		var map = this.maps[this.api];
                if ( map.init == true ) {
                    cross=document.getElementById('Googlev3_Control_CrossHair');
                    cross.style.visibility = 'hidden';
                };
	},
	
	mousePosition: function(element) {
		var map = this.maps[this.api];

		// TODO: Add provider code	
	}
},

LatLonPoint: {
	
	toProprietary: function() {
		return new google.maps.LatLng(this.lat, this.lon);
	},

	fromProprietary: function(googlePoint) {
		this.lat = googlePoint.lat();
		this.lon = googlePoint.lng();
	}
	
},

Marker: {
	
	toProprietary: function() {
		var options = {};

		// do we have an Anchor?
		var ax = 0;  // anchor x 
		var ay = 0;  // anchor y

		if (this.iconAnchor) {
			ax = this.iconAnchor[0];
			ay = this.iconAnchor[1];
		}
		var gAnchorPoint = new google.maps.Point(ax,ay);

		if (this.iconUrl) {
 			options.icon = new google.maps.MarkerImage(
				this.iconUrl,
				new google.maps.Size(this.iconSize[0], this.iconSize[1]),
				new google.maps.Point(0,0),
				gAnchorPoint
			);

			// do we have a Shadow?
			if (this.iconShadowUrl) {
				if (this.iconShadowSize) {
					var x = this.iconShadowSize[0];
					var y = this.iconShadowSize[1];
					options.shadow = new google.maps.MarkerImage(
						this.iconShadowUrl,
						new google.maps.Size(x,y),
						new google.maps.Point(0,0),
						gAnchorPoint 
					);
				}
				else {
					options.shadow = new google.maps.MarkerImage(this.iconShadowUrl);
				}
			}
		}
		if (this.draggable){
			options.draggable = this.draggable;
		}
		if (this.labelText){
			options.title =  this.labelText;
		}
		if (this.imageMap){
			options.shape = {
				coord: this.imageMap,
				type: 'poly'
			};
		}
		
		options.position = this.location.toProprietary(this.api);
		options.map = this.map;

		var marker = new google.maps.Marker(options);

		if (this.infoBubble){
			var infowindow = new google.maps.InfoWindow({
				content: this.infoBubble
			});

			var event_action = "click";
			if (this.hover) {
				event_action = "mouseover";
			}
			google.maps.event.addListener(marker, event_action, function() { infowindow.open(this.map,marker); });
		}

		if (this.hoverIconUrl){
			var gSize = new google.maps.Size(this.iconSize[0], this.iconSize[1]);
			var zerozero = new google.maps.Point(0,0);
 			var hIcon = new google.maps.MarkerImage(
				this.hoverIconUrl,
				gSize,
				zerozero,
				gAnchorPoint
			);
 			var Icon = new google.maps.MarkerImage(
				this.iconUrl,
				gSize,
				zerozero,
				gAnchorPoint
			);
			google.maps.event.addListener(
				marker, 
				"mouseover", 
				function(){ 
					marker.setIcon(hIcon); 
				}
			);
			google.maps.event.addListener(
				marker, 
				"mouseout", 
				function(){ marker.setIcon(Icon); }
			);
		}

		google.maps.event.addListener(marker, 'click', function() {
			marker.mapstraction_marker.click.fire();
		});
		
		return marker;
	},

	openBubble: function() {
		var infowindow = new google.maps.InfoWindow({
	   		content: this.infoBubble
		});
		infowindow.open(this.map,this.proprietary_marker);
	},

	hide: function() {
		this.proprietary_marker.setOptions({visible:false});
	},

	show: function() {
		this.proprietary_marker.setOptions({visible:true});
	},

	update: function() {
		// TODO: Add provider code
	}
	
},

Polyline: {
	toProprietary: function() {
		var pts = this.points;
		var gpts = [];
		for (var i=0; i<pts.length; i++) {
		  gpts.push(pts[i].toProprietary(this.api));
		}
		if (this.closed || pts[0].equals(pts[pts.length - 1])) {
		  return new google.maps.Polygon({
		    path: gpts,
    		strokeColor: this.color,
   			strokeOpacity: this.opacity,
    		strokeWeight: this.width,
    		fillColor: this.fillColor || "#5462E3",
    		fillOpacity: this.opacity || "0.3"
		  });
		}
		else {
		  return new google.maps.Polyline({
		    path: gpts,
    		strokeColor: this.color,
   			strokeOpacity: this.opacity,
    		strokeWeight: this.width
		  });
		}
	},
	
	show: function() {
			throw 'Not implemented';
	},

	hide: function() {
			throw 'Not implemented';
	}
	
}

});
