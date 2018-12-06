from django.conf.urls import url

from cove.urls import urlpatterns, handler500  # noqa: F401
from django.conf.urls.static import static
from django.conf import settings

import cove_iom.views

urlpatterns = [
    url(r'^$', cove_iom.views.data_input_iati, name='index'),
    url(r'^data/(.+)$', cove_iom.views.explore_iati, name='explore'),
    url(r'^api_test', cove_iom.views.api_test, name='api_test'),
    url(r'^upload/$', cove_iom.views.upload, name='upload'),
] + urlpatterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
