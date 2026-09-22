from pathlib import Path
from os.path import join as join_path


def get_unique_filepath(parent_path, template: str) -> Path:
    i = 0

    Path(parent_path).mkdir(parents=True, exist_ok=True)

    while Path(join_path(parent_path, template + str(i))).exists():
        i += 1
    return Path(join_path(parent_path, template + str(i)))
