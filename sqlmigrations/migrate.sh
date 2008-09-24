#!/bin/sh

psql -U django_website django_website_dev < $1
