//Post to server
    $('#cardRevealForm').submit(function(event) {
    $.post(
        $('#cardRevealForm').attr('action'),
        $('#cardRevealForm').serialize()
     ).done(function(data){
        $( "#actionBar" ).html( data );
     });

    event.preventDefault();
});