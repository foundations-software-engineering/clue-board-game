//Post to server
    $('#suggestionTurnForm').submit(function(event) {
    $.post(
        $('#suggestionTurnForm').attr('action'),
        $('#suggestionTurnForm').serialize()
     ).done(function(data){
        $( "#actionBar" ).html( data );
     });

    event.preventDefault();
});