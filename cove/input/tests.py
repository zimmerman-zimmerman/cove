import pytest
import os
import cove.input.views as v
from cove.input.models import SuppliedData
from django.conf import settings


def fake_cove_middleware(request):
    by_namespace = settings.COVE_CONFIG_BY_NAMESPACE
    request.cove_config = {key: by_namespace[key]['default'] for key in by_namespace}
    request.current_app = 'test'
    return request


@pytest.mark.django_db
def test_input(rf):
    resp = v.input(fake_cove_middleware(rf.get('/')))
    assert resp.status_code == 200


@pytest.mark.django_db
def test_input_post(rf, httpserver):
    source_filename = 'tenders_releases_2_releases.json'
    with open(os.path.join('cove', 'fixtures', source_filename), 'rb') as fp:
        httpserver.serve_content(fp.read())
    source_url = httpserver.url + '/' + source_filename
    resp = v.input(fake_cove_middleware(rf.post('/', {
        'source_url': source_url
    })))
    assert resp.status_code == 302
    assert SuppliedData.objects.count() == 1
    data = SuppliedData.objects.first()
    assert resp.url.endswith(str(data.pk))
