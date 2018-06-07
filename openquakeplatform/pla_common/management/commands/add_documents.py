import json
# import re
# import os
from django.core.management.base import BaseCommand
from geonode.base.models import Link
from django.core.files.storage import default_storage as storage


class Command(BaseCommand):
    args = '<documents_document.json>'
    help = ('Import documents')

    def handle(self, doc_fname, *args, **options):
        doc_json = open(doc_fname).read()
        doc_load = json.loads(doc_json)

        for doc in doc_load:
            print(doc['pk'])
