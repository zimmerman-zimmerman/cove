import logging
import json
import tempfile
import os
import requests
from shutil import copyfile

from django.shortcuts import render
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.conf import settings

from cove.lib.converters import convert_spreadsheet, convert_json
from cove.lib.exceptions import cove_web_input_error
from cove.input.models import SuppliedData
from cove.input.views import data_input
from cove.views import explore_data_context
from .lib.iati import common_checks_context_iati, get_file_type
from .lib.api import iati_json_output
from .lib.schema import SchemaIATI

from cove_iom.utils import CleanFile, CleanXML


logger = logging.getLogger(__name__)


class UploadForm(forms.ModelForm):
    class Meta:
        model = SuppliedData
        fields = ['original_file']
        labels = {
            'original_file': _('Upload a file (.csv, .xlsx, .xml)')
        }


class UrlForm(forms.ModelForm):
    class Meta:
        model = SuppliedData
        fields = ['source_url']
        labels = {
            'source_url': _('Supply a URL')
        }


class TextForm(forms.Form):
    paste = forms.CharField(label=_('Paste (XML only)'), widget=forms.Textarea)


class UploadApi(forms.Form):
    name = forms.CharField(max_length=200)
    file = forms.FileField()
    openag = forms.BooleanField(required=False)
    orgids = forms.BooleanField(required=False)


iati_form_classes = {
    'upload_form': UploadForm,
    'url_form': UrlForm,
    'text_form': TextForm,
}


def data_input_iati(request):
    return data_input(
        request, form_classes=iati_form_classes, text_file_name='text.xml')


@cove_web_input_error
def explore_iati(request, pk):
    context, db_data, error = explore_data_context(request, pk, get_file_type)
    if error:
        return error

    file_type = context['file_type']
    if file_type != 'xml':

        if file_type == 'csv':
            # the process clean up of the IOM CSV data data format
            try:
                CleanFile(
                    file_location=db_data.original_file.file.name).execute(
                    output_file=db_data.original_file.file.name)
            except KeyError:
                pass

        schema_iati = SchemaIATI()
        context.update(convert_spreadsheet(
            db_data.upload_dir(),
            db_data.upload_url(),
            db_data.original_file.file.name,
            file_type, xml=True, xml_schemas=[
                schema_iati.activity_schema,
                schema_iati.organisation_schema,
                schema_iati.common_schema,
            ]))
        data_file = context['converted_path']

        if file_type == 'csv':
            # this process is specific for the IOM activity file
            # in the CSV  format
            # add attribute version & generated-datetime
            CleanXML(input_file=data_file).add_iati_activities_attr()

    else:
        data_file = db_data.original_file.file.name
        context.update(
            convert_json(db_data.upload_dir(),
                         db_data.upload_url(),
                         db_data.original_file.file.name,
                         request=request,
                         flatten=request.POST.get('flatten'),
                         xml=True))

    context = common_checks_context_iati(
        context, db_data.upload_dir(), data_file, file_type)
    context['first_render'] = not db_data.rendered

    if not db_data.rendered:
        db_data.rendered = True

    return render(request, 'cove_iom/explore.html', context)


@require_POST
@csrf_exempt
def api_test(request):
    form = UploadApi(request.POST, request.FILES)
    if form.is_valid():
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = os.path.join(tmpdirname, form.cleaned_data['name'])
            with open(file_path, 'wb+') as destination:
                for chunk in request.FILES['file'].chunks():
                    destination.write(chunk)
            result = iati_json_output(tmpdirname,
                                      file_path, form.cleaned_data['openag'],
                                      form.cleaned_data['orgids'])
            return HttpResponse(json.dumps(result),
                                content_type='application/json')
    else:
        return HttpResponseBadRequest(json.dumps(form.errors),
                                      content_type='application/json')


@require_POST
@csrf_exempt
def upload(request):
    """
    To upload file using is needed fields:
    - original_file
    - type_data

    type_data should be:
    - activity
    - organisation

    The requirement, we should make two folder manually
    with the name 'activity' & 'organisation' in the media folder
    """
    form_classes = iati_form_classes

    request_data = None
    if request.POST:
        request_data = request.POST

    if request_data:
        form_name = 'upload_form'
        form = form_classes[form_name](request_data, request.FILES)

        if form.is_valid():
            data = form.save(commit=False)
            data.current_app = request.current_app
            data.form_name = form_name
            data.save()

            # The process to make the IATI XML file
            host_url = '{protocol}://{host}'.format(
                protocol='https' if request.is_secure() else 'http',
                host=request.get_host())
            path = data.get_absolute_url()
            url = '{host_url}{path}'.format(host_url=host_url, path=path)

            response = requests.get(url)

            # Save the result xml file to specific folder
            # related to the type of file
            if response.status_code == 200:
                type_data = request.POST.get(
                    'type_data', 'activity')

                root = settings.MEDIA_ROOT
                src = '{root}{path}/unflattened.xml'.format(
                    root=root, path=path.replace('/data', ''))
                dst = '{root}/{type_data}/iom-{type_data}.xml'.format(
                    root=root, type_data=type_data)
                copyfile(src, dst)

                return JsonResponse(
                    status=response.status_code,
                    data={'url': '{host_url}/media/{type_data}/iom-{type_data}.xml'.format(  # NOQA: E501
                        host_url=host_url, type_data=type_data)})
            else:
                return JsonResponse(status=response.status_code, data={
                    'message': 'Access to media with status {}'.format(
                        url
                    )
                })
        else:
            return JsonResponse(status=400, data={'message': form.errors})

    return JsonResponse(status=400, data={'message': 'Bad Request'})
