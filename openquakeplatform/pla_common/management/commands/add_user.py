import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    args = '<auth_user_demo.json>'
    help = ('Import users')

    def handle(self, user_fname, *args, **options):
        user_json = open(user_fname).read()
        user_load = json.loads(user_json)

        User = get_user_model()

        for user in user_load:
            fields = user['fields']
            username = fields['username']
            email = fields['email']
            first_name = fields['first_name']
            last_name = fields['last_name']
            password = fields['password']

            gem_user = User.objects.create_user(
                                           username=username,
                                           email=email,
                                           password=password,
                                           first_name=first_name,
                                           last_name=last_name)

            # Print if create Gem user is successfully
            if gem_user.username == username:
                print('%s user created' % username)
            else:
                raise ValueError

