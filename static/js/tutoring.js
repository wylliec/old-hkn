var color = "#6f6";
var colorcur = "#fb6";

var locked = false;
var tutoringcss = document.createElement('style');
tutoringcss.type = 'text/css';
tutoringcss.rel = 'stylesheet';
document.getElementsByTagName("head")[0].appendChild(tutoringcss);

// Highlight using these funky colors.
function highlight(className) {
	if(!locked) tutoringcss.innerHTML = '.' + className + 'cur { background: ' + colorcur + ' !important; }' +
				'.' + className + ' { background: ' + color + ' !important; }';
}

// Get rid of the css.
function unhighlight(className){
	if(!locked) tutoringcss.innerHTML = "";
}

// Highlight and stay highlighted until we click something else.
// If you do click a different class, highlight it instead of clearing.
function locklight(className){
	if (!locked){
		highlight(className);
		locked = className;
	}
	else if(locked != className){
		locked = false;
		highlight(className);
		locked = className;
	}
	else{
		locked = false;
		highlight(className);
	}

	return false;
}

