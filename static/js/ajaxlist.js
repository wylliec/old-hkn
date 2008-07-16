function send_ajaxinfo(action, url){
	info = {};
	info["action"] = action;
	info["page"] = parseInt( $("select#page option:selected").text() )
	
	if(action == "prev") info["page"] = info["page"] - 1;
	else if(action == "next") info["page"] = info["page"] + 1;
	
	$(".ajaxinfo").each( function() {
		info[this.name] = this.value;
	});
	
	alert("Action: " + action + ", Page: " + info["page"]);
	
	$.post(url, info, function(data){
		alert("hi");
		$("#ajaxwrapper").html(data);
	});
	return false;
}

$(document).ready(function (){
	$("#ajaxwrapper a.next_page").click(function () { send_ajaxinfo("next", "#"); return false; });
	$("#ajaxwrapper a.prev_page").click(function () { send_ajaxinfo("prev", "#"); return false; });
	$("#ajaxwrapper select#page").change(function () { send_ajaxinfo("change_page", "#"); return false; });
	$("#query_button").click(function () { send_ajaxinfo("search", "#"); return false; });
	$("#objects_query").keypress( function (e) { if(e.which == 13) { send_ajaxinfo("search", "#"); } });
});