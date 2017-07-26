from os import path
from datetime import datetime
import requests
from lxml import objectify
from rdflib import Graph, URIRef, Namespace, Literal, XSD, OWL, RDF, RDFS


def get_directory_xml():
    r = requests.get('https://www.directory.gov.au/sites/default/files/export.xml')
    this_dir = path.dirname(path.realpath(__file__))
    export_file_name = 'export_' + datetime.now().strftime('%Y-%m-%d') + '.xml'
    open(path.join(this_dir, 'data', export_file_name), 'w').write(r.content.decode('utf-8'))


'''
<item>
    <content_id>80951</content_id>
    <unique_record_id>O-000887</unique_record_id>
    <title>Geoscience Australia</title>
    <type>organisation</type>
    <portfolio>78911</portfolio>
    <abn>80 091 799 039</abn>
    <annual_report_prep_tabled>Yes</annual_report_prep_tabled>
    <auditor>ANAO</auditor>
    <asl>600</asl>
    <classification>A. Principal</classification>
    <creation_date>1949-07-02 00:00:00</creation_date>
    <current_budget_total_expenditure>206121</current_budget_total_expenditure>
    <current_budget_total_appropriations>155790</current_budget_total_appropriations>
    <description>Geoscience Australia is Australia&#039;s national geoscience agency and exists to apply geoscience to Australia&#039;s most important challenges. Geoscience Australia provides geoscientific advice and information to the Australian Government to support it to deliver its priorities. Geoscientific information is also provided to industry and other stakeholders where it supports achievement of Australian Government objectives.</description>
    <email>sales@ga.gov.au</email>
    <established_by_under>PGPA Rule (Schedule 1)</established_by_under><fax_number>(02) 6249 9999</fax_number>
    <gfs_function>Mining and Mineral Resources (other than fuels) Manufacturing and Construction</gfs_function>
    <gfs_sector_classification>GGS</gfs_sector_classification><materiality>Small</materiality>
    <media_releases>http://www.ga.gov.au/about-us/news-media.html</media_releases>
    <phone_number>(02) 6249 9111</phone_number>
    <type_of_body>A. Non Corporate Commonwealth Entity</type_of_body>
    <updated>20/06/2017 - 4:15pm</updated>
    <website>http://www.ga.gov.au</website>
    <address>
        <country>AU</country>
        <administrative_area>ACT</administrative_area>
        <locality>Symonston</locality><postal_code>2609</postal_code>
        <thoroughfare>Cnr Jerrabomberra Ave and Hindmarsh Drive</thoroughfare>
    </address>
    <postal_address>GPO Box 378, Canberra ACT 2601</postal_address>
    <ps_act_body>Yes - Operate with some Independence</ps_act_body>
</item>
'''


SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')


ITEMS_CLASS_URIS = {
    'board':                        ['http://reference.data.gov.au/def/ont/directory#Board'],
    'commonwealth_of_parliament':   ['http://reference.data.gov.au/def/ont/directory#Commonwealth_of_parliament'],
    'courts':                       ['http://reference.data.gov.au/def/ont/directory#Court'],
    'directory_role':               ['http://reference.data.gov.au/def/ont/directory#Directory_role'],
    'directory_sub_structure':      ['http://reference.data.gov.au/def/ont/directory#Directory_sub_structure'],
    'enquiry_line':                 ['http://reference.data.gov.au/def/ont/directory#Enquiry_line'],
    'governor_general':             ['http://reference.data.gov.au/def/ont/directory#Governor_general'],
    'non_board':                    ['http://reference.data.gov.au/def/ont/directory#Non_board'],
    'organisation':                 ['http://www.w3.org/ns/org#Organization'],
    'person':                       ['http://xmlns.com/foaf/0.1/Person'],
    'portfolio':                    ['http://reference.data.gov.au/def/ont/directory#Portfolio'],
    'portfolio_role':               ['http://reference.data.gov.au/def/ont/directory#Portfolio_role'],
    'role':                         ['http://www.w3.org/ns/org#Role'],
    'single_executive_role':        ['http://reference.data.gov.au/def/ont/directory#Single_executive_role']
}


