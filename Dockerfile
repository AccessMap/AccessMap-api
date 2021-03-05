FROM python:3.7-alpine3.11

# Compiler deps
RUN apk add --no-cache gcc musl-dev

# Rust compiler required for cryptography module. Has to be newer version
ENV PATH=/root/.cargo/bin:$PATH
RUN apk add --no-cache curl
RUN curl https://sh.rustup.rs -sSf | \
    sh -s -- --default-toolchain stable -y
RUN rustup toolchain install 1.41.1

# CFFI deps
RUN apk add --no-cache libffi-dev openssl-dev

# psycopg2 deps
RUN apk add postgresql-dev

RUN pip install --upgrade pip

RUN pip install poetry

COPY . /www/

WORKDIR /www/

RUN poetry install

CMD ["poetry", "run", "python", "run.py"]
