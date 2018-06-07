import json
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = '<documents_document.json>'
    help = ('Import documents')

    def handle(self, doc_fname, *args, **options):
        doc_json = open(doc_fname).read()
        doc_load = json.loads(doc_json)

        for doc in doc_load:
            print('%s' % doc['pk'])
            print('%s' % doc['model'])
            print('%s' % doc['fields']['doc_file'])
            print('%s' % doc['fields']['extension'])
