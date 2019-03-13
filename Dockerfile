FROM python:3.7.2-alpine3.9

# Compiler deps
RUN apk add --no-cache gcc musl-dev

# CFFI deps
RUN apk add --no-cache libffi-dev openssl-dev

# psycopg2 deps
RUN apk add postgresql-dev

RUN pip install poetry

COPY . /www/

WORKDIR /www/

RUN poetry install

CMD ["poetry", "run", "python", "run.py"]
