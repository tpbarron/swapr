$(document).ready(function() {
	
	var map, geocoder;
	initialize();
	
	function initialize() {
	    geocoder = new google.maps.Geocoder();
		var myOptions = {
	      center: new google.maps.LatLng(38.848973, -104.826492),
	      zoom: 14,
	      mapTypeId: google.maps.MapTypeId.ROADMAP
	    };
	    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
	}
	
	$("#id_date").datepicker({
		showOtherMonths: true,
		selectOtherMonths: true
	});
	
	$("#id_location").bind('focusout', function() {
		var locText = $(this).val();
		codeAddress(locText);
		console.log(locText);
	});
	
	function codeAddress(locText) {
	    geocoder.geocode( { 'address': locText}, function(results, status) {
	        if (status == google.maps.GeocoderStatus.OK) {
	        	map.setCenter(results[0].geometry.location);
	        	var marker = new google.maps.Marker({
	        		map: map,
	        		position: results[0].geometry.location
	        	});
	        	$("label[for='id_location']").html("Location // <b>Thanks! Is the marker on the map correct?</b>");
	        } else {
	        	//alert("Geocode was not successful for the following reason: " + status);
	        	$("label[for='id_location']").html("Location // <b>Please enter a more specific address.</b>");
	        }
	    });
	}

});
