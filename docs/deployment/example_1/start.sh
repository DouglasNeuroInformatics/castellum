#!/bin/sh

set -e

docker-compose pull
docker-compose up -d

# wait for databases
docker-compose run --rm db_wait

docker-compose run --rm web django-admin migrateall
docker-compose run --rm scheduler django-admin migrate

# Load recommended data
docker-compose run --rm web django-admin loaddata groups study_types study_groups resources attribute_descriptions

# Load optional demo data (WARNING: do not use in production!)
if [ "$1" = '--demo' ]; then
    docker-compose run --rm web django-admin create_demo_users
    docker-compose run --rm web django-admin create_demo_content
fi

echo ''
echo 'Castellum is running in the background.'
echo 'You can access it at http://127.0.0.1:8000/'
echo 'run `docker-compose up` to attach to the running process.'
echo 'run `docker-compose stop` to stop the running process.'
echo 'run `docker-compose down` to stop the running process and delete all data.'
