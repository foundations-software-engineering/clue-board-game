
$(document).ready(function(){
		$('#new_position').hide();
		$('#new_position_label').hide()
		$("#player_move").change(showRooms);

});

function showRooms(moveType){
	var moveType = $('#player_move').val();
	if(moveType=="moveSpace"){
		$('#new_position').show();
		$('#new_position_label').show();
	}
	else{
		$('#new_position').hide();
		$('#new_position_label').hide();
	}
}

$('#playerTurnForm').submit(function(event) {
    $.post(
        $('#playerTurnForm').attr('action'),
        $('#playerTurnForm').serialize()
     ).done(function(data){
        $( "#actionBar" ).html( data );
     });

    event.preventDefault();
});
