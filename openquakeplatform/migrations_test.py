# import unittest
from django_migration_testcase import MigrationTest

# @unittest.skip("temporarily disabled")
class VulnMigrationTest(MigrationTest):

    app_name = 'vulnerability'
    before = '0001_initial'
    after = '0002_func_dist_shape_def_val_ctx'

    def test_migration_model_1(self):

        MyModel_1 = self.get_model_before('funcdistrdtldiscr')

        self.run_migration()

        MyModel_1 = self.get_model_after('funcdistrdtldiscr')

    def test_migration_model_2(self):

        MyModel_2 = self.get_model_before('funcdistrfragcont')

        self.run_migration()

        MyModel_2 = self.get_model_after('funcdistrfragcont')

    def test_migration_model_3(self):

        MyModel_3 = self.get_model_before('funcdistrvulncont')

        self.run_migration()

        MyModel_3 = self.get_model_after('funcdistrvulncont')

    def test_migration_model_4(self):

        MyModel_4 = self.get_model_before('funcdistrvulndiscr')

        self.run_migration()

        MyModel_4 = self.get_model_after('funcdistrvulndiscr')
