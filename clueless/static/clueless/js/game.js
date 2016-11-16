function Player (color, x, y) {
	//Declare instance variables
	this.color = color;
	this.positionX = x;
	this.positionY = y;
	
	//Initialize other class variables
	this.gamePiece = null;
	
	//Declare functions
	this.createGamePiece = function() {
		//Create shape
		this.gamePiece = new createjs.Shape();
		//Set location
		this.gamePiece.graphics.beginFill(this.color).drawCircle(0,0,15);
		this.gamePiece.x = this.positionX;
		this.gamePiece.y = this.positionY;

		//Return game piece to be displayed
		return this.gamePiece;
	}
}

function getLocationFromCoordinates(x, y){
	var locations = [
		[11, "Study Trapdoor", 0, 0, 45, 45],
		[13, "Lounge Trapdoor", 755, 0, 800, 45],
		[17, "Conservatory Trapdoor", 0, 755, 45, 800],
		[19, "Kitchen Trapdoor", 755, 755, 800, 800],
		[1, "Study", 0, 0, 170, 215],
		[2, "Hall", 260, 0, 525, 215],
		[3, "Lounge", 615, 0, 800, 215],
		[4, "Library", 0, 310, 170, 485],
		[5, "Billiard Room", 260, 315, 525, 485],
		[6, "Dining Room", 615, 310, 800, 485],
		[7, "Conservatory", 0, 575, 170, 800],
		[8, "Ballroom", 260, 575, 525, 800],
		[9, "Kitchen", 615, 575, 800, 800],
		[21, "Study-Hall Hallway", 170, 0, 260, 215],
		[22, "Hall-Lounge Hallway", 525, 0, 615, 215],
		[23, "Study-Library Hallway", 0, 215, 170, 310],
		[24, "Hall-Billiard Hallway", 260, 215, 525, 310],
		[25, "Lounge-Dining Hallway", 615, 215, 800, 310],
		[26, "Library-Billiard Hallway", 170, 310, 260, 485],
		[27, "Billiard-Dining Hallway", 525, 310, 615, 485],
		[28, "Library-Conservatory Hallway", 0, 485, 170, 575],
		[29, "Billiard-Ball Hallway", 260, 485, 525, 575],
		[30, "Dining-Kitchen Hallway", 615, 485, 800, 575],
		[31, "Conservatory-Ball Hallway", 170, 575, 260, 800],
		[32, "Ball-Kitchen Hallway", 525, 575, 615, 800]  
	];
	
	//console.log('('+x+','+y+')');
	
	var i;
	for(i=0; i<locations.length; i++){
		//Check for a valid location
		if((x >= locations[i][2]) && (x < locations[i][4]) && (y >= locations[i][3]) && (y < locations[i][5])){
			console.log(locations[i][1]);
			return locations[i];
		}
	}
}



$(document).ready(function(){
	//When AJAX test is clicked, process GET request
	$('#submit_ajax').click(function(){
		console.log('Submitting AJAX');
		//Get URL
		var url = $('#ajax_url').val();
		//Send GET request
		console.log('Sending GET request to: '+url);
		$.get( url , function( data ) {
			$( "#ajax_results" ).html( data );
			console.log("Load was performed.");
		});
	});
});




