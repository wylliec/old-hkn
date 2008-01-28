from hkn.settings import ROOT_URL

def hkn_vars(request):
    layout = request.session.get("layout", "-liquid")
    return {
        "ROOT_URL" : "/" + ROOT_URL,
	"LAYOUT"  : layout,
	"LAYOUT_HTML" : "hkn" + layout + ".html"
	}

