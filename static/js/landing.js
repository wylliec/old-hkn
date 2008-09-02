function prepareRow(event_div) {
    $(event_div).html('');
    $(event_div).show();
    $(event_div).html('<img src="/static/images/site/spinner.gif" />');
}

event_show_info_url = "/event/view/";
function showInfo(event_id) {
    event_div = "#event_" + event_id;
    prepareRow(event_div);
    
    url = event_show_info_url + event_id + "/";
    
    $.get(url, {}, function(data) {
        $(event_div).html("<p class='small'>" + data + "</p>");
    });   
}

event_rsvp_paragraph_url = "/event/rsvp/list_for_event_paragraph/";
event_rsvp_list_url = "/event/rsvp/list_event/";
function showRSVP(event_id) {
    event_div = "#event_" + event_id;
    prepareRow(event_div);    
    
    url = event_rsvp_paragraph_url + event_id + "/";
    
    $.get(url, {}, function(data) {
        html = [];
        html.push('<p class="small">');
        html.push(data);
        html.push('<br/>');
        html.push('<a href="' + event_rsvp_list_url + event_id + '/">view all rsvps</a>');        
        html.push('</p>');
    
        $(event_div).html(html.join(''));
    });   
}

rsvp_form_url = "/event/rsvp/edit-ajax/";
function rsvpForm(event_id) {
    event_div = "#event_" + event_id;
    prepareRow(event_div);    
    
    url = rsvp_form_url + event_id + "/";
    
    $.get(url, {}, function(data) {
        $(event_div).html(data);
    });   
}

function rsvpCallback(event_id) {
    showRSVP(event_id);
}
    
function hide(event_id) {
    event_div = "#event_" + event_id;
    $(event_div).html('');
    $(event_div).hide();
}    

$(document).ready( function() {
    $('.autoclear, #id_exam_course').each( function() {
        var value = $(this).attr('value');
        $(this).focus( function () {
            $(this).attr('value', '');
        });
        $(this).blur( function () {
            if($(this).attr('value') == "") {
                $(this).attr('value', value);
            }
        });
    })
});
