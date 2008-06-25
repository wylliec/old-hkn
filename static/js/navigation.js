$(document).ready(function() {
	$(".submenu:first").show();
	$(".navigation_toplevel_item:first").addClass("selected");
	$(".navigation_toplevel_item").bind("click", 
		function () {
			$(".submenu").hide();
			$(".navigation_toplevel_item").removeClass("selected");
			$(this).addClass("selected");
			$(".submenu").hide();
			id = "#" + $(this).attr("id") + "_submenu";
			$(id).fadeIn("fast");		
		}	
	);
});