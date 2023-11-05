from typing import Union, Optional, List
from pathlib import Path
from collections import namedtuple

import numpy as np
from astropy.cosmology import Planck15
from astropy.cosmology.core import Cosmology

from SNANA_StarterKit.util.txtobj import txtobj
from SNANA_StarterKit.util.getmu import getmu


FitresDataPath = namedtuple("FitresDataPath", ["name", "id", "fitres", "sys_matrix"])
"""
Paths to the systematic matrix and the FITRES data file.
"""

FitresData = namedtuple("FitresData", ["cov_matrix", "mu", "delta_mu"])
"""
Data required for computing \\chi squared for the MCMC model.
"""


def load_sys_from_file(path: Union[str, Path], dtype=np.float64) -> np.ndarray:
    """Loads a covariance matrix from a file in the format specified by the Pantheon sample.

    The first row of the file must be the number of entries in a single row/column of the covariance matrix.
    After that each row contains a single row entry.
    The method will break if the file does not contain enough data for the matrix to be square.

    Args:
        path (str, Path): The path to the file containing the covariance matrix.

    Returns:
        np.ndarray: The covariance matrix in the form of a numpy array.
    """
    with open(path, "r") as f:
        entry_per_row_str = f.readline()
        if not entry_per_row_str:
            raise RuntimeError(
                f"""The first row of the covariance matrix file must contain the number of entries per row in the matrix, but is empty or None.
                Covariance matrix file: '{path}'"""
            )
        n_entries = int(entry_per_row_str.strip())
        res = np.loadtxt(f, dtype=dtype)
        return res.reshape(n_entries, n_entries)


class FitresDataPaths(List[FitresDataPath]):
    def get_by_id(self, fit_id: str) -> Optional[FitresDataPath]:
        for path in self:
            if path.id == fit_id:
                return path
        return None


def _construct_fitres_data_path(fitres_file_path: Path) -> FitresDataPath:
    name: str = fitres_file_path.stem
    id = name[name.rindex("_") + 1 :]
    sys_mat_path = fitres_file_path.parent.joinpath(f"sys_full_long_{id}.txt")
    assert sys_mat_path.exists()
    return FitresDataPath(
        name=name, id=id, fitres=fitres_file_path, sys_matrix=sys_mat_path
    )


def get_available_fitres_data(fitres_path: Union[Path, str]) -> FitresDataPaths:
    fitres_path = Path(fitres_path)
    print(fitres_path)
    if not fitres_path.is_dir() or not fitres_path.exists():
        raise ValueError("The fitres_path parameter must be a valid directory")

    return FitresDataPaths(
        [_construct_fitres_data_path(path) for path in fitres_path.glob("*.FITRES")]
    )


def parse_fits(fitres: str, sys_matrix: str, cosmology: Cosmology = Planck15) -> Optional[FitresData]:    
    C_sys = load_sys_from_file(sys_matrix)
    tobj = txtobj(fitres, fitresheader=True)
    tobj = getmu(tobj, cosmo=cosmology)
    C = C_sys + np.diag(tobj.muerr**2)
    return FitresData(cov_matrix=C, mu=tobj.mu, delta_mu=tobj.mures)

def load_fit_data(
    fit_path: Optional[FitresDataPath],
    cosmology: Cosmology = Planck15
) -> Optional[FitresData]:

    if fit_path is None:
        return None
    return parse_fits(fit_path.fitres, fit_path.sys_matrix, cosmology)
