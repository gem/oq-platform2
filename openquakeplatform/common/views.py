#!/usr/bin/env python
from django.shortcuts import render_to_response
from django.template import RequestContext
from importlib import import_module
import openquakeplatform.version as version
from openquakeplatform.settings import (
        INSTALLED_APPS, GEM_ISC_MAP_UUID, GEM_GHEC_MAP_UUID,
        GEM_ACTFAU_MAP_UUID, GEM_STRRAT_MAP_UUID)
from django.views.generic import TemplateView
from geonode.maps.models import Map


def versions(request, **kwargs):
    page_title = 'Versions'

    apps_list = []
    for app_name in INSTALLED_APPS:
        if not app_name.startswith('openquakeplatform'):
            continue

        app = import_module(app_name)
        header_info = getattr(app, 'header_info', None)
        vers = getattr(app, '__version__', None)

        if vers is None:
            continue

        suff = version.git_suffix(app.__file__)
        if header_info:
            name = header_info['title']
        else:
            name = app_name

        apps_list.append({'name': name, 'vers': vers + suff})

    return render_to_response(
        "common/versions.html",
        dict(page_title=page_title,
             user=request.user,
             apps_list=apps_list,
             body_class='bodyclass'),
        context_instance=RequestContext(request))


class ExploreView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(ExploreView, self).get_context_data(**kwargs)

        try:
            isc_map = Map.objects.filter(
                uuid=GEM_ISC_MAP_UUID)
            context['ISC_MAP_ID'] = isc_map[0].pk
        except:
            context['ISC_MAP_ID'] = 23

        try:
            ghec_map = Map.objects.filter(
                uuid=GEM_GHEC_MAP_UUID)
            context['GHEC_MAP_ID'] = ghec_map[0].pk
        except:
            context['GHEC_MAP_ID'] = 24

        try:
            actfau_map = Map.objects.filter(
                uuid=GEM_ACTFAU_MAP_UUID)
            context['ACTFAU_MAP_ID'] = actfau_map[0].pk
        except:
            context['ACTFAU_MAP_ID'] = 24

        try:
            strrat_map = Map.objects.filter(
                uuid=GEM_STRRAT_MAP_UUID)
            context['STRRAT_MAP_ID'] = strrat_map[0].pk
        except:
            context['STRRAT_MAP_ID'] = 24
        return context
