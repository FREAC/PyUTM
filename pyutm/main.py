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

    def _get_uids(self, grid_refs, uid_column, prefix, prefix_column, gzd, k100, delimiter):
        """
        Uses the locate module to compute a Unique ID (UID) for every value in the input data.
        :param grid_refs: dataframe, grid references to be modified
        :param uid_column: string, column name for UIDs
        :param prefix: string, characters added to beginning of UID
        :param prefix_column: Pandas Series, characters added to beginning of UID
        :param gzd: whether the Grid Zone Designation should be included in the UID
        :param k100: boolean, whether the 100k meter grid reference should be included in the UID
        :param delimiter: string
        """
        if grid_refs.any():
            self._data[uid_column] = locate.UID(grid_refs, prefix, prefix_column, gzd, k100, delimiter).uids
        else:
            self._data[uid_column] = None

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

    def _write_data(self, fname, column):
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
            data.to_shp(fname, column, self._input_data, self._data, self._shape_type)
        return data.to_list(self._data, column)

    def write_refs(self, fname=None, ref_column='GRID_REFS', precision=10):
        """
        Gets the grid references for a set of points and writes them to the specified file,
        then returns a nested list of the coordinates and their grid reference.
        If no file name is given, returns a nested list without writing to a file.
        :param fname: string, default=None, file name of the output data
        :param ref_column: string, default='GRID_REFS', column name containing the grid references
        :param precision: int, default=10, desired precision of grid reference
        :return: list, nested list in [X, Y, grid reference] format
        """
        self._get_grid_refs(ref_column, precision)
        return self._write_data(fname, ref_column)

    def write_uids(self, fname=None, uid_column='UID_REFS', precision=10,
                   prefix=None, prefix_column=None, gzd=True, k100=True, delimiter='-'):
        """
        Gets the Unique IDs (UID) for a set of points and writes them to the specified file,
        then returns a nested list of the coordinates and their UID.
        If no file name is given, returns a nested list without writing to a file.
        :param fname: string, default=None, file name of the output data
        :param uid_column: string, default='UID_REFS', column name containing the UIDs
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
        self._get_uids(grid_refs, uid_column, prefix, prefix_column, gzd, k100, delimiter)
        return self._write_data(fname, uid_column)

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


if __name__ == "__main__":

    lonlats = [(-34.907587535813704, 50.58441270574641),
               (108.93083026662671, 32.38153601114477),
               (43.971544802, -46.1406771812),
               (108.930830266, 32.381536011),
               (-36.69218329018642, -45.06991972863084),
               (43.97154480746007, -46.140677181254475),
               (43.97154480, -46.140677181),
               (43.971544803, -46.1406771813)]

    lonlats2 = [[(-34.907587535813704, 50.58441270574641), True, [1, 2], 1, 'a'],
                [(108.93083026662671, 32.38153601114477), False, [3, 4], 2, 'b'],
                [(-36.69218329018642, -45.06991972863084), False, [5, 6], 3, 'c'],
                [(43.97154480746007, -46.140677181254475), True, [7, 8], 4, 'd']]

    lonlats3 = [((-34.907587535813704, 50.58441270574641), 1), ((108.93083026662671, 32.38153601114477), 2),
                ((-36.69218329018642, -45.06991972863084), 3), ((43.97154480746007, -46.140677181254475), 4)]

# TODO write tests!!!
    g = Grid((-34.907587535813704, 50.58441270574641))
    # g_output = g.write_refs(precision=10)
    g_output = g.write_uids(gzd=False, precision=10)
    print(g_output)
    h = Grid([(-34.907587535813704, 50.58441270574641), (108.93083026662671, 32.38153601114477)])
    h_output = h.write_refs()
    # h_output = h.write_uids(k100=False, prefix='pi')
    print(h_output)
    # g = Grid([(7, (-34.907587535813704, 50.58441270574641)), (8, (108.93083026662671, 32.38153601114477)),
    #           (9, (43.97154480746007, -46.140677181254475))], 1)
    i = Grid(lonlats)
    # i_output = i.write_refs()
    i_output = i.write_uids()
    # print(i_output)
    j = Grid(lonlats2)
    j_output = j.write_refs()
    j_output = j.write_uids()
    print(j_output)

    g = Grid((16.767984, -3.012058))
    print(g.write_refs())

    # g = Grid(lonlats3)
    # #
    # print()
    # print('g = Grid(lonlats2, 0)')
    # g = Grid(lonlats2, 0)
    # #
    # print()
    # print('g = Grid(lonlats2, (3, 10))')
    # g = Grid(lonlats2, (3, 10))
    # #
    # print()
    # print('g = Grid(lonlats3, 0)')
    # g = Grid(lonlats3, 0)
    #
    # print()
    # print("g = Grid('./tests/data/points.csv', ['POINT_X', 'POINT_Y'])")
    c = Grid('./tests/data/points.csv', ['POINT_X', 'POINT_Y'])
    csv_output = c.write_refs()
    # csv_output = c.write_uids(gzd=False, prefix_column='ADD_THESE')
    print(csv_output)

    # print()
    # print("g = Grid('./tests/data/points.csv', ['POINT_X', 0])")
    # g = Grid('./tests/data/points.csv', ['POINT_X', 0])
    #
    # print()
    # print("g = Grid('./tests/data/points.csv', ['POINT_X', 'PNT'])")
    # g = Grid('./tests/data/points.csv', ['POINT_X', 'PNT'])
    #
    # print()
    # print("g = Grid('./tests/data/points.csv', 'POINT_X')")
    # g = Grid('./tests/data/points.csv', 'POINT_X')
    #
    # print()
    # print("g = Grid('./tests/data/points.csv', [])")
    # g = Grid('./tests/data/points.csv', [])
    #
    # print()
    # print("g = Grid('./tests/data/points.csv')")
    # g = Grid('./tests/data/points.csv')

    j = Grid('./tests/data/points.shp')
    j_output = j.write_refs(r'test.shp')
    j_output = j.write_uids(prefix_column='ATTR')
    print(j_output)

    # x = Grid('./tests/data/points.shp', epsg=3086)
    # x_output = x.write_references(fname=r'./test.shp', column='Grid ID')
    # print(x_output)

    # import time
    #
    # start = time.time()
    # b = Grid('./tests/data/good_crimes.csv', ('Longitude', 'Latitude'))
    # b.write_references()
    # print(time.time() - start)
    #
    # start = time.time()
    # c = Grid('./tests/data/chicago_crimes_2016.csv', ('Longitude', 'Latitude'))
    # test3 = c.write_refs(r'ref2016.csv')
    # test3 = c.write_uids(r'uid2016.csv')
    # print(test3)
    # print(time.time() - start)

    # print(g.grid_refs)

    # These are the desired method calls
    # g = Grid('myassets.csv', ['Lon', 'Lat'], epsg=3086)
    # g.write_refs('myassets.shp', 'MY_OFFICIAL_GRID_REFERENCES', precision=100)
    # g.write_assets('myassets.shp', 'MY_UNIQUE_ASSET_NAMES', precision=100,
    # prefix='H', col=None, gzd=False, k100=False, delimiter='-')


# These possibilities are done
# print('Grid(True)')
# g = Grid(True)
# print('Grid(0)')
# g = Grid(0)
# print('Grid(1)')
# g = Grid(1)
# print('Grid(2)')
# g = Grid(2)
# print('Grid("i")')
# g = Grid('i')
# print('Grid("ijeg")')
# g = Grid('ijeg')
# print('Grid(0.123456)')
# g = Grid(0.123456)
# print('Grid([])')
# g = Grid([])
# print('Grid(())')
# g = Grid(())
# print('Grid([1])')
# g = Grid([1])
# print('Grid((1,))')
# g = Grid((1,))
# print('Grid((1))')
# g = Grid((1))
# g = Grid('points1.shp')
# print("g = Grid('./tests/data/points.shp', epsg=45673086)")
# g = Grid('./tests/data/points.shp', epsg=45673086)
# print("g = Grid('./tests/data/points.csv', ['POINT_X', 'POINT'])")
# g = Grid('./tests/data/points.csv', ['POINT_X', 'POINT'])
# print("g = Grid('points.csv', ['POINT_X', 'POINT_Y'])")
# g = Grid('./tests/data/points.csv', ['POINT_X', 'POINT_Y'], 26910)
#
# print("g = Grid('./tests/data/points.csv', ['POINT_X', 'POINT_Y'], 'B')")
# g = Grid('./tests/data/points.csv', ['POINT_X', 'POINT_Y'], 'B')
# print('Grid([1, 2])')
# g = Grid([1, 2])
# print('Grid((1, 2))')
# g = Grid((1, 2))
# print('Grid(lonlats2, 1)')
# g = Grid(lonlats2, 1)
# print('Grid(lonlats2, 2)')
# g = Grid(lonlats2, 2)
# print('Grid(lonlats2, 3)')
# g = Grid(lonlats2, 3)
# print('Grid(lonlats2, 4)')
# g = Grid(lonlats2, 4)
# print('Grid(lonlats2, 5)')
# g = Grid(lonlats2, 5)
# g = Grid(lonlats3)
