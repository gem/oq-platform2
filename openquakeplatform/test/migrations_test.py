from django_migration_testcase import MigrationTest


class VulnMigrationTest(MigrationTest):

    app_name = 'vulnerability'
    before = '0001_initial'
    after = '0003_auto_20190704_0901'

    def test_migration(self):

        MyModel = self.get_model_before('funcdistrdtldiscr')

        self.run_migration()

        MyModel = self.get_model_after('funcdistrdtldiscr')
