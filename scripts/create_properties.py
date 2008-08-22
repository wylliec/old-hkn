#!/usr/bin/env python
import hkn_settings
from hkn.main.models import HKN

properties = {"semester": "sp08",
              "vp": "Nir Ackner",
              }

def main():
    for k,v in properties.items():
        prop, c = HKN.objects.get_or_create(name=k)
        prop.value = v
        prop.save()

if __name__ == "__main__":
    main()
        
