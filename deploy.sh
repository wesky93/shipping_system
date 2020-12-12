#!/bin/bash

echo 'Starting to Deploy...'
ssh ubuntu@15.165.35.128 " sudo docker image prune -f
        cd shipping_system
        sudo docker-compose down
        git fetch origin
        git reset --hard origin/main
        sudo docker-compose build
        sudo docker-compose --rm run web python manage.py migrate
        sudo docker-compose up -d
        "
echo 'Deployment completed successfully'