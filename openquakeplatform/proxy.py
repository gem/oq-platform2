import httplib2
from django.conf import settings
from django.http import HttpResponse

# from geonode.utils import ogc_server_settings
from geonode.geoserver.helpers import ogc_server_settings


def geoserver(request):
    """
    Simple proxy to access geoserver and avoid Same-domain Access
    Control Policy restrictions
    """
    return _make_request(request, request.get_full_path())


def _make_request(request, url):
    url = "".join([
        ogc_server_settings.LOCATION,
        url[len("/geoserver/"):]])

    headers = {}
    if settings.SESSION_COOKIE_NAME in request.COOKIES:
        headers["Cookie"] = request.META["HTTP_COOKIE"]

    if request.method in ("POST", "PUT") and "CONTENT_TYPE" in request.META:
        headers["Content-Type"] = request.META["CONTENT_TYPE"]

    headers["Host"] = request.META["HTTP_HOST"]

    http = httplib2.Http()
    http.add_credentials(*(ogc_server_settings.credentials))
    response, content = http.request(
        url, request.method,
        body=request.body or None,
        headers=headers)

    return HttpResponse(
        content=content,
        status=response.status,
        content_type=response.get("content-type", "text/plain"))


def fake_proxy(request):
    url = request.GET['url']
    url = url[url.index("/"):]
    return _make_request(request, url)
