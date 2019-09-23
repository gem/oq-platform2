# Copyright (c) 2019, GEM Foundation.
#
# This program is free software: you can redistribute it and/or modify
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

    # results
    return HttpResponse(
        json.dumps(data, indent=4), content_type="application/json")
