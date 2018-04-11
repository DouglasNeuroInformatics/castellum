MANAGEPY = python castellum_core/manage.py


.PHONY: bootstrap createsuperuser install makemigrations migrate run

run:
	$(MANAGEPY) runserver

bootstrap: install migrate createsuperuser

migrate:
	$(MANAGEPY) migrate

makemigrations:
	$(MANAGEPY) makemigrations

createsuperuser:
	$(MANAGEPY) shell -c "from castellum_auth.models import User; User.objects.filter(username='admin') or User.objects.create_superuser('admin', 'admin@example.com', '123')"

install:
	pip install tox ipdb
	pip install -e .
	npm install
	mkdir -p castellum_core/static/
	cp node_modules/bootstrap/dist/css/bootstrap.min.css castellum_core/static/
