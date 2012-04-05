$(document).ready(function() {
	
	$.getJSON('/events/data/', function(data) {
			setCalendar(data);
		}
	);
	
	function setCalendar(data) {
	$('#calendar').fullCalendar({
			theme: true,
			header: {
				left: 'prev,next today',
				center: 'title',
				right: 'month,agendaWeek,agendaDay'
			},
			editable: false,
			events: data //'/events/data/'
	});
	}

});