

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


## Loading Datasets


GADM Countries and States
Cloud Storage Bucket: scl-backup/gadm_states_countries_simp2

https://drive.google.com/file/d/1vHsyu-GdSasb7Nktt7ij13Lv-eh57Kvk/view?usp=sharing

**Countries:**

```
ogr2ogr -f "PostGreSQL" PG:"host=scl_db user=postgres dbname=scl password=postgres" \
    "GDAM404_country_simp2.shp" \
    -append -update \
    -preserve_fid \
    -nln public.countries \
    -nlt MULTIPOLYGON \
    -dialect sqlite \
    -sql "SELECT Geometry as geom, countrynam as name, iso2 as iso2, iso3 as iso3, isonumeric from GDAM404_country_simp2"
```

**States:**

```
ogr2ogr -f "PostGreSQL" PG:"host=scl_db user=postgres dbname=scl password=postgres" \
    "GDAM404_state_simp2.shp" \
    -append -update \
    -preserve_fid \
    -nln public.states \
    -nlt MULTIPOLYGON \
    -dialect sqlite \
    -sql 'SELECT Geometry as geom, countrynam as name, iso2 as iso2, iso3 as iso3, isonumeric, gadm1code as gadm1_code, gadm1name as gadm1_name, "ENGTYPE_1" AS gadm1_type from GDAM404_state_simp2'
```


**Indigenous Range for TCL:**

Cloud Storage Bucket: `scl-backup/indigenous_range_for_tcl_3`
