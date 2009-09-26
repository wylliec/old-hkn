register_event_autocomplete = function() { 
    var fill_event_id = function (e, data, formatted) {
	$('#id_event_id').attr("value", data[1]);
    }
    $('#id_event_query').autocomplete('/event/event_autocomplete/');
    $('#id_event_query').result(fill_event_id)
};

$(document).ready( function() {
  register_event_autocomplete();	  
});
