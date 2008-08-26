

def add_events_metainfo(events):
    """
    This is very inefficient right now because the permissions framework is a little limited. In the future should maybe use manual SQL to do the view_permission filtering::

SELECT e.name, (ct.app_label || "." || p.codename) FROM auth_permission p, event_event e, django_content_type ct  WHERE e.rsvp_permission_id = p.id AND ct.id = p.content_type_id AND (ct.app_label || "." || p.codename) = "main.hkn_everyone" 
    """
    for event in events:
        if event.rsvp_none():
            continue
        event.can_rsvp = True
        event.num_rsvps = event.rsvp_set.count()
    return events
    

