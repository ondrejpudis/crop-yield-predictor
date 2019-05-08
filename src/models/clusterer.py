from collections import Counter
from typing import Any, Callable, Dict, List, Union

import ee

from ..collections import ImageCollection


def find_field_cluster_synchronous(field_collection: Dict[str, Any]) -> int:
    clusters = [f["properties"]["cluster"] for f in field_collection["features"]]
    return Counter(clusters).most_common(1)[0][0]


def find_field_cluster_asynchronous(field_collection: ee.FeatureCollection) -> ee.Number:
    clusters = field_collection.iterate(lambda elem, prev: ee.List(prev).add(elem.get("cluster")), ee.List([]))
    return ee.Number(ee.List(clusters).reduce(ee.Reducer.mode())).int8()


class Clusterer:
    clusterer: ee.Clusterer
    composite: ee.Image
    fields_cluster: ee.Number

    def __init__(self, model: Callable, args: Dict[str, Any], image_collection: ImageCollection):
        self.composite = image_collection.get_composite()
        self.clusterer = model(**args)

    def train(self, training_points: ee.FeatureCollection, training_bands: List[str]):
        """Train the clusterer and identify the cluster which contains fields.

        Done by searching for a number of cluster which is most common among the training features.
        """
        training_set = self.composite.sampleRegions(collection=training_points, properties=["type"], scale=30)
        self.clusterer = self.clusterer.train(training_set, training_bands)
        self.fields_cluster = find_field_cluster_asynchronous(
            training_set.cluster(self.clusterer).filter(ee.Filter.eq("type", "cropland"))
        )
        return self

    def cluster(
        self, clip_geometry: Union[ee.FeatureCollection, ee.Geometry], scale: int = 100
    ) -> ee.FeatureCollection:
        """Cluster given collection.

        Returns only features which are clustered as field.
        """
        return (
            self.composite.sample(region=clip_geometry, scale=scale, seed=1)
            .cluster(self.clusterer)
            .filter(ee.Filter.eq("cluster", self.fields_cluster))
        )
