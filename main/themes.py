from django.shortcuts import render_to_response

THEMES = {}

def local_namespace():
    base = {"landing_background" : "#F3F8F8",
            "landing_border" : "#5C7C0B",
            }
            
    theme_hisham = { "landing_background" : "#dfefe2" }

    

    themes_list = [x for x in locals().items() if x[0].startswith("theme_")]
    THEMES['base'] = base
    THEMES['base'].update({"theme_name" : "base"})
    for theme, val in themes_list:
        theme = theme.replace("theme_", "")
        THEMES[theme] = base.copy()
        THEMES[theme].update(val)
        THEMES[theme].update({ "theme_name" : theme})

local_namespace()

def theme_css(request, css_file):
    theme_name = request.session.get('theme', 'base')
    theme = THEMES[theme_name]
    resp = render_to_response("css/hkn-%s.css" % css_file, theme)
    resp['Content-Type'] = 'text/css'
    return resp
