#!/usr/bin/env python

from geoserver.catalog import Catalog
import geoserver.util
from metadata import (folder_rest,
                      name_workspace,
                      folder_workspace,
                      name,
                      name_store,
                      name_layer,
                      title,
                      abstract,
                      keywords,
                      folder_shape)

cat = Catalog("%s" % folder_rest, "admin", "geoserver")

dir_shapefile = geoserver.util.shapefile_and_friends("%s/%s" % (folder_shape,
                                                                name))
workspace = cat.get_workspace("%s" % name_workspace)

if workspace:
    pass
else:
    ws = cat.create_workspace(name_workspace, '%s' % folder_workspace)

with open("%s/%s.sld" % (folder_shape, name)) as f:
    cat.create_style(name, f.read(), overwrite=True)

fs = cat.create_featurestore("%s" %name, dir_shapefile, workspace)

layer = cat.get_layer("%s" % name_layer)
layer._set_default_style("%s" % name_store)
cat.save(layer)

resource = cat.get_resource("%s" % name, workspace="%s" % name_workspace)
# print dir(resource)
resource.title = "%s" % title
resource.abstract = "%s" % abstract
resource.keywords = keywords
# resource.metadata_links = [('text/xml', 'other', '%s.xml' % name),]
cat.save(resource)

# output
if layer:
    print "Updated layer %s" % name_layer
else:
    print "Created layer %s" % name_layer
