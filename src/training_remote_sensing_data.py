"""Acquire band values for the training points for analytic purposes."""

from pathlib import Path

from .collections import GeoPointCollection, ImageCollection
from .collections.image_collection import central_europe_filter
from .utils.bands import BANDS
from .utils.logger import json_logger

i = ImageCollection(BANDS, evi_ndvi=True, filter_function=central_europe_filter).filter_date("2017-01-01", "2017-12-31")

tagged_geo_points = GeoPointCollection(Path("datasets/geo_data/clustering_points.csv"))

tagged_collection = i.get_composite().sampleRegions(
    collection=tagged_geo_points.features(), properties=["type"], scale=50
)
evaluated_tagged_collection = tagged_collection.getInfo()

json_logger.to_json(
    [r["properties"] for r in evaluated_tagged_collection["features"]], Path("json/tagged_remote_sensing_2017.json")
)