ITEMS_NAMED_INDIVIDUALS_URI_BASES = {
    'board':                        'http://governance.data.gov.au/dataset/directory/board/',
    'commonwealth_of_parliament':   'http://governance.data.gov.au/dataset/directory/commonwealth_of_parliament/',
    'courts':                       'http://governance.data.gov.au/dataset/directory/courts/',
    'directory_role':               'http://governance.data.gov.au/dataset/directory/directory_role/',
    'directory_sub_structure':      'http://governance.data.gov.au/dataset/directory/directory_sub_structure/',
    'enquiry_line':                 'http://governance.data.gov.au/dataset/directory/enquiry_line/',
    'governor_general':             'http://governance.data.gov.au/dataset/directory/governor_general/',
    'non_board':                    'http://governance.data.gov.au/dataset/directory/non_board/',
    'organisation':                 'http://governance.data.gov.au/dataset/directory/organisation/',
    'person':                       'http://governance.data.gov.au/dataset/directory/person/',
    'portfolio':                    'http://governance.data.gov.au/dataset/directory/portfolio/',
    'portfolio_role':               'http://governance.data.gov.au/dataset/directory/portfolio_role/',
    'role':                         'http://governance.data.gov.au/dataset/directory/role/',
    'single_executive_role':        'http://governance.data.gov.au/dataset/directory/single_executive_role/',
}


def make_type_count(export_file_name):
    """
    Makes something like this from an export.xml:

    types = {
        'board': 826,
        'commonwealth_of_parliament': 14,
        'courts': 3,
        'directory_role': 4478,
        'directory_sub_structure': 3513,
        'enquiry_line': 145,
        'governor_general': 4,
        'non_board': 372,
        'organisation': 180,
        'person': 9043,
        'portfolio': 18,
        'portfolio_role': 255,
        'role': 4331,
        'single_executive_role': 48
    }

    :param export_file_name:
    :return:
    """
    this_dir = path.dirname(path.realpath(__file__))
    types = {}
    items = objectify.parse(path.join(this_dir, 'data', export_file_name)).getroot().getchildren()
    for item in items:
        t = str(item.type)
        if t not in types.keys():
            types[t] = 0
        else:
            types[t] += 1

    return types


def parse_board(g, item):
    named_individual_uri = URIRef(ITEMS_NAMED_INDIVIDUALS_URI_BASES[item.type] + item.unique_record_id)#Literal(item.unique_record_id, datatype=XSD.string)
    for c in ITEMS_CLASS_URIS[item.type]:
        g.add((named_individual_uri, RDF.type, URIRef(c)))
    g.add((named_individual_uri, SKOS.prefLabel, Literal(item.title, datatype=XSD.string)))


def parse_commonwealth_of_parliament(g, item):
    pass


def parse_courts(g, item):
    pass


def parse_directory_role(g, item):
    pass


def parse_directory_sub_structure(g, item):
    pass


def parse_enquiry_line(g, item):
    pass


def parse_governor_general(g, item):
    pass


def parse_non_board(g, item):
    pass


def parse_organisation(g, item):
    pass


def parse_portfolio(g, item):
    pass


def parse_portfolio_role(g, item):
    pass


def parse_role(g, item):
    pass


def parse_single_executive_role(g, item):
    pass


def parse_item(g, item):
    # parse each item based on its type
    if item.type == 'board':
        parse_board(g, item)
    elif item.type == 'commonwealth_of_parliament':
        parse_commonwealth_of_parliament(g, item)
    elif item.type == 'courts':
        parse_courts(g, item)
    elif item.type == 'directory_role':
        parse_directory_role(g, item)
    elif item.type == 'directory_sub_structure':
        parse_directory_sub_structure(g, item)
    elif item.type == 'enquiry_line':
        parse_enquiry_line(g, item)
    elif item.type == 'governor_general':
        parse_governor_general(g, item)
    elif item.type == 'non_board':
        parse_non_board(g, item)
    elif item.type == 'organisation':
        parse_organisation(g, item)
    elif item.type == 'portfolio':
        parse_board(g, item)
    elif item.type == 'portfolio_role':
        parse_portfolio_role(g, item)
    elif item.type == 'role':
        parse_role(g, item)
    elif item.type == 'single_executive_role':
        parse_single_executive_role(g, item)


def parse_items(g, export_file_name):
    this_dir = path.dirname(path.realpath(__file__))

    items = objectify.parse(path.join(this_dir, 'data', export_file_name)).getroot().getchildren()
    for item in items:
        # EXCLUSION FOR TESTING ONLY
        if item.type == 'board':
            parse_item(g, item)


if __name__ == '__main__':
    # get the XML from the web
    #get_directory_xml()

    g = Graph()
    g.bind('skos', SKOS)
    parse_items(g, 'export_2017-07-26.xml')
    #print(make_type_count('export_2017-07-26.xml'))
    print(g.serialize(format='turtle').decode('utf-8'))