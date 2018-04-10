MANAGEPY = python castellum_core/manage.py


run:
	$(MANAGEPY) runserver

bootstrap: install migrate createsuperuser

migrate:
	$(MANAGEPY) migrate

makemigrations:
	$(MANAGEPY) makemigrations

createsuperuser:
	$(MANAGEPY) shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', '123')"

install:
	pip install tox ipdb
	pip install -e .
