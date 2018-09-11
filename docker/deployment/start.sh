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
docker-compose -f docker-compose.yml -f docker-compose.manage.yml up migrate_default
docker-compose -f docker-compose.yml -f docker-compose.manage.yml up migrate_contacts
docker-compose -f docker-compose.yml -f docker-compose.manage.yml up createsuperuser
docker-compose -f docker-compose.yml -f docker-compose.manage.yml up populate
fg
