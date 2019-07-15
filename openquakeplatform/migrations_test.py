# import unittest
from django_migration_testcase import MigrationTest
from django.contrib.auth import get_user_model


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

        generalinformation = self.get_model_before('generalinformation')
        newgen = generalinformation(
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

        # fragilityfunc = self.get_model_before('fragilityfunc')
        # newfragilityfunc = fragilityfunc(
        #                                  owner=user,
        #                                  general_information_id=1000,
        #                                  method_of_estimation="2",
        #                                  func_distr_type="2"
        #                                 )
        # newfragilityfunc.save()

        # funcdistrdtldiscr = self.get_model_before('funcdistrdtldiscr')
        # newrec = funcdistrdtldiscr(
        #                            owner=user,
        #                            damage_to_loss_func_id='1000',
        #                            # var_mean_val='',
        #                            # var_val_coeff='',
        #                            # func_distr_shape=''
        #                           )
        # newrec.save()

        self.run_migration()

        generalinformation = self.get_model_after('generalinformation')
        # fragilityfunc = self.get_model_after('funcdistrdtldiscr')
        # funcdistrdtldiscr = self.get_model_after('funcdistrdtldiscr')
