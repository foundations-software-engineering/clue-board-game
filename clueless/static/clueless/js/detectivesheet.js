function manualSheetEdit(url, card_id, check){
    //Post to server
    notes = $('#detectiveSheetNotes').val();

    $.post(
        url,
        {card_id:card_id, check:check}
     ).done(function(data){
        loadDetectiveSheet(notes);
     });
}