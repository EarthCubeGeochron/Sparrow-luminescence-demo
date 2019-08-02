from sparrow.import_helpers import BaseImporter, SparrowImportError
from datetime import datetime
from math import isnan
import numpy as N
from click import echo, secho
from sqlalchemy.exc import IntegrityError, DataError
from pandas import read_excel
import re

def extract_table(fn):
    df = read_excel(fn, header=0, skiprows=[1])
    if not df.columns[0] == "SAMPLE ID":
        raise SparrowImportError("Data file does not match expected format")
    return df

title_exp = re.compile("(.+)\s\((\w+)\)")
def parse_title(fn):
    name = fn.stem
    z = title_exp.match(name)
    project_name = z.group(1)
    project_prefix = z.group(2)
    return (project_name, project_prefix)

class OSLImporter(BaseImporter):
    """
    A basic Sparrow importer for optically-stimulated luminescence data.
    """
    authority = "Desert Research Institute"

    def import_datafile(self, fn, rec, **kwargs):
        """
        Import an individual data file
        """
        # Get data
        df = extract_table(fn)
        project_name, project_prefix = parse_title(fn)

        n = len(df)
        echo(f"{n} records")

        # Set up the project
        project = self.project(project_name)
        self.db.session.add(project)
        # We should add the prefix as either
        # an extra column or unstructured data to the project

        for i, row in df.iterrows():
            # Add all researchers defined by the project
            for r in self.create_researchers(row):
                project.researcher_collection.append(r)

            sample = self.create_sample(row.replace({N.nan: None}))
            # This flush is important, maybe we should
            # integrate into create_sample
            self.db.session.flush()
            session = self.create_session(row, sample)
            project.add_session(session)
            # `yield`ing the results lets the importer
            # know that the data files should be linked
            # to both of these entities. Then, changes
            # to those data files will trigger merging
            # of any changes to the sample and session.
            yield sample
            yield session

    def create_researchers(self, row):
        names = row.loc["PI"].split("/")
        for name in names:
            yield self.researcher(name=name)

    def create_sample(self, row):
        sample_id = str(row["SAMPLE ID"])
        sample = self.sample(name=sample_id)

        # Import geographic coordinates
        lat = row.loc["GEOGRAPHIC COORDINATES"]
        lon = row.iloc[5]
        sample.location = self.location(lon, lat)

        ## Add material for sample
        # The column header for DEPOSIT/ROCK TYPE has spacing issues
        sample._material = self.material(row.iloc[6], "deposit")
        return sample

    def create_date(self, row):
        year = row["YEAR"]
        if isnan(year):
            return datetime.min
        return datetime(int(year), 1, 1)

    def create_session(self, row, sample):
        session = self.db.get_or_create(
            self.m.session,
            sample_id=sample.id,
            date=self.create_date(row))
        session.date_precision = 'year'

        # Target phase
        min = row.loc["MINERAL"].strip()
        if min == 'Q':
            min = 'quartz'
        if min == 'F':
            min = 'feldspar'
        if min is not None:
            session._material = self.material(min, "mineral phase")

        with self.db.session.no_autoflush:
            a1 = self.mineral_separation_data(row)
            a2 = self.dose_rate_data(row)
            a3 = self.age_calculation_data(row)
            session.analysis_collection = [a1,a2,a3]

        return session

    def mineral_separation_data(self, row):
        a = self.analysis("mineral separation")
        return a

    def dose_rate_data(self, row):
        a = self.analysis("dose rate measurement")
        return a

    def age_calculation_data(self, row):
        a = self.analysis("age calculation")
        return a
