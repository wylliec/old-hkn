register_candidate_autocomplete = function() { 
    var fill_candidate_id = function (e, data, formatted) {
	$('#id_candidate_id').attr("value", data[1]);
    }
    $('#id_candidate_query').autocomplete('/info/candidate_autocomplete/');
    $('#id_candidate_query').result(fill_candidate_id)
};

$(document).ready( function() {
  register_candidate_autocomplete();	  
});
