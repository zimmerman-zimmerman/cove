import os

import pytest
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile

from cove.input.models import SuppliedData
