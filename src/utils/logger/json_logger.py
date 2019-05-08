import json
from pathlib import Path


def json_exists(path: Path):
    return path.exists()


def to_json(dataset, path: Path):
    with path.open(mode="w") as file:
        file.write(json.dumps(dataset))


def from_json(path: Path):
    with path.open(mode="r") as file:
        return json.loads(file.read())
