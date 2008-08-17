from request.constants import REQUEST_OBJECT_CONFIRM_ATTR, REQUEST_OBJECT_METAINFO_ATTR, REQUEST_OBJECT_COMMENT_ATTR

class AlreadyRegistered(Exception):
    pass

registry = []

def register(model, model_metainfo_function, confirmation_attr='confirm', comment_attr=None, request_confirmation_function_attr=None):
    if model in registry:
        raise AlreadyRegistered('Model %s already registered for requests framework!' % model.__name__)
    registry.append(model)

    setattr(model, REQUEST_OBJECT_CONFIRM_ATTR, confirmation_attr)
    setattr(model, REQUEST_OBJECT_METAINFO_ATTR, model_metainfo_function)
    if comment_attr:
        setattr(model, REQUEST_OBJECT_COMMENT_ATTR, comment_attr)
    if request_confirmation_function_attr:
        setattr(model, request_confirmation_function_attr, request_confirmation)

