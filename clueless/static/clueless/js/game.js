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
	//Get canvas object
	var canvasObject = document.getElementById('clueless').getContext('2d');
	//Get the height and width
	var canvasHeight = canvasObject.canvas.height;
	var canvasWidth = canvasObject.canvas.width;
	//Get the equal blocks
	var heightBlock = Math.floor(canvasHeight/5);
	var widthBlock = Math.floor(canvasWidth/5);

	//Determine coordinates of block
	var droppedHeight = Math.floor(y/heightBlock)+1;
	var droppedWidth = Math.floor(x/widthBlock)+1;
	//Loop and find space by location
	for(i=0; i<spaceLocations.length; i++){
		//Check for a valid location
		if((droppedWidth == spaceLocations[i][1]) && (droppedHeight == spaceLocations[i][2])){
			return spaceLocations[i][0];
		}
	}
}


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

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




