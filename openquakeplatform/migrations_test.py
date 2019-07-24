# import unittest
from django_migration_testcase import MigrationTest
from openquakeplatform.vulnerability.models import GeneralInformation
from openquakeplatform.vulnerability.models import DamageToLossFunc
from openquakeplatform.vulnerability.models import FuncDistrDTLDiscr
from django.contrib.auth import get_user_model
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "local_settings")


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
        print('Pk: %s' % owner.pk)

        geninformation = self.get_model_before('GeneralInformation')
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

        newgen_istance = GeneralInformation.objects.get(
            name="9 Storey Non-Ductile RC-MRFs")
        print(newgen_istance.pk)

        damloss = self.get_model_before('DamageToLossFunc')

        newdamloss = damloss(
                             owner_id=owner.pk,
                             general_information_id=newgen_istance.pk,
                             method_of_estimation="2",
                             damage_scale="6",
                             resp_var="5"
                             )
        newdamloss.save()

        newdamloss_istance = DamageToLossFunc.objects.get(
            general_information=newgen_istance.pk)

        dtldiscr = self.get_model_before('FuncDistrDTLDiscr')
        newdtldiscr = dtldiscr(
                               owner_id=owner.pk,
                               damage_to_loss_func_id=newdamloss_istance.pk,
                               var_mean_val="0.1;0.2;0.4;0.9;1",
                               func_distr_shape=None
                               )
        newdtldiscr.save()

        self.run_migration()

        # after migrations
        geninformation = self.get_model_after('GeneralInformation')
        damloss = self.get_model_after('DamageToLossFunc')
        dtldiscr = self.get_model_after('FuncDistrDTLDiscr')

        new_gen = GeneralInformation.objects.get(
            name="9 Storey Non-Ductile RC-MRFs")

        new_damloss = DamageToLossFunc.objects.get(
            general_information_id=new_gen.pk)

        new_dtldiscr = FuncDistrDTLDiscr.objects.get(
            damage_to_loss_func_id=new_damloss.pk)

        # check func_distr_shape
        self.assertEqual(new_dtldiscr.func_distr_shape, 1)
