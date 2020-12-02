# Docker Environment Variables

All environment variables used by docker-compose are defined here. There are
no api keys, just define them as random strings in the following files:

## .env.django

>Accessed by `web` and `tasks` services.

- DJANGO_SECRET
- DJANGO_SUPERUSER_USERNAME
- DJANGO_SUPERUSER_EMAIL
- DJANGO_SUPERUSER_PASSWORD

## .env.db

>For mysql database initialization

- MYSQL_RANDOM_ROOT_PASSWORD=true

## .env.dbcreds

>Credentials for accessing the database, used by `web` and `tasks`

- MYSQL_DATABASE
- MYSQL_USER
- MYSQL_PASSWORD
