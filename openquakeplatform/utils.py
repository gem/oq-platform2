import openquakeplatform

from django.conf import settings
from django.http import HttpResponse

SIGN_IN_REQUIRED = ('You must be signed into the OpenQuake Platform to use '
                    'this feature.')


class allowed_methods(object):
    def __init__(self, methods):
        self.methods = methods

    def __call__(self, func):
        def wrapped(request):
            if request.method not in self.methods:
                return HttpResponse(status=405)
            else:
                return func(request)
        return wrapped


def oq_is_qgis_browser(request):
    for k in request.META:
        if k.startswith('HTTP_GEM__QGIS_'):
            return True
    return False


def oq_context_processor(request):
    """
    A custom context processor which allows injection of additional
    context variables.
    """

    context = {}

    context['SITEURL'] = settings.SITEURL
    context['OQP_VERSION'] = openquakeplatform.__version__
    context['third_party_urls'] = settings.THIRD_PARTY_URLS
    # BING API key for their maps
    # context['bing_key'] = settings.BING_KEY
    # Experimental features
    # context['is_gem_experimental'] = settings.GEM_EXPERIMENTAL
    # TileStream server URL
    context['TILESTREAM_URL'] = settings.TILESTREAM_URL
    # User manual base URL
    # context['HELP_URL'] = settings.HELP_URL
    # Exposure limits
    context['EXPOSURE_MAX_EXPORT_AREA_SQ_DEG'] = \
        settings.EXPOSURE_MAX_EXPORT_AREA_SQ_DEG
    context['EXPOSURE_MAX_TOT_GRID_COUNT'] = \
        settings.EXPOSURE_MAX_TOT_GRID_COUNT
    # Google Analytics tracking code
    context['GOOGLE_UA'] = getattr(settings, 'GOOGLE_UA', False)

    if oq_is_qgis_browser(request):
        context['gem_qgis'] = True

    return context


def sign_in_required(func):
    """
    View decorator. This can be used as an alternative to
    `django.contrib.auth.decorators.login_required`, but the function is
    distinctly different.

    Instead of immediately redirecting to a login URL, simply return a 401
    ("Unauthorized") and let the client figure out what to do with it. If the
    client then wants to authenticate to allow the wrapped view to be used, it
    needs to have some intimate knowledge of the server application in order to
    do so.

    In this way, the wrapped view can be used a bit more generically by any
    client (and not just a Django application).
    """
    def wrapped(request):
        if not request.user.is_authenticated():
            return HttpResponse(content=SIGN_IN_REQUIRED,
                                content_type="text/plain",
                                status=401)
        else:
            return func(request)
    return wrapped
