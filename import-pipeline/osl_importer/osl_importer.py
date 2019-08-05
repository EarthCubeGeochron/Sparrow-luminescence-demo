from sparrow.import_helpers import BaseImporter, SparrowImportError
from datetime import datetime
from math import isnan
import numpy as N
from click import echo, secho
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy import null
from pandas import read_excel
import re

def guard_nan(n):
    if n != n:
        return None
    return n

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
        session._method = self.method("OSL")
        session.name = guard_nan(row.iloc[1])
        # Reset data json field in case there is stale data.
        session.data = null()

        # Target phase
        min = row.loc["MINERAL"].strip()
        if min == 'Q':
            min = 'quartz'
        if min == 'F':
            min = 'feldspar'
        if min is not None:
            session._material = self.material(min, "mineral phase")

        a1 = self.mineral_separation_data(session, row)
        a2 = self.dose_rate_data(session, row)
        a3 = self.age_calculation_data(session, row)
        return session

    def mineral_separation_data(self, session, row):
        a = self.add_analysis(session, "mineral separation")

        sg_mg = row.iloc[8].strip().lower()
        if sg_mg == "sg":
            sg_mg = "single-grain separate"
        if sg_mg == "mg":
            sg_mg = "multi-grain separate"
        a._material = self.material(sg_mg, "mineral separate")

        mask_size = row.iloc[9]
        self.datum(a, "mask size", mask_size, unit='mm')

        # Can't import as numeric because it's a range...
        # maybe we need to adujst the data type?
        grain_size = row.iloc[10].split("-")
        assert len(grain_size) == 2
        self.datum(a, "minimum grain size", float(grain_size[0]), unit="µm")
        self.datum(a, "maximum grain size", float(grain_size[1]), unit="µm")

        return a

    def dose_rate_data(self, session, row):
        a = self.add_analysis(session, "luminescence dose measurement")
        self.attribute(a, "luminescence signal", row.iloc[11].strip())

        for v in row.iloc[12].split('&'):
            self.attribute(a, "dose rate measurement method", v.strip())

        self.datum(a, "H2O content",
            row.iloc[13],
            error=row.iloc[14],
            unit="%",
            error_metric="1s")
        self.db.session.flush()

        self.datum(a, "De",
            row.iloc[15],
            error=row.iloc[16],
            unit="Gy",
            error_metric="1s")

        self.datum(a, "OD", row.iloc[17], unit="%")
        return a

    def age_calculation_data(self, session, row):
        a = self.add_analysis(session, "age calculation")
        # I don't necessarily know if this concept is really
        # best modeled as a "constant"
        self.attribute(a, "age model", row.iloc[18])

        self.datum(a,
            "luminescence age",
            row.iloc[19],
            error=row.iloc[20],
            unit="ka",
            error_metric="1s")

        self.datum(a,
            "total dose rate",
            row.iloc[21],
            error=row.iloc[22],
            unit="Gy/ka",
            error_metric="1s")

        return a
