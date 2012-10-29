var undefined, canvas, ctx;

var cfg = {
	initX: 9*window.innerWidth/10,
	initY: window.innerHeight-125,
	max_sub_branch: 5,
	max_sub_angle: 3*Math.PI/4,
	max_size: 8,
	branch_length: 100,
	color: "black",
	flower_colors: ["red", "orange", "purple"]
};
	
function init() {
	if (canvas == undefined) {
		console.log("initing");
		canvas = document.getElementById('tree_canvas');
		canvas.width = window.innerWidth;
		canvas.height = 600;
		ctx = canvas.getContext("2d");
		ctx.strokeStyle = cfg.color;
		makeBranch(cfg.initX, cfg.initY, cfg.branch_length, -Math.PI/2, cfg.max_size);
	}
}

function makeBranch(start_x, start_y, length, angle, size) {
	console.log("making branch");
	if (size > 0) {
		ctx.lineWidth = size;
		ctx.beginPath();
		ctx.moveTo(start_x, start_y);
		
		var end_x = start_x + length * Math.cos(angle);
		var end_y = start_y + length * Math.sin(angle);
		ctx.lineTo(end_x, end_y);
		ctx.stroke();
		
		var sub_branch = Math.random(cfg.max_sub_branch - 1) + 2;
		var branch_length_dimin = .5 + Math.random()/2;
		
		for(var i=0; i < sub_branch; i++) {
			var newLength = length * branch_length_dimin;
			var newAngle = angle + Math.random() * cfg.max_sub_angle - cfg.max_sub_angle / 2;
			var newSize = size - 1;
			setMakeBranch(end_x, end_y, newLength, newAngle, newSize);			
		}
		ctx.closePath();
	} else {}
}

function setMakeBranch(end_x, end_y, newLength, newAngle, newSize) {
	window.setTimeout(function() {
		makeBranch (end_x, end_y, newLength, newAngle, newSize);
	}, 100);
}

window.onload = function() {
	init();
};
	



/*constants */
/*var max_sub_branch = 5;
var max_sub_angle = 3*Math.PI/4;
var max_size = 5;
var branch_length = 75;
	
function makeBranch(start_x, start_y, length, angle, size, flowerColor) {
	if (size > 0) {
		var end_x = start_x + length * Math.cos(angle);
		var end_y = start_y + length * Math.sin(angle);
		var pathString = "M"+start_x+" "+start_y+" L"+end_x+" "+end_y;
		paper.path(pathString).attr({"stroke-width":size,
									"stroke-linecap":"round",
									"fill":"black",
									"stroke":"brown"});
		if (size === 1 && Math.floor(Math.random()*11) > 4) {
			for (var i = 0; i < 3; i++) {//inline drawflower func
				paper.ellipse(end_x, end_y, 4, 1).attr({"fill":flowerColor[0],"stroke":flowerColor[1]}).rotate(60*i);
			}
		}
		var sub_branch = Math.floor(Math.random()*(max_sub_branch-1)+1.2);
		var branch_length_dimin = .5 + Math.random()/2 ;
		for (var i=0; i < sub_branch; i++) {
			var newLength = length * branch_length_dimin ;
			var newAngle = angle + Math.pow(Math.random(),2) * max_sub_angle - max_sub_angle / 2 ;
			var newSize = size - 1 ;
			window.setTimeout(function() {
				makeBranch(end_x, end_y, newLength, newAngle, newSize, flowerColor);
			}, 25);
		}
	}
}

var paper;
function init() {
	var m = document.getElementById("main");
	var w = m.scrollWidth;
	var h = window.innerHeight-81; //81 is the header height
	paper = Raphael(document.getElementById('tree_canvas'), w, h); 
	
	var pos = [[150,h], [w/2,h], [w-150,h]];
	var greenColor = ["orange", "green"];
	var pinkColor = ["pink", "purple"];
	var orangeColor = ["blue", "orange"];
	var colors = [greenColor, pinkColor, orangeColor];
	for (var x = 0; x < 3; x++) {
		setCall(x);
	}
	function setCall(x) {
		window.setTimeout(function() {
			makeBranch(pos[x][0], pos[x][1],branch_length,-Math.PI/2, max_size, colors[Math.floor(Math.random()*3)]);
		}, x*150);
	}
}

window.onload = function() {
	init();
};*/
