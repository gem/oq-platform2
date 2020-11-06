import os
import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = ('Extract users')

    def handle(self, user_fname, *args, **options):

        User = get_user_model()

        for user in user_load:
            fields = user['fields']

            # Add users
            if (fields['username'] == 'AnonymousUser'
                    or fields['username'] == 'GEM'):
                continue

            username = fields['username']
            email = fields['email']
            first_name = fields['first_name']
            last_name = fields['last_name']
            is_active = fields['is_active']
            is_super = fields['is_superuser']
            is_staff = fields['is_staff']

            gem_user = User.objects.model(
                                           first_name=first_name,
                                           last_name=last_name,
                                           email=email,
                                           is_active=is_active,
                                           is_superuser=is_super,
                                           is_staff=is_staff
                                         )

            print('%s user created' % username)
