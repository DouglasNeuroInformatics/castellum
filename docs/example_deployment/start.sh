#!/bin/sh

# The depends_on feature in docker-compose does not actually wait
# until the service is ready. So we have to scedule this manually.
#
# See https://docs.docker.com/compose/startup-order/

docker-compose pull
docker-compose up -d

# wait until the server is running
sleep 5

docker-compose run --rm web django-admin migrateall
docker-compose run --rm web django-admin sync_domains

# Load recommended sample data
docker-compose run --rm web django-admin loaddata sample_groups timeslots study_types
docker-compose run --rm web django-admin create_sample_attribute_descriptions

# Load optional demo data (WARNING: do not use in production!)
docker-compose run --rm web django-admin create_demo_users
docker-compose run --rm web django-admin create_demo_content

echo ''
echo 'castellum is running in the background.'
echo 'You can access it at http://127.0.0.1:8000/'
echo 'run `docker-compose up` to attach to the running process.'
echo 'run `docker-compose stop` to stop the running process.'
