function showRooms(){
	var moveType = $('#player_move').val();
	if(moveType=="moveSpace"){
		$('#new_position_div').show();
	}
	else{
		$('#new_position_div').hide();
	}
}

function toggleSubmit(){
    $('#playerturn').prop("disabled",
        $("#player_move").val() == "NOTHING"
    );
}

$('#playerTurnForm').submit(function(event) {
    if($("#player_move").val() != "NOTHING"){
        $('#playerTurnForm').css('visibility','hidden');
        $.post(
            $('#playerTurnForm').attr('action'),
            $('#playerTurnForm').serialize()
         ).done(function(data){
            $( "#actionBar" ).html( data );
         });
    }
    event.preventDefault();
});

$(document).ready(function(){
    showRooms();
    toggleSubmit();
    $("#player_move").change(function() {
        showRooms();
        toggleSubmit();
    });
    showRooms("hide");
});