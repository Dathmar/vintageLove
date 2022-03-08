from django.shortcuts import render
from django.conf import settings
from django.urls import URLPattern, URLResolver

urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [''])


def list_urls(lis, acc=None):
    if acc is None:
        acc = []
    if not lis:
        return
    l = lis[0]
    if isinstance(l, URLPattern):
        yield acc + [str(l.pattern)]
    elif isinstance(l, URLResolver):
        yield from list_urls(l.url_patterns, acc + [str(l.pattern)])
    yield from list_urls(lis[1:], acc)


# Create your views here.
def url_list(request):
    urls = []
    for p in list_urls(urlconf.urlpatterns):
        urls.append(p)
    return render(request, 'meta/url-list.html', {'urls': urls})