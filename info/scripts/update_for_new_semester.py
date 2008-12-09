#!/usr/bin/env python
import setup_settings

def main():
    for p in Person.objects.all():
        p.reconcile_status()
        p.save()
    
