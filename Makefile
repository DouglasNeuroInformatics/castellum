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

.PHONY: populate
populate: databases
	$(MANAGEPY) loaddata groups timeslots study_types study_groups resources
	$(MANAGEPY) create_attribute_descriptions
	$(MANAGEPY) create_demo_users
	$(MANAGEPY) create_demo_content

.PHONY: makemessages
makemessages:
	$(MANAGEPY) makemessages --ignore node_modules -l de -d django
	$(MANAGEPY) makemessages --ignore node_modules -l de -d djangojs

%.mo: %.po
	$(MANAGEPY) compilemessages -l de

.PHONY: remove_databases
remove_databases:
	docker-compose stop
	docker-compose rm -f

.PHONY: databases
databases:
	docker-compose up -d
	docker-compose up db_wait

.PHONY: reset_databases
reset_databases: remove_databases migrate populate

.PHONY: lint
lint:
	$(VIRTUAL_ENV)/bin/isort castellum tests
	$(VIRTUAL_ENV)/bin/flake8
	npx eslint castellum

.PHONY: test
test: databases
	$(VIRTUAL_ENV)/bin/pytest --show-capture=no tests

.PHONY: install
install: venv
	$(VIRTUAL_ENV)/bin/python -m pip install -e .[test,dev]
	npm install

.PHONY: venv
venv:
	if [ ! -d "$(VIRTUAL_ENV)" ]; then python3 -m venv "$(VIRTUAL_ENV)"; fi

.PHONY: install_githooks
install_githooks:
	cp .misc/pre-commit-hook .git/hooks/pre-commit
