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
        this.gamePiece = new createjs.Bitmap(base_url+color+'.png').set({scaleX: 0.20, scaleY: 0.20});
        //Set location
        this.gamePiece.x = this.positionX;
        this.gamePiece.y = this.positionY;

        //Return game piece to be displayed
        return this.gamePiece;
    }

    this.getGamePiece = function() {
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

function updateGameState(data){
	//Get canvas object
	var canvasObject = document.getElementById('clueless').getContext('2d');
	//Get the height and width
	var canvasHeight = canvasObject.canvas.height;
	var canvasWidth = canvasObject.canvas.width;
	//Get the equal blocks
	var heightBlock = Math.floor(canvasHeight/5);
	var widthBlock = Math.floor(canvasWidth/5);

	//Check if the game status has changed
	if(data['changed'] == true){
		//Update game sequence
		cached_game_seq = data['gamestate']['game_sequence'];
		//Loop through each player
		var index;
		for(index=0; index < data['gamestate']['playerstates'].length; index++){
			var characterId = data['gamestate']['playerstates'][index]['character']['character_id'];
			var characterColor = data['gamestate']['playerstates'][index]['character']['character_color'];
			var characterX = (data['gamestate']['playerstates'][index]['currentSpace']['posX']-1)*widthBlock+50;
			var characterY = (data['gamestate']['playerstates'][index]['currentSpace']['posY']-1)*heightBlock+50;
			//Adjust character locations to make them unique
			characterX += (index % 3) * 40;
			if(index >= 3){
				characterY += 40;
			}
			//Check to see if player has been initialized
			if(characterId in players){
				//Update current location
				players[characterId].getGamePiece().x = characterX;
				players[characterId].getGamePiece().y = characterY;
			}else{
				//Create object and set current location
				players[characterId] = new Player(
					characterColor,
					characterX,
					characterY
				);
				//Add player to stage
				stage.addChild(players[characterId].createGamePiece());
			}
		}

		//If it is the players turn, and it wasn't the players turn previously, reload action bar
		if(data['gamestate']['isPlayerTurn'] != cached_is_player_turn){
		    loadActionBar();
		}
		cached_is_player_turn = data['gamestate']['isPlayerTurn']

        //display the won game or lost game depending on whether the player won or lost
		if(data['gamestate']['gameResult'] == 1){
		    $('#wonGameRow').show();
		}else if (data['gamestate']['gameResult'] == -1){
		    $('#lostGameRow').show();
		}
		//Update canvas
		stage.update();
	}
}

function getGameState(url, game_id, player_id, cached_game_seq){
	//Post to server
	$.post(
	   url,
	   {game_id:game_id, player_id:player_id, cached_game_seq:cached_game_seq}
	).done(function(data){
	   updateGameState(data);
	   return data;
	});
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




