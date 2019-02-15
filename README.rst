Openquake Platform
==================

Development Installation
------------------------

Install the following dependencies::

    for Ubuntu: build-essential python-dev python-virtualenv virtualenvwrapper git postgresql-9.1 postgresql-server-dev-9.1 postgresql-9.1-postgis openjdk-6-jre libxml2 libxml2-dev libxslt1-dev libxslt1.1 libblas-dev liblapack-dev curl wget xmlstarlet gfortran

Create a virtual environment::

    $ virtualenv platform

Clone the git repo::

    $ git clone https://github.com/gem/oq-platform2

Change directory to the downloaded repository directory::

    $ cd oq-platform2

Install PostgreSQL and PostGIS. For best results, stick with PostgreSQL 9.5
and PostGIS 2.2.

Install and run the application::

    $ pip install -e oq-platform2

(Optional.) Add bing maps api key to local_settings.py by modifying the BING_KEY flag.

(Optional.) Set Global Exposure Database (GED) settings. Copy the sample config
file and customize the settings according to your database configuration::

    $ cp openquakeplatform/ged_settings.py.tmpl openquakeplatform/ged_settings.py


Usage
-----

Once your development environment is set up, you can just run the application
from the `openquakeplatform` dir in the root of the git clone::

    $ source /usr/local/bin/virtualenvwrapper.sh  # to enable venv
    $ paver start -b 0.0.0.0:8000

To stop the application at any time::

    $ paver stop

To re-start the application::

    $ paver start -b 0.0.0.0:8000

