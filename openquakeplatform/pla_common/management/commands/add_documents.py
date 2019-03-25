import os
import json
from django.core.management.base import BaseCommand
from geonode.documents.models import Document
from geonode.layers.models import Layer, Style, Attribute
from geonode.maps.models import Map, MapLayer
from geonode.base.models import TopicCategory, Region, License
from geonode.base.models import SpatialRepresentationType
from geonode.base.models import HierarchicalKeyword
from geonode.base.models import ResourceBase, TaggedContentItem
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from agon_ratings.models import OverallRating
from decimal import Decimal


def base_attrs(base):
    base_new = {}
    base_new.update(base)
    base_new['thumbnail_url'] = base['thumbnail']
    base_new['title_en'] = base['title']
    del base_new['thumbnail']
    del base_new['distribution_description']
    del base_new['distribution_url']
    del base_new['regions']
    return base_new


class Command(BaseCommand):
    args = '<documents_document.json>'
    help = ('Import data')

    def handle(doc_fname, *args, **options):

        # Read documents json
        doc_fname = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-platform2/openquakeplatform/common/gs_data/dump/'
                'documents_document.json'))
        doc_json = open(doc_fname).read()
        doc_load = json.loads(doc_json)

        # Read Style layer json
        layer_style_fname = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-platform2/openquakeplatform/common/gs_data/dump/'
                'layers_style.json'))
        layer_style_json = open(layer_style_fname).read()
        layer_style_load = json.loads(layer_style_json)

        # Read layer attribute json
        layer_attr_name = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-platform2/openquakeplatform/common/gs_data/dump/'
                'layers_attribute.json'))
        layer_attr_json = open(layer_attr_name).read()
        layer_attr_load = json.loads(layer_attr_json)

        # Read layer rating json
        layer_rating_name = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-platform2/openquakeplatform/common/gs_data/dump/'
                'rating_overall_rating.json'))
        layer_rating_json = open(layer_rating_name).read()
        layer_rating_load = json.loads(layer_rating_json)

        # Read layer json
        layer_name = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-platform2/openquakeplatform/common/gs_data/dump/'
                'layers_layer.json'))
        layer_json = open(layer_name).read()
        layer_load = json.loads(layer_json)

        # Read resourcebase json
        resource_name = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-platform2/openquakeplatform/common/gs_data/dump/'
                'base_resource_base.json'))
        resource_json = open(resource_name).read()
        resource_load = json.loads(resource_json)

        # Read map json
        maps_name = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-platform2/openquakeplatform/common/gs_data/dump/'
                'maps_map.json'))
        maps_json = open(maps_name).read()
        maps_load = json.loads(maps_json)

        # Read maplayer json
        maplayer_name = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-platform2/openquakeplatform/common/gs_data/dump/'
                'maps_maplayer.json'))
        maplayer_json = open(maplayer_name).read()
        maplayer_load = json.loads(maplayer_json)

        # ResourceBase json with pk equal pk of documents json
        new_resources = {}
        for resource in resource_load:
            new_resources[resource['pk']] = resource['fields']

        # Read category json
        category_name = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-platform2/openquakeplatform/common/gs_data/dump/'
                'base_topiccategory.json'))
        category_json = open(category_name).read()
        category_load = json.loads(category_json)

        # Read regions json
        region_name = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-platform2/openquakeplatform/common/gs_data/dump/'
                'base_region.json'))
        region_json = open(region_name).read()
        region_load = json.loads(region_json)

        # Read license json
        license_name = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-platform2/openquakeplatform/common/gs_data/dump/'
                'base_license.json'))
        license_json = open(license_name).read()
        license_load = json.loads(license_json)

        # Read SpatialRepresentationType json
        srt_name = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-platform2/openquakeplatform/common/gs_data/dump/'
                'base_spatialrepresentationtype.json'))
        srt_json = open(srt_name).read()
        srt_load = json.loads(srt_json)

        # Read tag json
        tag_name = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-platform2/openquakeplatform/common/gs_data/dump/'
                'taggit_tag.json'))
        tag_json = open(tag_name).read()
        tag_load = json.loads(tag_json)
        # print("tag load: %d" % len(tag_load))

        tag_name = (
            os.path.join(
                os.path.expanduser("~"),
                'oq-platform2/openquakeplatform/common/gs_data/dump/'
                'taggit_taggeditem.json'))
        tag_json = open(tag_name).read()
        tag_item_load = json.loads(tag_json)

        # Delete all licenses
        License.objects.all().delete()
        old_license_refs = {}
        # Import all licenses
        for license in license_load:
            pk = license['pk']
            lic = license['fields']
            url = lic['url']
            license_text = lic['license_text']
            name = lic['name']
            description = lic['description']

            new_license = License.objects.model(
                url=url, license_text_en=license_text, name=name,
                description=description)
            new_license.save()
            old_license_refs[pk] = new_license
        HierarchicalKeyword.objects.all().delete()

        # Delete all categories
        TopicCategory.objects.all().delete()

        old_category_refs = {}
        # Import all categories
        for category in category_load:
            field = category['fields']
            pk = category['pk']
            is_choice = field['is_choice']
            gn_descript = field['gn_description']
            identifier = field['identifier']
            description = field['description']

            new_cat = TopicCategory.objects.model(
                is_choice=is_choice, gn_description=gn_descript,
                identifier=identifier, description=description)
            new_cat.save()
            old_category_refs[pk] = new_cat

        Style.objects.all().delete()
        old_style_refs = {}
        # Import all styles
        for style in layer_style_load:
            pk = style['pk']
            field = style['fields']
            name = field['name']
            sld_url = field['sld_url']
            sld_version = field['sld_version']
            sld_title = field['sld_title']
            sld_body = field['sld_body']
            workspace = field['workspace']

            new_style = Style.objects.model(
                name=name, sld_url=sld_url, sld_version=sld_version,
                sld_title=sld_title, sld_body=sld_body, workspace=workspace)
            new_style.save()
            old_style_refs[pk] = new_style

        # Import maps
        map_old_refs = {}
        for map_full in maps_load:

            maps = map_full['fields']
            mapp = new_resources[map_full['pk']]

            # Istance user
            User = get_user_model()
            owner = User.objects.get(username=mapp['owner'][0])

            # Save maps
            newmap = Map.objects.model(
                uuid=mapp['uuid'],
                projection=maps['projection'],
                title_en=mapp['title'],
                zoom=maps['zoom'],
                last_modified=maps['last_modified'],
                center_x=maps['center_x'],
                center_y=maps['center_y'],
                owner=owner,
                abstract=mapp['abstract'],
                purpose=mapp['purpose'],
                date=mapp['csw_insert_date'],
                category=(old_category_refs[mapp['category']]
                          if mapp['category'] is not None
                          else None),
                license=(old_license_refs[mapp['license']]
                         if mapp['license'] is not None
                         else None),
                edition=mapp['edition'],
                supplemental_information_en=mapp['supplemental_information'],
                popular_count=maps['popular_count'],
                share_count=maps['share_count']
                )
            newmap.save()
            map_old_refs[map_full['pk']] = newmap

            # Istance and add regions
            regions = [region for region in mapp['regions']]

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
                newmap.regions.add(Reg)

            print(
                'Imported map: %s with pk %s' % (
                    mapp['title'], map_full['pk']))

        # Import maplayers
        for maplayer_full in maplayer_load:

            mapslayer = maplayer_full['fields']
            map_id = map_old_refs[mapslayer['map']].pk

            # Istance Map
            if map_id is not None:
                map_id = Map.objects.get(id=map_id)
            else:
                map_id = None

            # Save mapslayer
            newmaplayer = MapLayer.objects.model(
                opacity=mapslayer['opacity'],
                map=map_id,
                group=mapslayer['group'],
                name=mapslayer['name'],
                format=mapslayer['format'],
                visibility=mapslayer['visibility'],
                source_params=mapslayer['source_params'],
                layer_params=mapslayer['layer_params'],
                ows_url=mapslayer['ows_url'],
                stack_order=mapslayer['stack_order'],
                styles=mapslayer['styles'],
                fixed=mapslayer['fixed'],
                local=mapslayer['local'],
                transparent=mapslayer['transparent']
                )
            newmaplayer.save()

        # Import documents
        for doc_full in doc_load:

            doc = doc_full['fields']
            res = new_resources[doc_full['pk']]

            # Istance content_type
            ctype_name = doc['content_type']
            if ctype_name is not None:
                ctype = [ctype for ctype in doc['content_type']]
                label_type = ctype[0]
                cont_type = ctype[1]
                content_type = ContentType.objects.get(
                    app_label=label_type, model=cont_type)

            # Istance user
            User = get_user_model()
            owner = User.objects.get(username=res['owner'][0])

            object_id = None
            # associate optional map with document
            if doc['object_id'] is not None:
                object_id = map_old_refs[doc['object_id']].pk

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
                category=old_category_refs[res['category']],
                license=(old_license_refs[res['license']]
                         if res['license'] is not None
                         else None),
                content_type=content_type,
                edition=res['edition'],
                supplemental_information_en=res['supplemental_information'],
                popular_count=doc['popular_count'],
                share_count=doc['share_count']
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

        # Delete all layer
        Layer.objects.all().exclude(
            title_en='isc_viewer_measure').exclude(
            title_en='ghec_viewer_measure').delete()

        # Import SpatialRepresentationType
        srt_old_refs = {}
        for srt_full in srt_load:

            field = srt_full['fields']

            new_srt = SpatialRepresentationType.objects.model(**field)
            new_srt.save()
            srt_old_refs[srt_full['pk']] = new_srt

        # Import layers
        layer_old_refs = {}
        for layer_full in layer_load:

            layer = layer_full['fields']
            base = new_resources[layer_full['pk']]

            # Instance default SpatialRepresentationType
            srt = (srt_old_refs[srt_full['pk']]
                   if base['spatial_representation_type'] is not None
                   else None)

            # Istance user
            User = get_user_model()
            owner = User.objects.get(username=base['owner'][0])

            # Instance default style
            default_style = (old_style_refs[layer['default_style']]
                             if layer['default_style'] is not None
                             else None)

            attrs = base_attrs(base)
            attrs.update({
                "owner": owner,
                "name": layer['name'],
                "category": (old_category_refs[base['category']]
                             if base['category'] is not None
                             else None),
                "license": (old_license_refs[base['license']]
                            if base['license'] is not None
                            else None),
                "typename": layer['typename'],
                "store": layer['store'],
                "workspace": layer['workspace'],
                "default_style": default_style,
                "storeType": layer['storeType'],
                "bbox_x0": base['bbox_x0'],
                "bbox_x1": base['bbox_x1'],
                "bbox_y0": base['bbox_y0'],
                "bbox_y1": base['bbox_y1'],
                "spatial_representation_type": srt,
                "supplemental_information_en": base['supplemental_information']
            })

            # Save layer
            new_layer = Layer.objects.model(**attrs)
            new_layer.save()
            layer_old_refs[layer_full['pk']] = new_layer

            # Istance and add regions
            regions = [region for region in base['regions']]

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
                new_layer.regions.add(Reg)

            # Instance and add styles
            for sty in layer['styles']:
                new_layer.styles.add(old_style_refs[sty])

            print(
                'Imported layer: %s with pk: %s' % (
                    layer['name'], layer_full['pk']))

        # Import layer attribute
        for attr in layer_attr_load:

            field = attr['fields']
            layer_id = layer_old_refs[field['layer']]

            new_attr = Attribute.objects.model(
                count=field['count'],
                layer=layer_id,
                description=field['description'],
                min=field['min'],
                attribute_label=field['attribute_label'],
                attribute=field['attribute'],
                display_order=field['display_order'],
                unique_values=field['unique_values'],
                median=field['median'],
                sum=field['sum'],
                visible=field['visible'],
                last_stats_updated=field['last_stats_updated'],
                stddev=field['stddev'],
                attribute_type=field['attribute_type'],
                average=field['average'],
                max=field['max']
                )
            new_attr.save()

        # Import layer rating
        for rating in layer_rating_load:

            field = rating['fields']

            # Istance content_type
            ctype_name = field['content_type']
            if ctype_name is not None:
                r_type = [r_type for r_type in field['content_type']]
                label_type = r_type[0]
                cont_type = r_type[1]
                content_type = ContentType.objects.get(
                    app_label=label_type, model=cont_type)

            object_id = None
            if field['object_id'] is not None:
                object_id = layer_old_refs[field['object_id']].pk

            OverallRating.objects.all().delete()
            new_rating = OverallRating.objects.model(
                category=field['category'],
                rating=Decimal(value=field['rating']),
                object_id=object_id,
                content_type=content_type
                )
            new_rating.save()

        # Import all tags
        new_tags = {}

        for tag in tag_load:
            field = tag['fields']
            new_tags[tag['pk']] = tag['fields']
            name = field['name']
            HierarchicalKeyword.add_root(name=name)

        # Import all tagged items
        for tag_item in tag_item_load:
            field = tag_item['fields']

            tagitem_type_name = field['content_type']
            if tagitem_type_name is not None:
                tag_item_type = [tagitem_type
                                 for tagitem_type in field['content_type']]
                label_type = tag_item_type[0]
                cont_type = tag_item_type[1]
                content_type = ContentType.objects.get(
                    app_label=label_type, model=cont_type)

            try:
                content_object = ResourceBase.objects.get(
                    uuid=new_resources[field['object_id']]['uuid'])
            except:
                continue

            new_tag_item = TaggedContentItem.objects.model(
                tag=HierarchicalKeyword.objects.get(
                    name=new_tags[field['tag']]['name']),
                content_object=content_object)
            new_tag_item.save()
