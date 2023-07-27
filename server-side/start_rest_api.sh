#! /bin/bash 

echo "Starting webserver"

cd /home/bokajnevs/programming/website

uvicorn webb_api:app --host 192.168.0.127 --reload