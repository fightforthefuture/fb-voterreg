#!/bin/bash

rm db.sqlite
./manage.py syncdb --noinput
./manage.py migrate
