

## Settings Template

```
SECRET_KEY=
DB_NAME=
DB_USER=
DB_PASSWORD=
PGPASSWORD=
DB_HOST=
DB_PORT=
ENV=
API_AUDIENCE=
API_SIGNING_SECRET=
ADMIN_API_CLIENT_ID=
ADMIN_API_CLIENT_SECRET=
ADMIN_API_AUDIENCE=
AUTH0_DOMAIN=
GCP_SERVICE_ACCOUNT_KEY=
```

## GCP Settings Template

```
GCP_CLOUD_SQL_CONNECTION_STRING=	
GCP_CREDENTIAL_STRING=	
GCP_DB_NAME=	
GCP_DB_PASSWORD=	
GCP_DB_PORT=	
GCP_DB_USER=	
GCP_DJANGO_STATIC_URL=
GCP_PROJECT_ID=	
GCP_REGION=	
GCP_SERVICE_ACCOUNT_EMAIL=	
GCP_SERVICE_ACCOUNT_KEY_FILE=	
GCP_SQL_INSTANCE_NAME=

```


## Create Storage location for Django static files
```
# Bucket name: scl-django-static
gsutil mb gs://scl-django-static
gsutil defacl set public-read gs://scl-django-static
gsutil rsync -R static/ gs://scl-django-static/static
# Assets available at https://storage.googleapis.com/scl-django-static/static/
```
