import re
from collections import defaultdict, OrderedDict
from decimal import Decimal

import cove.lib.tools as tools
from cove.lib.common import common_checks_context, get_orgids_prefixes



def common_checks_fireproofbox(context, upload_dir, json_data, schema_obj):
    schema_name = schema_obj.release_pkg_schema_name
    common_checks = common_checks_context(upload_dir, json_data, schema_obj, schema_name, context)

    context.update(common_checks['context'])
    context['count'] = count_box_items(json_data)
    return context


def count_box_items(json_data):
    if not isinstance(json_data, dict):
        return 0
    return len(json_data.get("items", []))