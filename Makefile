# Makefile for FastAPI + PostgreSQL + Nginx + Migrations

# ---------- Build / Up / Down ----------

# Build all images
# command: make build
build:
	docker-compose build

# Up backend (in the background)
# command: make up-backend
up-backend:
	docker-compose up -d backend

# Up nginx (in the background)
# command: make up-nginx
up-nginx:
	docker-compose up -d nginx

# Up migrations (in the background)
# command: make up-nginx
up-migrations:
	docker-compose up -d migrations

# Stop all containers
# command: make down
down:
	docker-compose down

# Reset the database (only for DEV)
# command: make reset-db
reset-db:
	docker-compose down -v
	docker-compose up -d postgres_db

# ---------- Migrations ----------

# Create new migration with a message
# command: make makemigrations
makemigrations:
	docker-compose run --rm -it migrations revision --autogenerate -m "auto migration"

# Create new migration with a message
# command: make makemigrations-message msg="create initial tables"
makemigrations-message:
	@if [ -z "$(msg)" ]; then \
		echo "Error: Indicate the migration message, for example:"; \
		echo "make makemigrations msg=\"add users table\""; \
		exit 1; \
	fi
	docker-compose run --rm -it migrations revision --autogenerate -m "$(msg)"

# Create empty migration
# command: make makemigrations-empty msg="empty migration"
makemigrations-empty:
	@if [ -z "$(msg)" ]; then \
		echo "Error: Provide migration message, e.g. make makemigrations-empty msg=\"empty migration\""; \
		exit 1; \
	fi
	docker-compose run --rm -it migrations revision -m "$(msg)"

# Apply all migrations
# command: make migrate
migrate:
	docker-compose run --rm -it migrations upgrade head

# Rollback last migration
# command: make migrate-rollback
migrate-rollback:
	docker-compose run --rm -it migrations downgrade -1

# Mark migrations as performed without execution (FAKE)
# command: make migrate-fake-current
migrate-fake-current:
	docker-compose run --rm -it migrations stamp head

# Mark specific migration as completed (FAKE)
# command: make migrate-fake rev=123456abcdef
migrate-fake:
	@if [ -z "$(rev)" ]; then \
		echo "Error: Provide migration revision, e.g. make migrate-fake rev=123456abcdef"; \
		exit 1; \
	fi
	docker-compose run --rm -it migrations stamp $(rev)

# ---------- Interactive Shell / Bash ----------

# Open bash inside backend
# command: make bash-backend
bash-backend:
	docker exec -it eventcore bash

# Open bash inside postgres
# command: make bash-postgres
bash-postgres:
	docker exec -it eventcore-pgsql-db bash

# Open bash inside migrations
# command: make bash-migrations
bash-migrations:
	migrate: docker-compose run --rm -it migrations

# Open Python shell inside backend (interactive)
# command: make shell
shell:
	docker exec -it eventcore python

# Open Python shell with models and session (like Django shell)
# command: make shell-plus
shell-plus:
	docker exec -it -w /usr/src/app eventcore python -m app.shell

# ---------- Logs ----------

# Watch backend logs
# command: make logs-backend
logs-backend:
	docker-compose logs -f backend

# Watch nginx logs
# command: make logs-nginx
logs-nginx:
	docker-compose logs -f nginx

# ---------- Passwords and Secrets ----------

# Return a random key (32 bytes → base64)
# command: make get-pass-32
get-pass-32:
	openssl rand -base64 32

# Return a random key (24 bytes → base64)
# command: make get-pass-24
get-pass-24:
	openssl rand -base64 24

# HEX password for database (32 bytes → 64 hex chars)
# command: make get-pass-hex
get-pass-hex:
	openssl rand -hex 32

# Update SECRET_KEY in .env
# command: make set-secret
set-secret:
	@new_secret=$$(openssl rand -base64 32); \
	sed -i.bak "s/^JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$$new_secret/" .env; \
	echo "✅ SECRET_KEY updated"

# Update POSTGRES_PASSWORD in .env
# command: make set-db-pass
set-db-pass:
	@new_pass=$$(openssl rand -hex 32); \
	sed -i.bak "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$$new_pass/" .env; \
	echo "✅ POSTGRES_PASSWORD updated"

# Update both SECRET_KEY and POSTGRES_PASSWORD
# command: make set-env-secrets
set-env-secrets: set-secret set-db-pass

# Show current .env secrets (safe to use locally)
# command: make show-env
show-env:
	@echo "Current secrets in .env:" \
	@grep -E '^(SERVER|JWT_SECRET_KEY|POSTGRES_PASSWORD|POSTGRES_USER|POSTGRES_DB)=' .env || echo "No secrets found"
	#docker-compose run --rm backend alembic init app/database/migrations

