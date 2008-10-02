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

register_exam_listeners = function() { 
	$('#id_course_query').autocomplete('/course/course_autocomplete/', {extraParams : {"instructor" : $('#id_instructor_query').attr("value") } });
	$('#id_instructor_query').autocomplete('/course/instructor_autocomplete/', { extraParams : {course_query : function () { return $('#id_course_query').attr("value") } }  });	

	$('#id_filter_link').bind("click", function (e) {
	    send_ajaxinfo('', '#');
	});
	
	setInstructor = function(instr) {
		$('#id_instructor_query').attr("value", instr);	
		$('#id_filter_link').click();
	}

    $('.clickhide').each( function() {
        $(this).click( function() {
            $(this).next().toggle();
        });
    });
    
    toggleExamAdvanced(false);
};



$(document).ready( function() {
  register_exam_listeners();	  
});