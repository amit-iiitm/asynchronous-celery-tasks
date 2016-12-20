#!/bin/bash


celery worker -A client.celery --loglevel=info
