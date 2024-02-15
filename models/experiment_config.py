from pathlib import Path
from typing import List, TypeVar, Union, Mapping
from pydantic import BaseModel, validator

from astropy import cosmology

from parametrization import available_parametrizations
from priori import available_prioris


StrPath = Union[Path, str]
T = TypeVar("T")
OneOrList = Union[List[T], T]


class FitsPath(BaseModel):
    fitres: str
    sys: str


class Parametrization(BaseModel):
    name: str
    param_names: List[str]


class ExperimentConfig(BaseModel):
    name: str
    cosmo: str
    fits_path: FitsPath
    truth_values: str
    max_redshift: float
    nwalkers: int
    nchains: int
    nsteps: int
    priori: Mapping[str, str]
    parametrization: Parametrization

    @validator("cosmo")
    def cosmo_must_exist(cls, v):
        available = cosmology.available
        assert (
            v.lower() == "default" or v in available
        ), f"""Cosmology must be "default" or one of
        available cosmologies: {available}"""
        return v

    @validator("fits_path")
    def fits_path_must_exist_and_be_files(cls, v):
        fitres = v.fitres
        sys = v.sys
        fitres_path = Path(fitres)
        sys_path = Path(sys)
        fitres_exists = fitres_path.exists()
        sys_exists = sys_path.exists()
        if not fitres_exists or not sys_exists:
            err = ""
            if not fitres_exists:
                err += f"The 'fitres' file path: '{fitres}' specified in the configuration does not exist!\n"
            if not sys_exists:
                err += f"The 'sys' file path: '{sys}' specified in the configuration does not exist!"
            raise ValueError(err)

        fitres_is_dir = fitres_path.is_dir()
        sys_is_dir = sys_path.is_dir()
        if fitres_is_dir or sys_is_dir:
            err = ""
            if fitres_is_dir:
                err += f"The 'fitres' file path: {fitres} specified in the configuration is a directory!\n"
            if sys_is_dir:
                err += f"The 'sys' file path: {sys} specified in the configuration is a directory!"
            raise ValueError(err)
        return v

    @validator("truth_values")
    def truth_values_must_exist_and_be_csv(cls, truth_values):
        truth_path = Path(truth_values)
        if not truth_path.exists():
            raise ValueError(
                f"The 'truth_values' file path: '{truth_values}' in the specified configuration does not exist!"
            )
        if truth_path.is_dir():
            raise ValueError(
                f"The 'truth_values' file path: '{truth_values}' is a directory!"
            )
        if truth_path.suffix != ".csv":
            raise ValueError(
                f"The 'truth_values' file path: '{truth_values}' must end with '.csv' - be a valid CSV file!"
            )
        return truth_values

    @validator("parametrization")
    def parametrization_must_be_available(cls, val):
        assert (
            val.name in available_parametrizations()
        ), f"Parametrization must be one of the available parametrizations: {available_parametrizations()}"
        return val

    @validator("priori")
    def all_priori_available(cls, prioris):
        valid_prioris = available_prioris()
        print("valid_prioris ", valid_prioris)
        for key, val in prioris.items():
            print("prioris_k", key)
            print("prioris_v", val)
            print("valid_prioris.get(key, {}) ", valid_prioris.get(key, {}))
            if val not in valid_prioris.get(key, {}):
                raise ValueError(
                    f"All prioris must be from the following available ones: {valid_prioris}"
                )
        return prioris

    def __str__(self) -> str:
        return f'Experiment configuration: "{self.name}"'
