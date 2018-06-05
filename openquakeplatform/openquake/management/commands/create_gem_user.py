from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

class Command(BaseCommand):

    def handle(*args, **options):

        pwgem = 'GEM'
        groupname = 'vulnerability-editors'

        ## Create Gem user without password
        User = get_user_model()
        UserGem = User.objects.create_user(username=pwgem,
                                           email='info@globalquakemodel.org',
                                           first_name=pwgem,
                                           last_name='Foundation')

        ## Set pwd for Gem user
        UserGem = User.objects.get(username=pwgem)
        UserGem.set_password(pwgem)
        UserGem.save()

        ## Added Gen user in a group
        UserGroup = Group.objects.get(name=groupname)
        UserGem.groups.add(UserGroup)

        ## Print if create Gem user is successfully 
        if UserGem.first_name == pwgem:
            print('GEM user created')
        else:
            raise ValueError
