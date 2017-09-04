DATABASES = {
    'geddb': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ged',
        'USER': 'oqplatform2',
        'PASSWORD': 'password',
        'HOST': 'host',
        'PORT': 5432,
        'OPTIONS': {
            'sslmode': 'require',
        },
    },
}
