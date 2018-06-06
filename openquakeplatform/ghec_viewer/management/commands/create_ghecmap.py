# Copyright (c) 2012-2018, GEM Foundation.
#
# This program is free software: you can redistribute it and/or modify
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import re
import os
from django.core.management.base import BaseCommand
from geonode.maps.models import Map, MapLayer, MapSnapshot
from geonode.people.models import Profile
from geonode.base.models import Link
from django.core.files.storage import default_storage as storage
from geonode.settings import GEOSERVER_LOCATION
from geonode.settings import SITEURL

from pprint import pprint


class Command(BaseCommand):
    args = '<ghec_map_comps.json>'
    help = ('Import csv of GEM Global Historical Catalogue '
            '(catalogue and appendix)')

    def handle(self, ghec_map_comps_fname, *args, **options):
        map_json = open(ghec_map_comps_fname).read()
        map_json = map_json.replace('#GEOSERVER_LOCATION#',
                                    GEOSERVER_LOCATION)
        map_json = map_json.replace('#SITEURL#', SITEURL)
        map_comps = json.loads(map_json)
        map = None
        res_base = None

        maplayers = []
        links = []
        mapsnapshot = None

        for comp in map_comps:
            if comp['model'] == 'maps.map':
                if map is not None:
                    raise ValueError
                map = comp
            elif comp['model'] == 'base.resourcebase':
                if res_base is not None:
                    raise ValueError
                res_base = comp
            elif comp['model'] == 'base.link':
                links.append(comp)
            elif comp['model'] == 'maps.maplayer':
                maplayers.append(comp)
            elif comp['model'] == 'maps.mapsnapshot':
                mapsnapshot = comp
                pprint(comp['fields']['config'])
            else:
                print(comp['model'])

        map['fields'].update(res_base['fields'])

        print("Map uuid: %s" % map['fields']['uuid'])

        try:
            m_old = Map.objects.get(uuid=map['fields']['uuid'])
            m_old.delete()
            print("Old map found: deleted")
        except:
            print("No previous map found")

        fields = map['fields']
        kw = {}
        for field in fields:
            # print("%s: %s (%s)" % (field, fields[field],
            # type(fields[field])))

            if (field == 'polymorphic_ctype' or field == 'regions' or
                    field == 'tkeywords'):
                continue
            elif field == 'owner':
                kw[field] = Profile.objects.get(username=fields[field][0])
            else:
                kw[field] = fields[field]

        print("OWNER:  [%s]" % fields['owner'][0])
        owner = Profile.objects.get(username=fields['owner'][0])
        print("OWNER2: [%s]" % type(owner))
        kw['owner'] = owner

        print("THUMB: [%s]" % kw['thumbnail_url'])
        map_new = Map(**kw)

        map_new.save()

        thumb_filename = re.sub('.*/', '', kw['thumbnail_url'])
        thumb_filepath = os.path.join(
            os.path.dirname(__file__), '..', '..', 'dev_data',
            'ghec_map_comps_files', thumb_filename)
        map_new.save_thumbnail(thumb_filename, open(thumb_filepath).read())

        for maplayer in maplayers:
            fields = maplayer['fields']
            kw = {}
            for field in fields:
                # print('ML: %s' % field)
                if field == 'owner':
                    kw[field] = Profile.objects.get(
                        username=fields[field][0])
                if field == 'map':
                    kw[field] = map_new
                else:
                    kw[field] = fields[field]
#            kw['map'] = map_new
            maplayer_new = MapLayer(**kw)
            maplayer_new.save()

        links_old = Link.objects.filter(resource=map_new)
        links_old.delete()

        for link in links:
            fields = link['fields']
            kw = {}
            for field in fields:
                if field == 'resource':
                    kw[field] = map_new
                else:
                    kw[field] = fields[field]

            if kw['name'] == 'Thumbnail':
                thumb_filename = re.sub('.*/', '', kw['url'])
                thumb_filepath = os.path.join(
                    os.path.dirname(__file__), '..', '..', 'dev_data',
                    'ghec_map_comps_files', thumb_filename)
                thumb_file = open(thumb_filepath)

                upload_path = os.path.join('thumbs/', thumb_filename)

                if storage.exists(upload_path):
                    # Delete if exists otherwise the (FileSystemStorage)
                    # implementation will create a new file with a unique name
                    storage.delete(upload_path)

                storage.save(upload_path, thumb_file)

            link_new = Link(**kw)
            link_new.save()

        # MapSnapshot
        pprint(mapsnapshot)

        kw = {}
        fields = mapsnapshot['fields']
        for field in fields:
            if field == 'created_dttm':
                continue
            elif field == 'map':
                    kw[field] = map_new
            elif field == 'user':
                kw[field] = Profile.objects.get(
                    username=fields[field][0])
            else:
                kw[field] = fields[field]

        pprint(json.loads(kw['config']))
        snapshot_new = MapSnapshot(**kw)
        snapshot_new.save()

        return False
