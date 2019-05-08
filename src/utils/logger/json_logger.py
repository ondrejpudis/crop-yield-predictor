import json
from pathlib import Path


def json_exists(path: Path):
    return path.exists()


def to_json(dataset, path):
    with open(path, "w") as file:
        file.write(json.dumps(dataset))


def from_json(path):
    with open(path, "r") as file:
        return json.loads(file.read())
