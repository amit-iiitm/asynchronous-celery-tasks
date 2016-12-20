#!/bin/bash


redis-server &
celery worker -A client.celery --loglevel=info & 
python client.py &
