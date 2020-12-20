#!/bin/sh

python manage.py --no-input migrate
python manage.py --no-input collectstatic
python manage.py runserver 0.0.0.0:8000
