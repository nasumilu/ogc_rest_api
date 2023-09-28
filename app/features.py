from datetime import datetime
from typing import Dict, Any

from shapely import from_wkt, get_coordinates
from sqlalchemy import text, TextClause, Row

from app.collection import feature_collection, FeatureDataProvider


@feature_collection(collection_id='tc-location',
                    title='Tropical Cyclone Locations',
                    description='The location points for tropical cyclones',
                    spatial_extent=(-180, -68.5, 180, 83.01000),
                    temporal_extent=(
                            datetime.fromisoformat('1842-10-25 03:00:00.000000'),
                            datetime.fromisoformat('2023-06-16 12:00:00.000000')
                    ))
class TCLocation(FeatureDataProvider):

    def _map_feature_to_geojson(self, feature: Row) -> Dict[str, Any]:
        # there are tools for this but currently this a prototype project
        geom = from_wkt(feature[4])
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',  # not very dynamic?
                'coordinates': get_coordinates(geom).tolist()
            },
            'properties': {
                'id': feature[0],
                'sid': feature[1],
                'name': feature[2],
                'iso_time': feature[3]
            }
        }

    def _sql_for_items_query(self) -> TextClause:
        return text("""
        select id,
               sid,
               name, 
               iso_time,
               st_astext(geom) as geom
        from storm_location
        limit 25
        """)

    def _sql_for_item_query(self) -> TextClause:
        return text("""
        select id,
               sid,
               name,
               iso_time,
               st_astext(geom) geom
        from storm_location
        where sid = :feature_id
        """)


@feature_collection(collection_id='tc-track',
                    title='Tropical Cyclone Tracks',
                    description='The storm track (connecting the dots)',
                    spatial_extent=(-180, -68.5, 180, 83.01000),
                    temporal_extent=(
                            datetime.fromisoformat('1842-10-25 03:00:00.000000'),
                            datetime.fromisoformat('2023-06-16 12:00:00.000000')
                    ))
class TCTrack(FeatureDataProvider):

    def _map_feature_to_geojson(self, feature: Row) -> Dict[str, Any]:
        # there are tools for this but currently this a prototype project
        geom = from_wkt(feature[6])
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'MultiLineString',
                'coordinates': get_coordinates(geom).tolist()
            },
            'properties': {
                'id': feature[0],
                'sid': feature[1],
                'sshs': feature[2],
                'name': feature[3],
                'start_iso_time': feature[4],
                'end_iso_time': feature[5],
            }
        }

    def _sql_for_items_query(self) -> TextClause:
        return text("""
        select id, 
               sid,
               sshs,
               name,
               start_iso_time,
               end_iso_time,
               st_astext(geom) as geom
        from storm_track
        limit 25
        """)

    def _sql_for_item_query(self) -> TextClause:
        return text("""
        select id,
               sid,
               sshs,
               name,
               start_iso_time,
               end_iso_time,
               st_astext(geom) as geom
        from storm_track 
        where sid = :feature_id
        """)