from typing import Optional
import importlib.util
from pathlib import Path
import sys
import glob
import inspect
from functools import reduce
import warnings

from .parametrization_base import BaseParametrization

PARAMETRIZATIONS_DIRECTORY = Path(__file__).parent.absolute()

_IGNORE_FILES = {"__init__.py", "parametrization_base.py"}

def _import_module(module_path, name):
    module_name = f"parametrization.{name}"
    if module_name in sys.modules:
        module = sys.modules[module_name]
        spec = module.__spec__
    else:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# def _all_parametrizations():
#     parametrizations = {}
#     for filename in glob.glob(f"{PARAMETRIZATIONS_DIRECTORY}/*.py", recursive=False):
#         module_path = Path(filename)
#         if module_path.name not in _IGNORE_FILES:
#             module = _import_module(filename, module_path.stem)
#             for _, member in inspect.getmembers(module, inspect.isclass):
#                 if issubclass(member, BaseParametrization):
#                     parametrizations[member.name] = member
#     return parametrizations
# 
# _ALL_PARAMETRIZATIONS = _all_parametrizations()

def _iter_parametrizations():
    return filter(lambda p: p.name not in _IGNORE_FILES,
            map(Path, glob.glob(f'{PARAMETRIZATIONS_DIRECTORY}/*.py')))


def available_parametrizations():
    return [filepath.stem for filepath in _iter_parametrizations()]

def _parametrization_if_exists(init: Optional[Path], module_path: Optional[Path]) -> Optional[any]:
    if not module_path: 
        return init 
    else:
        module = _import_module(module_path, module_path.stem)
        for _, member in inspect.getmembers(module, inspect.isclass):
            if issubclass(member, BaseParametrization) and member != BaseParametrization:
                return member
        warnings.warn(f'No density parametrization defined in file: {module_path}')
        return init
#    return _import_module(module_path, module_path.stem) if module_path else init

def get_parametrization(name: str):
    if not name:
        raise ValueError("Name of parametrization cannot be None!")
    return reduce(_parametrization_if_exists,
            filter(lambda p: p.stem == name, _iter_parametrizations()),
            None)
