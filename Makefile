VIRTUAL_ENV ?= .venv
MANAGEPY = $(VIRTUAL_ENV)/bin/python manage.py

.PHONY: all
all: bootstrap run

.PHONY: run
run:
	$(MANAGEPY) runserver

.PHONY: bootstrap
bootstrap: install migrate populate castellum/locale/de/LC_MESSAGES/django.mo

.PHONY: migrate
migrate:
	$(MANAGEPY) migrateall

.PHONY: populate
populate:
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
	rm -f castellum/db.sqlite3
	rm -f castellum/contacts.sqlite3

.PHONY: reset_databases
reset_databases: remove_databases migrate populate

.PHONY: lint
lint:
	$(VIRTUAL_ENV)/bin/isort castellum tests
	$(VIRTUAL_ENV)/bin/flake8
	npx eslint castellum

.PHONY: test
test:
	$(VIRTUAL_ENV)/bin/pytest --show-capture=no tests

.PHONY: install
install: venv
	$(VIRTUAL_ENV)/bin/pip install -U pip
	$(VIRTUAL_ENV)/bin/pip install -r requirements-dev.txt
	$(VIRTUAL_ENV)/bin/pip install -e .
	npm install

.PHONY: venv
venv:
	if [ ! -d "$(VIRTUAL_ENV)" ]; then python3 -m venv "$(VIRTUAL_ENV)"; fi

.PHONY: install_githooks
install_githooks: .git/hooks/pre-commit

.git/hooks/%: .hooks/%
	cp $< $@
