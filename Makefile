MANAGEPY = python manage.py


.PHONY: bootstrap createsuperuser install makemigrations migrate run makemessages

run:
	$(MANAGEPY) runserver

bootstrap: install migrate createsuperuser castellum/locale/de/LC_MESSAGES/django.mo

migrate:
	$(MANAGEPY) makemigrations
	$(MANAGEPY) migrate
	$(MANAGEPY) migrate --database=contacts

createsuperuser:
	$(MANAGEPY) create_castellum_admin

collectstatic:
	$(MANAGEPY) collectstatic

makemessages:
	$(MANAGEPY) makemessages -l de -d django
	$(MANAGEPY) makemessages -l de -d djangojs

%.mo: %.po
	$(MANAGEPY) compilemessages -l de

remove_sqlite_databases:
	rm -f castellum/db.sqlite3
	rm -f castellum/contacts.sqlite3

remove_all_migration_files:
	find . -name 0*.py -delete

reset_databases: remove_sqlite_databases remove_all_migration_files migrate createsuperuser
	$(MANAGEPY) populate

install:
	pip install tox ipdb watchdog
	pip install -e .
	npm install

install-githooks: .git/hooks/pre-commit

.git/hooks/%: .hooks/%
	cp $< $@

tdd:
	watchmedo shell-command ./castellum --drop --patterns='*.py' --recursive --command='clear && tox -e py35,py36'
