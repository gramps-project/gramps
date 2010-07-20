/*
Copyright (c) 2010 Tom Carden, Steve Coast, Mikel Maron, Andrew Turner, Henri Bergius, Rob Moran, Derek Fowler
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 * Neither the name of the Mapstraction nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
/*
   Copyright (c) 2007, Andrew Turner
   All rights reserved.

   Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 * Neither the name of the Mapstraction nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */


// Use http://jsdoc.sourceforge.net/ to generate documentation

// TODO: add reverse geocoding support

/**
 * MapstractionGeocoder instantiates a geocoder with some API choice
 * @param {Function} callback The function to call when a geocode request returns (function(waypoint))
 * @param {String} api The API to use, currently only 'mapquest' is supported
 * @param {Function} error_callback The optional function to call when a geocode request fails
 * @constructor
 */
function MapstractionGeocoder(callback, api, error_callback) {
	this.api = api;
	this.callback = callback;
	this.geocoders = {};
	if(error_callback === null) {
		this.error_callback = this.geocode_error;
	} else {
		this.error_callback = error_callback;
	}

	// This is so that it is easy to tell which revision of this file 
	// has been copied into other projects.
	this.svn_revision_string = '$Revision: 107 $';

	this.addAPI(api);

}


/**
 * Internal function to actually set the router specific parameters
 */
MapstractionGeocoder.prototype.addAPI = function(api) { 

	me = this;
	switch (api) {
		case 'google':
			this.geocoders[api] = new GClientGeocoder();
			break;
		case 'mapquest':
			//set up the connection to the geocode server
			var proxyServerName = "";
			var proxyServerPort = "";
			var ProxyServerPath = "mapquest_proxy/JSReqHandler.php";

			var serverName = "geocode.access.mapquest.com";
			var serverPort = "80";
			var serverPath = "mq";
			this.geocoders[api] = new MQExec(serverName, serverPath, serverPort, proxyServerName, ProxyServerPath, proxyServerPort );
				
			break;
		default:
			alert(api + ' not supported by mapstraction-geocoder');
	}
};
/**
 * Change the Routing API to use
 * @param {String} api The API to swap to
 */
MapstractionGeocoder.prototype.swap = function(api) {
	if (this.api == api) { return; }

	this.api = api;
	if (!this.geocoders.hasOwnProperty(this.api)) {
		this.addAPI($(element),api);
	}
};

/**
 * Default Geocode error function
 */
MapstractionGeocoder.prototype.geocode_error = function(response) { 
	alert("Sorry, we were unable to geocode that address");
};

/**
 * Default handler for geocode request completion
 */
MapstractionGeocoder.prototype.geocode_callback = function(response, mapstraction_geocoder) { 
	var return_location = {};
	
	// TODO: what if the api is switched during a geocode request?
	// TODO: provide an option error callback
	switch (mapstraction_geocoder.api) {
		case 'google':
	  		if (!response || response.Status.code != 200) {
				mapstraction_geocoder.error_callback(response);
			} else {
				return_location.street = "";
				return_location.locality = "";
				return_location.region = "";
				return_location.country = "";

				var place = response.Placemark[0];
				if(place.AddressDetails.Country.AdministrativeArea !== null) {
					return_location.region = place.AddressDetails.Country.AdministrativeArea.AdministrativeAreaName;
						
					if(place.AddressDetails.Country.AdministrativeArea.SubAdministrativeArea !== null) {
						if(place.AddressDetails.Country.AdministrativeArea.SubAdministrativeArea.Locality !== null) {
							return_location.locality = place.AddressDetails.Country.AdministrativeArea.SubAdministrativeArea.Locality.LocalityName;

							if(place.AddressDetails.Country.AdministrativeArea.SubAdministrativeArea.Locality.Thoroughfare !== null) {
								return_location.street = place.AddressDetails.Country.AdministrativeArea.SubAdministrativeArea.Locality.Thoroughfare.ThoroughfareName;
							}
						}
							
					}
						
				}
				return_location.country = place.AddressDetails.Country.CountryNameCode;
				return_location.address = place.address;	

				return_location.point = new mxn.LatLonPoint(place.Point.coordinates[1], place.Point.coordinates[0]);
				mapstraction_geocoder.callback(return_location);
			}
			break;
		case 'mapquest':
			break;
	}
};


/**
 * Performs a geocoding and then calls the specified callback function with the location
 * @param {Object} address The address object to geocode
 */
 MapstractionGeocoder.prototype.geocode = function(address) { 
	 var return_location = {};

	 // temporary variable for later using in function closure
	 var mapstraction_geocoder = this;

	 switch (this.api) {
		 case 'google':
			if (address.address === null || address.address === "") {
				address.address = address.street + ", " + address.locality + ", " + address.region + ", " + address.country;
			}
			this.geocoders[this.api].getLocations(address.address, function(response) { mapstraction_geocoder.geocode_callback(response, mapstraction_geocoder); });
			break;
		case 'mapquest':
			var mqaddress = new MQAddress();
			var gaCollection = new MQLocationCollection("MQGeoAddress");
			 //populate the address object with the information from the form
			mqaddress.setStreet(address.street);
			mqaddress.setCity(address.locality);
			mqaddress.setState(address.region);
			mqaddress.setPostalCode(address.postalcode);
			mqaddress.setCountry(address.country);

			this.geocoders[this.api].geocode(mqaddress, gaCollection);
			var geoAddr = gaCollection.get(0);
			var mqpoint = geoAddr.getMQLatLng();
			return_location.street = geoAddr.getStreet();
			return_location.locality = geoAddr.getCity();
			return_location.region = geoAddr.getState();
			return_location.country = geoAddr.getCountry();
			return_location.point = new mxn.LatLonPoint(mqpoint.getLatitude(), mqpoint.getLongitude());
			this.callback(return_location, this);
			break;
		 default:
			alert(api + ' not supported by mapstraction-geocoder');
			break;
	 }
 };
