from pathlib import Path
from typing import List

import glom
import src.utils.logger.json_logger as json_logger

from .collections import ImageCollection, DistrictsCollection
from .collections.image_collection import central_europe_filter
from .models import Clusterer
from .models.regressor import district_predictor
from .utils.bands import Bands
from .wrappers import ClustererWrapper, CropYieldDataset

BANDS = Bands(
    values=["B1", "B2", "B3", "B4", "B5", "B7", "B4_1", "nd"],
    names=["blue", "green", "red", "near_infrared", "shortwave_infrared_1", "shortwave_infrared_2", "evi", "ndvi"],
)


def run(
    years: List,
    clusterer,
    clusterer_args,
    lowland_highland_split,
    predictor,
    predictor_args,
    yield_file,
    json_file_name: str,
    force_server: bool,
):

    if not json_logger.json_exists(Path(json_file_name)) or force_server:

        region_borders = DistrictsCollection(Path("datasets/geo_data/region_borders_parsed.csv"))

        clusterer_wrapper = ClustererWrapper(
            build_clusterer_function=lambda y: Clusterer(
                clusterer,
                clusterer_args,
                ImageCollection(BANDS, evi_ndvi=True, filter_function=central_europe_filter).filter_date(
                    f"{y}-01-01", f"{y}-12-31"
                ),
            ),
            lowland_highland_split=lowland_highland_split,
        )

        crop_yields = CropYieldDataset(years, clusterer_wrapper, yield_file)

        result = region_borders.iterate(district_predictor(predictor, predictor_args, crop_yields, BANDS))

        json_logger.to_json(result, Path(json_file_name))

    else:

        result = json_logger.from_json(Path(json_file_name))

    simplified = glom.glom(
        result, [{"prediction": "features.0.properties.classification", "correct": "features.0.properties.yield_value"}]
    )

    return simplified
