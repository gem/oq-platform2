oq-private
==========

Private data for "Instrumental Catalogue", "Historical Catalogue" and certificates
 for oq-platform https protocol.


isc_data history (md5sum, original name)
----------------------------------------

Sat Jun 30 15:36:58 2012 +0200
80bea2ba461e508b03d270fc1daa5b69  ISC\_preliminary_2012_05.csv => isc_data.csv

Tue, 10 Jul 2012 15:07:41 +0200
a96afaeeb6a844074abd2909c237ce0d  isc-gem-cat.csv => isc_data.csv
7c5ebafd7d262c045fc46a6f89430962  isc-gem-app.csv => isc_data_app.csv


ghec_data history (md5sum, original name)
-----------------------------------------

Fri, 12 Apr 2013 14:49:20 +0200
dc5c924ef370f74cc113c7e51ba9c329  src/GEM-GHEC-v1.txt => (processing) => ghec_data.csv
NOTE: If a new version of GHEC arrives put into ./src and process it with the command:
      ./bin/ghec_norm.sh ./src/GEM-GHEC-v1.txt ./ghec_data.csv

Wed, 17 Apr 2013 16:31:44 +0200
b42b06a9ac30416ed746b438f8285873  src/GEM-GHEC-v1.1.txt => ghec_data.csv


ssl
---

self-signed
-----------
Into the 'self-signed' directory you can find certificates to be used
to move oq-platform from http to https protocol for development.

