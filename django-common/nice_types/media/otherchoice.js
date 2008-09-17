$(document).ready( function() {
    $('select.vOtherChoice').change( function() {
        var otherinput = $('input.vOtherChoice');
        if($(this).val() == "_OTHER") {
            otherinput.show();
        } else {
            otherinput.hide();
            otherinput.attr('value', "");
        }
    }).change();
});
