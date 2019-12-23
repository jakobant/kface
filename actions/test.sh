#!/bin/bash
EXEC_PATH=$(dirname "$0")
source $EXEC_PATH/envs.sh

err_report() {
    docker stop kface
    docker stop redis
    docker rm --force redis
    docker rm --force kface
}

trap err_report ERR
set -e

docker run --name redis -p 6379:6379 -d redis
docker run -it  --name kface -p 8880:80 -e REDIS="redis" --link redis:redis -d $REPO/$NAME:$TAG
sleep 30
docker ps

curl -XPOST -Fname='Barak Obama' -Ffile=@$EXEC_PATH/../test/obama.jpeg http://localhost:8880/upload
curl -XPOST -Ffile=@$EXEC_PATH/../test/obamaandbiden.jpg http://localhost:8880/who
curl http://localhost:8880/list_name

sleep 10
docker stop redis
docker rm --force redis
docker rm --force kface
