import urllib2
import json
from django.http import HttpResponse
import psycopg2
from django.conf import settings


def monitoring(request):

    data = []

    title = ['Engine server', 'Geoserver']
    url = [
        'http://localhost:8800/v1/engine_version',
        'http://localhost:8080/geoserver'
        ]
    # check Geoserver and Engine server
    for a_title, a_url in zip(title, url):
        item = {}
        try:
            urllib2.urlopen(a_url, timeout=1)
            item['Title'] = a_title
            item['Url'] = a_url
            item['Status'] = 'OK'
        except urllib2.URLError:
            item['Title'] = a_title
            item['Url'] = a_url
            item['Status'] = 'Fail'
        data.append(item)

    # check postgres
    pg = {}
    PG_HOST = settings.DATABASES['default']['HOST']
    PG_NAME = settings.DATABASES['default']['NAME']
    PG_USER = settings.DATABASES['default']['USER']
    PG_PWD = settings.DATABASES['default']['PASSWORD']

    pg['Title'] = 'Postgres'
    try:
        psycopg2.connect(
            "host = '%s' "
            "dbname = '%s' "
            "user = '%s' "
            "password = '%s'" % (PG_HOST, PG_NAME, PG_USER, PG_PWD))

        pg['Status'] = 'OK'
    except psycopg2.OperationalError:
        pg['Status'] = 'Fail'
    data.append(pg)

    return HttpResponse(
        json.dumps(data, indent=4), content_type="application/json")
