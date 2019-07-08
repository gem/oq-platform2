import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "local_settings")
# from openquakeplatform.vulnerability.models import FuncDistrVulnDiscr, FDS
from django.apps import apps
from django.test import TestCase
from django.db.migrations.executor import MigrationExecutor
from django.db import connection

# import pdb
# pdb.set_trace()


class TestMigrations(TestCase):

    @property
    def app(self):
        return apps.get_containing_app_config(type(self).__module__).name

    migrate_from = None
    migrate_to = None

    def setUp(self):
        assert self.migrate_from and self.migrate_to, \
            "TestCase '{}' must define migrate_from and migrate_to properties".format(type(self).__name__)
        self.migrate_from = [(self.app, self.migrate_from)]
        self.migrate_to = [(self.app, self.migrate_to)]
        executor = MigrationExecutor(connection)
        old_apps = executor.loader.project_state(self.migrate_from).apps
        # old_apps = executor.loader.project_state(self.migrate_from).FuncDistrVulnDiscr

        # Reverse to the original migration
        executor.migrate(self.migrate_from)

        self.setUpBeforeMigration(old_apps)

        # Run the migration to test
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()  # reload.
        executor.migrate(self.migrate_to)

        self.apps = executor.loader.project_state(self.migrate_to).apps

        print(self.apps)

    def setUpBeforeMigration(self, apps):
        pass


class TagsTestCase(TestMigrations):

    migrate_from = '0002_auto_20190703_1424'
    migrate_to = '0003_auto_20190704_0901'

    def setUpBeforeMigration(self, apps):
        BlogPost = apps.get_model('blog', 'Post')
        self.post_id = BlogPost.objects.create(
            title="A test post with tags",
            body="",
            tags="tag1 tag2",
        ).id

    def test_tags_migrated(self):
        BlogPost = self.apps.get_model('blog', 'Post')
        post = BlogPost.objects.get(id=self.post_id)

        self.assertEqual(post.tags.count(), 2)
        self.assertEqual(post.tags.all()[0].name, "tag1")
        self.assertEqual(post.tags.all()[1].name, "tag2")
