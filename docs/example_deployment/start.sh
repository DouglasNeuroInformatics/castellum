#!/bin/sh

# The depends_on feature in docker-compose does not actually wait
# until the service is ready. So we have to scedule this manually.
#
# See https://docs.docker.com/compose/startup-order/

# activate job control so we can use fg
set -m

docker-compose pull
docker-compose up &
sleep 5  # wait until the server is running
docker-compose run web django-admin migrateall
docker-compose run web django-admin create_castellum_admin
docker-compose run web django-admin loaddata timeslots
docker-compose run web django-admin populate
fg
