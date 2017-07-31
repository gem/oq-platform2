from geoserver.catalog import Catalog

cat = Catalog("http://localhost:8080/geoserver/rest/", "admin", "geoserver")

workspace = cat.get_workspace("geonode")

## data_store = cat.get_store("ghec", workspace)
## ft = cat.publish_featuretype("myview", "ghec", "EPSG:4326", srs="EPSG:4326")

name = "ghec"

import geoserver.util

dir_shapefile = geoserver.util.shapefile_and_friends("/home/ubuntu/geonode/data/ghec_data_sh/ghec")

with open("/home/ubuntu/geonode/data/ghec_data_sh/ghec.sld") as f:
    cat.create_style(name, f.read(), overwrite=True)

# layer = cat.get_layer("geonode:ghec")
# layer._set_default_style("ghec", "")
# cat.save(layer)

# cat.get_style(name)

## shapefile_and_friends should look on the filesystem to find a shapefile
## and related files based on the base path passed in
##
## dir_shapefile == {
##    'shp': 'ghec.shp',
##    'shx': 'ghec.shx',
##    'prj': 'ghec.prj',
##    'dbf': 'ghec.dbf',
##    'xml': 'ghec.xml',
##    'sld': 'ghec.sld'
## }
## 'data' is required (there may be a 'schema' alternative later, for creating empty featuretypes)
## 'workspace' is optional (GeoServer's default workspace is used by... default)
## 'name' is required
ft = cat.create_featurestore(name, dir_shapefile, workspace)

resource = cat.get_resource("geonode:ghec", workspace="geonode")
resource.title = "thats my title"
cat.save(resource)

layer = cat.get_layer("geonode:ghec")
layer._set_default_style("ghec")
cat.save(layer)

