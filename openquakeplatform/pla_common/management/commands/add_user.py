import os
import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class Command(BaseCommand):
    args = '<auth_user.json>'
    help = ('Import users')

    def handle(self, user_fname, *args, **options):
        devel_data = os.getenv("DEVEL_DATA")
        prod_inst = os.getenv("PROD_INSTALL")
        user_json = open(user_fname).read()
        user_load = json.loads(user_json)

        User = get_user_model()

        for user in user_load:
            fields = user['fields']

            # Add users
            if (fields['username'] == 'AnonymousUser'
                    or fields['username'] == 'GEM'):
                continue
            if (devel_data != 'y'
                    or prod_inst != 'y'):
                if (fields['username'] == 'admin'):
                    continue

            username = fields['username']
            email = fields['email']
            first_name = fields['first_name']
            last_name = fields['last_name']
            password = fields['password']
            is_active = fields['is_active']
            is_super = fields['is_superuser']
            is_staff = fields['is_staff']

            # Set list of groups
            groupnames = [groupname.encode("utf-8")
                          for groupname in fields['groups'][0]]

            gem_user = User.objects.model(
                                           username=username,
                                           email=email,
                                           password=password,
                                           first_name=first_name,
                                           last_name=last_name,
                                           is_active=is_active,
                                           is_superuser=is_super,
                                           is_staff=is_staff
                                         )
            gem_user.save()

            # Add list group for single user
            for groupname in groupnames:
                # Add group to user
                UserGroup = Group.objects.get(name=groupname)
                gem_user.groups.add(UserGroup)

            print('%s user created' % username)
