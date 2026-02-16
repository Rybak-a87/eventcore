FROM python:3.12-slim

WORKDIR /usr/src/app

RUN python -m pip install --upgrade pip

COPY docker/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

WORKDIR /usr/src/app/app/database/migrations

ENTRYPOINT ["alembic"]
