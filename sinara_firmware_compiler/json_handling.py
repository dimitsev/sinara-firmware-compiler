import os
import json
import numpy as np


def to_json(
    dictionary     : dict, # will be written to file `json_file_path`
    json_file_path : str,
    verbose        : bool = True,
):
    json_file_path = os.path.realpath(json_file_path, strict=False)
    class CustomJSONEncoder(json.JSONEncoder):
        # `json.JSONEncoder.encode()` delegates supported types to their respective handlers
        # and unsupported types to `json.JSONEncoder.default()`.
        def default(self, obj):
            if isinstance(obj, np.generic):
                return obj.item()
            return super().default(obj)
    with open(json_file_path, "w") as json_file:
        json.dump(dictionary, json_file, cls=CustomJSONEncoder, indent=4)
    if verbose:
        print("Wrote to:", json_file_path)


def from_json(json_file_path : str):
    json_file_path = os.path.realpath(json_file_path, strict=True)
    with open(json_file_path, "r") as file:
        data = file.read()
    return json.loads(data)