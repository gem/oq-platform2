import os
import json
from django.core.management.base import BaseCommand
from geonode.layers.models import Layer
from geonode.base.models import Region
# from django.contrib.auth import get_user_model


class Command(BaseCommand):
    args = '<documents_document_demo.json>'
    help = ('Import layers')

    def handle(doc_fname, *args, **options):

        # Read Style layer json
        layer_style_fname = (
            os.path.join(os.path.expanduser("~"), 'oq-private/'
                                                  'old_platform_documents/'
                                                  'json/'
                                                  'layers_style.json'))
        layer_style_json = open(layer_style_fname).read()
        layer_style_load = json.loads(layer_style_json)

        # Read layer attribute json
        # layer_attr_name = (
        #     os.path.join(os.path.expanduser("~"), 'oq-private/'
        #                                           'old_platform_documents/'
        #                                           'json/'
        #                                           'layers_attribute.json'))
        # layer_attr_json = open(layer_attr_name).read()
        # layer_attr_load = json.loads(layer_attr_json)

        # Read layer json
        layer_name = (
            os.path.join(os.path.expanduser("~"), 'oq-private/'
                                                  'old_platform_documents/'
                                                  'json/'
                                                  'layers_layer.json'))
        layer_json = open(layer_name).read()
        layer_load = json.loads(layer_json)

        # ResourceBase json with pk equal style of layers json
        new_style = {}
        for style in layer_style_load:
            new_style[style['pk']] = {
                'name': style['fields']['name'],
                'sld_url': style['fields']['sld_url'],
                'sld_version': style['fields']['sld_version'],
                'sld_title': style['fields']['sld_title'],
                'sld_body': style['fields']['sld_body'],
                'workspace': style['fields']['workspace'],
                                             }

        # Import documents
        for layer in layer_load:
            layers = layer['fields']
            layer_pk = layer['pk']
            layer_name = layers['name']
            typename = layers['typename']
            title_en = layers['name']
            workspace = layers['workspace']
            storetype = layers['storeType']
            store = layers['store']

            # Istance regions
            # styles = [style for style in layers['styles']]

            # try:
            # layer['style'] = new_style['styles']['style']

            # Istance regions
            regions = [region.encode("utf-8")
                       for region in layers['regions']]

            # Save layers
            # pk = styles
            newlayer = Layer.objects.model(
                id=layer_pk,
                title_en=layer_name,
                pk=layer_pk,
                typename=typename,
                name=title_en,
                store=store,
                workspace=workspace,
                storeType=storetype
                )
            newlayer.save()

            # Add regions
            for reg in regions:
                Reg = Region.objects.get(id=regions)
                newlayer.regions.add(Reg)

            # Print if create documents is successfully
            if newlayer.id == layer_pk:
                print('%s: %s created' % (layer_pk, title_en))
            else:
                raise ValueError

            # except:
            #     pass
