# Prototype Project

This project is a rough prototype which provides the scaffolding for an OGC Feature API v1.0 
utilizing the FastAPI framework. 

## How it works

To configure a __Feature__ class utilized the decorator provided in the `app.collection` module and extent
the abstract `FeatureDataProvider` class.

### Example

```python

@feature_collection(collection_id='tc-track',
                    title='Tropical Cyclone Tracks',
                    description='The storm track (connecting the dots)',
                    spatial_extent=(-180, -68.5, 180, 83.01000),
                    temporal_extent=(
                            datetime.fromisoformat('1842-10-25 03:00:00.000000'),
                            datetime.fromisoformat('2023-06-16 12:00:00.000000')
                    ))
class TCTrack(FeatureDataProvider):

    def items(self) -> List[Any]:
        # todo: Model the data here
        sql = ('select id, sid, sshs, name, start_iso_time, end_iso_time, '
               'st_astext(geom) as wkt from storm_track limit 100')
        with self._engine.connect() as connection:
            results = connection.execute(text(sql))
        return [row._asdict() for row in results]

    def item(self, feature_id: str) -> str:
        # todo: possible sql injection; model data and use ORM
        sql = 'select id, sid, sshs, name, start_iso_time, end_iso_time, st_astext(geom) as wkt from storm_track where sid = \'{}\''.format(
            feature_id)
        with self._engine.connect() as connection:
            results = connection.execute(text(sql))
        return results.fetchone()._asdict()

```

The above example you can see that the `@feature_collection` decorator provides the necessary metadata
to describe the collection. Then the `items` and `item` method uses a connection to query the datatabase and 
provide the data. 

In short, the decorator is the configuration and the class is the adapter to retrieve the data. Given enough time each
of the `FeatureDataProvider` should have an ORM which would provide the necessary data conversion to/from the database.
In fact, the `FeatureDataProvider` has generic to type the modeled results.

## What need to be done

- Provide a mechanism to allow multiple datasource, rather than one global datasource
- Pagination for the /collections/{collection_id}/items endpoint
- Model the results for the `@feature_collection` decorated classes to convert the data from the database into a 
value GeoJSON response
- Configuration to define modules with `@feature_collections` so they are discovered and configured when the app starts
- Finish unit tests
- Document the code
- And much more...

### Example Output

#### Landing Page (/)

```json
{
  "title": "OGC Feature API",
  "description": "Simple one-off OGC Feature API Server",
  "links": [
    {
      "href": "http://127.0.0.1:8000/docs",
      "rel": "service-doc",
      "type": "text/html",
      "title": "The Swagger UI for this API"
    },
    {
      "href": "http://127.0.0.1:8000/redoc",
      "rel": "alternate",
      "type": "text/html",
      "title": "The ReDoc UI for this API"
    },
    {
      "href": "http://127.0.0.1:8000/openapi.json",
      "rel": "service-desc",
      "type": "application/json",
      "title": "The OpenAPI JSON definition"
    },
    {
      "href": "http://127.0.0.1:8000/conformance",
      "rel": "conformance",
      "type": "application/json"
    },
    {
      "href": "http://127.0.0.1:8000/collections",
      "rel": "data"
    },
    {
      "href": "http://127.0.0.1:8000/",
      "rel": "self",
      "type": "application/json"
    }
  ]
}
```


The Swagger UI generated by FastAPI's app, route, and model decorators (some inferred) found using the `rel="alternative"`
link.
![Swagger UI](./docs/images/swagger_ui.png)

The ReDoc UI generated by FastAPI's app, route, and model decorates (some inferred). Since the OGC responses are nearly 
like Collections+JSON HATEOAS format they provide nice discoverable linked data. 
![ReDoc UI](./docs/images/redoc_ui.png)


#### Conformance (/conformance)

> **IMPORTANT**: This isn't true or at least the current state does not conform to these standards. Once the app is 
> finished and the unit testing is completed per the OGC Feature API requirements; This will be so...

```json
{
  "conformsTo": [
    "http://www.opengis.net/spec/ogcapi-features-1/1.0/req/core",
    "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson",
    "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/html",
    "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30"
  ]
}
```

#### Collections (/collections)

> Much more testing is needed for the extent, as you see it is keyed wrong, one to many extents. That is where those 
> unit test come in handy. That bug would never get by, with proper unit testing. 

