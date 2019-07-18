from itertools import chain
from sparrow.import_helpers import BaseImporter, SparrowImportError
from datetime import datetime
from io import StringIO
from pandas import read_csv, concat
from math import isnan
import numpy as N
from click import secho
from sqlalchemy.exc import IntegrityError, DataError

from .normalize_data import normalize_data, generalize_samples

def extract_table(csv_data):
    tbl = csv_data
    if tbl is None:
        return
    f = StringIO()
    f.write(tbl.decode())
    f.seek(0)
    df = read_csv(f)
    df = df.iloc[:,1:]
    return normalize_data(df)

def infer_project_name(fp):
    folders = fp.split("/")[:-1]
    return max(folders, key=len)

class OSLImporter(BaseImporter):
    """
    A basic Sparrow importer for optically-stimulated luminescence data.
    """
    authority = "Desert Research Institute"

    def import_datafile(self, fn, rec, **kwargs):
        raise NotImplementedError()
