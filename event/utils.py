

def add_events_metainfo(user, events):
    """
    This is very inefficient right now because the permissions framework is a little limited. In the future should maybe use manual SQL to do the view_permission filtering::

SELECT e.name, (ct.app_label || "." || p.codename) FROM auth_permission p, event_event e, django_content_type ct  WHERE e.rsvp_permission_id = p.id AND ct.id = p.content_type_id AND (ct.app_label || "." || p.codename) = "main.hkn_everyone" 
    """
    perms = user.get_all_permissions()
    events = list(events)
    for event in events:
        view_permission_code = "%s.%s" % (event.view_permission.content_type.app_label, event.view_permission.codename)
        if view_permission_code not in perms:
            events.remove(event)
            continue
        if event.rsvp_none():
            continue
        rsvp_permission_code = "%s.%s" % (event.rsvp_permission.content_type.app_label, event.rsvp_permission.codename)
        if rsvp_permission_code in perms:
            event.can_rsvp = True
        event.num_rsvps = len(event.rsvp_set.all())
    return events
    

