#!/bin/bash                                                                 
IFS='
'
( for l in $(pip freeze | grep -v "github.com/GeoNode/geonode.git"); do
     
    name="$(echo "$l" | sed 's/==.*//g')"
    major="$(echo "$l" | sed 's/^.*==//g;s/^\([^\.]*\).*/\1/g')"
    minor="$(echo "$l" | sed 's/^.*==//g;s/^[^\.]*\.\([^\.]*\).*/\1/g')"
    minornum="$(echo "$minor" | sed 's/[^0-9].*//g')"
    rest="$(echo "$l" | sed 's/^.*==//g;s/^[^\.]*\.[^\.]*//g')"
     
    echo "$name >= $major.$minor$rest , < $major.$((minornum + 1))"

done ) > gem_geonode_requirements.txt

