import os
import json
from django.core.management.base import BaseCommand
from geonode.documents.models import Document
from geonode.base.models import TopicCategory, Region, License
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    args = '<documents_document.json>'
    help = ('Import documents')

    def handle(doc_fname, *args, **options):

        # Read documents json
        doc_fname = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-private/old_platform_documents/json/'
                'documents_document.json'))
        doc_json = open(doc_fname).read()
        doc_load = json.loads(doc_json)

        # Read resourcebase json
        resource_name = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-private/old_platform_documents/json/'
                'base_resource_base.json'))
        resource_json = open(resource_name).read()
        resource_load = json.loads(resource_json)

        # Read category json
        category_name = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-private/old_platform_documents/json/'
                'base_topiccategory.json'))
        category_json = open(category_name).read()
        category_load = json.loads(category_json)

        # Read license json
        license_name = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-private/old_platform_documents/json/base_license.json'))
        license_json = open(license_name).read()
        license_load = json.loads(license_json)

        # Delete all categories
        topiccategory = TopicCategory.objects.all()
        topiccategory.delete()

        # Import all licenses
        for license in license_load:
            pk = license['pk']
            lic = license['fields']
            url = lic['url']
            license_text = lic['license_text']
            name = lic['name']
            description = lic['description']

            new_license = License.objects.model(
                pk=pk, url=url, license_text_en=license_text, name=name,
                description=description)
            new_license.save()

        # Import all categories
        for category in category_load:
            cat = category['fields']
            pk = category['pk']
            is_choice = cat['is_choice']
            gn_descript = cat['gn_description']
            identifier = cat['identifier']
            description = cat['description']

            new_cat = TopicCategory.objects.model(
                pk=pk, is_choice=is_choice, gn_description=gn_descript,
                identifier=identifier, description=description)
            new_cat.save()

        # ResourceBase json with pk equal object_id of documents json
        new_resources = {}
        for resource in resource_load:
            new_resources[resource['pk']] = resource['fields']

        # Import documents
        for doc_full in doc_load:
            doc = doc_full['fields']

            res = new_resources[doc_full['pk']]

            # Istance regions
            regions = [region for region in res['regions']]

            # Istance user
            User = get_user_model()
            owner = User.objects.get(username=res['owner'][0])

            # Istance category
            cat = TopicCategory.objects.get(id=res['category'])

            # Istance license
            license_id = res['license']
            if license_id is not None:
                license = License.objects.get(id=license_id)
            else:
                license = None

            # Save documents
            newdoc = Document.objects.model(
                title_en=res['title'],
                owner=owner,
                extension=doc['extension'],
                abstract=res['abstract'],
                doc_file=doc['doc_file'],
                object_id=doc['object_id'],
                category=cat,
                license=license,
                edition=res['edition'],
                supplemental_information=res['supplemental_information']
                )
            newdoc.save()

            print(res['title'])

            # Add regions
            for reg in regions:
                Reg = Region.objects.get(id=reg)
                newdoc.regions.add(Reg)
