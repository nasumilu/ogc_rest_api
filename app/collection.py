from abc import abstractmethod, ABC
from datetime import datetime
from typing import List, TypeVar, Type, Generic, Dict, Any, Tuple

from sqlalchemy import Engine, text

from app.datasource import engine
from app.schema import Link, LinkRelation, MediaType
from fastapi import Request

T = TypeVar('T')


class FeatureDataProvider(ABC, Generic[T]):

    def __init__(self, engine: Engine):
        self._engine = engine

    @abstractmethod
    def items(self) -> List[T]:
        pass

    @abstractmethod
    def item(self, feature_id: str) -> T:
        pass


SpatialExtent = Tuple[float, float, float, float]
TemporalExtent = Tuple[datetime | None, datetime | None]


class FeatureClass(Generic[T]):

    def __init__(self,
                 collection_id: str,
                 title: str,
                 description: str,
                 provider_cls: Type[FeatureDataProvider[T]],
                 spatial_extent: SpatialExtent | List[SpatialExtent] | None = None,
                 temporal_extent: TemporalExtent | List[TemporalExtent] | None = None):
        self._collection_id: str = collection_id
        self._title: str = title
        self._description: str = description
        self._provider_cls: Type[FeatureDataProvider[T]] = provider_cls
        self._spatial_extent = [spatial_extent] if isinstance(spatial_extent, tuple) else spatial_extent
        self._temporal_extent = [temporal_extent] if isinstance(temporal_extent, tuple) else temporal_extent

        # lazy loaded
        self._instance: FeatureDataProvider[T] | None = None
        self._links: List[Link] | None = None
        self._extent: Dict[str, Dict[str, List[SpatialExtent] | List[TemporalExtent]]] | None = None

    @property
    def collection_id(self) -> str:
        return self._collection_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def feature_provider_cls(self) -> Type[FeatureDataProvider[T]]:
        return self._provider_cls

    def instance(self, engine: Engine) -> FeatureDataProvider[T]:
        if self._instance is None:
            self._instance = self._provider_cls(engine)
        return self._instance

    @property
    def spatial_extent(self) -> List[SpatialExtent] | None:
        return self._spatial_extent

    @property
    def extent(self) -> Dict[str, Dict[str, List[SpatialExtent] | List[TemporalExtent]]] | None:
        if self._extent is None:
            extent: Dict[str, Dict[str, List[SpatialExtent] | List[TemporalExtent]]] | None = None
            if self._spatial_extent is not None:
                extent = {'extent': {'spatial': self._spatial_extent}}
            if self._temporal_extent is not None:
                extent = {'extent': {}} if extent is None else extent
                extent['extent']['temporal'] = self._temporal_extent
            self._extent = extent
        return self._extent

    def link(self, request: Request) -> List[Link]:
        if self._links is None:
            self._links = [
                Link(href=request.url_for('collection', collection_id=self._collection_id), rel=LinkRelation.SELF,
                     title=self._title, type=MediaType.APPLICATION_JSON),
                Link(href=request.url_for('collection_items', collection_id=self._collection_id),
                     rel=LinkRelation.ITEMS, title='{} Items'.format(self._title), type=MediaType.APPLICATION_JSON)
            ]
        return self._links

    def as_dict(self, request: Request) -> Dict[str, Any]:
        return {k: v for k, v in {
            'id': self._collection_id,
            'title': self._title,
            'description': self._description,
            'extent': self.extent,
            'itemType': 'feature',  # this is the only possible value for this one-off and is really the default value
            # todo: Add crs property but infer EPSG:4326 as that is the "expected" GeoJSON crs.
            'links': [link.model_dump(exclude_unset=True) for link in self.link(request)],
        }.items() if v}


class FeatureClassRegistry:

    def __init__(self, engine: Engine):
        self._collections: Dict[str, Any] = {}
        self._engine = engine

    def links(self, request: Request) -> List[Link]:
        return [
            Link(
                href=request.url_for('collection', collection_id=collection_id),
                rel=LinkRelation.COLLECTION,
                title=''
            ) for collection_id in self._collections.keys()
        ]

    def collections(self, request: Request) -> List[Any]:
        return [
            {k: v for k, v in feature_class.as_dict(request).items() if v}
            for feature_class in self._collections.values()
        ]

    def register(self, feature_class: FeatureClass):
        self._collections[feature_class.collection_id] = feature_class

    def find(self, collection_id: str) -> Type[FeatureDataProvider[T]]:
        return self._collections[collection_id]

    def instance(self, collection_id: str) -> FeatureDataProvider:
        return self._collections[collection_id].instance(self._engine)

    def as_dict(self, request: Request) -> Dict[str, Any]:
        return {
            'links': [link.model_dump(exclude_none=True) for link in self.links(request)],
            'collections': self.collections(request)
        }


_registry: FeatureClassRegistry | None = None


def feature_registry() -> FeatureClassRegistry:
    global _registry
    if _registry is None:
        _registry = FeatureClassRegistry(engine)
    return _registry


def feature_collection(collection_id: str,
                       title: str,
                       description: str,
                       spatial_extent: SpatialExtent | List[SpatialExtent] | None = None,
                       temporal_extent: TemporalExtent | List[TemporalExtent] | None = None):
    def decorator(provider_cls: Type[FeatureDataProvider]):
        feature_registry().register(
            FeatureClass(collection_id, title, description, provider_cls, spatial_extent, temporal_extent)
        )

    return decorator


@feature_collection(collection_id='tc-location',
                    title='Tropical Cyclone Locations',
                    description='The location points for tropical cyclones',
                    spatial_extent=(-180, -68.5, 180, 83.01000),
                    temporal_extent=(
                            datetime.fromisoformat('1842-10-25 03:00:00.000000'),
                            datetime.fromisoformat('2023-06-16 12:00:00.000000')
                    ))
class TCLocation(FeatureDataProvider):

    def items(self) -> List[Any]:
        # todo: Model the data here
        sql = 'select id, sid, name, iso_time, st_asgeojson(geom) as geom from storm_location limit 25'
        with self._engine.connect() as connection:
            results = connection.execute(text(sql))
        return [row._asdict() for row in results]

    def item(self, feature_id: str) -> str:
        # todo: possible sql injection; model data and use ORM
        sql = ('select id, sid, name, season, basin, subbasin, iso_time, nature, intensity, wind, speed, direction, '
               'pressure, gust, st_asgeojson(geom) geom  from storm_location where sid = \'{}\'').format(feature_id)
        with self._engine.connect() as connection:
            results = connection.execute(text(sql))
        return results.fetchone()._asdict()


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
