#!/bin/bash


name="video-db"

# Only run db if video-db containter isnt already running
[[ $(docker ps -f "name=$name" --format '{{.Names}}') == $name ]] || 
sudo docker run -d --name video-db -e POSTGRES_USER=dbuser -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=video-db -p 5432:5432 postgres:13
cat sql-scripts/init.sql | sudo docker exec -i video-db psql -U dbuser -d video-db
