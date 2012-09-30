$(document).ready(function() {
	
	console.log("vote.js");
	
	/*
	 * upvote = 1
	 * downvote = 0
	 */
	
	$(".vote span").bind('click', function(e) {
		e.preventDefault();
		console.log(this);
		
		var id = $(this).attr('id').substring(2);
		console.log(id);
		if ($(this).parent().hasClass("active")) {
			var vote;
			if ($(this).hasClass("up")) {
				vote = 1;
			} else if ($(this).hasClass("down")) {
				vote = 0;
			}
			updateVoteCount(vote, id);
			sendToServer(vote, id);
			setDisabled($(this).parent());
		} 
	});
	
	function updateVoteCount(vote, id) {
		var count = $("#votes"+id);
		console.log(count.text());
		if (vote == 1) {
			count.text(parseInt(count.text())+1);
		} else if (vote == 0) {
			count.text(parseInt(count.text())-1);
		}
	}
	
	
	function sendToServer(vote, id) {
		$.get('/suggestions/vote/'+vote+'/'+id+'/', function(data) {
			console.log(data);
		});
		
	}
	
	function setDisabled(parent) {
		parent.removeClass("active").addClass("inactive");
	}
	
	
});