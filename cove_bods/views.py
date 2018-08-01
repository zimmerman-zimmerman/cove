import json
import logging
from decimal import Decimal

from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from cove.lib.converters import convert_spreadsheet, convert_json
from cove.lib.exceptions import CoveInputDataError, cove_web_input_error
from cove.views import explore_data_context

logger = logging.getLogger(__name__)


def common_errors(request):
    return render(request, 'cove_bods/common_errors.html')


def additional_checks(request):
    context = {}
    context["checks"] = [{**check.check_text, 'desc': check.__doc__} for check in TEST_CLASSES]
    return render(request, 'cove_bods/additional_checks.html', context)
