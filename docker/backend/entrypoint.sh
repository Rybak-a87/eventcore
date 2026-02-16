#!/bin/bash
set -e

# Check DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
  export DATABASE_URL="sqlite+aiosqlite:///./db_sqlite/db_first_test.sqlite3"
  echo "📌 DATABASE_URL not set, using SQLite ($DATABASE_URL)"
else
  echo "📌 Using DATABASE_URL=$DATABASE_URL"
fi

# If it is postgres - we are waiting for it to rise
#if [[ "$DATABASE_URL" == postgresql+asyncpg* ]]; then
#  echo "⏳ Waiting for Postgres at $POSTGRES_HOST:$POSTGRES_PORT..."
#  until nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
#    sleep 1
#  done
#  echo "✅ Postgres is up!"
#fi

# Run migrations
#echo "📌 Running migrations..."
#alembic upgrade head

# If the arguments are transferred, we launch them (for example, alembic, Shell, etc.)
if [ "$#" -gt 0 ]; then
  echo "📌 Executing custom command: $@"
  exec "$@"
else
  # By default - launch the server
  echo "🚀 Starting FastAPI on $SERVER_HOST:$SERVER_PORT --- $SERVER"
  exec uvicorn app.main:app --host "${SERVER_HOST:-0.0.0.0}" --port "${SERVER_PORT:-8000}" --reload
fi
