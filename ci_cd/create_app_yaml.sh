#! /bin/bash

_CIRCLE_SHA1="${CIRCLE_SHA1:0:7}"
_APP_YAML_FILE='app.yaml'
_APP_YAML_TEMPLATE="### Build ${_CIRCLE_SHA1}
runtime: custom
env: flex

resources:
  cpu: 1
  memory_gb: 2

skip_files:
- ^docker-compose.yml$
- ^fabfile.py$
- ^LICENSE$
- ^Makefile$
- ^README.md$
- ^requirements-dev.txt$
- ^google-cloud-sdk^
- ci_cd/

manual_scaling:
    instances: 1

env_variables:
  BUILD: \"${_CIRCLE_SHA1}\"
  ADMIN_API_AUDIENCE: \"${ADMIN_API_AUDIENCE}\"
  ADMIN_API_CLIENT_ID: \"${ADMIN_API_CLIENT_ID}\"
  ADMIN_API_CLIENT_SECRET: \"${ADMIN_API_CLIENT_SECRET}\"
  API_AUDIENCE: \"${API_AUDIENCE}\"
  API_SIGNING_SECRET: \"${API_SIGNING_SECRET}\"
  AUTH0_DOMAIN: \"${AUTH0_DOMAIN}\"
  DB_NAME: \"${GCP_DB_NAME}\"
  DB_PASSWORD: \"${GCP_DB_PASSWORD}\"
  DB_PORT: \"${GCP_DB_PORT}\"
  DB_USER: \"${GCP_DB_USER}\"
  ENV: \"${ENV}\"
  GCP_CLOUD_SQL_CONNECTION_STRING: \"${GCP_CLOUD_SQL_CONNECTION_STRING}\"
  GCP_DJANGO_STATIC_URL:  \"${GCP_DJANGO_STATIC_URL}\"
  SECRET_KEY: \"${SECRET_KEY}\"
  GCP_SERVICE_ACCOUNT_KEY: '${GCP_SERVICE_ACCOUNT_KEY}'
  ALLOWED_HOSTS: \"${ALLOWED_HOSTS}\"
  ZOTERO_GROUP: \"${ZOTERO_GROUP}\"

beta_settings:
  cloud_sql_instances: \"${GCP_CLOUD_SQL_CONNECTION_STRING}\"
"

echo "${_APP_YAML_TEMPLATE}" > "${_APP_YAML_FILE}"