```json
{
  "links": [
    {
      "href": "http://127.0.0.1:8000/collections/tc-location",
      "rel": "collection",
      "title": ""
    },
    {
      "href": "http://127.0.0.1:8000/collections/tc-track",
      "rel": "collection",
      "title": ""
    }
  ],
  "collections": [
    {
      "id": "tc-location",
      "title": "Tropical Cyclone Locations",
      "description": "The location points for tropical cyclones",
      "extent": {
        "extent": {
          "spatial": [
            [
              -180,
              -68.5,
              180,
              83.01
            ]
          ],
          "temporal": [
            [
              "1842-10-25T03:00:00",
              "2023-06-16T12:00:00"
            ]
          ]
        }
      },
      "itemType": "feature",
      "links": [
        {
          "href": "http://127.0.0.1:8000/collections/tc-location",
          "rel": "self",
          "type": "application/json",
          "title": "Tropical Cyclone Locations"
        },
        {
          "href": "http://127.0.0.1:8000/collections/tc-location/items",
          "rel": "items",
          "type": "application/json",
          "title": "Tropical Cyclone Locations Items"
        }
      ]
    },
    {
      "id": "tc-track",
      "title": "Tropical Cyclone Tracks",
      "description": "The storm track (connecting the dots)",
      "extent": {
        "extent": {
          "spatial": [
            [
              -180,
              -68.5,
              180,
              83.01
            ]
          ],
          "temporal": [
            [
              "1842-10-25T03:00:00",
              "2023-06-16T12:00:00"
            ]
          ]
        }
      },
      "itemType": "feature",
      "links": [
        {
          "href": "http://127.0.0.1:8000/collections/tc-track",
          "rel": "self",
          "type": "application/json",
          "title": "Tropical Cyclone Tracks"
        },
        {
          "href": "http://127.0.0.1:8000/collections/tc-track/items",
          "rel": "items",
          "type": "application/json",
          "title": "Tropical Cyclone Tracks Items"
        }
      ]
    }
  ]
}
```

#### Collection Items (/collections/{collection_id}/items)

> Not valid GeoJSON still need a lot of work. Example is only a subset of 10 features with the geometry exported as
> GeoJSON string literal.

```json
[
  {
    "id": 1,
    "sid": "1842298N11080",
    "name": "NOT_NAMED",
    "iso_time": "1842-10-25T03:00:00",
    "geom": "{\"type\":\"Point\",\"coordinates\":[80.300003052,10.899999619]}"
  },
  {
    "id": 2,
    "sid": "1842298N11080",
    "name": "NOT_NAMED",
    "iso_time": "1842-10-25T06:00:00",
    "geom": "{\"type\":\"Point\",\"coordinates\":[79.830001831,10.869999886]}"
  },
  {
    "id": 3,
    "sid": "1842298N11080",
    "name": "NOT_NAMED",
    "iso_time": "1842-10-25T09:00:00",
    "geom": "{\"type\":\"Point\",\"coordinates\":[79.349998474,10.840000153]}"
  },
  {
    "id": 4,
    "sid": "1842298N11080",
    "name": "NOT_NAMED",
    "iso_time": "1842-10-25T12:00:00",
    "geom": "{\"type\":\"Point\",\"coordinates\":[78.879997253,10.819999695]}"
  },
  {
    "id": 5,
    "sid": "1842298N11080",
    "name": "NOT_NAMED",
    "iso_time": "1842-10-25T15:00:00",
    "geom": "{\"type\":\"Point\",\"coordinates\":[78.400001526,10.800000191]}"
  },
  {
    "id": 6,
    "sid": "1842298N11080",
    "name": "NOT_NAMED",
    "iso_time": "1842-10-25T18:00:00",
    "geom": "{\"type\":\"Point\",\"coordinates\":[77.919998169,10.789999962]}"
  },
  {
    "id": 7,
    "sid": "1842298N11080",
    "name": "NOT_NAMED",
    "iso_time": "1842-10-25T21:00:00",
    "geom": "{\"type\":\"Point\",\"coordinates\":[77.430000305,10.779999733]}"
  },
  {
    "id": 8,
    "sid": "1842298N11080",
    "name": "NOT_NAMED",
    "iso_time": "1842-10-26T00:00:00",
    "geom": "{\"type\":\"Point\",\"coordinates\":[76.930000305,10.789999962]}"
  },
  {
    "id": 9,
    "sid": "1842298N11080",
    "name": "NOT_NAMED",
    "iso_time": "1842-10-26T03:00:00",
    "geom": "{\"type\":\"Point\",\"coordinates\":[76.400001526,10.800000191]}"
  },
  {
    "id": 10,
    "sid": "1842298N11080",
    "name": "NOT_NAMED",
    "iso_time": "1842-10-26T06:00:00",
    "geom": "{\"type\":\"Point\",\"coordinates\":[75.839996338,10.81000042]}"
  }
]
```

#### Collection Item Endpoint (/collections/{collection_id}/items/{feature_id})

> Not valid GeoJSON the geometry is exported as a GeoJSON geometry string literal.

```json
{
  "id": 1,
  "sid": "1842298N11080",
  "name": "NOT_NAMED",
  "season": 1842,
  "basin": "NI",
  "subbasin": "BB",
  "iso_time": "1842-10-25T03:00:00",
  "nature": "NR",
  "intensity": null,
  "wind": null,
  "speed": 9,
  "direction": 266,
  "pressure": null,
  "gust": null,
  "geom": "{\"type\":\"Point\",\"coordinates\":[80.300003052,10.899999619]}"
}
```

