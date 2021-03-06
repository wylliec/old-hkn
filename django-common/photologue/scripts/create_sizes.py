#!/usr/bin/env python

from photologue.models import *

PHOTOSIZES = (
	('thumbnail', 100, 100),
	('display', 800, 600),
	('profilepic', 100, 100),
	('tutorpic', 60, 80),
)

def add_photosizes():
	for size in PHOTOSIZES:
		p = PhotoSize(name=size[0], width=size[1], height=size[2])
		p.save()
		
def main():
	add_photosizes()
	
if __name__ == "__main__":
	main()
