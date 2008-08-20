#!/usr/bin/env python
import os

def import_all(path):
    import setup_settings
    setup_settings.PATH = path
    setup_settings.setup()

