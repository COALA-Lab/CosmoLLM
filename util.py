from astropy import cosmology
import pandas as pd


def get_cosmology(cosmology_name: str):
    if cosmology_name.lower() == "default":
        return cosmology.default_cosmology.get()
    else:
        # Validate is actually get by name for some reason?
        return cosmology.default_cosmology.validate(cosmology_name)


def read_truth_values(max_redshift: float, csv_path: str = "hubbles.csv"):
    df = pd.read_csv(csv_path)
    df = df[df.z <= max_redshift]
    return df.H.to_numpy(), df.z.to_numpy(), df.abs_err.to_numpy()
