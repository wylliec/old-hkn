/** This function sets up the menu. It creates listeners for all of the links and displays
 * the appropriate submenu when needed.
 */
/**
 * Finds what path we're at currently and extracts the lowest subdirectory.
 * It will then look to see if there is a toplevel menu that has that name. If so,
 * it will make it selected. If not it will pick the first one it finds and make that 
 * selected. Might be deprecated soon.
 */
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
			$(".navigation_toplevel_item").removeClass("selected");
			$(this).addClass("selected");
			$(this).blur();
			$(".submenu").hide();
			id = "#" + $(this).attr("id") + "_submenu";
			$(id).fadeIn("fast");		
		}	
	);
});