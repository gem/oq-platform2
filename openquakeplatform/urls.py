# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from django.conf.urls import include, patterns, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from geonode.sitemap import LayerSitemap, MapSitemap
from django.views.generic import TemplateView, RedirectView
from django.contrib import admin
import openquakeplatform.common.views as oq_common_views

import geonode.proxy.urls

from geonode.api.urls import api
from geonode.api.views import verify_token, roles, users, admin_role

import autocomplete_light


# Setup Django Admin
autocomplete_light.autodiscover()

admin.autodiscover()

js_info_dict = {
    'domain': 'djangojs',
    'packages': ('geonode',)
}
sitemaps = {
    "layer": LayerSitemap,
    "map": MapSitemap
}

<<<<<<< HEAD
urlpatterns = patterns(
    '',
    # Static pages
    url(r'^/?$',
        TemplateView.as_view(template_name='index.html'),
        name='home'),
    url(r'^help/$',
        TemplateView.as_view(template_name='help.html'),
        name='help'),
    url(r'^developer/$',
        TemplateView.as_view(
            template_name='developer.html'),
        name='developer'),
    url(r'^about/$',
        RedirectView.as_view(
            url='https://www.globalquakemodel.org/oq-getting-started'),
        name='about'),
    url(r'^explore/$',
        TemplateView.as_view(template_name='explore.html'),
        name='explore'),
    url(r'^share/$',
        TemplateView.as_view(template_name='share.html'),
        name='share'),
    url(r'^calculate/$',
        TemplateView.as_view(
            template_name='calculate.html'),
        name='calculate'),
    url(r'^account/terms/$',
        TemplateView.as_view(
            template_name='account/terms.html'),
        name='terms'),
    url(r'^versions/$', oq_common_views.versions,
        name='oq_common_versions'),
    url(r'^grv/$', TemplateView.as_view(
        template_name="grv/grv_viewer.html"), name='grv'),
    url(r'^irv/',
        include('openquakeplatform.irv.urls')),

    # svir
    (r'^svir/', include('openquakeplatform.svir.urls')),
    (r'^world/', include('openquakeplatform.world.urls')),
    url(r'^irv/',
        include('openquakeplatform.irv.urls')),

    # Layer views
    (r'^layers/', include('geonode.layers.urls')),

    # Map views
    (r'^maps/', include('geonode.maps.urls')),

    # Catalogue views
    (r'^catalogue/', include('geonode.catalogue.urls')),

    # data.json
    url(r'^data.json$', 'geonode.catalogue.views.data_json',
        name='data_json'),

    # ident
    url(r'^ident.json$', 'geonode.views.ident_json',
        name='ident_json'),

    # h keywords
    url(r'^h_keywords_api$', 'geonode.views.h_keywords',
        name='h_keywords_api'),

    # Search views
    url(r'^search/$',
        TemplateView.as_view(
            template_name='search/search.html'),
        name='search'),

    # geodetic
    url(r'^geodetic/$',
        TemplateView.as_view(
            template_name="geodetic.html"),
        name='geodetic'),

    # Social views
    (r"^account/", include("account.urls")),
    (r'^people/', include('geonode.people.urls')),
    (r'^avatar/', include('avatar.urls')),
    (r'^comments/', include('dialogos.urls')),
    (r'^ratings/', include('agon_ratings.urls')),
    (r'^activity/', include('actstream.urls')),
    (r'^announcements/', include('announcements.urls')),
    (r'^messages/', include('user_messages.urls')),
    (r'^social/', include('geonode.social.urls')),
    (r'^security/', include('geonode.security.urls')),

    # svir
    (r'^svir/', include('openquakeplatform.svir.urls')),
    (r'^world/', include('openquakeplatform.world.urls')),

    # Accounts
    url(r'^account/ajax_login$', 'geonode.views.ajax_login',
        name='account_ajax_login'),
    url(r'^account/ajax_lookup$',
        'geonode.views.ajax_lookup',
        name='account_ajax_lookup'),

    # Meta
    url(r'^lang\.js$',
        TemplateView.as_view(
            template_name='lang.js',
            content_type='text/javascript'),
        name='lang'),

    url(r'^jsi18n/$',
        'django.views.i18n.javascript_catalog',
        js_info_dict, name='jscat'),
    url(r'^sitemap\.xml$',
        'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': sitemaps},
        name='sitemap'),

    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^autocomplete/', include('autocomplete_light.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^groups/', include('geonode.groups.urls')),
    (r'^documents/', include('geonode.documents.urls')),
    (r'^services/', include('geonode.services.urls')),

    # GeoServer Helper Views
    (r'^gs/', include('geonode.geoserver.urls')),
    # OAuth Provider
    url(r'^o/', include('oauth2_provider.urls',
        namespace='oauth2_provider')),

    # Api Views
    url(r'^api/o/v4/tokeninfo', verify_token,
        name='tokeninfo'),
    url(r'^api/roles', roles, name='roles'),
    url(r'^api/adminRole', admin_role, name='adminRole'),
    url(r'^api/users', users, name='users'),
    url(r'', include(api.urls)),
    )
