# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ghec_viewer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Measure',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('the_geom', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('en', models.CharField(max_length=255)),
                ('src', models.CharField(max_length=255)),
                ('yea', models.IntegerField()),
                ('mon', models.IntegerField(default=None, null=True, blank=True)),
                ('day', models.IntegerField(default=None, null=True, blank=True)),
                ('hou', models.IntegerField(default=None, null=True, blank=True)),
                ('min', models.IntegerField(default=None, null=True, blank=True)),
                ('sec', models.FloatField(default=None, null=True, blank=True)),
                ('are', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('lat', models.FloatField()),
                ('lon', models.FloatField()),
                ('latunc', models.FloatField(default=None, null=True, blank=True)),
                ('lonunc', models.FloatField(default=None, null=True, blank=True)),
                ('epdet', models.CharField(default=b'', max_length=5, null=True, blank=True, choices=[(b'bx', b'determined according to the method by Gasperini et al. (1999; 2010'), (b'bw', b'determined according to the method by Bakun and Wenthworth (1997)'), (b'cat', b'derived from another catalogue'), (b'instr', b'instrumental')])),
                ('dep', models.FloatField(default=None, null=True, blank=True)),
                ('io', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('msrc', models.CharField(max_length=255)),
                ('m', models.FloatField()),
                ('munc', models.FloatField(default=None, null=True, blank=True)),
                ('mtyp', models.CharField(default=b'', max_length=5, null=True, blank=True, choices=[(b'w', b'Mw'), (b's', b'Ms'), (b'jma', b'Mjma')])),
                ('mdet', models.CharField(default=b'', max_length=5, null=True, blank=True, choices=[(b'bx', b'determined according to the method by Gasperini et al. (1999; 2010)'), (b'bw', b'determined according to the method by Bakun and Wenthworth (1997)'), (b'int', b'converted from epicentral or maximum intensity'), (b'cat', b'derived from another catalogue'), (b'instr', b'instrumental')])),
                ('mdpsrc', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('mdpn', models.IntegerField(default=None, null=True, blank=True)),
                ('mdpix', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('mdpsc', models.CharField(default=b'', max_length=5, null=True, blank=True, choices=[(b'MM', b'modified Mercalli'), (b'MSK', b'Medvedev-Sponheuer-Karnik'), (b'EMS', b'European Macroseimic Scale'), (b'MCS', b'Mercalli-Cancani-Sieberg'), (b'JMA', b'Japan Meteorological Agency')])),
                ('rem', models.CharField(default=b'', max_length=1024, null=True, blank=True)),
            ],
            options={
                'managed': False,
            },
        ),
    ]
