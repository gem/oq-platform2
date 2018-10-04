# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL("""
DROP OPERATOR IF EXISTS =~@ (character varying, character varying);
DROP FUNCTION IF EXISTS icompare_unaccent(character varying, character varying);
DROP EXTENSION IF EXISTS unaccent;

CREATE EXTENSION unaccent;
CREATE FUNCTION icompare_unaccent(character varying, character varying)
    RETURNS boolean
    AS 'SELECT upper(unaccent($1)) LIKE upper(unaccent($2));'
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;

CREATE OPERATOR =~@ (
    LEFTARG = character varying,
    RIGHTARG = character varying,
    PROCEDURE = icompare_unaccent,
    NEGATOR = !=~@
);
"""),
    ]
