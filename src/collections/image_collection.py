from typing import Callable, Optional

import ee

from ..utils import Bands


def central_europe_filter(collection: ee.ImageCollection) -> ee.ImageCollection:
    return collection.filter(
        ee.Filter.And(
            ee.Filter.gte("WRS_PATH", 186),
            ee.Filter.lte("WRS_PATH", 189),
            ee.Filter.gte("WRS_ROW", 26),
            ee.Filter.lte("WRS_ROW", 27),
        )
    )


def add_evi_ndvi(composite: ee.Image) -> ee.Image:
    red = composite.select("B3")
    blue = composite.select("B1")
    infrared = composite.select("B4")
    return composite.addBands(
        infrared.subtract(red).multiply(2.5).divide(infrared.add(red.multiply(6)).subtract(blue.multiply(7.5)).add(1))
    ).addBands(composite.normalizedDifference(bandNames=["B4", "B3"]))


class ImageCollection:
    collection: ee.ImageCollection
    bands: Bands
    evi_ndvi: bool

    def __init__(self, bands: Bands, evi_ndvi: bool = False, filter_function: Optional[Callable] = None):
        self.collection = ee.ImageCollection("LANDSAT/LE07/C01/T1")
        if filter_function:
            self.collection = filter_function(self.collection)
        self.bands = bands
        self.evi_ndvi = evi_ndvi

    def get_composite(self) -> ee.Image:
        """Create a new composite from the collection.

        Rename the bands according to the Bands objects passed during initialisation.
        """
        composite = ee.Algorithms.Landsat.simpleComposite(collection=self.collection)
        if self.evi_ndvi:
            evi_ndvi_composite = add_evi_ndvi(
                ee.Algorithms.Landsat.simpleComposite(collection=self.collection, asFloat=True)
            )
            composite = composite.addBands(evi_ndvi_composite.select(["nd", "B4_1"]))
        return composite.select(self.bands.values).rename(self.bands.names)

    def filter_date(self, date_from: str, date_to: str) -> "ImageCollection":
        self.collection = self.collection.filterDate(date_from, date_to)
        return self
