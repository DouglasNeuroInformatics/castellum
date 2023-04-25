VIRTUAL_ENV ?= .venv
MANAGEPY = $(VIRTUAL_ENV)/bin/python manage.py

.PHONY: all
all: install migrate populate compilemessages run

.PHONY: run
run:
	$(MANAGEPY) runserver

.PHONY: install
install:
	if [ ! -d "$(VIRTUAL_ENV)" ]; then python3 -m venv "$(VIRTUAL_ENV)"; fi
	$(VIRTUAL_ENV)/bin/python -m pip install wheel
	$(VIRTUAL_ENV)/bin/python -m pip install -e .[test,dev]
	npm install
	.misc/extract_fullcalendar_css.sh

.PHONY: migrate
migrate:
	$(MANAGEPY) migrateall

.PHONY: populate
populate:
	$(MANAGEPY) loaddata groups study_types study_groups attribute_descriptions resources
	$(MANAGEPY) create_demo_users
	$(MANAGEPY) create_demo_content

.PHONY: lint
lint:
	$(VIRTUAL_ENV)/bin/isort castellum tests
	$(VIRTUAL_ENV)/bin/flake8 castellum tests
	npx eslint castellum

.PHONY: test
test:
	$(VIRTUAL_ENV)/bin/pytest --no-migrations

.PHONY: makemessages
makemessages:
	$(MANAGEPY) makemessages --ignore node_modules -l de -d django
	$(MANAGEPY) makemessages --ignore node_modules -l de -d djangojs

.PHONY: compilemessages
compilemessages:
	$(MANAGEPY) compilemessages -l de
