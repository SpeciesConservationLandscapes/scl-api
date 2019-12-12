#! /bin/bash

# CircleCI usage
# name: Run DB migration
# run: docker exec -it api_service /var/projects/webapp/migrate_db.sh

_GCP_CREDENTIAL_STRING=${GCP_CREDENTIAL_STRING}
_GCP_CLOUD_SQL_CONNECTION_STRING=${GCP_CLOUD_SQL_CONNECTION_STRING}
_GCP_DB_PORT=${GCP_DB_PORT}

# Override environment variables
export DB_NAME="${GCP_DB_NAME}"
export DB_HOST="127.0.0.1"
export DB_PORT="${GCP_DB_PORT}"
export DB_PASSWORD="${GCP_DB_PASSWORD}"
export PGPASSWORD="${GCP_DB_PASSWORD}"

echo "Creating key.json file..."
echo "${_GCP_CREDENTIAL_STRING}" > ./key.json

echo "Installing cloud_sql_proxy..."
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
chmod +x cloud_sql_proxy

echo "Starting cloud_sql_proxy connection..."
./cloud_sql_proxy -instances=${_GCP_CLOUD_SQL_CONNECTION_STRING}=tcp:${_GCP_DB_PORT} -credential_file=./key.json &
sleep 5

echo "Verifying we can connect to Cloud SQL..."
psql \
    --username="postgres" \
    --dbname="${DB_NAME}" \
    --host="${DB_HOST}"\
    --port="${DB_PORT}" \
    --command="SELECT now();";

echo "Running migrations..."
python manage.py migrate






