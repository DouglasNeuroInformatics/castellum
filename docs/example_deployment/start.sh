#!/bin/sh

# The depends_on feature in docker-compose does not actually wait
# until the service is ready. So we have to scedule this manually.
#
# See https://docs.docker.com/compose/startup-order/

# activate job control so we can use fg
set -m

docker-compose pull
docker-compose up &

# wait until the server is running
for i in `seq 10` ; do
    nc -z "localhost" "8000" > /dev/null 2>&1

    if [ $? -ne 0 ] ; then
        sleep 1
    fi
done

docker-compose run web django-admin migrateall
docker-compose run web django-admin create_castellum_admin
docker-compose run web django-admin loaddata timeslots --database=contacts
docker-compose run web django-admin loaddata attribute_descriptions --database=default
docker-compose run web django-admin populate

fg
