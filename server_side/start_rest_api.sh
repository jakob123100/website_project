#! /bin/bash 

echo "Starting webserver"

cd /home/bokajnevs/programming/website/website_project/server_side

uvicorn rest_api:app --host 192.168.0.127 --reload