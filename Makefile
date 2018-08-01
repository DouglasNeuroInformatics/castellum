MANAGEPY = python manage.py


.PHONY: bootstrap createsuperuser install makemigrations migrate run makemessages

run:
	$(MANAGEPY) runserver

bootstrap: install migrate createsuperuser castellum/locale/de/LC_MESSAGES/django.mo

migrate:
	$(MANAGEPY) migrate
	$(MANAGEPY) migrate --database=contacts

makemigrations:
	$(MANAGEPY) makemigrations

createsuperuser:
	$(MANAGEPY) create_castellum_admin

collectstatic:
	$(MANAGEPY) collectstatic

makemessages:
	$(MANAGEPY) makemessages -l de -d django
	$(MANAGEPY) makemessages -l de -d djangojs

%.mo: %.po
	$(MANAGEPY) compilemessages -l de

install:
	pip install tox ipdb watchdog
	pip install -e .
	npm install

tdd:
	watchmedo shell-command ./castellum --drop --patterns='*.py' --recursive --command='clear && tox -e py35,py36'
