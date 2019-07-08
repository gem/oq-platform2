import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "local_settings")
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

# import pdb;pdb.set_trace()


User = 'Armando'
print('User: %s' % User)


def test_migrate_profile_to_user(transactional_db):
    executor = MigrationExecutor(connection)
    app = "vulnerability"
    print(app)
    migrate_from = [(app, "0002_auto_20190703_1424")]
    migrate_to = [(app, "0003_auto_20190704_0901")]

    executor.migrate(migrate_from)
    old_apps = executor.loader.project_state(migrate_from).apps

    print(old_apps)

    # Create some old data.
    Profile = old_apps.get_model(app, "Profile")
    old_profile = Profile.objects.create(model_name="model_name",
                                         name="name",
                                         field="field")
    # Migrate forwards.
    executor.loader.build_graph()  # reload.
    executor.migrate(migrate_to)
    new_apps = executor.loader.project_state(migrate_to).apps

    # Test the new data.
    Profile = new_apps.get_model(app, "Profile")
    User = new_apps.get_model(app, "UserEntry")
    print('User: %s' % User)
    assert 'firstname' not in Profile._meta.get_all_field_names()

    user = User.objects.get(email='email')
    profile = Profile.objects.get(user__email='email')
    assert user.profile.pk == old_profile.pk == profile.pk
    assert profile.user.email == 'email'
    assert profile.user.first_name == 'firstname'
    assert profile.user.last_name == 'lastname'
