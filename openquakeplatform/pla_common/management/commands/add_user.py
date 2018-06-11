import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class Command(BaseCommand):
    args = '<auth_user_demo.json>'
    help = ('Import users')

    def handle(self, user_fname, *args, **options):
        user_json = open(user_fname).read()
        user_load = json.loads(user_json)

        User = get_user_model()

        for user in user_load:
            fields = user['fields']

            # User not to be imported
            gem = 'GEM'
            anonymous = 'AnonymousUser'
            admin = 'admin'

            # Add users
            if (fields['username'] != '%s' % gem
                and fields['username'] != '%s' % anonymous
                    and fields['username'] != '%s' % admin):

                        username = fields['username']
                        email = fields['email']
                        first_name = fields['first_name']
                        last_name = fields['last_name']
                        password = fields['password']
                        is_active = fields['is_active']
                        is_super = fields['is_superuser']
                        is_staff = fields['is_staff']
                        groupname = fields['groups']

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

                        # Print if create users is successfully
                        if gem_user.username == username:
                            print('%s user created' % username)
                        else:
                            raise ValueError

                        # Added user into the group assigned
                        UserGroup = Group.objects.get(name=groupname)
                        gem_user.groups.add(UserGroup)
