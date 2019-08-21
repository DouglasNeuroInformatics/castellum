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
	$(MANAGEPY) makemigrations
	$(MANAGEPY) migrateall

.PHONY: populate
populate: databases
	$(MANAGEPY) loaddata sample_groups timeslots
	$(MANAGEPY) create_sample_attribute_descriptions
	$(MANAGEPY) create_sample_users
	$(MANAGEPY) populate

.PHONY: makemessages
makemessages:
	$(MANAGEPY) makemessages -l de -d django
	$(MANAGEPY) makemessages -l de -d djangojs

%.mo: %.po
	$(MANAGEPY) compilemessages -l de

.PHONY: remove_databases
remove_databases: databases
	psql postgres postgres -h localhost -p 6670 -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO postgres; GRANT ALL ON SCHEMA public TO public;"
	psql postgres postgres -h localhost -p 6671 -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO postgres; GRANT ALL ON SCHEMA public TO public;"

.PHONY: remove_migrations
remove_migrations:
	find castellum -name 0*.py -delete

.PHONY: databases
databases:
	docker-compose up -d db_contacts db_default
	sleep 2

.PHONY: reset_databases
reset_databases: remove_databases remove_migrations migrate populate

.PHONY: bootstrap
install:
	$(VIRTUAL_ENV)/bin/pip install -U pip
	$(VIRTUAL_ENV)/bin/pip install tox ipdb django-debug-toolbar
	$(VIRTUAL_ENV)/bin/pip install -e .
	npm install

.PHONY: install_githooks
install_githooks: .git/hooks/pre-commit

.git/hooks/%: .hooks/%
	cp $< $@
