MANAGEPY = python manage.py

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
remove_databases:
	docker-compose stop db_contacts db_default
	docker-compose rm -f db_contacts db_default

.PHONY: remove_migrations
remove_migrations:
	find castellum -name 0*.py -delete

.PHONY: databases
databases:
	docker-compose up -d db_contacts db_default
	sleep 2

.PHONY: reset_databases
reset_databases: remove_databases remove_migrations databases migrate populate

.PHONY: bootstrap
install:
	pip install tox ipdb watchdog django-debug-toolbar
	pip install -e .
	npm install

.PHONY: install_githooks
install_githooks: .git/hooks/pre-commit

.git/hooks/%: .hooks/%
	cp $< $@

.PHONY: tdd
tdd:
	watchmedo shell-command . --drop --patterns='*.py' --recursive --command='clear && tox -e py35,py36 -- --disable-warnings -m unittest'
