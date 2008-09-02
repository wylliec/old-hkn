#!/usr/bin/env python
import hkn_settings
from hkn.main.models import HKN

properties = {"semester": "fa08",
              "vp": "Aimee Moriwaki",
              "hkn_tutor_version" : "-1",
              }

def main():
    for k,v in properties.items():
        prop, c = HKN.objects.get_or_create(name=k)
        prop.value = v
        prop.save()

if __name__ == "__main__":
    main()
        
