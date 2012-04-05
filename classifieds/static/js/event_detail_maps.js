$(document).ready(function() {
	
	var map, geocoder;
	initialize();
	codeAddress();
	geolocate();
	
	function initialize() {
	    geocoder = new google.maps.Geocoder();
		var myOptions = {
	      center: new google.maps.LatLng(38.848973, -104.826492),
	      zoom: 14,
	      mapTypeId: google.maps.MapTypeId.ROADMAP
	    };
	    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
	}
	
	function codeAddress(locText) {
	    geocoder.geocode( { 'address': $("#detail_location").text()}, function(results, status) {
	        if (status == google.maps.GeocoderStatus.OK) {
	        	map.setCenter(results[0].geometry.location);
	        	var marker = new google.maps.Marker({
	        		map: map,
	        		position: results[0].geometry.location
	        	});
	        } else {
	          alert("Geocode was not successful for the following reason: " + status);
	        }
	    });
	}
	
	function geolocate() {
		if (navigator.geolocation) {
			navigator.geolocation.getCurrentPosition(geoSuccess, geoError);
		} else {
			error('not supported');
		}
	}
	
	function geoSuccess(pos) {
		var lat = pos.coords.latitude;
		var lng = pos.coords.longitude;
		var location = new google.maps.LatLng(lat, lng);
		var geoMarker = new google.maps.Marker({
			map: map,
			position: location
		});
		console.log(location);
		reverseGeocode(lat, lng);
	}
	
	function geoError() {
		$("#direction_from").html("From - <b>please enter your location</b>");
	}
	
	function reverseGeocode(lat, lng) {
		$.jsonp({
			url:'http://maps.googleapis.com/maps/api/geocode/json?latlng='+lat+','+lng+'&sensor=false', 
			callback: "callback",
			success: reverseGeocodeSuccess
		});
	}
	
	function reverseGeocodeSuccess(data) {
		console.log("hello");
		console.log(data);
		//results.address_components.formatted_address
	}
	
});