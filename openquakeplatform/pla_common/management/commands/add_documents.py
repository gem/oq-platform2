import json
from django.core.management.base import BaseCommand
from geonode.documents.models import Document


class Command(BaseCommand):
    args = '<documents_document_demo.json>'
    help = ('Import documents')

    # def handle(self, doc_fname, *args, **options):
    def handle(doc_fname, *args, **options):
        doc_fname = ('/home/ubuntu/oq-platform2/'
                     'openquakeplatform/dump/documents_document_demo.json')
        doc_json = open(doc_fname).read()
        doc_load = json.loads(doc_json)

        # Print documents fields
        for doc in doc_load:
            docs = doc['fields']
            doc_id = doc['pk']
            extension = docs['extension']
            object_id = docs['object_id']
            doc_file = docs['doc_file']
            title_en = doc_file.replace('documents/', '')
            print(title_en)

            # Add documents
            newdoc = Document.objects.model(
                                            id=doc_id,
                                            title_en=title_en,
                                            extension=extension,
                                            object_id=object_id,
                                            doc_file=doc_file
                                            )
            newdoc.save()
