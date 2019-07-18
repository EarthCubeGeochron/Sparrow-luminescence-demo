#!/usr/bin/env python

from os import environ
from click import command, option, argument, echo, secho, style
from pathlib import Path
from sparrow import Database
from sparrow.import_helpers import SparrowImportError, working_directory

from .osl_importer import OSLImporter

@command()
@option('--stop-on-error', is_flag=True, default=False)
@option('--verbose','-v', is_flag=True, default=False)
@option('--redo', default=False, is_flag=True)
def cli(stop_on_error=False, verbose=False, redo=False):
    """
    Import OSL data files
    """
    varname = "SPARROW_DATA_DIR"
    env = environ.get(varname, None)
    if env is None:
        v = style(varname, fg='cyan', bold=True)
        echo(f"Environment variable {v} is not set.")
        secho("Aborting", fg='red', bold=True)
        return
    path = Path(env)
    assert path.is_dir()

    db = Database()
    importer = OSLImporter(db)
    importer.iterfiles(path.glob("*.xlsx"))
