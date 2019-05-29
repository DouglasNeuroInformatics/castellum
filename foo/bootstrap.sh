#!/bin/sh -e

python3 -m venv .venv
. .venv/bin/activate
pip install ..
python manage.py migrateall
python manage.py runserver
