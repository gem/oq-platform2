# import unittest
from django_migration_testcase import MigrationTest
from django.contrib.auth import get_user_model
from openquakeplatform.vulnerability.models import GeneralInformation
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "local_settings")


# @unittest.skip("temporarily disabled")
class VulnMigrationTest(MigrationTest):

    app_name = 'vulnerability'
    before = '0001_initial'
    after = '0002_func_dist_shape_def_val_ctx'

    def test_migration_model(self):

        User = get_user_model()
        user = User.objects.model(
                                  username="admin",
                                  password="admin",
                                  is_superuser="true"
                                 )
        user.save()
        owner = User.objects.get(username="admin")
        print(owner.pk)

        geninformation = self.get_model_before('generalinformation')
        newgen = geninformation(
                                owner_id=owner.pk,
                                name="9 Storey Non-Ductile RC-MRFs",
                                category='10',
                                material=None,
                                type_of_assessment="10",
                                article_title="Influence horizontal",
                                structure_type="10",
                                year="2016"
                               )
        newgen.save()

        # import pdb;pdb.set_trace()
        self.run_migration()

        geninformation = self.get_model_after('generalinformation')

        newgen = GeneralInformation.objects.get(
            name="9 Storey Non-Ductile RC-MRFs")
        print('Function: %s' % newgen.pk)
