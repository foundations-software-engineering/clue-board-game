//Post to server
    $('#accusationTurnForm').submit(function(event) {
    $.post(
        $('#accusationTurnForm').attr('action'),
        $('#accusationTurnForm').serialize()
     ).done(function(data){
        $( "#actionBar" ).html( data );
     });

    event.preventDefault();
});