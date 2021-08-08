# `accessmap-api`: AccessMap's user/profiles/auth API

## Why?

AccessMap users want to securely store and access settings, routing profiles, and
other information across browsers and devices.

## How?

`accessmap-api` is a fairly boilerplate Flask application (a popular Python web
framework) with roughly RESTful interfaces: it uses HTTP verbs appropriately for GET,
POST, PUT, etc. `accessmap-api` is only compatible with Python 3.6+.

## Installation

`accessmap-api` is developed using `poetry`, which makes development, releases, and
installation more simple and reproducible. The best way to install `accessmap-api`
into a development environment is to use the poetry tool

    poetry install

A guide for installing `poetry` itself can be found here:
https://poetry.eustace.io/docs/

This command will create an isolated virtual environment for all of `accessmap-api`'s
dependencies. You can now run any commands in this environment by prepending
`poetry run` to the command. We'll set up a testing database to show how it works, but
first we need to set up our configuration.

## Configuration

Configuration of `accessmap-api` is done with environment variables. Flask supports the
use of a .env file that contains `ENV_VAR=value` lines or using the default environment
variables available on the system. Note that system environment variables will
supercede entries in the .env file.

*Please note that all of the following environment variables that are marked "required"
are necessary for `accessmap-api` to function correctly and securetly.*

- `SECRET_KEY` (required): This is a secret used to sign / secure sessions during a
request context. It is very imporatnt to keep this value secure, particularly if your
application is exposed to the internet. It is a best practice to generate the value of
most secrets using a secure hashing algorithm with a good source of entropy - something
like `ssh-keygen`.

- `JWT_SECRET_KEY` (required): This is a secret used to sign JWTs issued by
`accessmap-api` and is the most important secret to get correct, as JWTs will be
publicly sent to clients (over HTTPS). It must be kept private and generated using best
practices (like `ssh-keygen`).

- `SQLALCHEMY_DATABASE_URI`: An SQLAlchemy-compatible database URI. This defauls to
an SQLite3 database stored at `/tmp/accessmap-api.db` (for development), but can be
any valid SQLAlchemy URI for postgres, mysql, etc.

- `OAUTH_CACHE_DIR`: A path used to cache OAuth data - i.e. user-authorized
token information. This makes auth workflows more efficient. This defaults to
`/tmp/accessmap-api-cache`.

- `OSM_CLIENT_ID` (required): AccessMap currently uses OpenStreetMap for
authentication. This is the OAuth 1.0a client ID of your registered application.

- `OSM_CLIENT_SECRET` (required): AccessMap currently uses OpenStreetMap for
authentication. This is the OAuth 1.0a client secret of your registered application.

- `OSM_URI`: The base API path to use when talking to OpenStreetMap for authentication.
It is important to use the testing/development server(s) when trying out new features
that might impact the data on OpenStreetMap or expose a client's credentials, so this
is set to the primary OpenStreetMap testing URI by default. For production applications
using HTTPS and secure secrets, use `https://api.openstreetmap.org`. Keep in mind that
you will need to separately register OAuth 1.0a applications for the testing
OpenStreetMap API vs. the main one, so they will have different `OSM_CLIENT_ID` and
`OSM_CLIENT_SECRET` credentials.

- `OSM_CONSUMER_CALLBACK_URI` (required): as a security precaution, this API will currently
only send OAuth callback redirects to a URI (URL) defined by this environment variable.
The callback URI defined by this variable will be appended with `access_token` and
`refresh_token` URL parameters defining a JWT access token and a JWT refresh token for
use with protected `accessmap-api` endpoints. `OSM_CONSUMER_CALLBACK_URI` should therefore
be a client URI such as an instance of `accessmap-webapp`, e.g.
`http://localhost:3000/callback` in development mode.

## Creating and migrating the database

`accessmap-api` uses `Flask-Migrate`, which uses the `alembic` library to manage
database migrations. To initialize a database, run:

    poetry run flask db upgrade

If you make changes to the database and need to create a new migration, run:

    poetry run flask db migrate

## Running `accessmap-api`

By default, `accessmap-api` runs a `werkzeug` development server. For a production
system, you should use a WSGI framework. `accessmap-api` comes with a script to assist
deployments using a WSGI runner: `wsgi.py`. It is important to note that it is
currently hard-coded to assume that you are running `accessmap-api` at the `/api`
subdirectory of your production host, for example `https://example.com/api`.
