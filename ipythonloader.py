from django.db.models.loading import get_models
for m in get_models():
    globals()[m.__name__] = m
