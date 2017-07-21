from geoserver.catalog import Catalog
cat = Catalog("http://localhost:8080/geoserver/rest/", "admin", "geoserver")
workspace = cat.get_workspace("geonode")
import geoserver.util
dir_shapefile = geoserver.util.shapefile_and_friends("/home/ubuntu/geonode/data/ghec_data_sh/ghec")
with open("/home/ubuntu/oq-private/ghec_data_sh/ghec.sld") as f:
    cat.create_style("ghec", f.read())
that_layer = cat.get_layer("ghec")
that_layer.default_style = 'ghec'
# shapefile_and_friends should look on the filesystem to find a shapefile
# and related files based on the base path passed in
#
# shapefile_plus_sidecars == {
#    'shp': 'ghec.shp',
#    'shx': 'ghec.shx',
#    'prj': 'ghec.prj',
#    'dbf': 'ghec.dbf',
#    'xml': 'ghec.xml',
#    'sld': 'ghec.sld'
# }
# 'data' is required (there may be a 'schema' alternative later, for creating empty featuretypes)
# 'workspace' is optional (GeoServer's default workspace is used by... default)
# 'name' is required
ft = cat.create_featurestore("ghec", dir_shapefile, workspace)
