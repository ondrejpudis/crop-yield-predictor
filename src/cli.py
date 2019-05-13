"""CLI interface commands."""

from math import sqrt
from pathlib import Path
from typing import Any, Dict, Tuple, Union

import click
import ee
from sklearn.metrics import mean_absolute_error, mean_squared_error

from .predictors.predictor import run as run_predictor
from .predictors.test_predictor import run as run_test_predictor

MODEL_ARGUMENTS: Dict[str, Tuple[Union[ee.Clusterer, ee.Classifier], Dict[str, Any]]] = {
    "kmeans": (ee.Clusterer.wekaKMeans, {"nClusters": 4, "init": 2, "distanceFunction": "Manhattan", "seed": 1}),
    "lvq": (ee.Clusterer.wekaLVQ, {"numClusters": 4, "epochs": 10000, "learningRate": 0.05, "normalizeInput": True}),
    "lr": (ee.Classifier.gmoLinearRegression, {"weight1": 0.5, "maxIterations": 200, "smooth": True}),
    "svm": (ee.Classifier.svm, {"svmType": "NU_SVR", "kernelType": "RBF", "gamma": 0.15, "cost": 100, "nu": 0.5}),
}

YIELD_DATASETS: Dict[str, Path] = {
    "cereals": Path("datasets/crop_data/cereals.csv"),
    "potatoes": Path("datasets/crop_data/potatoes.csv"),
}


@click.command(help="Test the models and get Mean Absolute or Root Mean Squared Errors.")
@click.option("-c", "clusterer", required=True, type=click.Choice(["kmeans", "lvq"]), help="Clustering algorithm.")
@click.option("-p", "predictor", required=True, type=click.Choice(["lr", "svm"]), help="Prediction algorithm.")
@click.option("--start", default=1999, type=click.IntRange(1999, 2017), help="Year to start in.")
@click.option("--end", default=2017, type=click.IntRange(1999, 2017), help="Year to end in.")
@click.option("--crop", default="cereals", type=click.Choice(["cereals", "potatoes"]), help="A crop for a prediction.")
@click.option("--split/--no-split", default=False, help="Use Lowland--Highland split.")
@click.option("--rmse/--no-rmse", default=False, help="Display RMSE score.")
@click.option("--force-server/--no-force-server", default=False, help="Force computation on server.")
def test(clusterer, predictor, start, end, crop, split, rmse, force_server):
    if start >= end:
        raise ValueError("start must be less than end")

    clustering_model = MODEL_ARGUMENTS[clusterer]
    predictor_model = MODEL_ARGUMENTS[predictor]
    result = run_test_predictor(
        years=list(range(start, end + 1)),
        clusterer=clustering_model[0],
        clusterer_args=clustering_model[1],
        lowland_highland_split=split,
        predictor=predictor_model[0],
        predictor_args=predictor_model[1],
        yield_file=YIELD_DATASETS[crop],
        json_file_name=Path(f"json/{clusterer}_{predictor}_{start}_{end}_{crop}_{split}.json"),
        force_server=force_server,
    )
    if rmse:
        print("RMSE:", sqrt(mean_squared_error([g["correct"] for g in result], [g["prediction"] for g in result])))
    print("MAE:", mean_absolute_error([g["correct"] for g in result], [g["prediction"] for g in result]))


@click.command(help="Predict a yield for a specified year for either a district or the whole republic.")
@click.option("-c", "clusterer", required=True, type=click.Choice(["kmeans", "lvq"]), help="Clustering algorithm.")
@click.option("-p", "predictor", required=True, type=click.Choice(["lr", "svm"]), help="Prediction algorithm.")
@click.option("--year", default=2019, type=click.IntRange(1999, 2019), help="A year to make the prediction for.")
@click.option("--district", default=None, help="A district to make the prediction for.")
@click.option("--crop", default="cereals", type=click.Choice(["cereals", "potatoes"]), help="A crop for a prediction.")
@click.option("--split/--no-split", default=False, help="Use Lowland--Highland split.")
@click.option("--force-server/--no-force-server", default=False, help="Force computation on server.")
def predict(clusterer, predictor, year, district, crop, split, force_server):
    clustering_model = MODEL_ARGUMENTS[clusterer]
    predictor_model = MODEL_ARGUMENTS[predictor]
    years = list(range(1999, year + 1))
    if year > 2018:
        years.remove(2018)

    result = run_predictor(
        years=years,
        clusterer=clustering_model[0],
        clusterer_args=clustering_model[1],
        lowland_highland_split=split,
        predictor=predictor_model[0],
        predictor_args=predictor_model[1],
        yield_file=YIELD_DATASETS[crop],
        json_file_name=Path(f"json/prediction_{district}_{clusterer}_{predictor}_{year}_{crop}_{split}.json"),
        districts=district,
        force_server=force_server,
    )
    print(result)
