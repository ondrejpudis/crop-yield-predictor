from pathlib import Path

from .collections import GeoPointCollection, ImageCollection
from .collections.image_collection import central_europe_filter
from .utils import Bands
from .utils.logger import json_logger

i = ImageCollection(
    Bands(
        values=["B1", "B2", "B3", "B4", "B5", "B7", "B4_1", "nd"],
        names=["blue", "green", "red", "near_infrared", "shortwave_infrared_1", "shortwave_infrared_2", "evi", "ndvi"],
    ),
    evi_ndvi=True,
    filter_function=central_europe_filter,
).filter_date("2017-01-01", "2017-12-31")

tagged_geo_points = GeoPointCollection(Path("datasets/geo_data/clustering_points.csv"))

tagged_collection = i.get_composite().sampleRegions(
    collection=tagged_geo_points.features(), properties=["type"], scale=50
)
evaluated_tagged_collection = tagged_collection.getInfo()

json_logger.to_json(
    [r["properties"] for r in evaluated_tagged_collection["features"]], Path("json/tagged_remote_sensing_2017.json")
)
