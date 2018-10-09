# Copyright (c) 2015-2018, GEM Foundation.
#
# This program is free software: you can redistribute it and/or modify
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib.gis.db import models
from django.db.models import Lookup
from django.db.models.fields import Field


@Field.register_lookup
class CaseInsensitiveMatch(Lookup):
    """
    Adding 'unaccent' to the standard lookup_name
    """
    lookup_name = 'unaccent'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s =~@ %s' % (lhs, rhs), params


class UnaccentCharField(models.CharField):
    """
    Custom CharField that can be filtered using the 'unaccent' custom
    lookup criterion. It leverages the custom '=~@' postgres operator,
    that uses as procedure the custom 'icompare_unaccent' function.
    This fieldtype can therefore be filtered both case insensitive
    and accent insensitive.
    """
    def get_db_prep_lookup(self, lookup_type, value,
                           connection, prepared=False):
        if lookup_type == 'unaccent':
            # EXAMPLE:
            # Filtering GeneralInformation by author,
            # filter(authors__unaccent=author), with author='test'
            # would produce a query like:
            # SELECT [...] WHERE
            # UPPER
            # ("vulnerability_generalinformation"."authors"::text) =~@ %test%
            return ["%%%s%%" % connection.ops.prep_for_like_query(value)]
        else:
            return super(UnaccentCharField, self).get_db_prep_lookup(
                lookup_type, value, connection, prepared)

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'unaccent':
            return value
        else:
            return super(UnaccentCharField, self).get_prep_lookup(lookup_type,
                                                                  value)
    pass
