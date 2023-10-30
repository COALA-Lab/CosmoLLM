import importlib.util
from pathlib import Path
import sys
import glob
import inspect

from .priori_base import PrioriFunction, PrioriContext

PRIORIS_DIRECTORY = Path(__file__).parent.absolute()
_IGNORE_FILES = {"__init__.py", "priori_base.py"}


def _import_module(module_path, name):
    module_name = f"priori.{name}"
    if module_name in sys.modules:
        module = sys.modules[module_name]
        spec = module.__spec__
    else:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _all_prioris():
    prioris = {}
    for filename in glob.glob(f"{PRIORIS_DIRECTORY}/*.py", recursive=False):
        module_path = Path(filename)
        if module_path.name not in _IGNORE_FILES:
            module = _import_module(filename, module_path.stem)
            for _, member in inspect.getmembers(module, inspect.isclass):
                if issubclass(member, PrioriFunction):
                    priori_registry = prioris.get(module_path.stem, {})
                    priori_registry[member.name] = member
                    prioris[module_path.stem] = priori_registry
    return prioris


_ALL_PRIORIS = _all_prioris()


def available_prioris():
    return {registry: set(prioris.keys()) for registry, prioris in _ALL_PRIORIS.items()}


def get_priori(registry_name: str, priori_name: str):
    if not registry_name:
        raise ValueError('Name of priori registry file cannot be None!')
    if not priori_name:
        raise ValueError('Name of priori cannot be None!')
    return _ALL_PRIORIS.get(registry_name, {}).get(priori_name, None)
