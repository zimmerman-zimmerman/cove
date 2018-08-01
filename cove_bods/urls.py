from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from cove.urls import urlpatterns, handler500  # noqa: F401

import cove_bods.views
