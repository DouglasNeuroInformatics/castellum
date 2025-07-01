VIRTUAL_ENV ?= .venv
MANAGEPY = $(VIRTUAL_ENV)/bin/python manage.py

.PHONY: all
all: install migrate populate run

.PHONY: run
run:
	$(MANAGEPY) runserver

.PHONY: install
install:
	if [ ! -d "$(VIRTUAL_ENV)" ]; then uv venv "$(VIRTUAL_ENV)" || python3 -m venv "$(VIRTUAL_ENV)"; fi
	uv pip install -e .[test,dev] || $(VIRTUAL_ENV)/bin/python -m pip install -e .[test,dev]
	npm install
	.misc/extract_fullcalendar_css.sh
	$(MANAGEPY) compilemessages -l de

.PHONY: migrate
migrate:
	$(MANAGEPY) migrateall

.PHONY: populate
populate:
	$(MANAGEPY) loaddata groups study_types study_groups attributes resources
	$(MANAGEPY) create_demo_users
	$(MANAGEPY) create_demo_content

.PHONY: lint
lint:
	$(VIRTUAL_ENV)/bin/ruff check --fix castellum tests

.PHONY: test
test:
	$(VIRTUAL_ENV)/bin/pytest --no-migrations

.PHONY: makemessages
makemessages:
	$(MANAGEPY) makemessages -l de -d django

.PHONY: docs
docs:
	$(VIRTUAL_ENV)/bin/sphinx-build -W -b html docs/usage/ docs_html
