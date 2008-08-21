#!/usr/bin/env python
import hkn_settings
from django.conf import settings

import exam.scripts; exam.scripts.import_all(settings.SERVER_ROOT)
