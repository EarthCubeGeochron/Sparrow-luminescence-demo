from itertools import chain
from sparrow.import_helpers import BaseImporter, SparrowImportError
from datetime import datetime
from io import StringIO
from pandas import read_csv, concat
from math import isnan
import numpy as N
from click import echo, secho
from sqlalchemy.exc import IntegrityError, DataError
from pandas import read_excel

def extract_table(fn):
    df = read_excel(fn, header=0, skiprows=[1])
    if not df.columns[0] == "SAMPLE ID":
        raise SparrowImportError("Data file does not match expected format")

    n = len(df)
    echo(f"{n} records")

    raise NotImplementedError()

class OSLImporter(BaseImporter):
    """
    A basic Sparrow importer for optically-stimulated luminescence data.
    """
    authority = "Desert Research Institute"

    def import_datafile(self, fn, rec, **kwargs):
        df = extract_table(fn)
        raise NotImplementedError()
