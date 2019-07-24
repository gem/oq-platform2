from django_migration_testcase import MigrationTest
from openquakeplatform.vulnerability.models import FDS
from django.contrib.auth import get_user_model
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "local_settings")


class VulnMigrationTest(MigrationTest):

    app_name = 'vulnerability'
    before = '0001_initial'
    after = '0002_func_dist_shape_def_val_ctx'

    def test_migration_model(self):

        User = get_user_model()
        user = User.objects.create(
                                  username="admin",
                                  password="admin",
                                  is_superuser="true"
                                 )
        user.save()
        owner = User.objects.get(username="admin")

        GeneralInformation_be = self.get_model_before('GeneralInformation')
        be_gen = GeneralInformation_be.objects.create(
            owner_id=owner.pk,
            name="9 Storey Non-Ductile RC-MRFs",
            category='10',
            material=None,
            type_of_assessment="10",
            article_title="Influence horizontal",
            structure_type="10",
            year="2016",
            )
        be_gen.save()

        DamageToLossFunc_be = self.get_model_before('DamageToLossFunc')

        be_damloss = DamageToLossFunc_be.objects.create(
            owner_id=owner.pk,
            general_information=be_gen,
            method_of_estimation="2",
            damage_scale="6",
            resp_var="5"
            )
        be_damloss.save()

        FuncDistrDTLDiscr_be = self.get_model_before('FuncDistrDTLDiscr')
        be_dtldiscr = FuncDistrDTLDiscr_be.objects.create(
            owner_id=owner.pk,
            damage_to_loss_func=be_damloss,
            var_mean_val="0.1;0.2;0.4;0.9;1",
            func_distr_shape=None
            )
        be_dtldiscr.save()

        self.run_migration()

        # after migrations
        GeneralInformation_af = self.get_model_after('GeneralInformation')

        af_gen = GeneralInformation_af.objects.get(
            name="9 Storey Non-Ductile RC-MRFs")

        af_dtldiscr = af_gen.damage_to_loss_func.func_distr_dtl_discr

        # check func_distr_shape
        self.assertEqual(af_dtldiscr.func_distr_shape, FDS.LOGNORMAL)
