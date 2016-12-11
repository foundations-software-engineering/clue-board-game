//Post to server
 $('#cardRevealForm').submit(function(event) {
    $('#cardRevealForm').css('visibility','hidden');
    $.post(
        $('#cardRevealForm').attr('action'),
        $('#cardRevealForm').serialize()
     ).done(function(data){
        $( "#actionBar" ).html( data );
     });

    event.preventDefault();
});