$(document).ready(function() {
	
	var map, geocoder, directionsDisplay, directionsService;
		
	initialize();
	geolocate();
	codeAddress();
	
	
	/* initializes google map */
	function initialize() {
		directionsDisplay = new google.maps.DirectionsRenderer();
		directionsService = new google.maps.DirectionsService();
	    geocoder = new google.maps.Geocoder();
		var myOptions = {
	      center: new google.maps.LatLng(38.848973, -104.826492),
	      zoom: 14,
	      mapTypeId: google.maps.MapTypeId.ROADMAP
	    };
	    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
	    directionsDisplay.setMap(map);
	}
	
	/* sets map given address of event */
	function codeAddress(locText) {
	    geocoder.geocode({ 
	    	'address': $("#detail_location").text()
	    }, function(results, status) {
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
	
	/* locates user using native geolocation if available */
	function geolocate() {
		if (navigator.geolocation) {
			navigator.geolocation.getCurrentPosition(geoSuccess, geoError);
		} else {
			console.log('geolocation not supported');
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
		$.ajax({
			url:'http://127.0.0.1:8000/events/ajax/reversegeocode?lat='+lat+'&lng='+lng,
			success:function(data) {
				console.log(data);
				if (data != "failure") {
					$("#direction_from_input").val(data);
				} else {
					geoError();
				}
			},
			error: geoError
		});
	}
	
	
	$('#direction_submit').bind('click', function(e) {
		e.preventDefault();
		calcRoute();
	});
	/* called when the user decides to get directions */
	function calcRoute() {
		$("#directions_detail_list").empty();
		
		var start = $("#direction_from_input").val();
		var end = $("#direction_to_input").val();
		var travel_mode = $("#travel_mode").val();
		console.log(travel_mode);
		var request = {
			origin: start,
			destination: end,
			travelMode: google.maps.DirectionsTravelMode[travel_mode]	
		};
		directionsService.route(request, function(response, status) {
			if (status == google.maps.DirectionsStatus.OK) {
				directionsDisplay.setDirections(response);
				showSteps(response);
			}
		});
	}
	
	/* modified code from google example 
	 * https://google-developers.appspot.com/maps/documentation/javascript/examples/directions-complex
	 */
	function showSteps(directionResult) {
		var myRoute = directionResult.routes[0].legs[0];

		for ( var i = 0; i < myRoute.steps.length; i++) {
			var text = myRoute.steps[i].instructions;
			$("#directions_detail_heading").show();
			$("#directions_detail_list").append(
					'<li class="direction">' + text + '</li>');
		}
	}
	
});