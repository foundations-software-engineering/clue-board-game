//Post to server
$('#accusationTurnForm').submit(function(event) {
    $('#accusationTurnForm').css('visibility','hidden');
    $.post(
        $('#accusationTurnForm').attr('action'),
        $('#accusationTurnForm').serialize()
     ).done(function(data){
        $( "#actionBar" ).html( data );
     });

    event.preventDefault();
});