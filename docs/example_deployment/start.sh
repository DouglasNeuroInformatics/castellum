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
docker-compose run --rm web django-admin loaddata sample_groups timeslots
docker-compose run --rm web django-admin create_sample_users
docker-compose run --rm web django-admin populate

echo ''
echo 'castellum is running in the background.'
echo 'run `docker-compose up` to attach to the running process.'
echo 'run `docker-compose stop` to stop the running process.'
