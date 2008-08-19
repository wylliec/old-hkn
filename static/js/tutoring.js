var color = "#6f6";
var colorcur = "#fb6";

var locked = false;
var highlighted = false;

function getObjectCss () {
	var css = null;
	try {
		var head = document.getElementsByTagName("head").item(0);
		head.appendChild(document.createElement("style"));
		css = document.styleSheets[document.styleSheets.length-1];
	} catch (ex) {
		css = document.createStyleSheet("tutoringStyle.css");
	}
	return css;
}

function addCssRule (css, selector, rule) {
	if (css.insertRule) {
		css.insertRule(selector + " { " + rule + " }", css.cssRules.length);
	} else if(css.addRule) {
		css.addRule(selector, rule);
	}
}

function deleteCssRule (css, selector) {
	if (!selector) {
		return;
	}

	if (tutoringcss.cssRules) {
		rules = tutoringcss.cssRules;
	}
	else if (tutoringcss.rules) {
		rules = tutoringcss.rules;
	}
	else {
		return;
	}

	for (var it = 0; it < rules.length; it++) {
		if (rules[it].selectorText.toLowerCase() == selector.toLowerCase()) {
			if (tutoringcss.deleteRule) {
				tutoringcss.deleteRule(it);
			}
			else if (tutoringcss.removeRule) {
				tutoringcss.removeRule(it);
			}
			return;
		}
	}
}

// Highlight using these funky colors.
function highlight (className) {
	if (!locked) {
		deleteCssRule(tutoringcss, '.' + highlighted + 'cur');
		deleteCssRule(tutoringcss, '.' + highlighted);
		highlighted = className;
		addCssRule(tutoringcss, '.' + className + 'cur', 'background: ' + colorcur + ' !important');
		addCssRule(tutoringcss, '.' + className, 'background: ' + color + ' !important');
	}
}

// Get rid of the css.
function unhighlight (className) {
	if (!locked) {
		deleteCssRule(tutoringcss, '.' + highlighted + 'cur');
		deleteCssRule(tutoringcss, '.' + highlighted);
		highlighted = false;
	}
}

// Highlight and stay highlighted until we click something else.
// If you do click a different class, highlight it instead of clearing.
function locklight (className) {
	if (!locked){
		highlight(className);
		locked = className;
	}
	else if (locked != className) {
		locked = false;
		highlight(className);
		locked = className;
	}
	else {
		locked = false;
		highlight(className);
	}

	return false;
}

var tutoringcss = getObjectCss();
