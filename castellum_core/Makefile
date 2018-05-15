MANAGEPY = python castellum_core/manage.py


.PHONY: bootstrap createsuperuser install makemigrations migrate run

run:
	$(MANAGEPY) runserver

bootstrap: install migrate createsuperuser

migrate:
	$(MANAGEPY) migrate

makemigrations:
	$(MANAGEPY) makemigrations

createsuperuser:
	$(MANAGEPY) create_castellum_admin

collectstatic:
	$(MANAGEPY) collectstatic

install:
	pip install tox ipdb
	pip install -e .
	npm install
