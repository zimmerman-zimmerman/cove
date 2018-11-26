# -*- coding: utf-8 -*-

import csv as csv_lib
import json as json_lib
import logging
import xml.etree.ElementTree as ET


class CSV:
    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        with open(self.file_path, mode='rU') as infile:
            return [
                [rows[i] for i in range(len(rows))]
                for rows in csv_lib.reader(infile)
            ]

    def write(self, list_to_write, force_unicode=True):
        with open(self.file_path, 'r') as outfile:
            def convert_to_unicode():
                unicode_table = []
                for column in list_to_write:
                    row = []
                    try:
                        [row.append(cell) for cell in column]
                    except UnicodeDecodeError:
                        pass
                    unicode_table.append(row)
                    del row
                return unicode_table

            writer = csv_lib.writer(
                outfile, quoting=csv_lib.QUOTE_NONE, escapechar='\\')
            list_to_write = convert_to_unicode() \
                if force_unicode else list_to_write
            return [
                writer.writerow([s.encode("utf-8")
                                 for s in row]) for row in list_to_write
            ]


class JSON:
    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        with open(self.file_path) as json_data:
            return json_lib.load(json_data)


class XML:
    def __init__(self, file_path):
        self.log = logging
        try:
            self.xml_file = ET.parse(file_path)
        except ET.ParseError:
            self.log.error('No such file!')
            raise FileNotFoundError
        self.file_path = file_path

    def __save__(self):
        return self.xml_file.write(self.file_path)

    def update_head(self, attributes=False, text=False):
        element = self.xml_file.getroot()

        if text:
            element.text = text

        if type(attributes) is dict:
            for key, value in attributes.items():
                element.attrib[key] = value

        self.__save__()
