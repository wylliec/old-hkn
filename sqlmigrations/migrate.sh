#!/bin/sh

psql -U django_website django_website_prod < $1
