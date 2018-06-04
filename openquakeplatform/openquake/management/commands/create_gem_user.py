from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):

    def handle(*args, **options):

        ## create Gem user without password
        User = get_user_model()
        UserGem = User.objects.create_user(username='GEM',
                                           email='info@globalquakemodel.org',
                                           first_name='GEM',
                                           last_name='Foundation')

        ## Set pwd for Gem user
        UserGem = User.objects.get(username='GEM')
        UserGem.set_password('GEM')
        UserGem.save()

        ## Print if create Gem user is successfully 
        if UserGem.first_name == 'GEM':
            print('GEM user created')
        else:
            raise ValueError
