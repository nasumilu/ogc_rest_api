import urllib.parse

from fastapi.testclient import TestClient

from .main import app
from .schema import LinkRelation, MediaType, ConformanceClass

client = TestClient(app)


def test_landing_page():
    """
    Test the OGC Feature API v1.0.0 requirements for the landing page.

    `API landing page requirements <https://docs.ogc.org/is/17-069r4/17-069r4.html#_api_landing_page>`_
    :return:
    """
    # 1a
    response = client.get('/')
    # 2a
    assert response.status_code == 200
    # 2b
    data = response.json()
    assert 'links' in data
    conformance = next(filter(lambda link: link['rel'] == LinkRelation.CONFORMANCE, data['links']), None)
    assert conformance is not None and urllib.parse.urlparse(conformance['href'])[2] == '/conformance'
    collections = next(filter(lambda link: link['rel'] == LinkRelation.DATA, data['links']), None)
    assert collections is not None and urllib.parse.urlparse(collections['href'])[2] == '/collections'

    # recommendations
    # 1a
    self_link = next(filter(lambda link: link['rel'] == LinkRelation.SELF, data['links']), None)
    if self_link is not None:
        assert urllib.parse.urlparse(self_link['href'])[2] == '/'

    alternates = list(filter(lambda link: link['rel'] == LinkRelation.ALTERNATE, data['links']))
    for alternate in alternates:
        assert alternate['type'] != MediaType.APPLICATION_JSON


def test_conformance():
    """
    Unit test for the conformance endpoint requirements.

    `Conformance Endpoint Requirements <https://docs.ogc.org/is/17-069r4/17-069r4.html#_declaration_of_conformance_classes>`_
    :return:
    """
    # 5a
    response = client.get('/conformance')
    # 6a
    assert response.status_code == 200
    data = response.json()
    # 6b
    assert 'conformsTo' in data
    assert next(filter(lambda c: c == ConformanceClass.CORE, data['conformsTo']), None) is not None
