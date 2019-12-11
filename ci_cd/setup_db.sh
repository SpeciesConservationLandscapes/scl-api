#! /bin/bash

_GCP_SERVICE_ACCOUNT_KEY_FILE=${GCP_SERVICE_ACCOUNT_KEY_FILE}
_GCP_DB_PASSWORD=${GCP_DB_PASSWORD}

_GCP_PROJECT_ID=${GCP_PROJECT_ID}
_GCP_SQL_INSTANCE_NAME=${GCP_SQL_INSTANCE_NAME}
_GCP_REGION=${GCP_REGION}

_GCP_SERVICE_ACCOUNT_EMAIL=${GCP_SERVICE_ACCOUNT_EMAIL}
_GCP_DB_NAME=${GCP_DB_NAME}
_MACHINE_TYPE="$(uname -s)"


clear
echo "Setting up database..."

echo
echo "Checking credentials..."
if [[ -z "${_GCP_DB_PASSWORD}" ]]
then
      echo "GCP_DB_PASSWORD is undefined."
      echo "Set it by executing: export GCP_DB_PASSWORD=your_secure_password"
      echo "Cancelling database setup..."
      exit 1
else
      echo "GCP_DB_PASSWORD is set."
fi
if [[ -z "${_GCP_SERVICE_ACCOUNT_KEY_FILE}" ]]
then
      echo "SERVICE_ACCOUNT_KEY_FILE is undefined."
      echo "Set it by executing: export SERVICE_ACCOUNT_KEY_FILE=path_to_key_file.json"
      echo "Cancelling database setup..."
      exit 1
else
      echo "SERVICE_ACCOUNT_KEY_FILE is set."
fi

echo
echo "Authenticating gcloud using service account..."
gcloud auth activate-service-account \
        ${_GCP_SERVICE_ACCOUNT_EMAIL} \
        --key-file=${_GCP_SERVICE_ACCOUNT_KEY_FILE} \
        --project=${_GCP_PROJECT_ID}

echo
echo "Creating Postgres SQL instance..."
gcloud sql instances create \
        ${_GCP_SQL_INSTANCE_NAME} \
        --database-version=POSTGRES_11 \
        --cpu=1 \
        --memory=3840MiB \
        --region=${_GCP_REGION}

echo
echo "Setting password of default 'postgres' user..."
gcloud sql users set-password \
        postgres \
        --instance=${_GCP_SQL_INSTANCE_NAME} \
        --password=${_GCP_DB_PASSWORD}

echo
echo "Creating database..."
gcloud sql databases create \
        ${_GCP_DB_NAME} \
        --instance=${_GCP_SQL_INSTANCE_NAME}

echo
echo "Installing cloud_sql_proxy..."
case "${_MACHINE_TYPE}" in
    Linux*)    wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy;;
    Darwin*)   curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.amd64;;
    *)         echo 'Unsupported OS.' && echo 'Cancelling database setup...' && exit 1;;
esac
chmod +x cloud_sql_proxy

echo
echo "Starting cloud_sql_proxy connection..."
export PGPASSWORD=${_GCP_DB_PASSWORD}
_GCP_INSTANCE_CONNECT_STRING=$(gcloud sql instances describe ${_GCP_SQL_INSTANCE_NAME} | grep connectionName)
_GCP_INSTANCE_CONNECT_STRING="${_GCP_INSTANCE_CONNECT_STRING:15}"
./cloud_sql_proxy -instances=${_GCP_INSTANCE_CONNECT_STRING}=tcp:5433 &
sleep 5

echo
echo "Installing extensions postgis..."
psql \
    --username="postgres" \
    --dbname="${_GCP_DB_NAME}" \
    --host 127.0.0.1 \
    --port 5433 \
    --command="CREATE EXTENSION postgis;"

echo
echo "Installing extension postgis_tiger_geocoder..."
psql \
    --username="postgres" \
    --dbname="${_GCP_DB_NAME}" \
    --host 127.0.0.1 \
    --port 5433 \
    --command="CREATE EXTENSION postgis_tiger_geocoder CASCADE;"

echo
echo "Installing extension postgis_topology..."
psql \
    --username="postgres" \
    --dbname="${_GCP_DB_NAME}" \
    --host 127.0.0.1 \
    --port 5433 \
    --command="CREATE EXTENSION postgis_topology;"
