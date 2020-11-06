import os
import csv
import codecs
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    args = '<csv name>'
    help = ('Extract users')

    def handle(self, user_fname, *args, **options):

        with open(user_fname, 'wb') as csvfile:
            fieldnames = ['email', 'full_name', 'is_active', 'is_superuser', 'is_staff']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            User = get_user_model()

            users = User.objects.all()

            for user in users:

                email = user.email.encode('utf8')
                first_name = user.first_name.encode('utf8')
                last_name = user.last_name.encode('utf8')
                is_active = str(user.is_active)
                is_superuser = str(user.is_superuser)
                is_staff = str(user.is_staff)

                if first_name is not '' and last_name is not '':
                    full_name = '%s %s' % (first_name, last_name)
                else:
                    full_name = '%s%s' % (first_name, last_name)

                writer.writerow({'email': email, 'full_name': full_name, 'is_active': is_active,
                    'is_superuser': is_superuser, 'is_staff': is_staff})

