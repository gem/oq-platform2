import json
from django.core.management.base import BaseCommand
from geonode.documents.models import Document
from geonode.base.models import TopicCategory
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    args = '<documents_document_demo.json>'
    help = ('Import documents')

    # def handle(self, doc_fname, *args, **options):
    def handle(doc_fname, *args, **options):

        # Delete all categories
        topiccategory = TopicCategory.objects.all()
        topiccategory.delete()

        doc_fname = ('/home/ubuntu/oq-platform2/'
                     'openquakeplatform/dump/documents_document_demo.json')
        doc_json = open(doc_fname).read()
        doc_load = json.loads(doc_json)

        resource_name = ('/home/ubuntu/oq-platform2/'
                         'openquakeplatform/dump/base_resourcebase_demo.json')
        resource_json = open(resource_name).read()
        resource_load = json.loads(resource_json)

        # Print documents fields
        for doc in doc_load:
            docs = doc['fields']
            doc_pk = doc['pk']
            extension = docs['extension']
            object_id = docs['object_id']
            doc_file = docs['doc_file']

            for resource in resource_load:

                resource_fields = resource['fields']
                owner = resource_fields['owner'][0]
                title = resource_fields['title']
                abstract = resource_fields['abstract']
                sinfo = resource_fields['supplemental_information']
                regions = resource_fields['regions']
                edition = resource_fields['edition']
                print(owner)
                print(regions)

                User = get_user_model()
                owners = User.objects.get(username=owner)
                print(owners)

                pk = object_id
                newdoc = Document.objects.model(
                                                id=doc_pk,
                                                title_en=title,
                                                pk=pk,
                                                owner=owners,
                                                extension=extension,
                                                abstract=abstract,
                                                doc_file=doc_file,
                                                object_id=object_id,
                                                # regions=regions,
                                                edition=edition,
                                                supplemental_information=sinfo
                                                )

                newdoc.save()
