#!/usr/bin/env python
import hkn_settings
from django.conf import settings

import course.scripts; course.scripts.import_all(settings.SERVER_ROOT)
