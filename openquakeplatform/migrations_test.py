from django_migration_testcase import MigrationTest
from openquakeplatform.vulnerability.models import FDS
from django.contrib.auth import get_user_model
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "local_settings")


class VulnMigrationTest(MigrationTest):

    app_name = 'vulnerability'
    before = '0001_initial'
    after = '0005_func_dist_vuln_dtl_scm'

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

        VulnerabilityFunc_be = self.get_model_before('VulnerabilityFunc')
        be_vulnfunc = VulnerabilityFunc_be.objects.create(
            owner_id=owner.pk,
            general_information=be_gen,
            method_of_estimation="1",
            resp_var="5",
            func_distr_type="2"
            )
        be_vulnfunc.save()

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
            var_val_coeff=None,
            func_distr_shape=None
            )
        be_dtldiscr.save()

        FuncDistrVulnDiscr_be = self.get_model_before('FuncDistrVulnDiscr')
        be_distr_vuln_discr = FuncDistrVulnDiscr_be.objects.create(
            owner_id=owner.pk,
            vulnerability_func=be_vulnfunc,
            resp_var_mean_val="0.1;0.2;0.4;0.9;1",
            resp_var_val_coeff="",
            data_pts_num="3"
            )
        be_distr_vuln_discr.save()

        # run migrations
        self.run_migration()

        # after migrations
        GeneralInformation_af = self.get_model_after('GeneralInformation')
        VulnerabilityFunc_af = self.get_model_after('VulnerabilityFunc')

        af_gen = GeneralInformation_af.objects.get(
            name="9 Storey Non-Ductile RC-MRFs")

        af_vul_f = VulnerabilityFunc_af.objects.get(resp_var="5")

        af_dtldiscr = (af_gen.damage_to_loss_func.func_distr_dtl_discr)
        af_vuln_discr = af_vul_f.func_distr_vuln_discr

        # check func_distr_shape, var_val_coeff, resp_var_val_coeff
        self.assertEqual(af_dtldiscr.func_distr_shape, FDS.LOGNORMAL)
        self.assertEqual(af_dtldiscr.var_val_coeff, '0;0;0;0;0')
        self.assertEqual(af_vuln_discr.resp_var_val_coeff, '0;0;0;0;0')
