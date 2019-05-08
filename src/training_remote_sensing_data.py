from pathlib import Path

import ee

from .collections import GeoPointCollection, ImageCollection
from .collections.image_collection import central_europe_filter
from .utils import Bands
from .utils.logger import json_logger

border_geometry = ee.Geometry.Polygon(
    [
        [17.203105592774705, 48.887824730434595],
        [17.378886842774705, 48.80106278886175],
        [17.565654420899705, 48.81191625214434],
        [17.801860475587205, 48.887824730434595],
        [17.950175905274705, 48.9491901770376],
        [18.235820436524705, 49.16517174840778],
        [18.450053834962205, 49.36948543498712],
        [18.625835084962205, 49.46954027716647],
        [18.851054811524705, 49.480248340960486],
        [18.944438600587205, 49.3802153547628],
        [19.202617311524705, 49.3802153547628],
        [19.427837038087205, 49.56939118001678],
        [19.779399538087205, 49.16517174840778],
        [20.125468874024705, 49.15798748008519],
        [20.416606569337205, 49.362330853803755],
        [20.889018678712205, 49.27997833020684],
        [21.839336061524705, 49.33012235413078],
        [22.059062624024705, 49.14720912341545],
        [22.471049928712205, 49.06089783435401],
        [22.020610475587205, 48.43429129157933],
        [21.773418092774705, 48.40147933472836],
        [21.504253053712205, 48.62345694247512],
        [20.444072389649705, 48.57259723808054],
        [20.048564577149705, 48.2151447775751],
        [19.581645631837205, 48.28829824214727],
        [19.411357545899705, 48.13088889639065],
        [18.774150514649705, 48.07953491638651],
        [18.686259889649705, 47.81092900813653],
        [17.785380983399705, 47.781407861055534],
        [16.900981569337205, 48.36499676499905],
        [17.010844850587205, 48.60893082330078],
        [17.203105592774705, 48.887824730434595],
    ]
)

i = ImageCollection(
    Bands(
        values=["B1", "B2", "B3", "B4", "B5", "B7", "B4_1", "nd"],
        names=["blue", "green", "red", "near_infrared", "shortwave_infrared_1", "shortwave_infrared_2", "evi", "ndvi"],
    ),
    add_evi_ndvi=True,
    filter_function=central_europe_filter,
).filter_date("2017-01-01", "2017-12-31")

random_geo_points = ee.FeatureCollection.randomPoints(region=border_geometry, points=1000, seed=1)
tagged_geo_points = GeoPointCollection(Path("datasets/geo_data/clustering_points.csv"))

collection = i.get_composite().sampleRegions(collection=random_geo_points, scale=50)
tagged_collection = i.get_composite().sampleRegions(collection=tagged_geo_points.data, properties=["type"], scale=50)
evaluated_collection = collection.getInfo()
evaluated_tagged_collection = tagged_collection.getInfo()

json_logger.to_json(
    [r["properties"] for r in evaluated_collection["features"]], Path("json/training_remote_sensing_2017.json")
)

json_logger.to_json(
    [r["properties"] for r in evaluated_tagged_collection["features"]], Path("json/tagged_remote_sensing_2017.json")
)
