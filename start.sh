#!/bin/sh
alembic upgrade head

gunicorn -w 4 -b 0.0.0.0:80 todo_app:app