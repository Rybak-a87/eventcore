FROM python:3.12-slim

WORKDIR /usr/src/app

RUN python -m pip install --upgrade pip

COPY docker/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY docker/backend/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

COPY src ./src

ENTRYPOINT ["entrypoint.sh"]
