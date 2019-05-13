from pathlib import Path
from typing import Any, Dict, List

import ee
import glom

from ..collections import DistrictsCollection, ImageCollection
from ..collections.image_collection import central_europe_filter
from ..models import Clusterer
from ..models.regressor import district_predictor
from ..utils.bands import BANDS
from ..utils.logger import json_logger
from ..wrappers import ClustererWrapper, PredictionCropYieldDataset


def run(
    years: List[int],
    districts: List[str],
    clusterer: ee.Clusterer,
    clusterer_args: Dict[str, Any],
    lowland_highland_split: bool,
    predictor: ee.Classifier,
    predictor_args: Dict[str, Any],
    yield_file: Path,
    json_file_name: Path,
    force_server: bool,
):
    if not json_logger.json_exists(json_file_name) or force_server:

        region_borders = DistrictsCollection(Path("datasets/geo_data/region_borders_parsed.csv"))

        clusterers = ClustererWrapper(
            build_function=lambda y: Clusterer(
                clusterer,
                clusterer_args,
                ImageCollection(BANDS, evi_ndvi=True, filter_function=central_europe_filter).filter_date(
                    f"{y}-01-01", f"{y}-12-31"
                ),
            ),
            lowland_highland_split=lowland_highland_split,
        )

        crop_yields = PredictionCropYieldDataset(years, clusterers, yield_file)

        result = region_borders.filter_districts(districts).iterate(
            district_predictor(predictor, predictor_args, crop_yields, BANDS)
        )

        json_logger.to_json(result, json_file_name)

    else:

        result = json_logger.from_json(json_file_name)

    # simplify the results to a list of dictionaries of district and prediction
    simplified = glom.glom(result, [{"district": "district", "prediction": "features.0.properties.classification"}])

    return simplified
