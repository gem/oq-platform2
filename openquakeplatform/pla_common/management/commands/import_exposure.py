import os
import json
from django.core.management.base import BaseCommand
from geonode.documents.models import Document
from geonode.base.models import TopicCategory, Region, License
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    args = '<documents_document.json>'
    help = ('Import exposure data')

    def handle(doc_fname, *args, **options):

        # Read resourcebase json
        resource_name = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-platform2/openquakeplatform/common/gs_data/dump/'
                'exposure_demo/base_resourcebase.json'))
        resource_json = open(resource_name).read()
        resource_load = json.loads(resource_json)

        # ResourceBase json with pk equal pk of documents json
        new_resources = {}
        for resource in resource_load:
            new_resources[resource['pk']] = resource['fields']
        doc_fname = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-platform2/openquakeplatform/common/gs_data/dump/'
                'exposure_demo/documents_document.json'))
        doc_json = open(doc_fname).read()
        doc_load = json.loads(doc_json)

        # Read regions json
        region_name = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-platform2/openquakeplatform/common/gs_data/dump/'
                'base_region.json'))
        region_json = open(region_name).read()
        region_load = json.loads(region_json)

        # ResourceBase json with pk equal pk of documents json
        new_resources = {}
        for resource in resource_load:
            new_resources[resource['pk']] = resource['fields']

        # Import documents
        for doc_full in doc_load:

            doc = doc_full['fields']
            res = new_resources[doc_full['pk']]

            # Istance user
            User = get_user_model()
            owner = User.objects.get(username=res['owner'][0])

            object_id = None

            license = License.objects.get(id=res['license'])

            category = TopicCategory.objects.get(id=res['category'])


            # Save documents
            newdoc = Document.objects.model(
                uuid=res['uuid'],
                title_en=res['title'],
                owner=owner,
                extension=doc['extension'],
                abstract=res['abstract'],
                purpose=res['purpose'],
                doc_file=doc['doc_file'],
                object_id=object_id,
                category=category,
                license=license,
                content_type=content_type,
                edition=res['edition'],
                supplemental_information_en=res['supplemental_information'],
                )
            newdoc.save()

            # Istance and add regions
            regions = [region for region in res['regions']]

            for reg in regions:
                # Search in old region json
                for region in region_load:
                    field = region['fields']
                    if region['pk'] == reg:
                        name = field['name']
                    else:
                        continue
                # Add region to each document
                Reg = Region.objects.get(name=name)
                newdoc.regions.add(Reg)

            print('Imported document: %s' % res['title'])
