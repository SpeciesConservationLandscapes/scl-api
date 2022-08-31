## CORS


```
gsutil cors set cors_config.json gs://cache.speciescl.org


// config.json
[
    {
        "origin": [
            "http://localhost:8181",
            "https://speciescl.org",
            "https://*.speciescl.org"
        ],
        "method": ["GET"],
        "responseHeader": ["Content-Type"],
        "maxAgeSeconds": 3600
    }
]
```****