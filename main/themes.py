from django.shortcuts import render_to_response

THEMES = {}

def local_namespace():
    base = {"primary_color" : "#FFFFFF",
            "some_other_color" : "#EEEEEE",
            "links_color" : "#AAAAAA"
            }

    theme_blue = {   "primary_color" : "blue",
                    "links_color" : "#AEAEAE"
                }

    theme_green = {   "primary_color" : "green",
                    "links_color" : "#AEAEAE"
                }

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
    return render_to_response("css/hkn-%s.css" % css_file, theme)
