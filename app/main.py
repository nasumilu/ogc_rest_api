from typing import Dict, List, Annotated

from fastapi import FastAPI, Request, Depends

from app.collection import FeatureClassRegistry, feature_registry
from app.schema import LandingPage, Link, LinkRelation, MediaType, ConformanceClass


app = FastAPI(
    title='OGC Feature API',
    description='Simple one-off OGC Feature API Server',
    version='1.0.0',
    license_info={'name': 'Apache 2.0', 'url': 'https://www.apache.org/licenses/LICENSE-2.0.txt'},
    contact={'name': 'Michael Lucas', 'email': 'nasumilu@gmail.com'}
)


@app.get('/', operation_id='landing_page', name='landingPage', description='',
         response_model=LandingPage, response_model_exclude_none=True, status_code=200)
async def landing_page(request: Request) -> LandingPage:
    """
    This is a simple one-off OGC Feature API so nothing to exciting here. Typically, a more dynamic approach would
    be expected so this server could discover and configure feature collections.
    """
    root_url = str(request.url)[:-1]
    return LandingPage(
        title=app.title,
        description=app.description,
        links=[
            Link(href=root_url + app.docs_url, rel=LinkRelation.SERVICE_DOC,
                 type=MediaType.TEXT_HTML, title='The Swagger UI for this API'),
            Link(href=root_url + app.redoc_url, rel=LinkRelation.ALTERNATE,
                 type=MediaType.TEXT_HTML, title='The ReDoc UI for this API'),
            Link(href=root_url + app.openapi_url, rel=LinkRelation.SERVICE_DESC,
                 type=MediaType.APPLICATION_JSON, title='The OpenAPI JSON definition'),
            Link(href=request.url_for('conformance'), rel=LinkRelation.CONFORMANCE,
                 type=MediaType.APPLICATION_JSON),
            Link(href=request.url_for('collections'), rel=LinkRelation.DATA),
            Link(href=request.url_for('landingPage'), rel=LinkRelation.SELF, type=MediaType.APPLICATION_JSON)
        ]
    )


@app.get('/conformance', operation_id='conformance', name='conformance',
         description='The conformance classes provided by this API')
async def conformance() -> Dict[str, List[str]]:
    """
    The conformance endpoint required by the OGC Feature API v1.0.0

    - `OGC Feature API - Conformance <https://docs.ogc.org/is/17-069r4/17-069r4.html#_conformance>`_
    """
    return {
        'conformsTo': [
            ConformanceClass.CORE,
            ConformanceClass.GEOJSON,
            ConformanceClass.HTML,
            ConformanceClass.OAS30
        ]
    }


@app.get('/collections', operation_id='collections', name='collections',
         description='List of feature collections provide by this API',
         response_model_exclude_none=True)
async def collections(request: Request,
                      registry: Annotated[FeatureClassRegistry, Depends(feature_registry)]):
    return registry.as_dict(request)


@app.get('/collections/{collection_id}', operation_id='collection', name='collection',
         description='')
async def collection(collection_id: str,
                     registry: Annotated[FeatureClassRegistry, Depends(feature_registry)],
                     request: Request):
    return registry.find(collection_id).as_dict(request)


@app.get('/collections/{collection_id}/items', operation_id='collection_items', name='collection_items',
         description='')
async def collection_items(collection_id: str,
                           registry: Annotated[FeatureClassRegistry, Depends(feature_registry)],
                           request: Request):
    return registry.instance(collection_id).items()


@app.get('/collections/{collection_id}/items/{feature_id}')
async def collection_feature(collection_id: str,
                             feature_id: str,
                             registry: Annotated[FeatureClassRegistry, Depends(feature_registry)]):

    return registry.instance(collection_id).item(feature_id)

