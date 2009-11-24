function prepareRow(event_div) {
    $(event_div).html('<img src="/static/images/site/spinner.gif" />');
}

event_show_info_url = "/event/view/";

/*Handles showing info for events on the sidebar. If there is an extremely
 *long word, break it up by inserting <wbr> between each character. It does
 *so by first breaking up the text by whitespaces, checking the length of
 *each substring, then joining them back together (replacing the whitespaces
 *with spaces. This assumes that either <br> or <p> would be used to indicate
 *newlines (since it's html) and it might break if there's no whitespace
 *between a word and a html tag. Firefox will hopefully get a supported css
 *word break function soon... *crosses fingers*.
*/
function showInfo(event_id) {
    event_info_div = "#event_" + event_id + "_info";
    event_rsvp_div = "#event_" + event_id + "_rsvp";
    event_rsvp_list_div = "#event_" + event_id + "_rsvp_list";
    if($(event_info_div).html() == ""){
      prepareRow(event_info_div);
      
      url = event_show_info_url + event_id + "/";
      
      $.get(url, {}, function(data) {
          var str=data.split(/\s/);
	  for(i=0;i<str.length;i++){
	      if(str[i].length>40) str[i]=str[i].split("").join("<wbr>");
	  }
	  str=str.join(" ");
          $(event_info_div).html("<p class='small'>" + str + "</p>");
      });  
    }
    $(event_rsvp_div).hide();
    $(event_info_div).toggle();
    $(event_rsvp_list_div).hide(); 
}

event_rsvp_paragraph_url = "/event/rsvp/list_for_event_paragraph/";
event_rsvp_list_url = "/event/rsvp/list_event/";
function showRSVP(event_id) {
    event_info_div = "#event_" + event_id + "_info";
    event_rsvp_div = "#event_" + event_id + "_rsvp";
    event_rsvp_list_div = "#event_" + event_id + "_rsvp_list";
    if($(event_rsvp_list_div).html() == ""){
      prepareRow(event_rsvp_list_div);    
      
      url = event_rsvp_paragraph_url + event_id + "/";
      
      $.get(url, {}, function(data) {
          html = [];
          html.push('<p class="small">');
          html.push(data);
          html.push('<br/>');
          html.push('<a href="' + event_rsvp_list_url + event_id + '/">view all rsvps</a>');        
          html.push('</p>');
      
          $(event_rsvp_list_div).html(html.join(''));
      });
    }
    $(event_rsvp_div).hide();
    $(event_info_div).hide();
    $(event_rsvp_list_div).toggle();
}

rsvp_form_url = "/event/rsvp/edit-ajax/";
function rsvpForm(event_id) {
    event_info_div = "#event_" + event_id + "_info";
    event_rsvp_div = "#event_" + event_id + "_rsvp";
    event_rsvp_list_div = "#event_" + event_id + "_rsvp_list";
    
    if($(event_rsvp_div).html() == ""){
      prepareRow(event_rsvp_div);    
      
      url = rsvp_form_url + event_id + "/";
      
      $.get(url, {}, function(data) {
          $(event_rsvp_div).html(data);
      });
    }
    
    $(event_rsvp_div).toggle();
    $(event_info_div).hide();
    $(event_rsvp_list_div).hide();
    
}

function rsvpCallback(event_id) {
    event_rsvp_div = "#event_" + event_id + "_rsvp";
    $(event_rsvp_div).html("Successfully RSVP'd.")
}
    
function hide(event_id) {
    event_div = "#event_" + event_id;
    $(event_div).html('');
    $(event_div).hide();
}    
