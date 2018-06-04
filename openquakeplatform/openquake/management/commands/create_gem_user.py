from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):

    def handle(*args, **options):
        User = get_user_model()
        UserGem = User.objects.create_user(username='GEM',
                                     email='info@globalquakemodel.org',
                                     first_name='GEM',
                                     last_name='Foundation')

        UserGem = User.objects.get(username='GEM')
        UserGem.set_password('GEM')
        UserGem.save()


        if UserGem.first_name == 'GEM':
            print('GEM user created')
        else:
            raise ValueError

