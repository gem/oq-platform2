import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    args = '<auth_user.json>'
    help = ('Import users')

    def handle(self, user_fname, *args, **options):
        user_json = open(user_fname).read()
        user_load = json.loads(user_json)

        User = get_user_model()

        for user in user_load:
            username = user['fields']['username']
            email = user['fields']['email']
            first_name = user['fields']['first_name']
            last_name = user['fields']['last_name']
            password = user['fields']['password']

            gem_user = User.objects.create_user(
                                           username=username,
                                           email=email,
                                           first_name=first_name,
                                           last_name=last_name)

            # Print if create Gem user is successfully
            if gem_user.username == username:
                print('%s user created' % username)
            else:
                raise ValueError

            # Set pwd for Gem user
            gem_user.set_password(password)
            gem_user.save()

            # print(user['fields']['username'])
            # print(user['fields']['email'])
            # print(user['fields']['first_name'])
            # print(user['fields']['last_name'])
