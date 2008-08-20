function toggleAdvanced(toggle) {
    if(toggle) {
        $('#advanced_toggle').hide();            
        $('.advanced_control').show();
    } else {
        $('.advanced_control').hide();    
        $('#advanced_toggle').show();            
    }            
}

register_listeners = function() { 
	$('#id_course_query').autocomplete('/course/course_autocomplete', {extraParams : {"instructor" : $('#id_instructor_query').attr("value") } });
	$('#id_instructor_query').autocomplete('/course/instructor_autocomplete', { extraParams : {course_query : function () { return $('#id_course_query').attr("value") } }  });	
	$('#id_select_after').attr('value', '{{ after_filter }}');
	$('#id_select_type').attr('value', '{{ type_filter }}');
	$('#id_select_number').attr('value', '{{ number_filter }}');	
	$('#id_filter_link').bind("click", function (e) {
		category = "";
		$('.list_filter').each( function (index, e) {
			ee = $(e);
			if(ee.attr("value") != undefined) {
				category += ee.attr("name") + ":" + ee.attr("value") + "|";
			}
		});
		filter('{{ sort }}', '1', '{{ max }}', category, '');
	});
	
	setInstructor = function(instr) {
		$('#id_instructor_query').attr("value", instr);	
		$('#id_filter_link').click();
	}

    $('.clickhide').click( function() {
            $(this.nextSibling).toggle();
    });
    
    toggleAdvanced(false);
};


