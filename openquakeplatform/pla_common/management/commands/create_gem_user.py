from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class Command(BaseCommand):

    def handle(*args, **options):

        gem_username = 'GEM'
        gem_pwd = 'GEM'
        groupname = 'vulnerability-editors'

        # Create Gem user without password
        User = get_user_model()
        gem_user = User.objects.create_user(username=gem_username,
                                            email='info@globalquakemodel.org',
                                            first_name=gem_username,
                                            last_name='Foundation',
                                            organization='Gem Foundation',
                                            city='Pavia (PV)',
                                            voice='+390000000000',
                                            zipcode='27100',
                                            country='ITA')

        # Print if create Gem user is successfully
        if gem_user.first_name == gem_username:
            print('GEM user created')
        else:
            raise ValueError

        # Set pwd for Gem user
        gem_user.set_password(gem_pwd)
        gem_user.save()

        # Added Gen user in a group
        UserGroup = Group.objects.get(name=groupname)
        gem_user.groups.add(UserGroup)
