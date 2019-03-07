# -*- coding: utf-8 -*-
import pandas
import pytz
import logging
from datetime import datetime

from django.conf import settings

from cove_iom.readers import XML


class CleanXML:
    def __init__(self, input_file):
        self.log = logging
        self.log.basicConfig(
            format='%(levelname)s: %(message)s', level=logging.DEBUG)

        self.xml_file = input_file
        try:
            self.xml = XML(self.xml_file)
        except FileNotFoundError:
            self.log.error('No such file!')
            self.xml = False

    def add_iati_activities_attr(self, version='2.02'):
        iso_date_time_now_utc = datetime.now(pytz.utc).isoformat()
        if self.xml:
            self.xml.update_head({'version': version})
            self.xml.update_head({'generated-datetime': iso_date_time_now_utc})
            return True
        else:
            return self.xml


class CleanFile:
    def __init__(self, file_location, sheet_name='IATI Only Fields'):
        self.file_location = file_location
        self.log = logging

        if self.file_location.endswith('xlsx'):
            self.work = self.clean_xlsx(pandas.read_excel(
                self.file_location, sheet_name=sheet_name, header=None))
        else:
            self.work = pandas.read_csv(
                self.file_location,
                na_filter=False,
                error_bad_lines=False
            )

    @staticmethod
    def clean_xlsx(work):
        work.drop(work.index[7:10], inplace=True)
        work.drop(work.index[0:6], inplace=True)
        work.reset_index(drop=True, inplace=True)
        work.columns = work.iloc[0]

        df = work.reindex(work.index.drop(0))
        df.drop(['IATI XML Name'], axis=1, inplace=True)
        df.dropna(how='all', inplace=True)
        return df

    def mapping(self):
        # Convert some field to string data type
        self.work['activity-date/0/@type'] = self.work[
            'activity-date/0/@type'].astype(str)
        self.work['activity-date/1/@type'] = self.work[
            'activity-date/1/@type'].astype(str)
        self.work['activity-date/2/@type'] = self.work[
            'activity-date/2/@type'].astype(str)
        self.work['activity-date/3/@type'] = self.work[
            'activity-date/3/@type'].astype(str)
        self.work['sector/1/@code'] = self.work['sector/1/@code'].astype(str)
        self.work['sector/2/@code'] = self.work['sector/2/@code'].astype(str)
        self.work['sector/2/@vocabulary'] = self.work[
            'sector/2/@vocabulary'].astype(str)
        self.work['activity-status/@code'] = self.work[
            'activity-status/@code'].astype(str)
        self.work['recipient-region/@vocabulary'] = self.work[
            'recipient-region/@vocabulary'].astype(str)
        self.work['recipient-region/@code'] = self.work[
            'recipient-region/@code'].astype(str)

        for i, row in self.work.iterrows():
            value = row['sector/0/@code']

            activity_date_type = row['activity-date/3/@type'].split('.')[0]
            activity_date_type = '' if activity_date_type == 'nan' \
                else activity_date_type
            self.work.set_value(i, 'activity-date/3/@type', activity_date_type)

            activity_status = row['activity-status/@code'].split('.')[0]
            self.work.set_value(i, 'activity-status/@code', activity_status)

            # Mapping sector code from 0 to dac code on sector 2
            dac = str(settings.PROJECT_TYPE_MAPPING.get(value, ''))
            if dac:
                self.work.set_value(i, 'sector/2/@code', dac)
                # Default of the IATI DAC 5 vocabulary is 1
                self.work.set_value(i, 'sector/2/@vocabulary', '1')

            # Forced recipient-region/@vocabulary
            recipient_region_vocabulary = \
                row['recipient-region/@vocabulary'].split('.')[0]
            recipient_region_vocabulary = '' \
                if recipient_region_vocabulary == 'nan' \
                else recipient_region_vocabulary

            self.work.set_value(
                i, 'recipient-region/@vocabulary', recipient_region_vocabulary)

            # Forced recipient-region/@code
            recipient_region_code = \
                row['recipient-region/@code'].split('.')[0]
            recipient_region_code = '' \
                if recipient_region_code == 'nan' \
                else recipient_region_code

            self.work.set_value(
                i, 'recipient-region/@code', recipient_region_code)

    def execute(self, output_file):
        for i in self.work.columns:
            # change ob ject data type
            self.work[i] = self.work[i].apply(
                lambda x: x.str.strip()
                if hasattr(x, "dtype") and x.dtype == "object" else x
            )

        try:
            # covert Yes or No to boolean type
            self.work["@humanitarian"][self.work['@humanitarian'] == "Yes"] = 1
            self.work["@humanitarian"][self.work['@humanitarian'] == "No"] = 0
        except TypeError:
            pass

        self.mapping()

        try:
            return self.work.to_csv(output_file, index=False)
        except UnicodeEncodeError:
            return self.work.to_csv(output_file, index=False, encoding='utf-8')
