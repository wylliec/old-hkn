$(document).ready(function() {
	$(".submenu:first").show();
	$(".navigation_toplevel_item").bind("click", 
		function () {
			$(".submenu").hide();
			id = "#" + $(this).attr("id") + "_submenu";
			$(id).fadeIn("slow");		
		}	
	);
});