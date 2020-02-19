VIRTUAL_ENV ?= .venv
MANAGEPY = $(VIRTUAL_ENV)/bin/python manage.py

.PHONY: all
all: bootstrap run

.PHONY: run
run: databases
	$(MANAGEPY) runserver

.PHONY: bootstrap
bootstrap: install migrate populate castellum/locale/de/LC_MESSAGES/django.mo

.PHONY: migrate
migrate: databases
	$(MANAGEPY) migrateall
	$(MANAGEPY) sync_domains

.PHONY: populate
populate: databases
	$(MANAGEPY) loaddata groups timeslots study_types
	$(MANAGEPY) create_attribute_descriptions
	$(MANAGEPY) create_demo_users
	$(MANAGEPY) create_demo_content

.PHONY: makemessages
makemessages:
	$(MANAGEPY) makemessages -l de -d django
	$(MANAGEPY) makemessages -l de -d djangojs

%.mo: %.po
	$(MANAGEPY) compilemessages -l de

.PHONY: remove_databases
remove_databases:
	docker-compose stop
	docker-compose rm -f

.PHONY: databases
databases:
	docker-compose up -d

.PHONY: reset_databases
reset_databases: remove_databases migrate populate

.PHONY: install
install:
	$(VIRTUAL_ENV)/bin/pip install -U pip
	$(VIRTUAL_ENV)/bin/pip install -r requirements-dev.txt
	$(VIRTUAL_ENV)/bin/pip install -e .
	npm install

.PHONY: install_githooks
install_githooks: .git/hooks/pre-commit

.git/hooks/%: .hooks/%
	cp $< $@
