from pathlib import Path
import glob

CONFIG_DIRECTORY = Path(__file__).parent.absolute()
_IGNORE_FILES = {"__init__.py"}


def _iter_configs():
    return filter(
        lambda p: p.name not in _IGNORE_FILES,
        map(Path, glob.glob(f'{CONFIG_DIRECTORY}/*.json'))
    )


def available_configs():
    return [filepath.stem for filepath in _iter_configs()]

