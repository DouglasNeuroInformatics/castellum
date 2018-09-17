MANAGEPY = python manage.py


.PHONY: bootstrap createsuperuser install makemigrations migrate run makemessages

run:
	$(MANAGEPY) runserver

bootstrap: install migrate createsuperuser castellum/locale/de/LC_MESSAGES/django.mo

migrate:
	$(MANAGEPY) makemigrations
	$(MANAGEPY) migrateall

createsuperuser:
	$(MANAGEPY) create_castellum_admin

collectstatic:
	$(MANAGEPY) collectstatic

makemessages:
	$(MANAGEPY) makemessages -l de -d django
	$(MANAGEPY) makemessages -l de -d djangojs

%.mo: %.po
	$(MANAGEPY) compilemessages -l de

remove_databases:
	psql postgres postgres -h localhost -p 6670 -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO postgres; GRANT ALL ON SCHEMA public TO public;"
	psql postgres postgres -h localhost -p 6671 -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO postgres; GRANT ALL ON SCHEMA public TO public;"

remove_all_migration_files:
	find castellum -name 0001_initial.py -delete
	find castellum -name *_auto_*.py -delete

reset_databases: remove_databases remove_all_migration_files migrate createsuperuser
	$(MANAGEPY) loaddata timeslots --database=contacts
	$(MANAGEPY) populate

install:
	pip install tox ipdb watchdog django-debug-toolbar
	pip install -e .
	npm install

install-githooks: .git/hooks/pre-commit

.git/hooks/%: .hooks/%
	cp $< $@

tdd:
	watchmedo shell-command ./castellum --drop --patterns='*.py' --recursive --command='clear && tox -e py35,py36'
