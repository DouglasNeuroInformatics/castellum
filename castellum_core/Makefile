MANAGEPY = python castellum_core/manage.py


.PHONY: bootstrap createsuperuser install makemigrations migrate run makemessages

run:
	$(MANAGEPY) runserver

bootstrap: install migrate createsuperuser castellum_core/locale/de/LC_MESSAGES/django.mo

migrate:
	$(MANAGEPY) migrate
	$(MANAGEPY) migrate --database=subject_management

makemigrations:
	$(MANAGEPY) makemigrations

createsuperuser:
	$(MANAGEPY) create_castellum_admin

collectstatic:
	$(MANAGEPY) collectstatic

makemessages:
	$(MANAGEPY) makemessages -d django
	$(MANAGEPY) makemessages -d djangojs

%.mo: %.po
	$(MANAGEPY) compilemessages

install:
	pip install tox ipdb
	pip install -e .
	npm install
