import os
import json
from django.core.management.base import BaseCommand
from geonode.documents.models import Document
from geonode.base.models import TopicCategory, Region, License
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    args = '<documents_document_demo.json>'
    help = ('Import documents')

    def handle(doc_fname, *args, **options):

        # Read documents json
        # doc_fname = (os.path.join(os.path.expanduser("~"), 'oq-platform2/'
        #             'openquakeplatform/dump/documents_document_demo.json'))
        doc_fname = (
            os.path.join(os.path.expanduser("~"), 'oq-private/'
                                                  'old_platform_documents/'
                                                  'json/'
                                                  'documents_document.json'))
        doc_json = open(doc_fname).read()
        doc_load = json.loads(doc_json)

        # Read resourcebase json
        # resource_name = (
        #     os.path.join(os.path.expanduser("~"), 'oq-platform2/'
        #                                           'openquakeplatform/dump/'
        #                                           'base_resourcebase_demo.json'))
        resource_name = (
            os.path.join(os.path.expanduser("~"), 'oq-private/'
                                                  'old_platform_documents/'
                                                  'json/'
                                                  'base_resource_base.json'))
        resource_json = open(resource_name).read()
        resource_load = json.loads(resource_json)

        # Read category json
        category_name = (
            os.path.join(os.path.expanduser("~"), 'oq-private/'
                                                  'old_platform_documents/'
                                                  'json/'
                                                  'base_topiccategory.json'))
        category_json = open(category_name).read()
        category_load = json.loads(category_json)

        # Read license json
        license_name = (
            os.path.join(os.path.expanduser("~"), 'oq-private/'
                                                  'old_platform_documents/'
                                                  'json/base_license.json'))
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
                                                pk=pk,
                                                url=url,
                                                license_text_en=license_text,
                                                name=name,
                                                description=description
                                                )
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
                                                  pk=pk,
                                                  is_choice=is_choice,
                                                  gn_description=gn_descript,
                                                  identifier=identifier,
                                                  description=description
                                                  )
            new_cat.save()

        # ResourceBase json with pk equal object_id of documents json
        new_resources = {}
        for resource in resource_load:
            new_resources[resource['pk']] = {
                'owner': resource['fields']['owner'][0],
                'title': resource['fields']['title'],
                'abstract': resource['fields']['abstract'],
                'sinfo': resource['fields']['supplemental_information'],
                'category': resource['fields']['category'],
                'edition': resource['fields']['edition'],
                'licenses': resource['fields']['license'],
                'regions': resource['fields']['regions'],
                                             }

        # Import documents
        for doc in doc_load:
            docs = doc['fields']
            doc_pk = doc['pk']
            extension = docs['extension']
            object_id = docs['object_id']
            doc_file = docs['doc_file']

            try:
                doc['resource'] = new_resources[doc_pk]

                licenses = doc['resource']['licenses']

                # Istance regions
                regions = [region.encode("utf-8")
                           for region in doc['resource']['regions']]

                # Istance user
                User = get_user_model()
                owners = User.objects.get(username=doc['resource']['owner'])

                # Istance category
                cat = TopicCategory.objects.get(id=doc['resource']['category'])

                # Istance license
                license = License.objects.get(id=licenses)

                # Save documents
                pk = doc_pk
                newdoc = Document.objects.model(
                    # id=doc_pk,
                    title_en=doc['resource']['title'],
                    pk=pk,
                    owner=owners,
                    extension=extension,
                    abstract=doc['resource']['abstract'],
                    doc_file=doc_file,
                    object_id=object_id,
                    category=cat,
                    license=license,
                    edition=doc['resource']['edition'],
                    supplemental_information=doc['resource']['sinfo']
                    )
                newdoc.save()

                # Add regions
                for reg in regions:
                    Reg = Region.objects.get(id=regions)
                    newdoc.regions.add(Reg)

                # Print if create documents is successfully
                if newdoc.id == doc_pk:
                    title = doc['resource']['title'])
                    print('%s: %s created' % (doc_pk, title))
                else:
                    raise ValueError

            except:
                pass
