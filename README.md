# EventCore API

## Setup Environment

Create an environment file:

`cp .env.example .env`

for dev if not running docker

`cp dev.py src/dev.py`

---

## Build Containers

Build all containers:

`docker-compose build`

or using make:

`make build`

---

## Start Containers

### For Development

Start only the backend:

`docker-compose up -d backend`

or using make:

`make up-backend`

### For Production

Start Nginx (and dependent services):

`docker-compose up -d nginx`

or using make:

`make up-nginx`

---

## Run Migrations

Create a new migration:

`docker-compose run --rm -it migrations revision --autogenerate -m "auto migration"`

or using make:

`make makemigrations`
