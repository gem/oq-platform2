# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('isc_viewer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Measure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('src_id', models.IntegerField(default=-1)),
                ('date', models.DateTimeField()),
                ('lat', models.FloatField()),
                ('lon', models.FloatField()),
                ('the_geom', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('smajax', models.FloatField(null=True, blank=True)),
                ('sminax', models.FloatField(null=True, blank=True)),
                ('strike', models.FloatField(null=True, blank=True)),
                ('epic_q', models.CharField(default=b'', max_length=1, blank=True, choices=[(b'A', b'Highest quality'), (b'B', b'Medium quality'), (b'C', b'Lowest quality')])),
                ('depth', models.FloatField(null=True, blank=True)),
                ('depth_unc', models.FloatField(null=True, blank=True)),
                ('depth_q', models.CharField(default=b'', max_length=1, blank=True, choices=[(b'A', b'Highest quality'), (b'B', b'Medium quality'), (b'C', b'Lowest quality')])),
                ('mw', models.FloatField(null=True, blank=True)),
                ('mw_unc', models.FloatField(null=True, blank=True)),
                ('mw_q', models.CharField(default=b'', max_length=1, blank=True, choices=[(b'A', b'Highest quality'), (b'B', b'Medium quality'), (b'C', b'Lowest quality')])),
                ('s', models.CharField(default=b'', max_length=1, blank=True, choices=[(b'p', b'Mw proxy'), (b'd', b'direct Mw computation')])),
                ('mo', models.FloatField(null=True, blank=True)),
                ('fac', models.FloatField(null=True, blank=True)),
                ('mo_auth', models.CharField(default=b'', max_length=255, blank=True)),
                ('mpp', models.FloatField(null=True, blank=True)),
                ('mpr', models.FloatField(null=True, blank=True)),
                ('mrr', models.FloatField(null=True, blank=True)),
                ('mrt', models.FloatField(null=True, blank=True)),
                ('mtp', models.FloatField(null=True, blank=True)),
                ('mtt', models.FloatField(null=True, blank=True)),
                ('eventid', models.IntegerField(default=-1)),
            ],
            options={
                'managed': False,
            },
        ),
    ]
