import json
import os

TEST_BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def load_json(path: str):
    with open(os.path.join(TEST_BASE_PATH, path)) as f:
        return json.load(f)
