IMG_ORDER = { "up" : "/static/images/site/arrow_asc.gif", "down" : "/static/images/site/arrow_desc.gif" };
PLUS_MINUS = { "plus" : "/static/images/site/plus.gif", "minus" : "/static/images/site/minus.gif" };


function register_listeners(){
	$("#ajaxwrapper .ajaxlist_filter").click(function() { send_ajaxinfo("filter="+$(this).attr("key")+"="+$(this).attr("val"), "#"); return false; });
	$("#ajaxwrapper .ajaxlist_remove_item").click(function () { remove_item($(this).parent().parent(), $(this).attr("value").split('=')[1]); return false; });
	$("#ajaxwrapper .ajaxlist_check").change(function () { checkbox_changed($(this).attr("checked"), $(this).attr("value")); return false; });
	$("#ajaxwrapper .sortable").click(function() { send_ajaxinfo("sort_by="+$(this).attr("name"), "#"); return false; });
	$("#ajaxwrapper .sortable").append("<img />");
	$("#ajaxwrapper a.next_page").click(function () { send_ajaxinfo("next", "#"); return false; });
	$("#ajaxwrapper a.prev_page").click(function () { send_ajaxinfo("prev", "#"); return false; });
	$("#ajaxwrapper select.page").change(function () { send_ajaxinfo("change_page="+this.options[this.selectedIndex].value, "#"); return false; });
}

ajaxlist_checkbox_post_address = "/ajaxlist/"
function remove_item(row_object, value){
	var identifier = $("#ajaxwrapper").attr("identifier");
	$.post(ajaxlist_checkbox_post_address, {"action" : "remove", "identifier" : identifier, "value" : value}, 
		function () { 
			if ($(row_object).parent().children().size() == 2){
				window.location.reload( true );
			} else {
				$(row_object).remove(); 
			}
			
		}
	);
}

function checkbox_changed(state, value){
	var identifier = $("#ajaxwrapper").attr("identifier");
	
	if(state == true) {
	    action = "add";
	} else if(state == undefined) {
	    action = "remove";
	} else {
	    action = "unknown";
	}

//	alert(action + ", " + value + ", " + identifier + ", " + ajaxlist_checkbox_post_address);
	$.ajax({
	    url: ajaxlist_checkbox_post_address,
	    type: "POST",
	    data: {"action" : action, "identifier" : identifier, "value" : value},
	    dataType: "script",
	    });
}

ajaxlist_get_url = window.location.pathname
function send_ajaxinfo(action, url){
	if(url == "#") {
		url = ajaxlist_get_url
	}
    
	$("img.ajaxspinner").show();
	var info = {};
	info["action"] = action;
	
	var action_pair = action.split("=");
	
	// Filter action?
	if (action_pair[0] == "filter"){
		info[action_pair[1]] = action_pair[2];
	}
	
	// Clear action?
	if (action_pair[0] == "clear"){
		var identifier = $("#ajaxwrapper").attr("identifier");
		$.get(ajaxlist_checkbox_post_address + "clear/", {"identifier" : identifier});
	}
	
	// Retrieve the page
	var page = parseInt( $("#ajaxwrapper select.page option:selected:first").text() );
	if(action_pair[0] == "change_page"){
		page = parseInt(action_pair[1]);
	}	
	info["page"] = page;
	if(action == "prev") info["page"] = info["page"] - 1;
	else if(action == "next") info["page"] = info["page"] + 1;
	
	// Retrieve sort information
	var sort_by = $("#ajaxwrapper .sortable[selected='yes']").attr("name");
	var order = $("#ajaxwrapper .sortable[selected='yes'] img").attr("order");
	if (order == undefined) {
		order = "up"
	}
	// Update sort information if sorting by a different field
	if(action_pair[0] == 'sort_by'){
		if(sort_by == action_pair[1]) {
			if (order == "up") {
				order = "down";
			} else {
				order = "up";
			}
		} else {
			order = "up"
		}
		
		sort_by = action_pair[1];
	}
	info["sort_by"] = sort_by;
	info["order"] = order;
	
	// Add any additional info
	$(".ajaxinfo").each( function() {
		info[this.name] = this.value;
	});
	
	//alert("Action: " + action + ", Page: " + info["page"] +", URL: " + url +", Sort_by: " + sort_by + ", Order: " + order);
	
	//info = $.param(info);
	//url = url + "?" + info 

	// Send get request
	$.get(url, info, function(data){
		//alert("POST request returned");
		$("#ajaxwrapper").html(data);
		register_listeners();
		
		if (sort_by == undefined){
			sort_by = $("#ajaxwrapper th.sortable[default='on']").attr("name");
		}
		$("#ajaxwrapper .sortable[name='"+sort_by+"']").attr("selected", "yes");
		$("#ajaxwrapper .sortable[name='"+sort_by+"'] img").attr("order", order);
		$("#ajaxwrapper .sortable[name='"+sort_by+"'] img").attr("src", IMG_ORDER[order]);
		$("img.ajaxspinner").hide()
	});
	
	return false;
}



$(document).ready(function (){
	register_listeners();
	$("#ajaxwrapper .sortable[default='on']").attr("selected", "yes");
	$("#ajaxwrapper .sortable[default='on'] img").attr("src", IMG_ORDER["up"]).attr("order", "up");	
	$("#query_button").click(function () { send_ajaxinfo("search", "#"); return false; });
	$("#query_field").keypress( function (e) { if(e.which == 13) { send_ajaxinfo("search", "#"); } });
	$(".ajaxlist_clear_items").click(function () { send_ajaxinfo("clear", "#"); return false; });
});


function toggle_options_div(options_div, img_div) {
    var options = document.getElementById(options_div);
    var toggle_img = document.getElementById(img_div);
    if ( options.style.display != 'none' ) {
        options.style.display = 'none';
        toggle_img.src = PLUS_MINUS["plus"];
    } else {
        options.style.display = '';
        toggle_img.src = PLUS_MINUS["minus"];
    }
}

