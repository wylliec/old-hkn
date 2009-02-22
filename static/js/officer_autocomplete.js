
function toggleExamAdvanced(toggle) {
    if(toggle) {
        $('#advanced_toggle_show').hide();            
        $('#advanced_toggle_hide').show();                    
        $('.advanced_control').show();
    } else {
        $('.advanced_control').hide();    
        $('#advanced_toggle_hide').hide();                    
        $('#advanced_toggle_show').show();            
    }            
}


register_officer_listeners = function() { 
        var fill_officer_id = function (e, data, formatted) {
            $('#id_officer_id').attr("value", data[1]);
        }
	$('#id_officer_query').autocomplete('/info/officer_autocomplete/');
        $('#id_officer_query').result(fill_officer_id)
	
	var d = {};
	d['officer'] = $('id_officer_query').value;
	d['challenge_name'] = $('id_challenge_name').value;
	
	
	$('#challenge_submit').click(function (e) {
	    //send_ajaxinfo('', '#');
	    $.post('/cand/portal/create_challenge', d, query_confirm);
	});
	
	setInstructor = function(instr) {
		$('#id_officer_query').attr("value", instr);	
		$('#id_filter_link').click();
	}

    $('.clickhide').each( function() {
        $(this).click( function() {
            $(this).next().toggle();
        });
    });
    
    query_confirm = function(e) {
        
    }
    
    toggleExamAdvanced(false);
};

$(document).ready( function() {
  register_officer_listeners();	  
});
