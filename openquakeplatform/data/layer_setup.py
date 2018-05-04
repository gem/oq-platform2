#!/usr/bin/env python
import sys
import importlib
from geoserver.catalog import Catalog
import geoserver.util

mod = importlib.import_module(sys.argv[1])

cat = Catalog("%s" % mod.folder_rest, "admin", "geoserver")

dir_shapefile = geoserver.util.shapefile_and_friends("%s/%s" % (mod.folder_shape,
                                                                mod.name))
workspace = cat.get_workspace("%s" % mod.name_workspace)

if workspace:
    pass
else:
    ws = cat.create_workspace(mod.name_workspace, '%s' % mod.folder_workspace)

with open("%s/%s.sld" % (mod.folder_shape, mod.name)) as f:
    cat.create_style(mod.name, f.read(), overwrite=True)

fs = cat.create_featurestore("%s" % mod.name, dir_shapefile, workspace)

layer = cat.get_layer("%s" % mod.name_layer)
layer._set_default_style("%s" % mod.name_store)
cat.save(layer)

resource = cat.get_resource("%s" % mod.name, workspace="%s" % mod.name_workspace)
# print dir(resource)
resource.title = "%s" % mod.title
resource.abstract = "%s" % mod.abstract
resource.keywords = mod.keywords
# resource.metadata_links = [('text/xml', 'other', '%s.xml' % name),]
cat.save(resource)

# output
if layer:
    print "Updated layer %s" % mod.name_layer
else:
    print "Created layer %s" % mod.name_layer
