#!/bin/sh

set -e

docker compose up --pull always --detach

docker compose exec web python3 -m django migrateall
docker compose exec scheduler python3 -m django migrate

# Load recommended data
docker compose exec web python3 -m django loaddata groups study_types study_groups resources attributes

# Load optional demo data (WARNING: do not use in production!)
if [ "$1" = '--demo' ]; then
    docker compose exec web python3 -m django create_demo_users
    docker compose exec web python3 -m django create_demo_content
fi

echo ''
echo 'Castellum is running in the background.'
echo 'You can access it at http://127.0.0.1:8000/'
echo 'run `docker compose up` to attach to the running process.'
echo 'run `docker compose stop` to stop the running process.'
echo 'run `docker compose down` to stop the running process and delete all data.'
