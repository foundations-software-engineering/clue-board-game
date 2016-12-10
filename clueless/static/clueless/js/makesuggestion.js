//Post to server
$('#suggestionTurnForm').submit(function(event) {
    $('#suggestionTurnForm').css('visibility','hidden');
    $.post(
        $('#suggestionTurnForm').attr('action'),
        $('#suggestionTurnForm').serialize()
     ).done(function(data){
        $( "#actionBar" ).html( data );
     });

    event.preventDefault();
});