=======
urlpatterns = patterns('',
                       # Static pages
                       url(r'^isc_viewer/$', TemplateView.as_view(
                           template_name="isc_viewer.html"), name='isc_viewer'),
                       url(r'^ghec_viewer/$', TemplateView.as_view(
                           template_name="ghec_viewer.html"), name='ghec_viewer'),
                       url(r'^/?$',
                           TemplateView.as_view(template_name='index.html'),
                           name='home'),
                       url(r'^help/$',
                           TemplateView.as_view(template_name='help.html'),
                           name='help'),
                       url(r'^developer/$',
                           TemplateView.as_view(
                               template_name='developer.html'),
                           name='developer'),
                       url(r'^about/$',
                           RedirectView.as_view(url='https://www.globalquakemodel.org/oq-getting-started'),
                           name='about'),
                       url(r'^explore/$',
                           TemplateView.as_view(template_name='explore.html'),
                           name='explore'),
                       url(r'^share/$',
                           TemplateView.as_view(template_name='share.html'),
                           name='share'),
                       url(r'^calculate/$',
                           TemplateView.as_view(
                               template_name='calculate.html'),
                           name='calculate'),
                       url(r'^account/terms/$',
                           TemplateView.as_view(
                               template_name='account/terms.html'),
                           name='terms'),
                       url(r'^versions/$', oq_common_views.versions,
                           name='oq_common_versions'),
                       url(r'^grv/$', TemplateView.as_view(
                           template_name="grv/grv_viewer.html"), name='grv'),
                       # Layer views
                       (r'^layers/', include('geonode.layers.urls')),

                       # Map views
                       (r'^maps/', include('geonode.maps.urls')),

                       # Catalogue views
                       (r'^catalogue/', include('geonode.catalogue.urls')),

                       # data.json
                       url(r'^data.json$', 'geonode.catalogue.views.data_json',
                           name='data_json'),

                       # ident
                       url(r'^ident.json$', 'geonode.views.ident_json',
                           name='ident_json'),

                       # h keywords
                       url(r'^h_keywords_api$', 'geonode.views.h_keywords',
                           name='h_keywords_api'),

                       # Search views
                       url(r'^search/$',
                           TemplateView.as_view(
                               template_name='search/search.html'),
                           name='search'),

                       # geodetic
                       url(r'^geodetic/$',
                           TemplateView.as_view(
                               template_name="geodetic.html"),
                           name='geodetic'),

                       # Social views
                       (r"^account/", include("account.urls")),
                       (r'^people/', include('geonode.people.urls')),
                       (r'^avatar/', include('avatar.urls')),
                       (r'^comments/', include('dialogos.urls')),
                       (r'^ratings/', include('agon_ratings.urls')),
                       (r'^activity/', include('actstream.urls')),
                       (r'^announcements/', include('announcements.urls')),
                       (r'^messages/', include('user_messages.urls')),
                       (r'^social/', include('geonode.social.urls')),
                       (r'^security/', include('geonode.security.urls')),

                       # Accounts
                       url(r'^account/ajax_login$', 'geonode.views.ajax_login',
                           name='account_ajax_login'),
                       url(r'^account/ajax_lookup$',
                           'geonode.views.ajax_lookup',
                           name='account_ajax_lookup'),

                       # Meta
                       url(r'^lang\.js$',
                           TemplateView.as_view(
                               template_name='lang.js',
                               content_type='text/javascript'),
                           name='lang'),

                       url(r'^jsi18n/$',
                           'django.views.i18n.javascript_catalog',
                           js_info_dict, name='jscat'),
                       url(r'^sitemap\.xml$',
                           'django.contrib.sitemaps.views.sitemap',
                           {'sitemaps': sitemaps},
                           name='sitemap'),

                       (r'^i18n/', include('django.conf.urls.i18n')),
                       (r'^autocomplete/', include('autocomplete_light.urls')),
                       (r'^admin/', include(admin.site.urls)),
                       (r'^groups/', include('geonode.groups.urls')),
                       (r'^documents/', include('geonode.documents.urls')),
                       (r'^services/', include('geonode.services.urls')),

                       # GeoServer Helper Views
                       (r'^gs/', include('geonode.geoserver.urls')),
                       # OAuth Provider
                       url(r'^o/', include('oauth2_provider.urls',
                           namespace='oauth2_provider')),

                       # Api Views
                       url(r'^api/o/v4/tokeninfo', verify_token,
                           name='tokeninfo'),
                       url(r'^api/roles', roles, name='roles'),
                       url(r'^api/adminRole', admin_role, name='adminRole'),
                       url(r'^api/users', users, name='users'),
                       url(r'', include(api.urls)),
                       )

