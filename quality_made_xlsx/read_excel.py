from pypif.obj import System, Property, FileReference
from hashlib import sha256
import ast
import logging
import pandas as pd
import numpy as np
import re
import os
import sys


_logger = logging.getLogger(__name__)

# _logger.setLevel(logging.DEBUG)
#
# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
#
# _logger.addHandler(handler)


def excel_to_DataFrame(*args, **kwds):
    """
    Reads data from an excel file and applies a conversion to each
    element allowing the cells to hold lists/tuples, and dictionaries in
    addition to scalar values.

    :param args: Positional parameters for `pandas.read_excel`
    :param kwds: Optional parameters for `pandas.read_excel`
    :returns: pandas.DataFrame
    """
    def convert(obj):
        """
        Pandas `read_excel` has the `converters` option that allows the
        user to specify converters for each column. The value of this
        option must be a dictionary that maps the column name or index
        of the column to a function that accepts the cell data (as a
        string) and returns the converted value.

        If python-style lists, tuples, dictionaries, etc. are stored
        in an Excel cell, Converter calls ast.literal_eval as a conversion
        for each cell regardless of the key (column name/column index).
        """
        try:
            if isinstance(obj, str):
                # error handling: list-like object doesn't have square brackets.
                obj = obj.strip('[]')
                obj = [s.strip() for s in obj.strip('[]').split(',')]
            return ast.literal_eval(obj)
        except (ValueError, SyntaxError):
            return obj

    df = pd.read_excel(*args, **kwds)
    # convert each element to handle lists, tuples, etc.
    return df.applymap(convert)


def read_excel(filename, index=None, **excel_kwds):
    """
    Reads an Excel-formatted filename.

    :param filename: File name object to read from.
    :type filename: str
    :param index: Column name to use as the Index
    :type index: str
    :param excel_kwds: Keywords passed to pandas.read_excel. (Optional)
    :type excel_kwds: dictionary
    :return: list of PIF objects.
    """
    def FileReference_from_key_value(key, value):
        # get name
        name = re.sub(r'FILE:\s*(.*)\s*', r'\1', key)
        # create property
        prop = Property(name=name, files=[])
        if (value in (None, '') or
            (isinstance(value, float) and np.isnan(value))):
            # no property is specified
            _logger.debug(f"{value} is empty.")
            filenames = []
        elif isinstance(value, str):
            # only one name is specified
            _logger.debug(f"{value} is a string.")
            filenames = [value]
        elif hasattr(value, "__iter__"):
            # list of filenames
            _logger.debug(f"{value} is a list.")
            filenames = [str(s) for s in value]
        else:
            raise ValueError(f"{value} is not a recognized file type.")
        for filename in filenames:
            # for each filename, add file reference and SHA256 hash
            ref = FileReference(relative_path=filename)
            if os.path.isfile(filename):
                with open(filename) as ifs:
                    ref.sha256 = sha256(ifs.read().encode()).digest()
            prop.files.append(ref)
        return prop

    def property_from_key_value(key, value):
        try:
            # extract "description (units)"
            match = re.match(
                pattern=r'\s*([^(]*)\(([^)]*)\).*',
                string=key).groups()
            name, units = [s.strip() for s in match]
        except AttributeError:
            # no units were provided
            name = key
            units = None
        except:
            raise ValueError(f"'{key}' --> '{match}'")
        return Property(
            name=name,
            scalars=value,
            units=units
        )

    def system_from_row(row, names=None):
        """
        Handles three "magic" columns: "Sample Name", "Parent Sample Name",
        and "FILE:..."

        :param row: Row from a pandas.DataFrame.
        :type row: Pandas namespace object
        :param names: Names to use for the keys. The Sample Name should be
            the Index and, therefore, should not be included in names.
        :type names: iterable of strings
        :return: Record in Citrine System format
        :rtype: pif.System
        """
        # convert to dictionary
        if names is None:
            names = list(row._fields)
        else:
            names = ['Index'] + [n for n in names if n != "Index"]
        record = dict(zip(names, row))
        # create system object
        retval = System()
        # set uid (from magic #1: Sample Name, the Index in the DataFrame)
        retval.uid = str(record['Index'])
        del record['Index']
        # set source/parent name (from magic #2: Parent Sample Name)
        for k,v in iter(record.items()):
            if re.match(r'parent sample name', k, re.IGNORECASE):
                if not (np.isnan(v) or v is None):
                    retval.sub_systems = System(uid=str(v))
                del record[k]
                break
        # add properties and files
        properties = []
        for k,v in iter(record.items()):
            if re.match(r'^FILE:', k):
                # files (from magic #3: FILE:...)
                properties.append(FileReference_from_key_value(k, v))
            else:
                # miscellaneous properties
                properties.append(property_from_key_value(k, v))
        retval.properties = properties
        return retval

    records = []
    xls = pd.ExcelFile(filename)
    for sheetName in xls.sheet_names:
        _logger.info(f"Reading sheetname {sheetName}.")
        # read from fileobj
        df = excel_to_DataFrame(filename, sheet_name=sheetName)
        if index in df:
            df.set_index(index)
        _logger.info(f"DataFrame\n{df.head()}")

        # convert to PIF
        records.extend(
            [system_from_row(row, names=df.columns) for row in df.itertuples()])

    # done
    return records
