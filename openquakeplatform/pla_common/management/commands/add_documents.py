import json
from django.core.management.base import BaseCommand
from geonode.documents.models import Document
from geonode.base.models import TopicCategory, Region
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    args = '<documents_document_demo.json>'
    help = ('Import documents')

    def handle(doc_fname, *args, **options):

        # Read documents json
        doc_fname = ('/home/ubuntu/oq-platform2/'
                     'openquakeplatform/dump/documents_document_demo.json')
        doc_json = open(doc_fname).read()
        doc_load = json.loads(doc_json)

        # Read resourcebase json
        resource_name = ('/home/ubuntu/oq-platform2/'
                         'openquakeplatform/dump/base_resourcebase_demo.json')
        resource_json = open(resource_name).read()
        resource_load = json.loads(resource_json)

        # Read category json
        category_name = ('/home/ubuntu/oq-platform2/'
                         'openquakeplatform/dump/base_topiccategory.json')
        category_json = open(category_name).read()
        category_load = json.loads(category_json)

        # Read region json
        # region_fname = ('/home/ubuntu/oq-platform2/'
        #                 'openquakeplatform/dump/base_regions.json')
        # region_json = open(region_fname).read()
        # region_load = json.loads(region_json)

        # Delete all categories
        topiccategory = TopicCategory.objects.all()
        topiccategory.delete()

        # Upload all regions
        # for region in region_load:
        #     reg = region['fields']
        #     pk = region['pk']
        #     code = reg['code']
        #     name = reg['name']

        #     new_region = Region.objects.model(
        #                                       pk=pk,
        #                                       code=code,
        #                                       name=name
        #                                       )
        #     new_region.save()

        # Upload category
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
                category = resource_fields['category']
                edition = resource_fields['edition']
                # region = resource_fields['regions']
                regions = [region.encode("utf-8")
                           for region in resource_fields['regions']]

                print(owner)
                print(category)
                print(regions)

                # Istance user
                User = get_user_model()
                owners = User.objects.get(username=owner)
                print(owners)

                # Istance category
                cat = TopicCategory.objects.get(id=category)
                print(cat)

                # Istance regions
                # reg = Region.objects.get(id=region)
                # print(reg)

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
                                                category=cat,
                                                edition=edition,
                                                supplemental_information=sinfo
                                                )
                newdoc.save()

                # Add regions
                for reg in regions:
                    Reg = Region.objects.get(id=regions)
                    newdoc.regions.add(Reg)
