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
workspace = cat.get_workspace(name_workspace)

if workspace:
    pass
else:
    ws = cat.create_workspace(name_workspace, '%s' % folder_workspace)

datastore = cat.get_store(name)

if datastore:
    pass
else:
    cat.create_featurestore(name, dir_shapefile, workspace)

with open("%s/%s.sld" % (folder_shape, name)) as f:
    cat.create_style(name, f.read(), overwrite=True)

layer = cat.get_layer(name_layer)
layer._set_default_style(name_store)
cat.save(layer)

resource = cat.get_resource(name, workspace=name_workspace)
# print dir(resource)
resource.title = title
resource.abstract = abstract
resource.keywords = keywords
cat.save(resource)

# output
if layer:
    print "Updated layer %s" % name_layer
else:
    print "Created layer %s" % name_layer
