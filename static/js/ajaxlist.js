// Sort information:
//  info[sort_by], info[order]
//
IMG_ORDER = { "up" : "/static/images/site/arrow_asc.gif", "down" : "/static/images/site/arrow_desc.gif" };

function register_listeners(){
	$("#ajaxwrapper th.sortable").click(function() { send_ajaxinfo("sort_by="+$(this).attr("name"), "#"); return false; });
	$("#ajaxwrapper th.sortable").append("<img />");
	$("#ajaxwrapper a.next_page").click(function () { send_ajaxinfo("next", "#"); return false; });
	$("#ajaxwrapper a.prev_page").click(function () { send_ajaxinfo("prev", "#"); return false; });
	$("#ajaxwrapper select.page").change(function () { send_ajaxinfo("change_page="+this.options[this.selectedIndex].value, "#"); return false; });
}

function send_ajaxinfo(action, url){
	var info = {};
	info["action"] = action;
	
	var action_pair = action.split("=");
	
	// Retrieve the page
	var page = parseInt( $("#ajaxwrapper select.page option:selected:first").text() );
	if(action_pair[0] == "change_page"){
		page = parseInt(action_pair[1]);
	}	
	info["page"] = page;
	if(action == "prev") info["page"] = info["page"] - 1;
	else if(action == "next") info["page"] = info["page"] + 1;
	
	//info["checks"] = $("#ajaxwrapper table.ajaxtable tr :checked").map(function() { return this.value; }).get().join(" ");
	//alert(info["checks"]);
	
	// Retrieve sort information
	var sort_by = $("#ajaxwrapper th.sortable[selected='yes']").attr("name");
	var order = $("#ajaxwrapper th.sortable[selected='yes'] img").attr("order");
	if(action_pair[0] == 'sort_by'){
		if(sort_by == action_pair[1]) {
			if (order == "up") {
				order = "down";
			} else {
				order = "up";
			}
		} 
		
		sort_by = action_pair[1];
	}
	info["sort_by"] = sort_by;
	info["order"] = order;
	
	$(".ajaxinfo").each( function() {
		info[this.name] = this.value;
	});
	
	//alert("Action: " + action + ", Page: " + info["page"] +", URL: " + url +", Sort_by: " + sort_by + ", Order: " + order);
	
	$.post(url, info, function(data){
		//alert("POST request returned");
		$("#ajaxwrapper").html(data);
		register_listeners();
		$("#ajaxwrapper th.sortable[name='"+sort_by+"']").attr("selected", "yes");
		$("#ajaxwrapper th.sortable[name='"+sort_by+"'] img").attr("order", order);
		$("#ajaxwrapper th.sortable[name='"+sort_by+"'] img").attr("src", IMG_ORDER[order]);
	});
	
	return false;
}



$(document).ready(function (){
	register_listeners();
	$("#ajaxwrapper th.sortable[default='on']").attr("selected", "yes");
	$("#ajaxwrapper th.sortable[default='on'] img").attr("src", IMG_ORDER["up"]).attr("order", "up");
	$("#query_button").click(function () { send_ajaxinfo("search", "#"); return false; });
	$("#query_field").keypress( function (e) { if(e.which == 13) { send_ajaxinfo("search", "#"); } });
});