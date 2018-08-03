from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from cove.urls import urlpatterns, handler500  # noqa: F401

import cove_bods.views

urlpatterns += [
    url(r'^data/(.+)/advanced$', cove_bods.views.explore_bods, name='explore', kwargs=dict(template='cove_bods/explore_advanced.html')),
    url(r'^data/(.+)$', cove_bods.views.explore_bods, name='explore'),
    url(r'^common_errors', cove_bods.views.common_errors, name='common_errors'),
    url(r'^additional_checks', cove_bods.views.additional_checks, name='additional_checks')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)