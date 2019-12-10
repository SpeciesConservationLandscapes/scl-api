#!/usr/bin/env bash

_CIRCLE_SHA1="${CIRCLE_SHA1:0:7}"
_APP_YAML_FILE='app.yaml'
_APP_YAML_TEMPLATE="### Build ${_CIRCLE_SHA1}
runtime: custom
env: flex

skip_files:
- ^docker-compose.yml$
- ^fabfile.py$
- ^LICENSE$
- ^Makefile$
- ^README.md$
- ^requirements-dev.txt$
- ci_cd/

manual_scaling:
    instances: 1

env_variables:
  BUILD: \"${_CIRCLE_SHA1}\"
  SECRET_KEY: \"${SECRET_KEY}\"
  DB_NAME: \"${DB_NAME}\"
  DB_USER: \"${DB_USER}\"
  DB_PASSWORD: \"${DB_PASSWORD}\"
  # enable when running locally
  # DB_HOST: \"${DB_HOST}\"
  DB_PORT: \"${DB_PORT}\"
  ENV: \"${ENV}\"
  API_AUDIENCE: \"${API_AUDIENCE}\"
  API_SIGNING_SECRET: \"${API_SIGNING_SECRET}\"
  ADMIN_API_CLIENT_ID: \"${ADMIN_API_CLIENT_ID}\"
  ADMIN_API_CLIENT_SECRET: \"${ADMIN_API_CLIENT_SECRET}\"
  ADMIN_API_AUDIENCE: \"${ADMIN_API_AUDIENCE}\"
  AUTH0_DOMAIN: \"${AUTH0_DOMAIN}\"
  CLOUD_SQL_CONNECTION_STRING: \"${CLOUD_SQL_CONNECTION_STRING}\"

beta_settings:
  cloud_sql_instances: \"${CLOUD_SQL_CONNECTION_STRING}\"
"

echo "${_APP_YAML_TEMPLATE}" > "${_APP_YAML_FILE}"
