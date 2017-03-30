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

#ipt
import os
import re
import json
import zipfile
import tempfile
import shutil
from email.Utils import formatdate

from django.shortcuts import render
from django.http import (HttpResponse,
                         HttpResponseBadRequest,
                         )
from django.conf import settings
from django import forms

from openquakeplatform.settings import WEBUIURL
import requests
from requests import HTTPError
from build_rupture_plane import get_rupture_surface_round
# end ipt

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
try:
    import json
except ImportError:
    from django.utils import simplejson as json
from django.db.models import Q
from django.template.response import TemplateResponse

from geonode import get_version
from geonode.base.templatetags.base_tags import facets
from geonode.groups.models import GroupProfile


class AjaxLoginForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    username = forms.CharField()


def ajax_login(request):
    if request.method != 'POST':
        return HttpResponse(
            content="ajax login requires HTTP POST",
            status=405,
            content_type="text/plain"
        )
    form = AjaxLoginForm(data=request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is None or not user.is_active:
            return HttpResponse(
                content="bad credentials or disabled user",
                status=400,
                content_type="text/plain"
)
        else:
            login(request, user)
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            return HttpResponse(
                content="successful login",
                status=200,
                content_type="text/plain"
            )
    else:
        return HttpResponse(
            "The form you submitted doesn't look like a username/password
combo.",
            content_type="text/plain",
            status=400)


def ajax_lookup(request):
    if request.method != 'POST':
        return HttpResponse(
            content='ajax user lookup requires HTTP POST',
            status=405,
            content_type='text/plain'
        )
    elif 'query' not in request.POST:
        return HttpResponse(
            content='use a field named "query" to specify a prefix to filter
usernames',
            content_type='text/plain')
    keyword = request.POST['query']
    users = get_user_model().objects.filter(Q(username__istartswith=keyword) |
                                            Q(first_name__icontains=keyword) |
                                            Q(organization__icontains=keyword)).exclude(username='AnonymousUser')
    groups = GroupProfile.objects.filter(Q(title__istartswith=keyword) |
                                         Q(description__icontains=keyword))
    json_dict = {
        'users': [({'username': u.username}) for u in users],
        'count': users.count(),
    }

    json_dict['groups'] = [({'name': g.slug, 'title': g.title}) for g in
groups]
    return HttpResponse(
        content=json.dumps(json_dict),
        content_type='text/plain'
    )

def err403(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(
            reverse('account_login') +
            '?next=' +
            request.get_full_path())
    else:
        return TemplateResponse(request, '401.html', {}, status=401).render()


def ident_json(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(
            reverse('account_login') +
            '?next=' +
            request.get_full_path())

    json_data = {}
    json_data['siteurl'] = settings.SITEURL
    json_data['name'] =
settings.PYCSW['CONFIGURATION']['metadata:main']['identification_title']

    json_data['poc'] = {
        'name':
settings.PYCSW['CONFIGURATION']['metadata:main']['contact_name'],
        'email':
settings.PYCSW['CONFIGURATION']['metadata:main']['contact_email'],
        'twitter': 'https://twitter.com/%s' % settings.TWITTER_SITE
    }

    json_data['version'] = get_version()

    json_data['services'] = {
        'csw': settings.CATALOGUE['default']['URL'],
        'ows': settings.OGC_SERVER['default']['LOCATION']
    }

    json_data['counts'] = facets({'request': request, 'facet_type': 'home'})

    return HttpResponse(content=json.dumps(json_data),
mimetype='application/json')

def h_keywords(request):
    from geonode.base.models import HierarchicalKeyword as hk
    keywords = json.dumps(hk.dump_bulk_tree())
    return HttpResponse(content=keywords)

ALLOWED_DIR = ['rupture_file', 'list_of_sites', 'exposure_model',
               'site_model', 'site_conditions', 'imt',
               'fragility_model', 'fragility_cons',
               'vulnerability_model', 'gsim_logic_tree_file',
               'source_model_logic_tree_file', 'source_model_file']


def _get_error_line(exc_msg):
    # check if the exc_msg contains a line number indication
    search_match = re.search(r'line \d+', exc_msg)
    if search_match:
        error_line = int(search_match.group(0).split()[1])
    else:
        error_line = None
    return error_line


def _make_response(error_msg, error_line, valid):
    response_data = dict(error_msg=error_msg,
                         error_line=error_line,
                         valid=valid)
    return HttpResponse(
        content=json.dumps(response_data), content_type=JSON)

JSON = 'application/json'


def _do_validate_nrml(xml_text):
    data = dict(xml_text=xml_text)
    ret = requests.post('%sv1/valid/' % WEBUIURL, data)

    if ret.status_code != 200:
        raise HTTPError({'message': "URL '%s' unreachable", 'lineno': -1})

    ret_dict = json.loads(ret.content)

    if not ret_dict['valid']:
        raise ValueError({ 'message': ret_dict.get('error_msg', ''),
                           'lineno': ret_dict.get('error_line', -1)})

def validate_nrml(request):
    """
    Leverage oq-risklib to check if a given XML text is a valid NRML
    :param request:
        a `django.http.HttpRequest` object containing the mandatory
        parameter 'xml_text': the text of the XML to be validated as NRML
    :returns: a JSON object, containing:
        * 'valid': a boolean indicating if the provided text is a valid NRML
        * 'error_msg': the error message, if any error was found
                       (None otherwise)
        * 'error_line': line of the given XML where the error was found
                        (None if no error was found or if it was not a
                        validation error)
    """
    xml_text = request.POST.get('xml_text')
    if not xml_text:
        return HttpResponseBadRequest(
            'Please provide the "xml_text" parameter')
    try:
        xml_text = xml_text.replace('\r\n', '\n').replace('\r', '\n')
        _do_validate_nrml(xml_text)
    except (HTTPError, ValueError) as e:
        exc = e.args[0]
        return _make_response(error_msg=exc['message'],
                              error_line=exc['lineno'],
                              valid=False)
    except Exception as exc:
        # get the exception message
        exc_msg = exc.args[0]
        if isinstance(exc_msg, bytes):
            exc_msg = exc_msg.decode('utf-8')   # make it a unicode object
        elif isinstance(exc_msg, unicode):
            pass
        else:
            # if it is another kind of object, it is not obvious a priori how
            # to extract the error line from it
# but we can attempt anyway to extract it
            error_line = _get_error_line(unicode(exc_msg))
            return _make_response(
                error_msg=unicode(exc_msg), error_line=error_line,
                valid=False)
        error_msg = exc_msg
        error_line = _get_error_line(exc_msg)
        return _make_response(
            error_msg=error_msg, error_line=error_line, valid=False)
    else:
        return _make_response(error_msg=None, error_line=None, valid=True)


def sendback_nrml(request):
    """
    Leverage oq-risklib to check if a given XML text is a valid NRML. If it is,
    save it as a XML file.
    :param request:
        a `django.http.HttpRequest` object containing the mandatory
        parameter 'xml_text': the text of the XML to be validated as NRML
        and the optional parameter 'func_type': the function type (known types
        are ['exposure', 'fragility', 'vulnerability', 'site'])
    :returns: an XML file, containing the given NRML text
    """
    xml_text = request.POST.get('xml_text')
    func_type = request.POST.get('func_type')
    if not xml_text:
        return HttpResponseBadRequest(
            'Please provide the "xml_text" parameter')
    known_func_types = [
        'exposure', 'fragility', 'vulnerability', 'site', 'earthquake_rupture']
    try:
        xml_text = xml_text.replace('\r\n', '\n').replace('\r', '\n')
        _do_validate_nrml(xml_text)
    except:
        return HttpResponseBadRequest(
            'Invalid NRML')
    else:
        if func_type in known_func_types:
            filename = func_type + '_model.xml'
        else:
            filename = 'unknown_model.xml'
        resp = HttpResponse(content=xml_text,
                            content_type='application/xml')
resp['Content-Disposition'] = (
            'attachment; filename="' + filename + '"')
        return resp


def sendback_er_rupture_surface(request):
    mag = request.POST.get('mag')
    hypo_lat = request.POST.get('hypo_lat')
    hypo_lon = request.POST.get('hypo_lon')
    hypo_depth = request.POST.get('hypo_depth')
    strike = request.POST.get('strike')
    dip = request.POST.get('dip')
    rake = request.POST.get('rake')

    if (mag is None or hypo_lat is None or hypo_lon is None or
        hypo_depth is None or strike is None or dip is None or rake is None):
        ret = {'ret': 1, 'ret_s': 'incomplete arguments'}
    else:
        try:
            mag = float(mag)
            hypo_lat = float(hypo_lat)
            hypo_lon = float(hypo_lon)
            hypo_depth = float(hypo_depth)
            strike = float(strike)
            dip = float(dip)
            rake = float(rake)

            ret = get_rupture_surface_round(mag, {"lon": hypo_lon,
                                                  "lat": hypo_lat,
                                                  "depth": hypo_depth},
                                            strike, dip, rake)
            ret['ret'] = 0
            ret['ret_s'] = 'success'
        except Exception as exc:
            ret = {'ret': 2, 'ret_s': 'exception raised: %s' % exc}

    return HttpResponse(json.dumps(ret), content_type="application/json")


class FileUpload(forms.Form):
    file_upload = forms.FileField(allow_empty_file=True)


class FilePathFieldByUser(forms.ChoiceField):
def __init__(self, userid, subdir, namespace, match=None,
                 recursive=False, allow_files=True,
                 allow_folders=False, required=True, widget=None, label=None,
                 initial=None, help_text=None, *args, **kwargs):
        self.match, self.recursive = match, recursive
        self.subdir = subdir
        self.userid = str(userid)
        self.namespace = namespace
        self.allow_files, self.allow_folders = allow_files, allow_folders
        super(FilePathFieldByUser, self).__init__(
            choices=(), required=required, widget=widget, label=label,
            initial=initial, help_text=help_text, *args, **kwargs)

        if self.required:
            self.choices = []
        else:
            self.choices = [("", "---------")]

        if self.match is not None:
            self.match_re = re.compile(self.match)

        normalized_path = get_full_path(self.userid, self.namespace,
                                        self.subdir)
        user_allowed_path = get_full_path(self.userid, self.namespace)
        if not normalized_path.startswith(user_allowed_path):
            raise LookupError('Unauthorized path: "%s"' % normalized_path)

        if recursive:
            for root, dirs, files in sorted(os.walk(normalized_path)):
                if self.allow_files:
                    for f in files:
                        if self.match is None or self.match_re.search(f):
                            filename = os.path.basename(f)
                            subdir_and_name = os.path.join(subdir, filename)
                            self.choices.append((subdir_and_name, filename))
                if self.allow_folders:
                    for f in dirs:
                        if f == '__pycache__':
                            continue
                        if self.match is None or self.match_re.search(f):
                            f = os.path.join(root, f)
                            filename = os.path.basename(f)
                            subdir_and_name = os.path.join(subdir, filename)
                            self.choices.append((subdir_and_name, filename))
else:
            try:
                for f in sorted(os.listdir(normalized_path)):
                    if f == '__pycache__':
                        continue
                    full_file = os.path.normpath(
                        os.path.join(normalized_path, f))
                    if (((self.allow_files and os.path.isfile(full_file)) or
                            (self.allow_folders and os.path.isdir(full_file)))
                            and
                            (self.match is None or self.match_re.search(f))):
                        self.choices.append((f, f))
            except OSError:
                pass

        self.widget.choices = self.choices


def filehtml_create(suffix, userid, namespace, dirnam=None,
                    match=".*\.xml", is_multiple=False):
    if dirnam is None:
        dirnam = suffix
    if (dirnam not in ALLOWED_DIR):
        raise KeyError("dirnam (%s) not in allowed list" % dirnam)

    normalized_path = get_full_path(userid, namespace, dirnam)
    user_allowed_path = get_full_path(userid, namespace)
    if not normalized_path.startswith(user_allowed_path):
        raise LookupError('Unauthorized path: "%s"' % normalized_path)
    if not os.path.isdir(normalized_path):
        os.makedirs(normalized_path)

    class FileHtml(forms.Form):
        file_html = FilePathFieldByUser(
            userid=userid,
            subdir=dirnam,
            namespace=namespace,
            match=match,
            recursive=True,
            required=is_multiple,
            widget=(forms.fields.SelectMultiple if is_multiple else None))
    fh = FileHtml()

    return fh

def _get_available_gsims():

    ret = requests.get('%sv1/available_gsims' % WEBUIURL)

    if ret.status_code != 200:
        raise HTTPError({'message': "URL '%s' unreachable" % WEBUIURL})

    ret_list = json.loads(ret.content)

    return [gsim.encode('utf8') for gsim in ret_list]

def view(request, **kwargs):
    if getattr(settings, 'STANDALONE', False):
        userid = ''
    else:
        userid = str(request.user.id)
    namespace = request.resolver_match.namespace
    gmpe = _get_available_gsims()

    rupture_file_html = filehtml_create(
        'rupture_file', userid, namespace)
    rupture_file_upload = FileUpload()

    list_of_sites_html = filehtml_create(
        'list_of_sites', userid, namespace, match=".*\.csv")
    list_of_sites_upload = FileUpload()

    exposure_model_html = filehtml_create(
        'exposure_model', userid, namespace)
    exposure_model_upload = FileUpload()

    site_model_html = filehtml_create(
        'site_model', userid, namespace)
    site_model_upload = FileUpload()

    fm_structural_html = filehtml_create(
        'fm_structural', userid, namespace, dirnam='fragility_model')
    fm_structural_upload = FileUpload()
    fm_nonstructural_html = filehtml_create(
        'fm_nonstructural', userid, namespace, dirnam='fragility_model')
    fm_nonstructural_upload = FileUpload()
    fm_contents_html = filehtml_create(
        'fm_contents', userid, namespace, dirnam='fragility_model')
fm_contents_upload = FileUpload()
    fm_businter_html = filehtml_create(
        'fm_businter', userid, namespace, dirnam='fragility_model')
    fm_businter_upload = FileUpload()

    fm_structural_cons_html = filehtml_create(
        'fragility_cons', userid, namespace)
    fm_structural_cons_upload = FileUpload()
    fm_nonstructural_cons_html = filehtml_create(
        'fragility_cons', userid, namespace)
    fm_nonstructural_cons_upload = FileUpload()
    fm_contents_cons_html = filehtml_create(
        'fragility_cons', userid, namespace)
    fm_contents_cons_upload = FileUpload()
    fm_businter_cons_html = filehtml_create(
        'fragility_cons', userid, namespace)
    fm_businter_cons_upload = FileUpload()

    vm_structural_html = filehtml_create(
        'vm_structural', userid, namespace, dirnam='vulnerability_model')
    vm_structural_upload = FileUpload()
    vm_nonstructural_html = filehtml_create(
        'vm_nonstructural', userid, namespace, dirnam='vulnerability_model')
    vm_nonstructural_upload = FileUpload()
    vm_contents_html = filehtml_create(
        'vm_contents', userid, namespace, dirnam='vulnerability_model')
    vm_contents_upload = FileUpload()
    vm_businter_html = filehtml_create(
        'vm_businter', userid, namespace, dirnam='vulnerability_model')
    vm_businter_upload = FileUpload()
    vm_occupants_html = filehtml_create(
        'vm_occupants', userid, namespace, dirnam='vulnerability_model')
    vm_occupants_upload = FileUpload()

    site_conditions_html = filehtml_create(
        'site_conditions', userid, namespace)
    site_conditions_upload = FileUpload()

    imt_html = filehtml_create('imt', userid, namespace)
    imt_upload = FileUpload()

    gsim_logic_tree_file_html = filehtml_create(
        'gsim_logic_tree_file', userid, namespace)
gsim_logic_tree_file_upload = FileUpload()

    source_model_logic_tree_file_html = filehtml_create(
        'source_model_logic_tree_file', userid, namespace)
    source_model_logic_tree_file_upload = FileUpload()

    source_model_file_html = filehtml_create(
        'source_model_file', userid, namespace, is_multiple=True)
    source_model_file_upload = FileUpload()

    return render(
        request,
        "ipt/ipt.html",
        dict(
            g_gmpe=gmpe,
            rupture_file_html=rupture_file_html,
            rupture_file_upload=rupture_file_upload,
            list_of_sites_html=list_of_sites_html,
            list_of_sites_upload=list_of_sites_upload,
            exposure_model_html=exposure_model_html,
            exposure_model_upload=exposure_model_upload,
            site_model_html=site_model_html,
            site_model_upload=site_model_upload,

            fm_structural_html=fm_structural_html,
            fm_structural_upload=fm_structural_upload,
            fm_nonstructural_html=fm_nonstructural_html,
            fm_nonstructural_upload=fm_nonstructural_upload,
            fm_contents_html=fm_contents_html,
            fm_contents_upload=fm_contents_upload,
            fm_businter_html=fm_businter_html,
            fm_businter_upload=fm_businter_upload,

            fm_structural_cons_html=fm_structural_cons_html,
            fm_structural_cons_upload=fm_structural_cons_upload,
            fm_nonstructural_cons_html=fm_nonstructural_cons_html,
            fm_nonstructural_cons_upload=fm_nonstructural_cons_upload,
            fm_contents_cons_html=fm_contents_cons_html,
            fm_contents_cons_upload=fm_contents_cons_upload,
            fm_businter_cons_html=fm_businter_cons_html,
            fm_businter_cons_upload=fm_businter_cons_upload,

            vm_structural_html=vm_structural_html,
vm_structural_upload=vm_structural_upload,
            vm_nonstructural_html=vm_nonstructural_html,
            vm_nonstructural_upload=vm_nonstructural_upload,
            vm_contents_html=vm_contents_html,
            vm_contents_upload=vm_contents_upload,
            vm_businter_html=vm_businter_html,
            vm_businter_upload=vm_businter_upload,
            vm_occupants_html=vm_occupants_html,
            vm_occupants_upload=vm_occupants_upload,

            site_conditions_html=site_conditions_html,
            site_conditions_upload=site_conditions_upload,
            imt_html=imt_html,
            imt_upload=imt_upload,
            gsim_logic_tree_file_html=gsim_logic_tree_file_html,
            gsim_logic_tree_file_upload=gsim_logic_tree_file_upload,

            source_model_logic_tree_file_html=source_model_logic_tree_file_html,
            source_model_logic_tree_file_upload=source_model_logic_tree_file_upload,

            source_model_file_html=source_model_file_html,
            source_model_file_upload=source_model_file_upload
        ))


def upload(request, **kwargs):
    ret = {}

    if 'target' not in kwargs:
        ret['ret'] = 3
        ret['ret_msg'] = 'Malformed request.'
        return HttpResponse(json.dumps(ret), content_type="application/json")

    target = kwargs['target']
    if target not in ALLOWED_DIR:
        ret['ret'] = 4
        ret['ret_msg'] = 'Unknown target "' + target + '".'
        return HttpResponse(json.dumps(ret), content_type="application/json")

    if request.is_ajax():
        if request.method == 'POST':
            class FileUpload(forms.Form):
                file_upload = forms.FileField(allow_empty_file=True)
            form = FileUpload(request.POST, request.FILES)
if target in ['list_of_sites']:
                exten = "csv"
            else:
                exten = "xml"

            if form.is_valid():
                if request.FILES['file_upload'].name.endswith('.' + exten):
                    if getattr(settings, 'STANDALONE', False):
                        userid = ''
                    else:
                        userid = str(request.user.id)
                    namespace = request.resolver_match.namespace
                    user_dir = get_full_path(userid, namespace)
                    bname = os.path.join(user_dir, target)
                    # check if the directory exists (or create it)
                    if not os.path.exists(bname):
                        os.makedirs(bname)
                    full_path = os.path.join(
                        bname, request.FILES['file_upload'].name)
                    overwrite_existing_files = request.POST.get(
                        'overwrite_existing_files', True)
                    if not overwrite_existing_files:
                        modified_path = full_path
                        n = 0
                        while os.path.isfile(modified_path):
                            n += 1
                            f_name, f_ext = os.path.splitext(full_path)
                            modified_path = '%s_%s%s' % (f_name, n, f_ext)
                        full_path = modified_path
                    if not os.path.normpath(full_path).startswith(user_dir):
                        ret['ret'] = 5
                        ret['ret_msg'] = 'Not authorized to write the file.'
                        return HttpResponse(json.dumps(ret),
                                            content_type="application/json")
                    f = file(full_path, "w")
                    f.write(request.FILES['file_upload'].read())
                    f.close()

                    suffix = target
                    match = ".*\." + exten

                    class FileHtml(forms.Form):
                        file_html = FilePathFieldByUser(
                            userid=userid,
subdir=suffix,
                            namespace=namespace,
                            match=match,
                            recursive=True)

                    fileslist = FileHtml()

                    ret['ret'] = 0
                    ret['items'] = fileslist.fields['file_html'].choices
                    orig_file_name = str(request.FILES['file_upload'])
                    new_file_name = os.path.basename(full_path)
                    ret['selected'] = os.path.join(target, new_file_name)
                    changed_msg = ''
                    if orig_file_name != new_file_name:
                        changed_msg = ' (Renamed into %s)' % new_file_name
                    ret['ret_msg'] = ('File %s uploaded successfully.%s' %
                                      (orig_file_name, changed_msg))
                else:
                    ret['ret'] = 1
                    ret['ret_msg'] = ('File uploaded isn\'t an %s file.' %
                                      exten.upper())

                # Redirect to the document list after POST
                return HttpResponse(json.dumps(ret),
                                    content_type="application/json")

    ret['ret'] = 2
    ret['ret_msg'] = 'Please provide the file.'

    return HttpResponse(json.dumps(ret), content_type="application/json")


def get_full_path(userid, namespace, subdir_and_filename=""):
    return os.path.normpath(os.path.join(settings.FILE_PATH_FIELD_DIRECTORY,
                            userid,
                            namespace,
                            subdir_and_filename))


def exposure_model_prep_sect(data, z, is_regcons, userid, namespace):
    jobini = "\n[Exposure model]\n"
    #           ################

    jobini += "exposure_file = %s\n" % os.path.basename(data['exposure_model'])
    z.write(get_full_path(userid, namespace, data['exposure_model']),
os.path.basename(data['exposure_model']))
    if is_regcons:
        if data['exposure_model_regcons_choice'] is True:
            is_first = True
            jobini += "region_constraint = "
            for el in data['exposure_model_regcons_coords_data']:
                if is_first:
                    is_first = False
                else:
                    jobini += ", "
                jobini += "%s %s" % (el[0], el[1])
            jobini += "\n"

        if data['asset_hazard_distance_choice'] is True:
            jobini += ("asset_hazard_distance = %s\n" %
                       data['asset_hazard_distance'])

    return jobini


def vulnerability_model_prep_sect(data, z, userid, namespace):
    jobini = "\n[Vulnerability model]\n"
    #            #####################
    descr = {'structural': 'structural', 'nonstructural': 'nonstructural',
             'contents': 'contents', 'businter': 'business_interruption',
             'occupants': 'occupants'}
    for losslist in ['structural', 'nonstructural', 'contents', 'businter',
                     'occupants']:
        if data['vm_loss_%s_choice' % losslist] is True:
            jobini += "%s_vulnerability_file = %s\n" % (
                descr[losslist], os.path.basename(data['vm_loss_' + losslist]))
            z.write(get_full_path(userid, namespace,
                                  data['vm_loss_%s' % losslist]),
                    os.path.basename(data['vm_loss_%s' % losslist]))

    jobini += "insured_losses = %s\n" % (
        "True" if data['insured_losses'] else "False")

    if data['asset_correlation_choice']:
        jobini += "asset_correlation = %s" % data['asset_correlation']

    return jobini


def site_conditions_prep_sect(data, z, userid, namespace):
    jobini = "\n[Site conditions]\n"
    #           #################

    if data['site_conditions_choice'] == 'from-file':
        jobini += ("site_model_file = %s\n" %
                   os.path.basename(data['site_model_file']))
        z.write(get_full_path(userid, namespace, data['site_model_file']),
                os.path.basename(data['site_model_file']))
    elif data['site_conditions_choice'] == 'uniform-param':
        jobini += "reference_vs30_value = %s\n" % data['reference_vs30_value']
        jobini += "reference_vs30_type = %s\n" % data['reference_vs30_type']
        jobini += ("reference_depth_to_2pt5km_per_sec = %s\n" %
                   data['reference_depth_to_2pt5km_per_sec'])
        jobini += ("reference_depth_to_1pt0km_per_sec = %s\n" %
                   data['reference_depth_to_1pt0km_per_sec'])
    return jobini


def scenario_prepare(request, **kwargs):
    ret = {}

    if request.POST.get('data', '') == '':
        ret['ret'] = 1
        ret['msg'] = 'Malformed request.'
        return HttpResponse(json.dumps(ret), content_type="application/json")

    if getattr(settings, 'STANDALONE', False):
        userid = ''
    else:
        userid = str(request.user.id)

    namespace = request.resolver_match.namespace

    data = json.loads(request.POST.get('data'))

    (fd, fname) = tempfile.mkstemp(
        suffix='.zip', prefix='ipt_', dir=tempfile.gettempdir())
    fzip = os.fdopen(fd, 'w')
    z = zipfile.ZipFile(fzip, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)

    jobini = "# Generated automatically with IPT at %s\n" % formatdate()
    jobini += "[general]\n"
    jobini += "description = %s\n" % data['description']

    if data['risk'] == 'damage':
        jobini += "calculation_mode = scenario_damage\n"
    elif data['risk'] == 'losses':
        jobini += "calculation_mode = scenario_risk\n"
    elif data['hazard'] == 'hazard':
        jobini += "calculation_mode = scenario\n"
    else:
        ret['ret'] = 2
        ret['msg'] = 'Neither hazard nor risk selected.'
        return HttpResponse(json.dumps(ret), content_type="application/json")

    jobini += "random_seed = 113\n"

    if data['hazard'] == 'hazard':
        jobini += "\n[Rupture information]\n"
        #            #####################

        jobini += ("rupture_model_file = %s\n" %
                   os.path.basename(data['rupture_model_file']))
        z.write(get_full_path(userid, namespace, data['rupture_model_file']),
                os.path.basename(data['rupture_model_file']))

        jobini += "rupture_mesh_spacing = %s\n" % data['rupture_mesh_spacing']

    if data['hazard'] == 'hazard':
        jobini += "\n[Hazard sites]\n"
        #            ##############

        if data['hazard_sites_choice'] == 'region-grid':
            jobini += "region_grid_spacing = %s\n" % data['grid_spacing']
            is_first = True
            jobini += "region = "
            for el in data['reggrid_coords_data']:
                if is_first:
                    is_first = False
                else:
                    jobini += ", "
                jobini += "%s %s" % (el[0], el[1])
jobini += "\n"
        elif data['hazard_sites_choice'] == 'list-of-sites':
            jobini += "sites = %s\n" % os.path.basename(data['list_of_sites'])
            z.write(get_full_path(userid, namespace, data['list_of_sites']),
                    os.path.basename(data['list_of_sites']))
        elif data['hazard_sites_choice'] == 'exposure-model':
            pass
        elif data['hazard_sites_choice'] == 'site-cond-model':
            if data['site_conditions_choice'] != 'from-file':
                ret['ret'] = 4
                ret['msg'] = ('Input hazard sites choices mismatch method to '
                              'specify site conditions.')
                return HttpResponse(json.dumps(ret),
                                    content_type="application/json")
        else:
            ret['ret'] = 4
            ret['msg'] = 'Unknown hazard_sites_choice.'
            return HttpResponse(json.dumps(ret),
                                content_type="application/json")

    if ((data['hazard'] == 'hazard' and
         data['hazard_sites_choice'] == 'exposure-model')
            or data['risk'] is not None):
        jobini += exposure_model_prep_sect(
            data, z, (data['risk'] is not None), userid, namespace)

    if data['risk'] == 'damage':
        jobini += "\n[Fragility model]\n"
        #            #################
        descr = {'structural': 'structural', 'nonstructural': 'nonstructural',
                 'contents': 'contents', 'businter': 'business_interruption'}
        with_cons = data['fm_loss_show_cons_choice']
        for losslist in ['structural', 'nonstructural',
                         'contents', 'businter']:
            if data['fm_loss_%s_choice' % losslist] is True:
                jobini += "%s_fragility_file = %s\n" % (
                    descr[losslist],
                    os.path.basename(data['fm_loss_' + losslist]))
                z.write(get_full_path(userid, namespace,
                                      data['fm_loss_' + losslist]),
                        os.path.basename(data['fm_loss_' + losslist]))
                if with_cons is True:
                    jobini += "%s_consequence_file = %s\n" % (
descr[losslist],
                        os.path.basename(data['fm_loss_%s_cons' % losslist]))
                    z.write(get_full_path(userid, namespace,
                                          data['fm_loss_%s_cons' % losslist]),
                            os.path.basename(
                                data['fm_loss_%s_cons' % losslist]))
    elif data['risk'] == 'losses':
        jobini += vulnerability_model_prep_sect(data, z, userid, namespace)

    if data['hazard'] == 'hazard':
        jobini += site_conditions_prep_sect(data, z, userid, namespace)

    if data['hazard'] == 'hazard':
        jobini += "\n[Calculation parameters]\n"
        #            ########################

        if data['gmpe_choice'] == 'specify-gmpe':
            jobini += "gsim = %s\n" % data['gsim'][0]
        elif data['gmpe_choice'] == 'from-file':
            jobini += ("gsim_logic_tree_file = %s\n" %
                       os.path.basename(data['gsim_logic_tree_file']))
            z.write(get_full_path(userid, namespace,
                                  data['gsim_logic_tree_file']),
                    os.path.basename(data['gsim_logic_tree_file']))

        if data['risk'] is None:
            jobini += "intensity_measure_types = "
            is_first = True
            for imt in data['intensity_measure_types']:
                if is_first:
                    is_first = False
                else:
                    jobini += ", "
                jobini += imt
            if data['custom_imt'] != '':
                if not is_first:
                    jobini += ", "
                jobini += data['custom_imt']
            jobini += "\n"

        jobini += ("ground_motion_correlation_model = %s\n" %
                   data['ground_motion_correlation_model'])
        if data['ground_motion_correlation_model'] == 'JB2009':
            jobini += ("ground_motion_correlation_params = "
"{\"vs30_clustering\": False}\n")

        jobini += "truncation_level = %s\n" % data['truncation_level']
        jobini += "maximum_distance = %s\n" % data['maximum_distance']
        jobini += ("number_of_ground_motion_fields = %s\n" %
                   data['number_of_ground_motion_fields'])

    print jobini

    z.writestr('job.ini', jobini)
    z.close()

    ret['ret'] = 0
    ret['msg'] = 'Success, download it.'
    ret['zipname'] = os.path.basename(fname)
    return HttpResponse(json.dumps(ret), content_type="application/json")


def event_based_prepare(request, **kwargs):
    ret = {}

    if request.POST.get('data', '') == '':
        ret['ret'] = 1
        ret['msg'] = 'Malformed request.'
        return HttpResponse(json.dumps(ret), content_type="application/json")

    if getattr(settings, 'STANDALONE', False):
        userid = ''
    else:
        userid = str(request.user.id)

    namespace = request.resolver_match.namespace

    data = json.loads(request.POST.get('data'))

    (fd, fname) = tempfile.mkstemp(
        suffix='.zip', prefix='ipt_', dir=tempfile.gettempdir())
    fzip = os.fdopen(fd, 'w')
    z = zipfile.ZipFile(fzip, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)

    jobini = "# Generated automatically with IPT at %s\n" % formatdate()
    jobini += "[general]\n"
    jobini += "description = %s\n" % data['description']

    jobini += "calculation_mode = event_based_risk\n"

    jobini += "random_seed = 113\n"

    # Exposure model
    jobini += exposure_model_prep_sect(data, z, True, userid, namespace)

    # Vulnerability model
    jobini += vulnerability_model_prep_sect(data, z, userid, namespace)

    # Hazard model
    jobini += "source_model_logic_tree_file = %s\n" % os.path.basename(
        data['source_model_logic_tree_file'])
    z.write(get_full_path(userid, namespace,
                          data['source_model_logic_tree_file']),
            os.path.basename(data['source_model_logic_tree_file']))

    for source_model_name in data['source_model_file']:
        z.write(get_full_path(userid, namespace, source_model_name),
                os.path.basename(source_model_name))

    jobini += "gsim_logic_tree_file = %s\n" % os.path.basename(
        data['gsim_logic_tree_file'])
    z.write(get_full_path(userid, namespace, data['gsim_logic_tree_file']),
            os.path.basename(data['gsim_logic_tree_file']))

    jobini += "\n[Hazard model]\n"
    #            ##############
    jobini += "width_of_mfd_bin = %s\n" % data['width_of_mfd_bin']

    if data['rupture_mesh_spacing_choice'] is True:
        jobini += "rupture_mesh_spacing = %s\n" % data['rupture_mesh_spacing']
    if data['area_source_discretization_choice'] is True:
        jobini += ("area_source_discretization = %s\n" %
                   data['area_source_discretization'])

    # Site conditions
    jobini += site_conditions_prep_sect(data, z, userid, namespace)

    jobini += "\n[Hazard calculation]\n"
    #            ####################
    jobini += "truncation_level = %s\n" % data['truncation_level']
jobini += "maximum_distance = %s\n" % data['maximum_distance']
    jobini += "investigation_time = %s\n" % data['investigation_time']
    jobini += ("ses_per_logic_tree_path = %s\n" %
               data['ses_per_logic_tree_path'])
    jobini += ("number_of_logic_tree_samples = %s\n" %
               data['number_of_logic_tree_samples'])
    jobini += ("ground_motion_correlation_model = %s\n" %
               data['ground_motion_correlation_model'])
    if data['ground_motion_correlation_model'] == 'JB2009':
        jobini += ("ground_motion_correlation_params = "
                   "{\"vs30_clustering\": True}")

    jobini += "\n[Risk calculation]\n"
    #            ##################
    jobini += ("risk_investigation_time = %s\n" %
               data['risk_investigation_time'])
    if data['loss_curve_resolution_choice'] is True:
        jobini += ("loss_curve_resolution = %s\n" %
                   data['loss_curve_resolution'])
    if data['loss_ratios_choice'] is True:
        jobini += "loss_ratios = { "
        descr = {'structural': 'structural', 'nonstructural': 'nonstructural',
                 'contents': 'contents', 'businter': 'business_interruption',
                 'occupants': 'occupants'}
        is_first = True
        for losslist in ['structural', 'nonstructural', 'contents', 'businter',
                         'occupants']:
            if data['vm_loss_%s_choice' % losslist] is True:
                jobini += "%s\"%s\": [ %s ]" % (
                    ("" if is_first else ", "),
                    descr[losslist], data['loss_ratios_' + losslist])
                is_first = False
        jobini += "}\n"

    jobini += "\n[Hazard outputs]\n"
    #            ################
    jobini += "ground_motion_fields = %s\n" % data['ground_motion_fields']
    jobini += ("hazard_curves_from_gmfs = %s\n" %
               data['hazard_curves_from_gmfs'])
    if data['hazard_curves_from_gmfs']:
        jobini += "mean_hazard_curves = %s\n" % data['mean_hazard_curves']
        if data['quantile_hazard_curves_choice']:
            jobini += ("quantile_hazard_curves = %s\n" %
data['quantile_hazard_curves'])
    jobini += "hazard_maps = %s\n" % data['hazard_maps']
    if data['hazard_maps']:
        jobini += "poes = %s\n" % data['poes']
    jobini += "uniform_hazard_spectra = %s\n" % data['uniform_hazard_spectra']

    jobini += "\n[Risk outputs]\n"
    #            ##############
    jobini += "avg_losses = %s\n" % data['avg_losses']
    jobini += "asset_loss_table = %s\n" % data['asset_loss_table']
    if data['quantile_loss_curves_choice']:
        jobini += "quantile_loss_curves = %s\n" % data['quantile_loss_curves']
    if data['conditional_loss_poes_choice']:
        jobini += ("conditional_loss_poes = %s\n" %
                   data['conditional_loss_poes'])

    print jobini

    z.writestr('job.ini', jobini)
    z.close()

    ret['ret'] = 0
    ret['msg'] = 'Success, download it.'
    ret['zipname'] = os.path.basename(fname)
    return HttpResponse(json.dumps(ret), content_type="application/json")


def download(request):
    if request.method == 'POST':
        zipname = request.POST.get('zipname', '')
        dest_name = request.POST.get('dest_name', 'Unknown')
        if zipname == '':
            return HttpResponseBadRequest('No zipname provided.')
        absfile = os.path.join(tempfile.gettempdir(), zipname)
        if not os.path.isfile(absfile):
            return HttpResponseBadRequest('Zipfile not found.')
        with open(absfile, 'rb') as content_file:
            content = content_file.read()

        resp = HttpResponse(content=content,
                            content_type='application/zip')
        resp['Content-Disposition'] = (
            'attachment; filename="' + dest_name + '.zip"')
        return resp


def clean_all(request):
    if request.method == 'POST':
        if getattr(settings, 'STANDALONE', False):
            userid = ''
        else:
            userid = str(request.user.id)
        namespace = request.resolver_match.namespace
        user_allowed_path = get_full_path(userid, namespace)
        for ipt_dir in ALLOWED_DIR:
            normalized_path = get_full_path(userid, namespace, ipt_dir)
            if not normalized_path.startswith(user_allowed_path):
                raise LookupError('Unauthorized path: "%s"' % normalized_path)
            if not os.path.isdir(normalized_path):
                continue
            shutil.rmtree(normalized_path)
            os.makedirs(normalized_path)

        ret = {}
        ret['ret'] = 0
        ret['msg'] = 'Success, reload it.'
return HttpResponse(json.dumps(ret), content_type="application/json")

