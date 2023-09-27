from enum import StrEnum
from typing import Optional, List

from pydantic import BaseModel, HttpUrl, Field, ConfigDict, field_serializer
from starlette.datastructures import URL


class ConformanceClass(StrEnum):
    CORE = 'http://www.opengis.net/spec/ogcapi-features-1/1.0/req/core'
    OAS30 = 'http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30'
    HTML = 'http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/html'
    GEOJSON = 'http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson'
    GMLSF0 = 'http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/gmlsf0'
    GMLSF2 = 'http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/gmlsf2'


class MediaType(StrEnum):
    TEXT_HTML = 'text/html'
    PLAIN_TEXT = 'text/plain'
    APPLICATION_JSON = 'application/json'
    GEOJSON = 'application/geo+json'


class LinkRelation(StrEnum):
    """
    Description
    -------------
    Enumeration of commonly used link relations for OGC Feature API.

    Reference
    -------------
    - `RFC 8288 (Web Linking) <https://www.rfc-editor.org/rfc/rfc8288.html>`_
    - `Internet Assigned Numbers Authority (IANA) Link Relation Types <https://www.iana.org/assignments/link-relations/link-relations.xml>`_
    - `OGC API - Features - Part 1: Core corrigendum <https://docs.ogc.org/is/17-069r4/17-069r4.html#_link_relations>`_
    """
    ALTERNATE = 'alternate'
    COLLECTION = 'collection'
    DESCRIBED_BY = 'describe_by'
    ITEM = 'item'
    NEXT = 'next'
    LICENSE = 'license'
    PREV = 'prev'
    SELF = 'self'
    SERVICE_DESC = 'service-desc'
    SERVICE_DOC = 'service-doc'
    ITEMS = 'items'
    CONFORMANCE = 'conformance'
    DATA = 'data'


class Link(BaseModel):
    href: URL | str
    rel: str | LinkRelation = Field(description='The link relation.')
    type: Optional[str | MediaType] = Field(default=None, description='The link media type.')
    hreflang: Optional[str] = Field(default=None, description='The language of the reference resource.')
    title: Optional[str] = Field(default=None, description='')
    length: Optional[int] = Field(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer('href')
    def serialize_url(self, value: URL, _info) -> str:
        return str(value)


class LandingPage(BaseModel):
    title: str
    description: str
    links: List[Link]


class Collection(BaseModel):
    id: str
    title: Optional[str] = None
