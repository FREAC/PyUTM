import pyproj

import pyutm.data as data
import pyutm.locate as locate


class Grid:
    """
    This class serves as the API for pyutm, with two main public methods: write_refs() and write_uids().
    """
    def __init__(self, data, columns=None, epsg=4326):
        """
        Validates, loads and optionally transforms the input data. Assumes coordinates are in EPSG:4326.
        :param data: list or string, data or file path to data
        :param columns: tuple or list of length 2, default=None, column names containing X and Y coordinates,
        in that order
        :param epsg: int, default=4326, European Petroleum Survey Group number for the input coordinate system
        """
        self._input_data = data
        self._input_columns = columns
        self._input_datatype = None
        self._shape_type = None
        self._data = None
        self._columns = None
        self._epsg = epsg
        self._error_message = None

        # Load data
        self._set_columns()
        self._set_data()
        # Transform coordinates to EPSG 4326, if necessary
        if self._epsg != 4326:
            self._transform_coords()

        if self._error_message:
            self._error(self._error_message)

    def _set_columns(self):
        """
        Validates the columns parameter: only tuples and lists of length 2 are considered valid.
        An invalid columns parameter defaults to None.
        """
        if isinstance(self._input_columns, (tuple, list)):
            if len(self._input_columns) == 2:
                self._columns = tuple(self._input_columns)
            else:
                self._columns = None

    def _set_data(self):
        """
        Loads the data based on type. 0: tuple or list, 1: CSV, or 2: SHP file.
        """
        # Tuples or lists must contain at least two elements
        if isinstance(self._input_data, (tuple, list)) and (len(self._input_data) > 1):
            self._input_datatype = 0
            self._data, self._error_message = data.from_list(self._input_data)
        else:
            try:
                if self._input_data.endswith('.csv') and self._columns:
                    self._input_datatype = 1
                    self._data, self._error_message = data.from_csv(self._input_data, self._columns)
                elif self._input_data.endswith('.shp'):
                    self._input_datatype = 2
                    self._data, self._shape_type, self._error_message = data.from_shp(self._input_data)
                # Everything else raises an error
                else:
                    raise AttributeError
            except AttributeError:
                self._error_message = 'Invalid parameter(s): Grid(data={}, columns={}, epsg={})'.format(
                    repr(self._input_data), repr(self._input_columns), self._epsg)

    def _transform_coords(self):
        """
        Reprojects coordinates into longitude and latitude.
        """
        try:
            p = pyproj.Proj(init='epsg:{}'.format(self._epsg))
            self._data[0], self._data[1] = p(self._data[0].values, self._data[1].values, inverse=True)
        except RuntimeError:
            self._error_message = 'EPSG:{} not found'.format(self._epsg)

    def _get_grid_refs(self, column, precision):
        """
        Uses the locate module class to compute a grid reference for every value in the input data.
        :param column: string, column name for grid references
        :param precision: int, desired precision of grid references
        """
        try:
            self._data[column] = [locate.Point(coord[0], coord[1], precision).grid_ref for coord in self._data.values]
        except (KeyError, ValueError):
            self._error('Invalid column name')

    def _get_uids(self, grid_refs, column, prefix, prefix_column, gzd, k100, delimiter):
        """
        Uses the locate module to compute a Unique ID (UID) for every value in the input data.
        :param grid_refs: dataframe, grid references to be modified
        :param column: string, column name for UIDs
        :param prefix: string, characters added to beginning of UID
        :param prefix_column: Pandas Series, characters added to beginning of UID
        :param gzd: whether the Grid Zone Designation should be included in the UID
        :param k100: boolean, whether the 100k meter grid reference should be included in the UID
        :param delimiter: string
        """
        if grid_refs.any():
            self._data[column] = locate.UID(grid_refs, prefix, prefix_column, gzd, k100, delimiter).uids
        else:
            self._data[column] = None

    def _get_prefix_column(self, prefix_column):
        """
        Uses the data module to retrieve prefix values if stored in the original data file.
        :param prefix_column: string or list, column name containing prefix values for the UID
        """
        try:
            prefixes = None
            # If input was a string, wrap it in a list
            if isinstance(prefix_column, str):
                prefix_column = [prefix_column]
            # Get column data from the original data files
            if self._input_datatype == 1:
                prefixes, error_message = data.from_csv(self._input_data, prefix_column, prefix=True)
            elif self._input_datatype == 2:
                prefixes, shape_type, error_message = data.from_shp(self._input_data, prefix_column)
            else:
                return prefixes
            # Call the error function directly if something went wrong
            if error_message:
                self._error(error_message)
            else:
                return prefixes.iloc[:, 0]
        except (KeyError, ValueError, AttributeError):
            self._error('Invalid column name')

    def _write_data(self, fname, column, uid=False):
        """
        Uses the setrefs module to write data to a list or file, based on the data type.
        Always returns a nested list of the computed data.
        :param fname: string, file name of the output data
        :param column: string, column name containing the grid reference or UID
        :return: list, nested list in [X, Y, grid reference or UID] format
        """
        if self._input_datatype == 1:
            data.to_csv(fname, column, self._input_data, self._data)
        elif self._input_datatype == 2:
            data.to_shp(fname, column, self._input_data, self._data, self._shape_type, uid)
        return data.to_list(self._data, column)

    def write_refs(self, fname=None, column='GRID_REFS', precision=10):
        """
        Gets the grid references for a set of points and writes them to the specified file,
        then returns a nested list of the coordinates and their grid reference.
        If no file name is given, returns a nested list without writing to a file.
        :param fname: string, default=None, file name of the output data
        :param column: string, default='GRID_REFS', column name containing the grid references
        :param precision: int, default=10, desired precision of grid reference
        :return: list, nested list in [X, Y, grid reference] format
        """
        self._get_grid_refs(column, precision)
        return self._write_data(fname, column)

    def write_uids(self, fname=None, column='UID_REFS', precision=10, prefix=None, prefix_column=None, gzd=True,
                   k100=True, delimiter='-'):
        """
        Gets the Unique IDs (UID) for a set of points and writes them to the specified file,
        then returns a nested list of the coordinates and their UID.
        If no file name is given, returns a nested list without writing to a file.
        :param fname: string, default=None, file name of the output data
        :param column: string, default='UID_REFS', column name containing the UIDs
        :param precision: int, default=10, desired precision of UID
        :param prefix: string, default=None, characters added to beginning of UID
        :param prefix_column: Pandas Series, default=None, characters added to beginning of UID
        :param gzd: boolean, default=True, whether the Grid Zone Designation should be included in the UID
        :param k100: boolean, default=True, whether the 100k meter grid reference should be included in the UID
        :param delimiter: string, default='-', delimiter of the UID
        :return: list, nested list in [X, Y, UID] format
        """
        ref_column = 'GRID_REFS'
        if prefix_column:
            prefix_column = self._get_prefix_column(prefix_column)
        self._get_grid_refs(ref_column, precision)
        # Select only the relevant column from the dataframe
        grid_refs = self._data[ref_column]
        self._get_uids(grid_refs, column, prefix, prefix_column, gzd, k100, delimiter)
        return self._write_data(fname, column, uid=True)

    @staticmethod
    def _error(message):
        """
        Prints an error message then exits the script with an exit status of 1.
        :param message: string, error message to print
        """
        # Only import sys for errors
        import sys
        print('Error creating Grid object: {}'.format(message))
        sys.exit(1)


lonlat = [(16.776031, -3.005612), (16.772291, -3.007136), (0, 0), (-93.0, 44.99995)]
g = Grid(lonlat)
myr = g.write_refs(precision=1)
print(myr)