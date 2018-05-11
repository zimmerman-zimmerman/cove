'''
Sorts an IATI XML file according to the schema. This is most useful for 2.0x
where that ordering is required.

Copyright (c) 2013-2014 Ben Webb
Copyright (c) 2016 Open Data Services Co-operative Limited

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''
from collections import OrderedDict
import defusedxml.lxml as ET
import sys

# Namespaces necessary for opening schema files
namespaces = {
    'xsd': 'http://www.w3.org/2001/XMLSchema'
}


class IATISchemaWalker(object):
    '''
    Class for converting an IATI XML schema to documentation in the
    reStructuredText format.

    Based on the Schema2Doc class in https://github.com/IATI/IATI-Standard-SSOT/blob/version-2.02/gen.py
    '''
    def __init__(self, schema):
        '''
        schema -- the filename of the schema to use, e.g.
                  'iati-activities-schema.xsd'
        '''
        self.tree = ET.parse('cove_iati/iati_schemas/2.03/' + schema)
        self.tree2 = ET.parse('cove_iati/iati_schemas/2.03//iati-common.xsd')

    def get_schema_element(self, tag_name, name_attribute):
        '''
        Return the specified element from the schema.

        tag_name -- the name of the tag in the schema, e.g. 'complexType'
        name_attribute -- the value of the 'name' attribute in the schema, ie.
                          the name of the element/type etc. being described,
                          e.g. iati-activities
        '''
        schema_element = self.tree.find('xsd:{0}[@name="{1}"]'.format(tag_name, name_attribute), namespaces=namespaces)
        if schema_element is None:
            schema_element = self.tree2.find('xsd:{0}[@name="{1}"]'.format(tag_name, name_attribute), namespaces=namespaces)
        return schema_element

    def element_loop(self, element):
        '''
        Return information about the children of the supplied element.
        '''
        a = element.attrib
        type_elements = []
        if 'type' in a:
            complexType = self.get_schema_element('complexType', a['type'])
            if complexType is not None:
                type_elements = (complexType.findall('xsd:choice/xsd:element', namespaces=namespaces) +
                    complexType.findall('xsd:sequence/xsd:element', namespaces=namespaces))

        children = (element.findall('xsd:complexType/xsd:choice/xsd:element', namespaces=namespaces) +
                    element.findall('xsd:complexType/xsd:sequence/xsd:element', namespaces=namespaces) +
                    element.findall("xsd:complexType/xsd:all/xsd:element", namespaces=namespaces) +
                    type_elements)
        for child in children:
            a = child.attrib
            if 'name' in a:
                yield a['name'], child, None, a.get('minOccurs'), a.get('maxOccurs')
            else:
                yield a['ref'], None, child, a.get('minOccurs'), a.get('maxOccurs')

    def create_schema_dict(self, parent_name, parent_element=None):
        '''
        Created a nested OrderedDict representing the sturucture (and order!) of
        element in the IATI schema.
        '''
        if parent_element is None:
            parent_element = self.get_schema_element('element', parent_name)

        return OrderedDict([(name, self.create_schema_dict(name, element))
                           for name, element, _, _, _ in self.element_loop(parent_element)])

    def attribute_loop(self, element):
        """
        Returns a list containing a tuple for each attribute the given element
        can have.
        The format of the tuple is (name, is_required)
        """
        #if element.find("xsd:complexType[@mixed='true']", namespaces=namespaces) is not None:
        #    print_column_info('text', indent)
            
        a = element.attrib
        type_attributes = []
        type_attributeGroups = []
        if 'type' in a:
            complexType = self.get_schema_element('complexType', a['type'])
            if complexType is not None:
                type_attributes = (
                    complexType.findall('xsd:attribute', namespaces=namespaces) +
                    complexType.findall('xsd:simpleContent/xsd:extension/xsd:attribute', namespaces=namespaces)
                    )
                type_attributeGroups = (
                    complexType.findall('xsd:attributeGroup', namespaces=namespaces) +
                    complexType.findall('xsd:simpleContent/xsd:extension/xsd:attributeGroup', namespaces=namespaces)
                    )

        group_attributes = []
        for attributeGroup in (
                element.findall('xsd:complexType/xsd:attributeGroup', namespaces=namespaces) +
                element.findall('xsd:complexType/xsd:simpleContent/xsd:extension/xsd:attributeGroup', namespaces=namespaces) +
                type_attributeGroups
                ):
            group_attributes += self.get_schema_element('attributeGroup', attributeGroup.attrib['ref']).findall('xsd:attribute', namespaces=namespaces)

        for attribute in (
                element.findall('xsd:complexType/xsd:attribute', namespaces=namespaces) +
                element.findall('xsd:complexType/xsd:simpleContent/xsd:extension/xsd:attribute', namespaces=namespaces) +
                type_attributes + group_attributes
                ):
            doc = attribute.find(".//xsd:documentation", namespaces=namespaces)
            if 'ref' in attribute.attrib:
                referenced_attribute = self.get_schema_element('attribute', attribute.get('ref'))
                if referenced_attribute is not None:
                    attribute = referenced_attribute
                if doc is None:
                    # Only fetch the documentation of the referenced definition
                    # if we don't already have documentation.
                    doc = attribute.find(".//xsd:documentation", namespaces=namespaces)
            yield attribute.get('name') or attribute.get('ref'), attribute.get('use') == 'required'

    def has_simple_content(self, element):
        a = element.attrib
        simple_content = False
        if 'type' in a:
            complexType = self.get_schema_element('complexType', a['type'])
            if complexType is not None:
                simple_content = bool(complexType.findall('xsd:simpleContent', namespaces=namespaces))
        return simple_content or bool(element.findall('xsd:complexType/xsd:simpleContent', namespaces=namespaces))

    def generate_paths(self, parent_name, parent_element=None, parent_path=''):
        if parent_element is None:
            parent_element = self.get_schema_element('element', parent_name)

        for name, required, in self.attribute_loop(parent_element):
            yield parent_path + '@' + name

        for name, element, _, minOccurs, maxOccurs in self.element_loop(parent_element):
            if element is None:
                element = self.get_schema_element('element', name)
            path = parent_path + name
            if maxOccurs == 'unbounded' or int(maxOccurs) > 1:
                path += '/0'
            if self.has_simple_content(element):
                yield path
            path += '/'
            yield from list(self.generate_paths(name, element, path))


def sort_iati_element(element, schema_subdict):
    '''
    Sort the given elements children according to the order of schema_subdict.
    '''
    children = list(element)
    for child in children:
        element.remove(child)
    keys = list(schema_subdict.keys())

    def index_key(x):
        if x.tag in keys:
            return keys.index(x.tag)
        else:
            return len(keys) + 1

    for child in sorted(children, key=index_key):
        element.append(child)
        sort_iati_element(child, schema_subdict.get(child.tag, {}))


def sort_iati_xml_file(input_file, output_file):
    '''
    Sort an IATI XML file according to the schema.
    '''
    schema_dict = IATISchemaWalker('iati-activities-schema.xsd').create_schema_dict('iati-activity')
    tree = ET.parse(input_file)
    root = tree.getroot()

    for element in root:
        sort_iati_element(element, schema_dict)

    with open(output_file, 'wb') as fp:
        tree.write(fp, encoding='utf-8')


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'generate_template':
    for path in IATISchemaWalker('iati-activities-schema.xsd').generate_paths('iati-activity'):
        print(path)
