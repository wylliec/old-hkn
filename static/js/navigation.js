$(document).ready(function() {
	current = location.pathname.replace('/','');
	current = current.substring(0,current.indexOf('/'));
	id = "#" + current;	
	if ($(id).length != 0) {
		$(id).addClass("selected");
		submenuid = "#" + current + "_submenu";
		$(submenuid).show();	
	}
	else {			
		$(".navigation_toplevel_item:first").addClass("selected");	
		$(".submenu:first").show();
	}
	$(".navigation_toplevel_item").bind("click", 
		function () {
			$(".submenu").hide();
			$(".navigation_toplevel_item").removeClass("selected");
			$(this).addClass("selected");
			$(this).blur();
			$(".submenu").hide();
			id = "#" + $(this).attr("id") + "_submenu";
			$(id).fadeIn("fast");		
		}	
	);
});