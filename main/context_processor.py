from hkn.settings import ROOT_URL, STATIC_PREFIX

def hkn_vars(request):
    layout = request.session.get("layout", "-green")
    return {
        "ROOT_URL" : "/" + ROOT_URL,
        "STATIC_PREFIX" : STATIC_PREFIX,
	"LAYOUT"  : layout,
	"LAYOUT_HTML" : "hkn" + layout + ".html"
	}

