MANAGEPY = python manage.py


.PHONY: bootstrap populate install makemigrations migrate run makemessages

run: start_database_containers
	$(MANAGEPY) runserver

bootstrap: install migrate populate castellum/locale/de/LC_MESSAGES/django.mo

migrate: start_database_containers
	$(MANAGEPY) makemigrations
	$(MANAGEPY) migrateall

populate: start_database_containers
	$(MANAGEPY) loaddata sample_groups timeslots
	$(MANAGEPY) create_sample_attribute_descriptions
	$(MANAGEPY) create_sample_users
	$(MANAGEPY) populate

collectstatic:
	$(MANAGEPY) collectstatic

makemessages:
	$(MANAGEPY) makemessages -l de -d django
	$(MANAGEPY) makemessages -l de -d djangojs

%.mo: %.po
	$(MANAGEPY) compilemessages -l de

remove_databases:
	docker-compose stop db_contacts db_default
	docker-compose rm -f db_contacts db_default

remove_all_migration_files:
	find castellum -name 0*.py -delete

start_database_containers:
	docker-compose up -d db_contacts db_default
	sleep 2

reset_databases: remove_databases remove_all_migration_files start_database_containers migrate populate

install:
	pip install tox ipdb watchdog django-debug-toolbar
	pip install -e .
	npm install

install-githooks: .git/hooks/pre-commit

.git/hooks/%: .hooks/%
	cp $< $@

tdd:
	watchmedo shell-command . --drop --patterns='*.py' --recursive --command='clear && tox -e py35,py36 -- --disable-warnings -m unittest'
