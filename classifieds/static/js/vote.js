$(document).ready(function() {
	
	console.log("vote.js");
	
	/*
	 * upvote = 1
	 * downvote = 0
	 */
	
	$(".vote a").bind('click', function(e) {
		e.preventDefault();
		console.log(this);
		var id = $(this).attr('id');
		if ($(this).hasClass("up")) {
			vote = 1;
		} else if ($(this).hasClass("down")) {
			vote = 0;
		}
		
		updateVoteCount(vote, id);
		sendToServer(vote, id);
		setDisabled();
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
		$.get('/vote/'+vote+'/'+id, function(data) {
			console.log(data);
		});
		
	}
	
	function setDisabled() {
		
	}
	
	
});