if "geonode.contrib.dynamic" in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
                            (r'^dynamic/',
                             include('geonode.contrib.dynamic.urls')),
                            )

if "geonode.contrib.metadataxsl" in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
                            (r'^showmetadata/',
                             include('geonode.contrib.metadataxsl.urls')),
                            )

if 'geonode.geoserver' in settings.INSTALLED_APPS:
    # GeoServer Helper Views
    urlpatterns += patterns('',
                            # Upload views
                            (r'^upload/', include('geonode.upload.urls')),
                            (r'^gs/', include('geonode.geoserver.urls')),
                            )
if 'geonode_qgis_server' in settings.INSTALLED_APPS:
    # QGIS Server's urls
    urlpatterns += patterns('',
                            (r'', include('geonode_qgis_server.urls')),
                            )

if 'notification' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
                            (r'^notifications/', include('notification.urls')),
                            )

if "djmp" in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
                            (r'^djmp/', include('djmp.urls')),
                            )

# Set up proxy
urlpatterns += geonode.proxy.urls.urlpatterns

# Enable internal geoserver proxy in development mode.
# In production it must be done by Apache/Nginx, not by Django
if settings.DEBUG:
    urlpatterns += patterns(
        '', url(r'^geoserver/', 'openquakeplatform.proxy.geoserver',
                name="geoserver"),
    )

urlpatterns += geonode.proxy.urls.urlpatterns

# Server static files
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler403 = 'geonode.views.err403'

# Featured Maps Pattens
urlpatterns += patterns(
    '',
    (r'^featured/(?P<site>[A-Za-z0-9_\-]+)/$',
     'geonode.maps.views.featured_map'),
    (r'^featured/(?P<site>[A-Za-z0-9_\-]+)/info$',
     'geonode.maps.views.featured_map_info'),
    )

# openquake_platform
urlpatterns += patterns(
    '',
    (r'^taxtweb/',
     include('openquakeplatform_taxtweb.urls',
             namespace='taxtweb')),
    (r'^ipt/',
     include('openquakeplatform_ipt.urls',
             namespace='ipt')),
    (r'^building-class/',
     include('openquakeplatform_building_class.urls',
             namespace='building_class')),
    (r'^vulnerability/',
     include('openquakeplatform.vulnerability.urls',
             namespace='vulnerability')),
    (r'^exposure/',
     include('openquakeplatform.exposure.urls')),
    )
